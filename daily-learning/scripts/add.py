"""手动添加词汇：交互模式 或 CSV 批量导入。

用法：
  python add.py               # 交互式逐条添加
  python add.py --import inbox.csv
"""

import csv
import json
import os
import sys
from datetime import date

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPTS_DIR)
WORDS_FILE = os.path.join(PROJECT_DIR, "data", "words.json")

CATEGORIES = {"programming", "ai", "music", "daily", "general"}
PREFIXES = {
    "programming": "prog",
    "ai": "ai",
    "music": "music",
    "daily": "daily",
    "general": "gen",
}


def load_words():
    with open(WORDS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_words(words):
    with open(WORDS_FILE, "w", encoding="utf-8") as f:
        json.dump(words, f, ensure_ascii=False, indent=2)


def next_id(words, category):
    prefix = PREFIXES[category]
    nums = [
        int(w["id"].split("_")[1]) for w in words if w["id"].startswith(prefix + "_")
    ]
    return f"{prefix}_{(max(nums) + 1 if nums else 1):03d}"


def make_word(category, en, zh, definition, example, difficulty, words):
    return {
        "id": next_id(words, category),
        "category": category,
        "en": en,
        "zh": zh,
        "definition": definition,
        "example": example,
        "difficulty": difficulty,
        "next_review": date.today().isoformat(),
        "review_count": 0,
        "status": "new",
    }


def interactive(words):
    existing = {w["en"].lower() for w in words}

    while True:
        print("\n── 添加新词汇 ──")

        cat = ""
        while cat not in CATEGORIES:
            cat = input("分类 [programming / ai / music / daily]: ").strip().lower()

        en = input("英文: ").strip()
        if not en:
            print("英文不能为空，跳过")
        elif en.lower() in existing:
            print(f"「{en}」已存在，跳过")
        else:
            zh = input("中文: ").strip()
            definition = input("释义: ").strip()
            example = input("例句（可留空）: ").strip()

            diff = 0
            while diff not in range(1, 6):
                try:
                    diff = int(input("难度 1-5: ").strip())
                except ValueError:
                    pass

            word = make_word(cat, en, zh, definition, example, diff, words)
            words.append(word)
            existing.add(en.lower())
            print(f"✓ 已添加「{en}」，词库共 {len(words)} 条")

        if input("\n继续添加？[y/N]: ").strip().lower() != "y":
            break


def import_csv(words, csv_path):
    existing = {w["en"].lower() for w in words}
    added = skipped = 0

    with open(csv_path, "r", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            en = row.get("en", "").strip()
            cat = row.get("category", "").strip().lower()

            if not en or en.lower() in existing or cat not in CATEGORIES:
                skipped += 1
                continue

            try:
                diff = max(1, min(5, int(row.get("difficulty", 2))))
            except (ValueError, TypeError):
                diff = 2

            word = make_word(
                cat,
                en,
                row.get("zh", "").strip(),
                row.get("definition", "").strip(),
                row.get("example", "").strip(),
                diff,
                words,
            )
            words.append(word)
            existing.add(en.lower())
            added += 1

    print(f"✓ 导入 {added} 条，跳过 {skipped} 条")


def main():
    words = load_words()

    if "--import" in sys.argv:
        idx = sys.argv.index("--import")
        if idx + 1 >= len(sys.argv):
            print("用法: python add.py --import inbox.csv")
            sys.exit(1)
        path = sys.argv[idx + 1]
        if not os.path.exists(path):
            print(f"文件不存在: {path}")
            sys.exit(1)
        import_csv(words, path)
    else:
        interactive(words)

    save_words(words)
    print(f"词库已保存，共 {len(words)} 条")


if __name__ == "__main__":
    main()
