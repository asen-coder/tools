/* ── 状态 ──────────────────────────────────────────────────────────────── */
const state = {
  todayData: null,
  allWordsData: null,
  tab: 'today',
  search: '',
  category: 'all',
};

const CAT_LABELS = { ai: 'AI', programming: '编程', music: '音乐', daily: '日常' };

/* ── 语音 ──────────────────────────────────────────────────────────────── */
let preferredVoice = null;

function initVoice() {
  const pick = () => {
    const voices = speechSynthesis.getVoices();
    preferredVoice =
      voices.find((v) => v.lang === 'en-US' && v.localService) ||
      voices.find((v) => v.lang === 'en-US') ||
      voices.find((v) => v.lang.startsWith('en')) ||
      null;
  };
  speechSynthesis.addEventListener('voiceschanged', pick);
  pick();
}

window.speak = function (text, btnEl) {
  if (!('speechSynthesis' in window)) return;
  window.speechSynthesis.cancel();

  const u = new SpeechSynthesisUtterance(text);
  u.lang = 'en-US';
  u.rate = 0.85;
  u.pitch = 1;
  if (preferredVoice) u.voice = preferredVoice;

  if (btnEl) {
    btnEl.classList.add('speaking');
    u.onend = () => btnEl.classList.remove('speaking');
    u.onerror = () => btnEl.classList.remove('speaking');
  }
  window.speechSynthesis.speak(u);
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

  const pills = ['all', 'ai', 'programming', 'music', 'daily']
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
  initVoice();

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
