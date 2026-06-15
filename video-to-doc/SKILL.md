---
name: video-to-doc
description: 给定 YouTube 或 Bilibili 视频地址，输出契合视频内容的中文教学文档。当用户提供视频链接并希望生成教程、笔记、讲义或学习文档时使用。
---

# video-to-doc

把一个 YouTube / Bilibili 视频转成一份**中文教学文档**：精简字幕但不丢核心，按视频节奏组织，技术类内容对照权威文档校验。

## 核心理念：工程化降低 AI 方差

文档质量不应该完全取决于模型聪明程度。本技能把"一个大的理解+生成任务"拆成**结构化流水线**：

> **让 AI 做信息提取（有标准答案、可验证），让脚本做信息组装（模板化、可测试）。**

**关键边界（必须诚实对待）**：工程只能把**格式与完整性**做成模型无关，做不到把**内容好坏**做成模型无关。策略是把"好不好"尽量拆成"在不在 / 对不对 / 有没有依据"这种机器或弱模型也能判的小问题，再用一个强模型判官兜住纯创作下限。

## 流水线总览

```
raw/subtitles/epNN.json
  │ Stage 1a  你：单集结构化提取            → analysis/epNN_extraction.json
  │ Stage 1b  你：章节规划（判断合并）      → analysis/chapter_plan.json
  │ Stage 2   你+脚本：文档检索             → analysis/chNN_docs.json
  │ Stage 3   你：填章节数据（核心锚点）    → chapters/chNN_data.json
  │ Stage 4   脚本：四道机器闸门            → validation/*.json
  │           run_gates.py 汇总 passed/blocked
  │ C3        你（强模型）：rubric 判官      → validation/chNN_rubric.json
  │ 回灌      你：对 blocked 做局部字段重写
  │ Stage 5   脚本：渲染                     → 第X部分/NN-标题.md
  ▼
教学文档
```

脏活（下载字幕、跑代码、查 URL、渲染）交给 `scripts/`；理解、判类、提取、填数据、判质量由你（Claude）完成。

---

## 1. 取字幕

### YouTube
直接运行脚本，无需额外配置：
```
python scripts/fetch_transcript.py <视频URL> -o ./out
```

### B站（必读！有坑）

**坑 1：412 Precondition Failed**
yt-dlp 直接访问 B站会被拒绝（HTTP 412），必须携带登录 Cookie。

**解决方案 A（推荐）：用 Playwright 提取 Cookie**
1. 用 `mcp__playwright__browser_navigate` 打开 B站视频页面
2. 如用户已在浏览器登录 B站，请用户确认登录状态
3. 用 `mcp__playwright__browser_evaluate` 提取 Cookie：`() => document.cookie`
4. 把 Cookie 写成 Netscape 格式文件（`out/.cache/bili_cookies.txt`）：
   ```
   # Netscape HTTP Cookie File
   .bilibili.com	TRUE	/	FALSE	<过期时间戳>	<name>	<value>
   ```
   关键 Cookie 字段：`DedeUserID`、`DedeUserID__ckMd5`、`bili_jct`、`buvid3`、`buvid4`
5. 运行脚本时传入 Cookie 文件：
   ```
   python scripts/fetch_transcript.py <url> --cookies out/.cache/bili_cookies.txt -o ./out
   ```

**解决方案 B：用户手动导出**
让用户用浏览器插件（如 "Get cookies.txt LOCALLY"）导出 `bilibili.com` 的 Cookie，然后传 `--cookies`。

**坑 2：`--cookies-from-browser` 在 Windows 上失败**
yt-dlp 的 `--cookies-from-browser chrome/edge` 在 Windows 上因 DPAPI 加密问题失败（`Could not copy Cookie database` / `Failed to decrypt with DPAPI`）。**不要用这个方式**，用上面的 Playwright 方案代替。

