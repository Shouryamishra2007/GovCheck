// ═══════════════════════════════════════════════════════════════════════════════
// GovCheck Emotional Design Features
// Purpose: Personalization, motivation, and aspirational microcopy
// ═══════════════════════════════════════════════════════════════════════════════

'use strict';

// DOM References
const form = document.getElementById('eligibility-form');
const findBtn = document.getElementById('find-btn');
const errorMsg = document.getElementById('error-msg');
const resultsSection = document.getElementById('results-section');
const resultCount = document.getElementById('result-count');
const centralWrapper = document.getElementById('central-wrapper');
const stateWrapper = document.getElementById('state-wrapper');
const centralList = document.getElementById('central-list');
const stateList = document.getElementById('state-list');
const noResults = document.getElementById('no-results');
const filterTabs = document.querySelectorAll('.filter-tab');
const searchInput = document.getElementById('global-search');
const searchBtn = document.getElementById('search-btn');
const searchResultsBox = document.getElementById('search-results');
const aiInput = document.getElementById('ai-input');
const aiBtn = document.getElementById('ai-btn');
const aiResult = document.getElementById('ai-result');
const navbar = document.getElementById('navbar');

// ═══════════════════════════════════════════════════════════════════════════════
// NAVBAR SCROLL DETECTION
// ═══════════════════════════════════════════════════════════════════════════════
window.addEventListener('scroll', () => {
  navbar.classList.toggle('scrolled', window.scrollY > 50);
});

// ═══════════════════════════════════════════════════════════════════════════════
// FORM SUBMISSION - WITH PERSONALIZED GREETING
// ═══════════════════════════════════════════════════════════════════════════════
if (form) {
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    hideError();
    setFindLoading(true);

    try {
      const res = await fetch('/get-exams', { method: 'POST', body: new FormData(form) });
      const data = await res.json();
      
      if (data.success) {
        // Show personalized greeting before results
        showPersonalizedGreeting(data);
        renderResults(data.results || []);
        resultsSection.classList.remove('hidden');
        setTimeout(() => resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' }), 200);
      } else {
        showError(data.error || 'No results found. Try different filters.');
      }
    } catch (e) {
      showError('Connection error. Please try again.');
    } finally {
      setFindLoading(false);
    }
  });
}

// ═══════════════════════════════════════════════════════════════════════════════
// PERSONALIZED GREETING SYSTEM
// ═══════════════════════════════════════════════════════════════════════════════
function showPersonalizedGreeting(data) {
  const status = form.querySelector('select[name="status"]').value;
  const category = form.querySelector('select[name="category"]').value;
  
  const greetings = {
    '12th': [
      { text: 'Welcome, Future Officer', subtext: 'Your journey to government service starts here.' },
      { text: 'Welcome, Future Researcher', subtext: 'Let\'s find opportunities for your research career.' },
      { text: 'Welcome, Future Engineer', subtext: 'Great exams are waiting for you.' },
    ],
    'graduation': [
      { text: 'Welcome back, Achiever', subtext: `You have ${data.results.length} unlocked opportunities.` },
      { text: 'Welcome, Career Builder', subtext: 'Your next step is just ahead.' },
      { text: 'Welcome, Future Leader', subtext: `${data.results.length} paths forward are now visible.` },
    ],
    'post-graduation': [
      { text: 'Welcome, Specialist', subtext: 'Elite opportunities matched to your expertise.' },
      { text: 'Welcome, Expert', subtext: `Found ${data.results.length} opportunities for your advanced profile.` },
    ],
  };

  const greetingArray = greetings[status] || greetings['graduation'];
  const greeting = greetingArray[Math.floor(Math.random() * greetingArray.length)];

  document.getElementById('greeting-text').textContent = greeting.text;
  document.getElementById('greeting-subtext').textContent = greeting.subtext;
}

// ═══════════════════════════════════════════════════════════════════════════════
// RENDER RESULTS WITH EMOTIONAL DESIGN
// ═══════════════════════════════════════════════════════════════════════════════
function renderResults(results) {
  centralList.innerHTML = '';
  stateList.innerHTML = '';
  noResults.classList.add('hidden');

  if (!results.length) {
    noResults.classList.remove('hidden');
    updateResultCount(0);
    return;
  }

  const central = results.filter(e =>
    ['CENTRAL', 'UNION TERRITORY'].some(k => (e.govt_type || '').toUpperCase().includes(k))
  );
  const state = results.filter(e =>
    !['CENTRAL', 'UNION TERRITORY'].some(k => (e.govt_type || '').toUpperCase().includes(k))
  );

  central.forEach((e, i) => centralList.appendChild(makeCard(e, i)));
  state.forEach((e, i) => stateList.appendChild(makeCard(e, i)));

  updateResultCount(results.length);
  updateHighlights(results);

  // Reset filter tabs
  filterTabs.forEach(t => t.classList.remove('active'));
  document.querySelector('[data-filter="all"]')?.classList.add('active');
  centralWrapper.style.display = '';
  stateWrapper.style.display = '';
}

