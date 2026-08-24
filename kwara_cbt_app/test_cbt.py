import sys
import os
import unittest
import json
import time

app_dir = os.path.dirname(os.path.abspath(__file__))
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

from fastapi import HTTPException
from app import (
    app, get_exam_info, start_exam, submit_exam,
    admin_login, get_admin_submissions, export_results_excel, export_results_csv,
    toggle_exam_status,
    StartExamRequest, SubmitExamRequest, AdminLoginRequest
)
from parser import seed_database
from database import get_db_connection, init_db, set_setting

class TestKwaraCBTDirect(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("\n--- Initializing database and seeding questions ---")
        init_db()
        seed_database()
        set_setting("exam_status", "open")
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("DELETE FROM submissions")
        c.execute("DELETE FROM candidates")
        conn.commit()
        conn.close()

    def test_01_info_endpoint(self):
        data = get_exam_info()
        self.assertEqual(data["questions_per_exam"], 50)
        self.assertEqual(data["default_duration_minutes"], 20)
        self.assertEqual(data["exam_status"], "open")
        self.assertIn("Kwara State Office of Head of Service", data["title"])
        self.assertIn("GL 08", data["grade_levels"])
        self.assertIn("GL 06-07", data["grade_levels"])
        self.assertIn("GL 09", data["grade_levels"])
        print("[PASS] /api/info verified (20 mins, Kwara State Office of Head of Service)")

    def test_02_start_exam_all_grades(self):
        for grade in ["GL 06-07", "GL 08", "GL 09"]:
            req = StartExamRequest(
                name=f"Officer Test ({grade})",
                psn=f"84920{grade[-1]}",
                email=f"test_{grade.replace(' ', '_')}@kwarastate.gov.ng",
                grade_level=grade,
                mda="Office of the Head of Service"
            )
            data = start_exam(req)
            self.assertTrue(data["success"])
            self.assertEqual(data["total_questions"], 50)
            self.assertEqual(data["duration_minutes"], 20)
            self.assertEqual(len(data["questions"]), 50)
            
            for q in data["questions"]:
                self.assertTrue(1 <= q["number"] <= 50)
                self.assertTrue(bool(q["question"]))
                self.assertTrue(bool(q["options"]["A"]))
                self.assertTrue(bool(q["options"]["B"]))
                self.assertTrue(bool(q["options"]["C"]))
                self.assertTrue(bool(q["options"]["D"]))
                self.assertNotIn("correct_answer", q)
            print(f"[PASS] /api/start-exam for {grade} verified")

    def test_03_submit_exam_and_single_attempt_enforcement(self):
        psn_test = "771829"
        req = StartExamRequest(
            name="Aishat Mohammed",
            psn=psn_test,
            email="aishat.m@kwarastate.gov.ng",
            grade_level="GL 08",
            mda="Office of the Head of Service"
        )
        start_data = start_exam(req)
        cand_id = start_data["candidate_id"]

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT question_number, correct_answer FROM questions WHERE grade_level = 'GL 08'")
        key_map = {str(r["question_number"]): r["correct_answer"].strip().upper() for r in cursor.fetchall()}
        conn.close()

        simulated_answers = {}
        for q_num in range(1, 51):
            q_str = str(q_num)
            if q_num <= 42:
                simulated_answers[q_str] = key_map[q_str]
            else:
                simulated_answers[q_str] = "X"

        sub_req = SubmitExamRequest(
            candidate_id=cand_id,
            name="Aishat Mohammed",
            psn=psn_test,
            email="aishat.m@kwarastate.gov.ng",
            grade_level="GL 08",
            mda="Office of the Head of Service",
            answers=simulated_answers,
            time_taken_seconds=950
        )

        sub_data = submit_exam(sub_req)
        self.assertTrue(sub_data["success"])
        self.assertEqual(sub_data["candidate"]["psn"], psn_test)
        self.assertEqual(sub_data["score"]["correct_count"], 42)
        self.assertEqual(sub_data["score"]["score_percentage"], 84.0)
        self.assertEqual(sub_data["score"]["grade_remark"], "Distinction (Excellent)")
        print(f"[PASS] /api/submit-exam verified (42/50 = 84% Distinction)")

        # Verify duplicate attempt is strictly BLOCKED
        with self.assertRaises(HTTPException) as ctx:
            start_exam(req)
        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("already completed this evaluation", ctx.exception.detail)
        print("[PASS] Single attempt enforcement verified: duplicate attempt blocked with 400 error")

    def test_04_admin_auth_and_exports(self):
        login_res = admin_login(AdminLoginRequest(username="admin", password="admin123"))
        self.assertTrue(login_res["success"])
        self.assertTrue(bool(login_res["token"]))
        print("[PASS] /api/admin/login verified with valid credentials")

        admin_data = get_admin_submissions(auth=True)
        self.assertGreaterEqual(admin_data["summary"]["total_submissions"], 1)
        self.assertEqual(admin_data["exam_status"], "open")
        print(f"[PASS] /api/admin/submissions verified: {admin_data['summary']['total_submissions']} submission(s)")

        excel_res = export_results_excel(auth=True)
        excel_bytes = excel_res.body
        self.assertGreater(len(excel_bytes), 1000)
        print(f"[PASS] /api/results/excel export verified ({len(excel_bytes)} bytes)")

        csv_res = export_results_csv(auth=True)
        csv_text = csv_res.body.decode("utf-8")
        self.assertIn("PSN", csv_text)
        self.assertIn("771829", csv_text)
        print("[PASS] /api/results/csv export verified")

    def test_05_admin_close_and_open_exam(self):
        # 1. Admin closes exam
        toggle_res = toggle_exam_status(auth=True)
        self.assertEqual(toggle_res["exam_status"], "closed")
        print("[PASS] Admin toggled exam to CLOSED")

        # 2. Candidate attempts to start when closed -> must be blocked with 403
        req = StartExamRequest(
            name="Late Candidate",
            psn="999999",
            email="late@kwarastate.gov.ng",
            grade_level="GL 08",
            mda="Office of the Head of Service"
        )
        with self.assertRaises(HTTPException) as ctx:
            start_exam(req)
        self.assertEqual(ctx.exception.status_code, 403)
        self.assertIn("closed", ctx.exception.detail.lower())
        print("[PASS] Candidate start-exam correctly blocked with 403 when exam is CLOSED")

        # 3. Admin re-opens exam
        toggle_res2 = toggle_exam_status(auth=True)
        self.assertEqual(toggle_res2["exam_status"], "open")
        print("[PASS] Admin toggled exam back to OPEN")

        # 4. Candidate can now start
        start_res = start_exam(req)
        self.assertTrue(start_res["success"])
        print("[PASS] Candidate can successfully start exam after Admin re-opens it")

if __name__ == "__main__":
    unittest.main()
