/**
 * Kwara State Office of the Head of Service CBT Testing Engine
 */

// Application State
const state = {
  candidate: null,
  candidateId: null,
  questions: [],
  currentIndex: 0,
  answers: {}, // { "1": "A", "2": "C" }
  flagged: new Set(), // Set of question numbers (1-50)
  durationSeconds: 20 * 60,
  secondsRemaining: 20 * 60,
  timerInterval: null,
  isSubmitted: false,
  adminToken: sessionStorage.getItem('kws_admin_token') || null,
  adminSubmissions: [],
  examStatus: 'open'
};

// DOM Elements
const views = {
  entry: document.getElementById('view-entry'),
  exam: document.getElementById('view-exam'),
  result: document.getElementById('view-result'),
  admin: document.getElementById('view-admin')
};

// Custom Alert Modal System with Optional Action Buttons
function showAlertModal(title, message, type = 'warning', actionConfig = null) {
  const modal = document.getElementById('custom-alert-modal');
  const titleEl = document.getElementById('alert-modal-title');
  const msgEl = document.getElementById('alert-modal-msg');
  const iconEl = document.getElementById('alert-modal-icon');
  const okBtn = document.getElementById('alert-modal-ok-btn');
  const viewResBtn = document.getElementById('alert-modal-view-res-btn');

  if (!modal) return;

  titleEl.textContent = title;
  msgEl.textContent = message;

  if (type === 'error') {
    iconEl.textContent = '⛔';
    iconEl.style.background = '#fee2e2';
    iconEl.style.color = '#dc2626';
  } else if (type === 'timer') {
    iconEl.textContent = '⏱️';
    iconEl.style.background = '#fffbeb';
    iconEl.style.color = '#d97706';
  } else if (type === 'info') {
    iconEl.textContent = 'ℹ️';
    iconEl.style.background = '#e0f2fe';
    iconEl.style.color = '#0284c7';
  } else if (type === 'success') {
    iconEl.textContent = '✅';
    iconEl.style.background = '#d1fae5';
    iconEl.style.color = '#059669';
  } else {
    iconEl.textContent = '⚠️';
    iconEl.style.background = '#fef3c7';
    iconEl.style.color = '#b45309';
  }

  if (viewResBtn) {
    if (actionConfig && actionConfig.showResultBtn && actionConfig.psn) {
      viewResBtn.style.display = 'block';
      viewResBtn.onclick = () => {
        closeAlertModal();
        retrieveResultByPsn(actionConfig.psn);
      };
    } else {
      viewResBtn.style.display = 'none';
      viewResBtn.onclick = null;
    }
  }

  modal.classList.add('active');
  if (okBtn) okBtn.focus();
}

function closeAlertModal() {
  const modal = document.getElementById('custom-alert-modal');
  if (modal) modal.classList.remove('active');
}

// Exit Exam Confirmation Modal
function openExitModal() {
  const modal = document.getElementById('exit-exam-modal');
  if (modal) modal.classList.add('active');
}

function closeExitModal() {
  const modal = document.getElementById('exit-exam-modal');
  if (modal) modal.classList.remove('active');
}

// Close CBT Exam Session
function closeExamSession() {
  if (state.timerInterval) clearInterval(state.timerInterval);
  state.candidate = null;
  state.candidateId = null;
  state.questions = [];
  state.answers = {};
  state.flagged.clear();
  state.isSubmitted = false;

  const entryForm = document.getElementById('form-entry');
  if (entryForm) entryForm.reset();
  const retrieveForm = document.getElementById('form-retrieve-result');
  if (retrieveForm) retrieveForm.reset();

  window.history.pushState({}, '', '/');
  showView('entry');
  switchEntryTab('start');
  showAlertModal(
    'CBT Session Closed',
    'Your CBT examination session has been closed successfully. You can now safely close your browser tab or proceed.',
    'success'
  );
}

// Return to Portal Home from Result View
function returnToPortalHome() {
  window.history.pushState({}, '', '/');
  showView('entry');
  switchEntryTab('retrieve');
}

// Switch Views
function showView(viewName) {
  Object.keys(views).forEach(v => {
    if (views[v]) {
      views[v].classList.toggle('active', v === viewName);
    }
  });

  const navExam = document.getElementById('nav-exam-btn');
  if (navExam) {
    navExam.classList.toggle('active', viewName !== 'admin');
  }
}

