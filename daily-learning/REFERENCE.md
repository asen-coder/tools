# 词汇参考文档

> 更新于 2026-06-15，共 102 条词汇。
> 按分类 + 难度排列，难度 ★ 最低，★★★★★ 最高。

## AI / LangChain / LangGraph

### LLM · 大语言模型  ★

基于海量文本训练、能理解和生成自然语言的大型神经网络模型

```
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model='gpt-4o')
```

*状态：✓ 已开始学习*

### prompt · 提示词  ★

发送给语言模型的输入文本，直接决定模型输出质量

```
prompt = 'Summarize the following text in one sentence: {text}'
```

*状态：✓ 已开始学习*

### token · 词元  ★

LLM 处理文本的基本单位，约等于 0.75 个英文单词或 1-2 个汉字

```
'Hello world' is typically 2 tokens; pricing is per token
```

*状态：✓ 已开始学习*

### chain · 链  ★

LangChain 的核心概念，将多个组件（LLM、提示、解析器等）按顺序串联

```
chain = prompt | llm | output_parser
```

*状态：✓ 已开始学习*

### inference · 推理  ★

使用已训练好的模型对新输入进行预测或生成的过程

```
response = llm.invoke('What is RAG?')  # inference call
```

*状态：✓ 已开始学习*

### model · 模型  ★

从数据中学习规律并做出预测或生成的数学系统

```
llm = ChatOpenAI(model='gpt-4o-mini')  # select a model
```

*状态：✓ 已开始学习*

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

*状态：✓ 已开始学习*

### document loader · 文档加载器  ★★

将 PDF、网页、CSV 等各种格式文件转换为 LangChain Document 对象的工具

```
loader = PyPDFLoader('report.pdf')
docs = loader.load()
```

*状态：✓ 已开始学习*

### text splitter · 文本分割器  ★★

将长文档切分成适合 LLM 上下文窗口大小的小块

```
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
```

*状态：✓ 已开始学习*

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

## 编程 / 前端

### component · 组件  ★

封装了模板、逻辑和样式的可复用独立 UI 单元

```
<UserCard :name='user.name' @click='handleClick' />
```

*状态：✓ 已开始学习*

### props · 属性  ★

父组件向子组件传递数据的机制，单向数据流

```
defineProps<{ title: string; count: number }>()
```

*状态：✓ 已开始学习*

### callback · 回调函数  ★

作为参数传给另一个函数、在某个时机被调用的函数

```
setTimeout(() => console.log('done'), 1000)  // arrow fn is the callback
```

*状态：✓ 已开始学习*

### API · 应用编程接口  ★

允许不同软件互相通信的规范，前端主要通过 HTTP API 获取数据

```
const data = await fetch('/api/users').then(r => r.json())
```

*状态：✓ 已开始学习*

### async · 异步  ★

不阻塞主线程、允许其他代码继续运行的操作方式

```
async function fetchUser(id) { return await api.get(`/users/${id}`) }
```

*状态：✓ 已开始学习*

### DOM · 文档对象模型  ★

浏览器将 HTML 解析成树形结构的内存表示，JS 通过它操作页面

```
document.getElementById('app')  // access DOM node
```

*状态：✓ 已开始学习*

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

## 音乐

### note · 音符  ★

表示特定音高和时值的音乐符号，是音乐的基本构成单位

```
C, D, E, F, G, A, B are the 7 natural notes
```

*状态：✓ 已开始学习*

### beat · 拍  ★

音乐中规律性重复的基本时间单位，就像心跳的节律

```
A 4/4 time signature has 4 beats per measure
```

*状态：✓ 已开始学习*

### tempo · 速度  ★

音乐演奏的快慢，用 BPM（每分钟拍数）表示

```
120 BPM is a common tempo; 60 BPM feels like a slow heartbeat
```

*状态：✓ 已开始学习*

### melody · 旋律  ★

一系列音符按时间顺序排列形成的可识别音乐线条，歌曲的'主角'

```
The melody is what you hum when you remember a song
```

*状态：✓ 已开始学习*

### chord · 和弦  ★

三个或更多不同音高的音符同时发声的组合

```
C major chord = C + E + G played together
```

*状态：✓ 已开始学习*

### rhythm · 节奏  ★

音符时值长短和强弱的规律性排列模式

```
A drum kit primarily provides the rhythm in a band
```

*状态：✓ 已开始学习*

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

## 日常沟通

### Could you repeat that? · 你能再说一遍吗？  ★

礼貌请求对方重复刚才说的内容

```
Sorry, could you repeat that? The connection was breaking up.
```

*状态：✓ 已开始学习*

### I understand. · 我明白了。  ★

表示你已理解对方说的内容

```
I understand the requirements. I'll start working on it today.
```

*状态：✓ 已开始学习*

### That's a good point. · 这是个好观点。  ★

表达对对方意见的认可和肯定

```
That's a good point about performance. We should optimize the query.
```

*状态：✓ 已开始学习*

### I agree. · 我同意。  ★

表示与对方观点一致

```
I agree. Using TypeScript would reduce runtime errors significantly.
```

*状态：✓ 已开始学习*

### Please go ahead. · 请继续。  ★

邀请对方继续发言或开始做某件事

```
You wanted to share the test results? Please go ahead.
```

*状态：✓ 已开始学习*

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

*状态：○ 待学习*

### Feel free to interrupt me. · 请随时打断我。  ★★

允许听众在自己发言时提问或发表意见，营造开放的交流氛围

```
I'll walk through the architecture. Feel free to interrupt me with questions.
```

*状态：○ 待学习*

### Could we revisit this later? · 我们可以稍后再讨论这个吗？  ★★

将某个话题推迟到更合适的时机讨论，避免当前跑题

```
That's important but out of scope today. Could we revisit this later?
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
