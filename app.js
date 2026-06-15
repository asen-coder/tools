/* ── 状态 ──────────────────────────────────────────────────────────────── */
const state = {
  todayData: null,
  allWordsData: null,
  tab: 'today',
  search: '',
  category: 'all',
};

const CAT_LABELS = { ai: 'AI', programming: '编程', music: '音乐', daily: '日常', general: '通用' };

/* ── 语音 ──────────────────────────────────────────────────────────────── */
// 语音合成初始化
const tts = {
  ready: false,
  voices: [],
  preferredVoice: null,

  init() {
    if (!('speechSynthesis' in window)) return;

    const loadVoices = () => {
      this.voices = window.speechSynthesis.getVoices();
      this.ready = this.voices.length > 0;
      this.pickPreferredVoice();
    };

    // 立即加载（可能返回空）
    loadVoices();

    // 监听 voiceschanged 事件（异步加载）
    window.speechSynthesis.addEventListener('voiceschanged', () => {
      loadVoices();
      console.log(`[TTS] 已加载 ${this.voices.length} 个声音`);
    });
  },

  pickPreferredVoice() {
    if (!this.ready) return;

    // 按优先级查找：英文本地 → 英文云端 → 任意英文 → 第一个可用
    this.preferredVoice =
      this.voices.find(v => v.lang === 'en-US' && v.localService) ||
      this.voices.find(v => v.lang === 'en-US') ||
      this.voices.find(v => v.lang.startsWith('en')) ||
      this.voices.find(v => v.lang.startsWith('en-')) ||
      this.voices[0] ||
      null;

    if (this.preferredVoice) {
      console.log(`[TTS] 选择声音: ${this.preferredVoice.name} (${this.preferredVoice.lang})`);
    }
  },

  speak(text, btnEl) {
    if (!('speechSynthesis' in window)) {
      console.warn('[TTS] 浏览器不支持语音合成');
      return;
    }

    if (!this.ready) {
      // 如果还没准备好，强制刷新一次
      this.voices = window.speechSynthesis.getVoices();
      this.ready = this.voices.length > 0;
      this.pickPreferredVoice();
    }

    const u = new SpeechSynthesisUtterance(text);
    u.rate = 0.85;
    u.pitch = 1;

    // 强制使用英文，即使系统没有英文声音也会尝试朗读
    u.lang = 'en-US';

    // 如果有选中的声音就使用
    if (this.preferredVoice) {
      u.voice = this.preferredVoice;
    }

    // 按钮动画
    if (btnEl) {
      btnEl.classList.add('speaking');
      u.onend = () => btnEl.classList.remove('speaking');
      u.onerror = (e) => {
        console.error('[TTS] 播放错误:', e);
        btnEl.classList.remove('speaking');
      };
    }

    // 取消当前播放，延迟 50ms 避免 Chrome bug
    window.speechSynthesis.cancel();
    setTimeout(() => {
      try {
        window.speechSynthesis.speak(u);
        console.log(`[TTS] 正在播放: "${text}"`);
      } catch (err) {
        console.error('[TTS] 播放失败:', err);
      }
    }, 50);
  }
};

// 页面加载时初始化
tts.init();

// 全局 speak 函数
window.speak = function (text, btnEl) {
  tts.speak(text, btnEl);
};