// Format Seconds to MM:SS
function formatTime(seconds) {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
}

// -------------------------------------------------------------
// 0. Initialize Exam Status & Routing (/admin support)
// -------------------------------------------------------------
async function initPortalStatus() {
  try {
    const res = await fetch('/api/info');
    if (res.ok) {
      const data = await res.json();
      state.examStatus = data.exam_status || 'open';
      applyExamStatusToUI(state.examStatus);
    }
  } catch (e) {
    console.warn('Could not fetch portal status:', e);
  }
}

function applyExamStatusToUI(status) {
  const closedBanner = document.getElementById('exam-closed-banner');
  const startBtn = document.getElementById('btn-start-exam');
  const startBtnText = document.getElementById('btn-start-exam-text');

  if (status === 'closed') {
    if (closedBanner) closedBanner.style.display = 'block';
    if (startBtn) {
      startBtn.disabled = true;
      startBtn.style.opacity = '0.6';
      startBtn.style.cursor = 'not-allowed';
    }
    if (startBtnText) startBtnText.textContent = '🔒 Examination is Currently Closed';
  } else {
    if (closedBanner) closedBanner.style.display = 'none';
    if (startBtn) {
      startBtn.disabled = false;
      startBtn.style.opacity = '1';
      startBtn.style.cursor = 'pointer';
    }
    if (startBtnText) startBtnText.textContent = '🚀 Login & Commence CBT Examination (20 Mins)';
  }
}

function checkRoute() {
  const path = window.location.pathname.toLowerCase();
  const hash = window.location.hash.toLowerCase();

  if (path === '/admin' || hash === '#admin') {
    if (state.adminToken) {
      showView('admin');
      loadAdminSubmissions();
    } else {
      showView('entry');
      openAdminLoginModal();
    }
  }
}

function navigateToExam() {
  if (state.isSubmitted) {
    showView('result');
  } else if (state.candidate && state.questions && state.questions.length > 0) {
    showView('exam');
  } else {
    if (window.location.pathname.toLowerCase() === '/admin') {
      window.history.pushState({}, '', '/');
    }
    showView('entry');
  }
}

// -------------------------------------------------------------
// 1. Candidate Entry Tabs: Take Exam vs Retrieve Result
// -------------------------------------------------------------
function switchEntryTab(tab) {
  const btnStart = document.getElementById('tab-btn-start');
  const btnRetrieve = document.getElementById('tab-btn-retrieve');
  const contentStart = document.getElementById('tab-content-start');
  const contentRetrieve = document.getElementById('tab-content-retrieve');
  const title = document.getElementById('entry-card-title');
  const subtitle = document.getElementById('entry-card-subtitle');

  if (tab === 'retrieve') {
    if (btnStart) btnStart.classList.remove('active');
    if (btnRetrieve) btnRetrieve.classList.add('active');
    if (contentStart) contentStart.style.display = 'none';
    if (contentRetrieve) contentRetrieve.style.display = 'block';
    if (title) title.textContent = 'Retrieve Official Result Slip';
    if (subtitle) subtitle.textContent = 'Enter your Public Service Number (PSN) to view, verify, and reprint your official result slip anytime';
    const inputPsn = document.getElementById('input-retrieve-psn');
    if (inputPsn) inputPsn.focus();
  } else {
    if (btnStart) btnStart.classList.add('active');
    if (btnRetrieve) btnRetrieve.classList.remove('active');
    if (contentStart) contentStart.style.display = 'block';
    if (contentRetrieve) contentRetrieve.style.display = 'none';
    if (title) title.textContent = 'Officer CBT Examination Login';
    if (subtitle) subtitle.textContent = 'Please enter your official verification details below to log in and begin your evaluation test';
  }
}

// Result Retrieval by PSN
async function retrieveResultByPsn(psn) {
  const btn = document.getElementById('btn-retrieve-result');
  const originalText = btn ? btn.innerHTML : '';
  if (btn) {
    btn.disabled = true;
    btn.innerHTML = `<span>⏳ Searching Examination Records...</span>`;
  }

  try {
    const res = await fetch(`/api/result/${encodeURIComponent(psn)}`);
    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.detail || `No examination result found for PSN: ${psn}`);
    }

    renderResultSlip(data);
    showView('result');
    closeAlertModal();
  } catch (err) {
    showAlertModal('Result Not Found', err.message, 'error');
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.innerHTML = originalText;
    }
  }
}

