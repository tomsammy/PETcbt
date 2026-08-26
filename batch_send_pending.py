import sys
sys.stdout.reconfigure(line_buffering=True)
import os
import time
import argparse
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import psycopg2
import psycopg2.extras

# Add app directory to path
app_dir = os.path.join(os.path.dirname(__file__), "kwara_cbt_app")
sys.path.insert(0, app_dir)

from email_service import build_result_email_html

NEON_URL = os.environ.get(
    "DATABASE_URL", 
    "postgresql://neondb_owner:npg_Rl0zv1crIkTY@ep-purple-heart-axjsakzf-pooler.c-4.us-east-2.aws.neon.tech/neondb?sslmode=require"
)

def run_batch_email(limit=None, dry_run=False, gmail_user=None, gmail_pass=None):
    # Retrieve credentials
    smtp_user = (gmail_user or os.environ.get("GMAIL_USER") or "tomoriad@gmail.com").strip()
    smtp_pass = (gmail_pass or os.environ.get("GMAIL_APP_PASSWORD") or "").strip()

    if not smtp_pass and not dry_run:
        print("\n" + "=" * 65)
        print("ERROR: Gmail App Password is required!")
        print("Run with: python batch_send_pending.py --pass 'your-16-letter-app-password'")
        print("Or set GMAIL_APP_PASSWORD in your environment variables.")
        print("=" * 65 + "\n")
        return

    print("=" * 65)
    print("KWARA STATE OFFICE OF THE HEAD OF SERVICE - CBT EMAIL DISPATCHER")
    print(f"Database: Neon PostgreSQL")
    print(f"Sender: {smtp_user}")
    print(f"Mode: {'DRY RUN (No emails sent)' if dry_run else 'LIVE DISPATCH'}")
    print("=" * 65)

    conn = psycopg2.connect(NEON_URL)
    conn.autocommit = True
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    query = """
        SELECT id, candidate_id, candidate_name, psn, email, grade_level, mda,
               total_questions, correct_count, score_percentage, grade_remark,
               time_taken_seconds, submitted_at
        FROM submissions
        WHERE email_status = 'pending'
        ORDER BY id ASC
    """
    if limit:
        query += f" LIMIT {int(limit)}"

    cur.execute(query)
    candidates = cur.fetchall()
    total = len(candidates)
    print(f"\nFound {total} pending candidates to email.\n")

    if total == 0:
        print("No pending emails found! All candidates have received their results.")
        cur.close()
        conn.close()
        return

    sent_count = 0
    failed_count = 0

    # Connect to SMTP if not dry run
    server = None
    if not dry_run:
        try:
            print("Connecting to Gmail SMTP (smtp.gmail.com:465 SSL)...", flush=True)
            server = smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=20)
            server.login(smtp_user, smtp_pass)
            print("Connected & Authenticated successfully!\n", flush=True)
        except Exception as e:
            print(f"Failed to connect to Gmail: {e}")
            cur.close()
            conn.close()
            return

    for idx, c in enumerate(candidates, start=1):
        cand_email = c["email"].strip().lower()
        cand_name = c["candidate_name"]
        psn = c["psn"]
        submission_id = c["id"]

        print(f"[{idx}/{total}] Processing: {cand_name} (PSN: {psn}) -> {cand_email}...", end=" ", flush=True)

        if dry_run:
            print("[SIMULATED]")
            sent_count += 1
            continue

        try:
            html = build_result_email_html(
                candidate_name=cand_name,
                psn=psn,
                email=cand_email,
                grade_level=c["grade_level"],
                mda=c["mda"],
                score_percentage=float(c["score_percentage"]),
                total_marks=c["correct_count"] * 2,
                max_marks=c["total_questions"] * 2,
                correct_count=c["correct_count"],
                total_questions=c["total_questions"],
                grade_remark=c["grade_remark"],
                time_taken_seconds=c["time_taken_seconds"],
                submitted_at=str(c["submitted_at"]),
                submission_id=submission_id
            )

            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"Official CBT Evaluation Result Slip - {cand_name} (PSN: {psn})"
            msg["From"] = f"Kwara State Office of Head of Service <{smtp_user}>"
            msg["To"] = cand_email
            msg.attach(MIMEText(html, "html"))

            server.sendmail(smtp_user, [cand_email], msg.as_string())

            # Mark as sent in Neon
            cur.execute("""
                UPDATE submissions 
                SET email_status = 'sent', email_sent_at = NOW() 
                WHERE id = %s
            """, (submission_id,))

            print("✅ SENT")
            sent_count += 1
            time.sleep(0.8) # safe delay between messages

        except smtplib.SMTPResponseException as e:
            print(f"❌ SMTP ERROR ({e.smtp_code}): {e.smtp_error.decode('utf-8', errors='ignore')}")
            failed_count += 1
            if "quota" in str(e.smtp_error).lower() or e.smtp_code in (421, 451, 550):
                print("\n⚠️ Google daily sending quota reached! Pausing batch now.")
                print(f"Dispatched {sent_count} emails successfully before quota limit.")
                break
        except Exception as e:
            print(f"❌ ERROR: {e}")
            failed_count += 1

    if server:
        try:
            server.quit()
        except Exception:
            pass

    cur.close()
    conn.close()

    print("\n" + "=" * 65)
    print(f"BATCH SUMMARY: {sent_count} sent successfully, {failed_count} errors, {total - sent_count - failed_count} remaining.")
    print("=" * 65)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Batch send pending CBT result emails")
    parser.add_argument("--limit", type=int, default=None, help="Maximum number of emails to send")
    parser.add_argument("--dry-run", action="store_true", help="Simulate without sending")
    parser.add_argument("--user", type=str, default=None, help="Gmail address")
    parser.add_argument("--pass", dest="password", type=str, default=None, help="Gmail 16-letter App Password")

    args = parser.parse_args()
    run_batch_email(limit=args.limit, dry_run=args.dry_run, gmail_user=args.user, gmail_pass=args.password)
