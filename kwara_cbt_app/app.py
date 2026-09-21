import os
import json
import sqlite3
import io
import secrets
import hmac
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional, Union

from fastapi import FastAPI, APIRouter, HTTPException, Request, Response, Depends, Header, Query, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

from database import get_db_connection, init_db, get_setting, set_setting
from email_service import send_result_email

app = FastAPI(title="KWARA STATE CIVIL SERVICE COMMISSION - 2026 Promotion Evaluation CBT Examination")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Robust static directory resolver for local and Vercel environments
STATIC_DIR = None
for p in [
    os.path.join(os.path.dirname(__file__), "static"),
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "static"),
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "public", "static"),
    os.path.join(os.getcwd(), "static"),
    os.path.join(os.getcwd(), "kwara_cbt_app", "static"),
    os.path.join(os.getcwd(), "public", "static")
]:
    if os.path.exists(p) and os.path.isdir(p):
        STATIC_DIR = p
        break

if not STATIC_DIR:
    STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
    os.makedirs(STATIC_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")
SECRET_KEY = os.environ.get("CBT_SECRET_KEY", "kwara_hos_cbt_secure_secret_2026")
ACTIVE_ADMIN_TOKENS = set()

def generate_admin_token(username: str) -> str:
    timestamp = str(int(datetime.now().timestamp()))
    payload = f"{username}:{timestamp}"
    signature = hmac.new(SECRET_KEY.encode('utf-8'), payload.encode('utf-8'), hashlib.sha256).hexdigest()
    return f"{payload}:{signature}"

def verify_admin_token_stateless(token_str: str) -> bool:
    if not token_str:
        return False
    parts = token_str.split(":")
    if len(parts) != 3:
        return False
    username, timestamp, signature = parts
    if username != ADMIN_USERNAME:
        return False
    payload = f"{username}:{timestamp}"
    expected_sig = hmac.new(SECRET_KEY.encode('utf-8'), payload.encode('utf-8'), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(signature, expected_sig):
        return False
    try:
        ts = int(timestamp)
        # Valid for 48 hours
        if datetime.now().timestamp() - ts > 172800:
            return False
    except Exception:
        return False
    return True

class AdminLoginRequest(BaseModel):
    username: str
    password: str

class StartExamRequest(BaseModel):
    name: str
    psn: str
    email: str
    grade_level: str
    mda: Optional[str] = "State Civil Service"

class SubmitExamRequest(BaseModel):
    candidate_id: Optional[Union[int, str]] = None
    name: str
    psn: str
    email: str
    grade_level: str
    mda: Optional[str] = "State Civil Service"
    paper_code: Optional[str] = None
    answers: Dict[str, str] = {}
    time_taken_seconds: Optional[int] = 0

class RetrieveResultRequest(BaseModel):
    psn: str

class SendResultEmailRequest(BaseModel):
    psn: str
    email: Optional[str] = None

class ResetCandidateRequest(BaseModel):
    psn: str
    reason: Optional[str] = "Approved by Admin for Retake"

class CandidateLookupRequest(BaseModel):
    psn: str
    code_1: str

class CompleteRegistrationRequest(BaseModel):
    psn: str
    code_1: str
    amended_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    passport_photo: str

class StartExamWithTokenRequest(BaseModel):
    psn: str
    token_code: str

def verify_admin_auth(
    authorization: Optional[str] = Header(None),
    token: Optional[str] = Query(None)
):
    auth_token = token
    if not auth_token and authorization:
        if authorization.startswith("Bearer "):
            auth_token = authorization.split("Bearer ")[1].strip()
        else:
            auth_token = authorization.strip()
            
    if not auth_token:
        raise HTTPException(status_code=401, detail="Unauthorized: Admin login required.")
        
    if not verify_admin_token_stateless(auth_token) and auth_token not in ACTIVE_ADMIN_TOKENS:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid or expired administrator session.")
    return True

@app.on_event("startup")
def startup_event():
    init_db()

@app.get("/", response_class=HTMLResponse)
@app.get("/admin", response_class=HTMLResponse)
def read_index():
    candidates = [
        os.path.join(STATIC_DIR, "index.html"),
        os.path.join(os.path.dirname(__file__), "static", "index.html"),
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "index.html"),
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "public", "index.html"),
        os.path.join(os.getcwd(), "static", "index.html"),
        os.path.join(os.getcwd(), "kwara_cbt_app", "static", "index.html"),
        os.path.join(os.getcwd(), "public", "index.html")
    ]
    for c in candidates:
        if os.path.exists(c):
            with open(c, "r", encoding="utf-8") as f:
                return f.read()
    return "<h1>KWARA STATE CIVIL SERVICE COMMISSION - 2026 Promotion Evaluation CBT Examination</h1>"
 
# Router for all CBT Endpoints (supports both /api/* and /* paths)
router = APIRouter()

@router.post("/admin/login")
@router.post("/api/admin/login")
def admin_login(creds: AdminLoginRequest):
    u = creds.username.strip()
    p = creds.password.strip()
    
    if u == ADMIN_USERNAME and p == ADMIN_PASSWORD:
        token = generate_admin_token(u)
        ACTIVE_ADMIN_TOKENS.add(token)
        return {
            "success": True,
            "token": token,
            "message": "Admin authentication successful."
        }
    raise HTTPException(status_code=401, detail="Invalid administrator username or password.")

@router.get("/admin/verify")
@router.get("/api/admin/verify")
def admin_verify(auth: bool = Depends(verify_admin_auth)):
    return {"success": True, "authenticated": True}

