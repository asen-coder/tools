# video-to-doc

## 这是什么
给定一个 YouTube 或 Bilibili 视频地址，最终输出一份**契合视频内容的中文教学文档**。

## 技术栈
本工具是一条**结构化流水线**，核心理念：用工程降低 AI 理解力对文档质量的影响——AI 做可验证的信息提取，脚本做模板化的组装与校验（详见 SKILL.md「核心理念」）。

- Python 3 脚本（`scripts/`，仅标准库 + yt-dlp，全部无 AI、做脏活）：
  - `fetch_transcript.py`：下载字幕，无字幕时 Whisper 转写。
  - `verify_code.py` / `verify_docs.py` / `validate_schema.py` / `verify_grounding.py`：四道客观闸门。
  - `run_gates.py`：编排器，串联四闸门并汇总 passed/blocked。
  - `render.py`：把章节数据渲染成 Markdown。
- 外部依赖：`yt-dlp`（必需）、`ffmpeg` + `faster-whisper`（仅无字幕兜底）、Playwright MCP（B站）。
- 理解、提取、判类、查权威文档、填章节数据、判质量（rubric）、定向回灌：由对话中的 Claude 完成（见 SKILL.md）。

## 边界
- 不依赖仓库内任何其他工具。
- 关键边界：工程只能把**格式与完整性**做成模型无关，做不到把**内容好坏**做成模型无关。
- 术语约定：
  - "脚本" = `scripts/` 下的 Python，只做脏活（取字幕 / 校验 / 渲染），不产生创作内容。
  - "章节数据" = `chapters/chNN_data.json`，Stage 3 由 Claude 填，是渲染的唯一数据源。
  - "文档" = 最终交付的中文教学 Markdown，由 `render.py` 从章节数据渲染。
  - "闸门" = 渲染前的客观校验，跑不通/无据/缺字段的章被拦下。
  - "核心内容" = 视频口头强调（"重点/注意/划重点/important/key"等）或权威文档明确强调的内容。

## 运行方式
取字幕（脏活，脚本独立可跑）：
```
python scripts/fetch_transcript.py <视频URL> -o ./out
```
完整"出文档"流程：在对话里触发本技能（见 SKILL.md），把视频地址给 Claude。

## 内部结构
- `SKILL.md`        —— 技能定义与完整流水线工作流（开发测试 OK 后整目录同步到 .claude/skills/video-to-doc/）。
- `scripts/`        —— 全部脏活脚本（取字幕 / 四道闸门 / 编排器 / 渲染），各脚本 docstring 是其权威说明。
- `out/`            —— 运行产物（已 gitignore），目录规范见 SKILL.md「产物目录规范」。

## 同步为正式技能
开发测试通过后，把本目录内容复制到 `<仓库根>/.claude/skills/video-to-doc/` 即可被 Claude Code 识别触发。
