#!/usr/bin/env python3
"""闸门 A：代码执行验证。

读取 Stage 3 产出的 chNN_data.json，抽取其中所有代码段（知识点 how.code
与练习 answer.code），逐段在隔离 venv 里执行，验证"跑得通 / 输出对得上"，
把结果写到 validation/chNN_code.json。

纯脏活、无 AI：跑不通的代码不许进文档，用机器把质量从"靠模型聪明"
变成"靠能否运行"。

代码分级（决定怎么验）：
  L0 纯逻辑   —— 只 import 标准库 → 真实执行，比对 expected_output
  L1 需三方库 —— import 第三方但不联网 → venv 装 dependencies 后执行
  L2 需 API   —— 命中 openai/api_key 等 → 只做语法 + import 可解析性检查（降级）

依赖：仅标准库（venv / pip 通过子进程调用）。
"""

import argparse
import ast
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# 命中即判为 L2（需真实外部服务，本闸门只做静态检查，不真跑）
_L2_PATTERNS = re.compile(
    r"\b(openai|anthropic|ChatOpenAI|ChatAnthropic|api_key|API_KEY"
    r"|os\.environ|getenv|requests\.(get|post)|httpx|urllib\.request"
    r"|dashscope|zhipuai|qianfan)\b"
)

# import 名 → pip 包名的常见差异（兜底映射；优先用 data 里显式 dependencies）
_IMPORT_TO_PKG = {
    "cv2": "opencv-python",
    "PIL": "pillow",
    "sklearn": "scikit-learn",
    "yaml": "pyyaml",
    "bs4": "beautifulsoup4",
}


def die(msg: str, code: int = 1):
    print(f"[错误] {msg}", file=sys.stderr)
    sys.exit(code)


def _stdlib_names() -> frozenset[str]:
    # 3.10+ 才有 sys.stdlib_module_names；旧版退化为空集（一律当三方处理）
    return getattr(sys, "stdlib_module_names", frozenset())


_STDLIB = _stdlib_names()


# ── 代码抽取 ──────────────────────────────────────────────────────────────────


def extract_code_blocks(data: dict) -> list[dict]:
    """从章节数据里收集所有待验证代码段。

    返回 [{ref, code, language, dependencies, expected_output}]。
    练习若未声明 dependencies，则继承本章所有知识点依赖的并集。
    """
    blocks: list[dict] = []

    chapter_deps: set[str] = set()
    for kp in data.get("knowledge_points") or []:
        how = kp.get("how") or {}
        for d in how.get("dependencies") or []:
            chapter_deps.add(d)

    for i, kp in enumerate(data.get("knowledge_points") or []):
        how = kp.get("how") or {}
        code = (how.get("code") or "").strip()
        if not code:
            continue
        blocks.append(
            {
                "ref": f"{kp.get('id') or f'kp{i + 1}'}.how.code",
                "code": code,
                "language": (how.get("language") or "python").lower(),
                "dependencies": list(how.get("dependencies") or []),
                "expected_output": how.get("expected_output"),
            }
        )

    for ex in data.get("exercises") or []:
        ans = ex.get("answer") or {}
        code = (ans.get("code") or "").strip()
        if not code:
            continue
        blocks.append(
            {
                "ref": f"ex{ex.get('level', '?')}.answer.code",
                "code": code,
                "language": (ans.get("language") or "python").lower(),
                "dependencies": list(ans.get("dependencies") or chapter_deps),
                "expected_output": ans.get("expected_output"),
            }
        )

    return blocks


# ── 分级 ──────────────────────────────────────────────────────────────────────


