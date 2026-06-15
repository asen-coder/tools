#!/usr/bin/env python3
"""C2：接地校验（offline，无 AI）。

防"幻觉式解释"——字段说得头头是道，但视频里根本没这回事。
对 chNN_data.json 里每个带 evidence 的创作字段：
  - type=video：去对应 epNN_extraction.json 里核对 quote 确实存在（模糊子串）
  - type=doc：复用闸门 B 的 chNN_docs_check.json，确认该 url 已验证通过
对不上 → evidence_unverified，判 error。

把"模型有没有瞎编"从主观变成可机器抽查。
依赖：仅标准库。
"""

import argparse
import json
import re
import sys
from pathlib import Path

_FUZZ = 0.15  # video quote 允许的编辑距离占比（字幕本身口语化，放宽于文档）
_MIN_LEN = 6


def die(msg: str, code: int = 1):
    print(f"[错误] {msg}", file=sys.stderr)
    sys.exit(code)


def _norm(s: str) -> str:
    return re.sub(r"\s+", "", (s or "").lower())


def _bounded_lev(a: str, b: str, budget: int) -> int:
    la, lb = len(a), len(b)
    if abs(la - lb) > budget:
        return budget + 1
    prev = list(range(lb + 1))
    for i in range(1, la + 1):
        cur = [i] + [0] * lb
        rmin = cur[0]
        for j in range(1, lb + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + cost)
            rmin = min(rmin, cur[j])
        if rmin > budget:
            return budget + 1
        prev = cur
    return prev[lb]


def quote_in_text(quote: str, text: str) -> bool:
    q = _norm(quote)
    if len(q) < _MIN_LEN:
        return q in text
    if q in text:
        return True
    budget = int(len(q) * _FUZZ) + 1
    anchor = q[:4]
    for m in re.finditer(re.escape(anchor), text):
        st = m.start()
        if _bounded_lev(q, text[st : st + len(q)], budget) <= budget - 1:
            return True
    return False


def load_episode_text(ep_ref: str, analysis_dir: Path) -> str | None:
    """ep_ref 形如 'ep01.t1' 或 'ep01'，取该集 extraction 的全部文本拼接。"""
    ep = ep_ref.split(".", 1)[0]
    f = analysis_dir / f"{ep}_extraction.json"
    if not f.exists():
        return None
    data = json.loads(f.read_text(encoding="utf-8"))
    chunks: list[str] = []
    for t in data.get("topics") or []:
        chunks.append(t.get("title", ""))
        chunks.extend(t.get("key_claims") or [])
        for em in t.get("emphasis_markers") or []:
            chunks.append(em.get("text", ""))
            chunks.append(em.get("context", ""))
    return _norm(" ".join(chunks))


def load_verified_urls(ch: int, validation_dir: Path) -> set[str]:
    f = validation_dir / f"ch{ch:02d}_docs_check.json"
    if not f.exists():
        return set()
    data = json.loads(f.read_text(encoding="utf-8"))
    return {c["url"] for c in data.get("checked") or [] if c.get("excerpt_verified")}


def iter_evidence_fields(d: dict):
    """产出 (ref, evidence) ——所有带 evidence 的创作字段。"""
    for i, kp in enumerate(d.get("knowledge_points") or []):
        kid = kp.get("id") or f"kp{i + 1}"
        for fname in ("what", "why", "how"):
            field = kp.get(fname) or {}
            if field.get("evidence"):
                yield f"{kid}.{fname}", field["evidence"]


def check_file(path: Path, analysis_dir: Path, validation_dir: Path) -> dict:
    d = json.loads(path.read_text(encoding="utf-8"))
    ch = d.get("chapter_number")
    verified_urls = (
        load_verified_urls(ch, validation_dir) if isinstance(ch, int) else set()
    )

    results: list[dict] = []
    ep_text_cache: dict[str, str | None] = {}

    for ref, ev in iter_evidence_fields(d):
        etype = ev.get("type")
        if etype == "video":
            epref = ev.get("ref", "")
            ep = epref.split(".", 1)[0]
            if ep not in ep_text_cache:
                ep_text_cache[ep] = load_episode_text(epref, analysis_dir)
            text = ep_text_cache[ep]
            if text is None:
                results.append(
                    {
                        "ref": ref,
                        "type": "video",
                        "status": "fail",
                        "reason": f"找不到 {ep}_extraction.json，无法核对",
                    }
                )
            elif quote_in_text(ev.get("quote", ""), text):
                results.append({"ref": ref, "type": "video", "status": "pass"})
            else:
                results.append(
                    {
                        "ref": ref,
                        "type": "video",
                        "status": "fail",
                        "reason": "quote 在该集字幕提取里找不到（疑似杜撰）",
                        "fix_hint": "改用字幕真实出现的原句，或把该字段标 supplementary 并补 doc_url",
                    }
                )
        elif etype == "doc":
            url = ev.get("url", "")
            if url in verified_urls:
                results.append({"ref": ref, "type": "doc", "status": "pass"})
            else:
                results.append(
                    {
                        "ref": ref,
                        "type": "doc",
                        "status": "fail",
                        "reason": "url 未在闸门 B 中验证通过",
                        "fix_hint": "先让该 url 通过 verify_docs，或换一个已验证来源",
                    }
                )
        else:
            results.append(
                {
                    "ref": ref,
                    "type": etype,
                    "status": "fail",
                    "reason": f"未知 evidence type: {etype}",
                }
            )

    n_fail = sum(1 for r in results if r["status"] == "fail")
    return {
        "chapter_number": ch,
        "source": path.name,
        "summary": {"checked": len(results), "fail": n_fail},
        "results": results,
    }


def main():
    ap = argparse.ArgumentParser(description="C2：接地校验")
    ap.add_argument("target", help="chNN_data.json 文件，或 chapters/ 目录")
    ap.add_argument("--analysis", help="extraction 所在目录（默认 ../analysis）")
    ap.add_argument("--validation", help="闸门 B 输出所在目录（默认 ../validation）")
    ap.add_argument("-o", "--out", help="输出目录（默认 ../validation）")
    args = ap.parse_args()

    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8")

    target = Path(args.target)
    if not target.exists():
        die(f"目标不存在: {target}")

    files = sorted(target.glob("ch*_data.json")) if target.is_dir() else [target]
    if not files:
        die("未找到 ch*_data.json")

    base = target if target.is_dir() else target.parent
    analysis_dir = Path(args.analysis) if args.analysis else (base.parent / "analysis")
    validation_dir = (
        Path(args.validation) if args.validation else (base.parent / "validation")
    )
    out_dir = Path(args.out) if args.out else (base.parent / "validation")
    out_dir.mkdir(parents=True, exist_ok=True)

    total_fail = 0
    for f in files:
        r = check_file(f, analysis_dir, validation_dir)
        ch = r["chapter_number"]
        out = out_dir / (
            f"ch{ch:02d}_grounding.json"
            if isinstance(ch, int)
            else f"{f.stem}_grounding.json"
        )
        out.write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
        total_fail += r["summary"]["fail"]
        flag = "FAIL" if r["summary"]["fail"] else "OK"
        print(
            f"[{flag}] {f.name}: 接地失败 {r['summary']['fail']}/{r['summary']['checked']} → {out.name}"
        )

    sys.exit(1 if total_fail else 0)


if __name__ == "__main__":
    main()
