# 词汇参考文档

> 更新于 2026-06-16，共 1262 条词汇。
> 按分类 + 难度排列，难度 ★ 最低，★★★★★ 最高。

## AI / LangChain / LangGraph

### prompt template · 提示模板  ★★

带占位符变量的可复用提示结构，运行时填入具体值

```
template = PromptTemplate.from_template('Translate {text} to {language}')
```

*状态：✓ 已开始学习*

### output parser · 输出解析器  ★★

将 LLM 原始文本响应转换为结构化数据（JSON、列表等）的组件

```
parser = JsonOutputParser(pydantic_object=Recipe)
chain = prompt | llm | parser
```

*状态：✓ 已开始学习*

### embedding · 嵌入向量  ★★

将文本转化为固定维度数字向量的表示，语义相似的文本向量距离近

```
embeddings = OpenAIEmbeddings()
vector = embeddings.embed_query('What is RAG?')
```

*状态：✓ 已开始学习*

### retriever · 检索器  ★★

根据查询从知识库中找到相关文档的组件，是 RAG 架构的核心

```
retriever = vectorstore.as_retriever(search_kwargs={'k': 4})
```

*状态：✓ 已开始学习*

### vector store · 向量数据库  ★★

存储文档嵌入向量并支持高效语义相似度搜索的专用数据库

```
db = Chroma.from_documents(docs, embedding=OpenAIEmbeddings())
```

*状态：✓ 已开始学习*

### memory · 记忆  ★★

在多轮对话中保存上下文历史，让模型记住之前的交流内容

```
memory = ConversationBufferMemory(return_messages=True)
```

*状态：○ 待学习*

### document loader · 文档加载器  ★★

将 PDF、网页、CSV 等各种格式文件转换为 LangChain Document 对象的工具

```
loader = PyPDFLoader('report.pdf')
docs = loader.load()
```

*状态：○ 待学习*

### text splitter · 文本分割器  ★★

将长文档切分成适合 LLM 上下文窗口大小的小块

```
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
```

*状态：○ 待学习*

### temperature · 温度  ★★

控制模型输出随机性的参数，0 最确定，1+ 最有创意

```
llm = ChatOpenAI(temperature=0)  # deterministic output
```

*状态：○ 待学习*

### few-shot · 少样本  ★★

在提示中提供少量输入输出示例，引导模型按期望格式回答

```
FewShotPromptTemplate(examples=[{'q': '...', 'a': '...'}], ...)
```

*状态：○ 待学习*

### ChatPromptTemplate · 聊天提示模板  ★★

LangChain 中用于构建对话提示的模板类，支持 system/human/ai 三种角色消息

```
prompt = ChatPromptTemplate.from_messages([("system", "You are {role}"), ("human", "{input}")])
```

*状态：○ 待学习*

### output parser · 输出解析器  ★★

将 LLM 返回的字符串解析为结构化对象（JSON、Pydantic 模型等）的组件

```
chain = prompt | llm | StrOutputParser()
```

*状态：○ 待学习*

### streaming · 流式输出  ★★

LLM 逐 token 实时输出而非等待完整响应，显著改善用户体验

```
async for chunk in chain.astream(input):
    print(chunk, end='', flush=True)
```

*状态：○ 待学习*

### vector store · 向量数据库  ★★

存储文本嵌入向量并支持高效语义相似度搜索的专用数据库

```
vectorstore = Chroma.from_documents(documents, OpenAIEmbeddings())
```

*状态：○ 待学习*

### text splitter · 文本分割器  ★★

将长文档切分为适合向量化和检索的小块（chunk）的工具

```
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
```

*状态：○ 待学习*

### document loader · 文档加载器  ★★

LangChain 中从各种数据源（PDF、网页、数据库）读取内容并转为 Document 对象的组件

```
loader = PyPDFLoader('report.pdf')
docs = loader.load()
```

*状态：○ 待学习*

### fine-tuning · 微调  ★★

在预训练大模型基础上用小规模领域数据进一步训练，使其适配特定任务

```
Fine-tuned GPT-3.5 on customer support data to improve response accuracy
```

*状态：○ 待学习*

### hallucination · 幻觉  ★★

LLM 生成看似可信但实际上错误或虚构内容的问题，是当前 AI 的主要挑战之一

```
The model hallucinated a fake citation to support its argument
```

*状态：○ 待学习*

### context window · 上下文窗口  ★★

LLM 在单次推理时能接收和处理的最大 token 数量，决定可处理文档的长度

```
Claude's context window is 200K tokens, allowing entire codebases as input
```

*状态：○ 待学习*

### temperature · 温度（采样参数）  ★★

控制 LLM 输出随机性的参数，0 最确定，1 以上最随机

```
llm = ChatOpenAI(temperature=0.0)  # 适合代码生成等精确任务
```

*状态：○ 待学习*

### embedding · 词嵌入  ★★

将文本转换为能捕捉语义的高维稠密向量，相似含义的文本向量距离更近

```
embeddings = OpenAIEmbeddings()
vector = embeddings.embed_query('hello world')
```

*状态：○ 待学习*

### semantic search · 语义搜索  ★★

基于语义相似度而非关键词匹配的搜索方式，能理解查询的实际含义

```
Searching 'how to cook pasta' returns recipes even without exact keyword match
```

*状态：○ 待学习*

### multimodal · 多模态  ★★

能同时处理多种数据类型（文本、图像、音频、视频）的 AI 模型能力

```
GPT-4V can analyze both text and images in the same conversation
```

*状态：○ 待学习*

### few-shot · 少样本  ★★

在提示词中提供少量示例（2-10 个）来引导模型完成特定格式或任务的技术

```
Providing 3 input-output pairs in the prompt to demonstrate the desired format
```

*状态：○ 待学习*

### LangSmith · LangSmith（链路追踪平台）  ★★

LangChain 官方的 LLM 应用调试和监控平台，可追踪每次 LLM 调用的输入输出

```
LANGCHAIN_TRACING_V2=true  # 启用后所有 chain 调用自动记录
```

*状态：○ 待学习*

### tokenizer · 分词器  ★★

将输入文本切分为 token 序列的预处理工具，不同模型使用不同的分词策略

```
tiktoken.encoding_for_model('gpt-4').encode('Hello world')  # → [9906, 1917]
```

*状态：○ 待学习*

### RAG · 检索增强生成  ★★★

结合向量检索和 LLM 生成的架构：先检索相关文档，再让模型基于文档回答

```
chain = {'context': retriever, 'question': passthrough} | prompt | llm
```

*状态：○ 待学习*

### LCEL · LangChain 表达式语言  ★★★

用管道符 | 串联 LangChain 组件的 DSL，所有组件都实现 Runnable 接口

```
chain = prompt | llm | StrOutputParser()  # this is LCEL
```

*状态：○ 待学习*

### runnable · 可运行对象  ★★★