**坑 3：B站 AI 字幕不走标准字幕接口**
B站 AI 字幕走独立的 `aisubtitle.hdslb.com` CDN，需要通过播放器 API 获取 URL：
```js
// 在 Playwright 已登录页面里执行
async () => {
  const aid = window.__INITIAL_STATE__.aid;
  const cid = window.__INITIAL_STATE__.cid;
  const resp = await fetch(`https://api.bilibili.com/x/player/wbi/v2?aid=${aid}&cid=${cid}`, { credentials: 'include' });
  const data = await resp.json();
  const sub = data.data?.subtitle?.subtitles?.find(s => s.lan === 'ai-zh');
  return sub?.subtitle_url;  // //aisubtitle.hdslb.com/... 格式
}
```
字幕 URL 以 `//` 开头，补全 `https:` 后直接下载，不需要 Cookie（公开 CDN）。
字幕格式：`{"body": [{"from": 0.0, "to": 2.5, "content": "文本"}]}`

**坑 4：auth_key 有时效**
B站字幕 URL 里的 `auth_key` 有效期约几分钟。拿到 URL 后立刻下载，不要存 URL 等待。

### B站系列视频（多集）
1. 从 `window.__INITIAL_STATE__.videoData.pages` 拿全部集的 `cid` 列表
2. 在 Playwright 里循环调 `/x/player/wbi/v2` API 批量取字幕 URL
3. 用 Python（urllib）下载每集到 `out/<教程标题>/raw/subtitles/ep{N:02d}.json`
4. **每集独立存储，不要合并成一个大文件**（合并后可能超 100 万字符、超出 context）

字幕来源会写进 meta：`bilibili-ai-subtitle`（口语化、断句不全，需多清洗）/ `whisper`（语音转写，错别字多，理解放宽）/ `subtitle`（标准字幕）。

---

## Stage 1a：单集结构化提取（每集一次，可并行）

**输入**：`raw/subtitles/epNN.json`
**你做的是分类+摘录，不是创作**：把字幕流切成话题段，逐段提取标题、关键断言、强调标记、代码片段，并判断这集与前后集的连续性（供合并决策）。

**规则**：
- 去滚动重复（相邻完全相同的字幕合并）
- 强调标记：原文出现"重点/注意/记住/划重点/关键/important/key/note"等 → 连同上下文存入 `emphasis_markers`
- 代码片段即使不完整也提取，标 `complete:false`
- 连续性：开头明显接上集 → `continues_from_prev:true`；结尾无收束 → `continues_to_next:true`

**输出**：`analysis/epNN_extraction.json`
```json
{
  "episode": "ep01",
  "episode_title": "简介与核心概念",
  "continuity": {"continues_from_prev": false, "continues_to_next": false, "reason": "独立成章"},
  "prerequisites_implied": ["Python 基础"],
  "topics": [
    {"id": "t1", "title": "什么是 LangChain", "time_start": 0, "time_end": 183,
     "key_claims": ["LangChain 是构建 LLM 应用的开源框架"],
     "emphasis_markers": [{"text": "这个是核心，一定要理解", "time": 45, "context": "..."}],
     "code_fragments": [{"code": "from langchain_core.prompts import ChatPromptTemplate", "complete": true}]}
  ]
}
```
> `key_claims` 和 `emphasis_markers.text/context` 后续会被接地校验（verify_grounding.py）拿去核对，所以必须是字幕里真实出现的话。

**自检**：话题段时间应连续无大缺口、覆盖全集时长，否则是漏切/切飞。

---

## Stage 1b：章节规划（全集一次）

**输入**：全部 `epNN_extraction.json`
**你做的**：读所有摘要和连续性标记，决定集与章的对应——**相邻且连续性强的集可合并为一章**，并把全部章节分成若干"部分"。

**合并规则**：
- 可合并：前集 `continues_to_next` 且后集 `continues_from_prev`；或合并后话题数 ≤ 3
- 不可合并：合并后估计篇幅超过 30 分钟学习量
- 部分边界：主题明显跳跃处（如从"基础"到"进阶"）
- 合并章的 `prerequisites_implied` 跨集去重