@router.post("/admin/logout")
@router.post("/api/admin/logout")
def admin_logout(
    authorization: Optional[str] = Header(None),
    token: Optional[str] = Query(None)
):
    auth_token = token
    if not auth_token and authorization and authorization.startswith("Bearer "):
        auth_token = authorization.split("Bearer ")[1].strip()
    if auth_token in ACTIVE_ADMIN_TOKENS:
        ACTIVE_ADMIN_TOKENS.remove(auth_token)
    return {"success": True, "message": "Logged out successfully."}

@router.post("/admin/toggle-exam-status")
@router.post("/api/admin/toggle-exam-status")
def toggle_exam_status(auth: bool = Depends(verify_admin_auth)):
    current = get_setting("exam_status", "open")
    new_status = "closed" if current == "open" else "open"
    set_setting("exam_status", new_status)
    return {
        "success": True,
        "exam_status": new_status,
        "message": f"CBT Examination is now officially {'OPEN' if new_status == 'open' else 'CLOSED'}."
    }

@router.get("/info")
@router.get("/api/info")
def get_exam_info():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT grade_level FROM questions ORDER BY grade_level")
    levels = [row["grade_level"] for row in cursor.fetchall()]
    conn.close()
    
    status = get_setting("exam_status", "open")
    
    return {
        "title": "KWARA STATE CIVIL SERVICE COMMISSION - 2026 Promotion Evaluation CBT Examination",
        "grade_levels": levels if levels else ["GL 06-07", "GL 08", "GL 09"],
        "default_duration_minutes": 20,
        "questions_per_exam": 40,
        "marks_per_question": 2.5,
        "total_marks": 100,
        "exam_status": status
    }

@router.post("/start-exam")
@router.post("/api/start-exam")
def start_exam(data: StartExamRequest):
    exam_status = get_setting("exam_status", "open")
    if exam_status == "closed":
        raise HTTPException(
            status_code=403,
            detail="The CBT Examination has been closed by the Administrator (Civil Service Commission). Candidate registration and test attempts are suspended. You cannot take the examination."
        )

    name = data.name.strip()
    psn = data.psn.strip()
    email = data.email.strip().lower()
    grade_level = data.grade_level.strip()
    mda = (data.mda or "State Civil Service").strip()
    
    if not name or not psn or not email:
        raise HTTPException(status_code=400, detail="Name, PSN, and Email address are required.")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if this PSN has already completed an exam
    cursor.execute("SELECT id, submitted_at, score_percentage FROM submissions WHERE psn = ?", (psn,))
    existing_sub = cursor.fetchone()
    if existing_sub:
        conn.close()
        raise HTTPException(
            status_code=400,
            detail=f"The CBT Examination is closed for this record. Officer with PSN {psn} has already taken this test on {existing_sub['submitted_at']} (Score: {existing_sub['score_percentage']}%). You cannot take the examination again."
        )
    
    # Register candidate
    cursor.execute("""
        INSERT INTO candidates (name, psn, email, grade_level, mda)
        VALUES (?, ?, ?, ?, ?)
    """, (name, psn, email, grade_level, mda))
    candidate_id = cursor.lastrowid
    
    # Retrieve questions for this grade level
    cursor.execute("""
        SELECT id, question_number, question_text, option_a, option_b, option_c, option_d
        FROM questions
        WHERE grade_level = ?
        ORDER BY question_number ASC
    """, (grade_level,))
    
    rows = cursor.fetchall()
    conn.commit()
    conn.close()
    
    if not rows:
        raise HTTPException(status_code=404, detail=f"No questions found for grade level {grade_level}.")
    
    questions = []
    for r in rows:
        questions.append({
            "id": r["id"],
            "number": r["question_number"],
            "question": r["question_text"],
            "options": {
                "A": r["option_a"],
                "B": r["option_b"],
                "C": r["option_c"],
                "D": r["option_d"]
            }
        })
        
    return {
        "success": True,
        "candidate_id": candidate_id,
        "candidate": {
            "name": name,
            "psn": psn,
            "email": email,
            "grade_level": grade_level,
            "mda": mda
        },
        "total_questions": len(questions),
        "duration_minutes": 20,
        "questions": questions
    }

def fetch_cbt_questions(cursor, paper_code, mda, group_category):
    clean_paper = (paper_code or "").strip()
    clean_mda = (mda or "").strip()
    clean_group = (group_category or "").replace("GROUP ", "").strip()
    
    rows = []
    matched_paper = clean_paper

    # 1. Exact paper_code match with normalization variants
    if clean_paper:
        alt_paper1 = clean_paper.replace("/", "-")
        alt_paper2 = clean_paper.replace("-", "/")
        alt_paper3 = clean_paper.replace("&CD", "")
        alt_paper4 = clean_paper.replace("/AI", "/A1").replace("-AI", "-A1")
        cursor.execute("""
            SELECT id, question_number, question_text, option_a, option_b, option_c, option_d, correct_answer
            FROM cbt_questions
            WHERE paper_code = ? OR paper_code = ? OR paper_code = ? OR paper_code = ? OR paper_code = ?
            ORDER BY question_number ASC
            LIMIT 40
        """, (clean_paper, alt_paper1, alt_paper2, alt_paper3, alt_paper4))
        rows = cursor.fetchall()

    # 2. Same MDA match
    if not rows and clean_mda:
        cursor.execute("""
            SELECT id, question_number, question_text, option_a, option_b, option_c, option_d, correct_answer
            FROM cbt_questions
            WHERE mda = ?
            ORDER BY question_number ASC
            LIMIT 40
        """, (clean_mda,))
        rows = cursor.fetchall()
        if rows:
            matched_paper = f"{clean_mda} Cadre"

    # 3. Same Group Category in OHOS (Civil Service General)
    if not rows and clean_group:
        cursor.execute("""
            SELECT id, question_number, question_text, option_a, option_b, option_c, option_d, correct_answer
            FROM cbt_questions
            WHERE mda = 'OHOS' AND group_category = ?
            ORDER BY question_number ASC
            LIMIT 40
        """, (clean_group,))
        rows = cursor.fetchall()
        if rows:
            matched_paper = f"OHOS/{clean_group}1"

    # 4. Fallback to questions table
    if not rows:
        cursor.execute("""
            SELECT id, question_number, question_text, option_a, option_b, option_c, option_d, correct_answer
            FROM questions
            ORDER BY question_number ASC
            LIMIT 40
        """)
        rows = cursor.fetchall()
        matched_paper = "Civil Service General"

    rows = [dict(r) for r in rows]

    # Renumber sequentially 1..40 so palette and scoring are always 1 to 40
    renumbered = []
    for idx, r in enumerate(rows[:40], start=1):
        r["question_number"] = idx
        renumbered.append(r)

    return renumbered, matched_paper

