import os
import json
import urllib.request
import urllib.error
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("cbt_email")

def build_result_email_html(
    candidate_name: str,
    psn: str,
    email: str,
    grade_level: str,
    mda: str,
    score_percentage: float,
    total_marks: int,
    max_marks: int,
    correct_count: int,
    total_questions: int,
    grade_remark: str,
    time_taken_seconds: int,
    submitted_at: str,
    submission_id: int
) -> str:
    mins = time_taken_seconds // 60
    secs = time_taken_seconds % 60
    time_str = f"{mins}m {secs}s"
    ref_code = f"KWS-HOS-{submission_id:05d}-{psn}"
    
    remark_bg = "#d1fae5" if score_percentage >= 75 else ("#e0f2fe" if score_percentage >= 60 else ("#fef3c7" if score_percentage >= 50 else "#fee2e2"))
    remark_color = "#065f46" if score_percentage >= 75 else ("#0369a1" if score_percentage >= 60 else ("#92400e" if score_percentage >= 50 else "#991b1b"))

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f1f5f9; margin: 0; padding: 20px; color: #1e293b; }}
  .container {{ max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.08); border: 1px solid #e2e8f0; }}
  .header {{ background: linear-gradient(135deg, #004d40 0%, #00796b 100%); color: #ffffff; padding: 28px 24px; text-align: center; }}
  .header h1 {{ margin: 0; font-size: 18px; letter-spacing: 0.02em; font-weight: 800; }}
  .header p {{ margin: 6px 0 0 0; font-size: 13px; color: #ffd54f; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }}
  .body-content {{ padding: 28px 24px; }}
  .greeting {{ font-size: 16px; font-weight: 600; margin-bottom: 16px; color: #0f172a; }}
  .score-hero {{ background: #f8fafc; border: 2px solid #e2e8f0; border-radius: 10px; padding: 20px; text-align: center; margin: 20px 0; }}
  .score-val {{ font-size: 42px; font-weight: 900; color: #004d40; margin: 0; line-height: 1; }}
  .score-sub {{ font-size: 14px; color: #475569; margin: 8px 0 12px 0; font-weight: 600; }}
  .remark-pill {{ display: inline-block; padding: 6px 16px; border-radius: 20px; font-size: 13px; font-weight: 700; background: {remark_bg}; color: {remark_color}; }}
  .details-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
  .details-table td {{ padding: 10px 12px; border-bottom: 1px solid #f1f5f9; font-size: 14px; }}
  .details-table td.lbl {{ color: #64748b; font-weight: 600; width: 40%; }}
  .details-table td.val {{ color: #0f172a; font-weight: 700; text-align: right; }}
  .footer {{ background: #f8fafc; padding: 18px 24px; border-top: 1px solid #e2e8f0; text-align: center; font-size: 12px; color: #64748b; }}
  .ref-box {{ font-family: monospace; font-weight: 700; color: #004d40; font-size: 13px; margin-bottom: 4px; }}
</style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>KWARA STATE OFFICE OF THE HEAD OF SERVICE</h1>
      <p>Productivity Enhancement Evaluation CBT</p>
    </div>
    <div class="body-content">
      <div class="greeting">Dear {candidate_name},</div>
      <p style="font-size: 14px; line-height: 1.5; color: #475569; margin: 0 0 16px 0;">
        This is your official evaluation result for the Computer Based Test (CBT) conducted by the Kwara State Office of the Head of Service.
      </p>

      <div class="score-hero">
        <div class="score-val">{score_percentage:.1f}%</div>
        <div class="score-sub">Total Marks: {total_marks} / {max_marks} marks ({correct_count} of {total_questions} correct)</div>
        <div class="remark-pill">{grade_remark}</div>
      </div>

      <table class="details-table">
        <tr>
          <td class="lbl">Officer Full Name</td>
          <td class="val">{candidate_name}</td>
        </tr>
        <tr>
          <td class="lbl">Public Service Number (PSN)</td>
          <td class="val">{psn}</td>
        </tr>
        <tr>
          <td class="lbl">Evaluation Cadre</td>
          <td class="val">{grade_level}</td>
        </tr>
        <tr>
          <td class="lbl">MDA / Organization</td>
          <td class="val">{mda}</td>
        </tr>
        <tr>
          <td class="lbl">Time Spent</td>
          <td class="val">{time_str}</td>
        </tr>
        <tr>
          <td class="lbl">Submission Date & Time</td>
          <td class="val">{submitted_at}</td>
        </tr>
      </table>

      <div style="background: #eff6ff; border-left: 4px solid #3b82f6; padding: 12px 14px; border-radius: 4px; font-size: 13px; color: #1e40af; margin-top: 16px;">
        <strong>Notice:</strong> This is an electronically verified record. Additional evaluation attempts are not permitted under the single-attempt policy.
      </div>
    </div>
    <div class="footer">
      <div class="ref-box">Ref: {ref_code}</div>
      <div>Office of the Head of Service &bull; Kwara State Civil Service Commission</div>
    </div>
  </div>
</body>
</html>"""

def send_result_email(
    candidate_email: str,
    candidate_name: str,
    psn: str,
    grade_level: str,
    mda: str,
    score_percentage: float,
    total_marks: int,
    max_marks: int,
    correct_count: int,
    total_questions: int,
    grade_remark: str,
    time_taken_seconds: int,
    submitted_at: str,
    submission_id: int
) -> Dict[str, Any]:
    if not candidate_email or "@" not in candidate_email:
        return {"success": False, "error": "Invalid candidate email address"}

    html_content = build_result_email_html(
        candidate_name=candidate_name,
        psn=psn,
        email=candidate_email,
        grade_level=grade_level,
        mda=mda,
        score_percentage=score_percentage,
        total_marks=total_marks,
        max_marks=max_marks,
        correct_count=correct_count,
        total_questions=total_questions,
        grade_remark=grade_remark,
        time_taken_seconds=time_taken_seconds,
        submitted_at=submitted_at,
        submission_id=submission_id
    )

    subject = f"Official CBT Evaluation Result Slip - {candidate_name} (PSN: {psn})"
    resend_key = os.environ.get("RESEND_API_KEY", "").strip()
    sendgrid_key = os.environ.get("SENDGRID_API_KEY", "").strip()
    email_from = os.environ.get("EMAIL_FROM", "Kwara State Head of Service <onboarding@resend.dev>").strip()

    # 1. Resend API Dispatch
    if resend_key:
        try:
            payload = json.dumps({
                "from": email_from,
                "to": [candidate_email],
                "subject": subject,
                "html": html_content
            }).encode("utf-8")
            
            req = urllib.request.Request(
                "https://api.resend.com/emails",
                data=payload,
                headers={
                    "Authorization": f"Bearer {resend_key}",
                    "Content-Type": "application/json",
                    "User-Agent": "KwaraHOS-CBT/1.0"
                }
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                res_body = json.loads(response.read().decode("utf-8"))
                return {"success": True, "provider": "resend", "id": res_body.get("id")}
        except Exception as e:
            logger.error(f"Resend dispatch error: {e}")
            return {"success": False, "error": str(e)}

    # 2. SendGrid API Dispatch
    if sendgrid_key:
        try:
            from_email = email_from.split("<")[-1].replace(">", "").strip() if "<" in email_from else email_from
            payload = json.dumps({
                "personalizations": [{"to": [{"email": candidate_email}]}],
                "from": {"email": from_email, "name": "Kwara State Office of Head of Service"},
                "subject": subject,
                "content": [{"type": "text/html", "value": html_content}]
            }).encode("utf-8")

            req = urllib.request.Request(
                "https://api.sendgrid.com/v3/mail/send",
                data=payload,
                headers={
                    "Authorization": f"Bearer {sendgrid_key}",
                    "Content-Type": "application/json",
                    "User-Agent": "KwaraHOS-CBT/1.0"
                }
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                return {"success": True, "provider": "sendgrid"}
        except Exception as e:
            logger.error(f"SendGrid dispatch error: {e}")
            return {"success": False, "error": str(e)}

    # Fallback simulated (when API keys are not set in dev/local)
    logger.info(f"[SIMULATED EMAIL] Result email prepared for {candidate_email} (PSN: {psn}, Score: {score_percentage}%)")
    return {"success": True, "provider": "simulated", "message": "Email template generated and logged"}