LangChain 中所有组件（LLM、提示、解析器等）共同实现的标准接口

```
# Runnables support: invoke, stream, batch, ainvoke, astream
```

*状态：○ 待学习*

### agent · 智能体  ★★★

能自主规划步骤、调用工具并根据结果决定下一步行动的 AI 系统

```
agent = create_react_agent(llm, tools=[search_tool, calculator])
```

*状态：○ 待学习*

### tool calling · 工具调用  ★★★

LLM 在生成过程中请求执行外部函数（搜索、计算等）并获取结果的能力

```
@tool
def get_weather(city: str) -> str:
    return weather_api(city)
```

*状态：○ 待学习*

### hallucination · 幻觉  ★★★

模型自信地生成听起来合理但实际上错误或捏造的内容

```
RAG helps reduce hallucination by grounding answers in real documents
```

*状态：○ 待学习*

### context window · 上下文窗口  ★★★

模型单次能处理的最大 token 数量，超出则需截断或用其他策略

```
GPT-4o has a 128k context window; Claude 3.5 has 200k
```

*状态：○ 待学习*

### callback handler · 回调处理器  ★★★

监听链/代理执行过程中各阶段事件（开始、结束、错误）的钩子机制

```
chain.invoke(input, config={'callbacks': [StreamingHandler()]})
```

*状态：○ 待学习*

### chain-of-thought · 思维链  ★★★

让模型在给出最终答案前逐步展示推理过程的提示技术

```
prompt = 'Think step by step before answering: {question}'
```

*状态：○ 待学习*

### streaming · 流式输出  ★★★

LLM 逐 token 输出内容而非等待全部生成完再返回，改善用户体验

```
for chunk in chain.stream({'question': 'What is LCEL?'}):
    print(chunk, end='')
```

*状态：○ 待学习*

### MessagesPlaceholder · 消息占位符  ★★★

在聊天提示模板中动态插入一组消息（如历史记录）的占位符组件

```
MessagesPlaceholder(variable_name="chat_history")
```

*状态：○ 待学习*

### RAG · 检索增强生成  ★★★

将外部知识检索结果注入 LLM 上下文，弥补模型知识截止日期的局限

```
rag_chain = retriever | format_docs | prompt | llm | StrOutputParser()
```

*状态：○ 待学习*

### tool calling · 工具调用  ★★★

LLM 根据用户意图决定调用哪些预定义工具（函数）并传入参数的能力

```
@tool
def search_web(query: str) -> str:
    return results
```

*状态：○ 待学习*

### StateGraph · 状态图  ★★★

LangGraph 的核心数据结构，定义节点（操作）和边（流转路径）构成的有向图

```
graph = StateGraph(State)
graph.add_node('research', research_node)
graph.add_edge('research', 'write')
```

*状态：○ 待学习*

### checkpoint · 检查点  ★★★

LangGraph 在每个节点执行后保存的完整状态快照，用于断点续跑和人工干预

```
memory = MemorySaver()
graph = builder.compile(checkpointer=memory)
```

*状态：○ 待学习*

### human-in-the-loop · 人机协作  ★★★

在 AI 工作流中设置人工审核节点，让人类在关键决策点审批或修正

```
graph.compile(interrupt_before=['sensitive_action'])
```

*状态：○ 待学习*

### multi-agent · 多智能体  ★★★

多个专职 AI 智能体协同工作，分别负责不同子任务（如研究员 + 写手 + 审稿人）

```
supervisor → researcher → writer → reviewer
```

*状态：○ 待学习*

### cosine similarity · 余弦相似度  ★★★

衡量两个向量方向接近程度的指标（-1 到 1），向量数据库检索的核心算法

```
similarity = dot(a, b) / (norm(a) * norm(b))
```

*状态：○ 待学习*

### quantization · 量化  ★★★

将模型权重从高精度浮点数压缩为低精度整数，减少内存占用和推理延迟

```
llama.cpp runs LLaMA-3 with 4-bit quantization on consumer hardware
```

*状态：○ 待学习*

### zero-shot · 零样本  ★★★

无需针对性训练示例，直接让模型执行从未见过的任务的能力

```
GPT-4 can classify sentiment zero-shot by just describing the task in the prompt
```

*状态：○ 待学习*

### chain of thought · 思维链  ★★★

让模型在给出最终答案前显式写出中间推理步骤，显著提升复杂问题的准确率

```
Let's think step by step: first calculate X, then Y, therefore Z.
```

*状态：○ 待学习*

### guardrails · 安全护栏  ★★★

防止 AI 输出有害内容或越界行为的安全机制，包括输入过滤和输出校验

```
Input guardrail blocks prompt injection; output guardrail checks for PII
```

*状态：○ 待学习*

### throughput · 吞吐量  ★★★

LLM 服务每秒能处理的 token 数量，衡量模型在高并发场景下的性能

```
This deployment achieves 200 tokens/sec throughput on A100 GPU
```

*状态：○ 待学习*

### grounding · 接地气 / 现实锚定  ★★★

确保 AI 输出基于真实可验证的信息，而非凭空生成，通常通过 RAG 或工具调用实现

```
Grounding the chatbot with a product database ensures it only mentions real products
```

*状态：○ 待学习*

### StateGraph · 状态图  ★★★★

LangGraph 的核心类，定义以共享状态驱动的有向图工作流

```
graph = StateGraph(AgentState)
graph.add_node('llm', call_llm)
```

*状态：○ 待学习*

### conditional edge · 条件边  ★★★★

LangGraph 中根据当前状态动态决定流向哪个节点的路由逻辑

```
graph.add_conditional_edges('agent', should_continue, {'tools': 'tools', 'end': END})
```

*状态：○ 待学习*

### checkpointer · 检查点  ★★★★

LangGraph 中保存图执行状态的机制，支持暂停、恢复和人工审核

```
memory = MemorySaver()
graph = graph.compile(checkpointer=memory)
```

*状态：○ 待学习*

### human-in-the-loop · 人在回路  ★★★★

在自动化 AI 流程中插入人工审核/确认节点，防止危险操作自动执行

```
graph.add_node('human_review', interrupt_before=['execute_code'])
```

*状态：○ 待学习*

### subgraph · 子图  ★★★★

LangGraph 中可独立运行、也可嵌套进父图的封装图结构

```
parent.add_node('child_graph', child_graph.compile())
```

*状态：○ 待学习*

### fine-tuning · 微调  ★★★★

在预训练大模型基础上，用特定领域数据继续训练以适应专用任务

```
Fine-tune GPT-4o-mini on customer support data to improve domain accuracy
```

*状态：○ 待学习*

### RLHF · 基于人类反馈的强化学习  ★★★★

通过人类标注者对 AI 输出打分来训练奖励模型，再用强化学习优化 AI 行为的技术

```
ChatGPT was trained using RLHF to align responses with human preferences
```

*状态：○ 待学习*