**输出**：`analysis/chapter_plan.json`
```json
{"parts": [
  {"part_number": 1, "title": "LangChain 1.2 新版特性", "chapters": [
    {"chapter_number": 1, "title": "简介与核心概念", "episodes": ["ep01"], "merge_reason": null},
    {"chapter_number": 5, "title": "Models 层", "episodes": ["ep05","ep06"], "merge_reason": "ep05理论ep06实操，连贯，合并18分钟"}
  ]}
]}
```

---

## Stage 2：文档检索（每章一次，可并行）

**技术类必需，生活类跳过。** 目标：核对视频说法是否准确，并为视频未覆盖的字段（最佳实践、坑）预存官方素材。

**流程**：
1. 从该章各 extraction 收集 `key_claims` 和 `topics[].title`
2. 你为每个话题生成 1-2 条**规范技术术语**搜索词（不要直接用字幕原文搜）
3. 用 `context7` 查库文档、`WebSearch`/`WebFetch` 查补充
4. 你从结果里摘取相关段落，**标注来源 URL**，标注它验证/补充哪条 claim

**规则**：
- 每个话题至少 1 条有效来源；搜不到则 `not_found:true`（Stage 3 在文档开头显著标注"未找到权威文档佐证"）
- `excerpt` 必须是页面里真实存在的原文——闸门 B（verify_docs.py）会反向 fetch URL 核对，编造会被作废

**输出**：`analysis/chNN_docs.json`
```json
{"chapter_number": 1, "topics": {
  "t1": {
    "search_queries": ["LangChain framework overview"],
    "doc_sources": [{"url": "https://python.langchain.com/docs/introduction/",
                     "excerpt": "LangChain is a framework for developing applications...",
                     "verifies_claims": ["LangChain 是构建 LLM 应用的开源框架"]}],
    "not_found": false,
    "supplementary_material": {"best_practices": ["官方原文：Use LCEL..."], "pitfalls": ["migration guide：AgentExecutor 已废弃"]}
  }
}}
```

---

## Stage 3：章节数据生成（核心锚点）

**输入**：该章各 `epNN_extraction.json` + `chNN_docs.json`
**输出**：`chapters/chNN_data.json`——**渲染的唯一数据源**，每个字段都有来源规则。

### 字段来源与空值兜底

| 字段 | 来源优先级 | 填不了时 |
|------|-----------|---------|
| `what.definition` / `analogy` | 视频 | 从 docs 补，`supplementary:true` + `doc_url` |
| `why.*`（拆三槽） | 视频强调标记优先 | 从 docs 补，标 supplementary |
| `how.code` | 视频代码片段 → 官方示例 | 从 docs 取最小示例，标 supplementary |
| `best_practices` | 视频 → docs.supplementary_material | 从 docs 补 |
| `pitfalls` | 视频强调 → docs migration/warning | 从 docs 补 |
| `exercises` | 你依据知识点原创 | **不允许空** |

**用户已确认的策略：字段填不了时，从官方文档补充并标注 `supplementary:true`（而非留空）**，且必须附可验证的 `doc_url`。

### Schema（必须严格遵守，闸门会逐字段校验）

