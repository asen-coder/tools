#!/usr/bin/env python3
"""闸门 B：文档引用反查。

读取 Stage 2 产出的 chNN_docs.json，对每条 doc_source：
  1. 拉取 url（404/超时 → url_dead）
  2. 把 excerpt 归一化后在页面正文里模糊匹配（容忍 ≤10% 编辑距离）
  3. 匹配不上 → excerpt_unverified
结果写到 validation/chNN_docs_check.json。

目的：杜绝模型编造 URL / 编造 excerpt，让"权威文档佐证"为真。
一个话题的所有 doc_source 全作废 → 该话题退化为 not_found，
Stage 3 里引用它的字段不许标 supplementary（查无实据）。

纯脏活、无 AI。依赖：仅标准库（urllib）。
"""

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
# 容忍的最大编辑距离占比：文档可能有微调，但不能整段对不上
_MAX_DISTANCE_RATIO = 0.10
# 太短的 excerpt 容易误判命中，要求至少这么长才做模糊匹配
_MIN_EXCERPT_LEN = 12


def die(msg: str, code: int = 1):
    print(f"[错误] {msg}", file=sys.stderr)
    sys.exit(code)


# ── 取页面正文 ────────────────────────────────────────────────────────────────


class _TextExtractor(HTMLParser):
    """剥掉 script/style，抽出可见文本。"""

    _SKIP = {"script", "style", "noscript", "head"}

    def __init__(self):
        super().__init__()
        self._skip_depth = 0
        self.parts: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag in self._SKIP:
            self._skip_depth += 1

    def handle_endtag(self, tag):
        if tag in self._SKIP and self._skip_depth:
            self._skip_depth -= 1

    def handle_data(self, data):
        if self._skip_depth == 0:
            self.parts.append(data)


def fetch_text(url: str, timeout: int) -> tuple[str | None, str | None]:
    """返回 (归一化正文, 错误)。错误非空表示 url_dead。"""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": _UA})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            charset = resp.headers.get_content_charset() or "utf-8"
        html = raw.decode(charset, errors="ignore")
    except urllib.error.HTTPError as e:
        return None, f"HTTP {e.code}"
    except Exception as e:
        return None, f"{e.__class__.__name__}: {e}"

    parser = _TextExtractor()
    try:
        parser.feed(html)
    except Exception:
        pass
    return _norm(" ".join(parser.parts)), None


# ── 模糊匹配 ──────────────────────────────────────────────────────────────────


def _norm(s: str) -> str:
    # 归一化：小写、压缩空白、去掉零宽字符
    s = s.lower().replace("​", "")
    return re.sub(r"\s+", " ", s).strip()


