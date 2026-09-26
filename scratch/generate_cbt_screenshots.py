import os
import subprocess
import time

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
OUTPUT_DIR = os.path.abspath("scratch/orientation_screenshots")
os.makedirs(OUTPUT_DIR, exist_ok=True)

LOGO_URL = "file:///" + os.path.abspath("kwara_cbt_app/static/images/logo.png").replace("\\", "/")
CSS_URL = "file:///" + os.path.abspath("kwara_cbt_app/static/css/style.css").replace("\\", "/")

def get_base_head(title):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{title}</title>
  <link rel="stylesheet" href="{CSS_URL}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
  <style>
    body {{
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      margin: 0;
      padding: 0;
      background: #f1f5f9;
      color: #1e293b;
      -webkit-font-smoothing: antialiased;
    }}
    .demo-header-brand {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}
    .demo-header-brand img {{
      width: 44px;
      height: 44px;
      object-fit: contain;
    }}
    .demo-header-title {{
      font-size: 1.05rem;
      font-weight: 800;
      letter-spacing: -0.01em;
      color: #ffffff;
      line-height: 1.2;
    }}
    .demo-header-sub {{
      font-size: 0.75rem;
      color: #a7f3d0;
      font-weight: 500;
    }}
  </style>
</head>
"""

# STAGE 1: Candidate Portal Login
stage1_html = get_base_head("Stage 1 - Candidate Login") + f"""
<body>
  <header class="header-bar" style="background:#004d40; padding:12px 30px; display:flex; justify-content:space-between; align-items:center;">
    <div class="demo-header-brand">
      <img src="{LOGO_URL}" alt="Logo">
      <div>
        <div class="demo-header-title">KWARA STATE CIVIL SERVICE COMMISSION</div>
        <div class="demo-header-sub">2026 Promotion Evaluation CBT Examination Portal</div>
      </div>
    </div>
    <div style="background:#00796b; color:#fff; padding:6px 14px; border-radius:20px; font-size:0.8rem; font-weight:700; display:flex; align-items:center; gap:6px;">
      <span style="width:8px; height:8px; border-radius:50%; background:#10b981; display:inline-block;"></span>
      PORTAL STATUS: ACTIVE & ACCREDITATION OPEN
    </div>
  </header>

  <main style="max-width:960px; margin:36px auto; padding:0 20px;">
    <!-- Welcome Notification Banner -->
    <div style="background:#ecfdf5; border:1.5px solid #a7f3d0; border-radius:12px; padding:14px 20px; margin-bottom:24px; display:flex; align-items:center; gap:12px;">
      <span style="font-size:1.6rem;">📢</span>
      <div style="font-size:0.88rem; color:#065f46; line-height:1.4;">
        <strong>Welcome, Promotion Candidate!</strong> Please enter your Public Service Number (PSN) and the <strong>Code 1</strong> printed on your official Photocard Registration Slip to access your allocated examination paper.
      </div>
    </div>

    <div style="display:grid; grid-template-columns: 1.3fr 1fr; gap:24px; align-items:start;">
      <!-- Login Card -->
      <div style="background:#fff; border-radius:16px; padding:32px; box-shadow:0 10px 25px rgba(0,0,0,0.06); border:1px solid #e2e8f0;">
        <div style="display:flex; align-items:center; gap:10px; margin-bottom:18px;">
          <div style="background:#e0f2f1; color:#004d40; width:40px; height:40px; border-radius:10px; display:flex; align-items:center; justify-content:center; font-size:1.3rem;">🔑</div>
          <div>
            <h2 style="font-size:1.25rem; font-weight:800; color:#0f172a; margin:0;">Candidate Accreditation</h2>
            <p style="font-size:0.82rem; color:#64748b; margin:2px 0 0 0;">Enter your login credentials from your examination slip</p>
          </div>
        </div>

        <form style="display:flex; flex-direction:column; gap:18px;">
          <div>
            <label style="display:block; font-size:0.82rem; font-weight:700; color:#334155; margin-bottom:6px;">PUBLIC SERVICE NUMBER (PSN)</label>
            <div style="position:relative;">
              <input type="text" value="123456" readonly style="width:100%; padding:13px 14px; font-size:1rem; font-weight:600; border:2px solid #004d40; border-radius:8px; background:#f8fafc; color:#0f172a;">
              <span style="position:absolute; right:12px; top:12px; color:#10b981; font-weight:700; font-size:1.1rem;">✓</span>
            </div>
            <span style="font-size:0.75rem; color:#64748b; margin-top:4px; display:block;">Your 6-digit Kwara State civil service staff number</span>
          </div>

          <div>
            <label style="display:block; font-size:0.82rem; font-weight:700; color:#334155; margin-bottom:6px;">OFFICIAL ACCESS CODE (CODE 1)</label>
            <div style="position:relative;">
              <input type="text" value="B-10294" readonly style="width:100%; padding:13px 14px; font-size:1rem; font-weight:700; border:2px solid #004d40; border-radius:8px; background:#f8fafc; color:#0f172a; letter-spacing:0.05em;">
              <span style="position:absolute; right:12px; top:12px; color:#10b981; font-weight:700; font-size:1.1rem;">✓</span>
            </div>
            <span style="font-size:0.75rem; color:#64748b; margin-top:4px; display:block;">As clearly printed on your Photocard Registration Slip</span>
          </div>

          <button type="button" style="background:#004d40; color:#fff; border:none; padding:15px; border-radius:8px; font-size:1rem; font-weight:700; cursor:pointer; display:flex; align-items:center; justify-content:center; gap:8px; margin-top:8px; box-shadow:0 4px 12px rgba(0,77,64,0.3);">
            <span>Verify & Access Examination</span>
            <span>➔</span>
          </button>
        </form>
      </div>

      <!-- Quick Rules Aside -->
      <div style="background:#fff; border-radius:16px; padding:26px; border:1px solid #e2e8f0; box-shadow:0 4px 15px rgba(0,0,0,0.03);">
        <h3 style="font-size:0.98rem; font-weight:800; color:#004d40; margin-top:0; margin-bottom:14px; display:flex; align-items:center; gap:8px;">
          <span>📋</span> Examination Guidelines
        </h3>
        <ul style="margin:0; padding-left:18px; font-size:0.82rem; color:#334155; line-height:1.7; display:flex; flex-direction:column; gap:8px;">
          <li><strong>Total Questions:</strong> Exactly 40 multiple-choice questions.</li>
          <li><strong>Exam Duration:</strong> 20 minutes strictly with live countdown.</li>
          <li><strong>Single Attempt:</strong> Each candidate can only take the test once.</li>
          <li><strong>Proctored Environment:</strong> Switching apps or tabs triggers automated strikes.</li>
          <li><strong>Score Privacy:</strong> Scores are confidential and processed directly by your MDA.</li>
        </ul>
        <div style="margin-top:20px; background:#fffbeb; border:1px solid #fde68a; border-radius:8px; padding:10px 12px; font-size:0.75rem; color:#92400e; font-weight:600;">
          💡 Tip: Ensure your mobile phone battery is well charged before logging in.
        </div>
      </div>
    </div>
  </main>
