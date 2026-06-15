#!/usr/bin/env python3
"""闸门编排器：按顺序跑四道客观闸门，汇总放行/拦截结果。

对 chapters/ 下每个 chNN_data.json：
  闸门B 文档反查(verify_docs) → Stage4 结构(validate_schema)
  → C2 接地(verify_grounding) → 闸门A 代码执行(verify_code)
任一闸门有 error/fail → 该章进 validation/blocked.json，不进渲染；
全绿的章列入 validation/passed.json，可交给 render.py。

本编排器只跑"无 AI 的机器闸门"。C3 rubric 判官（需强模型）和
定向回灌（需重写模型）由对话层 Claude 执行，见 SKILL.md。

依赖：仅标准库。同目录的各 verify_*.py / validate_schema.py。
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent


def die(msg: str, code: int = 1):
    print(f"[错误] {msg}", file=sys.stderr)
    sys.exit(code)


def run(script: str, *cli: str) -> int:
    """跑一个子脚本，回显其输出，返回退出码。"""
    p = subprocess.run(
        [sys.executable, str(_SCRIPTS / script), *cli],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if p.stdout:
        print(p.stdout, end="")
    if p.returncode != 0 and p.stderr:
        print(p.stderr, end="", file=sys.stderr)
    return p.returncode


def _load(path: Path) -> dict | None:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def collect_blocks(ch: int, val_dir: Path) -> list[dict]:
    """从各闸门产物里收集该章的所有 error/fail，附 ref + fix 信息。"""
    blocks: list[dict] = []
    p = f"ch{ch:02d}"

    schema = _load(val_dir / f"{p}_schema.json")
    if schema:
        for e in schema.get("errors") or []:
            blocks.append({"gate": "schema", **e})

    grounding = _load(val_dir / f"{p}_grounding.json")
    if grounding:
        for r in grounding.get("results") or []:
            if r.get("status") == "fail":
                blocks.append(
                    {
                        "gate": "grounding",
                        "ref": r.get("ref"),
                        "msg": r.get("reason"),
                        "fix_hint": r.get("fix_hint"),
                    }
                )

    code = _load(val_dir / f"{p}_code.json")
    if code:
        for r in code.get("results") or []:
            if r.get("status") in ("fail", "timeout"):
                blocks.append(
                    {
                        "gate": "code",
                        "ref": r.get("ref"),
                        "msg": r.get("error"),
                        "fix_hint": r.get("fix_hint"),
                    }
                )

    docs = _load(val_dir / f"{p}_docs_check.json")
    if docs:
        for t in docs.get("summary", {}).get("topics_degraded") or []:
            blocks.append(
                {
                    "gate": "docs",
                    "ref": f"topic.{t}",
                    "msg": "话题所有文档来源失效，退化为 not_found",
                }
            )
    return blocks


def main():
    ap = argparse.ArgumentParser(description="闸门编排器")
    ap.add_argument("tutorial_root", help="out/<教程标题>/ 目录")
    ap.add_argument("--timeout", type=int, default=30, help="代码执行单段超时秒数")
    ap.add_argument("--network", action="store_true", help="代码执行允许联网")
    args = ap.parse_args()

    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8")

    root = Path(args.tutorial_root)
    chapters = root / "chapters"
    analysis = root / "analysis"
    val = root / "validation"
    if not chapters.is_dir():
        die(f"找不到 {chapters}")
    val.mkdir(parents=True, exist_ok=True)

    # 1. 闸门 B 文档反查（按 analysis 目录批量；无 docs 文件则跳过）
    if list(analysis.glob("ch*_docs.json")):
        print("=== 闸门B：文档反查 ===")
        run("verify_docs.py", str(analysis))

    # 2. Stage4 结构
    print("=== Stage4：结构校验 ===")
    run("validate_schema.py", str(chapters))

    # 3. C2 接地
    print("=== C2：接地校验 ===")
    run("verify_grounding.py", str(chapters))

    # 4. 闸门 A 代码执行
    print("=== 闸门A：代码执行 ===")
    code_cli = [str(chapters), "--timeout", str(args.timeout)]
    if args.network:
        code_cli.append("--network")
    run("verify_code.py", *code_cli)

    # 汇总
    passed, blocked = [], {}
    for f in sorted(chapters.glob("ch*_data.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        ch = d.get("chapter_number")
        if not isinstance(ch, int):
            continue
        blocks = collect_blocks(ch, val)
        if blocks:
            blocked[f"ch{ch:02d}"] = {"title": d.get("title"), "blocks": blocks}
        else:
            passed.append(f"ch{ch:02d}")

    (val / "passed.json").write_text(
        json.dumps({"chapters": passed}, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (val / "blocked.json").write_text(
        json.dumps(blocked, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print("\n========= 汇总 =========")
    print(f"放行 {len(passed)} 章：{passed}")
    print(f"拦截 {len(blocked)} 章：{list(blocked.keys())}")
    for ch, info in blocked.items():
        print(f"  {ch} {info['title']}：{len(info['blocks'])} 处")
        for b in info["blocks"]:
            print(f"    [{b['gate']}] {b.get('ref')}: {b.get('msg')}")
    print(
        "\n下一步：blocked 章把上面 blocks 喂给对话层做定向重写；passed 章可 render.py 渲染。"
    )

    sys.exit(1 if blocked else 0)


if __name__ == "__main__":
    main()