```json
{
  "chapter_number": 1, "part_number": 1, "part_title": "LangChain 1.2 新版特性",
  "title": "简介与核心概念", "episodes": ["ep01"], "estimated_minutes": 15,
  "learning_outcomes": ["能解释 LangChain 解决什么问题", "能运行最小示例"],
  "prerequisites": [{"name": "Python 基础", "level": "能写函数和类"}],
  "knowledge_points": [
    {
      "id": "kp1", "title": "什么是 LangChain",
      "what": {
        "definition": "构建 LLM 应用的框架",
        "analogy": "像给大模型应用搭的脚手架",
        "supplementary": false,
        "evidence": {"type": "video", "ref": "ep01.t1", "quote": "字幕真实原句"}
      },
      "why": {
        "problem_solved": "不用它：手写 prompt 拼接易错、换模型要重写",
        "alternative_compared": {"name": "直接调 OpenAI SDK", "tradeoff": "灵活但无统一抽象，换模型成本高"},
        "when_not_to_use": "只调单一模型、无链式逻辑时是过度设计",
        "supplementary": false,
        "evidence": {"type": "video", "ref": "ep01.t1", "quote": "..."}
      },
      "how": {
        "content": "最小示例说明",
        "code": "from langchain_core.prompts import ChatPromptTemplate\n...",
        "language": "python", "version": "langchain >= 0.3",
        "dependencies": ["langchain>=0.3", "langchain-openai>=0.2"],
        "expected_output": "Hello",
        "alternatives": {"domestic": "用 Qwen/Zhipu API 替换 OpenAI：..."},
        "supplementary": false, "doc_url": null,
        "evidence": {"type": "video", "ref": "ep01.t1", "quote": "..."}
      },
      "best_practices": {"items": ["新链一律用 LCEL"], "supplementary": true, "doc_url": "https://..."},
      "pitfalls": {"items": [{"symptom": "...", "cause": "...", "solution": "..."}], "supplementary": false}
    }
  ],
  "summary": ["要点1", "要点2", "下一章将介绍环境搭建"],
  "exercises": [
    {"level": 1, "title": "...", "requirement": "...", "hint": "...", "answer": {"code": "...", "language": "python", "key_points": "..."}},
    {"level": 2, "title": "...", "requirement": "...", "hint": "...", "answer": {"code": "...", "language": "python", "key_points": "..."}},
    {"level": 3, "title": "...", "requirement": "...", "hint": "...", "answer": {"code": "...", "language": "python", "key_points": "..."}}
  ]
}
```

### 硬约束（闸门会拦，提前满足）
- `learning_outcomes` ≥ 2 条且可量化
- 每个知识点 `what`/`why`/`how` 必须带 `evidence`；video 证据的 `quote` 必须是字幕真实原句
- `how.code` 必须可运行：含 import、`language`、`version`、`dependencies`；有 `expected_output` 则会比对
- 代码依赖 OpenAI → 必须给 `alternatives.domestic`
- `supplementary:true` → 必须有 `doc_url`
- `pitfalls` 每条三槽：symptom / cause / solution
- `exercises` 恰好覆盖 1/2/3 三级；L3 需查文档或组合多知识点，不得与 how.code 雷同
- `summary` 最后一条以"下一章"开头

---

## Stage 4：机器闸门（脚本，无 AI）

一条命令跑完四道客观闸门并汇总：
```
python scripts/run_gates.py out/<教程标题>/ --timeout 30
```

| 闸门 | 脚本 | 查什么 |
|------|------|--------|
| B 文档反查 | `verify_docs.py` | URL 可达 + excerpt 真在页面里（防编造） |
| Stage4 结构 | `validate_schema.py` | 字段完整性、三级练习、国产替代、supplementary 有据 |
| C2 接地 | `verify_grounding.py` | evidence.quote 真在字幕提取里（防杜撰解释） |
| A 代码执行 | `verify_code.py` | L0 真跑比对输出 / L1 venv 跑 / L2（API）静态检查 |

产物：`validation/passed.json`（全绿章）、`validation/blocked.json`（每条缺陷带 `gate`+`ref`+`fix_hint`）。退出码非零表示有章被拦。
> 单独跑某一闸门也可，各脚本支持传单个 `chNN_data.json` 或目录。

---

## C3：rubric 判官（你，建议用强模型）

机器闸门查完"在不在、有没有据"，剩下"好不好"由你按锚点评分表打分。判官比生成容易，建议这一步用强模型，对每章打一次分。

