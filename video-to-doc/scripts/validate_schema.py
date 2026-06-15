#!/usr/bin/env python3
"""Stage 4：章节数据结构校验（纯规则，无 AI）。

读取 chNN_data.json，按固定规则检查"该有的字段在不在、该满足的约束满足没有"，
把 error/warning 写到 validation/chNN_schema.json。

只查结构与完整性，不查内容好坏（内容质量由接地校验 + rubric 判官负责）。
error 阻断渲染；warning 不阻断但记录。

依赖：仅标准库。
"""

import argparse
import json
import re
import sys
from pathlib import Path

# 创作字段的接地证据应指向的来源类型
_EVIDENCE_TYPES = {"video", "doc"}


def die(msg: str, code: int = 1):
    print(f"[错误] {msg}", file=sys.stderr)
    sys.exit(code)


def _norm_len(s) -> int:
    return len(re.sub(r"\s+", "", s or ""))


class Checker:
    def __init__(self):
        self.errors: list[dict] = []
        self.warnings: list[dict] = []

    def err(self, ref: str, msg: str):
        self.errors.append({"ref": ref, "msg": msg})

    def warn(self, ref: str, msg: str):
        self.warnings.append({"ref": ref, "msg": msg})

    # ── 章级 ──────────────────────────────────────────────────────────────

    def check_chapter(self, d: dict):
        if len(d.get("learning_outcomes") or []) < 2:
            self.err("learning_outcomes", "量化学习目标少于 2 条")
        if not d.get("prerequisites"):
            self.warn("prerequisites", "未列前置知识")

        kps = d.get("knowledge_points") or []
        if not kps:
            self.err("knowledge_points", "没有任何知识点")
        if len(kps) > 3:
            self.warn("knowledge_points", f"知识点 {len(kps)} 个，超过 3 个建议拆章")
        for i, kp in enumerate(kps):
            self.check_kp(kp.get("id") or f"kp{i + 1}", kp)

        self.check_summary(d.get("summary") or [])
        self.check_exercises(d.get("exercises") or [])

    # ── 知识点级 ──────────────────────────────────────────────────────────

    def check_kp(self, kid: str, kp: dict):
        # what：定义 + 类比，两槽必填
        what = kp.get("what") or {}
        if not what.get("definition"):
            self.err(f"{kid}.what.definition", "缺定义")
        if not what.get("analogy"):
            self.err(f"{kid}.what.analogy", "缺类比（每个概念至少一个类比）")
        self.check_supplementary(f"{kid}.what", what)
        self.check_evidence(f"{kid}.what", what)

        # why：拆三槽——解决什么问题 / 对比替代方案 / 何时不该用
        why = kp.get("why") or {}
        if not why.get("problem_solved"):
            self.err(f"{kid}.why.problem_solved", "缺'解决什么问题'")
        alt = why.get("alternative_compared") or {}
        if not alt.get("name") or not alt.get("tradeoff"):
            self.err(
                f"{kid}.why.alternative_compared",
                "缺替代方案对比（需 name + tradeoff）",
            )
        if not why.get("when_not_to_use"):
            self.warn(f"{kid}.why.when_not_to_use", "缺'何时不该用'")
        self.check_supplementary(f"{kid}.why", why)
        self.check_evidence(f"{kid}.why", why)

        # how：代码必须带 language + version
        how = kp.get("how") or {}
        if not how.get("code"):
            self.err(f"{kid}.how.code", "缺可运行代码")
        else:
            if not how.get("language"):
                self.err(f"{kid}.how.language", "代码缺 language 标注")
            if not how.get("version"):
                self.err(f"{kid}.how.version", "代码缺 version 标注")
            if not how.get("dependencies") and how.get("language") == "python":
                self.warn(
                    f"{kid}.how.dependencies",
                    "未声明 dependencies，闸门 A 将用 import 名兜底",
                )
        # 依赖 OpenAI 必须给国产替代
        if re.search(r"openai|ChatOpenAI", how.get("code", ""), re.I):
            if not (how.get("alternatives") or {}).get("domestic"):
                self.err(
                    f"{kid}.how.alternatives.domestic",
                    "代码依赖 OpenAI，必须补国内可用替代方案",
                )
        self.check_supplementary(f"{kid}.how", how)

        # pitfalls：每条三槽
        pit = kp.get("pitfalls") or {}
        items = pit.get("items") or []
        if not items:
            self.warn(f"{kid}.pitfalls", "没有常见坑（happy-path 思维风险）")
        for j, it in enumerate(items):
            if not all(it.get(k) for k in ("symptom", "cause", "solution")):
                self.err(f"{kid}.pitfalls[{j}]", "坑需三槽：symptom/cause/solution")

    def check_supplementary(self, ref: str, field: dict):
        # 标了补充，就必须有可核验的 doc_url
        if field.get("supplementary") and not field.get("doc_url"):
            self.err(ref, "supplementary=true 但缺 doc_url（无据不许标补充）")

    def check_evidence(self, ref: str, field: dict):
        ev = field.get("evidence")
        if not ev:
            self.err(f"{ref}.evidence", "创作字段缺接地证据 evidence")
            return
        if ev.get("type") not in _EVIDENCE_TYPES:
            self.err(f"{ref}.evidence.type", f"type 必须是 {_EVIDENCE_TYPES}")
        if ev.get("type") == "video" and not ev.get("quote"):
            self.err(f"{ref}.evidence.quote", "video 证据缺原句 quote")
        if ev.get("type") == "doc" and not ev.get("url"):
            self.err(f"{ref}.evidence.url", "doc 证据缺 url")

    # ── 小结 / 练习 ───────────────────────────────────────────────────────

    def check_summary(self, summary: list):
        if len(summary) < 2:
            self.err("summary", "小结少于 2 条")
        elif not str(summary[-1]).startswith("下一章"):
            self.warn("summary", "小结最后一条未以'下一章'开头，缺递进引导")

    def check_exercises(self, exs: list):
        levels = sorted(e.get("level") for e in exs if e.get("level"))
        if levels != [1, 2, 3]:
            self.err("exercises", f"练习必须恰好覆盖 1/2/3 三级，当前 {levels}")
        for e in exs:
            lv = e.get("level")
            ans = e.get("answer") or {}
            if not e.get("requirement"):
                self.err(f"ex{lv}.requirement", "缺需求描述")
            if not ans.get("code"):
                self.err(f"ex{lv}.answer.code", "缺参考答案代码")
            if not ans.get("key_points"):
                self.warn(f"ex{lv}.answer.key_points", "缺关键点说明")