</body>
</html>"""

# STAGE 2: Candidate Bio-Data & Slip Verification Modal
stage2_html = get_base_head("Stage 2 - Verification Modal") + f"""
<body style="background:#cbd5e1; overflow:hidden;">
  <!-- Mock Background -->
  <header class="header-bar" style="background:#004d40; padding:12px 30px; display:flex; justify-content:space-between; align-items:center; filter:blur(2px);">
    <div class="demo-header-brand">
      <img src="{LOGO_URL}" alt="Logo">
      <div class="demo-header-title">KWARA STATE CIVIL SERVICE COMMISSION</div>
    </div>
  </header>

  <!-- Modal Backdrop -->
  <div style="position:fixed; inset:0; background:rgba(15,23,42,0.7); display:flex; align-items:center; justify-content:center; z-index:1000; padding:20px;">
    <!-- Modal Card -->
    <div style="background:#ffffff; width:100%; max-width:680px; border-radius:18px; box-shadow:0 25px 50px -12px rgba(0,0,0,0.35); overflow:hidden; border:1px solid #e2e8f0; animation:pop 0.3s ease;">
      <!-- Modal Header -->
      <div style="background:linear-gradient(135deg, #004d40 0%, #00796b 100%); color:#fff; padding:22px 28px; display:flex; align-items:center; gap:14px;">
        <div style="background:#ffffff; width:48px; height:48px; border-radius:12px; display:flex; align-items:center; justify-content:center; padding:4px;">
          <img src="{LOGO_URL}" alt="Logo" style="width:100%; height:100%; object-fit:contain;">
        </div>
        <div>
          <h2 style="font-size:1.2rem; font-weight:800; margin:0; letter-spacing:-0.01em;">CANDIDATE ACCREDITATION VERIFICATION</h2>
          <p style="font-size:0.78rem; color:#e0f2f1; margin:3px 0 0 0;">Please carefully verify that all details below match your Photocard Slip</p>
        </div>
      </div>

      <!-- Modal Body -->
      <div style="padding:26px 28px;">
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:14px; background:#f8fafc; border:1px solid #e2e8f0; border-radius:12px; padding:18px; margin-bottom:20px;">
          <div>
            <div style="font-size:0.72rem; font-weight:700; color:#64748b; text-transform:uppercase;">Candidate Full Name</div>
            <div style="font-size:0.95rem; font-weight:800; color:#0f172a; margin-top:2px;">FATIMAH BOLA AHMED</div>
          </div>
          <div>
            <div style="font-size:0.72rem; font-weight:700; color:#64748b; text-transform:uppercase;">Public Service Number (PSN)</div>
            <div style="font-size:0.95rem; font-weight:800; color:#004d40; margin-top:2px;">123456</div>
          </div>
          <div>
            <div style="font-size:0.72rem; font-weight:700; color:#64748b; text-transform:uppercase;">Ministry / Department / Agency</div>
            <div style="font-size:0.85rem; font-weight:700; color:#334155; margin-top:2px;">Ministry of Agriculture & Rural Dev.</div>
          </div>
          <div>
            <div style="font-size:0.72rem; font-weight:700; color:#64748b; text-transform:uppercase;">Proposed Grade Level</div>
            <div style="font-size:0.85rem; font-weight:700; color:#334155; margin-top:2px;">GL 12 (Principal Officer)</div>
          </div>
          <div>
            <div style="font-size:0.72rem; font-weight:700; color:#64748b; text-transform:uppercase;">Allocated Examination Paper</div>
            <div style="font-size:0.85rem; font-weight:800; color:#b45309; margin-top:2px;">MARD-GL12-B (Professional)</div>
          </div>
          <div>
            <div style="font-size:0.72rem; font-weight:700; color:#64748b; text-transform:uppercase;">Batch & Exam Duration</div>
            <div style="font-size:0.85rem; font-weight:800; color:#059669; margin-top:2px;">Batch B • 40 Questions / 20 Mins</div>
          </div>
        </div>

        <div style="background:#fef2f2; border:1px solid #fecaca; border-radius:8px; padding:12px 14px; font-size:0.78rem; color:#991b1b; line-height:1.4; margin-bottom:22px; display:flex; gap:10px; align-items:start;">
          <span style="font-size:1.1rem;">⚠️</span>
          <div>
            <strong>Important Notice:</strong> Once you click <em>"Confirm & Begin Examination"</em>, your 20-minute countdown will start immediately. Do not switch away from this browser window or attempt screen capture.
          </div>
        </div>

        <!-- Buttons -->
        <div style="display:flex; justify-content:space-between; gap:14px;">
          <button type="button" style="flex:1; background:#f1f5f9; color:#475569; border:1px solid #cbd5e1; padding:14px; border-radius:8px; font-size:0.88rem; font-weight:700; cursor:pointer;">
            ❌ Report Discrepancy
          </button>
          <button type="button" style="flex:1.4; background:#004d40; color:#ffffff; border:none; padding:14px; border-radius:8px; font-size:0.95rem; font-weight:800; cursor:pointer; box-shadow:0 4px 14px rgba(0,77,64,0.3); display:flex; align-items:center; justify-content:center; gap:8px;">
            <span>✅ Confirm & Begin Examination</span>
            <span>➔</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</body>
