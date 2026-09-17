/**
 * Kwara State Civil Service Commission - 2026 Promotion Evaluation CBT Examination
 */

// Application State
const state = {
  candidate: null,
  candidateId: null,
  registeredCandidate: null,
  tempPassportBase64: null,
  webcamStream: null,
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
  adminTokensSummary: null,
  examStatus: 'open'
};

// DOM Elements
const views = {
  entry: document.getElementById('view-entry'),
  photocard: document.getElementById('view-photocard'),
  exam: document.getElementById('view-exam'),
  result: document.getElementById('view-result'),
  admin: document.getElementById('view-admin')
};

// Custom Alert Modal System
function showAlertModal(title, message, type = 'warning') {
  const modal = document.getElementById('custom-alert-modal');
  const titleEl = document.getElementById('alert-modal-title');
  const msgEl = document.getElementById('alert-modal-msg');
  const iconEl = document.getElementById('alert-modal-icon');
  const okBtn = document.getElementById('alert-modal-ok-btn');

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
  if (!modal) return;
  const total = state.questions.length;
  const answeredCount = Object.keys(state.answers).length;
  const exitSubmitBtn = document.getElementById('btn-exit-submit-now');
  const exitDesc = document.getElementById('exit-modal-desc');

  if (exitSubmitBtn) {
    if (answeredCount < total) {
      exitSubmitBtn.style.display = 'none';
      if (exitDesc) {
        const remaining = total - answeredCount;
        exitDesc.innerHTML = `You have answered <strong>${answeredCount} of ${total}</strong> questions (<span style="color:#b45309; font-weight:700;">${remaining} unanswered remaining</span>).<br><br>Under Kwara State Civil Service Commission regulations, manual early submission is disabled until all questions are answered.<br><br>You may return to continue your test. When the 20-minute countdown concludes, all your answers will automatically be submitted.`;
      }
    } else {
      exitSubmitBtn.style.display = 'block';
      if (exitDesc) {
        exitDesc.innerHTML = `You have answered all <strong>${total} questions</strong>. Are you sure you want to finish and submit your CBT examination now?`;
      }
    }
  }
  modal.classList.add('active');
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

  window.history.pushState({}, '', '/');
  showView('entry');
  switchEntryTab('start');
  showAlertModal(
    'CBT Session Closed',
    'Your CBT examination session has been closed successfully. You can now safely close your browser tab or proceed.',
    'success'
  );
}