def validate_file(path: Path) -> dict:
    d = json.loads(path.read_text(encoding="utf-8"))
    c = Checker()
    c.check_chapter(d)
    return {
        "chapter_number": d.get("chapter_number"),
        "source": path.name,
        "summary": {"errors": len(c.errors), "warnings": len(c.warnings)},
        "errors": c.errors,
        "warnings": c.warnings,
    }


def main():
    ap = argparse.ArgumentParser(description="Stage 4：章节数据结构校验")
    ap.add_argument("target", help="chNN_data.json 文件，或 chapters/ 目录")
    ap.add_argument("-o", "--out", help="validation 输出目录（默认 ../validation）")
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
    out_dir = Path(args.out) if args.out else (base.parent / "validation")
    out_dir.mkdir(parents=True, exist_ok=True)

    total_err = 0
    for f in files:
        r = validate_file(f)
        ch = r["chapter_number"]
        out = out_dir / (
            f"ch{ch:02d}_schema.json"
            if isinstance(ch, int)
            else f"{f.stem}_schema.json"
        )
        out.write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
        total_err += r["summary"]["errors"]
        flag = "FAIL" if r["summary"]["errors"] else "OK"
        print(
            f"[{flag}] {f.name}: error {r['summary']['errors']}，warning {r['summary']['warnings']} → {out.name}"
        )

    sys.exit(1 if total_err else 0)


if __name__ == "__main__":
    main()