@router.post("/submit-exam")
@router.post("/api/submit-exam")
def submit_exam(data: SubmitExamRequest, background_tasks: BackgroundTasks = BackgroundTasks()):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    paper_code = (data.paper_code or "").strip()
    mda = (data.mda or "State Civil Service").strip()
    group_cat = data.grade_level.replace("GROUP ", "").strip()
    
    q_rows, loaded_paper = fetch_cbt_questions(cursor, paper_code, mda, group_cat)
    if not q_rows:
        conn.close()
        raise HTTPException(status_code=404, detail="No examination answer key found.")
        
    correct_key_map = {str(r["question_number"]): r["correct_answer"].strip().upper() for r in q_rows}
    total_questions = len(correct_key_map)
    
    correct_count = 0
    candidate_answers = data.answers or {}
    
    for q_num, correct_ans in correct_key_map.items():
        user_ans = candidate_answers.get(q_num, "").strip().upper()
        if user_ans and user_ans == correct_ans:
            correct_count += 1
            
    score_percentage = round((correct_count / total_questions) * 100, 2) if total_questions > 0 else 0.0
    
    if score_percentage >= 75:
        grade_remark = "Distinction (Excellent)"
    elif score_percentage >= 60:
        grade_remark = "Credit (Very Good)"
    elif score_percentage >= 50:
        grade_remark = "Pass (Satisfactory)"
    else:
        grade_remark = "Needs Improvement"
        
    answers_json_str = json.dumps(candidate_answers)
    
    cid = data.candidate_id
    if cid is not None:
        try:
            cid = int(cid)
        except Exception:
            cid = None

    cursor.execute("""
        INSERT INTO submissions (
            candidate_id, candidate_name, psn, email, grade_level, mda,
            total_questions, correct_count, score_percentage, grade_remark,
            time_taken_seconds, answers_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        cid, data.name.strip(), data.psn.strip(),
        data.email.strip().lower(), data.grade_level.strip(),
        (data.mda or "State Civil Service").strip(),
        total_questions, correct_count, score_percentage, grade_remark,
        data.time_taken_seconds or 0, answers_json_str
    ))
    submission_id = cursor.lastrowid
    
    cursor.execute("SELECT submitted_at FROM submissions WHERE id = ?", (submission_id,))
    sub_row = cursor.fetchone()
    submitted_at = sub_row["submitted_at"] if sub_row else datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Mark exam token and candidate roster as completed/tested
    try:
        cursor.execute("UPDATE exam_tokens SET status = 'completed' WHERE assigned_to_psn = ?", (data.psn.strip(),))
        cursor.execute("UPDATE candidate_roster SET registration_status = 'tested' WHERE psn = ?", (data.psn.strip(),))
    except Exception:
        pass
    
    conn.commit()
    conn.close()

    # Note: Background score email dispatch has been disabled per Civil Service Commission confidentiality policy
    
    return {
        "success": True,
        "submission_id": submission_id,
        "candidate": {
            "name": data.name.strip(),
            "psn": data.psn.strip(),
            "email": data.email.strip().lower(),
            "grade_level": data.grade_level.strip(),
            "mda": (data.mda or "State Civil Service").strip(),
            "paper_code": getattr(data, 'paper_code', '') or ""
        },
        "time_taken_seconds": data.time_taken_seconds or 0,
        "submitted_at": submitted_at,
        "message": "Examination answers successfully submitted and recorded."
    }

@router.post("/candidate/lookup")
@router.post("/api/candidate/lookup")
def candidate_lookup(data: CandidateLookupRequest):
    psn = data.psn.strip()
    code_1 = data.code_1.strip().upper()
    
    if not psn or not code_1:
        raise HTTPException(status_code=400, detail="Both PSN and Registration Code 1 are required.")
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, psn, name, amended_name, code_1, mda, exam_code,
               proposed_rank, proposed_gl, group_category,
               exam_date, batch_session, batch_time, accreditation_time,
               phone, email, passport_photo, registration_status
        FROM candidate_roster
        WHERE psn = ? AND UPPER(code_1) = ?
    """, (psn, code_1))
    
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(
            status_code=401,
            detail=f"Authentication Failed: No officer matched PSN '{psn}' with Registration Code '{code_1}'. Please check your slip and try again."
        )
        
    return {
        "success": True,
        "candidate": dict(row)
    }