### ReAct · 推理-行动框架  ★★★★

让 AI 交替进行推理（Reasoning）和工具调用（Acting），用于构建复杂任务智能体

```
Thought: I need to search → Action: search('query') → Observation: result
```

*状态：○ 待学习*

### attention mechanism · 注意力机制  ★★★★

Transformer 模型的核心，让模型在处理每个 token 时动态关注最相关的部分

```
Self-attention allows 'bank' to attend to 'river' or 'money' based on context
```

*状态：○ 待学习*

### LLM · 大语言模型  ★★★★★

基于海量文本训练、能理解和生成自然语言的大型神经网络模型

```
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model='gpt-4o')
```

*状态：○ 待学习*

### prompt · 提示词  ★★★★★

发送给语言模型的输入文本，直接决定模型输出质量

```
prompt = 'Summarize the following text in one sentence: {text}'
```

*状态：○ 待学习*

### token · 词元  ★★★★★

LLM 处理文本的基本单位，约等于 0.75 个英文单词或 1-2 个汉字

```
'Hello world' is typically 2 tokens; pricing is per token
```

*状态：○ 待学习*

### chain · 链  ★★★★★

LangChain 的核心概念，将多个组件（LLM、提示、解析器等）按顺序串联

```
chain = prompt | llm | output_parser
```

*状态：○ 待学习*

### inference · 推理  ★★★★★

使用已训练好的模型对新输入进行预测或生成的过程

```
response = llm.invoke('What is RAG?')  # inference call
```

*状态：○ 待学习*

### model · 模型  ★★★★★

从数据中学习规律并做出预测或生成的数学系统

```
llm = ChatOpenAI(model='gpt-4o-mini')  # select a model
```

*状态：○ 待学习*

### system prompt · 系统提示词  ★★★★★

对话开始前设置 AI 角色、规则和约束的特殊指令

```
You are a helpful assistant. Always respond in Chinese.
```

*状态：○ 待学习*

## 编程 / 前端

### event delegation · 事件委托  ★★

将子元素的事件监听绑定到父元素，利用事件冒泡减少监听器数量

```
list.addEventListener('click', e => { if (e.target.matches('li')) handle(e) })
```

*状态：○ 待学习*

### closure · 闭包  ★★

内层函数能访问并记住外层函数作用域变量的特性，即使外层已执行完毕

```
function counter() { let n=0; return () => ++n }  // returned fn is a closure
```

*状态：○ 待学习*

### promise · Promise  ★★

代表未来某个异步操作结果的对象，状态只能从 pending 变为 fulfilled 或 rejected

```
fetch('/api').then(r => r.json()).catch(err => console.error(err))
```

*状态：○ 待学习*

### debounce · 防抖  ★★

限制函数在连续触发时只在最后一次停止后才执行，常用于搜索输入

```
const search = debounce(query => api.search(query), 300)
```

*状态：○ 待学习*

### throttle · 节流  ★★

限制函数在固定时间间隔内最多执行一次，常用于滚动/窗口 resize

```
window.addEventListener('scroll', throttle(handleScroll, 100))
```

*状态：○ 待学习*

### lazy loading · 懒加载  ★★

按需加载资源（图片、组件、路由等），而非页面初始化时全部加载

```
const UserProfile = defineAsyncComponent(() => import('./UserProfile.vue'))
```

*状态：○ 待学习*

### viewport · 视口  ★★

用户在屏幕上实际可见的网页区域，响应式设计的基准参照

```
<meta name='viewport' content='width=device-width, initial-scale=1'>
```

*状态：○ 待学习*

### semantic HTML · 语义化 HTML  ★★

用有意义的标签（article/section/header）描述内容结构，而非全用 div

```
<article><h2>Title</h2><p>Content</p></article>  // vs <div><div>...
```

*状态：○ 待学习*

### accessibility · 无障碍  ★★

确保网页对所有用户（包括残障人士）可用的设计实践，简称 a11y

```
<button aria-label='Close dialog'>×</button>  // screen reader can read it
```

*状态：○ 待学习*

### reactive · 深层响应式  ★★

Vue 3 中将对象/数组转为深层响应式的函数，无需 .value 访问

```
const state = reactive({ count: 0, user: { name: 'Alice' } })
state.count++
```

*状态：○ 待学习*

### computed · 计算属性  ★★

Vue 3 中基于其他响应式数据派生的只读属性，自动追踪依赖并缓存结果

```
const doubled = computed(() => count.value * 2)
```

*状态：○ 待学习*

### watch · 侦听器  ★★

Vue 3 中监听特定响应式数据变化并执行副作用的 API

```
watch(count, (newVal, oldVal) => { console.log(`${oldVal} → ${newVal}`) })
```

*状态：○ 待学习*

### slot · 插槽  ★★

Vue 组件中供父组件注入内容的占位符，实现组件内容的灵活定制

```
<MyCard><template #title>Hello</template></MyCard>
```

*状态：○ 待学习*

### defineProps · 声明 props  ★★

Vue 3 setup script 中声明组件接收的 props 及其类型约束的编译器宏

```
const props = defineProps<{ title: string; count?: number }>()
```

*状态：○ 待学习*

### Pinia · Pinia（Vue 状态管理）  ★★

Vue 3 官方状态管理库，比 Vuex 更简单，支持 Composition API 和 TypeScript

```
const useStore = defineStore('main', () => { const count = ref(0); return { count } })
```

*状态：○ 待学习*

### union type · 联合类型  ★★

TypeScript 中表示一个值可以是多种类型之一的类型声明，用 | 分隔

```
type ID = string | number
function getUser(id: ID) { ... }
```

*状态：○ 待学习*

### optional chaining · 可选链  ★★

安全访问深层属性的语法（?.），在遇到 null/undefined 时短路返回 undefined

```
const city = user?.address?.city ?? 'Unknown'
```

*状态：○ 待学习*

### nullish coalescing · 空值合并  ★★

当左侧为 null 或 undefined 时返回右侧值的运算符（??），不会跳过 0 和空字符串

```
const port = config.port ?? 3000  // 0 不会触发右侧
```

*状态：○ 待学习*

### HMR · 热模块替换  ★★

开发时修改文件后无需刷新页面、只替换变更模块并保留应用状态的技术

```
Save a Vue file → component updates in browser without losing form state
```

*状态：○ 待学习*

### CORS · 跨域资源共享  ★★

浏览器安全机制，限制跨域请求，服务端通过设置响应头来允许特定来源访问

```
Access-Control-Allow-Origin: https://myapp.com
```

*状态：○ 待学习*

### WebSocket · WebSocket  ★★

在单个 TCP 连接上实现全双工实时通信的协议，适合聊天室、实时协作等场景

```
const ws = new WebSocket('wss://api.example.com/ws')
ws.send(JSON.stringify({action: 'join'}))
```

*状态：○ 待学习*

### JWT · JSON Web Token  ★★

