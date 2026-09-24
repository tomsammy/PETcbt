import os, json, shutil

json_path = r"C:\Users\hp\.gemini\antigravity\brain\59e11c97-b96e-4533-9f69-eecf246fc521\scratch\omitted_22_results.json"
with open(json_path, "r", encoding="utf-8") as f:
    candidates = json.load(f)

print(f"Loaded {len(candidates)} candidates.")

html_head = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Kwara CSC 2026 CBT - Registration Clearance Slips (Omitted Candidates - 22 Officers)</title>
  <style>
    *, *::before, *::after {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }

    @page {
      size: A4 portrait;
      margin: 6mm 6mm;
    }

    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
      background: #f1f5f9;
      color: #0f172a;
      -webkit-print-color-adjust: exact !important;
      print-color-adjust: exact !important;
    }

    /* Screen-only Controls */
    .no-print {
      background: #004d40;
      color: #fff;
      padding: 14px 20px;
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      position: sticky;
      top: 0;
      z-index: 1000;
      box-shadow: 0 4px 12px rgba(0,0,0,0.18);
    }

    .no-print h1 {
      font-size: 1.1rem;
      font-weight: 800;
      letter-spacing: -0.01em;
    }
    .no-print p {
      font-size: 0.8rem;
      opacity: 0.9;
      margin-top: 2px;
    }

    .controls-group {
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .btn-print {
      background: #f59e0b;
      color: #000;
      font-weight: 800;
      border: none;
      padding: 9px 20px;
      border-radius: 6px;
      cursor: pointer;
      font-size: 0.92rem;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      transition: background 0.2s ease;
    }
    .btn-print:hover {
      background: #d97706;
      color: #fff;
    }

    /* Screen Wrapper */
    .screen-wrapper {
      max-width: 900px;
      margin: 20px auto;
    }

    /* A4 PAGE CONTAINER: Exactly 10 Slips (2 Columns x 5 Rows) */
    .page-container {
      width: 198mm;
      height: 284mm;
      margin: 0 auto 20px auto;
      background: #fff;
      display: grid;
      grid-template-columns: repeat(2, 95mm);
      grid-template-rows: repeat(5, 52.8mm);
      gap: 4mm 6mm;
      padding: 2mm 0;
      box-shadow: 0 4px 14px rgba(0,0,0,0.08);
      page-break-after: always;
      break-after: page;
    }

    /* Individual Slip Card (Fits 52.8mm height x 95mm width) */
    .slip-card {
      width: 95mm;
      height: 52.8mm;
      border: 1.2px dashed #004d40;
      border-radius: 4px;
      padding: 3mm 3.8mm;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      background: #ffffff;
      box-sizing: border-box;
      overflow: hidden;
      position: relative;
    }

    /* Micro Watermark */
    .slip-card::before {
      content: "KWS-CSC";
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%) rotate(-25deg);
      font-size: 28px;
      font-weight: 900;
      color: rgba(0, 77, 64, 0.035);
      letter-spacing: 4px;
      pointer-events: none;
      z-index: 0;
    }

    .slip-header {
      border-bottom: 1.2px solid #004d40;
      padding-bottom: 1.5px;
      margin-bottom: 1.5px;
      text-align: center;
    }
    .header-seal {
      font-size: 7.2px;
      font-weight: 900;
      color: #004d40;
      letter-spacing: 0.3px;
      text-transform: uppercase;
      line-height: 1.1;
    }
    .header-sub {
      font-size: 5.8px;
      font-weight: 700;
      color: #b45309;
      letter-spacing: 0.2px;
      margin-top: 0.5px;
    }

    .name-block {
      margin-bottom: 1px;
      line-height: 1.1;
    }
    .lbl-small {
      font-size: 5.8px;
      color: #64748b;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.3px;
    }
    .officer-name {
      font-size: 8.2px;
      font-weight: 800;
      color: #0f172a;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .code-box {
      background: #fffbeb;
      border: 1.2px dashed #d97706;
      border-radius: 3px;
      padding: 1.2px 3px;
      text-align: center;
      margin-bottom: 1.5px;
    }
    .code-title {
      font-size: 5.5px;
      font-weight: 700;
      color: #b45309;
      text-transform: uppercase;
      letter-spacing: 0.4px;
    }
    .code-val {
      font-size: 10.5px;
      font-weight: 900;
      color: #b45309;
      letter-spacing: 1.5px;
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      line-height: 1.1;
    }

    .details-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 6.5px;
      margin-bottom: 1.5px;
    }
    .details-table td {
      padding: 0.8px 1.5px;
      vertical-align: middle;
      line-height: 1.15;
    }
    .td-lbl {
      font-weight: 700;
      color: #475569;
      width: 18%;
    }
    .td-val {
      font-weight: 800;
      color: #0f172a;
    }
    .psn-highlight {
      color: #004d40;
      font-size: 8px;
      font-weight: 900;
    }

    .instruction-box {
      background: #f8fafc;
      border-left: 2.5px solid #004d40;
      padding: 1.5px 3px;
      font-size: 5.8px;
      color: #334155;
      line-height: 1.15;
      border-radius: 0 2px 2px 0;
      margin-bottom: 1.5px;
    }

    .slip-footer strong {
      color: #004d40;
      font-weight: 800;
    }
    .slip-footer {
      border-top: 0.8px dashed #cbd5e1;
      padding-top: 1px;
      display: flex;
      justify-content: space-between;
      font-size: 5.5px;
      color: #64748b;
      line-height: 1;
    }

    /* Print Optimizations: Exactly 10 Slips per Sheet */
    @media print {
      body {
        background: #fff;
      }
      .no-print {
        display: none !important;
      }
      .screen-wrapper {
        max-width: 100%;
        margin: 0;
        padding: 0;
      }
      .page-container {
        box-shadow: none;
        margin: 0;
        width: 198mm;
        height: 284mm;
        page-break-after: always;
        break-after: page;
      }
      .slip-card {
        border: 1.5px dashed #004d40 !important;
      }
      .code-box {
        border: 1.8px dashed #d97706 !important;
      }
    }
  </style>