@router.post("/candidate/complete-registration")
@router.post("/api/candidate/complete-registration")
def complete_candidate_registration(data: CompleteRegistrationRequest):
    psn = data.psn.strip()
    code_1 = data.code_1.strip().upper()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM candidate_roster WHERE psn = ? AND UPPER(code_1) = ?", (psn, code_1))
    existing = cursor.fetchone()
    if not existing:
        conn.close()
        raise HTTPException(status_code=401, detail="Authentication Failed: Invalid PSN or Registration Code.")
        
    cursor.execute("""
        UPDATE candidate_roster
        SET amended_name = ?, phone = ?, email = ?, passport_photo = ?,
            registration_status = 'registered', registered_at = CURRENT_TIMESTAMP
        WHERE psn = ?
    """, (
        (data.amended_name or "").strip(),
        (data.phone or "").strip(),
        (data.email or "").strip().lower(),
        data.passport_photo,
        psn
    ))
    
    cursor.execute("""
        SELECT id, psn, name, amended_name, code_1, mda, exam_code,
               proposed_rank, proposed_gl, group_category,
               exam_date, batch_session, batch_time, accreditation_time,
               phone, email, passport_photo, registration_status, registered_at
        FROM candidate_roster
        WHERE psn = ?
    """, (psn,))
    
    updated_row = cursor.fetchone()
    conn.commit()
    conn.close()
    
    return {
        "success": True,
        "message": "Registration verified and photocard generated successfully!",
        "candidate": dict(updated_row)
    }

@router.get("/candidate/photocard/{psn}")
@router.get("/api/candidate/photocard/{psn}")
def get_candidate_photocard(psn: str):
    query_psn = psn.strip()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, psn, name, amended_name, code_1, mda, exam_code,
               proposed_rank, proposed_gl, group_category,
               exam_date, batch_session, batch_time, accreditation_time,
               phone, email, passport_photo, registration_status, registered_at
        FROM candidate_roster
        WHERE psn = ?
    """, (query_psn,))
    
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail=f"No registration photocard found for PSN: {query_psn}")
        
    return {
        "success": True,
        "photocard": dict(row)
    }

@router.post("/exam/start-with-token")
@router.post("/api/exam/start-with-token")
def start_exam_with_token(data: StartExamWithTokenRequest):
    psn = data.psn.strip()
    token_code = data.token_code.strip()
    
    if not psn or not token_code:
        raise HTTPException(status_code=400, detail="Both PSN and 5-digit Exam Token are required.")
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Check if exam is open
    status = get_setting("exam_status", "open")
    if status == "closed":
        conn.close()
        raise HTTPException(status_code=403, detail="The CBT Examination portal is currently closed by Administrator.")
        
    # 2. Check single attempt protection in submissions (Sandbox bypass for 999xxx test accounts)
    if not psn.startswith("999"):
        cursor.execute("SELECT id, submitted_at, score_percentage FROM submissions WHERE psn = ?", (psn,))
        sub = cursor.fetchone()
        if sub:
            conn.close()
            raise HTTPException(
                status_code=400,
                detail=f"This examination has already been completed for PSN {psn} on {sub['submitted_at']} (Score: {sub['score_percentage']}%). Retakes are restricted."
            )
        
    # 3. Validate Token
    cursor.execute("SELECT id, token_code, status, assigned_to_psn FROM exam_tokens WHERE token_code = ?", (token_code,))
    tok = cursor.fetchone()
    if not tok:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Invalid Exam Access Token '{token_code}'. Please check your token slip.")
        
    # Check if assigned to another PSN (Sandbox test accounts can re-use test tokens)
    if tok["assigned_to_psn"] and tok["assigned_to_psn"] != psn and not psn.startswith("999"):
        conn.close()
        raise HTTPException(
            status_code=403,
            detail=f"Access Denied: This 5-digit token ({token_code}) has already been activated by another officer."
        )
        
    # If unassigned, bind atomically to this PSN (or re-bind if test account)
    if not tok["assigned_to_psn"] or psn.startswith("999"):
        cursor.execute("""
            UPDATE exam_tokens
            SET assigned_to_psn = ?, status = 'active', activated_at = CURRENT_TIMESTAMP
            WHERE token_code = ?
        """, (psn, token_code))
        
    # 4. Fetch candidate details from candidate_roster
    cursor.execute("""
        SELECT id, psn, name, amended_name, mda, exam_code, proposed_rank, proposed_gl, group_category, email
        FROM candidate_roster
        WHERE psn = ?
    """, (psn,))
    cand = cursor.fetchone()
    
    if not cand:
        # Fallback to candidates table
        cursor.execute("SELECT id, name, psn, email, grade_level, mda FROM candidates WHERE psn = ?", (psn,))
        c_old = cursor.fetchone()
        if c_old:
            cand = {
                "id": c_old["id"],
                "psn": c_old["psn"],
                "name": c_old["name"],
                "amended_name": c_old["name"],
                "mda": c_old["mda"],
                "exam_code": "OHOS/C1",
                "proposed_rank": "Officer",
                "proposed_gl": c_old["grade_level"],
                "group_category": "C",
                "email": c_old["email"]
            }
        else:
            conn.close()
            raise HTTPException(status_code=404, detail=f"Officer record with PSN '{psn}' not found in candidate roster.")
            
    # 5. Fetch questions matching candidate's exam_code
    paper_code = cand["exam_code"]
    mda = cand["mda"]
    group_cat = cand["group_category"].replace("GROUP ", "").strip()
    
    q_rows, loaded_paper = fetch_cbt_questions(cursor, paper_code, mda, group_cat)
    
    conn.commit()
    conn.close()
    
    if not q_rows:
        raise HTTPException(status_code=404, detail="No examination questions found for this cadre.")
        
    questions = []
    for r in q_rows:
        questions.append({
            "id": r["id"],
            "number": r["question_number"],
            "question": r["question_text"],
            "options": {
                "A": r["option_a"],
                "B": r["option_b"],
                "C": r["option_c"],
                "D": r["option_d"]
            }
        })
        
    display_name = cand["amended_name"] if cand["amended_name"] else cand["name"]
    
    return {
        "success": True,
        "candidate_id": cand.get("id"),
        "candidate": {
            "name": display_name,
            "psn": cand["psn"],
            "email": cand.get("email") or f"{psn}@cbt.kw.gov.ng",
            "grade_level": cand.get("proposed_gl") or "10",
            "mda": cand["mda"],
            "paper_code": loaded_paper
        },
        "paper_code": loaded_paper,
        "total_questions": len(questions),
        "duration_minutes": 20,
        "questions": questions
    }

@router.get("/admin/tokens")
@router.get("/api/admin/tokens")
def get_admin_tokens(auth: bool = Depends(verify_admin_auth)):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) as total FROM exam_tokens")
    total = cursor.fetchone()["total"]
    
    cursor.execute("SELECT COUNT(*) as unassigned FROM exam_tokens WHERE status = 'unassigned'")
    unassigned = cursor.fetchone()["unassigned"]
    
    cursor.execute("SELECT COUNT(*) as active FROM exam_tokens WHERE status = 'active'")
    active = cursor.fetchone()["active"]
    
    cursor.execute("SELECT COUNT(*) as completed FROM exam_tokens WHERE status = 'completed'")
    completed = cursor.fetchone()["completed"]
    
    # Return 100 sample unassigned tokens for printing
    cursor.execute("SELECT token_code FROM exam_tokens WHERE status = 'unassigned' ORDER BY id ASC LIMIT 250")
    sample_tokens = [r["token_code"] for r in cursor.fetchall()]
    
    conn.close()
    
    return {
        "summary": {
            "total_tokens": total,
            "unassigned": unassigned,
            "active": active,
            "completed": completed
        },
        "sample_unassigned_tokens": sample_tokens
    }

@router.get("/result/{psn}")
@router.get("/api/result/{psn}")
@router.post("/retrieve-result")
@router.post("/api/retrieve-result")
def retrieve_result(
    psn: Optional[str] = None,
    data: Optional[RetrieveResultRequest] = None
):
    raise HTTPException(
        status_code=403,
        detail="Candidate examination result checking is disabled. In accordance with Kwara State Civil Service Commission regulations, examination scores are confidential and will be communicated through official Ministry / Department / Agency channels."
    )

@router.post("/send-result-email")
@router.post("/api/send-result-email")
def send_result_email_endpoint(data: SendResultEmailRequest, background_tasks: BackgroundTasks = BackgroundTasks()):
    raise HTTPException(
        status_code=403,
        detail="Examination result emailing is disabled. Official results will be published through designated Commission channels."
    )

@router.get("/admin/submissions")
@router.get("/api/admin/submissions")
def get_admin_submissions(auth: bool = Depends(verify_admin_auth)):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, candidate_name, psn, email, grade_level, mda,
               total_questions, correct_count, score_percentage, grade_remark,
               time_taken_seconds, submitted_at
        FROM submissions
        ORDER BY id DESC
    """)
    rows = cursor.fetchall()
    
    # Photocard & Roster stats
    total_roster = 2499
    photocards_printed = 0
    try:
        cursor.execute("SELECT COUNT(*) as cnt FROM candidate_roster")
        r_row = cursor.fetchone()
        if r_row:
            total_roster = r_row["cnt"] if isinstance(r_row, dict) else r_row[0]

        cursor.execute("""
            SELECT COUNT(*) as cnt FROM candidate_roster 
            WHERE registration_status IN ('registered', 'tested') OR registered_at IS NOT NULL
        """)
        p_row = cursor.fetchone()
        if p_row:
            photocards_printed = p_row["cnt"] if isinstance(p_row, dict) else p_row[0]
    except Exception as e:
        pass

    conn.close()
    
    submissions = [dict(r) for r in rows]
    
    total_count = len(submissions)
    avg_score = round(sum(s["score_percentage"] for s in submissions) / total_count, 2) if total_count > 0 else 0.0
    passed_count = sum(1 for s in submissions if s["score_percentage"] >= 50)
    pass_rate = round((passed_count / total_count) * 100, 2) if total_count > 0 else 0.0
    photocards_pct = round((photocards_printed / total_roster) * 100, 1) if total_roster > 0 else 0.0
    
    return {
        "summary": {
            "total_submissions": total_count,
            "average_score": avg_score,
            "pass_rate": pass_rate,
            "passed_count": passed_count,
            "failed_count": total_count - passed_count,
            "total_roster": total_roster,
            "photocards_printed": photocards_printed,
            "photocards_pct": photocards_pct
        },
        "exam_status": get_setting("exam_status", "open"),
        "submissions": submissions
    }