// Return to Portal Home from Acknowledgement View
function returnToPortalHome() {
  window.history.pushState({}, '', '/');
  showView('entry');
  switchEntryTab('start');
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
// 1. Candidate Entry Navigation: Registration vs Exam
// -------------------------------------------------------------
function switchEntryTab(tab) {
  const targetTab = (tab === 'start') ? 'start' : 'register';
  const btnRegister = document.getElementById('tab-btn-register');
  const btnStart = document.getElementById('tab-btn-start');

  const contentRegister = document.getElementById('tab-content-register');
  const contentStart = document.getElementById('tab-content-start');

  const title = document.getElementById('entry-card-title');
  const subtitle = document.getElementById('entry-card-subtitle');

  // Reset active classes on tabs
  if (btnRegister) btnRegister.classList.toggle('active', targetTab === 'register');
  if (btnStart) btnStart.classList.toggle('active', targetTab === 'start');

  // Switch content visibility
  if (contentRegister) contentRegister.style.display = (targetTab === 'register') ? 'block' : 'none';
  if (contentStart) contentStart.style.display = (targetTab === 'start') ? 'block' : 'none';

  if (targetTab === 'register') {
    if (title) title.textContent = 'Candidate Verification & Photocard';
    if (subtitle) subtitle.textContent = 'Verify your promotion candidate record, upload passport photo, and generate your official CBT photocard';
    const inputRegPsn = document.getElementById('reg-input-psn');
    if (inputRegPsn) inputRegPsn.focus();
  } else {
    if (title) title.textContent = 'Take CBT Examination';
    if (subtitle) subtitle.textContent = 'Enter your Public Service Number (PSN) and 5-digit Exam Scratch Card Token issued in the examination hall';
    const inputTokenPsn = document.getElementById('token-exam-psn');
    if (inputTokenPsn) inputTokenPsn.focus();
  }
}

// -------------------------------------------------------------
// 1B. Candidate Clearance & Photocard Generation (Code 1)
// -------------------------------------------------------------
function resetCandidateLookup() {
  const lookupBox = document.getElementById('reg-lookup-box');
  const profileBox = document.getElementById('reg-profile-box');
  if (lookupBox) lookupBox.style.display = 'block';
  if (profileBox) profileBox.style.display = 'none';
  state.registeredCandidate = null;
  state.tempPassportBase64 = null;
}

// Lookup Form Event Listener
const lookupForm = document.getElementById('form-candidate-lookup');
if (lookupForm) {
  lookupForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const psn = document.getElementById('reg-input-psn').value.trim();
    const code1 = document.getElementById('reg-input-code1').value.trim().toUpperCase();

    if (!psn || !code1) {
      showAlertModal('Information Required', 'Please provide both your PSN and your Registration Clearance Code (Code 1).', 'warning');
      return;
    }

    const btn = document.getElementById('btn-lookup-candidate');
    const originalText = btn ? btn.innerHTML : '';
    if (btn) {
      btn.disabled = true;
      btn.innerHTML = `<span>⏳ Verifying Clearance Records...</span>`;
    }

    try {
      const res = await fetch('/api/candidate/lookup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ psn, code_1: code1 })
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Candidate lookup failed. Please check your credentials.');
      }

      const cand = data.candidate;
      state.registeredCandidate = cand;

      // Populate form
      document.getElementById('reg-orig-name-lbl').textContent = cand.name;
      document.getElementById('reg-amended-name').value = cand.amended_name || cand.name;
      document.getElementById('reg-disp-psn').value = cand.psn;
      document.getElementById('reg-disp-mda').value = cand.mda;
      document.getElementById('reg-disp-rank').value = cand.proposed_rank || 'Civil Service Cadre';
      document.getElementById('reg-disp-gl').value = `${cand.proposed_gl || ''} (${cand.group_category || ''})`;
      document.getElementById('reg-disp-paper').value = `${cand.exam_code} - ${cand.group_category}`;

      document.getElementById('reg-disp-date').textContent = cand.exam_date || 'Tuesday, 29th September 2026';
      document.getElementById('reg-disp-batch').textContent = cand.batch_session || 'Batch 1';
      document.getElementById('reg-disp-accred').textContent = cand.accreditation_time || '09:00 AM';
      document.getElementById('reg-disp-examtime').textContent = cand.batch_time || '10:00 AM';

      document.getElementById('reg-input-phone').value = cand.phone || '';
      document.getElementById('reg-input-email').value = cand.email || '';

      const previewImg = document.getElementById('reg-passport-preview');
      if (cand.passport_photo) {
        previewImg.src = cand.passport_photo;
        state.tempPassportBase64 = cand.passport_photo;
      } else {
        previewImg.src = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='140' height='160' viewBox='0 0 140 160'><rect width='140' height='160' fill='%23f1f5f9'/><circle cx='70' cy='55' r='30' fill='%23cbd5e1'/><path d='M20 145 C20 105 50 95 70 95 C90 95 120 105 120 145 Z' fill='%23cbd5e1'/><text x='70' y='155' text-anchor='middle' font-size='10' fill='%2394a3b8' font-family='sans-serif'>No Photo</text></svg>";
        state.tempPassportBase64 = null;
      }

      const directBtn = document.getElementById('btn-direct-photocard');
      if (directBtn) {
        directBtn.style.display = (cand.registration_status === 'registered' || cand.registration_status === 'tested' || cand.passport_photo) ? 'block' : 'none';
      }

      document.getElementById('reg-lookup-box').style.display = 'none';
      document.getElementById('reg-profile-box').style.display = 'block';

    } catch (err) {
      showAlertModal('Verification Unsuccessful', err.message, 'error');
    } finally {
      if (btn) {
        btn.disabled = false;
        btn.innerHTML = originalText;
      }
    }
  });
}

// Handle Passport File Upload
function handlePassportFileSelect(input) {
  if (!input.files || !input.files[0]) return;
  const file = input.files[0];
  if (!file.type.startsWith('image/')) {
    showAlertModal('Invalid File', 'Please select an image file (PNG, JPG, JPEG).', 'warning');
    return;
  }

  const reader = new FileReader();
  reader.onload = (e) => {
    const img = new Image();
    img.onload = () => {
      // Resize to standard passport dimensions (280x320)
      const canvas = document.createElement('canvas');
      canvas.width = 280;
      canvas.height = 320;
      const ctx = canvas.getContext('2d');

      // Crop center to maintain aspect ratio
      const scale = Math.max(canvas.width / img.width, canvas.height / img.height);
      const w = img.width * scale;
      const h = img.height * scale;
      const x = (canvas.width - w) / 2;
      const y = (canvas.height - h) / 2;

      ctx.drawImage(img, x, y, w, h);
      const dataUri = canvas.toDataURL('image/jpeg', 0.85);
      state.tempPassportBase64 = dataUri;
      const preview = document.getElementById('reg-passport-preview');
      if (preview) preview.src = dataUri;
    };
    img.src = e.target.result;
  };
  reader.readAsDataURL(file);
}