def classify(code: str) -> tuple[str, list[str], str | None]:
    """返回 (级别, 三方顶层 import 列表, 语法错误信息)。语法错误时级别为 'syntax'。"""
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return "syntax", [], f"{e.__class__.__name__}: {e}"

    third_party: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            mods = [a.name.split(".")[0] for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            # 相对 import（node.level>0）是脚本内部模块，忽略
            mods = (
                [node.module.split(".")[0]] if node.module and node.level == 0 else []
            )
        else:
            continue
        for m in mods:
            if m and m not in _STDLIB and m not in third_party:
                third_party.append(m)

    if _L2_PATTERNS.search(code):
        return "L2", third_party, None
    if third_party:
        return "L1", third_party, None
    return "L0", third_party, None


def resolve_packages(declared: list[str], imports: list[str]) -> list[str]:
    """优先用 data 显式声明的 pip 规格；缺失的三方 import 用名字兜底。"""
    if declared:
        return declared
    return [_IMPORT_TO_PKG.get(m, m) for m in imports]


# ── venv 管理（按依赖集哈希缓存复用）────────────────────────────────────────────


def _venv_python(venv_dir: Path) -> Path:
    if platform.system() == "Windows":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def ensure_venv(
    packages: list[str], cache_root: Path
) -> tuple[Path | None, str | None]:
    """建/复用一个装好 packages 的 venv，返回 (python 路径, 安装错误)。

    无三方依赖时返回当前解释器，不建 venv。
    """
    if not packages:
        return Path(sys.executable), None

    key = hashlib.sha256("\n".join(sorted(packages)).encode()).hexdigest()[:16]
    venv_dir = cache_root / key
    marker = venv_dir / ".ready"
    py = _venv_python(venv_dir)

    if marker.exists() and py.exists():
        return py, None

    if venv_dir.exists():
        shutil.rmtree(venv_dir, ignore_errors=True)
    venv_dir.mkdir(parents=True, exist_ok=True)

    r = subprocess.run(
        [sys.executable, "-m", "venv", str(venv_dir)],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if r.returncode != 0:
        return None, f"创建 venv 失败: {r.stderr.strip()}"

    # pip 阶段需要联网，不受断网哨兵影响（哨兵只注入用户代码子进程）
    r = subprocess.run(
        [
            str(py),
            "-m",
            "pip",
            "install",
            "--quiet",
            "--disable-pip-version-check",
            *packages,
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=600,
    )
    if r.returncode != 0:
        return None, f"pip install 失败: {r.stderr.strip()[-500:]}"

    marker.write_text("ok", encoding="utf-8")
    return py, None


# ── 执行 ──────────────────────────────────────────────────────────────────────


# 断网哨兵：作为 sitecustomize 在解释器启动时自动加载，掐断 socket
_NETBLOCK = (
    "import socket\n"
    "def _b(*a, **k):\n"
    "    raise OSError('network disabled by verify_code')\n"
    "socket.socket = _b\n"
    "socket.create_connection = _b\n"
)


def run_code(code: str, python: Path, timeout: int, no_network: bool) -> dict:
    """在子进程跑一段代码，返回 {returncode, stdout, stderr, timed_out}。"""
    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        (tdp / "snippet.py").write_text(code, encoding="utf-8")

        env = os.environ.copy()
        if no_network:
            (tdp / "sitecustomize.py").write_text(_NETBLOCK, encoding="utf-8")
            # 让 sitecustomize 优先被找到
            env["PYTHONPATH"] = str(tdp) + os.pathsep + env.get("PYTHONPATH", "")

        try:
            r = subprocess.run(
                [str(python), str(tdp / "snippet.py")],
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=timeout,
                env=env,
                cwd=td,
            )
            return {
                "returncode": r.returncode,
                "stdout": r.stdout or "",
                "stderr": r.stderr or "",
                "timed_out": False,
            }
        except subprocess.TimeoutExpired:
            return {"returncode": None, "stdout": "", "stderr": "", "timed_out": True}


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip()


def _fix_hint(error: str) -> str:
    if "ModuleNotFoundError" in error or "No module named" in error:
        return "import 的包未安装或与标注版本不符，检查 how.dependencies 是否完整、版本是否对得上 import 路径"
    if "SyntaxError" in error:
        return "代码语法错误，无法解析"
    if "network disabled" in error:
        return "代码尝试联网，但本段被判为 L0/L1 不应联网；若确需外部服务应标 L2 或补 dependencies"
    return "执行失败，见 error 详情"


def verify_block(block: dict, cache_root: Path, timeout: int, no_network: bool) -> dict:
    ref = block["ref"]
    if block["language"] != "python":
        return {
            "ref": ref,
            "level": "skipped",
            "status": "skipped",
            "error": f"非 python 代码（{block['language']}），暂不执行",
        }

    level, imports, syntax_err = classify(block["code"])

    if level == "syntax":
        return {
            "ref": ref,
            "level": "syntax",
            "status": "fail",
            "error": syntax_err,
            "output_match": None,
            "fix_hint": _fix_hint(syntax_err),
        }

    # L2：只静态确认能解析（classify 已过 ast.parse），不真跑
    if level == "L2":
        return {
            "ref": ref,
            "level": "L2",
            "status": "pass",
            "note": "命中外部服务特征，仅做语法 + import 静态检查，未真实执行",
        }

    packages = resolve_packages(block["dependencies"], imports) if level == "L1" else []
    python, install_err = ensure_venv(packages, cache_root)
    if install_err:
        return {
            "ref": ref,
            "level": level,
            "status": "fail",
            "error": install_err,
            "output_match": None,
            "fix_hint": _fix_hint(install_err),
        }

    res = run_code(block["code"], python, timeout, no_network)

    if res["timed_out"]:
        return {
            "ref": ref,
            "level": level,
            "status": "timeout",
            "error": f"执行超过 {timeout}s 被终止",
            "output_match": None,
            "fix_hint": "可能死循环或等待网络输入",
        }

    if res["returncode"] != 0:
        err = res["stderr"].strip()[-800:]
        return {
            "ref": ref,
            "level": level,
            "status": "fail",
            "error": err,
            "output_match": None,
            "fix_hint": _fix_hint(err),
        }

    expected = block.get("expected_output")
    output_match = None
    if expected:
        output_match = _norm(expected) in _norm(res["stdout"])
        if not output_match:
            return {
                "ref": ref,
                "level": level,
                "status": "fail",
                "error": f"实际输出与 expected_output 不符。实际(截断): {res['stdout'].strip()[:300]}",
                "output_match": False,
                "fix_hint": "改代码使输出符合预期，或修正 expected_output",
            }

    return {"ref": ref, "level": level, "status": "pass", "output_match": output_match}


# ── 主流程 ────────────────────────────────────────────────────────────────────


def verify_file(path: Path, cache_root: Path, timeout: int, no_network: bool) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    blocks = extract_code_blocks(data)
    results = [verify_block(b, cache_root, timeout, no_network) for b in blocks]
    n_pass = sum(1 for r in results if r["status"] == "pass")
    n_fail = sum(1 for r in results if r["status"] in ("fail", "timeout"))
    return {
        "chapter_number": data.get("chapter_number"),
        "source": path.name,
        "summary": {
            "total": len(results),
            "pass": n_pass,
            "fail": n_fail,
            "skipped": len(results) - n_pass - n_fail,
        },
        "results": results,
    }


def main():
    ap = argparse.ArgumentParser(description="闸门 A：章节代码执行验证")
    ap.add_argument("target", help="chNN_data.json 文件，或包含它们的 chapters/ 目录")
    ap.add_argument(
        "-o", "--out", help="validation 输出目录（默认 target 同级 ../validation）"
    )
    ap.add_argument(
        "--timeout", type=int, default=30, help="单段执行超时秒数（默认 30）"
    )
    ap.add_argument("--network", action="store_true", help="允许联网（默认断网）")
    ap.add_argument("--venv-cache", help="venv 缓存目录（默认 out 同级 .cache/venvs）")
    args = ap.parse_args()

    # Windows 控制台默认 GBK，强制 UTF-8 以免中文进度行乱码
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")

    target = Path(args.target)
    if not target.exists():
        die(f"目标不存在: {target}")

    files = sorted(target.glob("ch*_data.json")) if target.is_dir() else [target]
    if not files:
        die("未找到 ch*_data.json")

    base = target if target.is_dir() else target.parent
    out_dir = Path(args.out) if args.out else (base.parent / "validation")
    out_dir.mkdir(parents=True, exist_ok=True)
    cache_root = (
        Path(args.venv_cache) if args.venv_cache else (base.parent / ".cache" / "venvs")
    )
    cache_root.mkdir(parents=True, exist_ok=True)

    overall_fail = 0
    for f in files:
        report = verify_file(f, cache_root, args.timeout, not args.network)
        ch = report["chapter_number"]
        out_path = (
            out_dir / f"ch{ch:02d}_code.json"
            if isinstance(ch, int)
            else out_dir / f"{f.stem}_code.json"
        )
        out_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        s = report["summary"]
        overall_fail += s["fail"]
        flag = "FAIL" if s["fail"] else "OK"
        print(
            f"[{flag}] {f.name}: 通过 {s['pass']}/{s['total']}，失败 {s['fail']} → {out_path.name}"
        )

    # 有失败时非零退出，便于 CI / 回灌回路判断
    sys.exit(1 if overall_fail else 0)


if __name__ == "__main__":
    main()