用于在各方之间安全传递声明的紧凑型令牌，包含 Header.Payload.Signature 三部分

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

*状态：○ 待学习*

### debounce · 防抖  ★★

在事件停止触发一段时间后才执行回调，避免高频事件（如输入）重复调用

```
const debouncedSearch = debounce(search, 300)  // 停止输入 300ms 后才搜索
```

*状态：○ 待学习*

### throttle · 节流  ★★

限制函数在固定时间间隔内最多执行一次，适合 scroll/resize 等高频事件

```
const throttledScroll = throttle(handleScroll, 100)  // 100ms 最多执行一次
```

*状态：○ 待学习*

### lazy loading · 懒加载  ★★

延迟加载非关键资源（图片、模块）直到真正需要时，提升页面初始加载性能

```
<img loading="lazy" src="./photo.jpg" />
```

*状态：○ 待学习*

### middleware · 中间件  ★★

在请求到达目标处理器之前拦截并处理请求的函数，可用于认证、日志、限流等

```
app.use(authMiddleware)  // runs before every route handler
```

*状态：○ 待学习*

### singleton pattern · 单例模式  ★★

确保一个类只有一个实例，并提供全局访问点的设计模式

```
const db = Database.getInstance()  // always returns same connection pool
```

*状态：○ 待学习*

### CI/CD · 持续集成/持续部署  ★★

每次代码提交自动触发测试和部署流水线，快速发现问题并缩短上线周期

```
Push code → GitHub Actions runs tests → if passed, deploys to production
```

*状态：○ 待学习*

### regression · 回归（缺陷）  ★★

新代码引入的 bug 导致原本正常功能变得异常

```
The v2.1 release caused a regression in the login flow, fixed in v2.1.1
```

*状态：○ 待学习*

### deprecate · 废弃  ★★

标记某个 API 或功能为不推荐使用，通常给出替代方案并约定在未来版本中删除

```
Options API is deprecated; migrate to Composition API
```

*状态：○ 待学习*

### transpile · 转译  ★★

将一种语言/版本的代码转换为另一种的过程，如 TypeScript → JavaScript、ES2022 → ES5

```
Babel transpiles modern JavaScript so it runs in older browsers
```

*状态：○ 待学习*

### hydration · 水合  ★★★

在客户端激活服务端渲染的静态 HTML，绑定事件使其具有交互能力

```
SSR renders HTML on server; hydration makes it interactive in browser
```

*状态：○ 待学习*

### SSR · 服务端渲染  ★★★

在服务器上生成完整 HTML 再发送给浏览器，首屏快、SEO 好

```
Nuxt.js/Next.js use SSR; initial page is rendered on the server
```

*状态：○ 待学习*

### tree shaking · 摇树优化  ★★★

打包时自动移除未被引用的代码，减小最终 bundle 体积

```
import { ref } from 'vue'  // only 'ref' is bundled, not entire Vue
```

*状态：○ 待学习*

### virtual DOM · 虚拟 DOM  ★★★

用 JS 对象模拟 DOM 树，通过 diff 算法找最小变更再批量更新真实 DOM

```
React/Vue use virtual DOM to minimize expensive real DOM operations
```

*状态：○ 待学习*

### web worker · Web Worker  ★★★

在独立后台线程运行脚本，避免复杂计算阻塞主线程导致页面卡顿

```
const worker = new Worker('compute.js')  // runs off the main thread
```

*状态：○ 待学习*

### memoization · 记忆化  ★★★

缓存函数调用结果，相同参数直接返回缓存值，避免重复计算

```
const memoized = useMemo(() => expensiveCalc(data), [data])
```

*状态：○ 待学习*

### PWA · 渐进式 Web 应用  ★★★

结合网页和原生应用优势的 Web 应用，可离线访问、可安装到桌面

```
Service Worker + Web App Manifest = PWA capabilities
```

*状态：○ 待学习*

### composable · 组合式函数  ★★★

Vue 3 中封装有状态逻辑的可复用函数，约定以 use 开头（如 useRouter、useFetch）

```
function useMousePosition() { const x = ref(0); return { x, y } }
```

*状态：○ 待学习*

### provide / inject · 依赖注入（Vue）  ★★★

Vue 3 中实现跨层级组件通信的 API，祖先 provide，后代 inject，无需 props 逐层传递

```
provide('theme', 'dark')  // 祖先
const theme = inject('theme') // 后代
```

*状态：○ 待学习*

### defineEmits · 声明 emits  ★★★

Vue 3 setup script 中声明组件可触发的自定义事件的编译器宏

```
const emit = defineEmits<{ change: [value: string]; close: [] }>()
```

*状态：○ 待学习*

### generic · 泛型  ★★★

TypeScript 中让函数、类或接口适配多种类型而保持类型安全的参数化类型机制

```
function identity<T>(arg: T): T { return arg }
identity<string>('hello')
```

*状态：○ 待学习*

### type guard · 类型守卫  ★★★

TypeScript 中在代码分支中缩窄变量类型范围的技术，让编译器理解运行时类型

```
if (typeof x === 'string') { x.toUpperCase() } // x is string here
```

*状态：○ 待学习*

### tree shaking · 摇树优化  ★★★

打包时静态分析代码，删除未被引用的模块和导出，减小最终 bundle 体积

```
Import { only, what, you, need } from 'library'  // unused exports are dropped
```

*状态：○ 待学习*

### code splitting · 代码分割  ★★★

将 JavaScript 按路由或特性拆分为多个 chunk，按需加载以提升首屏速度

```
const AdminPage = () => import('./AdminPage.vue')  // 懒加载
```

*状态：○ 待学习*

### SSE · 服务器发送事件  ★★★

服务器向客户端单向推送实时数据的轻量级协议，LLM 流式响应的常用实现方式

```
const es = new EventSource('/stream')
es.onmessage = (e) => console.log(e.data)
```

*状态：○ 待学习*

### OAuth 2.0 · 开放授权协议  ★★★

允许用户授权第三方应用访问其资源而无需暴露密码的标准授权框架

```
Sign in with Google → authorize → receive access token → call Google APIs
```

*状态：○ 待学习*

### idempotent · 幂等  ★★★

多次执行相同操作产生与一次执行相同结果的特性，HTTP GET/PUT 应是幂等的

```
DELETE /users/123 called 5 times still results in user being deleted
```

*状态：○ 待学习*

### race condition · 竞态条件  ★★★

多个并发操作以不确定顺序执行，导致结果依赖时序而出现难以复现的 bug

```
Two requests both read count=5, both increment to 6, but expected result was 7
```

*状态：○ 待学习*

### memoization · 记忆化  ★★★

缓存函数调用结果，当相同参数再次传入时直接返回缓存值而不重新计算

```
const result = useMemo(() => heavyCompute(n), [n])
```

*状态：○ 待学习*

### virtual DOM · 虚拟 DOM  ★★★