@router.get("/admin/registrations")
@router.get("/api/admin/registrations")
def get_admin_registrations(auth: bool = Depends(verify_admin_auth)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT psn, name, amended_name, mda, proposed_rank, proposed_gl, group_category, exam_code,
               phone, email, registration_status, registered_at
        FROM candidate_roster
        WHERE registration_status IN ('registered', 'tested') OR registered_at IS NOT NULL
        ORDER BY registered_at DESC
    """)
    rows = cursor.fetchall()
    
    cursor.execute("SELECT COUNT(*) as cnt FROM candidate_roster")
    tot_row = cursor.fetchone()
    total_candidates = tot_row["cnt"] if isinstance(tot_row, dict) else (tot_row[0] if tot_row else 2499)
    conn.close()
    
    registrations = []
    for r in rows:
        d = dict(r)
        if d.get("registered_at") and hasattr(d["registered_at"], "strftime"):
            d["registered_at_str"] = d["registered_at"].strftime("%d-%b-%Y %I:%M %p")
        else:
            d["registered_at_str"] = str(d.get("registered_at") or "N/A")
        registrations.append(d)

    return {
        "total_candidates": total_candidates,
        "total_registered": len(registrations),
        "percentage": round((len(registrations) / total_candidates) * 100, 2) if total_candidates > 0 else 0.0,
        "registrations": registrations
    }

@router.get("/admin/registrations/excel")
@router.get("/api/admin/registrations/excel")
def export_photocards_excel(auth: bool = Depends(verify_admin_auth)):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            psn, 
            name, 
            amended_name, 
            mda, 
            proposed_rank, 
            proposed_gl, 
            exam_code,
            phone, 
            email, 
            registration_status, 
            registered_at
        FROM candidate_roster
        WHERE registration_status IN ('registered', 'tested') OR registered_at IS NOT NULL
        ORDER BY registered_at DESC
    """)
    rows = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) as cnt FROM candidate_roster")
    tot_row = cursor.fetchone()
    total_candidates = tot_row["cnt"] if isinstance(tot_row, dict) else (tot_row[0] if tot_row else 2499)
    conn.close()

    total_registered = len(rows)
    pct = (total_registered / total_candidates * 100) if total_candidates > 0 else 0.0

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Photocards Generated"
    ws.views.sheetView[0].showGridLines = True

    primary_green = "004D40"
    light_green = "E0F2F1"
    border_gray = "CCCCCC"
    thin_border = Border(
        left=Side(style='thin', color=border_gray),
        right=Side(style='thin', color=border_gray),
        top=Side(style='thin', color=border_gray),
        bottom=Side(style='thin', color=border_gray)
    )

    # Title Block
    ws.merge_cells("A1:K1")
    ws["A1"] = "KWARA STATE CIVIL SERVICE COMMISSION"
    ws["A1"].font = Font(name="Arial", size=15, bold=True, color="FFFFFF")
    ws["A1"].fill = PatternFill(start_color=primary_green, end_color=primary_green, fill_type="solid")
    ws["A1"].alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 28

    ws.merge_cells("A2:K2")
    ws["A2"] = "2026 Promotion CBT Examination - Verified Candidates & Photocard Generation Log"
    ws["A2"].font = Font(name="Arial", size=11, bold=True, color="FFFFFF")
    ws["A2"].fill = PatternFill(start_color="00796B", end_color="00796B", fill_type="solid")
    ws["A2"].alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[2].height = 22

    ws.merge_cells("A3:K3")
    ws["A3"] = f"Report Generated: {datetime.now().strftime('%d-%b-%Y %I:%M %p')} | Total Photocards Generated: {total_registered} of {total_candidates} ({pct:.2f}%)"
    ws["A3"].font = Font(name="Arial", size=10, italic=True, color="333333")
    ws["A3"].alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[3].height = 20

    headers = [
        "S/N", "PSN", "Roster Name", "Verified / Amended Name", 
        "MDA", "Proposed Rank", "GL", "Exam Code", 
        "Phone Number", "Email Address", "Photocard Generated At"
    ]

    header_row = 5
    ws.row_dimensions[header_row].height = 25
    for col_idx, h in enumerate(headers, 1):
        cell = ws.cell(row=header_row, column=col_idx, value=h)
        cell.font = Font(name="Arial", size=10, bold=True, color="FFFFFF")
        cell.fill = PatternFill(start_color=primary_green, end_color=primary_green, fill_type="solid")
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = thin_border

    for idx, r in enumerate(rows, 1):
        curr_row = header_row + idx
        ws.row_dimensions[curr_row].height = 20
        reg_time_str = r["registered_at"].strftime("%d-%b-%Y %I:%M:%S %p") if r.get("registered_at") and hasattr(r["registered_at"], "strftime") else str(r.get("registered_at") or "N/A")
        row_vals = [
            idx,
            r["psn"],
            r["name"],
            r["amended_name"] or r["name"],
            r["mda"],
            r["proposed_rank"],
            r["proposed_gl"],
            r["exam_code"],
            r["phone"] or "N/A",
            r["email"] or "N/A",
            reg_time_str
        ]
        is_even = (idx % 2 == 0)
        row_fill = PatternFill(start_color=light_green if is_even else "FFFFFF", fill_type="solid")

        for c_idx, val in enumerate(row_vals, 1):
            cell = ws.cell(row=curr_row, column=c_idx, value=val)
            cell.font = Font(name="Arial", size=9)
            cell.fill = row_fill
            cell.border = thin_border
            if c_idx in [1, 2, 7, 8, 11]:
                cell.alignment = Alignment(horizontal="center", vertical="center")
            else:
                cell.alignment = Alignment(horizontal="left", vertical="center")

    for col in ws.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            if cell.row < 4:
                continue
            v = str(cell.value or "")
            if len(v) > max_len:
                max_len = len(v)
        ws.column_dimensions[col_letter].width = max(max_len + 3, 11)

    out = io.BytesIO()
    wb.save(out)
    excel_content = out.getvalue()
    
    filename = f"Kwara_CSC_2026_Photocard_Registrations_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
    return Response(
        content=excel_content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@router.post("/admin/reset-candidate")
@router.post("/api/admin/reset-candidate")
def reset_candidate_for_retake(data: ResetCandidateRequest, auth: bool = Depends(verify_admin_auth)):
    query_psn = data.psn.strip()
    if not query_psn:
        raise HTTPException(status_code=400, detail="PSN is required.")
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, candidate_id, candidate_name, psn, email, grade_level, mda,
               total_questions, correct_count, score_percentage, grade_remark,
               time_taken_seconds, submitted_at, answers_json
        FROM submissions
        WHERE psn = ?
    """, (query_psn,))
    rows = cursor.fetchall()
    if not rows:
        conn.close()
        raise HTTPException(status_code=404, detail=f"No active submission found for PSN: {query_psn}.")
        
    for r in rows:
        cursor.execute("""
            INSERT INTO archived_submissions (
                original_submission_id, candidate_id, candidate_name, psn, email,
                grade_level, mda, total_questions, correct_count, score_percentage,
                grade_remark, time_taken_seconds, submitted_at, answers_json, reason
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            r["id"], r.get("candidate_id"), r.get("candidate_name"), r.get("psn"), r.get("email"),
            r.get("grade_level"), r.get("mda"), r.get("total_questions"), r.get("correct_count"),
            r.get("score_percentage"), r.get("grade_remark"), r.get("time_taken_seconds"),
            r.get("submitted_at"), str(r.get("answers_json")), data.reason or "Approved by Admin for Retake"
        ))
        
    cursor.execute("DELETE FROM submissions WHERE psn = ?", (query_psn,))
    conn.commit()
    conn.close()
    
    return {
        "success": True,
        "message": f"Officer with PSN {query_psn} has been unlocked for a CBT retake. Previous record archived safely."
    }

