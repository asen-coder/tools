# daily-learning

每日英语学习工具，自动推送 LangChain/LangGraph、前端、音乐、日常沟通词汇。

## 目录

```
daily-learning/
├── data/
│   ├── words.json       # 词汇库 + 学习进度（勿手动乱改）
│   └── stats.json       # 打卡连续天数
├── docs/                # GitHub Pages 服务目录（gh-pages 分支）
│   ├── index.html
│   ├── style.css
│   ├── app.js
│   ├── today.json       # 由 generate.py 自动生成
│   └── all_words.json   # 由 generate.py 自动生成
├── scripts/
│   ├── seed.py          # 一次性：初始化词汇库
│   ├── generate.py      # 每日：生成推送内容
│   └── add.py           # 随时：手动添加词汇
└── inbox.csv            # 批量导入模板
```

## 首次初始化

```bash
cd daily-learning
python scripts/seed.py        # 写入初始 120 条词汇
python scripts/generate.py    # 生成 docs/today.json
```

本地预览：在 docs/ 目录启动 HTTP 服务器：
```bash
cd docs && python -m http.server 8080
# 访问 http://localhost:8080
```

## 日常用法

**添加单词（交互）**：
```bash
python scripts/add.py
```

**批量导入**：编辑 `inbox.csv`，然后：
```bash
python scripts/add.py --import inbox.csv
```
导入后清空 inbox.csv 的数据行（保留表头），再 git push 即可。

## GitHub 配置（一次性）

1. 创建 GitHub 仓库并推送代码
2. Settings → Actions → General → Workflow permissions → **Read and write permissions**
3. 等待第一次 Actions 运行后，Settings → Pages → Source → **Deploy from a branch** → Branch: **gh-pages** / **(root)**

访问地址：`https://asen-coder.github.io/<仓库名>/`

## 分类说明

| 分类 | 代码 | 内容 |
|------|------|------|
| AI/LangChain | `ai` | LangChain、LangGraph、大模型通用概念 |
| 前端/编程 | `programming` | Vue、JS、浏览器 API、工程化 |
| 音乐 | `music` | 乐理、演奏术语 |
| 日常沟通 | `daily` | 职场/会议英语句型 |

## 间隔重复阶梯

首次 → 1天 → 3天 → 7天 → 14天 → 30天 → 90天（循环）