// Live Webcam Snapshot Handling
async function openWebcamModal() {
  const modal = document.getElementById('webcam-modal');
  const video = document.getElementById('webcam-video');
  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: { width: { ideal: 640 }, height: { ideal: 480 }, facingMode: 'user' }
    });
    state.webcamStream = stream;
    if (video) {
      video.srcObject = stream;
      video.play();
    }
    if (modal) modal.classList.add('active');
  } catch (err) {
    showAlertModal(
      'Webcam Unavailable',
      'Unable to access camera (' + err.message + '). Please use the "Upload Photo File" button to upload your passport photo directly.',
      'warning'
    );
  }
}

function captureWebcamPhoto() {
  const video = document.getElementById('webcam-video');
  const canvas = document.getElementById('webcam-canvas');
  if (!video || !canvas) return;

  const ctx = canvas.getContext('2d');
  canvas.width = 280;
  canvas.height = 320;

  // Mirror effect compensation
  ctx.translate(canvas.width, 0);
  ctx.scale(-1, 1);

  const vWidth = video.videoWidth || 640;
  const vHeight = video.videoHeight || 480;
  const scale = Math.max(canvas.width / vWidth, canvas.height / vHeight);
  const w = vWidth * scale;
  const h = vHeight * scale;
  const x = (canvas.width - w) / 2;
  const y = (canvas.height - h) / 2;

  ctx.drawImage(video, x, y, w, h);
  const dataUri = canvas.toDataURL('image/jpeg', 0.85);
  state.tempPassportBase64 = dataUri;

  const preview = document.getElementById('reg-passport-preview');
  if (preview) preview.src = dataUri;

  closeWebcamModal();
}

function closeWebcamModal() {
  if (state.webcamStream) {
    state.webcamStream.getTracks().forEach(track => track.stop());
    state.webcamStream = null;
  }
  const modal = document.getElementById('webcam-modal');
  if (modal) modal.classList.remove('active');
}

// Save Registration and View Photocard
const completeRegForm = document.getElementById('form-complete-reg');
if (completeRegForm) {
  completeRegForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (!state.registeredCandidate) {
      showAlertModal('Session Expired', 'Please look up your PSN again.', 'warning');
      return;
    }

    if (!state.tempPassportBase64) {
      showAlertModal(
        'Passport Photo Required',
        'Please upload or take a live webcam snapshot of your passport photograph before proceeding.',
        'warning'
      );
      return;
    }

    const amendedName = document.getElementById('reg-amended-name').value.trim();
    const phone = document.getElementById('reg-input-phone').value.trim();
    const email = document.getElementById('reg-input-email').value.trim();

    const btn = document.getElementById('btn-save-photocard');
    const originalText = btn ? btn.innerHTML : '';
    if (btn) {
      btn.disabled = true;
      btn.innerHTML = `<span>💾 Generating Official Photocard...</span>`;
    }

    try {
      const res = await fetch('/api/candidate/complete-registration', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          psn: state.registeredCandidate.psn,
          code_1: state.registeredCandidate.code_1,
          amended_name: amendedName,
          phone: phone,
          email: email,
          passport_photo: state.tempPassportBase64
        })
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Failed to complete registration.');
      }

      state.registeredCandidate = data.candidate;
      renderPhotocard(data.candidate);
      openInstructionsModal();

    } catch (err) {
      showAlertModal('Registration Error', err.message, 'error');
    } finally {
      if (btn) {
        btn.disabled = false;
        btn.innerHTML = originalText;
      }
    }
  });
}

function openInstructionsModal() {
  const modal = document.getElementById('photocard-instructions-modal');
  const chk = document.getElementById('chk-acknowledge-rules');
  const btn = document.getElementById('btn-ack-rules');
  if (chk) chk.checked = false;
  if (btn) {
    btn.disabled = true;
    btn.style.opacity = '0.5';
    btn.style.cursor = 'not-allowed';
  }
  if (modal) modal.classList.add('active');
}

function toggleAckButton() {
  const chk = document.getElementById('chk-acknowledge-rules');
  const btn = document.getElementById('btn-ack-rules');
  if (!chk || !btn) return;
  if (chk.checked) {
    btn.disabled = false;
    btn.style.opacity = '1';
    btn.style.cursor = 'pointer';
  } else {
    btn.disabled = true;
    btn.style.opacity = '0.5';
    btn.style.cursor = 'not-allowed';
  }
}