@router.get("/results/excel")
@router.get("/api/results/excel")
def export_results_excel(auth: bool = Depends(verify_admin_auth)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, candidate_name, psn, email, grade_level, mda,
               correct_count, total_questions, score_percentage,
               (correct_count * 2) as marks_obtained,
               (total_questions * 2) as max_marks,
               grade_remark, time_taken_seconds, submitted_at
        FROM submissions
        ORDER BY id ASC
    """)
    rows = cursor.fetchall()
    conn.close()
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "CBT Results"
    ws.views.sheetView[0].showGridLines = True
    
    primary_green = "004D40"
    light_green = "E0F2F1"
    border_gray = "CCCCCC"
    
    # Title Block
    ws.merge_cells("A1:L1")
    ws["A1"] = "KWARA STATE CIVIL SERVICE COMMISSION"
    ws["A1"].font = Font(name="Arial", size=16, bold=True, color="FFFFFF")
    ws["A1"].fill = PatternFill(start_color=primary_green, end_color=primary_green, fill_type="solid")
    ws["A1"].alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 32
    
    ws.merge_cells("A2:L2")
    ws["A2"] = "2026 Promotion Evaluation CBT Examination - Official Results Roster"
    ws["A2"].font = Font(name="Arial", size=12, bold=True, color="FFFFFF")
    ws["A2"].fill = PatternFill(start_color="00796B", end_color="00796B", fill_type="solid")
    ws["A2"].alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[2].height = 24
    
    ws.merge_cells("A3:L3")
    ws["A3"] = f"Report Generated On: {datetime.now().strftime('%d-%b-%Y %I:%M %p')} | Total Candidates: {len(rows)}"
    ws["A3"].font = Font(name="Arial", size=10, italic=True, color="333333")
    ws["A3"].alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[3].height = 20
    
    # Table Headers
    headers = [
        "S/N", "Candidate Name", "PSN", "Email Address",
        "Grade Level", "MDA / Organization", "Correct (of 50)",
        "Marks (of 100)", "Score (%)", "Performance Remark",
        "Time Spent", "Submission Date & Time"
    ]
    
    header_row = 5
    ws.row_dimensions[header_row].height = 26
    thin_border = Border(
        left=Side(style='thin', color=border_gray),
        right=Side(style='thin', color=border_gray),
        top=Side(style='thin', color=border_gray),
        bottom=Side(style='thin', color=border_gray)
    )
    
    for col_idx, header in enumerate(headers, start=1):
        cell = ws.cell(row=header_row, column=col_idx, value=header)
        cell.font = Font(name="Arial", size=11, bold=True, color="FFFFFF")
        cell.fill = PatternFill(start_color=primary_green, end_color=primary_green, fill_type="solid")
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = thin_border
        
    for idx, r in enumerate(rows, start=1):
        current_row = header_row + idx
        ws.row_dimensions[current_row].height = 22
        mins = r["time_taken_seconds"] // 60
        secs = r["time_taken_seconds"] % 60
        time_str = f"{mins}m {secs}s"
        
        row_data = [
            idx,
            r["candidate_name"],
            r["psn"],
            r["email"],
            r["grade_level"],
            r["mda"],
            f"{r['correct_count']} / {r['total_questions']}",
            r["marks_obtained"],
            f"{r['score_percentage']:.1f}%",
            r["grade_remark"],
            time_str,
            r["submitted_at"]
        ]
        
        is_even = (idx % 2 == 0)
        row_fill = PatternFill(start_color=light_green if is_even else "FFFFFF", fill_type="solid")
        
        for col_idx, val in enumerate(row_data, start=1):
            cell = ws.cell(row=current_row, column=col_idx, value=val)
            cell.font = Font(name="Arial", size=10)
            cell.border = thin_border
            cell.fill = row_fill
            
            if col_idx in [1, 7, 8, 9, 11]:
                cell.alignment = Alignment(horizontal="center", vertical="center")
            elif col_idx in [2, 3, 4, 5, 6, 10]:
                cell.alignment = Alignment(horizontal="left", vertical="center")
            else:
                cell.alignment = Alignment(horizontal="center", vertical="center")
                
            if col_idx == 9:
                score_val = r["score_percentage"]
                if score_val >= 70:
                    cell.font = Font(name="Arial", size=10, bold=True, color="00796B")
                elif score_val < 50:
                    cell.font = Font(name="Arial", size=10, bold=True, color="C62828")
                    
    for col in ws.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            if cell.row < 4:
                continue
            val_str = str(cell.value or "")
            if len(val_str) > max_len:
                max_len = len(val_str)
        ws.column_dimensions[col_letter].width = max(max_len + 4, 12)
        
    output = io.BytesIO()
    wb.save(output)
    excel_content = output.getvalue()
    
    filename = f"Kwara_HOS_CBT_Results_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
    return Response(
        content=excel_content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

@router.get("/results/csv")
@router.get("/api/results/csv")
def export_results_csv(auth: bool = Depends(verify_admin_auth)):
    conn = get_db_connection()
    df = pd.read_sql_query("""
        SELECT id AS 'S/N',
               candidate_name AS 'Candidate Name',
               psn AS 'PSN',
               email AS 'Email Address',
               grade_level AS 'Grade Level',
               mda AS 'MDA',
               correct_count AS 'Correct Questions',
               total_questions AS 'Total Questions',
               (correct_count * 2) AS 'Marks Obtained (Max 100)',
               score_percentage AS 'Score Percentage',
               grade_remark AS 'Performance Remark',
               time_taken_seconds AS 'Time Taken (Seconds)',
               submitted_at AS 'Submission Timestamp'
        FROM submissions
        ORDER BY id ASC
    """, conn)
    conn.close()
    
    stream = io.StringIO()
    df.to_csv(stream, index=False)
    csv_bytes = stream.getvalue().encode("utf-8")
    
    filename = f"Kwara_HOS_CBT_Results_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    return Response(
        content=csv_bytes,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

@router.post("/admin/reset-submission/{submission_id}")
@router.post("/api/admin/reset-submission/{submission_id}")
def reset_submission(submission_id: int, auth: bool = Depends(verify_admin_auth)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM submissions WHERE id = ?", (submission_id,))
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    
    if deleted == 0:
        raise HTTPException(status_code=404, detail="Submission not found.")
    return {"success": True, "message": "Candidate record reset successfully."}

@router.get("/admin/roster/excel")
@router.get("/api/admin/roster/excel")
def download_candidate_roster_excel(auth: bool = Depends(verify_admin_auth)):
    possible_paths = [
        os.path.join(STATIC_DIR, "Kwara_CSC_2026_CBT_Candidate_Registration_Slips_Master.xlsx") if STATIC_DIR else "",
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Kwara_CSC_2026_CBT_Candidate_Registration_Slips_Master.xlsx"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "Kwara_CSC_2026_CBT_Candidate_Registration_Slips_Master.xlsx"),
        "Kwara_CSC_2026_CBT_Candidate_Registration_Slips_Master.xlsx"
    ]
    for p in possible_paths:
        if p and os.path.exists(p):
            with open(p, "rb") as f:
                content = f.read()
            return Response(
                content=content,
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={"Content-Disposition": 'attachment; filename="Kwara_CSC_2026_CBT_Candidate_Registration_Slips_Master.xlsx"'}
            )
            
    # Fallback directly from DB
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT psn, name, code_1, proposed_rank, proposed_gl, mda,
               group_category, exam_code, exam_date, batch_session, batch_time, accreditation_time
        FROM candidate_roster
        ORDER BY id ASC
    """)
    rows = cursor.fetchall()
    conn.close()
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Registration Codes"
    ws.append(["S/N", "PSN", "Officer Full Name", "Registration Clearance Code (Code 1)", "Proposed Rank", "Grade Level", "MDA", "Group", "Exam Code", "Exam Date", "Batch Session", "Exam Time", "Accreditation Time"])
    for idx, r in enumerate(rows, 1):
        ws.append([idx, r["psn"], r["name"], r["code_1"], r["proposed_rank"], r["proposed_gl"], r["mda"], r["group_category"], r["exam_code"], r["exam_date"], r["batch_session"], r["batch_time"], r["accreditation_time"]])
        
    out = io.BytesIO()
    wb.save(out)
    return Response(
        content=out.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="Kwara_CSC_2026_CBT_Candidate_Registration_Slips_Master.xlsx"'}
    )

