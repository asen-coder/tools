"""每日内容生成脚本，由 GitHub Actions 自动调用。"""

import json
import os
from datetime import date, timedelta

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPTS_DIR)
WORDS_FILE = os.path.join(PROJECT_DIR, "data", "words.json")
STATS_FILE = os.path.join(PROJECT_DIR, "data", "stats.json")
DOCS_DIR = os.path.join(PROJECT_DIR, "docs")

# 间隔重复阶梯（天数）
INTERVALS = [1, 3, 7, 14, 30, 90]
NEW_VOCAB_PER_DAY = 10  # ai / programming / music
NEW_SENTENCES_PER_DAY = 3  # daily

DAY_NAMES = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]


def next_interval(review_count):
    idx = min(review_count, len(INTERVALS) - 1)
    return INTERVALS[idx]


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def update_streak(stats, today_str):
    last = stats.get("last_generated")
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    if last == today_str:
        return  # 今天已经跑过，不重复计算
    if last == yesterday:
        stats["streak"] = stats.get("streak", 0) + 1
    else:
        stats["streak"] = 1
    stats["last_generated"] = today_str
    stats["total_sessions"] = stats.get("total_sessions", 0) + 1


def main():
    today = date.today()
    today_str = today.isoformat()
    day_name = DAY_NAMES[today.weekday()]

    words = load_json(WORDS_FILE)
    stats = load_json(STATS_FILE)

    already_run_today = stats.get("last_generated") == today_str
    update_streak(stats, today_str)

    due_vocab_reviews = []
    due_sentence_reviews = []
    new_vocab_queue = []
    new_sentence_queue = []

    for w in words:
        is_sentence = w["category"] == "daily"
        if w["status"] == "new":
            (new_sentence_queue if is_sentence else new_vocab_queue).append(w)
        elif w["status"] == "learning" and w["next_review"] <= today_str:
            (due_sentence_reviews if is_sentence else due_vocab_reviews).append(w)

    new_vocab_queue.sort(key=lambda x: (x["difficulty"], x["id"]))
    new_sentence_queue.sort(key=lambda x: (x["difficulty"], x["id"]))

    if not already_run_today:
        # 每天只推一次新词，防止 workflow 多次触发导致超额推送
        todays_vocab = new_vocab_queue[:NEW_VOCAB_PER_DAY]
        todays_sentences = new_sentence_queue[:NEW_SENTENCES_PER_DAY]
        shown_ids = {
            w["id"]
            for w in todays_vocab
            + todays_sentences
            + due_vocab_reviews
            + due_sentence_reviews
        }
        for w in words:
            if w["id"] in shown_ids:
                rc = w["review_count"]
                w["next_review"] = (
                    today + timedelta(days=next_interval(rc))
                ).isoformat()
                w["review_count"] = rc + 1
                w["status"] = "learning"
        save_json(WORDS_FILE, words)
        save_json(STATS_FILE, stats)
    else:
        todays_vocab = []
        todays_sentences = []

    total = len(words)
    mastered = sum(1 for w in words if w["review_count"] >= len(INTERVALS))
    learning = sum(1 for w in words if w["status"] == "learning")
    new_count = sum(1 for w in words if w["status"] == "new")

    today_data = {
        "date": today_str,
        "day_of_week": day_name,
        "new_words": todays_vocab,
        "new_sentences": todays_sentences,
        "vocab_reviews": due_vocab_reviews,
        "sentence_reviews": due_sentence_reviews,
        "stats": {
            "total": total,
            "mastered": mastered,
            "learning": learning,
            "new": new_count,
            "streak": stats["streak"],
            "total_sessions": stats["total_sessions"],
        },
    }

    os.makedirs(DOCS_DIR, exist_ok=True)
    save_json(os.path.join(DOCS_DIR, "today.json"), today_data)

    all_words_data = {"generated": today_str, "words": words}
    save_json(os.path.join(DOCS_DIR, "all_words.json"), all_words_data)

    build_reference(words, today_str)

    print(
        f"{today_str} 生成完成："
        f"新词 {len(todays_vocab)} | 新句 {len(todays_sentences)} | "
        f"复习词 {len(due_vocab_reviews)} | 复习句 {len(due_sentence_reviews)} | "
        f"连续打卡 {stats['streak']} 天"
    )


DIFF_MARKS = ["", "★", "★★", "★★★", "★★★★", "★★★★★"]
CAT_ORDER = ["ai", "programming", "music", "daily"]
CAT_NAMES = {
    "ai": "AI / LangChain / LangGraph",
    "programming": "编程 / 前端",
    "music": "音乐",
    "daily": "日常沟通",
}


def build_reference(words, today_str):
    lines = [
        "# 词汇参考文档",
        "",
        f"> 更新于 {today_str}，共 {len(words)} 条词汇。",
        "> 按分类 + 难度排列，难度 ★ 最低，★★★★★ 最高。",
        "",
    ]

    by_cat = {c: [] for c in CAT_ORDER}
    for w in words:
        if w["category"] in by_cat:
            by_cat[w["category"]].append(w)

    for cat in CAT_ORDER:
        group = sorted(by_cat[cat], key=lambda x: (x["difficulty"], x["id"]))
        if not group:
            continue

        lines += [f"## {CAT_NAMES[cat]}", ""]

        for w in group:
            diff = DIFF_MARKS[w["difficulty"]]
            status_mark = "✓" if w["status"] == "learning" else "○"
            lines.append(f"### {w['en']} · {w['zh']}  {diff}")
            lines.append("")
            lines.append(f"{w['definition']}")
            if w.get("example"):
                lines.append("")
                lines.append("```")
                lines.append(w["example"])
                lines.append("```")
            lines.append("")
            lines.append(
                f"*状态：{status_mark} {'已开始学习' if w['status'] == 'learning' else '待学习'}*"
            )
            lines.append("")

    ref_path = os.path.join(PROJECT_DIR, "REFERENCE.md")
    with open(ref_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    main()
