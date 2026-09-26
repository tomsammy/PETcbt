import os

html_content = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0, viewport-fit=cover">
  <title>Kwara CSC CBT 2026 - Interactive Candidate Orientation & Presentation</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
  <style>
    :root {
      --primary: #004d40;
      --primary-dark: #00251a;
      --primary-teal: #00796b;
      --accent-gold: #d97706;
      --accent-red: #dc2626;
      --accent-green: #10b981;
      --dark-slate: #0f172a;
      --card-bg: #ffffff;
      --text-dark: #1e293b;
      --text-muted: #64748b;
      --border-color: #e2e8f0;
    }

    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }

    body {
      background: #090d16;
      color: #ffffff;
      min-height: 100vh;
      overflow-x: hidden;
      display: flex;
      flex-direction: column;
    }

    /* Presentation Navigation Bar */
    .pres-nav {
      background: rgba(0, 77, 64, 0.95);
      backdrop-filter: blur(12px);
      border-bottom: 1.5px solid rgba(255, 255, 255, 0.1);
      padding: 10px 24px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      position: sticky;
      top: 0;
      z-index: 1000;
    }
    .brand-group {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .brand-logo {
      width: 40px;
      height: 40px;
      object-fit: contain;
    }
    .brand-title {
      font-size: 0.95rem;
      font-weight: 800;
      color: #ffffff;
      line-height: 1.2;
    }
    .brand-sub {
      font-size: 0.72rem;
      color: #a7f3d0;
      font-weight: 500;
    }

    .nav-actions {
      display: flex;
      align-items: center;
      gap: 10px;
    }
    .btn-nav {
      background: rgba(255, 255, 255, 0.12);
      color: #ffffff;
      border: 1px solid rgba(255, 255, 255, 0.2);
      padding: 7px 14px;
      border-radius: 8px;
      font-size: 0.82rem;
      font-weight: 700;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      text-decoration: none;
      transition: all 0.2s ease;
    }
    .btn-nav:hover {
      background: rgba(255, 255, 255, 0.25);
      border-color: #34d399;
    }
    .btn-nav-gold {
      background: #d97706;
      border-color: #f59e0b;
      color: #ffffff;
    }
    .btn-nav-gold:hover {
      background: #b45309;
    }

    /* Presentation Viewport */
    .pres-viewport {
      flex: 1;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 24px 20px;
      position: relative;
    }

    /* Slide Stage Container */
    .slide-stage {
      background: #ffffff;
      color: var(--text-dark);
      width: 100%;
      max-width: 1240px;
      aspect-ratio: 16 / 9;
      border-radius: 18px;
      box-shadow: 0 25px 60px rgba(0, 0, 0, 0.5);
      overflow: hidden;
      display: none;
      flex-direction: column;
      position: relative;
      animation: fadeInSlide 0.35s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .slide-stage.active {
      display: flex;
    }

    @keyframes fadeInSlide {
      from { opacity: 0; transform: scale(0.985) translateY(8px); }
      to { opacity: 1; transform: scale(1) translateY(0); }
    }

    /* Slide Inner Elements */
    .slide-header {
      background: var(--primary);
      color: #ffffff;
      padding: 12px 28px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 2px solid #00796b;
    }
    .slide-header-left {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .slide-header-logo {
      width: 38px;
      height: 38px;
      object-fit: contain;
    }
    .slide-badge-category {
      font-size: 0.72rem;
      font-weight: 800;
      color: #a7f3d0;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }
    .slide-title {
      font-size: 1.25rem;
      font-weight: 800;
      color: #ffffff;
      letter-spacing: -0.01em;
    }
    .slide-pill {
      background: var(--primary-teal);
      color: #ffffff;
      padding: 5px 14px;
      border-radius: 20px;
      font-size: 0.8rem;
      font-weight: 800;
      border: 1px solid #34d399;
    }

    .slide-content {
      flex: 1;
      padding: 24px 30px;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
    }

    .slide-footer {
      background: #f8fafc;
      border-top: 1px solid #e2e8f0;
      padding: 10px 28px;
      font-size: 0.78rem;
      color: var(--text-muted);
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    /* 2-Column Screenshot + Instruction Layout */
    .slide-grid-split {
      display: grid;
      grid-template-columns: 1.35fr 1fr;
      gap: 24px;
      height: 100%;
      align-items: stretch;
    }

    .screenshot-card {
      background: #0f172a;
      border-radius: 12px;
      border: 1.5px solid #cbd5e1;
      overflow: hidden;
      box-shadow: 0 10px 25px rgba(0,0,0,0.1);
      display: flex;
      flex-direction: column;
      position: relative;
      cursor: zoom-in;
    }
    .screenshot-card img {
      width: 100%;
      height: 100%;
      object-fit: contain;
      display: block;
      background: #000;
    }
    .screenshot-caption {
      position: absolute;
      bottom: 0;
      left: 0;
      right: 0;
      background: rgba(15, 23, 42, 0.85);
      backdrop-filter: blur(6px);
      padding: 8px 14px;
      font-size: 0.75rem;
      font-weight: 700;
      color: #38bdf8;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }

    .guide-card {
      background: #f8fafc;
      border: 1.5px solid #e2e8f0;
      border-radius: 12px;
      padding: 20px;
      display: flex;
      flex-direction: column;
      gap: 12px;
      overflow-y: auto;
    }
    .guide-card h3 {
      font-size: 1.05rem;
      font-weight: 800;
      color: var(--primary);
      margin: 0;
    }
    .guide-list {
      list-style: none;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }
    .guide-list li {
      font-size: 0.86rem;
      line-height: 1.5;
      color: var(--text-dark);
      padding-left: 20px;
      position: relative;
    }
    .guide-list li::before {
      content: "✔";
      position: absolute;
      left: 0;
      color: var(--accent-green);
      font-weight: 900;
    }
    .guide-alert {
      background: #fef2f2;
      border: 1.5px solid #fecaca;
      border-radius: 8px;
      padding: 10px 14px;
      font-size: 0.8rem;
      color: #991b1b;
      line-height: 1.4;
      font-weight: 600;
      margin-top: auto;
    }
    .guide-tip {
      background: #fffbeb;
      border: 1.5px solid #fde68a;
      border-radius: 8px;
      padding: 10px 14px;
      font-size: 0.8rem;
      color: #92400e;
      line-height: 1.4;
      font-weight: 600;
      margin-top: auto;
    }

    /* Presentation Bottom Controls Bar */
    .pres-controls {
      background: rgba(15, 23, 42, 0.95);
      border-top: 1px solid rgba(255, 255, 255, 0.1);
      padding: 12px 24px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      position: sticky;
      bottom: 0;
      z-index: 1000;
    }
    .control-btn-group {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .btn-ctrl {
      background: #004d40;
      color: #ffffff;
      border: none;
      padding: 8px 18px;
      border-radius: 8px;
      font-size: 0.85rem;
      font-weight: 800;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      transition: all 0.2s ease;
    }
    .btn-ctrl:hover:not(:disabled) {
      background: #00796b;
      transform: translateY(-1px);
    }
    .btn-ctrl:disabled {
      opacity: 0.4;
      cursor: not-allowed;
    }
    .btn-ctrl-sub {
      background: rgba(255, 255, 255, 0.1);
      border: 1px solid rgba(255, 255, 255, 0.2);
    }

    .slide-progress-text {
      font-size: 0.88rem;
      font-weight: 700;
      color: #cbd5e1;
      font-variant-numeric: tabular-nums;
    }

    /* Speaker Notes Drawer */
    .speaker-drawer {
      display: none;
      background: #1e293b;
      color: #f1f5f9;
      border-top: 3px solid #d97706;
      padding: 16px 28px;
      font-size: 0.88rem;
      line-height: 1.6;
      max-height: 180px;
      overflow-y: auto;
    }
    .speaker-drawer.open {
      display: block;
    }
    .speaker-drawer-header {
      font-size: 0.78rem;
      font-weight: 800;
      color: #fbbf24;
      text-transform: uppercase;
      margin-bottom: 6px;
      display: flex;
      align-items: center;
      gap: 8px;
    }

    /* Modal Image Lightbox */
    .lightbox-modal {
      position: fixed;
      inset: 0;
      background: rgba(0, 0, 0, 0.95);
      display: none;
      align-items: center;
      justify-content: center;
      padding: 30px;
      z-index: 10000;
      cursor: zoom-out;
    }
    .lightbox-modal.open {
      display: flex;
    }
    .lightbox-modal img {
      max-width: 95vw;
      max-height: 90vh;
      border-radius: 12px;
      box-shadow: 0 20px 50px rgba(0,0,0,0.8);
      border: 2px solid #334155;
    }

    /* Responsive adjustments */
    @media (max-width: 900px) {
      .slide-stage {
        aspect-ratio: auto;
        min-height: 600px;
      }
      .slide-grid-split {
        grid-template-columns: 1fr;
      }
    }
  </style>
</head>
<body>

  <!-- Top Header Navigation -->
  <header class="pres-nav">
    <div class="brand-group">
      <img src="/static/images/logo.png" alt="Kwara CSC" class="brand-logo" onerror="this.src='/static/images/logo.png'">
      <div>
        <div class="brand-title">KWARA STATE CIVIL SERVICE COMMISSION</div>
        <div class="brand-sub">2026 Promotion Evaluation CBT Examination &bull; Candidate Orientation Presentation</div>
      </div>
    </div>

    <div class="nav-actions">
      <button type="button" class="btn-nav" onclick="toggleSpeakerNotes()">
        <span>🎙️</span> <span id="btn-notes-label">Speaker Notes (S)</span>
      </button>
      <button type="button" class="btn-nav" onclick="toggleFullscreen()">
        <span>⛶</span> Fullscreen (F)
      </button>
      <a href="/download-orientation-pptx" class="btn-nav btn-nav-gold" download>
        <span>📥</span> Download PowerPoint (.PPTX)
      </a>
      <a href="/demo" class="btn-nav" target="_blank" style="background:#059669; border-color:#10b981;">
        <span>🚀</span> Open Live Demo Exam
      </a>
    </div>
  </header>

  <!-- Main Slide Viewport -->
  <main class="pres-viewport">

    <!-- ========================================== -->
    <!-- SLIDE 1: Title Slide                       -->
    <!-- ========================================== -->
    <section class="slide-stage active" data-slide="1" style="background: radial-gradient(circle at top right, #00796b, #004d40); color: #fff; text-align: center; justify-content: center; align-items: center; padding: 40px 30px;">
      <img src="/static/images/logo.png" alt="Logo" style="width: 100px; height: 100px; object-fit: contain; margin-bottom: 20px;">
      <h2 style="font-size: 1.15rem; font-weight: 800; color: #a7f3d0; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 8px;">
        Kwara State Civil Service Commission
      </h2>
      <h1 style="font-size: 2.5rem; font-weight: 900; color: #ffffff; letter-spacing: -0.02em; max-width: 850px; line-height: 1.2; margin-bottom: 12px;">
        2026 Promotion Evaluation CBT Examination
      </h1>
      <p style="font-size: 1.15rem; color: #fef3c7; max-width: 750px; margin-bottom: 32px; font-weight: 600;">
        Candidate Step-by-Step Orientation & System Interface Walkthrough
      </p>

      <div style="background: rgba(255, 255, 255, 0.12); border: 1.5px solid rgba(255, 255, 255, 0.25); border-radius: 14px; padding: 12px 28px; display: inline-flex; align-items: center; gap: 16px; font-size: 0.95rem; font-weight: 700;">
        <span>📅 Batch 2026 Evaluation</span>
        <span>&bull;</span>
        <span>⏱️ 20 Minutes / 40 Questions</span>
        <span>&bull;</span>
        <span>🛡️ Proctored Environment</span>
      </div>

      <div style="position: absolute; bottom: 20px; font-size: 0.85rem; color: #a7f3d0; opacity: 0.8;">
        Use [◀ Left] and [Right ▶] Arrow Keys or Spacebar to Navigate
      </div>
    </section>

    <!-- ========================================== -->
    <!-- SLIDE 2: Ground Rules                      -->
    <!-- ========================================== -->
    <section class="slide-stage" data-slide="2">
      <div class="slide-header">
        <div class="slide-header-left">
          <img src="/static/images/logo.png" class="slide-header-logo" alt="Logo">
          <div>
            <div class="slide-badge-category">Core Examination Metrics</div>
            <div class="slide-title">Examination Ground Rules & Structure</div>
          </div>
        </div>
        <div class="slide-pill">Slide 2 / 13</div>
      </div>

      <div class="slide-content">
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 18px; margin-bottom: 24px;">
          <div style="background: #f8fafc; border: 1.5px solid #e2e8f0; border-radius: 14px; padding: 22px 18px; text-align: center;">
            <div style="font-size: 2.2rem; margin-bottom: 6px;">⏱️</div>
            <h3 style="font-size: 1.3rem; font-weight: 900; color: #004d40;">20 MINUTES</h3>
            <div style="font-size: 0.78rem; font-weight: 800; color: #d97706; margin-bottom: 8px;">STRICT DURATION</div>
            <p style="font-size: 0.82rem; color: #475569; line-height: 1.5;">Continuous countdown clock displayed on top of screen. Auto-submits at 00:00.</p>
          </div>

          <div style="background: #f8fafc; border: 1.5px solid #e2e8f0; border-radius: 14px; padding: 22px 18px; text-align: center;">
            <div style="font-size: 2.2rem; margin-bottom: 6px;">📝</div>
            <h3 style="font-size: 1.3rem; font-weight: 900; color: #004d40;">40 QUESTIONS</h3>
            <div style="font-size: 0.78rem; font-weight: 800; color: #d97706; margin-bottom: 8px;">MULTIPLE CHOICE</div>
            <p style="font-size: 0.82rem; color: #475569; line-height: 1.5;">Single choice objective questions. Every question carries 1 mark. No negative marking.</p>
          </div>

          <div style="background: #f8fafc; border: 1.5px solid #e2e8f0; border-radius: 14px; padding: 22px 18px; text-align: center;">
            <div style="font-size: 2.2rem; margin-bottom: 6px;">🔒</div>
            <h3 style="font-size: 1.3rem; font-weight: 900; color: #004d40;">ZERO SCORE</h3>
            <div style="font-size: 0.78rem; font-weight: 800; color: #d97706; margin-bottom: 8px;">ON WORKSTATION</div>
            <p style="font-size: 0.82rem; color: #475569; line-height: 1.5;">In accordance with Civil Service rules, marks are confidential and sent to your MDA.</p>
          </div>

          <div style="background: #f8fafc; border: 1.5px solid #e2e8f0; border-radius: 14px; padding: 22px 18px; text-align: center;">
            <div style="font-size: 2.2rem; margin-bottom: 6px;">🛡️</div>
            <h3 style="font-size: 1.3rem; font-weight: 900; color: #dc2626;">3-STRIKE RULE</h3>
            <div style="font-size: 0.78rem; font-weight: 800; color: #dc2626; margin-bottom: 8px;">PROCTOR POLICY</div>
            <p style="font-size: 0.82rem; color: #475569; line-height: 1.5;">App-switching or tab minimization triggers security curtain and infraction strikes.</p>
          </div>
        </div>

        <div style="background: #fef2f2; border: 1.5px solid #fecaca; border-radius: 12px; padding: 18px 24px; display: flex; align-items: center; gap: 16px;">
          <span style="font-size: 2.2rem;">⚠️</span>
          <div style="font-size: 0.9rem; color: #991b1b; line-height: 1.5;">
            <strong>Mandatory Hall Requirements:</strong> Ensure you have your printed <strong>Photocard Registration Slip</strong> with your <strong>Public Service Number (PSN)</strong> and <strong>Code 1</strong>. Phones must have at least 80% battery and Do-Not-Disturb turned on.
          </div>
        </div>
      </div>

      <div class="slide-footer">
        <span>Kwara State Civil Service Commission &bull; 2026 CBT Orientation</span>
        <span>Slide 2 of 13</span>
      </div>
    </section>

    <!-- ========================================== -->
    <!-- SLIDE 3: Stage 1 - Candidate Login         -->
    <!-- ========================================== -->
    <section class="slide-stage" data-slide="3">
      <div class="slide-header">
        <div class="slide-header-left">
          <img src="/static/images/logo.png" class="slide-header-logo" alt="Logo">
          <div>
            <div class="slide-badge-category">STAGE 1 OF 7</div>
            <div class="slide-title">Candidate Portal Login & Accreditation</div>
          </div>
        </div>
        <div class="slide-pill">Stage 1</div>
      </div>

      <div class="slide-content">
        <div class="slide-grid-split">
          <div class="screenshot-card" onclick="openLightbox('/static/images/orientation/stage1_login.png')">
            <img src="/static/images/orientation/stage1_login.png" alt="Stage 1 Login">
            <div class="screenshot-caption">
              <span>🔍 Stage 1: Official Login Screen</span>
              <span>Click to Enlarge</span>
            </div>
          </div>

          <div class="guide-card">
            <h3>🔑 How to Log In & Authenticate</h3>
            <ul class="guide-list">
              <li><strong>Check Status Bar:</strong> Confirm that the portal displays <em>"ACTIVE & ACCREDITATION OPEN"</em>.</li>
              <li><strong>Enter PSN:</strong> Type your 6-digit Kwara State civil service staff number (e.g. <code>123456</code>).</li>
              <li><strong>Enter Code 1:</strong> Type the exact Examination Code 1 from your photocard slip (e.g. <code>B-10294</code>).</li>
              <li><strong>Click Verify:</strong> Click <strong>"Verify & Access Examination"</strong> to load your assigned paper.</li>
            </ul>

            <div class="guide-tip">
              💡 <strong>Pro Tip:</strong> Code 1 is case-sensitive and includes hyphens. Do not share your Code 1 with anyone.
            </div>
          </div>
        </div>
      </div>

      <div class="slide-footer">
        <span>Kwara State Civil Service Commission &bull; Stage 1 Login</span>
        <span>Slide 3 of 13</span>
      </div>
    </section>

    <!-- ========================================== -->
    <!-- SLIDE 4: Stage 2 - Bio-Data Verification   -->
    <!-- ========================================== -->
    <section class="slide-stage" data-slide="4">
      <div class="slide-header">
        <div class="slide-header-left">
          <img src="/static/images/logo.png" class="slide-header-logo" alt="Logo">
          <div>
            <div class="slide-badge-category">STAGE 2 OF 7</div>
            <div class="slide-title">Candidate Bio-Data & Paper Allocation Verification</div>
          </div>
        </div>
        <div class="slide-pill">Stage 2</div>
      </div>

      <div class="slide-content">
        <div class="slide-grid-split">
          <div class="screenshot-card" onclick="openLightbox('/static/images/orientation/stage2_verification.png')">
            <img src="/static/images/orientation/stage2_verification.png" alt="Stage 2 Verification">
            <div class="screenshot-caption">
              <span>🔍 Stage 2: Accreditation Verification Modal</span>
              <span>Click to Enlarge</span>
            </div>
          </div>

          <div class="guide-card">
            <h3>📋 Critical Verification Steps</h3>
            <ul class="guide-list">
              <li><strong>Check Full Name:</strong> Verify your name matches your civil service record.</li>
              <li><strong>Verify MDA:</strong> Confirm your Ministry, Department, or Agency is correct.</li>
              <li><strong>Check Proposed Grade:</strong> Ensure your proposed promotional grade level is accurate.</li>
              <li><strong>Allocated Paper Code:</strong> Confirm your paper (e.g. <code>MARD-GL12-B</code>).</li>
              <li><strong>Confirm & Begin:</strong> Once verified, click <strong>"Confirm & Begin Examination"</strong>.</li>
            </ul>

            <div class="guide-alert">
              ⚠️ <strong>Strict Rule:</strong> The 20-minute countdown clock starts the exact moment you click "Confirm & Begin". Discrepancies must be reported before starting.
            </div>
          </div>
        </div>
      </div>

      <div class="slide-footer">
        <span>Kwara State Civil Service Commission &bull; Stage 2 Verification</span>
        <span>Slide 4 of 13</span>
      </div>
    </section>

    <!-- ========================================== -->
    <!-- SLIDE 5: Stage 3A - Active Exam Interface  -->
    <!-- ========================================== -->
    <section class="slide-stage" data-slide="5">
      <div class="slide-header">
        <div class="slide-header-left">
          <img src="/static/images/logo.png" class="slide-header-logo" alt="Logo">
          <div>
            <div class="slide-badge-category">STAGE 3 OF 7</div>
            <div class="slide-title">Active Examination Interface & Countdown Clock</div>
          </div>
        </div>
        <div class="slide-pill">Stage 3A</div>
      </div>

      <div class="slide-content">
        <div class="slide-grid-split">
          <div class="screenshot-card" onclick="openLightbox('/static/images/orientation/stage3_exam_screen.png')">
            <img src="/static/images/orientation/stage3_exam_screen.png" alt="Stage 3 Exam Screen">
            <div class="screenshot-caption">
              <span>🔍 Stage 3: Live Examination Interface</span>
              <span>Click to Enlarge</span>
            </div>
          </div>

          <div class="guide-card">
            <h3>🖥️ Screen Layout & Features</h3>
            <ul class="guide-list">
              <li><strong>Candidate Top Bar:</strong> Displays your name, PSN, paper code, and profile initials.</li>
              <li><strong>Live Countdown Clock:</strong> Real-time clock counting down from 20:00. Turns amber at 5 mins, red at 1 min.</li>
              <li><strong>Proctor Shield Badge:</strong> Confirms background proctoring is securing your test session.</li>
              <li><strong>Question Card:</strong> Clean, high-contrast question display with options A, B, C, D.</li>
              <li><strong>Instant Auto-Save:</strong> Selections save automatically in browser memory upon clicking.</li>
            </ul>

            <div class="guide-tip">
              ⏱️ <strong>Time Management:</strong> 20 minutes for 40 questions gives you 30 seconds per question. Keep moving forward!
            </div>
          </div>
        </div>
      </div>

      <div class="slide-footer">
        <span>Kwara State Civil Service Commission &bull; Stage 3 Interface</span>
        <span>Slide 5 of 13</span>
      </div>
    </section>

    <!-- ========================================== -->
    <!-- SLIDE 6: Stage 3B - 40-Question Palette    -->
    <!-- ========================================== -->
    <section class="slide-stage" data-slide="6">
      <div class="slide-header">
        <div class="slide-header-left">
          <img src="/static/images/logo.png" class="slide-header-logo" alt="Logo">
          <div>
            <div class="slide-badge-category">STAGE 3 (CONT.)</div>
            <div class="slide-title">Question Grid (40) & Navigation Controls</div>
          </div>
        </div>
        <div class="slide-pill">Stage 3B</div>
      </div>

      <div class="slide-content">
        <div class="slide-grid-split">
          <div class="screenshot-card" onclick="openLightbox('/static/images/orientation/stage3_exam_screen.png')">
            <img src="/static/images/orientation/stage3_exam_screen.png" alt="Stage 3 Controls">
            <div class="screenshot-caption">
              <span>🔍 Palette Grid & Action Buttons</span>
              <span>Click to Enlarge</span>
            </div>
          </div>

          <div class="guide-card">
            <h3>🎯 Palette Color Codes & Buttons</h3>
            <ul class="guide-list">
              <li><strong>🟩 GREEN:</strong> Question has been answered. Aim to turn all 40 green!</li>
              <li><strong>🟪 PURPLE:</strong> Flagged for review (bookmarked for later checking).</li>
              <li><strong>⬜ GRAY:</strong> Unanswered question. Do not leave any question gray!</li>
              <li><strong>Direct Jump:</strong> Click ANY number on the 40-grid to jump directly to that question.</li>
              <li><strong>✖ Clear Choice:</strong> Clears your selected answer if you want to leave it blank temporarily.</li>
              <li><strong>⚑ Flag for Review:</strong> Tags difficult questions so you can easily return later.</li>
            </ul>

            <div class="guide-tip">
              💡 <strong>Pro Tip:</strong> You don't need to click 'Next' 30 times. Simply tap the number on the grid!
            </div>
          </div>
        </div>
      </div>

      <div class="slide-footer">
        <span>Kwara State Civil Service Commission &bull; Stage 3 Controls</span>
        <span>Slide 6 of 13</span>
      </div>
    </section>

    <!-- ========================================== -->
    <!-- SLIDE 7: Stage 4 - Blackout Curtain        -->
    <!-- ========================================== -->
    <section class="slide-stage" data-slide="7">
      <div class="slide-header">
        <div class="slide-header-left">
          <img src="/static/images/logo.png" class="slide-header-logo" alt="Logo">
          <div>
            <div class="slide-badge-category">STAGE 4 OF 7</div>
            <div class="slide-title">Anti-Cheating & Proctored Blackout Curtain</div>
          </div>
        </div>
        <div class="slide-pill">Stage 4</div>
      </div>

      <div class="slide-content">
        <div class="slide-grid-split">
          <div class="screenshot-card" onclick="openLightbox('/static/images/orientation/stage4_blackout_curtain.png')">
            <img src="/static/images/orientation/stage4_blackout_curtain.png" alt="Stage 4 Blackout">
            <div class="screenshot-caption">
              <span>🔍 Stage 4: Proctored Blackout Curtain</span>
              <span>Click to Enlarge</span>
            </div>
          </div>

          <div class="guide-card">
            <h3>🛡️ Understanding the Blackout Curtain</h3>
            <ul class="guide-list">
              <li><strong>What Triggers It:</strong> Switching browser tabs, minimizing the window, opening another app, or incoming phone calls.</li>
              <li><strong>Instant Blackout:</strong> The screen goes pitch black to protect questions from external cameras or web search.</li>
              <li><strong>How to Resume:</strong> Tap or click anywhere on the black curtain to refocus the exam window immediately.</li>
              <li><strong>Official Strike:</strong> Refocusing will log an infraction and show the Security Warning dialog.</li>
            </ul>

            <div class="guide-alert">
              🚫 <strong>Forbidden Actions:</strong> PrintScreen, Snipping tool (Win+Shift+S), Cmd+Shift+3/4, Ctrl+P (Print), Ctrl+S (Save), F12 (DevTools), right-click, and text copying are locked and logged.
            </div>
          </div>
        </div>
      </div>

      <div class="slide-footer">
        <span>Kwara State Civil Service Commission &bull; Stage 4 Blackout</span>
        <span>Slide 7 of 13</span>
      </div>
    </section>

    <!-- ========================================== -->
    <!-- SLIDE 8: Stage 5 - 3-Strike System         -->
    <!-- ========================================== -->
    <section class="slide-stage" data-slide="8">
      <div class="slide-header">
        <div class="slide-header-left">
          <img src="/static/images/logo.png" class="slide-header-logo" alt="Logo">
          <div>
            <div class="slide-badge-category">STAGE 5 OF 7</div>
            <div class="slide-title">Security Violation Warnings (3-Strike System)</div>
          </div>
        </div>
        <div class="slide-pill">Stage 5</div>
      </div>

      <div class="slide-content">
        <div class="slide-grid-split">
          <div class="screenshot-card" onclick="openLightbox('/static/images/orientation/stage5_strike_warning.png')">
            <img src="/static/images/orientation/stage5_strike_warning.png" alt="Stage 5 Warning">
            <div class="screenshot-caption">
              <span>🔍 Stage 5: Strike 1 Warning Modal</span>
              <span>Click to Enlarge</span>
            </div>
          </div>

          <div class="guide-card">
            <h3>🚨 The 3-Strike Disqualification Progression</h3>
            <ul class="guide-list">
              <li><strong>STRIKE 1: Formal Warning:</strong> Modal appears. Timestamp and violation reason recorded on server. Click 'Return to Examination'.</li>
              <li><strong>STRIKE 2: Final Warning:</strong> High-urgency red alert: <em>"You have only ONE warning remaining!"</em>. Next violation terminates exam.</li>
              <li><strong>STRIKE 3: IMMEDIATE TERMINATION:</strong> Examination terminates immediately! Answers auto-submit with a disqualification flag.</li>
            </ul>

            <div class="guide-alert">
              📸 <strong>Forensic Watermark:</strong> A dynamic watermark with your PSN and timestamp is overlaid on screen. Photographing the screen with another device is traced directly to your PSN.
            </div>
          </div>
        </div>
      </div>

      <div class="slide-footer">
        <span>Kwara State Civil Service Commission &bull; Stage 5 Warnings</span>
        <span>Slide 8 of 13</span>
      </div>
    </section>

    <!-- ========================================== -->
    <!-- SLIDE 9: Stage 6 - Unanswered Check        -->
    <!-- ========================================== -->
    <section class="slide-stage" data-slide="9">
      <div class="slide-header">
        <div class="slide-header-left">
          <img src="/static/images/logo.png" class="slide-header-logo" alt="Logo">
          <div>
            <div class="slide-badge-category">STAGE 6 OF 7</div>
            <div class="slide-title">Incomplete Examination Check Before Submitting</div>
          </div>
        </div>
        <div class="slide-pill">Stage 6</div>
      </div>

      <div class="slide-content">
        <div class="slide-grid-split">
          <div class="screenshot-card" onclick="openLightbox('/static/images/orientation/stage6_unanswered_modal.png')">
            <img src="/static/images/orientation/stage6_unanswered_modal.png" alt="Stage 6 Modal">
            <div class="screenshot-caption">
              <span>🔍 Stage 6: Unanswered Questions Modal</span>
              <span>Click to Enlarge</span>
            </div>
          </div>

          <div class="guide-card">
            <h3>⚠️ Answer All 40 Questions</h3>
            <ul class="guide-list">
              <li><strong>Incomplete Warning:</strong> If you click 'Submit' while any question is still gray, this dialog warns you immediately.</li>
              <li><strong>No Negative Marking:</strong> There is no penalty for an incorrect choice. Blank questions receive zero marks.</li>
              <li><strong>Check the Palette:</strong> Look at the grid for gray squares. Tap on each gray square to answer it.</li>
              <li><strong>Recommended Action:</strong> Click <strong>"Return to Exam & Answer All Questions"</strong> to maximize your score.</li>
            </ul>

            <div class="guide-tip">
              🌟 <strong>Golden Rule:</strong> Never leave any question blank. Turn all 40 squares green before submitting!
            </div>
          </div>
        </div>
      </div>

      <div class="slide-footer">
        <span>Kwara State Civil Service Commission &bull; Stage 6 Incomplete Check</span>
        <span>Slide 9 of 13</span>
      </div>
    </section>

    <!-- ========================================== -->
    <!-- SLIDE 10: Stage 7 - Submission Slip        -->
    <!-- ========================================== -->
    <section class="slide-stage" data-slide="10">
      <div class="slide-header">
        <div class="slide-header-left">
          <img src="/static/images/logo.png" class="slide-header-logo" alt="Logo">
          <div>
            <div class="slide-badge-category">STAGE 7 OF 7</div>
            <div class="slide-title">Official Submission Acknowledgement Slip</div>
          </div>
        </div>
        <div class="slide-pill">Stage 7</div>
      </div>

      <div class="slide-content">
        <div class="slide-grid-split">
          <div class="screenshot-card" onclick="openLightbox('/static/images/orientation/stage7_submission_slip.png')">
            <img src="/static/images/orientation/stage7_submission_slip.png" alt="Stage 7 Slip">
            <div class="screenshot-caption">
              <span>🔍 Stage 7: Submission Acknowledgement Slip</span>
              <span>Click to Enlarge</span>
            </div>
          </div>

          <div class="guide-card">
            <h3>📄 What Your Slip Shows</h3>
            <ul class="guide-list">
              <li><strong>Recorded & Locked:</strong> Official proof that your 40 answers have been saved in the Commission database.</li>
              <li><strong>Audit Details:</strong> Name, PSN, MDA, Grade Level, Paper Code, Time Spent, and exact Timestamp.</li>
              <li><strong>Electronic Reference:</strong> Unique verification tracking number (e.g. <code>Ref: KWS-CSC-SUB-01048-123456</code>).</li>
              <li><strong>Print Slip (PDF):</strong> Click 'Print Acknowledgement Slip' to save or print a copy.</li>
              <li><strong>Session Concluded:</strong> Access code is deactivated. Retakes are strictly prohibited.</li>
            </ul>

            <div class="guide-tip">
              🔒 <strong>Confidentiality Notice:</strong> Notice that no numerical mark appears on this slip. This confirms the Commission's confidential result policy.
            </div>
          </div>
        </div>
      </div>

      <div class="slide-footer">
        <span>Kwara State Civil Service Commission &bull; Stage 7 Slip</span>
        <span>Slide 10 of 13</span>
      </div>
    </section>

    <!-- ========================================== -->
    <!-- SLIDE 11: Result Confidentiality Policy    -->
    <!-- ========================================== -->
    <section class="slide-stage" data-slide="11">
      <div class="slide-header">
        <div class="slide-header-left">
          <img src="/static/images/logo.png" class="slide-header-logo" alt="Logo">
          <div>
            <div class="slide-badge-category">COMMISSION POLICY</div>
            <div class="slide-title">Result Confidentiality & Official MDA Processing</div>
          </div>
        </div>
        <div class="slide-pill">Policy</div>
      </div>

      <div class="slide-content">
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; height: 100%;">
          <div style="background: #f8fafc; border: 1.5px solid #e2e8f0; border-radius: 14px; padding: 24px; display: flex; flex-direction: column;">
            <div style="font-size: 2.4rem; text-align: center; margin-bottom: 10px;">🔒</div>
            <h3 style="font-size: 1.15rem; font-weight: 800; color: #004d40; text-align: center; margin-bottom: 12px;">WORKSTATION PRIVACY</h3>
            <ul class="guide-list" style="font-size: 0.84rem;">
              <li>Scores are NOT displayed on candidate workstations upon submission.</li>
              <li>Eliminates hall distractions, emotional distress, and peer comparison.</li>
              <li>Ensures equal dignity and confidentiality for all ranks and cadres.</li>
            </ul>
          </div>

          <div style="background: #f8fafc; border: 1.5px solid #e2e8f0; border-radius: 14px; padding: 24px; display: flex; flex-direction: column;">
            <div style="font-size: 2.4rem; text-align: center; margin-bottom: 10px;">🏛️</div>
            <h3 style="font-size: 1.15rem; font-weight: 800; color: #004d40; text-align: center; margin-bottom: 12px;">MDA CHANNEL DISPATCH</h3>
            <ul class="guide-list" style="font-size: 0.84rem;">
              <li>Candidate answers and telemetry are encrypted on the central server.</li>
              <li>CBT scores are compiled alongside APER ratings and interview performance.</li>
              <li>Official promotion lists are dispatched formally through your MDA's Director of Personnel Management (DPM).</li>
            </ul>
          </div>

          <div style="background: #f8fafc; border: 1.5px solid #e2e8f0; border-radius: 14px; padding: 24px; display: flex; flex-direction: column;">
            <div style="font-size: 2.4rem; text-align: center; margin-bottom: 10px;">⚖️</div>
            <h3 style="font-size: 1.15rem; font-weight: 800; color: #004d40; text-align: center; margin-bottom: 12px;">AUDIT & INTEGRITY</h3>
            <ul class="guide-list" style="font-size: 0.84rem;">
              <li>Authorized CSC Commissioners review master sheets with telemetry logs.</li>
              <li>Any recorded violation strikes are reviewed by the malpractice committee.</li>
              <li>Guarantees zero leaks and 100% merit-based evaluation.</li>
            </ul>
          </div>
        </div>
      </div>

      <div class="slide-footer">
        <span>Kwara State Civil Service Commission &bull; Result Policy</span>
        <span>Slide 11 of 13</span>
      </div>
    </section>

    <!-- ========================================== -->
    <!-- SLIDE 12: Mobile Device Best Practices     -->
    <!-- ========================================== -->
    <section class="slide-stage" data-slide="12">
      <div class="slide-header">
        <div class="slide-header-left">
          <img src="/static/images/logo.png" class="slide-header-logo" alt="Logo">
          <div>
            <div class="slide-badge-category">TECHNICAL ADVISORY</div>
            <div class="slide-title">Best Practices for Mobile Phone / Tablet Candidates</div>
          </div>
        </div>
        <div class="slide-pill">Mobile Guide</div>
      </div>

      <div class="slide-content">
        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px;">
          <div style="background: #f8fafc; border: 1.5px solid #004d40; border-radius: 12px; padding: 16px;">
            <h4 style="font-size: 0.95rem; font-weight: 800; color: #004d40; margin-bottom: 6px;">🔋 BATTERY PREPARATION</h4>
            <p style="font-size: 0.82rem; color: #334155; line-height: 1.5;">Charge phone to at least 80% before reporting. Avoid power-saving mode which may throttle browser performance.</p>
          </div>

          <div style="background: #fef2f2; border: 1.5px solid #dc2626; border-radius: 12px; padding: 16px;">
            <h4 style="font-size: 0.95rem; font-weight: 800; color: #dc2626; margin-bottom: 6px;">🔕 DO NOT DISTURB (DND)</h4>
            <p style="font-size: 0.82rem; color: #334155; line-height: 1.5;">Turn on 'Do Not Disturb' or airplane mode with Wi-Fi only. Incoming phone calls minimize the browser and cause violation strikes!</p>
          </div>

          <div style="background: #f8fafc; border: 1.5px solid #00796b; border-radius: 12px; padding: 16px;">
            <h4 style="font-size: 0.95rem; font-weight: 800; color: #00796b; margin-bottom: 6px;">📱 LANDSCAPE / WIDE MODE</h4>
            <p style="font-size: 0.82rem; color: #334155; line-height: 1.5;">Rotate phone to landscape mode if you prefer seeing both the question card and 40-question grid simultaneously.</p>
          </div>

          <div style="background: #fffbeb; border: 1.5px solid #d97706; border-radius: 12px; padding: 16px;">
            <h4 style="font-size: 0.95rem; font-weight: 800; color: #d97706; margin-bottom: 6px;">👆 NO 3-FINGER SWIPES</h4>
            <p style="font-size: 0.82rem; color: #334155; line-height: 1.5;">Avoid multi-touch screenshot gestures. The proctoring system intercepts 3-finger swipes as screenshot attempts.</p>
          </div>

          <div style="background: #f8fafc; border: 1.5px solid #004d40; border-radius: 12px; padding: 16px;">
            <h4 style="font-size: 0.95rem; font-weight: 800; color: #004d40; margin-bottom: 6px;">🛡️ SCREEN WAKE-LOCK ACTIVE</h4>
            <p style="font-size: 0.82rem; color: #334155; line-height: 1.5;">The CBT portal keeps your phone screen awake so your device will not dim or sleep during the 20 minutes.</p>
          </div>

          <div style="background: #f8fafc; border: 1.5px solid #00796b; border-radius: 12px; padding: 16px;">
            <h4 style="font-size: 0.95rem; font-weight: 800; color: #00796b; margin-bottom: 6px;">🌐 RECOMMENDED BROWSER</h4>
            <p style="font-size: 0.82rem; color: #334155; line-height: 1.5;">Use standard Google Chrome, Microsoft Edge, or Safari. Avoid mini browsers (like Opera Mini) that compress layouts.</p>
          </div>
        </div>
      </div>

      <div class="slide-footer">
        <span>Kwara State Civil Service Commission &bull; Mobile Advisory</span>
        <span>Slide 12 of 13</span>
      </div>
    </section>

    <!-- ========================================== -->
    <!-- SLIDE 13: Exam Day Checklist               -->
    <!-- ========================================== -->
    <section class="slide-stage" data-slide="13">
      <div class="slide-header">
        <div class="slide-header-left">
          <img src="/static/images/logo.png" class="slide-header-logo" alt="Logo">
          <div>
            <div class="slide-badge-category">EXAM DAY CHECKLIST</div>
            <div class="slide-title">Golden Checklist & Final Instructions</div>
          </div>
        </div>
        <div class="slide-pill">Slide 13 / 13</div>
      </div>

      <div class="slide-content">
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
          <div style="background: #f0fdf4; border: 2px solid #10b981; border-radius: 12px; padding: 20px;">
            <h3 style="font-size: 1.15rem; font-weight: 800; color: #065f46; margin-bottom: 12px;">✅ WHAT YOU MUST DO</h3>
            <ul class="guide-list" style="font-size: 0.85rem;">
              <li>Bring your printed Photocard Slip with your PSN & Code 1.</li>
              <li>Arrive at the CBT center 30 minutes before your batch.</li>
              <li>Verify Name, MDA, and Paper Code before clicking Begin.</li>
              <li>Keep your eye on the 20-minute countdown clock.</li>
              <li>Attempt all 40 questions — turn all boxes GREEN.</li>
              <li>Print or save your Submission Acknowledgement Slip.</li>
            </ul>
          </div>

          <div style="background: #fef2f2; border: 2px solid #dc2626; border-radius: 12px; padding: 20px;">
            <h3 style="font-size: 1.15rem; font-weight: 800; color: #991b1b; margin-bottom: 12px;">❌ WHAT YOU MUST NEVER DO</h3>
            <ul class="guide-list" style="font-size: 0.85rem;">
              <li style="color: #991b1b;">NEVER switch to another browser tab or app (Strike trigger).</li>
              <li style="color: #991b1b;">NEVER attempt screen capture (PrintScreen, Snipping tool).</li>
              <li style="color: #991b1b;">NEVER leave questions blank (each unattempted question is 0).</li>
              <li style="color: #991b1b;">NEVER click 'Submit' prematurely without checking your grid.</li>
              <li style="color: #991b1b;">NEVER expect or demand a numerical score on your screen.</li>
              <li style="color: #991b1b;">NEVER attempt a second login after submitting (Single attempt).</li>
            </ul>
          </div>
        </div>

        <div style="background: #004d40; color: #ffffff; border-radius: 10px; padding: 14px 20px; text-align: center; font-size: 0.95rem; font-weight: 700; margin-top: auto;">
          🌟 The Kwara State Civil Service Commission wishes all promotion candidates success in their evaluation!
        </div>
      </div>

      <div class="slide-footer">
        <span>Kwara State Civil Service Commission &bull; Exam Day Checklist</span>
        <span>Slide 13 of 13</span>
      </div>
    </section>

  </main>

  <!-- Speaker Notes Drawer -->
  <aside id="speaker-drawer" class="speaker-drawer">
    <div class="speaker-drawer-header">
      <span>🎙️ Facilitator Speaker Notes</span>
      <span style="color:#94a3b8; font-weight:400;">(Press S to toggle)</span>
    </div>
    <div id="speaker-notes-content">
      Welcome candidates. Use the navigation buttons below or arrow keys to advance slides.
    </div>
  </aside>

  <!-- Bottom Presentation Controls -->
  <footer class="pres-controls">
    <div class="control-btn-group">
      <button type="button" id="btn-prev" class="btn-ctrl" onclick="prevSlide()">
        <span>◀ Previous</span>
      </button>
      <button type="button" id="btn-next" class="btn-ctrl" onclick="nextSlide()">
        <span>Next ▶</span>
      </button>
      <span class="slide-progress-text" id="slide-counter">Slide 1 of 13</span>
    </div>

    <div class="control-btn-group">
      <select id="slide-jump-select" onchange="goToSlide(parseInt(this.value))" style="background:#1e293b; color:#fff; border:1px solid #475569; padding:6px 10px; border-radius:6px; font-size:0.82rem; font-weight:600;">
        <option value="1">1. Welcome & Title</option>
        <option value="2">2. Core Ground Rules</option>
        <option value="3">3. Stage 1 - Candidate Login</option>
        <option value="4">4. Stage 2 - Bio-Data Verification</option>
        <option value="5">5. Stage 3A - Active Exam Interface</option>
        <option value="6">6. Stage 3B - 40-Question Palette Grid</option>
        <option value="7">7. Stage 4 - Blackout Curtain</option>
        <option value="8">8. Stage 5 - 3-Strike Policy</option>
        <option value="9">9. Stage 6 - Unanswered Questions Check</option>
        <option value="10">10. Stage 7 - Submission Acknowledgement Slip</option>
        <option value="11">11. Result Confidentiality Policy</option>
        <option value="12">12. Mobile Device Best Practices</option>
        <option value="13">13. Golden Exam Day Checklist</option>
      </select>
    </div>
  </footer>

  <!-- Lightbox Modal for Screenshots -->
  <div id="lightbox-modal" class="lightbox-modal" onclick="closeLightbox()">
    <img id="lightbox-img" src="" alt="Enlarged Screenshot">
  </div>

  <script>
    const speakerNotes = {
      1: "FACILITATOR SCRIPT:\\n'Good day, distinguished officers and promotion candidates of the Kwara State Civil Service. Welcome to today's orientation session for the 2026 Promotion Evaluation Computer Based Test. The Commission has structured this digital assessment to ensure merit, transparency, and seamless execution. In the next few minutes, we will walk you through every single screen and button you will encounter, the anti-cheating regulations, and what to expect on your workstation. Please pay close attention to every detail.'",
      2: "FACILITATOR SCRIPT:\\n'Before we examine the screens, remember these four pillars:\\n1. Timing: You have strictly 20 minutes for 40 questions. That is an average of 30 seconds per question.\\n2. Structure: 40 questions, objective multiple choice. Answer every single question.\\n3. Result Policy: Do not expect a score on the computer when you finish. Scores are confidential and delivered to your MDA.\\n4. Anti-cheating: The system detects tab switches and background applications. Three strikes terminate your exam.'",
      3: "FACILITATOR SCRIPT:\\n'Here on Slide 3 is the exact login screen you will see on your computer or mobile screen.\\nLook at your Photocard Slip. In the top right corner, you have your 6-digit PSN and your Code 1.\\nEnter your PSN in the first box. Enter your Code 1 in the second box. Make sure you include any letters and hyphens.\\nThen click Verify & Access Examination. Do not click multiple times—wait 2 seconds for the accreditation window to load.'",
      4: "FACILITATOR SCRIPT:\\n'When you authenticate, this verification pop-up appears.\\nDo NOT rush to click Confirm & Begin. Take 30 seconds to read every field.\\nIs that your name? Is that your PSN? Is that your Ministry? Is that your allocated paper?\\nIf there is any discrepancy whatsoever, raise your hand immediately and inform the supervisor.\\nOnce you click Confirm & Begin Examination, the system locks your paper and starts the countdown.'",
      5: "FACILITATOR SCRIPT:\\n'Now examine Slide 5: this is your examination workspace.\\nAt the top, keep your eye on the timer. It counts down continuously from 20:00.\\nYou do not need to press any Save button. As soon as you click an option, the system marks it as answered.\\nEven if your network disconnects for a second, your selections are saved securely in your browser cache.'",
      6: "FACILITATOR SCRIPT:\\n'Look closely at the right-hand side of your screen: the Question Grid with 40 boxes.\\nRemember these colors:\\n- GREEN means you have answered.\\n- PURPLE means you flagged it for review.\\n- GRAY means you have NOT answered yet.\\nYou do not need to click Next 30 times to get to question 30. Simply tap 30 on the grid!\\nIf you change your mind and want to clear an answer, click Clear Choice.'",
      7: "FACILITATOR SCRIPT:\\n'Candidates, this is a crucial security rule:\\nIf you minimize your browser, switch to WhatsApp, open Google, or try to take a screenshot, your screen will immediately go pitch black as shown on this slide.\\nThe system considers this an unauthorized window blur.\\nClicking back into the screen will resume the exam, but it will register an infraction against you.\\nKeep your focus solely on the CBT window throughout the 20 minutes.'",
      8: "FACILITATOR SCRIPT:\\n'The Civil Service Commission has implemented a strict 3-Strike policy:\\n- Strike 1: You get an official warning pop-up.\\n- Strike 2: You get a final warning in bold red.\\n- Strike 3: The system terminates your test immediately, locks your answers, and submits your paper with a proctor violation flag.\\nDo not risk your promotion. Stay on the examination page until you finish.'",
      9: "FACILITATOR SCRIPT:\\n'Before submitting, the computer performs an automated safety check.\\nIf you have unanswered questions, it will stop you with this warning showing exactly how many you missed.\\nThere is no negative marking in Kwara Civil Service CBT exams! A blank question is a guaranteed zero. An attempted question gives you a chance of scoring.\\nAlways click Return to Exam and attempt all 40 questions.'",
      10: "FACILITATOR SCRIPT:\\n'When you click final submit, this is what appears on your screen: your Submission Acknowledgement Slip.\\nIt provides official proof that your test was successfully recorded.\\nCheck your electronic reference code at the bottom.\\nYou can click Print Acknowledgement Slip to save it as a PDF or print it.\\nOnce you see this slip, your test is safely completed. You may close your browser and exit quietly.'",
      11: "FACILITATOR SCRIPT:\\n'We want to emphasize this policy very clearly:\\nMany candidates ask: Why didn't I see my score when I finished?\\nCivil Service promotion is a holistic evaluation. The CBT score is combined with your Annual Performance Evaluation Report (APER), your seniority, and promotional guidelines.\\nScores are not displayed on workstations to prevent unrest, hall disorder, or premature conclusions.\\nYour official results will reach you through your Ministry, Department, or Agency through the proper administrative channels.'",
      12: "FACILITATOR SCRIPT:\\n'For candidates taking the CBT on mobile devices or tablets, these 6 technical tips are essential:\\nNumber one: Put your phone on Do Not Disturb. If your relative or colleague calls you during the exam, the incoming call overlay minimizes the CBT page, and the system registers a Strike 1 violation!\\nNumber two: Do not attempt 3-finger screenshot gestures. It will trigger a screen blackout.\\nNumber three: Keep your screen clean and use standard Google Chrome or Edge.'",
      13: "FACILITATOR SCRIPT:\\n'To conclude our briefing today:\\nRemember your golden checklist on Slide 13.\\nBe calm, read each question carefully, manage your 20 minutes, answer all 40 questions, and print your acknowledgement slip when you submit.\\nAre there any questions before we take candidates to the practice demo?'"
    };

    let currentSlide = 1;
    const totalSlides = 13;

    function updateSlideView() {
      const slides = document.querySelectorAll('.slide-stage');
      slides.forEach(s => {
        const sNum = parseInt(s.getAttribute('data-slide'));
        if (sNum === currentSlide) {
          s.classList.add('active');
        } else {
          s.classList.remove('active');
        }
      });

      document.getElementById('slide-counter').textContent = `Slide ${currentSlide} of ${totalSlides}`;
      document.getElementById('btn-prev').disabled = (currentSlide === 1);
      document.getElementById('btn-next').disabled = (currentSlide === totalSlides);
      document.getElementById('slide-jump-select').value = currentSlide;

      // Update speaker notes
      const note = speakerNotes[currentSlide] || "No additional notes for this slide.";
      document.getElementById('speaker-notes-content').innerHTML = note.replace(/\\n/g, '<br>');
    }

    function nextSlide() {
      if (currentSlide < totalSlides) {
        currentSlide++;
        updateSlideView();
      }
    }

    function prevSlide() {
      if (currentSlide > 1) {
        currentSlide--;
        updateSlideView();
      }
    }

    function goToSlide(n) {
      if (n >= 1 && n <= totalSlides) {
        currentSlide = n;
        updateSlideView();
      }
    }

    // Keyboard Shortcuts
    window.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'PageDown') {
        e.preventDefault();
        nextSlide();
      } else if (e.key === 'ArrowLeft' || e.key === 'PageUp') {
        e.preventDefault();
        prevSlide();
      } else if (e.key === 'Home') {
        e.preventDefault();
        goToSlide(1);
      } else if (e.key === 'End') {
        e.preventDefault();
        goToSlide(totalSlides);
      } else if (e.key === 's' || e.key === 'S') {
        toggleSpeakerNotes();
      } else if (e.key === 'f' || e.key === 'F') {
        toggleFullscreen();
      }
    });

    function toggleSpeakerNotes() {
      const drawer = document.getElementById('speaker-drawer');
      drawer.classList.toggle('open');
      const isOpen = drawer.classList.contains('open');
      document.getElementById('btn-notes-label').textContent = isOpen ? 'Hide Notes (S)' : 'Speaker Notes (S)';
    }

    function toggleFullscreen() {
      if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen().catch(() => {});
      } else {
        if (document.exitFullscreen) document.exitFullscreen().catch(() => {});
      }
    }

    function openLightbox(src) {
      const modal = document.getElementById('lightbox-modal');
      const img = document.getElementById('lightbox-img');
      img.src = src;
      modal.classList.add('open');
    }

    function closeLightbox() {
      document.getElementById('lightbox-modal').classList.remove('open');
    }

    // Initial setup
    updateSlideView();
  </script>
</body>
</html>
"""

destinations = [
    os.path.abspath("kwara_cbt_app/static/orientation.html"),
    os.path.abspath("public/orientation.html"),
    os.path.abspath("static/orientation.html")
]

for d in destinations:
    with open(d, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Written: {d}")

print("Orientation HTML slide deck generated across all static directories!")
