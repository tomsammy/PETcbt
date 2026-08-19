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
    StartExamRequest, SubmitExamRequest, AdminLoginRequest
)
from parser import seed_database
from database import get_db_connection, init_db

class TestKwaraCBTDirect(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("\n--- Initializing database and seeding questions ---")
        init_db()
        seed_database()
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("DELETE FROM submissions")
        c.execute("DELETE FROM candidates")
        conn.commit()
        conn.close()

    def test_01_info_endpoint(self):
        data = get_exam_info()
        self.assertEqual(data["questions_per_exam"], 50)
        self.assertIn("Kwara State Staff Development College", data["title"])
        self.assertIn("GL 08", data["grade_levels"])
        self.assertIn("GL 06-07", data["grade_levels"])
        self.assertIn("GL 09", data["grade_levels"])
        print("[PASS] /api/info verified")

    def test_02_start_exam_all_grades(self):
        for grade in ["GL 06-07", "GL 08", "GL 09"]:
            req = StartExamRequest(
                name=f"Officer Test ({grade})",
                psn=f"84920{grade[-1]}",
                email=f"test_{grade.replace(' ', '_')}@kwarastate.gov.ng",
                grade_level=grade,
                mda="Staff Development College"
            )
            data = start_exam(req)
            self.assertTrue(data["success"])
            self.assertEqual(data["total_questions"], 50)
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
            mda="Ministry of Finance"
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
            mda="Ministry of Finance",
            answers=simulated_answers,
            time_taken_seconds=1640
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

if __name__ == "__main__":
    unittest.main()