</html>"""

# STAGE 3: The Active Examination Interface & Navigation
stage3_html = get_base_head("Stage 3 - Active Examination Screen") + f"""
<body>
  <!-- Exam Top Header -->
  <header style="background:#004d40; color:#fff; padding:10px 24px; display:flex; justify-content:space-between; align-items:center; box-shadow:0 2px 10px rgba(0,0,0,0.15);">
    <div style="display:flex; align-items:center; gap:14px;">
      <div style="width:42px; height:42px; border-radius:50%; background:#fff; display:flex; align-items:center; justify-content:center; font-size:1.2rem; font-weight:800; color:#004d40; border:2px solid #a7f3d0;">
        FB
      </div>
      <div>
        <div style="font-size:0.95rem; font-weight:800; color:#fff;">FATIMAH BOLA AHMED &bull; PSN: 123456</div>
        <div style="font-size:0.75rem; color:#a7f3d0; font-weight:600;">Paper: MARD-GL12-B &bull; Ministry of Agriculture & Rural Dev.</div>
      </div>
    </div>

    <!-- Timer and Shield -->
    <div style="display:flex; align-items:center; gap:16px;">
      <div style="background:#00251a; border:1.5px solid #059669; padding:6px 14px; border-radius:24px; display:flex; align-items:center; gap:8px;">
        <span style="font-size:1.1rem;">⏱️</span>
        <div>
          <span style="font-size:0.65rem; color:#a7f3d0; display:block; text-transform:uppercase; font-weight:700;">Time Remaining</span>
          <span style="font-size:1.15rem; font-weight:900; color:#34d399; font-variant-numeric:tabular-nums; letter-spacing:0.04em;">14:32</span>
        </div>
      </div>
      <div style="background:rgba(255,255,255,0.1); border:1px solid rgba(255,255,255,0.2); border-radius:20px; padding:6px 12px; font-size:0.75rem; font-weight:700; display:flex; align-items:center; gap:6px;">
        <span>🛡️</span> PROCTOR SECURE
      </div>
    </div>
  </header>

  <!-- Main Exam Body -->
  <main style="max-width:1200px; margin:22px auto; padding:0 20px; display:grid; grid-template-columns: 2fr 1fr; gap:22px; align-items:start;">
    <!-- Left Column: Question Card -->
    <div style="background:#ffffff; border-radius:14px; padding:26px; border:1px solid #e2e8f0; box-shadow:0 4px 15px rgba(0,0,0,0.04);">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:18px; border-bottom:1.5px solid #f1f5f9; padding-bottom:12px;">
        <span style="font-size:0.85rem; font-weight:800; color:#004d40; background:#e0f2f1; padding:4px 12px; border-radius:6px;">
          QUESTION 14 OF 40
        </span>
        <span style="font-size:0.8rem; color:#64748b; font-weight:600;">Single Choice &bull; 1 Mark</span>
      </div>

      <div style="font-size:1.08rem; font-weight:700; color:#1e293b; line-height:1.55; margin-bottom:24px;">
        Which of the following official store accounting documents is strictly required to verify physical receipt and custody of government agricultural machinery before entry into the asset register?
      </div>

      <!-- Options List -->
      <div style="display:flex; flex-direction:column; gap:12px; margin-bottom:28px;">
        <label style="display:flex; align-items:center; gap:14px; padding:14px 16px; border:1.5px solid #e2e8f0; border-radius:10px; cursor:pointer; background:#fff; transition:all 0.2s;">
          <input type="radio" name="opt" style="width:18px; height:18px;">
          <span style="font-weight:700; color:#64748b; font-size:0.95rem;">A.</span>
          <span style="font-size:0.92rem; color:#334155; font-weight:500;">Local Purchase Order (LPO)</span>
        </label>

        <!-- Selected Option (B) -->
        <label style="display:flex; align-items:center; gap:14px; padding:14px 16px; border:2px solid #004d40; border-radius:10px; cursor:pointer; background:#f0fdf4; box-shadow:0 2px 8px rgba(0,77,64,0.08);">
          <input type="radio" name="opt" checked style="width:18px; height:18px; accent-color:#004d40;">
          <span style="font-weight:800; color:#004d40; font-size:0.95rem;">B.</span>
          <span style="font-size:0.92rem; color:#004d40; font-weight:700;">Store Receipt Voucher (SRV)</span>
          <span style="margin-left:auto; background:#10b981; color:#fff; font-size:0.7rem; font-weight:800; padding:2px 8px; border-radius:10px;">SELECTED</span>
        </label>

        <label style="display:flex; align-items:center; gap:14px; padding:14px 16px; border:1.5px solid #e2e8f0; border-radius:10px; cursor:pointer; background:#fff;">
          <input type="radio" name="opt" style="width:18px; height:18px;">
          <span style="font-weight:700; color:#64748b; font-size:0.95rem;">C.</span>
          <span style="font-size:0.92rem; color:#334155; font-weight:500;">Departmental Vote Book Entry</span>
        </label>

        <label style="display:flex; align-items:center; gap:14px; padding:14px 16px; border:1.5px solid #e2e8f0; border-radius:10px; cursor:pointer; background:#fff;">
          <input type="radio" name="opt" style="width:18px; height:18px;">
          <span style="font-weight:700; color:#64748b; font-size:0.95rem;">D.</span>
          <span style="font-size:0.92rem; color:#334155; font-weight:500;">Treasury Form 15 Cash Receipt</span>
        </label>
      </div>

      <!-- Navigation & Control Buttons -->
      <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px; border-top:1.5px solid #f1f5f9; padding-top:18px;">
        <div style="display:flex; gap:10px;">
          <button type="button" style="background:#f1f5f9; color:#475569; border:1px solid #cbd5e1; padding:10px 16px; border-radius:8px; font-weight:700; font-size:0.85rem; cursor:pointer;">
            ◀ Previous
          </button>
          <button type="button" style="background:#004d40; color:#fff; border:none; padding:10px 20px; border-radius:8px; font-weight:700; font-size:0.85rem; cursor:pointer; box-shadow:0 2px 6px rgba(0,77,64,0.2);">
            Next Question ▶
          </button>
        </div>

        <div style="display:flex; gap:10px;">
          <button type="button" style="background:#f5f3ff; color:#6d28d9; border:1.5px solid #ddd6fe; padding:10px 14px; border-radius:8px; font-weight:700; font-size:0.82rem; cursor:pointer;">
            ⚑ Flag for Review
          </button>
          <button type="button" style="background:#fef2f2; color:#b91c1c; border:1.5px solid #fecaca; padding:10px 14px; border-radius:8px; font-weight:700; font-size:0.82rem; cursor:pointer;">
            ✖ Clear Choice
          </button>
        </div>
      </div>
    </div>

    <!-- Right Column: Question Grid (40 Questions) -->
    <div style="background:#ffffff; border-radius:14px; padding:22px; border:1px solid #e2e8f0; box-shadow:0 4px 15px rgba(0,0,0,0.04);">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;">
        <h3 style="font-size:0.95rem; font-weight:800; color:#0f172a; margin:0;">Question Grid (40)</h3>
        <span style="font-size:0.75rem; font-weight:700; color:#059669; background:#ecfdf5; padding:2px 8px; border-radius:12px;">13 / 40 Done</span>
      </div>

      <!-- 40 Questions Grid (8 cols x 5 rows) -->
      <div style="display:grid; grid-template-columns: repeat(8, 1fr); gap:6px; margin-bottom:16px;">
        <!-- Q1 to Q13 Answered (Green) -->
        <button style="aspect-ratio:1; background:#10b981; color:#fff; border:none; border-radius:6px; font-weight:800; font-size:0.8rem;">1</button>
        <button style="aspect-ratio:1; background:#10b981; color:#fff; border:none; border-radius:6px; font-weight:800; font-size:0.8rem;">2</button>
        <button style="aspect-ratio:1; background:#10b981; color:#fff; border:none; border-radius:6px; font-weight:800; font-size:0.8rem;">3</button>
        <button style="aspect-ratio:1; background:#10b981; color:#fff; border:none; border-radius:6px; font-weight:800; font-size:0.8rem;">4</button>
        <button style="aspect-ratio:1; background:#10b981; color:#fff; border:none; border-radius:6px; font-weight:800; font-size:0.8rem;">5</button>
        <button style="aspect-ratio:1; background:#10b981; color:#fff; border:none; border-radius:6px; font-weight:800; font-size:0.8rem;">6</button>
        <button style="aspect-ratio:1; background:#10b981; color:#fff; border:none; border-radius:6px; font-weight:800; font-size:0.8rem;">7</button>
        <button style="aspect-ratio:1; background:#10b981; color:#fff; border:none; border-radius:6px; font-weight:800; font-size:0.8rem;">8</button>
        <button style="aspect-ratio:1; background:#10b981; color:#fff; border:none; border-radius:6px; font-weight:800; font-size:0.8rem;">9</button>
        <button style="aspect-ratio:1; background:#10b981; color:#fff; border:none; border-radius:6px; font-weight:800; font-size:0.8rem;">10</button>
        <button style="aspect-ratio:1; background:#10b981; color:#fff; border:none; border-radius:6px; font-weight:800; font-size:0.8rem;">11</button>
        <button style="aspect-ratio:1; background:#10b981; color:#fff; border:none; border-radius:6px; font-weight:800; font-size:0.8rem;">12</button>
        <button style="aspect-ratio:1; background:#10b981; color:#fff; border:none; border-radius:6px; font-weight:800; font-size:0.8rem;">13</button>
        <!-- Q14 Current Active (Green with bold ring) -->
        <button style="aspect-ratio:1; background:#10b981; color:#fff; border:3px solid #004d40; border-radius:6px; font-weight:900; font-size:0.85rem; box-shadow:0 0 0 2px #34d399;">14</button>
        <!-- Q15 Flagged for Review (Purple) -->
        <button style="aspect-ratio:1; background:#8b5cf6; color:#fff; border:none; border-radius:6px; font-weight:800; font-size:0.8rem;">15</button>
        <!-- Q16-Q40 Unanswered (Gray) -->
        <button style="aspect-ratio:1; background:#f1f5f9; color:#64748b; border:1px solid #cbd5e1; border-radius:6px; font-weight:700; font-size:0.8rem;">16</button>
        <button style="aspect-ratio:1; background:#f1f5f9; color:#64748b; border:1px solid #cbd5e1; border-radius:6px; font-weight:700; font-size:0.8rem;">17</button>
        <button style="aspect-ratio:1; background:#f1f5f9; color:#64748b; border:1px solid #cbd5e1; border-radius:6px; font-weight:700; font-size:0.8rem;">18</button>
        <button style="aspect-ratio:1; background:#f1f5f9; color:#64748b; border:1px solid #cbd5e1; border-radius:6px; font-weight:700; font-size:0.8rem;">19</button>
        <button style="aspect-ratio:1; background:#f1f5f9; color:#64748b; border:1px solid #cbd5e1; border-radius:6px; font-weight:700; font-size:0.8rem;">20</button>
        <button style="aspect-ratio:1; background:#f1f5f9; color:#64748b; border:1px solid #cbd5e1; border-radius:6px; font-weight:700; font-size:0.8rem;">21</button>
        <button style="aspect-ratio:1; background:#f1f5f9; color:#64748b; border:1px solid #cbd5e1; border-radius:6px; font-weight:700; font-size:0.8rem;">22</button>
        <button style="aspect-ratio:1; background:#f1f5f9; color:#64748b; border:1px solid #cbd5e1; border-radius:6px; font-weight:700; font-size:0.8rem;">23</button>
        <button style="aspect-ratio:1; background:#f1f5f9; color:#64748b; border:1px solid #cbd5e1; border-radius:6px; font-weight:700; font-size:0.8rem;">24</button>
        <button style="aspect-ratio:1; background:#f1f5f9; color:#64748b; border:1px solid #cbd5e1; border-radius:6px; font-weight:700; font-size:0.8rem;">25</button>
        <button style="aspect-ratio:1; background:#f1f5f9; color:#64748b; border:1px solid #cbd5e1; border-radius:6px; font-weight:700; font-size:0.8rem;">26</button>
        <button style="aspect-ratio:1; background:#f1f5f9; color:#64748b; border:1px solid #cbd5e1; border-radius:6px; font-weight:700; font-size:0.8rem;">27</button>
        <button style="aspect-ratio:1; background:#f1f5f9; color:#64748b; border:1px solid #cbd5e1; border-radius:6px; font-weight:700; font-size:0.8rem;">28</button>
        <button style="aspect-ratio:1; background:#f1f5f9; color:#64748b; border:1px solid #cbd5e1; border-radius:6px; font-weight:700; font-size:0.8rem;">29</button>
        <button style="aspect-ratio:1; background:#f1f5f9; color:#64748b; border:1px solid #cbd5e1; border-radius:6px; font-weight:700; font-size:0.8rem;">30</button>
        <button style="aspect-ratio:1; background:#f1f5f9; color:#64748b; border:1px solid #cbd5e1; border-radius:6px; font-weight:700; font-size:0.8rem;">31</button>
        <button style="aspect-ratio:1; background:#f1f5f9; color:#64748b; border:1px solid #cbd5e1; border-radius:6px; font-weight:700; font-size:0.8rem;">32</button>
        <button style="aspect-ratio:1; background:#f1f5f9; color:#64748b; border:1px solid #cbd5e1; border-radius:6px; font-weight:700; font-size:0.8rem;">33</button>
        <button style="aspect-ratio:1; background:#f1f5f9; color:#64748b; border:1px solid #cbd5e1; border-radius:6px; font-weight:700; font-size:0.8rem;">34</button>
        <button style="aspect-ratio:1; background:#f1f5f9; color:#64748b; border:1px solid #cbd5e1; border-radius:6px; font-weight:700; font-size:0.8rem;">35</button>
        <button style="aspect-ratio:1; background:#f1f5f9; color:#64748b; border:1px solid #cbd5e1; border-radius:6px; font-weight:700; font-size:0.8rem;">36</button>
        <button style="aspect-ratio:1; background:#f1f5f9; color:#64748b; border:1px solid #cbd5e1; border-radius:6px; font-weight:700; font-size:0.8rem;">37</button>
        <button style="aspect-ratio:1; background:#f1f5f9; color:#64748b; border:1px solid #cbd5e1; border-radius:6px; font-weight:700; font-size:0.8rem;">38</button>
        <button style="aspect-ratio:1; background:#f1f5f9; color:#64748b; border:1px solid #cbd5e1; border-radius:6px; font-weight:700; font-size:0.8rem;">39</button>
        <button style="aspect-ratio:1; background:#f1f5f9; color:#64748b; border:1px solid #cbd5e1; border-radius:6px; font-weight:700; font-size:0.8rem;">40</button>
      </div>

      <!-- Color Legend -->
      <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:10px; font-size:0.75rem; display:flex; flex-direction:column; gap:6px; margin-bottom:18px;">
        <div style="display:flex; align-items:center; gap:8px;">
          <span style="width:14px; height:14px; border-radius:3px; background:#10b981; display:inline-block;"></span>
          <strong style="color:#065f46;">Green:</strong> Answered (13)
        </div>
        <div style="display:flex; align-items:center; gap:8px;">
          <span style="width:14px; height:14px; border-radius:3px; background:#8b5cf6; display:inline-block;"></span>
          <strong style="color:#5b21b6;">Purple:</strong> Flagged for Review (1)
        </div>
        <div style="display:flex; align-items:center; gap:8px;">
          <span style="width:14px; height:14px; border-radius:3px; background:#f1f5f9; border:1px solid #cbd5e1; display:inline-block;"></span>
          <strong style="color:#475569;">Gray:</strong> Unanswered (26)
        </div>
      </div>

      <!-- Submit Exam Button -->
      <button type="button" style="width:100%; background:#b91c1c; color:#fff; border:none; padding:12px; border-radius:8px; font-weight:800; font-size:0.9rem; cursor:pointer; display:flex; align-items:center; justify-content:center; gap:8px; box-shadow:0 3px 10px rgba(185,28,28,0.25);">
        <span>🔒 Finalize & Submit Exam</span>
      </button>
    </div>
  </main>
