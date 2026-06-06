// ============================================================
// GovCheck · Frontend Script
// Features: form, search, filters, score bars, AI summarizer
// ============================================================

'use strict';

// ── DOM refs ──────────────────────────────────────────────────────────────────
const navbar       = document.getElementById('navbar');
const form         = document.getElementById('eligibility-form');
const findBtn      = document.getElementById('find-btn');
const errorMsg     = document.getElementById('error-msg');
const resultsSection = document.getElementById('results-section');
const resultCount  = document.getElementById('result-count');
const centralWrapper = document.getElementById('central-wrapper');
const stateWrapper   = document.getElementById('state-wrapper');
const centralList  = document.getElementById('central-list');
const stateList    = document.getElementById('state-list');
const noResults    = document.getElementById('no-results');
const filterTabs   = document.querySelectorAll('.filter-tab');
const searchInput  = document.getElementById('global-search');
const searchBtn    = document.getElementById('search-btn');
const searchResultsBox = document.getElementById('search-results');
const aiInput      = document.getElementById('ai-input');
const aiBtn        = document.getElementById('ai-btn');
const aiResult     = document.getElementById('ai-result');

// ── Navbar scroll ─────────────────────────────────────────────────────────────
window.addEventListener('scroll', () => {
  navbar.classList.toggle('scrolled', window.scrollY > 50);
  updateActiveNav();
});

// ── Animated stat counters ───────────────────────────────────────────────────
function animateCounter(el, target, duration = 1800) {
  if (!target) return;
  const step = target / (duration / 16);
  let cur = 0;
  const t = setInterval(() => {
    cur += step;
    if (cur >= target) { el.textContent = target + '+'; clearInterval(t); }
    else el.textContent = Math.floor(cur) + '+';
  }, 16);
}

const statsObserver = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if (!entry.isIntersecting) return;
    entry.target.querySelectorAll('.stat-number[data-value]').forEach(el => {
      const v = parseInt(el.getAttribute('data-value'));
      if (!isNaN(v)) animateCounter(el, v);
    });
    statsObserver.unobserve(entry.target);
  });
}, { threshold: 0.2 });
document.querySelectorAll('.stats-section').forEach(el => statsObserver.observe(el));