// Retrieve Result Form Event Listener
const retrieveForm = document.getElementById('form-retrieve-result');
if (retrieveForm) {
  retrieveForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const psn = document.getElementById('input-retrieve-psn').value.trim();
    if (!psn) {
      showAlertModal('PSN Required', 'Please enter your Public Service Number (PSN) to retrieve your result slip.', 'warning');
      return;
    }
    await retrieveResultByPsn(psn);
  });
}

// Candidate Entry & Exam Initialization
const entryForm = document.getElementById('form-entry');
if (entryForm) {
  entryForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    if (state.examStatus === 'closed') {
      showAlertModal(
        'Examination Closed',
        'The CBT Examination is currently closed by the Administrator. Candidate registration and test attempts are suspended.',
        'error'
      );
      return;
    }

    const name = document.getElementById('input-name').value.trim();
    const psn = document.getElementById('input-psn').value.trim();
    const email = document.getElementById('input-email').value.trim();
    const gradeLevel = document.getElementById('select-grade').value;
    const mda = document.getElementById('input-mda').value.trim() || 'Kwara State Civil Service';

    if (!name || !psn || !email) {
      showAlertModal(
        'Required Information Missing',
        'Please enter your Full Name, PSN (Public Service Number), and Email Address to commence.',
        'warning'
      );
      return;
    }

    const btn = document.getElementById('btn-start-exam');
    const originalText = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = `<span>⏳ Preparing Exam Questions...</span>`;

    try {
      const response = await fetch('/api/start-exam', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, psn, email, grade_level: gradeLevel, mda })
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || 'Failed to start examination.');
      }

      state.candidate = data.candidate;
      state.candidateId = data.candidate_id;
      state.questions = data.questions;
      state.currentIndex = 0;
      state.answers = {};
      state.flagged.clear();
      state.isSubmitted = false;
      state.durationSeconds = (data.duration_minutes || 20) * 60;
      state.secondsRemaining = state.durationSeconds;

      // Update candidate details in exam header
      document.getElementById('exam-candidate-name').textContent = state.candidate.name;
      document.getElementById('exam-candidate-psn').textContent = `PSN: ${state.candidate.psn} | ${state.candidate.grade_level}`;
      document.getElementById('exam-candidate-avatar').textContent = state.candidate.name.charAt(0).toUpperCase();

      buildPalette();
      renderQuestion(0);
      startTimer();
      showView('exam');
    } catch (err) {
      state.candidate = null;
      state.candidateId = null;
      state.questions = [];
      state.answers = {};
      state.flagged.clear();

      const qText = document.getElementById('q-text');
      const optCont = document.getElementById('options-container');
      const palNum = document.getElementById('palette-numbers');
      if (qText) qText.textContent = '';
      if (optCont) optCont.innerHTML = '';
      if (palNum) palNum.innerHTML = '';

      showView('entry');

      const isAlreadyTaken = err.message.toLowerCase().includes('already taken') || err.message.toLowerCase().includes('cannot take');
      showAlertModal(
        'Examination Closed',
        err.message,
        'error',
        isAlreadyTaken ? { showResultBtn: true, psn: psn } : null
      );
    } finally {
      btn.disabled = false;
      btn.innerHTML = originalText;
    }
  });
}