在内存中用 JavaScript 对象模拟真实 DOM 树，通过 diff 算法最小化实际 DOM 操作

```
React/Vue maintain a vDOM tree; only changed nodes get real DOM updates
```

*状态：○ 待学习*

### dependency injection · 依赖注入（设计模式）  ★★★

将组件所需的依赖从外部传入而非内部创建，提升可测试性和可替换性的设计原则

```
class Service { constructor(private db: Database) {} }  // db injected from outside
```

*状态：○ 待学习*

### observer pattern · 观察者模式  ★★★

对象状态变化时自动通知所有订阅者的设计模式，是事件系统和响应式框架的基础

```
eventEmitter.on('change', handler)  // handler observes emitter
```

*状态：○ 待学习*

### closure · 闭包  ★★★

函数捕获其词法作用域中变量的特性，即使外部函数已返回，内部函数仍可访问这些变量

```
function counter() { let n = 0; return () => ++n }  // 返回的函数捕获了 n
```

*状态：○ 待学习*

### event loop · 事件循环  ★★★

JavaScript 运行时处理异步回调的机制：调用栈清空后从任务队列取出待执行任务

```
setTimeout callback runs after current synchronous code finishes
```

*状态：○ 待学习*

### polyfill · 兼容填充  ★★★

为不支持某特性的旧浏览器提供该特性实现的代码片段

```
core-js polyfills Array.prototype.flatMap for IE11
```

*状态：○ 待学习*

### microservices · 微服务  ★★★

将大型应用拆分为多个小型独立服务，每个服务负责单一业务能力，可独立部署和扩展

```
User service + Order service + Payment service → communicate via REST/gRPC
```

*状态：○ 待学习*

### service worker · Service Worker  ★★★★

在浏览器后台运行的脚本，可拦截网络请求实现离线缓存和推送通知

```
self.addEventListener('fetch', e => e.respondWith(caches.match(e.request)))
```

*状态：○ 待学习*

### shadow DOM · Shadow DOM  ★★★★

将组件内部 DOM 封装成独立作用域，外部 CSS 无法穿透影响内部样式

```
Web Components use shadow DOM for style encapsulation
```

*状态：○ 待学习*

### micro-frontend · 微前端  ★★★★

将大型前端应用拆分成多个可独立开发、部署的小应用的架构模式

```
qiankun / Module Federation enable micro-frontend architectures
```

*状态：○ 待学习*

### concurrent rendering · 并发渲染  ★★★★

渲染引擎能中断低优先级渲染去处理高优先级更新，保持 UI 响应

```
React 18's concurrent mode can pause rendering to handle user input first
```

*状态：○ 待学习*

### component · 组件  ★★★★★

封装了模板、逻辑和样式的可复用独立 UI 单元

```
<UserCard :name='user.name' @click='handleClick' />
```

*状态：○ 待学习*

### props · 属性  ★★★★★

父组件向子组件传递数据的机制，单向数据流

```
defineProps<{ title: string; count: number }>()
```

*状态：○ 待学习*

### callback · 回调函数  ★★★★★

作为参数传给另一个函数、在某个时机被调用的函数

```
setTimeout(() => console.log('done'), 1000)  // arrow fn is the callback
```

*状态：○ 待学习*

### API · 应用编程接口  ★★★★★

允许不同软件互相通信的规范，前端主要通过 HTTP API 获取数据

```
const data = await fetch('/api/users').then(r => r.json())
```

*状态：○ 待学习*

### async · 异步  ★★★★★

不阻塞主线程、允许其他代码继续运行的操作方式

```
async function fetchUser(id) { return await api.get(`/users/${id}`) }
```

*状态：○ 待学习*

### DOM · 文档对象模型  ★★★★★

浏览器将 HTML 解析成树形结构的内存表示，JS 通过它操作页面

```
document.getElementById('app')  // access DOM node
```

*状态：○ 待学习*

### ref · 响应式引用  ★★★★★

Vue 3 中将基础类型包装为响应式对象的函数，通过 .value 访问和修改

```
const count = ref(0)
count.value++
console.log(count.value) // 1
```

*状态：○ 待学习*

### Vite · Vite（前端构建工具）  ★★★★★

基于原生 ESM 的新一代前端构建工具，开发模式极速冷启动，生产使用 Rollup 打包

```
npm create vite@latest my-app -- --template vue-ts
```

*状态：○ 待学习*

### REST · REST 架构风格  ★★★★★

基于 HTTP 方法（GET/POST/PUT/DELETE）设计 API 的架构风格，无状态、资源导向

```
GET /users/123  →  { id: 123, name: 'Alice' }
```

*状态：○ 待学习*

## 音乐

### pitch · 音高  ★★

声音频率高低的感知属性，频率越高音越高

```
A4 (concert A) has a pitch of 440 Hz
```

*状态：○ 待学习*

### scale · 音阶  ★★

按固定音程关系依序排列的一组音符，是旋律和和声的基础

```
C major scale: C D E F G A B C (no sharps or flats)
```

*状态：○ 待学习*

### harmony · 和声  ★★

多个音符同时发声产生的音程关系，为旋律增添色彩和情感

```
Singing in harmony means two voices at different pitches at once
```

*状态：○ 待学习*

### measure · 小节  ★★

用竖线分隔的固定拍数音乐单元，就像文字中的句子

```
In 4/4 time, each measure contains exactly 4 quarter-note beats
```

*状态：○ 待学习*

### octave · 八度  ★★

频率比为 2:1 的两个音之间的音程，听起来'相同但高低不同'

```
A4 (440Hz) and A5 (880Hz) are one octave apart
```

*状态：○ 待学习*

### dynamics · 力度  ★★

音乐演奏的响度变化，从弱到强用 pp/p/mp/mf/f/ff 标记

```
pp (pianissimo) = very soft; ff (fortissimo) = very loud
```

*状态：○ 待学习*

### major scale · 大调音阶  ★★

由全-全-半-全-全-全-半音程排列的七声音阶，听起来明亮、欢快

```
C major: C D E F G A B C  (W W H W W W H)
```

*状态：○ 待学习*

### minor scale · 小调音阶  ★★

由全-半-全-全-半-全-全音程排列的七声音阶，听起来忧郁、深沉

```
A minor: A B C D E F G A  (natural minor, relative to C major)
```

*状态：○ 待学习*

### pentatonic scale · 五声音阶  ★★

由五个音符构成的音阶，在流行、蓝调、中国传统音乐中广泛使用

```
C major pentatonic: C D E G A  (remove 4th and 7th from major scale)
```

*状态：○ 待学习*

### vibrato · 颤音  ★★

演奏或演唱时音高快速微小的周期性波动，增加音符的表现力和温暖感

```
Classical violinists use wide vibrato; jazz guitarists prefer narrow, fast vibrato
```

*状态：○ 待学习*

### dynamics · 力度  ★★