// ── Form submission ───────────────────────────────────────────────────────────
if (form) {
  form.addEventListener('submit', async e => {
    e.preventDefault();
    hideError();
    setFindLoading(true);

    try {
      const res  = await fetch('/get-exams', { method: 'POST', body: new FormData(form) });
      const data = await res.json();
      if (data.success) {
        renderResults(data.results || []);
        resultsSection.classList.remove('hidden');
        setTimeout(() => resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' }), 200);
      } else {
        showError(data.error || 'No results found. Try different filters.');
      }
    } catch {
      showError('Connection error. Please try again.');
    } finally {
      setFindLoading(false);
    }
  });
}

function setFindLoading(on) {
  if (!findBtn) return;
  findBtn.disabled = on;
  findBtn.innerHTML = on
    ? '<span class="spinner"></span> Searching…'
    : '<span>Discover Opportunities</span>';
}

function showError(msg) {
  errorMsg.textContent = msg;
  errorMsg.classList.add('show');
}
function hideError() { errorMsg.classList.remove('show'); }

// ── Render results ────────────────────────────────────────────────────────────
function renderResults(results) {
  centralList.innerHTML = '';
  stateList.innerHTML   = '';
  noResults.classList.add('hidden');

  if (!results.length) {
    noResults.classList.remove('hidden');
    updateResultCount(0);
    return;
  }

  const central = results.filter(e =>
    ['CENTRAL', 'UNION TERRITORY'].some(k => (e.govt_type || '').toUpperCase().includes(k)));
  const state = results.filter(e =>
    !['CENTRAL', 'UNION TERRITORY'].some(k => (e.govt_type || '').toUpperCase().includes(k)));

  central.forEach((e, i) => centralList.appendChild(makeCard(e, i)));
  state.forEach((e, i)   => stateList.appendChild(makeCard(e, i)));
  updateResultCount(results.length);

  // Reset filter tabs
  filterTabs.forEach(t => t.classList.remove('active'));
  document.querySelector('[data-filter="all"]')?.classList.add('active');
  centralWrapper.style.display = '';
  stateWrapper.style.display   = '';
}

function makeCard(exam, idx) {
  const card = document.createElement('div');
  card.className = 'result-card';
  card.style.animationDelay = `${idx * 0.04}s`;

  const score    = exam.match_score ?? 0;
  const scoreColor = score >= 80 ? '#3dba6f' : score >= 60 ? '#e8813a' : '#e84444';
  const govtType = (exam.govt_type || 'Government').replace(' GOVERNMENT', '');
  const group    = Array.isArray(exam.group) ? exam.group.join(' · ') : (exam.group || 'N/A');
  const maxAge   = getMaxAge(exam);
  const eligArr  = Array.isArray(exam.eligibility) ? exam.eligibility : (exam.eligibility ? [exam.eligibility] : []);
  const link     = exam.official_link;
  const verifiedHtml = link
    ? exam.verified
      ? `<span class="verified-badge">✓ Verified Source</span>`
      : `<span class="unverified-badge">⚠ Verify Source</span>`
    : '';

  card.innerHTML = `
    <div class="result-header">
      <h3 class="result-title">${exam.name || 'Exam'}</h3>
      <span class="result-badge">${govtType}</span>
    </div>
    <div class="match-score">
      <div class="score-bar-track">
        <div class="score-bar-fill" style="width:${score}%; background:${scoreColor}"></div>
      </div>
      <span class="score-label" style="color:${scoreColor}">${score}%</span>
    </div>
    <div class="result-meta">
      <div class="result-item">
        <span class="result-label">Age Limit</span>
        <span class="result-value">${exam.min_age ?? '?'}–${maxAge} yrs</span>
      </div>
      <div class="result-item">
        <span class="result-label">Group</span>
        <span class="result-value">${group}</span>
      </div>
      <div class="result-item">
        <span class="result-label">Conducting Body</span>
        <span class="result-value">${exam.conducting_type || 'N/A'}</span>
      </div>
      <div class="result-item">
        <span class="result-label">Coverage</span>
        <span class="result-value">${exam.states === 'all' ? 'All India' : (exam.states || 'N/A')}</span>
      </div>
    </div>
    <p class="result-desc">${exam.description || ''}</p>
    <div class="result-footer">
      <div class="result-tags">${eligArr.map(e => `<span class="result-tag">${e}</span>`).join('')}</div>
      <div style="display:flex;align-items:center;gap:12px;">
        ${verifiedHtml}
        ${link ? `<a href="${link}" target="_blank" rel="noopener" class="result-link">Official →</a>` : ''}
      </div>
    </div>`;

  return card;
}

function getMaxAge(exam) {
  const d = exam.max_age;
  if (!d) return '?';
  if (typeof d === 'number') return d;
  if (typeof d === 'object') return d['General'] ?? Object.values(d)[0] ?? '?';
  return '?';
}

function updateResultCount(n) {
  if (resultCount) resultCount.textContent = `${n} exam${n !== 1 ? 's' : ''} found`;
}

// ── Filter tabs ───────────────────────────────────────────────────────────────
filterTabs.forEach(tab => {
  tab.addEventListener('click', () => {
    filterTabs.forEach(t => t.classList.remove('active'));
    tab.classList.add('active');
    const f = tab.getAttribute('data-filter');
    centralWrapper.style.display = (f === 'state')   ? 'none' : '';
    stateWrapper.style.display   = (f === 'central') ? 'none' : '';
  });
});

// ── Global search ─────────────────────────────────────────────────────────────
let searchTimeout;
searchInput?.addEventListener('input', () => {
  clearTimeout(searchTimeout);
  const q = searchInput.value.trim();
  if (!q) { searchResultsBox.classList.add('hidden'); return; }
  searchTimeout = setTimeout(() => doSearch(q), 320);
});
searchBtn?.addEventListener('click', () => doSearch(searchInput.value.trim()));

async function doSearch(q) {
  if (!q) return;
  try {
    const res  = await fetch(`/search?q=${encodeURIComponent(q)}`);
    const data = await res.json();
    renderSearchResults(data.results || []);
  } catch { /* silent */ }
}

function renderSearchResults(results) {
  searchResultsBox.innerHTML = '';
  if (!results.length) {
    searchResultsBox.innerHTML = '<div class="search-item"><span class="search-item-name" style="color:var(--text-muted)">No results found</span></div>';
  } else {
    results.slice(0, 8).forEach(e => {
      const item = document.createElement('a');
      item.className = 'search-item';
      item.href = e.official_link || '#';
      item.target = '_blank';
      item.rel = 'noopener';
      item.innerHTML = `
        <span class="search-item-name">${e.name}</span>
        <span class="search-item-meta">${e.conducting_type || ''}</span>`;
      searchResultsBox.appendChild(item);
    });
  }
  searchResultsBox.classList.remove('hidden');
}

document.addEventListener('click', e => {
  if (!searchResultsBox.contains(e.target) && e.target !== searchInput)
    searchResultsBox.classList.add('hidden');
});

// ── AI Summarizer ─────────────────────────────────────────────────────────────
aiBtn?.addEventListener('click', async () => {
  const text = aiInput.value.trim();
  if (!text) return;

  const original = aiBtn.innerHTML;
  aiBtn.disabled = true;
  aiBtn.innerHTML = '<span class="spinner"></span> Summarizing…';
  aiResult.classList.add('hidden');

  try {
    const res  = await fetch('/summarize', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text })
    });
    const data = await res.json();
    if (data.success) {
      renderAISummary(data.summary);
    } else {
      aiResult.innerHTML = `<p style="color:var(--red)">${data.error || 'AI error. Check your GEMINI_API_KEY.'}</p>`;
      aiResult.classList.remove('hidden');
    }
  } catch {
    aiResult.innerHTML = `<p style="color:var(--red)">Connection error. Try again.</p>`;
    aiResult.classList.remove('hidden');
  } finally {
    aiBtn.disabled = false;
    aiBtn.innerHTML = original;
  }
});

