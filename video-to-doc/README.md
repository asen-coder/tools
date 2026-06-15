# video-to-doc

给定 YouTube / Bilibili 视频地址，输出一套**中文教学文档**：清洗字幕、按视频节奏分章、技术类内容对照权威文档校验、每章配课后练习。

## 核心理念：工程化降低 AI 方差

文档质量不应完全取决于模型聪明程度。本工具把"一个大的理解+生成任务"拆成**结构化流水线**：

> 让 AI 做可验证的信息提取，让脚本做模板化的组装与校验。

渲染前有四道**客观闸门**把关——代码跑不通、文档 URL 编造、字段缺失、解释无字幕依据的章节会被拦下，从而把质量从"靠模型聪明"尽量转成"靠能否运行、有没有依据"。

**诚实的边界**：工程能把*格式与完整性*做成模型无关，但*内容的精彩程度*（类比是否贴切、为什么讲得透不透）天花板仍归模型。

## 目录结构

```
├── CLAUDE.md     # 项目说明（技术栈、边界、术语）
├── SKILL.md      # 技能定义 + 完整流水线工作流 + 质量自检标准
├── scripts/      # 全部脏活脚本（仅标准库，无 AI）
│   ├── fetch_transcript.py   # 取字幕 / Whisper 转写
│   ├── verify_code.py        # 闸门A：代码执行验证
│   ├── verify_docs.py        # 闸门B：文档 URL 反查 + excerpt 核对
│   ├── validate_schema.py    # Stage4：章节数据结构校验
│   ├── verify_grounding.py   # C2：接地校验（防杜撰解释）
│   ├── run_gates.py          # 编排器：串四闸门，汇总 passed/blocked
│   ├── render.py             # Stage5：章节数据 → Markdown
│   └── debug_subtitle.py     # 辅助：调试 B站字幕 API
└── out/          # 产物目录（gitignore）
```

## 流水线

```
字幕  → 单集提取 → 章节规划 → 文档检索 → 章节数据(chNN_data.json)
      → 四道闸门(run_gates) → rubric判官 → 定向回灌 → 渲染(render) → 文档
        └ 脚本，无 AI ┘        └ Claude，需强模型 ┘   └ 脚本 ┘
```

- 取字幕、闸门、渲染：`scripts/` 脏活脚本，独立可跑、可测试。
- 提取、规划、填数据、判质量、回灌：对话中的 Claude 完成，规则见 `SKILL.md`。

## 快速开始

```bash
# 1. 安装依赖
pip install yt-dlp

# 2. 取字幕（B站需 Cookie，详见 SKILL.md 第 1 步）
python scripts/fetch_transcript.py <视频URL> -o ./out

# 3. 对 AI 说"把这个视频转成教程"，AI 按 SKILL.md 流水线逐阶段产出 chapters/chNN_data.json

# 4. 跑闸门校验（跑不通/无据/缺字段的章会被拦）
python scripts/run_gates.py out/<教程标题>/

# 5. 渲染放行的章为 Markdown
python scripts/render.py out/<教程标题>/chapters/ -o out/<教程标题>/
```

## 产物示例

```
out/LangChain从入门到精通/
├── README.md                    # 教程总览
├── raw/subtitles/               # 原始字幕归档
├── analysis/                    # 提取 / 规划 / 检索中间产物
├── chapters/chNN_data.json      # 章节数据（渲染唯一数据源）
├── validation/                  # 闸门产物：passed.json / blocked.json / ...
├── 第一部分-LangChain1.2新版特性/
│   ├── 01-简介与核心概念.md
│   └── ...
├── 第二部分-LangChain1.0完整课程/
└── 第三部分-进阶应用/
```

每章包含：学完后能做什么 → 前置知识 → 知识点（是什么/为什么/怎么用/最佳实践/常见坑）→ 小结 → 课后练习（⭐⭐⭐）。