// ═══════════════════════════════════════════════════════════════════════════════
// UPDATE OPPORTUNITY HIGHLIGHTS
// ═══════════════════════════════════════════════════════════════════════════════
function updateHighlights(results) {
  // Perfect matches (score >= 85)
  const perfectMatches = results.filter(e => e.match_score >= 85).length;
  document.getElementById('perfect-matches').textContent = perfectMatches;

  // Closing soon (deadline < 10 days)
  const closingSoon = results.filter(e => {
    const deadline = e.application_deadline;
    if (!deadline) return false;
    const daysLeft = calculateDaysLeft(deadline);
    return daysLeft > 0 && daysLeft < 10;
  }).length;
  document.getElementById('closing-soon').textContent = closingSoon;

  // Recently added (optional field)
  const recentlyAdded = Math.floor(results.length * 0.15);
  document.getElementById('recently-added').textContent = recentlyAdded;
}

function calculateDaysLeft(dateStr) {
  try {
    const date = new Date(dateStr);
    const today = new Date();
    return Math.ceil((date - today) / (1000 * 60 * 60 * 24));
  } catch {
    return 999;
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// CREATE OPPORTUNITY CARD WITH EMOTIONAL DESIGN
// ═══════════════════════════════════════════════════════════════════════════════
function makeCard(exam, idx) {
  const card = document.createElement('div');
  card.className = 'result-card';
  card.style.animationDelay = `${idx * 0.05}s`;

  const score = exam.match_score ?? 0;
  let scoreColor = '#ff4757';
  let scoreStatus = 'Not Ideal';
  
  if (score >= 85) {
    scoreColor = '#00ff88';
    scoreStatus = 'Perfect Match';
  } else if (score >= 70) {
    scoreColor = '#00d4ff';
    scoreStatus = 'Strong Match';
  } else if (score >= 50) {
    scoreColor = '#ffa500';
    scoreStatus = 'Good Match';
  }

  const govtType = (exam.govt_type || 'Government').replace(' GOVERNMENT', '');
  const group = Array.isArray(exam.group) ? exam.group.join(' · ') : (exam.group || 'N/A');
  const maxAge = getMaxAge(exam);
  const eligArr = Array.isArray(exam.eligibility) ? exam.eligibility : (exam.eligibility ? [exam.eligibility] : []);
  const link = exam.official_link;
  
  const verifiedHtml = link
    ? exam.verified
      ? `<span class="verified-badge">✓ Verified Source</span>`
      : `<span class="unverified-badge">⚠ Verify Source</span>`
    : '';

  // Deadline indicator
  const daysLeft = calculateDaysLeft(exam.application_deadline);
  let deadlineHtml = '';
  let deadlineIcon = '⭕';
  
  if (daysLeft < 0) {
    deadlineIcon = '❌';
    deadlineHtml = '<span style="color: #ff4757; font-size: 0.8rem; font-weight: 700;">Application Closed</span>';
  } else if (daysLeft < 3) {
    deadlineIcon = '🔴';
    deadlineHtml = `<span style="color: #ff4757; font-size: 0.8rem; font-weight: 700;">⏰ ${daysLeft} days left!</span>`;
  } else if (daysLeft < 15) {
    deadlineIcon = '🟡';
    deadlineHtml = `<span style="color: #ffa500; font-size: 0.8rem; font-weight: 700;">${daysLeft} days left</span>`;
  } else {
    deadlineIcon = '🟢';
    deadlineHtml = `<span style="color: #00ff88; font-size: 0.8rem; font-weight: 700;">Safe: ${daysLeft} days</span>`;
  }

  card.innerHTML = `
    <div class="result-header">
      <h3 class="result-title">${exam.name || 'Exam'}</h3>
      <span class="result-badge">${govtType}</span>
    </div>
    
    <div class="match-score">
      <span class="score-label">${scoreStatus}</span>
      <div class="score-bar-track">
        <div class="score-bar-fill" style="width:${score}%; background: linear-gradient(90deg, ${scoreColor}, #ff6b9d);"></div>
      </div>
      <span class="score-percent">${score}%</span>
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
        <span class="result-label">Deadline</span>
        ${deadlineHtml}
      </div>
    </div>
    
    <p class="result-desc">${exam.description || ''}</p>
    
    <div class="result-footer">
      <div class="result-tags">${eligArr.map(e => `<span class="result-tag">${e}</span>`).join('')}</div>
      <div style="display:flex; align-items:center; gap:8px;">
        ${verifiedHtml}
        ${link ? `<a href="${link}" target="_blank" rel="noopener" class="result-link">Open →</a>` : ''}
      </div>
    </div>
  `;

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
  if (resultCount) {
    resultCount.textContent = n === 0 
      ? '0 exams found — but keep exploring!' 
      : `🔓 You have unlocked ${n} opportunity${n !== 1 ? 'ies' : ''}`;
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// ERROR HANDLING
// ═══════════════════════════════════════════════════════════════════════════════
function setFindLoading(on) {
  if (!findBtn) return;
  findBtn.disabled = on;
  findBtn.innerHTML = on
    ? '<span class="spinner"></span> Unlocking opportunities…'
    : '<span>Unlock My Opportunities</span>';
}

function showError(msg) {
  errorMsg.textContent = msg;
  errorMsg.classList.add('show');
}

function hideError() {
  errorMsg.classList.remove('show');
}

// ═══════════════════════════════════════════════════════════════════════════════
// FILTER TABS
// ═══════════════════════════════════════════════════════════════════════════════
filterTabs.forEach(tab => {
  tab.addEventListener('click', () => {
    filterTabs.forEach(t => t.classList.remove('active'));
    tab.classList.add('active');
    const f = tab.getAttribute('data-filter');
    centralWrapper.style.display = (f === 'state') ? 'none' : '';
    stateWrapper.style.display = (f === 'central') ? 'none' : '';
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// GLOBAL SEARCH
// ═══════════════════════════════════════════════════════════════════════════════
let searchTimeout;
searchInput?.addEventListener('input', () => {
  clearTimeout(searchTimeout);
  const q = searchInput.value.trim();
  if (!q) {
    searchResultsBox.classList.add('hidden');
    return;
  }
  searchTimeout = setTimeout(() => doSearch(q), 320);
});

searchBtn?.addEventListener('click', () => doSearch(searchInput.value.trim()));

async function doSearch(q) {
  if (!q) return;
  try {
    const res = await fetch(`/search?q=${encodeURIComponent(q)}`);
    const data = await res.json();
    renderSearchResults(data.results || []);
  } catch (e) {
    console.error(e);
  }
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
  if (!searchResultsBox?.contains(e.target) && e.target !== searchInput)
    searchResultsBox?.classList.add('hidden');
});

// ═══════════════════════════════════════════════════════════════════════════════
// AI SUMMARIZER WITH GROQ
// ═══════════════════════════════════════════════════════════════════════════════
aiBtn?.addEventListener('click', async () => {
  const text = aiInput.value.trim();
  if (!text) {
    showError('Please paste a notification first.');
    return;
  }

  const original = aiBtn.innerHTML;
  aiBtn.disabled = true;
  aiBtn.innerHTML = '<span class="spinner"></span> Analyzing with AI…';
  aiResult.classList.add('hidden');

  try {
    const res = await fetch('/summarize', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text })
    });
    const data = await res.json();
    
    if (data.success) {
      renderAISummary(data.summary);
    } else {
      aiResult.innerHTML = `<p style="color: var(--red)">❌ ${data.error || 'AI analysis failed.'}</p>`;
      aiResult.classList.remove('hidden');
    }
  } catch (e) {
    aiResult.innerHTML = `<p style="color: var(--red)">❌ Connection error. Try again.</p>`;
    aiResult.classList.remove('hidden');
  } finally {
    aiBtn.disabled = false;
    aiBtn.innerHTML = original;
  }
});

function renderAISummary(s) {
  const dates = Object.entries(s.important_dates || {})
    .map(([k, v]) => `<li><strong>${k.replace(/_/g, ' ')}:</strong> ${v}</li>`)
    .join('');
  const process = (s.selection_process || []).map(p => `<li>${p}</li>`).join('');
  const docs = (s.required_documents || []).map(d => `<li>${d}</li>`).join('');

  aiResult.innerHTML = `
    <div class="ai-quick-summary">✨ ${s.quick_summary || 'Summary generated.'}</div>
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

// ═══════════════════════════════════════════════════════════════════════════════
// SMOOTH SCROLL OBSERVER FOR NAV LINKS
// ═══════════════════════════════════════════════════════════════════════════════
function updateActiveNav() {
  const sections = document.querySelectorAll('section[id]');
  const navLinks = document.querySelectorAll('.navbar-nav a[href^="#"]');
  
  let current = '';
  sections.forEach(s => {
    if (window.scrollY >= s.offsetTop - 220) current = s.id;
  });
  
  navLinks.forEach(a => {
    a.classList.toggle('active', a.getAttribute('href') === `#${current}`);
  });
}

window.addEventListener('scroll', updateActiveNav);