</body>
</html>"""

# STAGE 4: Proctored Security Blackout Curtain
stage4_html = get_base_head("Stage 4 - Proctored Security Blackout Curtain") + f"""
<body style="background:#090d16; color:#ffffff; overflow:hidden;">
  <!-- Blackout Screen Overlay -->
  <div style="position:fixed; inset:0; background:rgba(3, 7, 18, 0.98); display:flex; align-items:center; justify-content:center; flex-direction:column; text-align:center; padding:24px; z-index:99999;">
    <!-- Siren / Warning Emblem -->
    <div style="width:84px; height:84px; border-radius:50%; background:#7f1d1d; border:3px solid #ef4444; display:flex; align-items:center; justify-content:center; font-size:2.8rem; margin-bottom:20px; box-shadow:0 0 40px rgba(239,68,68,0.5);">
      🛡️
    </div>

    <div style="background:#450a0a; color:#fca5a5; border:1.5px solid #ef4444; padding:6px 18px; border-radius:20px; font-size:0.85rem; font-weight:800; letter-spacing:0.06em; text-transform:uppercase; margin-bottom:16px;">
      ⚠️ SECURITY CURTAIN ACTIVE &bull; EXAM WINDOW BLURRED
    </div>

    <h1 style="font-size:2rem; font-weight:900; margin:0 0 14px 0; color:#ffffff; max-width:650px; letter-spacing:-0.02em;">
      UNAUTHORIZED WINDOW FOCUS LOST
    </h1>

    <p style="font-size:1.05rem; color:#cbd5e1; max-width:620px; line-height:1.6; margin:0 0 28px 0;">
      You have navigated away from the active CBT examination interface.<br>
      Switching to another browser tab, opening applications, minimizing the browser, or answering background calls is <strong>STRICTLY PROHIBITED</strong>.
    </p>

    <div style="background:#1e293b; border:1px solid #334155; border-radius:12px; padding:16px 24px; max-width:520px; text-align:left; margin-bottom:28px;">
      <div style="font-size:0.82rem; font-weight:700; color:#f59e0b; margin-bottom:6px;">PROCTORING TELEMETRY ALERT:</div>
      <div style="font-size:0.8rem; color:#94a3b8; line-height:1.5;">
        &bull; Event: <code style="color:#38bdf8;">window.blur / visibilitychange:hidden</code><br>
        &bull; Forensic Candidate ID: <strong>DEMO-PSN-123456</strong><br>
        &bull; Action: Returning to this window will trigger an official strike warning.
      </div>
    </div>

    <div style="background:#004d40; color:#a7f3d0; border:1px solid #059669; padding:12px 28px; border-radius:30px; font-weight:800; font-size:0.95rem; display:flex; align-items:center; gap:8px;">
      <span>👉 Click anywhere on this screen to return to your examination</span>
    </div>
  </div>