</head>
<body>

  <div class="no-print">
    <div>
      <h1>KWARA STATE CIVIL SERVICE COMMISSION</h1>
      <p>2026 Promotion Evaluation CBT &bull; Candidate Registration Clearance Slips (Omitted Candidates - 22 Officers)</p>
    </div>
    <div class="controls-group">
      <button class="btn-print" onclick="window.print()">🖨️ Print All Slips (PDF / Paper)</button>
    </div>
  </div>

  <div class="screen-wrapper">
"""

def generate_slip(c):
    return f"""      <div class="slip-card">
        <div class="slip-header">
          <div class="header-seal">KWARA STATE CIVIL SERVICE COMMISSION</div>
          <div class="header-sub">2026 PROMOTION EVALUATION &bull; ONBOARDING CLEARANCE SLIP</div>
        </div>

        <div class="name-block">
          <span class="lbl-small">OFFICER FULL NAME:</span>
          <div class="officer-name">{c['name']}</div>
        </div>

        <div class="code-box">
          <div class="code-title">🔑 REGISTRATION CLEARANCE CODE (CODE 1)</div>
          <div class="code-val">{c['code_1']}</div>
        </div>

        <table class="details-table">
          <tr>
            <td class="td-lbl">PSN:</td>
            <td class="td-val psn-highlight">{c['psn']}</td>
            <td class="td-lbl">MDA:</td>
            <td class="td-val">{c['mda']}</td>
          </tr>
          <tr>
            <td class="td-lbl">Proposed Rank:</td>
            <td class="td-val" colspan="3">{c['proposed_rank']} <strong>(GL {c['proposed_gl']})</strong></td>
          </tr>
          <tr>
            <td class="td-lbl">Exam Paper:</td>
            <td class="td-val" style="color:#004d40;"><strong>{c['exam_code']}</strong> &bull; {c['batch_session']} ({c['batch_time']})</td>
            <td class="td-lbl">Date:</td>
            <td class="td-val">{c['exam_date'].split(',')[0]}</td>
          </tr>
        </table>

        <div class="instruction-box">
          <strong>How to Register:</strong> Visit portal: <strong>kwaracsc.ng</strong> &rarr; <strong>Verification & Photocard</strong> &rarr; Enter <strong>PSN ({c['psn']})</strong> + <strong>Code 1 ({c['code_1']})</strong> &rarr; Upload photo & print Photocard.
        </div>

        <div class="slip-footer">
          <span>Ref: KWS-CSC-REG-{c['psn']}</span>
          <span>Portal: <strong>kwaracsc.ng</strong> &bull; Kwara CSC</span>
        </div>
      </div>