function renderAISummary(s) {
  const dates = Object.entries(s.important_dates || {})
    .map(([k, v]) => `<li><strong>${k.replace(/_/g, ' ')}:</strong> ${v}</li>`).join('');
  const process = (s.selection_process || []).map(p => `<li>${p}</li>`).join('');
  const docs    = (s.required_documents || []).map(d => `<li>${d}</li>`).join('');

  aiResult.innerHTML = `
    <div class="ai-quick-summary">${s.quick_summary || ''}</div>
    <div class="ai-result-grid">
      <div class="ai-result-item">
        <h4>Eligibility</h4>
        <p>${s.eligibility || 'Not specified'}</p>
      </div>
      <div class="ai-result-item">
        <h4>Age Limit</h4>
        <p>${s.age_limit || 'Not specified'}</p>
      </div>
      <div class="ai-result-item">
        <h4>Important Dates</h4>
        <ul>${dates || '<li>Not found</li>'}</ul>
      </div>
      <div class="ai-result-item">
        <h4>Selection Process</h4>
        <ul>${process || '<li>Not specified</li>'}</ul>
      </div>
      <div class="ai-result-item" style="grid-column:1/-1">
        <h4>Required Documents</h4>
        <ul>${docs || '<li>Not specified</li>'}</ul>
      </div>
    </div>`;
  aiResult.classList.remove('hidden');
}

// ── Active nav link ───────────────────────────────────────────────────────────
function updateActiveNav() {
  const sections  = document.querySelectorAll('section[id]');
  const navLinks  = document.querySelectorAll('.navbar-nav a[href^="#"]');
  let current = '';
  sections.forEach(s => {
    if (window.scrollY >= s.offsetTop - 220) current = s.id;
  });
  navLinks.forEach(a => {
    a.classList.toggle('active', a.getAttribute('href') === `#${current}`);
  });
}