音乐中音量强弱的变化，从最弱（ppp）到最强（fff），是表达情感的重要手段

```
mp (mezzo-piano) → mf (mezzo-forte) → f (forte) → ff (fortissimo)
```

*状态：○ 待学习*

### timbre · 音色  ★★

使不同乐器或声音听起来不同的音质特征，即使音高相同也各有其独特的声音质地

```
A violin and flute playing the same A4 note sound different due to their timbre
```

*状态：○ 待学习*

### arpeggio · 琶音  ★★

和弦音符不同时发音、而是按顺序一个个弹奏，像竖琴拨弦的效果

```
Roll the chord from bottom to top—play it as an arpeggio, not a block chord
```

*状态：○ 待学习*

### arpeggio · 琶音  ★★★

将和弦各音依次单独弹奏而非同时发声，常用于钢琴和吉他

```
Playing C-E-G one by one upward is a C major arpeggio
```

*状态：○ 待学习*

### staccato · 断音  ★★★

短促分离地弹奏每个音符，在音符上方或下方标记小圆点

```
Staccato notes sound like light, bouncy raindrops
```

*状态：○ 待学习*

### legato · 连奏  ★★★

音符之间流畅连贯地演奏，没有间断，用弧线（连线）标记

```
Legato playing sounds smooth like flowing water
```

*状态：○ 待学习*

### syncopation · 切分音  ★★★

将重音放在通常较弱的拍点上，造成节奏错位感，爵士乐大量使用

```
Most pop and jazz music uses syncopation for a groove feel
```

*状态：○ 待学习*

### crescendo · 渐强  ★★★

音量逐渐增大的演奏方式，用 < 符号或 cresc. 标记

```
The orchestra played a crescendo leading to the climax
```

*状态：○ 待学习*

### improvisation · 即兴演奏  ★★★

演奏时实时创作而非演奏预先写好的乐谱，爵士乐的灵魂

```
Jazz musicians improvise solos over chord progressions
```

*状态：○ 待学习*

### chord progression · 和弦进行  ★★★

多个和弦按特定顺序排列形成的音乐骨架，决定歌曲的情感走向

```
I-V-vi-IV (C-G-Am-F) is the most commonly used pop chord progression
```

*状态：○ 待学习*

### time signature · 拍号  ★★★

乐谱开头标明每小节拍数和基准音符时值的记号，如 4/4 表示每小节四个四分音符

```
4/4 is common in pop; 3/4 is waltz; 6/8 gives a compound duple feel
```

*状态：○ 待学习*

### key signature · 调号  ★★★

五线谱开头标明升降号的记号，决定乐曲所在的调式（大调或小调）

```
Two sharps (F# and C#) indicates D major or B minor key
```

*状态：○ 待学习*

### interval · 音程  ★★★

两个音符之间的音高距离，以度数（unison/third/fifth/octave）表示

```
C to G is a perfect fifth (7 semitones); C to E is a major third (4 semitones)
```

*状态：○ 待学习*

### accelerando · 渐快  ★★★

指示演奏逐渐加快速度的术语，常缩写为 accel.

```
The piece builds tension with an accelerando before the climactic final chord
```

*状态：○ 待学习*

### ritardando · 渐慢  ★★★

指示演奏逐渐放慢速度的术语，常缩写为 rit. 或 ritard.

```
The conductor signals a ritardando for the ending phrase
```

*状态：○ 待学习*

### transposition · 移调  ★★★

将一段音乐整体移高或降低固定音程，改变调性但保持旋律和声的内部关系不变

```
Transpose 'Happy Birthday' from C to G so it fits your vocal range
```

*状态：○ 待学习*

### syncopation · 切分节奏  ★★★

将重音移至通常不强的拍子（如弱拍或拍的弱部），制造推拉感，是爵士和流行音乐的特征

```
The ska rhythm accents the offbeats (2 and 4) creating a syncopated feel
```

*状态：○ 待学习*

### legato · 连奏  ★★★

指示音符要平滑连接、无明显间隔地演奏，与断奏（staccato）相对

```
Play this melody legato—like a singer breathing between phrases, not choppy
```

*状态：○ 待学习*

### staccato · 断奏  ★★★

指示音符要短促分离地演奏，每个音符之间有明显间隔，通常以小圆点标记

```
The staccato eighth notes in the opening give a playful, bouncy character
```

*状态：○ 待学习*

### counterpoint · 对位法  ★★★★

两条或多条独立旋律线同时演奏并在和声上形成协调关系的作曲技术

```
Bach's fugues are masterpieces of contrapuntal writing
```

*状态：○ 待学习*

### modulation · 转调  ★★★★

在音乐作品中从一个调性转换到另一个调性的作曲技法

```
The song modulated from C major to E major for the final chorus
```

*状态：○ 待学习*

### polyrhythm · 复合节奏  ★★★★

同时存在两种或多种不同节奏型的音乐手法，如 3 对 2 或 4 对 3

```
West African drumming often features complex polyrhythms
```

*状态：○ 待学习*

### dissonance · 不协和音  ★★★★

听起来紧张、不稳定、'需要解决'的音程或和弦组合

```
A tritone interval sounds tense and dissonant
```

*状态：○ 待学习*

### fermata · 延音记号  ★★★★

告知演奏者延长音符或休止符时值（超过正常时值）的记号，时长由演奏者判断

```
Beethoven's 'fate motif' uses a fermata on the fourth note for dramatic effect
```

*状态：○ 待学习*

### coda · 尾奏段落  ★★★★

乐曲结束前的收尾段落，通常从主体旋律中独立出来，以强烈的结束感收束

```
The coda begins at measure 120 after the D.S. al Coda marking
```

*状态：○ 待学习*

### modulation · 转调  ★★★★

乐曲从一个调性过渡到另一个调性的技术，为音乐增加色彩变化和情绪张力

```
The chorus modulates from C major to E major for an uplifting effect
```

*状态：○ 待学习*

### pizzicato · 拨弦  ★★★★

弦乐器演奏技术：用手指拨弦而非用琴弓拉奏，音色短促、颗粒感强

```
Stravinsky's 'Firebird' features pizzicato strings creating a mysterious texture
```

*状态：○ 待学习*

### ostinato · 固定音型  ★★★★

在乐曲中反复出现的固定节奏或旋律模式，是流行歌曲和古典作品的常见结构基础

```
Pachelbel's Canon is built on a repeating bass ostinato of 8 notes
```

*状态：○ 待学习*

### rubato · 弹性速度  ★★★★

演奏时灵活调整节奏速度，不受节拍器约束，根据音乐表达需要自由加快或放慢

```
Chopin's nocturnes are meant to be played with rubato—feel the music, not the beat
```

*状态：○ 待学习*

### note · 音符  ★★★★★

表示特定音高和时值的音乐符号，是音乐的基本构成单位