"""

body = ""
# 10 per page
page_num = 1
for i in range(0, len(candidates), 10):
    chunk = candidates[i:i+10]
    body += f"<!-- PAGE {page_num} -->\n<div class=\"page-container\">\n"
    for cand in chunk:
        body += generate_slip(cand)
    body += "</div>\n\n"
    page_num += 1

html_tail = """  </div>
</body>
</html>
"""

full_html = html_head + body + html_tail

dest_paths = [
    r"C:\Users\hp\Downloads\Omitted_Candidates_Registration_Slips_(22_Candidates).html",
    r"c:\Users\hp\Desktop\DataClassPython\Kwara_CSC_2026_CBT_Slips_By_MDA\Omitted_Candidates_Registration_Slips_(22_Candidates).html",
    r"c:\Users\hp\Desktop\DataClassPython\kwara_cbt_app\static\slips_by_mda\Omitted_Candidates_Registration_Slips_(22_Candidates).html",
    r"c:\Users\hp\Desktop\DataClassPython\static\slips_by_mda\Omitted_Candidates_Registration_Slips_(22_Candidates).html",
    r"c:\Users\hp\Desktop\DataClassPython\public\slips_by_mda\Omitted_Candidates_Registration_Slips_(22_Candidates).html"
]

for p in dest_paths:
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(full_html)
    print(f"Written: {p}")

print("\nUpdating 00_INDEX.html across slip directories...")
index_row = """    <tr style="background: #ecfdf5; border-left: 4px solid #059669;">
      <td style="text-align:center; font-weight:800; color:#059669;">★ LATEST</td>
      <td><strong>Omitted Promotion Candidates (22 Officers across 11 MDAs)</strong> <span style="background:#059669; color:#fff; font-size:0.7rem; padding:2px 6px; border-radius:3px; margin-left:6px;">Latest Addition</span></td>
      <td style="text-align:center; font-weight:800; color:#059669;">22</td>
      <td style="text-align:center;">3 A4 Pages</td>
      <td style="text-align:center;">
        <a href="Omitted_Candidates_Registration_Slips_(22_Candidates).html" target="_blank" class="open-btn" style="background:#059669; color:#fff;">&#128438; Open 22 Slips</a>
      </td>
    </tr>
"""

index_paths = [
    r"c:\Users\hp\Desktop\DataClassPython\Kwara_CSC_2026_CBT_Slips_By_MDA\00_INDEX.html",
    r"c:\Users\hp\Desktop\DataClassPython\kwara_cbt_app\static\slips_by_mda\00_INDEX.html",
    r"c:\Users\hp\Desktop\DataClassPython\static\slips_by_mda\00_INDEX.html",
    r"c:\Users\hp\Desktop\DataClassPython\public\slips_by_mda\00_INDEX.html"
]

for ip in index_paths:
    if os.path.exists(ip):
        with open(ip, "r", encoding="utf-8") as f:
            content = f.read()
        if "Omitted_Candidates_Registration_Slips_(22_Candidates).html" not in content:
            content = content.replace("<tbody>\n", "<tbody>\n" + index_row)
            with open(ip, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Updated index: {ip}")
        else:
            print(f"Index already has 22 slips link: {ip}")

print("Slips generation complete!")