</body>
</html>"""

# STAGE 5: Security Violation Warning Dialogs (3-Strike System)
stage5_html = get_base_head("Stage 5 - Security Violation Warning") + f"""
<body style="background:#0f172a; overflow:hidden;">
  <!-- Modal Dialog -->
  <div style="position:fixed; inset:0; background:rgba(0,0,0,0.85); display:flex; align-items:center; justify-content:center; padding:20px; z-index:1000;">
    <div style="background:#ffffff; width:100%; max-width:600px; border-radius:16px; box-shadow:0 25px 50px -12px rgba(0,0,0,0.5); overflow:hidden; border:2px solid #dc2626;">
      <!-- Header -->
      <div style="background:#dc2626; color:#fff; padding:20px 24px; display:flex; align-items:center; justify-content:space-between;">
        <div style="display:flex; align-items:center; gap:12px;">
          <span style="font-size:1.8rem;">🚨</span>
          <div>
            <h2 style="font-size:1.2rem; font-weight:900; margin:0; letter-spacing:0.02em;">DEMO / CBT SECURITY WARNING</h2>
            <span style="font-size:0.75rem; color:#fee2e2; font-weight:600;">OFFICIAL INFRACTION LOGGED</span>
          </div>
        </div>
        <div style="background:#ffffff; color:#dc2626; font-size:0.85rem; font-weight:900; padding:4px 12px; border-radius:20px;">
          STRIKE 1 OF 3
        </div>
      </div>

      <!-- Body -->
      <div style="padding:24px 26px;">
        <div style="background:#fef2f2; border:1.5px solid #fecaca; border-radius:10px; padding:16px; margin-bottom:20px;">
          <div style="font-size:0.95rem; font-weight:800; color:#991b1b; margin-bottom:6px;">
            Unauthorized Navigation Detected
          </div>
          <div style="font-size:0.85rem; color:#7f1d1d; line-height:1.5;">
            You attempted to exit or switch away from the examination window (<strong>Window Blur / Tab Switch</strong>).
          </div>
        </div>

        <div style="font-size:0.88rem; color:#334155; line-height:1.6; margin-bottom:20px;">
          The Kwara State Civil Service Commission CBT environment is strictly proctored.
          <ul style="margin:8px 0 0 0; padding-left:20px; font-size:0.82rem; color:#475569;">
            <li><strong>Strike 1 (Current):</strong> Formal warning recorded against your candidate file.</li>
            <li><strong>Strike 2:</strong> Final warning before automatic disqualification.</li>
            <li><strong>Strike 3:</strong> <strong>Immediate termination</strong> and automatic submission of your paper.</li>
          </ul>
        </div>

        <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:10px 14px; font-size:0.78rem; color:#64748b; margin-bottom:22px;">
          Candidate PSN: <strong>123456</strong> &bull; Incident Timestamp: <strong>10:08:24 AM</strong> &bull; Client Watermark: <strong>Active</strong>
        </div>

        <!-- Action -->
        <button type="button" style="width:100%; background:#004d40; color:#fff; border:none; padding:14px; border-radius:8px; font-size:0.95rem; font-weight:800; cursor:pointer; display:flex; align-items:center; justify-content:center; gap:8px; box-shadow:0 4px 14px rgba(0,77,64,0.3);">
          <span>🛡️ I Understand - Return to Examination</span>
        </button>
      </div>
    </div>
  </div>