function closeInstructionsModalAndShowPhotocard() {
  const modal = document.getElementById('photocard-instructions-modal');
  if (modal) modal.classList.remove('active');
  showView('photocard');
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function viewDirectPhotocard() {
  if (state.registeredCandidate) {
    renderPhotocard(state.registeredCandidate);
    openInstructionsModal();
  }
}

function renderPhotocard(c) {
  const target = document.getElementById('photocard-render-target');
  if (!target) return;

  const displayName = c.amended_name || c.name;
  const photoSrc = c.passport_photo || "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='140' height='160' viewBox='0 0 140 160'><rect width='140' height='160' fill='%23f1f5f9'/><circle cx='70' cy='55' r='30' fill='%23cbd5e1'/><path d='M20 145 C20 105 50 95 70 95 C90 95 120 105 120 145 Z' fill='%23cbd5e1'/><text x='70' y='155' text-anchor='middle' font-size='10' fill='%2394a3b8' font-family='sans-serif'>No Photo</text></svg>";

  target.innerHTML = `
    <div class="photocard-meta-grid">
      <div class="passport-box">
        <img src="${photoSrc}" alt="Candidate Passport Photo">
      </div>
      <div>
        <table class="candidate-info-table">
          <tr>
            <th style="padding: 3px 6px;">Candidate Name:</th>
            <td style="padding: 3px 6px;"><strong style="font-size: 1rem; color: #004d40;">${displayName}</strong></td>
          </tr>
          <tr>
            <th style="padding: 3px 6px;">Public Service No (PSN):</th>
            <td style="padding: 3px 6px;"><code style="font-size: 0.95rem; font-weight: 800; color: #0f172a;">${c.psn}</code></td>
          </tr>
          <tr>
            <th style="padding: 3px 6px;">Ministry / MDA:</th>
            <td style="padding: 3px 6px;">${c.mda}</td>
          </tr>
          <tr>
            <th style="padding: 3px 6px;">Present / Proposed Rank:</th>
            <td style="padding: 3px 6px;">${c.proposed_rank || 'Civil Service Cadre'}</td>
          </tr>
          <tr>
            <th style="padding: 3px 6px;">Proposed Grade Level:</th>
            <td style="padding: 3px 6px;"><span class="badge-cadre" style="padding: 2px 6px; font-size: 0.78rem;">${c.proposed_gl || ''} (${c.group_category || ''})</span></td>
          </tr>
          <tr>
            <th style="padding: 3px 6px;">Examination Subject:</th>
            <td style="padding: 3px 6px;"><strong style="color: #0369a1;">${c.exam_code}</strong> (${c.group_category || ''})</td>
          </tr>
          <tr>
            <th style="padding: 3px 6px;">Registration Code (Code 1):</th>
            <td style="padding: 3px 6px;"><span class="badge-code1" style="padding: 2px 6px; font-size: 0.8rem;">${c.code_1}</span></td>
          </tr>
        </table>
      </div>
    </div>

    <!-- Examination Timetable Allocation -->
    <div class="schedule-banner-box" style="padding: 8px 12px; margin-bottom: 10px;">
      <h4 style="font-size: 0.84rem; margin-bottom: 4px;">📅 Official Examination Schedule Allocation</h4>
      <div class="schedule-grid" style="gap: 6px;">
        <div class="schedule-item">
          Examination Date:
          <span style="font-size: 0.84rem;">${c.exam_date || 'Tuesday, 29th September 2026'}</span>
        </div>
        <div class="schedule-item">
          Session / Batch:
          <span style="font-size: 0.84rem;">${c.batch_session || 'Day 1 - Batch 1'}</span>
        </div>
        <div class="schedule-item">
          Accreditation Time:
          <span style="font-size: 0.84rem;">${c.accreditation_time || '09:00 AM'}</span>
        </div>
        <div class="schedule-item">
          Exam Commencement:
          <span style="font-size: 0.84rem;">${c.batch_time || '10:00 AM'}</span>
        </div>
        <div class="schedule-item" style="grid-column: 1 / -1; background: #f0fdf4; border: 1.5px solid #86efac; padding: 5px 8px; border-radius: 6px;">
          <strong style="color: #166534; font-size: 0.76rem; text-transform: uppercase;">📍 Designated Examination Venue:</strong>
          <span style="font-weight: 800; color: #004d40; font-size: 0.88rem; display: block; margin-top: 2px; line-height: 1.25;">
            Ilorin Innovation Hub, Ahmadu Bello Way, GRA, Ilorin, Kwara State, Nigeria
          </span>
        </div>
      </div>
    </div>

    <!-- Candidate Regulations -->
    <div class="photocard-rules" style="background: #fffbeb; border: 1.5px solid #fde68a; border-left: 4px solid #d97706; padding: 8px 12px; border-radius: 6px; margin: 8px 0;">
      <div style="font-weight: 800; color: #92400e; font-size: 0.78rem; margin-bottom: 4px; text-transform: uppercase; display: flex; align-items: center; gap: 4px;">
        <span>⚠️ MANDATORY EXAMINATION REGULATIONS & VENUE INSTRUCTIONS:</span>
      </div>
      <ol style="margin-left: 16px; font-size: 0.74rem; color: #78350f; line-height: 1.35; display: flex; flex-direction: column; gap: 2.5px;">
        <li><strong>Designated Venue:</strong> Ilorin Innovation Hub, Ahmadu Bello Way, GRA, Ilorin, Kwara State, Nigeria.</li>
        <li><strong>Strict Punctuality & Zero-Loitering Policy:</strong> Candidates must come to the venue at the stipulated accreditation time only (arrival is permitted at most <strong>20 minutes earlier</strong>). <strong>Loitering, crowding, or parading around the vicinity will NOT be tolerated.</strong></li>
        <li><strong>Mandatory Smart Mobile Device:</strong> Candidates <strong>MUST come to the venue with their smartphone</strong> (Android, iPhone, or any smart mobile device) with an active, functional web browser installed.</li>
        <li><strong>Physical Photocard Required:</strong> This printed physical photocard must be presented physically to the invigilator during hall accreditation.</li>
        <li><strong>Hall Scratch Card Token:</strong> Upon physical accreditation in the CBT hall, you will receive your single-use <strong>5-Digit Exam Scratch Card Token</strong> to unlock your workstation test.</li>
        <li><strong>Exam Duration:</strong> Strictly <strong>20 Minutes</strong> (50 cadre-specific multiple choice questions). The test automatically submits when the countdown timer expires.</li>
      </ol>
    </div>

    <div class="photocard-footer" style="padding-top: 8px; font-size: 0.72rem;">
      <div>
        <div><strong>Status:</strong> <span style="color:#059669; font-weight:800;">VERIFIED & ACCREDITED FOR CBT</span></div>
        <div style="font-size: 0.68rem; margin-top: 1px;">Security Verification Code: ${c.code_1}-${c.psn}</div>
      </div>
      <div class="slip-sign-line" style="width: 200px; font-size: 0.74rem;">
        Kwara State Civil Service Commission
      </div>
    </div>
  `;
}

function proceedToExamFromPhotocard() {
  showView('entry');
  switchEntryTab('start');
  if (state.registeredCandidate) {
    const psnInput = document.getElementById('token-exam-psn');
    if (psnInput) psnInput.value = state.registeredCandidate.psn;
    const tokenInput = document.getElementById('token-exam-code');
    if (tokenInput) tokenInput.focus();
  }
}

// -------------------------------------------------------------
// 1C. Take CBT Examination with 5-Digit Scratch Token
// -------------------------------------------------------------
const tokenExamForm = document.getElementById('form-token-exam');
if (tokenExamForm) {
  tokenExamForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    if (state.examStatus === 'closed') {
      showAlertModal(
        'Examination Closed',
        'The CBT Examination is currently closed by the Administrator. Candidate intake and test sessions are suspended.',
        'error'
      );
      return;
    }

    const psn = document.getElementById('token-exam-psn').value.trim();
    const tokenCode = document.getElementById('token-exam-code').value.trim();

    if (!psn || !tokenCode) {
      showAlertModal('Missing Credentials', 'Please provide both your PSN and your 5-digit Exam Scratch Card Token.', 'warning');
      return;
    }

    if (tokenCode.includes('-') || /[A-Za-z]/.test(tokenCode)) {
      showAlertModal(
        'Registration Code Entered',
        'You entered a Registration Clearance Code (' + tokenCode + '). Registration codes are used on Tab 1 ("🪪 Verification & Photocard") to generate your photocard.<br><br>To take the examination here on Tab 2, please enter your <strong>5-digit numeric hall scratch card token</strong> (e.g. <strong>65547</strong>).',
        'warning'
      );
      return;
    }

    if (tokenCode.length !== 5 || !/^\d{5}$/.test(tokenCode)) {
      showAlertModal('Invalid Token Format', 'The exam scratch card token must be exactly 5 digits (e.g. 65547).', 'warning');
      return;
    }

    const btn = document.getElementById('btn-start-token-exam');
    const originalText = btn ? btn.innerHTML : '';
    if (btn) {
      btn.disabled = true;
      btn.innerHTML = `<span>⏳ Validating Token & Unlocking Exam...</span>`;
    }

    try {
      const response = await fetch('/api/exam/start-with-token', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ psn: psn, token_code: tokenCode })
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || 'Failed to authenticate examination session.');
      }

      state.candidate = data.candidate;
      state.candidateId = data.candidate.psn;
      state.questions = data.questions;
      state.currentIndex = 0;
      state.answers = {};
      state.flagged.clear();
      state.isSubmitted = false;
      state.durationSeconds = (data.duration_minutes || 20) * 60; // Strictly 20 minutes (1200s)
      state.secondsRemaining = state.durationSeconds;

      // Update candidate details in exam header
      document.getElementById('exam-candidate-name').textContent = state.candidate.name;
      document.getElementById('exam-candidate-psn').textContent = `PSN: ${state.candidate.psn} | Paper: ${state.candidate.paper_code || data.paper_code || 'Cadre Evaluation'}`;
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

      showAlertModal(
        'Access Denied',
        err.message,
        'error'
      );
    } finally {
      if (btn) {
        btn.disabled = false;
        btn.innerHTML = originalText;
      }
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
  updateSubmitButtonState();
}

