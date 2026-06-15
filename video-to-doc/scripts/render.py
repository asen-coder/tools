#!/usr/bin/env python3
"""Stage 5：章节数据渲染为 Markdown（纯模板，零 AI）。

输入：chNN_data.json（应已通过各闸门）。
输出：out/<教程标题>/第X部分-.../NN-标题.md。
格式问题在这里改模板，与模型无关。

约定：
  - supplementary=true 的字段用蓝色 [补充] 包裹，并附 doc_url。
  - how.alternatives.domestic 存在 → 追加"国内替代方案"折叠块。
  - 练习答案一律 <details> 折叠。

依赖：仅标准库。
"""

import argparse
import json
import sys
from pathlib import Path

_SUP = '<span style="color:#2980b9">**[补充]** {text}</span>'


def die(msg: str, code: int = 1):
    print(f"[错误] {msg}", file=sys.stderr)
    sys.exit(code)


def sup(text: str, field: dict) -> str:
    """按 supplementary 标记包裹文本，附 doc_url。"""
    if not field.get("supplementary"):
        return text
    out = _SUP.format(text=text)
    if field.get("doc_url"):
        out += f"（来源：[{field['doc_url']}]({field['doc_url']})）"
    return out


def render_kp(idx: int, kp: dict) -> str:
    cn = "一二三四五六七八九十"[idx] if idx < 10 else str(idx + 1)
    L = [f"## {cn}、{kp.get('title', '')}\n"]

    what = kp.get("what") or {}
    L.append("### 是什么\n")
    L.append(sup(what.get("definition", ""), what))
    if what.get("analogy"):
        L.append(f"\n\n类比：{what['analogy']}")
    L.append("\n")

    why = kp.get("why") or {}
    L.append("### 为什么这么设计\n")
    L.append(sup(why.get("problem_solved", ""), why))
    alt = why.get("alternative_compared") or {}
    if alt.get("name"):
        L.append(f"\n\n对比 **{alt['name']}**：{alt.get('tradeoff', '')}")
    if why.get("when_not_to_use"):
        L.append(f"\n\n何时不该用：{why['when_not_to_use']}")
    L.append("\n")

    how = kp.get("how") or {}
    L.append("### 怎么用\n")
    if how.get("content"):
        L.append(sup(how["content"], how) + "\n")
    lang = how.get("language", "")
    if how.get("version"):
        L.append(f"\n> 依赖版本：`{how['version']}`\n")
    L.append(f"\n```{lang}\n{how.get('code', '')}\n```\n")
    if how.get("expected_output"):
        L.append(f"\n预期输出：\n\n```\n{how['expected_output']}\n```\n")
    dom = (how.get("alternatives") or {}).get("domestic")
    if dom:
        L.append(
            "\n<details>\n<summary>国内替代方案（无法直连 OpenAI 时）</summary>\n\n"
        )
        L.append(dom)
        L.append("\n\n</details>\n")

    bp = kp.get("best_practices") or {}
    if bp.get("items"):
        L.append("### 最佳实践\n")
        for it in bp["items"]:
            L.append(f"- {sup(it, bp)}")
        L.append("")

    pit = kp.get("pitfalls") or {}
    if pit.get("items"):
        L.append("### 常见坑\n")
        for k, it in enumerate(pit["items"], 1):
            L.append(
                f"- **坑 {k}**：{it.get('symptom', '')}。"
                f"原因：{it.get('cause', '')}。解决：{it.get('solution', '')}"
            )
        L.append("")

    return "\n".join(L)


def render_exercise(ex: dict) -> str:
    stars = "⭐" * ex.get("level", 1)
    tier = {1: "入门", 2: "中级", 3: "挑战"}.get(ex.get("level"), "")
    ans = ex.get("answer") or {}
    L = [
        f"### 练习{ex.get('level')}：{ex.get('title', '')}（{stars} {tier}）\n",
        f"**需求：** {ex.get('requirement', '')}\n",
        f"**提示：** {ex.get('hint', '')}\n",
        "<details>\n<summary>参考答案</summary>\n",
        f"```{ans.get('language', '')}\n{ans.get('code', '')}\n```\n",
    ]
    if ans.get("key_points"):
        L.append(f"**关键点：** {ans['key_points']}\n")
    L.append("</details>\n")
    return "\n".join(L)


def render_chapter(d: dict) -> str:
    n = d.get("chapter_number")
    L = [f"# 第{n}章：{d.get('title', '')}\n"]
    eps = "、".join(d.get("episodes") or [])
    L.append(f"> 对应视频：{eps}")
    if d.get("estimated_minutes"):
        L.append(f"> 预计学习时间：{d['estimated_minutes']} 分钟")
    L.append("")

    L.append("## 学完后你能做什么\n")
    for o in d.get("learning_outcomes") or []:
        L.append(f"- {o}")
    L.append("")

    if d.get("prerequisites"):
        L.append("## 前置知识\n")
        for p in d["prerequisites"]:
            L.append(f"- {p.get('name', '')}：{p.get('level', '')}")
        L.append("")

    L.append("---\n")
    for i, kp in enumerate(d.get("knowledge_points") or []):
        L.append(render_kp(i, kp))
        L.append("---\n")

    L.append("## 本章小结\n")
    for i, s in enumerate(d.get("summary") or [], 1):
        L.append(f"{i}. {s}")
    L.append("\n---\n")

    L.append("## 课后练习\n")
    for ex in sorted(d.get("exercises") or [], key=lambda e: e.get("level", 0)):
        L.append(render_exercise(ex))

    return "\n".join(L)


_CN = "零一二三四五六七八九十"


def part_dirname(d: dict) -> str:
    pn = d.get("part_number")
    cn = _CN[pn] if isinstance(pn, int) and pn < len(_CN) else str(pn)
    return f"第{cn}部分-{d.get('part_title', '')}"


def main():
    ap = argparse.ArgumentParser(description="Stage 5：章节数据渲染为 Markdown")
    ap.add_argument("target", help="chNN_data.json 文件，或 chapters/ 目录")
    ap.add_argument("-o", "--out", required=True, help="教程根目录 out/<教程标题>/")
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

    root = Path(args.out)
    for f in files:
        d = json.loads(f.read_text(encoding="utf-8"))
        part_dir = root / part_dirname(d)
        part_dir.mkdir(parents=True, exist_ok=True)
        n = d.get("chapter_number")
        name = (
            f"{n:02d}-{d.get('title', '')}.md" if isinstance(n, int) else f"{f.stem}.md"
        )
        md_path = part_dir / name
        md_path.write_text(render_chapter(d), encoding="utf-8")
        print(f"[渲染] {f.name} → {md_path.relative_to(root)}")


if __name__ == "__main__":
    main()