</body>
</html>"""

# STAGE 6: Incomplete / Unanswered Warning Dialog
stage6_html = get_base_head("Stage 6 - Incomplete Examination Warning") + f"""
<body style="background:#0f172a; overflow:hidden;">
  <!-- Modal Dialog -->
  <div style="position:fixed; inset:0; background:rgba(0,0,0,0.8); display:flex; align-items:center; justify-content:center; padding:20px; z-index:1000;">
    <div style="background:#ffffff; width:100%; max-width:580px; border-radius:16px; box-shadow:0 25px 50px -12px rgba(0,0,0,0.5); overflow:hidden; border:2px solid #f59e0b;">
      <!-- Header -->
      <div style="background:#f59e0b; color:#000; padding:18px 24px; display:flex; align-items:center; justify-content:space-between;">
        <div style="display:flex; align-items:center; gap:12px;">
          <span style="font-size:1.8rem;">⚠️</span>
          <div>
            <h2 style="font-size:1.2rem; font-weight:900; margin:0; letter-spacing:-0.01em;">UNANSWERED QUESTIONS DETECTED</h2>
            <span style="font-size:0.75rem; color:#78350f; font-weight:700;">CONFIRMATION REQUIRED BEFORE SUBMITTING</span>
          </div>
        </div>
        <div style="background:#78350f; color:#ffffff; font-size:0.8rem; font-weight:900; padding:4px 10px; border-radius:20px;">
          12 REMAINING
        </div>
      </div>

      <!-- Body -->
      <div style="padding:24px 26px;">
        <div style="text-align:center; margin-bottom:20px;">
          <div style="font-size:2.8rem; font-weight:900; color:#0f172a; margin-bottom:4px;">
            28 <span style="font-size:1.4rem; color:#64748b; font-weight:600;">/ 40 Answered</span>
          </div>
          <div style="font-size:0.88rem; color:#b45309; font-weight:700;">
            You still have 12 unanswered questions on your examination paper!
          </div>
        </div>

        <div style="background:#fffbeb; border:1px solid #fde68a; border-radius:10px; padding:14px 16px; font-size:0.82rem; color:#92400e; line-height:1.5; margin-bottom:22px;">
          <strong>Important Guidance:</strong> Every unattempted question earns zero marks. You still have time left on your countdown clock. It is strongly advised that you review the question grid and select an answer for all 40 questions.
        </div>

        <!-- Buttons -->
        <div style="display:flex; flex-direction:column; gap:10px;">
          <button type="button" style="background:#004d40; color:#ffffff; border:none; padding:14px; border-radius:8px; font-size:0.95rem; font-weight:800; cursor:pointer; box-shadow:0 4px 12px rgba(0,77,64,0.3); display:flex; align-items:center; justify-content:center; gap:8px;">
            <span>◀ Return to Exam & Answer All Questions (Recommended)</span>
          </button>
          <button type="button" style="background:#fff; color:#b91c1c; border:1.5px solid #fecaca; padding:11px; border-radius:8px; font-size:0.82rem; font-weight:700; cursor:pointer;">
            Submit Incomplete Examination Anyway
          </button>
        </div>
      </div>
    </div>
  </div>