@router.get("/admin/roster/slips")
@router.get("/api/admin/roster/slips")
def view_candidate_registration_slips(auth: bool = Depends(verify_admin_auth)):
    possible_paths = [
        os.path.join(STATIC_DIR, "slips.html") if STATIC_DIR else "",
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "candidate_registration_slips.html"),
        "candidate_registration_slips.html"
    ]
    for p in possible_paths:
        if p and os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Registration Slips not found. Please contact Administrator.</h1>", status_code=404)

@router.get("/admin/tokens/excel")
@router.get("/api/admin/tokens/excel")
def download_tokens_inventory_excel(auth: bool = Depends(verify_admin_auth)):
    possible_paths = [
        os.path.join(STATIC_DIR, "scratch_cards", "Kwara_CSC_2026_CBT_Scratch_Cards_Master_Inventory.xlsx") if STATIC_DIR else "",
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Kwara_CSC_2026_CBT_Scratch_Cards", "Kwara_CSC_2026_CBT_Scratch_Cards_Master_Inventory.xlsx")
    ]
    for p in possible_paths:
        if p and os.path.exists(p):
            return FileResponse(
                path=p,
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                filename="Kwara_CSC_2026_CBT_Scratch_Cards_Master_Inventory.xlsx"
            )

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, token_code, status, assigned_to_psn FROM exam_tokens ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Tokens Inventory"
    ws.append(["S/N", "Serial Number", "5-Digit Exam Token (Code 2)", "Token Status", "Assigned PSN"])
    for idx, r in enumerate(rows, 1):
        ws.append([idx, f"CSC-2026-{idx:04d}", r["token_code"], r["status"], r.get("assigned_to_psn") or "Unassigned"])

    out = io.BytesIO()
    wb.save(out)
    return Response(
        content=out.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="Kwara_CSC_2026_CBT_Scratch_Cards_Master_Inventory.xlsx"'}
    )

app.include_router(router)