```
C, D, E, F, G, A, B are the 7 natural notes
```

*状态：○ 待学习*

### beat · 拍  ★★★★★

音乐中规律性重复的基本时间单位，就像心跳的节律

```
A 4/4 time signature has 4 beats per measure
```

*状态：○ 待学习*

### tempo · 速度  ★★★★★

音乐演奏的快慢，用 BPM（每分钟拍数）表示

```
120 BPM is a common tempo; 60 BPM feels like a slow heartbeat
```

*状态：○ 待学习*

### melody · 旋律  ★★★★★

一系列音符按时间顺序排列形成的可识别音乐线条，歌曲的'主角'

```
The melody is what you hum when you remember a song
```

*状态：○ 待学习*

### chord · 和弦  ★★★★★

三个或更多不同音高的音符同时发声的组合

```
C major chord = C + E + G played together
```

*状态：○ 待学习*

### rhythm · 节奏  ★★★★★

音符时值长短和强弱的规律性排列模式

```
A drum kit primarily provides the rhythm in a band
```

*状态：○ 待学习*

### counterpoint · 对位法  ★★★★★

两条或多条旋律线同时演奏并保持和声关系的作曲技术，巴赫是最杰出的代表

```
Bach's 'Crab Canon' is a masterpiece of counterpoint
```

*状态：○ 待学习*

### polyrhythm · 复合节奏  ★★★★★

两种或多种不同节奏同时进行，是非洲打击乐和现代爵士的重要特征

```
3 against 2 polyrhythm: right hand plays triplets while left plays eighth notes
```

*状态：○ 待学习*

## 日常沟通

### Could you elaborate on that? · 你能详细说明一下吗？  ★★

请求对方对某个观点或情况提供更多细节和解释

```
Could you elaborate on that performance issue you mentioned?
```

*状态：✓ 已开始学习*

### Let me clarify. · 让我来说清楚一下。  ★★

主动消除误解，对之前表述不够清晰的内容进行澄清

```
Let me clarify — I meant the staging environment, not production.
```

*状态：✓ 已开始学习*

### I'll get back to you on that. · 关于这个我稍后回复你。  ★★

表示需要时间确认后再回答，不立即给出答案

```
I'll get back to you on that timeline after checking with the team.
```

*状态：✓ 已开始学习*

### That makes sense. · 这说得通。  ★★

表示对方的解释或逻辑是合理的、可以理解的

```
That makes sense. Using a queue would handle the load spikes.
```

*状态：✓ 已开始学习*

### I'd like to add something. · 我想补充一点。  ★★

在别人发言后礼貌地加入自己的观点或信息

```
I'd like to add something — we also need to consider mobile users.
```

*状态：✓ 已开始学习*

### Feel free to interrupt me. · 请随时打断我。  ★★

允许听众在自己发言时提问或发表意见，营造开放的交流氛围

```
I'll walk through the architecture. Feel free to interrupt me with questions.
```

*状态：✓ 已开始学习*

### Could we revisit this later? · 我们可以稍后再讨论这个吗？  ★★

将某个话题推迟到更合适的时机讨论，避免当前跑题

```
That's important but out of scope today. Could we revisit this later?
```

*状态：○ 待学习*

### Could you give me a heads-up? · 能提前通知我一下吗？  ★★

请求对方在事情发生前预先告知，以便有时间准备

```
If the meeting changes, could you give me a heads-up? I'm back-to-back all morning.
```

*状态：○ 待学习*

### I'll loop you in. · 我会把你拉进来（加入沟通）。  ★★

告知对方会将其纳入相关邮件、群组或讨论，让其了解最新进展

```
I'll loop you in on the email thread with the client so you're up to speed.
```

*状态：○ 待学习*

### I'm blocked on this. · 我被这件事卡住了。  ★★

告知他人自己因某个阻碍无法推进当前任务，需要帮助或等待解除阻塞

```
I'm blocked on the payment module until the API keys are provided.
```

*状态：○ 待学习*

### What's the ETA? · 预计什么时候完成？  ★★

询问某项工作的预计完成时间（Estimated Time of Arrival，借用航运术语）

```
The client just asked for an update. What's the ETA on the bug fix?
```

*状态：○ 待学习*

### In a nutshell... · 简而言之……  ★★

用于在总结时表示接下来要简洁地表达复杂内容

```
In a nutshell, we need to redesign the auth flow to reduce dropout by 30%.
```

*状态：○ 待学习*

### What are the trade-offs? · 有哪些权衡取舍？  ★★

询问某个方案的利弊得失，要求对方全面分析而非只讲优点

```
What are the trade-offs between monolith and microservices for our use case?
```

*状态：○ 待学习*

### I have some concerns about this. · 我对此有一些顾虑。  ★★

表达对某个决定或计划存在担忧，礼貌地提出反对意见

```
I have some concerns about the timeline. Can we review the resource allocation?
```

*状态：○ 待学习*

### What's the root cause? · 根本原因是什么？  ★★

要求找出问题的根本原因而非表面症状，是技术复盘的常用问题

```
The service went down three times this week. What's the root cause?
```

*状态：○ 待学习*

### We need a workaround for now. · 我们现在需要一个临时方案。  ★★

承认问题尚未根本解决，先采用临时手段绕过问题维持运转

```
We can't fix the database bottleneck today. Let's add a cache layer as a workaround.
```

*状态：○ 待学习*

### This is working as intended. · 这是按设计运行的（不是 bug）。  ★★

解释某个被质疑的行为其实是符合预期设计的，并非缺陷

```
The loading spinner on slow connections is working as intended—it's a feature.
```

*状态：○ 待学习*

### Let's align on the next steps. · 我们来确认一下后续步骤。  ★★

在会议或讨论结束时，确认所有人对接下来的行动计划达成共识

```
Before we wrap up, let's align on the next steps and who owns each item.
```

*状态：○ 待学习*

### That's out of scope. · 那超出范围了。  ★★

说明某个需求或话题不在当前项目、会议或任务的讨论范围之内

```
Internationalization is a great idea, but that's out of scope for this MVP.
```

*状态：○ 待学习*

### I'll take ownership of this. · 我来负责这件事。  ★★

主动承担某项任务的责任，表明自己将全权推动直至完成

```
Nobody is driving the API documentation. I'll take ownership of this.
```

*状态：○ 待学习*

### This needs more thought. · 这还需要再仔细考虑。  ★★

表示当前方案尚不成熟，需要进一步分析和研究再做决定

```
The migration plan looks rushed. This needs more thought before we commit.
```

*状态：○ 待学习*

### Let's circle back to this. · 让我们回头再讨论这个。  ★★★

在讨论其他内容后返回到之前未解决的话题

```
We got sidetracked. Let's circle back to the deployment timeline.
```

*状态：○ 待学习*

### I want to make sure we're on the same page. · 我想确认我们的理解是一致的。  ★★★