// -------------------------------------------------------------
// 2. CBT Testing Engine & Live Countdown
// -------------------------------------------------------------
function startTimer() {
  if (state.timerInterval) clearInterval(state.timerInterval);

  const timerEl = document.getElementById('exam-timer');
  const timerText = document.getElementById('timer-text');
  const sidebarTimerBox = document.getElementById('sidebar-timer-box');
  const sidebarTimerText = document.getElementById('sidebar-timer-text');

  function updateDisplay() {
    const formatted = formatTime(state.secondsRemaining);
    if (timerText) timerText.textContent = formatted;
    if (sidebarTimerText) sidebarTimerText.textContent = formatted;

    if (state.secondsRemaining <= 120) {
      if (timerEl) timerEl.className = 'timer-box danger';
      if (sidebarTimerBox) sidebarTimerBox.className = 'sidebar-timer-badge danger';
    } else if (state.secondsRemaining <= 300) {
      if (timerEl) timerEl.className = 'timer-box warning';
      if (sidebarTimerBox) sidebarTimerBox.className = 'sidebar-timer-badge warning';
    } else {
      if (timerEl) timerEl.className = 'timer-box';
      if (sidebarTimerBox) sidebarTimerBox.className = 'sidebar-timer-badge';
    }
  }

  updateDisplay();

  state.timerInterval = setInterval(() => {
    state.secondsRemaining--;
    if (state.secondsRemaining <= 0) {
      clearInterval(state.timerInterval);
      state.secondsRemaining = 0;
      updateDisplay();
      showAlertModal(
        'Time Expired',
        'Your 20-minute allotted time has concluded. Your test is being automatically submitted and graded now.',
        'timer'
      );
      submitExam(true);
    } else {
      updateDisplay();
    }
  }, 1000);
}

function buildPalette() {
  const container = document.getElementById('palette-numbers');
  container.innerHTML = '';

  state.questions.forEach((q, idx) => {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'pal-btn';
    btn.id = `pal-btn-${idx}`;
    btn.textContent = q.number;
    btn.onclick = () => jumpToQuestion(idx);
    container.appendChild(btn);
  });
  updatePaletteState();
}

function updatePaletteState() {
  state.questions.forEach((q, idx) => {
    const btn = document.getElementById(`pal-btn-${idx}`);
    if (!btn) return;

    const qNumStr = String(q.number);
    const isAnswered = Boolean(state.answers[qNumStr]);
    const isFlagged = state.flagged.has(q.number);
    const isCurrent = idx === state.currentIndex;

    btn.className = 'pal-btn';
    if (isAnswered) btn.classList.add('answered');
    if (isFlagged) btn.classList.add('flagged');
    if (isCurrent) btn.classList.add('current');
  });

  const answeredCount = Object.keys(state.answers).length;
  const flaggedCount = state.flagged.size;
  const unansweredCount = state.questions.length - answeredCount;

  document.getElementById('count-answered').textContent = answeredCount;
  document.getElementById('count-unanswered').textContent = unansweredCount;
  document.getElementById('count-flagged').textContent = flaggedCount;
}

function renderQuestion(index) {
  if (index < 0 || index >= state.questions.length) return;
  state.currentIndex = index;

  const q = state.questions[index];
  const qNumStr = String(q.number);

  document.getElementById('q-current-num').textContent = `Question ${q.number} of ${state.questions.length}`;
  document.getElementById('q-grade-tag').textContent = state.candidate.grade_level;
  document.getElementById('q-text').textContent = q.question;

  const optContainer = document.getElementById('options-container');
  optContainer.innerHTML = '';

  const selectedOpt = state.answers[qNumStr];

  ['A', 'B', 'C', 'D'].forEach(letter => {
    const text = q.options[letter];
    if (!text) return;

    const item = document.createElement('div');
    item.className = 'option-item' + (selectedOpt === letter ? ' selected' : '');
    item.onclick = () => selectOption(letter);

    item.innerHTML = `
      <div class="option-key">${letter}</div>
      <div class="option-text">${text}</div>
    `;
    optContainer.appendChild(item);
  });

  document.getElementById('btn-prev').disabled = (index === 0);
  document.getElementById('btn-next').disabled = (index === state.questions.length - 1);

  const flagBtn = document.getElementById('btn-flag');
  if (state.flagged.has(q.number)) {
    flagBtn.classList.add('flagged');
    flagBtn.innerHTML = `<span>🚩 Flagged</span>`;
  } else {
    flagBtn.classList.remove('flagged');
    flagBtn.innerHTML = `<span>🏳️ Flag for Review</span>`;
  }

  updatePaletteState();
}

function selectOption(letter) {
  const currentQ = state.questions[state.currentIndex];
  const qNumStr = String(currentQ.number);
  state.answers[qNumStr] = letter;
  renderQuestion(state.currentIndex);
}

function clearCurrentAnswer() {
  const currentQ = state.questions[state.currentIndex];
  const qNumStr = String(currentQ.number);
  delete state.answers[qNumStr];
  renderQuestion(state.currentIndex);
}

