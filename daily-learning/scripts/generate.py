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
NEW_PER_DAY = 5

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

    update_streak(stats, today_str)

    due_reviews = []
    new_queue = []

    for w in words:
        if w["status"] == "new":
            new_queue.append(w)
        elif w["status"] == "learning" and w["next_review"] <= today_str:
            due_reviews.append(w)

    # 按难度从低到高推新词
    new_queue.sort(key=lambda x: (x["difficulty"], x["id"]))
    todays_new = new_queue[:NEW_PER_DAY]

    # 更新已推送词汇的下次复习时间
    shown_ids = {w["id"] for w in todays_new + due_reviews}
    for w in words:
        if w["id"] in shown_ids:
            rc = w["review_count"]
            interval = next_interval(rc)
            w["next_review"] = (today + timedelta(days=interval)).isoformat()
            w["review_count"] = rc + 1
            w["status"] = "learning"

    save_json(WORDS_FILE, words)
    save_json(STATS_FILE, stats)

    # 统计数据
    total = len(words)
    mastered = sum(1 for w in words if w["review_count"] >= len(INTERVALS))
    learning = sum(1 for w in words if w["status"] == "learning")
    new_count = sum(1 for w in words if w["status"] == "new")

    # 生成 today.json（供网页主页面使用）
    today_data = {
        "date": today_str,
        "day_of_week": day_name,
        "new_words": todays_new,
        "reviews": due_reviews,
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

    # 生成 all_words.json（供词库页面使用，按需加载）
    all_words_data = {
        "generated": today_str,
        "words": words,
    }
    save_json(os.path.join(DOCS_DIR, "all_words.json"), all_words_data)

    print(
        f"{today_str} 生成完成：新词 {len(todays_new)} | 复习 {len(due_reviews)} | 连续打卡 {stats['streak']} 天"
    )


if __name__ == "__main__":
    main()