function updateSubmitButtonState() {
  const total = state.questions.length;
  const answeredCount = Object.keys(state.answers).length;
  const isComplete = (total > 0 && answeredCount >= total);

  // Update card submit button
  const submitBtn = document.getElementById('btn-submit-exam');
  const submitIcon = document.getElementById('btn-submit-icon');
  const submitText = document.getElementById('btn-submit-text');
  const submitHint = document.getElementById('submit-requirement-hint');

  // Sidebar submit button
  const sidebarSubmitBtn = document.getElementById('btn-sidebar-submit');
  const sidebarSubmitText = document.getElementById('sidebar-submit-text');

  if (submitBtn) {
    if (isComplete) {
      submitBtn.classList.remove('btn-submit-locked');
      submitBtn.classList.add('btn-submit-ready');
      if (submitIcon) submitIcon.textContent = '✅';
      if (submitText) submitText.textContent = `Finalize & Submit Exam (All ${total} Answered)`;
      if (submitHint) {
        submitHint.innerHTML = `<span style="color:#059669; font-weight:700;">✅ Excellent! All ${total} questions answered. You may now submit your examination.</span>`;
      }
    } else {
      submitBtn.classList.add('btn-submit-locked');
      submitBtn.classList.remove('btn-submit-ready');
      if (submitIcon) submitIcon.textContent = '🔒';
      const remaining = total - answeredCount;
      if (submitText) submitText.textContent = `Submit Exam (${answeredCount}/${total} Answered)`;
      if (submitHint) {
        submitHint.innerHTML = `<span style="color:#b45309;">⚠️ ${remaining} question${remaining > 1 ? 's' : ''} left. All ${total} questions must be answered before manual submission.</span>`;
      }
    }
  }

  if (sidebarSubmitBtn) {
    if (isComplete) {
      sidebarSubmitBtn.classList.remove('btn-submit-locked');
      sidebarSubmitBtn.classList.add('btn-submit-ready');
      if (sidebarSubmitText) {
        sidebarSubmitText.textContent = `✅ Finalize & Submit (${total}/${total})`;
      }
    } else {
      sidebarSubmitBtn.classList.add('btn-submit-locked');
      sidebarSubmitBtn.classList.remove('btn-submit-ready');
      if (sidebarSubmitText) {
        sidebarSubmitText.textContent = `🔒 Submit (${answeredCount}/${total} Answered)`;
      }
    }
  }
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

  if (total > 0 && answeredCount < total) {
    showUnansweredWarningModal(answeredCount, total, unansweredCount);
    return;
  }

  const ansEl = document.getElementById('modal-ans-count');
  const unansEl = document.getElementById('modal-unans-count');
  const flagEl = document.getElementById('modal-flag-count');

  if (ansEl) ansEl.textContent = answeredCount;
  if (unansEl) unansEl.textContent = unansweredCount;
  if (flagEl) flagEl.textContent = flaggedCount;

  const modal = document.getElementById('submit-modal');
  if (modal) modal.classList.add('active');
}