</body>
</html>"""

# STAGE 7: Examination Submission Acknowledgement Slip & Result Confidentiality
stage7_html = get_base_head("Stage 7 - Submission Acknowledgement Slip") + f"""
<body>
  <!-- Header -->
  <header class="header-bar" style="background:#004d40; padding:12px 30px; display:flex; justify-content:space-between; align-items:center;">
    <div class="demo-header-brand">
      <img src="{LOGO_URL}" alt="Logo">
      <div>
        <div class="demo-header-title">KWARA STATE CIVIL SERVICE COMMISSION</div>
        <div class="demo-header-sub">2026 Promotion Evaluation Examination - Submission Acknowledgement</div>
      </div>
    </div>
    <div style="background:#059669; color:#fff; padding:6px 14px; border-radius:20px; font-size:0.8rem; font-weight:800;">
      STATUS: RECORDED & LOCKED
    </div>
  </header>

  <main style="max-width:860px; margin:30px auto; padding:0 20px;">
    <!-- Acknowledgement Card -->
    <div style="background:#ffffff; border-radius:16px; border:1px solid #e2e8f0; box-shadow:0 10px 25px rgba(0,0,0,0.06); padding:32px;">
      <!-- Hero Banner -->
      <div style="background:linear-gradient(135deg, #004d40 0%, #00796b 100%); color:#ffffff; border-radius:12px; padding:22px; text-align:center; margin-bottom:24px; box-shadow:0 4px 14px rgba(0,77,64,0.2);">
        <div style="font-size:2.4rem; margin-bottom:6px;">✅</div>
        <h2 style="font-size:1.35rem; font-weight:900; margin:0 0 6px 0; color:#ffffff;">Examination Successfully Submitted</h2>
        <p style="font-size:0.88rem; color:#e0f2f1; margin:0; max-width:600px; margin:0 auto; line-height:1.5;">
          Your 40 CBT examination answers have been securely received and recorded in the Kwara State Civil Service Commission database.
        </p>
      </div>

      <!-- Candidate Slip Grid -->
      <div style="display:grid; grid-template-columns:1fr 1fr; gap:14px; background:#f8fafc; border:1.5px solid #e2e8f0; border-radius:12px; padding:20px; margin-bottom:22px;">
        <div>
          <div style="font-size:0.72rem; font-weight:700; color:#64748b; text-transform:uppercase;">Officer Full Name</div>
          <div style="font-size:0.95rem; font-weight:800; color:#0f172a; margin-top:2px;">FATIMAH BOLA AHMED</div>
        </div>
        <div>
          <div style="font-size:0.72rem; font-weight:700; color:#64748b; text-transform:uppercase;">Public Service Number (PSN)</div>
          <div style="font-size:0.95rem; font-weight:800; color:#004d40; margin-top:2px;">123456</div>
        </div>
        <div>
          <div style="font-size:0.72rem; font-weight:700; color:#64748b; text-transform:uppercase;">Ministry / Department / Agency</div>
          <div style="font-size:0.85rem; font-weight:700; color:#334155; margin-top:2px;">Ministry of Agriculture & Rural Dev.</div>
        </div>
        <div>
          <div style="font-size:0.72rem; font-weight:700; color:#64748b; text-transform:uppercase;">Cadre / Proposed Grade Level</div>
          <div style="font-size:0.85rem; font-weight:700; color:#334155; margin-top:2px;">Principal Agricultural Officer (GL 12)</div>
        </div>
        <div>
          <div style="font-size:0.72rem; font-weight:700; color:#64748b; text-transform:uppercase;">Examination Paper Code</div>
          <div style="font-size:0.85rem; font-weight:800; color:#b45309; margin-top:2px;">MARD-GL12-B</div>
        </div>
        <div>
          <div style="font-size:0.72rem; font-weight:700; color:#64748b; text-transform:uppercase;">Time Spent</div>
          <div style="font-size:0.85rem; font-weight:800; color:#059669; margin-top:2px;">16m 45s</div>
        </div>
        <div>
          <div style="font-size:0.72rem; font-weight:700; color:#64748b; text-transform:uppercase;">Submission Status</div>
          <div style="font-size:0.85rem; font-weight:800; color:#059669; margin-top:2px;">Recorded & Locked</div>
        </div>
        <div>
          <div style="font-size:0.72rem; font-weight:700; color:#64748b; text-transform:uppercase;">Submission Date & Time</div>
          <div style="font-size:0.85rem; font-weight:700; color:#334155; margin-top:2px;">2026-09-26 10:16:45</div>
        </div>
      </div>

      <!-- Confidentiality Notice Banner -->
      <div style="background:#f8fafc; border:1.5px solid #cbd5e1; border-left:5px solid #004d40; border-radius:8px; padding:16px 18px; margin-bottom:22px; font-size:0.85rem; color:#334155; line-height:1.6;">
        <div style="font-weight:800; color:#004d40; margin-bottom:4px; display:flex; align-items:center; gap:6px;">
          <span>🔒 Official Result Confidentiality Policy</span>
        </div>
        In accordance with Kwara State Civil Service Commission regulations, examination scores are <strong>NOT displayed on candidate workstations</strong>. Official promotional evaluation scores, recommendations, and promotion results will be compiled and communicated directly through designated Ministry, Department, and Agency (MDA) channels.
      </div>

      <!-- Single Attempt Notice Banner -->
      <div style="background:#fffbeb; border-radius:8px; padding:10px 14px; margin-bottom:24px; font-size:0.82rem; color:#92400e; text-align:center; border:1px solid #fde68a;">
        ℹ️ <strong>Evaluation Session Concluded:</strong> Retakes or additional test attempts are strictly prohibited.
      </div>

      <!-- Slip Footer -->
      <div style="display:flex; justify-content:space-between; align-items:center; border-top:1.5px solid #e2e8f0; padding-top:16px; margin-bottom:24px;">
        <div>
          <div style="font-weight:800; color:#004d40; font-size:0.88rem;">Ref: KWS-CSC-SUB-01048-123456</div>
          <div style="font-size:0.72rem; color:#64748b; margin-top:2px;">Electronically verified & recorded by Kwara State CSC Portal</div>
        </div>
        <div style="font-size:0.78rem; font-weight:700; color:#475569; text-transform:uppercase;">
          Civil Service Commission &bull; Ilorin
        </div>
      </div>

      <!-- Actions -->
      <div style="display:flex; justify-content:center; gap:14px;">
        <button type="button" style="background:#004d40; color:#fff; border:none; padding:12px 24px; border-radius:8px; font-size:0.9rem; font-weight:700; cursor:pointer; display:flex; align-items:center; gap:8px;">
          <span>🖨️ Print Acknowledgement Slip (PDF)</span>
        </button>
        <button type="button" style="background:#f1f5f9; color:#475569; border:1px solid #cbd5e1; padding:12px 20px; border-radius:8px; font-size:0.9rem; font-weight:700; cursor:pointer;">
          <span>🏠 Return to Portal Home</span>
        </button>
      </div>
    </div>
  </main>
</body>
</html>"""

stages = [
    ("stage1_login.html", stage1_html, "stage1_login.png"),
    ("stage2_verification.html", stage2_html, "stage2_verification.png"),
    ("stage3_exam_screen.html", stage3_html, "stage3_exam_screen.png"),
    ("stage4_blackout_curtain.html", stage4_html, "stage4_blackout_curtain.png"),
    ("stage5_strike_warning.html", stage5_html, "stage5_strike_warning.png"),
    ("stage6_unanswered_modal.html", stage6_html, "stage6_unanswered_modal.png"),
    ("stage7_submission_slip.html", stage7_html, "stage7_submission_slip.png"),
]

for html_name, html_content, png_name in stages:
    html_file = os.path.join(OUTPUT_DIR, html_name)
    png_file = os.path.join(OUTPUT_DIR, png_name)
    
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    cmd = [
        CHROME_PATH,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--window-size=1280,820",
        f"--screenshot={png_file}",
        f"file:///{html_file}"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if os.path.exists(png_file):
        print(f"Generated screenshot: {png_name} (Size: {os.path.getsize(png_file)} bytes)")
    else:
        print(f"ERROR generating: {png_name}")

print("All screenshots generated successfully!")