function toggleCurrentFlag() {
  const currentQ = state.questions[state.currentIndex];
  if (state.flagged.has(currentQ.number)) {
    state.flagged.delete(currentQ.number);
  } else {
    state.flagged.add(currentQ.number);
  }
  renderQuestion(state.currentIndex);
}

function nextQuestion() {
  if (state.currentIndex < state.questions.length - 1) {
    renderQuestion(state.currentIndex + 1);
  }
}

function prevQuestion() {
  if (state.currentIndex > 0) {
    renderQuestion(state.currentIndex - 1);
  }
}

function jumpToQuestion(index) {
  renderQuestion(index);
}

// -------------------------------------------------------------
// 3. Submission & Results Slip
// -------------------------------------------------------------
function openSubmitModal() {
  const answeredCount = Object.keys(state.answers).length;
  const total = state.questions.length;
  const unansweredCount = total - answeredCount;
  const flaggedCount = state.flagged.size;

  document.getElementById('modal-ans-count').textContent = answeredCount;
  document.getElementById('modal-unans-count').textContent = unansweredCount;
  document.getElementById('modal-flag-count').textContent = flaggedCount;

  document.getElementById('submit-modal').classList.add('active');
}

function closeSubmitModal() {
  document.getElementById('submit-modal').classList.remove('active');
}

async function submitExam(isAuto = false) {
  if (state.isSubmitted) return;
  state.isSubmitted = true;

  if (state.timerInterval) clearInterval(state.timerInterval);
  closeSubmitModal();
  closeExitModal();

  const timeTaken = state.durationSeconds - state.secondsRemaining;

  const payload = {
    candidate_id: state.candidateId,
    name: state.candidate.name,
    psn: state.candidate.psn,
    email: state.candidate.email,
    grade_level: state.candidate.grade_level,
    mda: state.candidate.mda,
    answers: state.answers,
    time_taken_seconds: timeTaken
  };

  try {
    const response = await fetch('/api/submit-exam', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    const result = await response.json();
    if (!response.ok) {
      throw new Error(result.detail || 'Submission failed.');
    }

    renderResultSlip(result);
    showView('result');
  } catch (err) {
    showAlertModal(
      'Submission Error',
      'An error occurred during submission: ' + err.message,
      'error'
    );
  }
}

function renderResultSlip(res) {
  const candidate = res.candidate;
  const score = res.score;

  document.getElementById('res-name').textContent = candidate.name;
  document.getElementById('res-psn').textContent = candidate.psn;
  document.getElementById('res-email').textContent = candidate.email;
  document.getElementById('res-grade').textContent = candidate.grade_level;
  document.getElementById('res-mda').textContent = candidate.mda;
  document.getElementById('res-date').textContent = res.submitted_at;

  const mins = Math.floor(res.time_taken_seconds / 60);
  const secs = res.time_taken_seconds % 60;
  document.getElementById('res-time').textContent = `${mins}m ${secs}s`;

  document.getElementById('res-pct').textContent = `${score.score_percentage}%`;
  document.getElementById('res-marks').textContent = `Total Score: ${score.total_marks} / ${score.max_marks} marks (${score.correct_count} of ${score.total_questions} questions correct)`;

  const remarkEl = document.getElementById('res-remark');
  remarkEl.textContent = score.grade_remark;

  remarkEl.className = 'remark-pill';
  if (score.score_percentage >= 75) {
    remarkEl.classList.add('distinction');
  } else if (score.score_percentage >= 60) {
    remarkEl.classList.add('credit');
  } else if (score.score_percentage >= 50) {
    remarkEl.classList.add('pass');
  } else {
    remarkEl.classList.add('fail');
  }

  const refCode = `KWS-HOS-${res.submission_id.toString().padStart(5, '0')}-${candidate.psn}`;
  document.getElementById('res-ref-code').textContent = `Ref: ${refCode}`;
}

// -------------------------------------------------------------
// 4. Admin Portal & Authentication & Exam Status Toggle
// -------------------------------------------------------------
function openAdminLoginModal() {
  const modal = document.getElementById('admin-login-modal');
  const err = document.getElementById('admin-login-error');
  if (err) err.style.display = 'none';
  if (modal) modal.classList.add('active');
  document.getElementById('admin-user').focus();
}

function closeAdminLoginModal() {
  const modal = document.getElementById('admin-login-modal');
  if (modal) modal.classList.remove('active');
  if (window.location.pathname.toLowerCase() === '/admin') {
    window.history.pushState({}, '', '/');
    showView('entry');
  }
}

const adminLoginForm = document.getElementById('form-admin-login');
if (adminLoginForm) {
  adminLoginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('admin-user').value.trim();
    const password = document.getElementById('admin-pass').value.trim();
    const errEl = document.getElementById('admin-login-error');
    const submitBtn = document.getElementById('btn-admin-submit-login');

    submitBtn.disabled = true;
    submitBtn.innerHTML = `<span>Verifying...</span>`;

    try {
      const res = await fetch('/api/admin/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Invalid administrator username or password.');
      }

      state.adminToken = data.token;
      sessionStorage.setItem('kws_admin_token', data.token);

      closeAdminLoginModal();
      adminLoginForm.reset();
      window.history.pushState({}, '', '/admin');
      showView('admin');
      loadAdminSubmissions();
    } catch (err) {
      if (errEl) {
        errEl.textContent = err.message;
        errEl.style.display = 'block';
      }
    } finally {
      submitBtn.disabled = false;
      submitBtn.innerHTML = `<span>🔑 Sign In</span>`;
    }
  });
}