def _min_window_distance(needle: str, haystack: str) -> int:
    """needle 与 haystack 中任一等长窗口的最小编辑距离（带早停）。

    先尝试子串直接命中（距离 0）；否则在候选位置上算 Levenshtein。
    候选位置用 needle 首词锚定，避免全文滑窗的 O(n*m)。
    """
    if needle in haystack:
        return 0

    n = len(needle)
    anchor = needle.split(" ", 1)[0]
    starts = [m.start() for m in re.finditer(re.escape(anchor), haystack)]
    if not starts:
        # 锚词都找不到，取整串首字符位置粗扫前若干处
        starts = list(range(0, max(1, len(haystack) - n), max(1, n // 2)))[:50]

    budget = int(n * _MAX_DISTANCE_RATIO) + 1
    best = n
    for st in starts:
        window = haystack[st : st + n]
        d = _bounded_levenshtein(needle, window, budget)
        if d < best:
            best = d
            if best == 0:
                break
    return best


def _bounded_levenshtein(a: str, b: str, budget: int) -> int:
    """带上界早停的编辑距离；超过 budget 直接返回 budget+1。"""
    la, lb = len(a), len(b)
    if abs(la - lb) > budget:
        return budget + 1
    prev = list(range(lb + 1))
    for i in range(1, la + 1):
        cur = [i] + [0] * lb
        row_min = cur[0]
        for j in range(1, lb + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + cost)
            row_min = min(row_min, cur[j])
        if row_min > budget:
            return budget + 1
        prev = cur
    return prev[lb]


def excerpt_matches(excerpt: str, page_text: str) -> tuple[bool, float]:
    """返回 (是否命中, 实际距离占比)。"""
    needle = _norm(excerpt)
    if len(needle) < _MIN_EXCERPT_LEN:
        # 太短，退化为严格子串判断，避免误命中
        return (needle in page_text, 0.0 if needle in page_text else 1.0)
    dist = _min_window_distance(needle, page_text)
    ratio = dist / max(1, len(needle))
    return ratio <= _MAX_DISTANCE_RATIO, round(ratio, 3)


# ── 主流程 ────────────────────────────────────────────────────────────────────


def check_file(path: Path, timeout: int) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    topics = data.get("topics") or {}

    checked: list[dict] = []
    page_cache: dict[str, tuple[str | None, str | None]] = {}
    topic_status: dict[str, dict] = {}

    for tid, topic in topics.items():
        sources = topic.get("doc_sources") or []
        alive_verified = 0

        for src in sources:
            url = src.get("url", "")
            excerpt = src.get("excerpt", "")

            if url not in page_cache:
                page_cache[url] = fetch_text(url, timeout)
            page_text, err = page_cache[url]

            if err:
                checked.append(
                    {
                        "topic": tid,
                        "url": url,
                        "url_dead": True,
                        "excerpt_verified": False,
                        "reason": err,
                    }
                )
                continue

            ok, ratio = excerpt_matches(excerpt, page_text or "")
            checked.append(
                {
                    "topic": tid,
                    "url": url,
                    "url_dead": False,
                    "excerpt_verified": ok,
                    "distance_ratio": ratio,
                }
            )
            if ok:
                alive_verified += 1

        # 该话题是否还有可信来源；原 not_found 也保留
        degraded = len(sources) > 0 and alive_verified == 0
        topic_status[tid] = {
            "sources_total": len(sources),
            "sources_verified": alive_verified,
            "degraded_to_not_found": degraded,
            "was_not_found": bool(topic.get("not_found")),
        }

    n_bad = sum(1 for c in checked if c["url_dead"] or not c["excerpt_verified"])
    degraded = [t for t, s in topic_status.items() if s["degraded_to_not_found"]]

    return {
        "chapter_number": data.get("chapter_number"),
        "source": path.name,
        "summary": {
            "sources_checked": len(checked),
            "sources_invalid": n_bad,
            "topics_degraded": degraded,
        },
        "topic_status": topic_status,
        "checked": checked,
    }


def main():
    ap = argparse.ArgumentParser(description="闸门 B：文档引用反查")
    ap.add_argument("target", help="chNN_docs.json 文件，或包含它们的 analysis/ 目录")
    ap.add_argument(
        "-o", "--out", help="validation 输出目录（默认 target 同级 ../validation）"
    )
    ap.add_argument(
        "--timeout", type=int, default=20, help="单个 URL 拉取超时秒数（默认 20）"
    )
    args = ap.parse_args()

    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")

    target = Path(args.target)
    if not target.exists():
        die(f"目标不存在: {target}")

    files = sorted(target.glob("ch*_docs.json")) if target.is_dir() else [target]
    if not files:
        die("未找到 ch*_docs.json")

    base = target if target.is_dir() else target.parent
    out_dir = Path(args.out) if args.out else (base.parent / "validation")
    out_dir.mkdir(parents=True, exist_ok=True)

    overall_bad = 0
    for f in files:
        report = check_file(f, args.timeout)
        ch = report["chapter_number"]
        out_path = (
            (out_dir / f"ch{ch:02d}_docs_check.json")
            if isinstance(ch, int)
            else (out_dir / f"{f.stem}_check.json")
        )
        out_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        s = report["summary"]
        overall_bad += s["sources_invalid"]
        flag = "FAIL" if (s["sources_invalid"] or s["topics_degraded"]) else "OK"
        print(
            f"[{flag}] {f.name}: 失效来源 {s['sources_invalid']}/{s['sources_checked']}，"
            f"退化话题 {len(s['topics_degraded'])} → {out_path.name}"
        )

    sys.exit(1 if overall_bad else 0)


if __name__ == "__main__":
    main()
