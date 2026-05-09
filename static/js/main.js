// ===========================
// GovCheck - Fixed Frontend JS
// ===========================

// DOM Elements
const navBar       = document.querySelector('.navbar');
const eligibilityForm = document.getElementById('eligibility-form');
const findBtn      = document.getElementById('find-btn');
const errorMsg     = document.getElementById('error-msg');
const resultsSection = document.getElementById('results-section');
const resultCount  = document.getElementById('result-count');

// BUG FIX: data-filter selector (HTML now has data-filter attributes)
const filterButtons = document.querySelectorAll('[data-filter]');

// ===========================
// Navbar Scroll Effect
// BUG FIX: was adding 'navbar-scrolled' but CSS class is 'scrolled'
// ===========================
window.addEventListener('scroll', () => {
  if (window.scrollY > 50) {
    navBar.classList.add('scrolled');
  } else {
    navBar.classList.remove('scrolled');
  }
});

// ===========================
// Smooth Scroll for Nav Links
// ===========================
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function(e) {
    const target = document.querySelector(this.getAttribute('href'));
    if (target) {
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  });
});

// ===========================
// Animated Counter for Stats
// BUG FIX: guard against non-numeric data-value to avoid NaN animations
// ===========================
function animateCounter(element, target, duration = 2000) {
  if (!target || target === 0) return;
  const increment = target / (duration / 16);
  let current = 0;
  const counter = setInterval(() => {
    current += increment;
    if (current >= target) {
      element.textContent = target + '+';
      clearInterval(counter);
    } else {
      element.textContent = Math.floor(current) + '+';
    }
  }, 16);
}

const statObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.querySelectorAll('.stat-number[data-value]').forEach(counter => {
        const value = parseInt(counter.getAttribute('data-value'));
        if (!isNaN(value) && value > 0) animateCounter(counter, value);
      });
      statObserver.unobserve(entry.target);
    }
  });
}, { threshold: 0.1 });

const statsSection = document.querySelector('.stats-section');
if (statsSection) statObserver.observe(statsSection);

// ===========================
// Intersection Observer (fade-in)
// ===========================
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('fade-in-visible');
      observer.unobserve(entry.target);
    }
  });
}, { threshold: 0.1, rootMargin: '0px 0px -80px 0px' });

document.querySelectorAll('.feature-card, .stat-card, .step-card, .trending-card').forEach(el => {
  observer.observe(el);
});

// ===========================
// Form Submission
// BUG FIX: form now submits as regular FormData to /get-exams (matches Flask route)
// BUG FIX: response reads data.success + data.results (matches Flask response format)
// ===========================
if (eligibilityForm) {
  eligibilityForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    errorMsg.innerHTML = '';
    errorMsg.classList.remove('show');

    const age      = document.getElementById('age').value.trim();
    const status   = document.getElementById('status').value;
    const category = document.getElementById('category').value;
    const state    = document.getElementById('state').value;

    if (!age || !status || !category || !state) {
      showError('Please fill in all fields');
      return;
    }

    setButtonLoading(true);

    try {
      const formData = new FormData(eligibilityForm);

      const response = await fetch('/get-exams', {
        method: 'POST',
        body: formData
      });

      const data = await response.json();

      if (data.success) {
        // BUG FIX: was data.results — app.py returns data.results ✓
        renderResults(data.results || []);
        scrollToResults();
      } else {
        showError(data.error || 'No exams found matching your criteria');
      }
    } catch (error) {
      showError('Error fetching results. Please try again.');
      console.error('Form submission error:', error);
    } finally {
      setButtonLoading(false);
    }
  });
}

// ===========================
// Button Loading State
// ===========================
function setButtonLoading(isLoading) {
  if (!findBtn) return;
  if (isLoading) {
    findBtn.disabled = true;
    findBtn.textContent = 'Searching...';
  } else {
    findBtn.disabled = false;
    findBtn.textContent = 'Discover Opportunities';
  }
}

// ===========================
// Error Display
// ===========================
function showError(message) {
  errorMsg.textContent = message;
  errorMsg.classList.add('show');
  setTimeout(() => errorMsg.classList.remove('show'), 5000);
}

// ===========================
// Render Results
// BUG FIX: was filtering by exam.type === 'Central'; JSON field is exam.govt_type
// BUG FIX: no-results now uses class .show instead of inline style
// ===========================
let allResults = [];

function renderResults(results) {
  if (!resultsSection) return;

  const centralList = document.getElementById('central-list');
  const stateList   = document.getElementById('state-list');
  const noResults   = document.getElementById('no-results');

  allResults = results;

  centralList.innerHTML = '';
  stateList.innerHTML   = '';
  noResults.classList.remove('show');

  if (!results || results.length === 0) {
    noResults.classList.add('show');
    updateResultCount(0);
    resultsSection.classList.add('show');
    return;
  }

  // BUG FIX: use govt_type (JSON field) instead of type
  const centralExams = results.filter(e => (e.govt_type || '').toUpperCase().includes('CENTRAL') ||
                                            (e.govt_type || '').toUpperCase().includes('UNION TERRITORY'));
  const stateExams   = results.filter(e => (e.govt_type || '').toUpperCase().includes('STATE'));

  centralExams.forEach((exam, i) => centralList.appendChild(createResultCard(exam, i)));
  stateExams.forEach((exam, i)   => stateList.appendChild(createResultCard(exam, i)));

  updateResultCount(results.length);
  resultsSection.classList.add('show');
}