/* ── 工具函数 ───────────────────────────────────────────────────────────── */
function esc(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function dots(difficulty) {
  return Array.from(
    { length: 5 },
    (_, i) => `<span class="dot ${i < difficulty ? 'on' : ''}"></span>`,
  ).join('');
}

/* ── 卡片 HTML ──────────────────────────────────────────────────────────── */
function cardHtml(word, type = 'new') {
  const label = CAT_LABELS[word.category] || word.category;
  const reviewTag =
    type === 'review'
      ? `<span class="review-tag">第 ${word.review_count} 次复习</span>`
      : '';

  const exampleBlock = word.example
    ? `<div class="example">
         <span class="example-label">例句</span>
         <pre class="example-code">${esc(word.example)}</pre>
       </div>`
    : '';

  return `
    <div class="card cat-${esc(word.category)}">
      <div class="card-meta">
        <span class="badge cat-${esc(word.category)}">${label}</span>
        <span class="dots">${dots(word.difficulty)}</span>
        ${reviewTag}
      </div>
      <div class="word-row">
        <div style="flex:1;min-width:0">
          <span class="word-en">${esc(word.en)}</span>
          <p class="word-zh">${esc(word.zh)}</p>
        </div>
        <button class="speak-btn" onclick="speak(${JSON.stringify(word.en)}, this)" aria-label="朗读 ${esc(word.en)}">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/>
            <path d="M19.07 4.93a10 10 0 0 1 0 14.14"/>
            <path d="M15.54 8.46a5 5 0 0 1 0 7.07"/>
          </svg>
        </button>
      </div>
      <p class="word-def">${esc(word.definition)}</p>
      ${exampleBlock}
    </div>`;
}

/* ── 今日页 ─────────────────────────────────────────────────────────────── */
function section(title, count, items, type) {
  if (!items || items.length === 0) return '';
  return `<div class="section-title">${title} <span class="count">${count}</span></div>
          <div class="card-grid">${items.map((w) => cardHtml(w, type)).join('')}</div>`;
}

function renderToday() {
  const d = state.todayData;
  const el = document.getElementById('today-content');

  const vocabReviews = d.vocab_reviews || [];
  const sentReviews = d.sentence_reviews || [];
  const newWords = d.new_words || [];
  const newSentences = d.new_sentences || [];
  const totalReviews = vocabReviews.length + sentReviews.length;
  const totalNew = newWords.length + newSentences.length;

  const isEmpty = totalNew === 0 && totalReviews === 0;

  el.innerHTML = `
    <div class="today-header">
      <div class="today-date">${esc(d.date)} <span>${esc(d.day_of_week)}</span></div>
      <div class="stats-row">
        <div class="stat-chip">新词 <strong>${newWords.length}</strong></div>
        <div class="stat-chip">新句 <strong>${newSentences.length}</strong></div>
        <div class="stat-chip">复习 <strong>${totalReviews}</strong></div>
        <div class="stat-chip streak">连续打卡 <strong>${d.stats.streak}</strong> 天</div>
      </div>
    </div>
    ${section('词汇复习', vocabReviews.length, vocabReviews, 'review')}
    ${section('句子复习', sentReviews.length, sentReviews, 'review')}
    ${section('今日新词', newWords.length, newWords, 'new')}
    ${section('今日新句', newSentences.length, newSentences, 'new')}
    ${isEmpty ? '<div class="state-box"><div class="state-icon">✓</div><p>今日内容已全部完成，明天继续！</p></div>' : ''}`;
}

/* ── 词库页 ─────────────────────────────────────────────────────────────── */
async function loadWordBank() {
  const el = document.getElementById('words-content');
  el.innerHTML = `<div class="skeleton-wrap">
    <div class="skeleton-line medium"></div>
    <div class="skeleton-grid">
      <div class="skeleton-card"></div><div class="skeleton-card"></div><div class="skeleton-card"></div>
    </div>
  </div>`;

  try {
    state.allWordsData = await fetch('./all_words.json').then((r) => r.json());
  } catch {
    el.innerHTML = `<div class="state-box"><div class="state-icon">⚠</div>
      <p>词库数据加载失败，请确认 GitHub Actions 已成功运行并生成 <code>all_words.json</code>。</p></div>`;
    return;
  }
  renderWordBank();
}

function renderWordBank() {
  const el = document.getElementById('words-content');
  const { search, category } = state;
  const allWords = state.allWordsData.words;

  const filtered = allWords.filter((w) => {
    const q = search.toLowerCase();
    const matchCat = category === 'all' || w.category === category;
    const matchSearch =
      !q ||
      w.en.toLowerCase().includes(q) ||
      w.zh.includes(search) ||
      w.definition.includes(search);
    return matchCat && matchSearch;
  });

  // 按难度、再按 id 排序
  filtered.sort((a, b) => a.difficulty - b.difficulty || a.id.localeCompare(b.id));

  const pills = ['all', 'ai', 'programming', 'music', 'daily', 'general']
    .map((c) => {
      const label = c === 'all' ? '全部' : CAT_LABELS[c];
      return `<button class="pill ${state.category === c ? 'active' : ''}" data-cat="${c}">${label}</button>`;
    })
    .join('');

  const cards = filtered.length
    ? `<div class="card-grid">${filtered.map((w) => cardHtml(w)).join('')}</div>`
    : `<div class="state-box"><div class="state-icon">○</div><p>没有匹配的词汇。</p></div>`;

  el.innerHTML = `
    <div class="words-toolbar">
      <input class="search-input" type="search" placeholder="搜索英文、中文或释义…" value="${esc(search)}" id="searchInput" />
      <div class="filter-pills">${pills}</div>
    </div>
    <div class="words-count">共 ${filtered.length} 条 / 总计 ${allWords.length} 条</div>
    ${cards}`;

  document.getElementById('searchInput').addEventListener('input', (e) => {
    state.search = e.target.value;
    renderWordBank();
  });

  el.querySelectorAll('.pill').forEach((btn) => {
    btn.addEventListener('click', () => {
      state.category = btn.dataset.cat;
      renderWordBank();
    });
  });
}

/* ── 进度页 ─────────────────────────────────────────────────────────────── */
function renderProgress() {
  const el = document.getElementById('progress-content');
  const s = state.todayData.stats;

  const pct = s.total > 0 ? Math.round((s.mastered / s.total) * 100) : 0;

  el.innerHTML = `
    <div class="streak-banner">
      <div class="streak-number">${s.streak}</div>
      <div class="streak-info">
        <div class="streak-label">连续打卡天数</div>
        <div class="streak-sub">累计学习 ${s.total_sessions} 天 · 继续加油！</div>
      </div>
    </div>
    <div class="progress-grid">
      <div class="progress-card">
        <div class="p-value">${s.total}</div>
        <div class="p-label">词库总量</div>
      </div>
      <div class="progress-card accent-green">
        <div class="p-value">${s.mastered}</div>
        <div class="p-label">已掌握（${pct}%）</div>
      </div>
      <div class="progress-card accent-primary">
        <div class="p-value">${s.learning}</div>
        <div class="p-label">复习中</div>
      </div>
      <div class="progress-card">
        <div class="p-value">${s.new}</div>
        <div class="p-label">待学习</div>
      </div>
    </div>
    <div class="section-title">间隔重复阶梯</div>
    <div class="card" style="max-width:480px">
      <p class="word-def" style="line-height:2">
        首次见面 → <strong>1天</strong>后复习<br>
        第1次复习 → <strong>3天</strong>后<br>
        第2次复习 → <strong>7天</strong>后<br>
        第3次复习 → <strong>14天</strong>后<br>
        第4次复习 → <strong>30天</strong>后<br>
        第5次以上 → <strong>90天</strong>后
      </p>
    </div>`;
}

/* ── 练习模式 ────────────────────────────────────────────────────────────── */
const quiz = {
  words: [],
  phase: 'idle',  // 'idle' | 'choice' | 'spell' | 'done'
  idx: 0,
  correct: 0,
  wrong: 0,
  answered: false,
  lastOk: null,
};

function shuffle(arr) {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

function getOptions(word) {
  const correct = word.zh;
  const pool = shuffle(quiz.words.map((w) => w.zh).filter((zh) => zh !== correct));
  const distractors = pool.slice(0, 3);
  while (distractors.length < 3) distractors.push('—');
  return shuffle([correct, ...distractors]);
}

function startQuiz() {
  const d = state.todayData;
  const all = [...(d.new_words || []), ...(d.vocab_reviews || [])];
  if (all.length === 0) {
    document.getElementById('quiz-content').innerHTML = `
      <div class="state-box">
        <div class="state-icon">○</div>
        <p>今日暂无词汇，明天再来练习！</p>
      </div>`;
    return;
  }
  quiz.words = shuffle(all);
  quiz.phase = 'choice';
  quiz.idx = 0;
  quiz.correct = 0;
  quiz.wrong = 0;
  quiz.answered = false;
  quiz.lastOk = null;
  renderQuizCard();
}

function renderQuizStart() {
  const d = state.todayData;
  const total = (d.new_words || []).length + (d.vocab_reviews || []).length;
  const el = document.getElementById('quiz-content');
  el.innerHTML = `
    <div class="quiz-start">
      <div class="quiz-start-icon">✦</div>
      <h2 class="quiz-start-title">今日练习</h2>
      <p class="quiz-start-sub">共 <strong>${total}</strong> 个词汇 · 先选择后拼写</p>
      <div class="quiz-flow-steps">
        <div class="quiz-flow-step active">
          <span class="qfs-num">1</span>
          <span>选择题</span>
        </div>
        <div class="qfs-arrow">→</div>
        <div class="quiz-flow-step">
          <span class="qfs-num">2</span>
          <span>拼写题</span>
        </div>
        <div class="qfs-arrow">→</div>
        <div class="quiz-flow-step">
          <span class="qfs-num">3</span>
          <span>结果</span>
        </div>
      </div>
      <button class="btn-primary quiz-start-btn" onclick="startQuiz()">开始练习</button>
    </div>`;
}

function renderQuizCard() {
  const el = document.getElementById('quiz-content');
  const word = quiz.words[quiz.idx];
  const total = quiz.words.length;
  const pct = Math.round(((quiz.idx) / total) * 100);

  const progressBar = `
    <div class="quiz-progress">
      <div class="quiz-progress-bar" style="width:${pct}%"></div>
    </div>
    <div class="quiz-progress-label">${quiz.phase === 'choice' ? '选择题' : '拼写题'} · ${quiz.idx + 1} / ${total}</div>`;

  if (quiz.phase === 'choice') {
    const options = getOptions(word);
    const optBtns = options.map((opt) => {
      let cls = 'quiz-option';
      if (quiz.answered) {
        if (opt === word.zh) cls += ' correct';
        else if (opt === quiz._chosen && !quiz.lastOk) cls += ' wrong';
      }
      const disabled = quiz.answered ? 'disabled' : '';
      return `<button class="${cls}" ${disabled} onclick="answerChoice(${JSON.stringify(opt)})">${esc(opt)}</button>`;
    }).join('');

    const feedback = quiz.answered
      ? `<div class="quiz-feedback ${quiz.lastOk ? 'ok' : 'fail'}">${quiz.lastOk ? '正确！' : `正确答案：${esc(word.zh)}`}</div>`
      : '';

    const nextBtn = quiz.answered
      ? `<button class="btn-primary quiz-next-btn" onclick="nextQuizCard()">下一题 →</button>`
      : '';

    el.innerHTML = `
      ${progressBar}
      <div class="quiz-card">
        <div class="quiz-card-meta">
          <span class="badge cat-${esc(word.category)}">${CAT_LABELS[word.category] || word.category}</span>
          <button class="speak-btn" onclick="speak(${JSON.stringify(word.en)}, this)" aria-label="朗读">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/>
              <path d="M19.07 4.93a10 10 0 0 1 0 14.14"/>
              <path d="M15.54 8.46a5 5 0 0 1 0 7.07"/>
            </svg>
          </button>
        </div>
        <div class="quiz-word">${esc(word.en)}</div>
        <div class="quiz-def">${esc(word.definition)}</div>
        <div class="quiz-options">${optBtns}</div>
        ${feedback}
        ${nextBtn}
      </div>`;
  } else {
    // 拼写题（仅非 daily 分类）
    const vocabOnly = quiz.words.filter((w) => w.category !== 'daily');
    const spellIdx = quiz.idx;
    const spellWord = vocabOnly[spellIdx];
    if (!spellWord) {
      finishQuiz();
      return;
    }

    const feedback = quiz.answered
      ? `<div class="quiz-feedback ${quiz.lastOk ? 'ok' : 'fail'}">${quiz.lastOk ? '正确！' : `正确答案：${esc(spellWord.en)}`}</div>`
      : '';

    const nextBtn = quiz.answered
      ? `<button class="btn-primary quiz-next-btn" onclick="nextSpellCard()">下一题 →</button>`
      : '';

    el.innerHTML = `
      ${progressBar}
      <div class="quiz-card">
        <div class="quiz-card-meta">
          <span class="badge cat-${esc(spellWord.category)}">${CAT_LABELS[spellWord.category] || spellWord.category}</span>
          <span class="quiz-phase-tag">拼写</span>
        </div>
        <div class="quiz-word zh">${esc(spellWord.zh)}</div>
        <div class="quiz-def">${esc(spellWord.definition)}</div>
        ${!quiz.answered ? `
        <div class="quiz-spell-row">
          <input class="quiz-spell-input" id="spellInput" type="text" placeholder="输入英文…" autocomplete="off" autocorrect="off" spellcheck="false" />
          <button class="btn-primary" onclick="answerSpell()">提交</button>
        </div>` : ''}
        ${feedback}
        ${nextBtn}
      </div>`;

    if (!quiz.answered) {
      const inp = document.getElementById('spellInput');
      if (inp) {
        inp.focus();
        inp.addEventListener('keydown', (e) => { if (e.key === 'Enter') answerSpell(); });
      }
    }
  }
}

window.answerChoice = function (chosen) {
  if (quiz.answered) return;
  quiz._chosen = chosen;
  quiz.lastOk = chosen === quiz.words[quiz.idx].zh;
  quiz.answered = true;
  if (quiz.lastOk) quiz.correct++; else quiz.wrong++;
  renderQuizCard();
};

window.answerSpell = function () {
  if (quiz.answered) return;
  const inp = document.getElementById('spellInput');
  if (!inp) return;
  const vocabOnly = quiz.words.filter((w) => w.category !== 'daily');
  const spellWord = vocabOnly[quiz.idx];
  if (!spellWord) return;
  const typed = inp.value.trim().toLowerCase();
  const correct = spellWord.en.toLowerCase();
  quiz.lastOk = typed === correct;
  quiz.answered = true;
  if (quiz.lastOk) quiz.correct++; else quiz.wrong++;
  renderQuizCard();
};

window.nextQuizCard = function () {
  quiz.idx++;
  quiz.answered = false;
  quiz.lastOk = null;
  if (quiz.idx >= quiz.words.length) {
    // 选择题结束，切换到拼写题
    const vocabOnly = quiz.words.filter((w) => w.category !== 'daily');
    if (vocabOnly.length === 0) {
      finishQuiz();
      return;
    }
    quiz.phase = 'spell';
    quiz.idx = 0;
    quiz.words = shuffle(vocabOnly);
  }
  renderQuizCard();
};

window.nextSpellCard = function () {
  const vocabOnly = quiz.words.filter((w) => w.category !== 'daily');
  quiz.idx++;
  quiz.answered = false;
  quiz.lastOk = null;
  if (quiz.idx >= vocabOnly.length) {
    finishQuiz();
    return;
  }
  renderQuizCard();
};

function finishQuiz() {
  quiz.phase = 'done';
  const total = quiz.correct + quiz.wrong;
  const pct = total > 0 ? Math.round((quiz.correct / total) * 100) : 0;
  const emoji = pct >= 90 ? '完美' : pct >= 70 ? '不错' : '继续加油';
  document.getElementById('quiz-content').innerHTML = `
    <div class="quiz-done">
      <div class="quiz-done-icon">${pct >= 90 ? '★' : pct >= 70 ? '○' : '△'}</div>
      <h2 class="quiz-done-title">${emoji}！</h2>
      <div class="quiz-done-score">${quiz.correct} / ${total}</div>
      <div class="quiz-done-pct">正确率 ${pct}%</div>
      <button class="btn-primary" style="margin-top:1.5rem" onclick="startQuiz()">再练一遍</button>
    </div>`;
}

/* ── 标签切换 ────────────────────────────────────────────────────────────── */
function switchTab(tab) {
  state.tab = tab;

  document.querySelectorAll('.tab-btn').forEach((b) => {
    const active = b.dataset.tab === tab;
    b.classList.toggle('active', active);
    b.setAttribute('aria-selected', String(active));
  });
  document.querySelectorAll('.tab-panel').forEach((p) => {
    p.classList.toggle('active', p.id === `tab-${tab}`);
  });

  if (tab === 'words' && !state.allWordsData) loadWordBank();
  if (tab === 'progress' && state.todayData) renderProgress();
  if (tab === 'quiz' && state.todayData && quiz.phase === 'idle') renderQuizStart();
}

document.querySelectorAll('.tab-btn').forEach((btn) => {
  btn.addEventListener('click', () => switchTab(btn.dataset.tab));
});

/* ── 主题切换 ────────────────────────────────────────────────────────────── */
function toggleTheme() {
  const html = document.documentElement;
  const next = html.dataset.theme === 'dark' ? 'light' : 'dark';
  html.dataset.theme = next;
  localStorage.setItem('theme', next);
}

document.getElementById('themeToggle').addEventListener('click', toggleTheme);

(function initTheme() {
  const saved = localStorage.getItem('theme');
  if (saved) document.documentElement.dataset.theme = saved;
})();

/* ── 启动 ────────────────────────────────────────────────────────────────── */
async function init() {
  try {
    state.todayData = await fetch('./today.json').then((r) => {
      if (!r.ok) throw new Error(r.status);
      return r.json();
    });
  } catch {
    document.getElementById('today-content').innerHTML = `
      <div class="state-box">
        <div class="state-icon">◇</div>
        <p>尚未生成今日内容。<br>
        请在项目根目录运行 <code>python scripts/seed.py</code>，再运行 <code>python scripts/generate.py</code>，然后刷新页面。</p>
      </div>`;
    return;
  }

  renderToday();
}

init();