// Admin Toggle Exam Open / Closed
async function toggleExamStatus() {
  if (!state.adminToken) {
    openAdminLoginModal();
    return;
  }

  const btn = document.getElementById('btn-toggle-status');
  if (btn) btn.disabled = true;

  try {
    const res = await fetch('/api/admin/toggle-exam-status', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${state.adminToken}`
      }
    });

    if (res.status === 401) {
      state.adminToken = null;
      sessionStorage.removeItem('kws_admin_token');
      openAdminLoginModal();
      return;
    }

    const data = await res.json();
    state.examStatus = data.exam_status;
    updateAdminStatusUI(data.exam_status);
    applyExamStatusToUI(data.exam_status);

    showAlertModal(
      'Exam Status Updated',
      data.message,
      data.exam_status === 'open' ? 'success' : 'warning'
    );
  } catch (err) {
    showAlertModal('Error', 'Failed to update exam status: ' + err.message, 'error');
  } finally {
    if (btn) btn.disabled = false;
  }
}

function updateAdminStatusUI(status) {
  const dot = document.getElementById('status-pulse-dot');
  const text = document.getElementById('admin-status-text');
  const btn = document.getElementById('btn-toggle-status');
  const btnText = document.getElementById('btn-toggle-status-text');

  if (status === 'closed') {
    if (dot) dot.className = 'status-pulse-dot closed';
    if (text) {
      text.className = 'status-text-closed';
      text.textContent = '🔴 CLOSED / LOCKED FOR CANDIDATES';
    }
    if (btn) {
      btn.className = 'btn-toggle-exam btn-status-open';
    }
    if (btnText) btnText.textContent = '🔓 Re-Open CBT Examination';
  } else {
    if (dot) dot.className = 'status-pulse-dot';
    if (text) {
      text.className = 'status-text-open';
      text.textContent = '🟢 ACTIVE & OPEN FOR CANDIDATES';
    }
    if (btn) {
      btn.className = 'btn-toggle-exam btn-status-close';
    }
    if (btnText) btnText.textContent = '🔒 Close CBT Examination';
  }
}

async function loadAdminSubmissions() {
  if (!state.adminToken) {
    openAdminLoginModal();
    return;
  }

  try {
    const response = await fetch('/api/admin/submissions', {
      headers: {
        'Authorization': `Bearer ${state.adminToken}`
      }
    });

    if (response.status === 401) {
      state.adminToken = null;
      sessionStorage.removeItem('kws_admin_token');
      openAdminLoginModal();
      return;
    }

    const data = await response.json();
    state.adminSubmissions = data.submissions || [];
    state.examStatus = data.exam_status || 'open';

    updateAdminStatusUI(state.examStatus);
    applyExamStatusToUI(state.examStatus);

    // KPI Cards
    document.getElementById('kpi-total').textContent = data.summary.total_submissions;
    document.getElementById('kpi-avg').textContent = `${data.summary.average_score}%`;
    document.getElementById('kpi-rate').textContent = `${data.summary.pass_rate}%`;
    document.getElementById('kpi-pass').textContent = `${data.summary.passed_count} Passed`;

    // Update download URLs with admin token
    const btnExcel = document.getElementById('btn-download-excel');
    const btnCsv = document.getElementById('btn-download-csv');
    if (btnExcel) btnExcel.href = `/api/results/excel?token=${encodeURIComponent(state.adminToken)}`;
    if (btnCsv) btnCsv.href = `/api/results/csv?token=${encodeURIComponent(state.adminToken)}`;

    renderAdminTable();
  } catch (err) {
    console.error('Failed to load admin submissions:', err);
  }
}

function renderAdminTable() {
  const tbody = document.getElementById('admin-table-body');
  const search = (document.getElementById('admin-search').value || '').toLowerCase();
  const gradeFilter = document.getElementById('admin-grade-filter').value;

  const filtered = state.adminSubmissions.filter(s => {
    const matchSearch = s.candidate_name.toLowerCase().includes(search) ||
                        s.psn.toLowerCase().includes(search) ||
                        s.email.toLowerCase().includes(search) ||
                        s.mda.toLowerCase().includes(search);
    const matchGrade = (gradeFilter === 'ALL' || s.grade_level === gradeFilter);
    return matchSearch && matchGrade;
  });

  if (filtered.length === 0) {
    tbody.innerHTML = `<tr><td colspan="10" style="text-align:center; padding: 24px; color:#64748b;">No candidate submissions found.</td></tr>`;
    return;
  }

  tbody.innerHTML = filtered.map((s, idx) => {
    let remarkBadge = 'background: #fef3c7; color: #92400e;';
    if (s.score_percentage >= 75) remarkBadge = 'background: #d1fae5; color: #065f46;';
    else if (s.score_percentage >= 60) remarkBadge = 'background: #e0f2fe; color: #0369a1;';
    else if (s.score_percentage < 50) remarkBadge = 'background: #fee2e2; color: #991b1b;';

    return `
      <tr>
        <td style="font-weight:700; text-align:center;">${idx + 1}</td>
        <td><strong>${s.candidate_name}</strong></td>
        <td><code>${s.psn}</code></td>
        <td>${s.email}</td>
        <td><span class="grade-tag">${s.grade_level}</span></td>
        <td>${s.mda}</td>
        <td style="text-align:center;"><strong>${s.correct_count * 2} / 100</strong> (${s.correct_count}/50)</td>
        <td style="text-align:center; font-weight:800; font-size:1.05rem; color:#004d40;">${s.score_percentage}%</td>
        <td><span style="display:inline-block; padding:3px 10px; border-radius:12px; font-size:0.8rem; font-weight:700; ${remarkBadge}">${s.grade_remark}</span></td>
        <td style="font-size:0.8rem; color:#64748b;">${s.submitted_at}</td>
      </tr>
    `;
  }).join('');
}

// -------------------------------------------------------------
// Event Listeners
// -------------------------------------------------------------
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    closeAlertModal();
    closeSubmitModal();
    closeExitModal();
    closeAdminLoginModal();
    return;
  }

  if (!views.exam.classList.contains('active')) return;

  const key = e.key.toUpperCase();
  if (['A', 'B', 'C', 'D'].includes(key)) {
    selectOption(key);
  } else if (key === 'ARROWLEFT' || key === 'P') {
    prevQuestion();
  } else if (key === 'ARROWRIGHT' || key === 'N') {
    nextQuestion();
  } else if (key === 'F') {
    toggleCurrentFlag();
  }
});

// Admin Logout
const adminLogoutBtn = document.getElementById('btn-admin-logout');
if (adminLogoutBtn) {
  adminLogoutBtn.addEventListener('click', async () => {
    if (state.adminToken) {
      try {
        await fetch('/api/admin/logout', {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${state.adminToken}` }
        });
      } catch (e) {}
    }
    state.adminToken = null;
    sessionStorage.removeItem('kws_admin_token');
    window.history.pushState({}, '', '/');
    showView('entry');
    switchEntryTab('start');
  });
}

// Admin Filter Inputs
document.getElementById('admin-search').addEventListener('input', renderAdminTable);
document.getElementById('admin-grade-filter').addEventListener('change', renderAdminTable);

// Result Actions
document.getElementById('btn-print-slip').addEventListener('click', () => {
  window.print();
});

window.addEventListener('popstate', checkRoute);

// Run initial status & route check on load
initPortalStatus();
checkRoute();