| 维度 | 0 分 | 2 分 |
|------|------|------|
| 类比贴切度 | "向量库就是数据库"（同义反复） | "向量库像给文档建语义索引，按意思找" |
| why 说服力 | "因为更好" | 指出具体痛点 + 替代方案代价 |
| 练习区分度 | 三题都在抄示例 | L3 需查文档/组合两知识点 |
| 信息密度 | 一章塞 6 个知识点 | ≤3 个，层层递进 |
| 心智模型 | 直接上代码无铺垫 | 先建直觉再看代码 |

输出 `validation/chNN_rubric.json`：每项 0/1/2 + 失败项的 `ref` + 可执行 `fix_instruction`。任一维度 0 分 → 进回灌。完整准绳见文末「附录：质量自检标准」。

---

## 回灌：定向局部重写（你）

对 `blocked.json` / rubric 失败项，**不重跑整章**（会引入新随机性），只重写出问题的那个字段：
1. 取该 block 的 `ref` + `msg`/`fix_hint`/`fix_instruction`
2. 构造局部 prompt：只给该知识点上下文 + 原字段 + 失败原因，要求只重新输出这一个字段的 JSON 片段
3. patch 回 `chNN_data.json`
4. 只重跑受影响的闸门（改代码→重跑A，改解释→重跑C2/C3）
5. 最多回灌 2 轮仍不过 → 留在 blocked，渲染时该章标"待人工"，**不阻断其他章**

---

## Stage 5：渲染（脚本，无 AI）

只渲染 `passed.json` 里的章：
```
python scripts/render.py out/<教程标题>/chapters/chNN_data.json -o out/<教程标题>/
```
`supplementary` 字段自动加蓝色 `[补充]` + 来源链接；`alternatives.domestic` 自动加折叠块；练习答案自动 `<details>` 折叠。格式问题改 `render.py` 模板即可，与模型无关。

README.md（教程总览）按下方「README.md 格式」手写或渲染。

---

## 产物目录规范

```
out/<教程标题>/
├── raw/subtitles/epNN.json          # 原始字幕归档
├── analysis/                        # Stage 1~2 中间产物
│   ├── epNN_extraction.json
│   ├── chapter_plan.json
│   └── chNN_docs.json
├── chapters/chNN_data.json          # Stage 3，渲染唯一数据源
├── validation/                      # 闸门产物，渲染前须全绿
│   ├── chNN_code.json / chNN_docs_check.json / chNN_schema.json / chNN_grounding.json
│   ├── chNN_rubric.json
│   ├── passed.json / blocked.json
├── golden/                          # 黄金回归基准（精修1-2章，换模型后比对不许退化）
├── README.md                        # 教程总览
├── 第X部分-<部分标题>/NN-<标题>.md  # Stage 5 渲染产物
└── .cache/                          # 临时文件（可重建）
    ├── bili_cookies.txt
    └── venvs/<deps-hash>/           # 闸门 A 的 venv 缓存
```

---

## 渲染契约：每章标准格式

`render.py` 产出的 Markdown 结构（看数据 → 知道会渲染成什么）：

```markdown
# 第N章：<标题>
> 对应视频：epXX
> 预计学习时间：XX 分钟

## 学完后你能做什么
- 能够<可量化能力>

## 前置知识
- <知识点>：<到什么程度>

---
## 一、<知识点标题>
### 是什么
<定义> + 类比：<类比>
### 为什么这么设计
<解决什么问题> + 对比<替代方案> + 何时不该用
### 怎么用
> 依赖版本：`xxx`
（代码块，含 import）
（预期输出代码块）
<details>国内替代方案</details>
### 最佳实践
### 常见坑
- **坑 1**：现象。原因：...。解决：...
---
## 本章小结
1. ... N. 下一章将……
---
## 课后练习
### 练习1（⭐ 入门）/ 练习2（⭐⭐ 中级）/ 练习3（⭐⭐⭐ 挑战）
**需求** → **提示** → <details>参考答案 + 关键点</details>
```