// ===========================
// Create Result Card
// BUG FIX: all field names updated to match exams.json structure
//   exam.type       → exam.govt_type
//   exam.link       → exam.official_link
//   exam.department → exam.conducting_type
//   exam.position   → exam.group (array)
//   exam.ageLimit   → derived from exam.min_age + exam.max_age
//   exam.salary     → not in JSON; removed
//   exam.qualification → exam.eligibility (array)
// ===========================
function createResultCard(exam, index) {
  const card = document.createElement('div');
  card.className = 'result-card';
  card.style.animationDelay = `${index * 0.05}s`;

  const govtType = (exam.govt_type || 'Government').replace(' GOVERNMENT', '');
  const group    = Array.isArray(exam.group) ? exam.group.join(', ') : (exam.group || 'N/A');
  const ageRange = exam.min_age !== undefined
    ? `${exam.min_age}–${getMaxAge(exam)} yrs`
    : 'N/A';
  const eligibility = Array.isArray(exam.eligibility)
    ? exam.eligibility
    : (exam.eligibility ? [exam.eligibility] : []);
  const link = exam.official_link
    ? `<a href="${exam.official_link}" target="_blank" rel="noopener" class="result-link">Official Website →</a>`
    : '';

  card.innerHTML = `
    <div class="result-header">
      <h3 class="result-title">${exam.name || 'Exam'}</h3>
      <span class="result-badge">${govtType}</span>
    </div>
    <div class="result-meta">
      <div class="result-item">
        <span class="result-label">Age Limit</span>
        <span class="result-value">${ageRange}</span>
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
    <div class="result-tags">
      ${eligibility.map(e => `<span class="result-tag">${e}</span>`).join('')}
    </div>
    <div class="result-actions">${link}</div>
  `;

  return card;
}

// Helper: get max age for user's category from the age dict
function getMaxAge(exam) {
  const maxAgeData = exam.max_age;
  if (!maxAgeData) return '?';
  if (typeof maxAgeData === 'number') return maxAgeData;
  if (typeof maxAgeData === 'object') {
    // Show general max age in card; category-specific shown by backend filtering
    return maxAgeData['General'] || Object.values(maxAgeData)[0] || '?';
  }
  return '?';
}

// ===========================
// Update Result Count
// ===========================
function updateResultCount(count) {
  if (!resultCount) return;
  resultCount.textContent = `${count} exam${count !== 1 ? 's' : ''} found`;
}

// ===========================
// Filter Results
// BUG FIX: now targets #central-wrapper / #state-wrapper (parentElement of lists)
//          so the column heading is hidden/shown along with the list
// ===========================
if (filterButtons.length > 0) {
  filterButtons.forEach(button => {
    button.addEventListener('click', () => {
      filterButtons.forEach(btn => btn.classList.remove('active'));
      button.classList.add('active');
      filterResults(button.getAttribute('data-filter'));
    });
  });
}

function filterResults(filter) {
  const centralWrapper = document.getElementById('central-wrapper');
  const stateWrapper   = document.getElementById('state-wrapper');
  if (!centralWrapper || !stateWrapper) return;

  switch (filter) {
    case 'central':
      centralWrapper.style.display = 'block';
      stateWrapper.style.display   = 'none';
      break;
    case 'state':
      centralWrapper.style.display = 'none';
      stateWrapper.style.display   = 'block';
      break;
    default:
      centralWrapper.style.display = 'block';
      stateWrapper.style.display   = 'block';
  }
}

// ===========================
// Scroll to Results
// ===========================
function scrollToResults() {
  if (resultsSection) {
    setTimeout(() => {
      resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 300);
  }
}

// ===========================
// Dynamic Active Nav Link
// BUG FIX: was querying '.nav-links a' which doesn't exist; now '.navbar-nav a'
// ===========================
function updateActiveNavLink() {
  const sections = document.querySelectorAll('section[id]');
  const navLinks  = document.querySelectorAll('.navbar-nav a[href^="#"]');
  let current = '';
  sections.forEach(section => {
    if (window.scrollY >= section.offsetTop - 200) {
      current = section.getAttribute('id');
    }
  });
  navLinks.forEach(link => {
    link.classList.remove('active');
    if (link.getAttribute('href') === `#${current}`) link.classList.add('active');
  });
}
window.addEventListener('scroll', updateActiveNavLink);

// ===========================
// Form Input Focus Effects
// ===========================
document.querySelectorAll('#eligibility-form input, #eligibility-form select').forEach(input => {
  input.addEventListener('focus', () => input.parentElement.classList.add('focused'));
  input.addEventListener('blur',  () => input.parentElement.classList.remove('focused'));
  input.addEventListener('change', () => {
    input.parentElement.classList.toggle('filled', !!input.value);
  });
});

// ===========================
// Page Load
// ===========================
window.addEventListener('load', () => {
  document.body.classList.add('loaded');
});