function closeSubmitModal() {
  const modal = document.getElementById('submit-modal');
  if (modal) modal.classList.remove('active');
}

function showUnansweredWarningModal(answered, total, unanswered) {
  const modal = document.getElementById('modal-unanswered-warning');
  if (!modal) return;
  const ansEl = document.getElementById('warn-answered-count');
  const totEl = document.getElementById('warn-total-count');
  const unansEl = document.getElementById('warn-unanswered-count');

  if (ansEl) ansEl.textContent = answered;
  if (totEl) totEl.textContent = total;
  if (unansEl) unansEl.textContent = unanswered;

  modal.classList.add('active');
}

function closeUnansweredWarningModal() {
  const modal = document.getElementById('modal-unanswered-warning');
  if (modal) modal.classList.remove('active');
}

function jumpToNextUnanswered() {
  closeUnansweredWarningModal();
  for (let i = 0; i < state.questions.length; i++) {
    const q = state.questions[i];
    if (!state.answers[String(q.number)]) {
      jumpToQuestion(i);
      const qCard = document.querySelector('.question-card');
      if (qCard) {
        qCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
      return;
    }
  }
}

function toggleMobilePalette() {
  const palette = document.getElementById('exam-palette-sidebar');
  if (!palette) return;
  palette.classList.toggle('mobile-open');
  if (palette.classList.contains('mobile-open')) {
    palette.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
}

async function submitExam(isAuto = false) {
  if (state.isSubmitted) return;

  const total = state.questions.length;
  const answeredCount = Object.keys(state.answers).length;

  // Enforce: manual submission requires ALL questions answered; autosubmit on timer bypasses
  if (!isAuto && total > 0 && answeredCount < total) {
    showUnansweredWarningModal(answeredCount, total, total - answeredCount);
    return;
  }

  state.isSubmitted = true;

  if (state.timerInterval) clearInterval(state.timerInterval);
  closeSubmitModal();
  closeExitModal();
  closeUnansweredWarningModal();

  const timeTaken = state.durationSeconds - state.secondsRemaining;

  const payload = {
    candidate_id: state.candidateId,
    name: state.candidate.name,
    psn: state.candidate.psn,
    email: state.candidate.email,
    grade_level: state.candidate.grade_level,
    mda: state.candidate.mda,
    paper_code: (state.candidate.paper_code || ""),
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
  const candidate = res.candidate || {};

  const nameEl = document.getElementById('res-name');
  if (nameEl) nameEl.textContent = candidate.name || '-';

  const psnEl = document.getElementById('res-psn');
  if (psnEl) psnEl.textContent = candidate.psn || '-';

  const emailEl = document.getElementById('res-email');
  if (emailEl) emailEl.textContent = candidate.email || '-';

  const gradeEl = document.getElementById('res-grade');
  if (gradeEl) gradeEl.textContent = candidate.grade_level || '-';

  const mdaEl = document.getElementById('res-mda');
  if (mdaEl) mdaEl.textContent = candidate.mda || '-';

  const paperEl = document.getElementById('res-paper');
  if (paperEl) {
    paperEl.textContent = candidate.paper_code || (state.candidate ? state.candidate.paper_code : '') || 'Promotion CBT Evaluation';
  }

  const dateEl = document.getElementById('res-date');
  if (dateEl) dateEl.textContent = res.submitted_at || new Date().toLocaleString();

  const totalSecs = res.time_taken_seconds || 0;
  const mins = Math.floor(totalSecs / 60);
  const secs = totalSecs % 60;
  const timeEl = document.getElementById('res-time');
  if (timeEl) timeEl.textContent = `${mins}m ${secs}s`;

  const subId = (res.submission_id || '00000').toString().padStart(5, '0');
  const refCode = `KWS-CSC-SUB-${subId}-${candidate.psn || '000000'}`;
  const refEl = document.getElementById('res-ref-code');
  if (refEl) refEl.textContent = `Ref: ${refCode}`;

  state.lastResult = res;
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
    const btnRoster = document.getElementById('btn-download-roster');
    if (btnExcel) btnExcel.href = `/api/results/excel?token=${encodeURIComponent(state.adminToken)}`;
    if (btnCsv) btnCsv.href = `/api/results/csv?token=${encodeURIComponent(state.adminToken)}`;
    if (btnRoster) btnRoster.href = `/api/admin/roster/excel?token=${encodeURIComponent(state.adminToken)}`;

    renderAdminTable();
    loadAdminTokens();
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
// Admin Scratch Card Tokens & Candidate Reset Tools
// -------------------------------------------------------------
async function loadAdminTokens() {
  if (!state.adminToken) return;
  try {
    const res = await fetch('/api/admin/tokens', {
      headers: { 'Authorization': `Bearer ${state.adminToken}` }
    });
    if (!res.ok) return;
    const data = await res.json();
    state.adminTokensSummary = data;

    const totEl = document.getElementById('admin-tok-total');
    const unEl = document.getElementById('admin-tok-unassigned');
    const actEl = document.getElementById('admin-tok-active');
    const compEl = document.getElementById('admin-tok-completed');

    if (totEl) totEl.textContent = Number(data.summary.total_tokens).toLocaleString();
    if (unEl) unEl.textContent = Number(data.summary.unassigned).toLocaleString();
    if (actEl) actEl.textContent = Number(data.summary.active).toLocaleString();
    if (compEl) compEl.textContent = Number(data.summary.completed).toLocaleString();
  } catch (err) {
    console.warn('Could not load admin tokens summary:', err);
  }
}

async function openAdminTokensModal() {
  const modal = document.getElementById('admin-tokens-modal');
  const grid = document.getElementById('admin-tokens-grid');
  if (!modal) return;
  modal.classList.add('active');

  if (grid) grid.innerHTML = `<div style="text-align: center; color: #64748b; padding: 24px; grid-column: 1 / -1;">⏳ Loading examination tokens...</div>`;

  try {
    const res = await fetch('/api/admin/tokens', {
      headers: { 'Authorization': `Bearer ${state.adminToken}` }
    });
    const data = await res.json();
    const tokens = data.sample_tokens || [];

    if (tokens.length === 0) {
      grid.innerHTML = `<div style="text-align: center; color: #64748b; padding: 24px; grid-column: 1 / -1;">No unassigned scratch tokens available in pool.</div>`;
      return;
    }

    grid.innerHTML = tokens.map((tok, idx) => `
      <div class="token-slip-item">
        <div class="tok-mda">Kwara CSC 2026 CBT</div>
        <div class="tok-num">${tok}</div>
        <div class="tok-sub">20-Min Promotion Exam Slip #${idx + 1}</div>
      </div>
    `).join('');
  } catch (err) {
    if (grid) grid.innerHTML = `<div style="text-align: center; color: #dc2626; padding: 24px; grid-column: 1 / -1;">Failed to load tokens: ${err.message}</div>`;
  }
}

function closeAdminTokensModal() {
  const modal = document.getElementById('admin-tokens-modal');
  if (modal) modal.classList.remove('active');
}

function printTokenSlips() {
  const grid = document.getElementById('admin-tokens-grid');
  if (!grid) return;
  const printWin = window.open('', '', 'width=900,height=650');
  printWin.document.write(`
    <!DOCTYPE html>
    <html>
    <head>
      <title>Kwara State CSC 2026 CBT - Exam Scratch Card Tokens</title>
      <style>
        body { font-family: monospace, sans-serif; padding: 20px; }
        h2 { text-align: center; margin-bottom: 4px; font-size: 18px; }
        p { text-align: center; font-size: 12px; color: #555; margin-bottom: 20px; }
        .grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
        .slip { border: 1.5px dashed #333; padding: 12px 8px; text-align: center; border-radius: 6px; page-break-inside: avoid; }
        .mda { font-size: 10px; font-weight: bold; text-transform: uppercase; color: #444; }
        .num { font-size: 26px; font-weight: 900; letter-spacing: 0.18em; margin: 8px 0; color: #000; }
        .info { font-size: 9px; color: #666; }
      </style>
    </head>
    <body>
      <h2>KWARA STATE CIVIL SERVICE COMMISSION</h2>
      <p>2026 PROMOTION EVALUATION CBT - OFFICIAL 5-DIGIT EXAM SCRATCH CARD SLIPS</p>
      <div class="grid">
        ${grid.innerHTML}
      </div>
    </body>
    </html>
  `);
  printWin.document.close();
  printWin.focus();
  setTimeout(() => { printWin.print(); }, 400);
}

function openAdminResetModal() {
  const modal = document.getElementById('admin-reset-modal');
  const msg = document.getElementById('admin-reset-msg');
  if (msg) msg.style.display = 'none';
  if (modal) modal.classList.add('active');
}

function closeAdminResetModal() {
  const modal = document.getElementById('admin-reset-modal');
  if (modal) modal.classList.remove('active');
}

async function executeAdminCandidateReset() {
  const psnInput = document.getElementById('admin-reset-psn');
  const reasonInput = document.getElementById('admin-reset-reason');
  const msg = document.getElementById('admin-reset-msg');

  const psn = (psnInput ? psnInput.value : '').trim();
  const reason = (reasonInput ? reasonInput.value : '').trim();

  if (!psn) {
    showAlertModal('PSN Required', 'Please enter candidate PSN to reset.', 'warning');
    return;
  }

  if (!confirm(`Are you sure you want to archive previous submissions and unlock PSN ${psn} for a retake?`)) {
    return;
  }

  try {
    const res = await fetch('/api/admin/reset-candidate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${state.adminToken}`
      },
      body: JSON.stringify({ psn, reason })
    });

    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.detail || 'Reset failed.');
    }

    if (msg) {
      msg.style.display = 'block';
      msg.style.background = '#dcfce7';
      msg.style.color = '#166534';
      msg.textContent = `✅ Success: PSN ${psn} has been unlocked and archived for retake.`;
    }

    loadAdminSubmissions();
    loadAdminTokens();
    setTimeout(() => { closeAdminResetModal(); }, 1600);
  } catch (err) {
    if (msg) {
      msg.style.display = 'block';
      msg.style.background = '#fee2e2';
      msg.style.color = '#991b1b';
      msg.textContent = `❌ Error: ${err.message}`;
    }
  }
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