核实双方对某件事的理解完全相同，避免误解导致工作偏差

```
Before we start coding, I want to make sure we're on the same page about the API contract.
```

*状态：○ 待学习*

### Let me push back on that. · 让我对此提出一些异议。  ★★★

礼貌地表示不同意某个观点，并准备提出反驳理由

```
Let me push back on that — a complete rewrite seems risky given the deadline.
```

*状态：○ 待学习*

### Could you walk me through your reasoning? · 你能带我过一遍你的思路吗？  ★★★

请对方一步步解释其得出结论的逻辑过程

```
Could you walk me through your reasoning for choosing Redis over Memcached?
```

*状态：○ 待学习*

### That's not quite what I had in mind. · 这和我设想的不完全一样。  ★★★

委婉地表示对方的理解或方案与自己的预期有偏差

```
That's not quite what I had in mind — I was thinking of a lighter solution.
```

*状态：○ 待学习*

### I appreciate your candor. · 感谢你的坦诚。  ★★★

感谢对方直接说出真实看法，即使是批评也是欢迎的

```
I appreciate your candor about the code quality issues.
```

*状态：○ 待学习*

### What's the rationale behind this? · 这背后的逻辑/依据是什么？  ★★★

礼貌地请求对方解释决定或设计背后的原因和思考过程

```
What's the rationale behind choosing GraphQL over REST for this project?
```

*状态：○ 待学习*

### Let's not get into the weeds. · 别陷入细节了。  ★★★

在讨论中过于纠结细节时提醒大家回到主线，避免因小失大

```
We only have 20 minutes. Let's not get into the weeds—focus on the three key decisions.
```

*状态：○ 待学习*

### I want to challenge this assumption. · 我想质疑一下这个假设。  ★★★

礼貌地表示方案背后的某个前提可能不成立，希望重新审视

```
I want to challenge this assumption that users prefer dark mode.
```

*状态：○ 待学习*

### Can we put a pin in that? · 我们先把这个话题记下来，待会再说？  ★★★

礼貌地请求将某个话题暂时搁置，待当前讨论结束或另择时间再回来处理

```
That's a great point. Can we put a pin in that and revisit after the demo?
```

*状态：○ 待学习*

### Let's move the needle. · 让我们取得实质性进展。  ★★★

要求做出有意义的推进，而非停留在讨论或小步骤，强调要有明显可见的结果

```
We've been planning for two weeks. It's time to move the needle and ship something.
```

*状态：○ 待学习*

### I want to level-set on our expectations. · 我想对齐一下我们的预期。  ★★★★

在项目开始前确保所有人对目标、范围和交付物有相同的理解

```
Before sprint planning, I want to level-set on our expectations for this feature.
```

*状态：○ 待学习*

### Let's align on the key deliverables. · 让我们就关键交付物达成一致。  ★★★★

明确并确认每个人对本次工作最终输出物的理解一致

```
Let's align on the key deliverables — is it the API docs or the demo as well?
```

*状态：○ 待学习*

### There seems to be some misalignment in our understanding. · 我们的理解之间似乎存在一些偏差。  ★★★★

委婉指出团队成员对同一件事的理解存在不一致的情况

```
There seems to be some misalignment — you said 'done' means tested, they said it means deployed.
```

*状态：○ 待学习*

### Let's table this for now and take it offline. · 我们先把这个搁置，私下再沟通。  ★★★★

将当前争论搁置，留到会议后小范围单独讨论，避免浪费集体时间

```
This is getting detailed. Let's table this for now and take it offline.
```

*状态：○ 待学习*

### This might be a red herring. · 这可能是个误导/干扰因素。  ★★★★

提醒大家当前关注的点可能与真正问题无关，是错误的追踪方向

```
The CSS error might be a red herring. The real bug is in the data fetching.
```

*状态：○ 待学习*

### Could you repeat that? · 你能再说一遍吗？  ★★★★★

礼貌请求对方重复刚才说的内容

```
Sorry, could you repeat that? The connection was breaking up.
```

*状态：○ 待学习*

### I understand. · 我明白了。  ★★★★★

表示你已理解对方说的内容

```
I understand the requirements. I'll start working on it today.
```

*状态：○ 待学习*

### That's a good point. · 这是个好观点。  ★★★★★

表达对对方意见的认可和肯定

```
That's a good point about performance. We should optimize the query.
```

*状态：○ 待学习*

### I agree. · 我同意。  ★★★★★

表示与对方观点一致

```
I agree. Using TypeScript would reduce runtime errors significantly.
```

*状态：○ 待学习*

### Please go ahead. · 请继续。  ★★★★★

邀请对方继续发言或开始做某件事

```
You wanted to share the test results? Please go ahead.
```

*状态：○ 待学习*

### Let's sync up. · 我们对齐一下（信息同步）。  ★★★★★

约定一次短暂会面或通话，让团队成员了解彼此的最新进展

```
Before the sprint review, let's sync up for 15 minutes to align on the demo flow.
```

*状态：○ 待学习*

### We're behind schedule. · 我们落后于计划了。  ★★★★★

说明项目进度滞后，没有按原定时间线推进

```
We're behind schedule by two days. Should we cut scope or add resources?
```

*状态：○ 待学习*

### That's a fair point. · 这是个合理的观点。  ★★★★★

认可对方的意见合理有据，表示接受或值得考虑，即使不完全同意

```
That's a fair point about test coverage. Let's add more unit tests before merging.
```

*状态：○ 待学习*

### This is a known issue. · 这是个已知问题。  ★★★★★

说明某个 bug 或问题已被记录在案，团队清楚其存在

```
The lag on the search page is a known issue. It's tracked as BUG-421.
```

*状态：○ 待学习*

### This is on the right track. · 这个方向对了。  ★★★★★

给出正面反馈，表示对方的思路或方案大方向正确，值得继续深化

```
Your proposal is on the right track. Let's flesh out the implementation details.
```

*状态：○ 待学习*

### Can you elaborate on that? · 你能详细展开说说吗？  ★★★★★

请求对方对某个观点或说法做更详细的解释

```
You mentioned scalability concerns—can you elaborate on that?
```

*状态：○ 待学习*

### I'll follow up on this. · 我来跟进这件事。  ★★★★★

表示自己会继续推进某个事项，并在适当时候反馈进展

```
I don't have the answer right now, but I'll follow up on this by Thursday.
```

*状态：○ 待学习*

### I'm not sure I follow. · 我不太确定是否理解你的意思。  ★★★★★

礼貌地表示没有理解对方说的内容，请求重新解释

```
I'm not sure I follow—could you walk me through the flow again with an example?
```

*状态：○ 待学习*

### We're good to go. · 我们可以开始了 / 都准备好了。  ★★★★★

表示所有准备工作已就绪，可以开始执行某项工作或进入下一阶段

```
Tests are passing, staging looks clean—we're good to go for the release.
```

*状态：○ 待学习*