### README.md 格式
```markdown
# <教程标题>
> 视频来源：<链接>　总集数：XX　总学习时间：约 XX 小时　字幕来源：<source>

## 这个教程讲什么 / 学完能做什么 / 前置知识

## 章节索引
### 第X部分：<标题>
| 章节 | 标题 | 对应视频 | 预计时间 |
|------|------|----------|----------|
| 01 | ... | ep01 | XX 分钟 |

## 参考权威文档
- [<文档名>](<URL>)

## 关于本教程
- 生成时间：<日期>　字幕来源：<source>
```

---

## 依赖
- `yt-dlp`（必需）：`pip install yt-dlp`
- `ffmpeg` + `faster-whisper`（仅无字幕兜底）：`pip install faster-whisper`
- Playwright MCP（B站 Cookie / AI 字幕 API）
- 闸门脚本仅用标准库；闸门 A 会按 `dependencies` 自动建 venv（需要能联网 pip install）

## 已知局限
- 字幕只有语音，拿不到屏幕代码（需从官方文档补或重建）
- PPT 高亮/板书等视觉强调无法从字幕捕获
- 工程能保证创作字段"有据、可跑、不重复、被判官打过分"，但天花板仍归模型——`why`/类比/练习的精彩程度有上限，这是已知边界

---

## 附录：质量自检标准

> 本附录是 rubric 判官（C3）的评分准绳，也是 Stage 3 填数据时的自我要求。

### 为什么需要统一标准
视频教程普遍：口语化跳跃、缺前置知识、只演示不解释为什么、错误处理缺失。好的教程不是"字幕转文字"，而是**重新设计知识传递路径**。本标准综合：认知负荷理论（Sweller, 1988）、布鲁姆认知分类法、刻意练习（Ericsson）、The Odin Project / freeCodeCamp / MDN 的设计原则、Feynman 技巧。

### 一、结构
- 开头是**"学完后你能做什么"**（可量化），不是"本章讲 XXX"
- 前置知识列明；章节复杂度从低到高不跳跃
- 单章 ≤ 3 个核心知识点；关键术语首次出现有定义

### 二、内容
- 代码在标注版本直接可运行；API 名与官方一致；有版本号
- 安装命令完整、环境变量设置方式、import 不省略、常见报错有处理
- 必补：API key 从哪获取、国产模型替代方案、免费 tier 限制
- 每个关键设计解释"为什么"，对比 ≥1 种替代方案，概念有类比

### 三、教学法
- 新概念先给完整最小示例再扩展；每次只引入一个新知识点
- 复杂代码逐行注释（只注释"为什么"）
- 覆盖布鲁姆**应用层及以上**（不停在记忆/理解）
- 重要概念在后续章节复现；每大章有小结

### 四、练习（最易被忽视，但最重要）
- 每个核心知识点 ≥ 1 道；考"独立实现"而非"抄代码"
- 需求清晰（输入/输出/约束）；提示引导思路不给答案；答案折叠
- 难度梯度：⭐入门（小改）/ ⭐⭐中级（组合两知识点）/ ⭐⭐⭐挑战（需查官方文档）

### 五、常见质量陷阱
| 陷阱 | 表现 | 修复 |
|------|------|------|
| 只演示不解释 | 贴代码无解释 | 加注释，解释关键决策 |
| Happy path | 只演示成功 | 补常见错误处理 |
| 版本不明 | 旧版能跑新版报错 | 明确标版本 |
| 只讲 API 不讲场景 | 列参数不说何时用 | 加适用/不适用场景 |
| 练习照抄 | 练习与示例雷同 | 练习需独立思考组合 |
| 国内踩坑 | 只用 OpenAI | 给国内可用替代 |
| 缺心智模型 | 给代码但读者不知是什么 | 先类比/图示建直觉 |
