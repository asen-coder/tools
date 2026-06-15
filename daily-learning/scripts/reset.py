"""重置学习进度，把所有词汇状态恢复为「待学习」。词汇内容不变。"""

import json
import os
from datetime import date

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPTS_DIR)
WORDS_FILE = os.path.join(PROJECT_DIR, "data", "words.json")
STATS_FILE = os.path.join(PROJECT_DIR, "data", "stats.json")


def main():
    today = date.today().isoformat()

    with open(WORDS_FILE, "r", encoding="utf-8") as f:
        words = json.load(f)

    for w in words:
        w["status"] = "new"
        w["review_count"] = 0
        w["next_review"] = today

    with open(WORDS_FILE, "w", encoding="utf-8") as f:
        json.dump(words, f, ensure_ascii=False, indent=2)

    stats = {"streak": 0, "last_generated": None, "total_sessions": 0}
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

    print(f"进度已重置，共 {len(words)} 条词汇全部恢复为「待学习」")


if __name__ == "__main__":
    main()
