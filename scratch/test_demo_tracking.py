import os
import sys

sys.path.insert(0, os.path.abspath("kwara_cbt_app"))
from app import (
    demo_candidate_lookup,
    demo_start,
    demo_submit,
    get_admin_demo_analytics,
    export_demo_excel,
    DemoStartRequest,
    DemoSubmitRequest
)
from database import get_db_connection

class MockRequest:
    def __init__(self):
        self.client = type("Client", (), {"host": "127.0.0.1"})()
        self.headers = {"user-agent": "Mozilla/5.0 EndToEndTestRunner"}

req = MockRequest()

print("--- 1. Testing Candidate Lookup ---")
conn = get_db_connection()
cursor = conn.cursor()
cursor.execute("SELECT psn, name, mda, proposed_gl FROM candidate_roster LIMIT 1")
row = cursor.fetchone()
if not row:
    print("No candidates in roster!")
    sys.exit(1)

test_psn = row["psn"]
expected_name = row["name"]
print(f"Found candidate in roster: {test_psn} -> {expected_name}")

lookup_data = demo_candidate_lookup(psn=test_psn)
print("Lookup result:", lookup_data)
assert lookup_data.get("found") is True
assert lookup_data.get("name") == expected_name

print("\n--- 2. Testing Demo Start Telemetry ---")
session_id = "TEST-SESSION-E2E-999"
start_req = DemoStartRequest(
    session_id=session_id,
    psn=test_psn,
    name=expected_name,
    mda=lookup_data.get("mda", "Test MDA"),
    grade_level=lookup_data.get("grade_level", "GL 10"),
    device_type="Desktop (Windows 11 Chrome)"
)
start_res = demo_start(start_req, req)
print("Start result:", start_res)
assert start_res.get("success") is True

print("\n--- 3. Testing Demo Submission Telemetry ---")
submit_req = DemoSubmitRequest(
    session_id=session_id,
    psn=test_psn,
    name=expected_name,
    mda=lookup_data.get("mda", "Test MDA"),
    grade_level=lookup_data.get("grade_level", "GL 10"),
    device_type="Desktop (Windows 11 Chrome)",
    answered_count=40,
    correct_count=35,
    total_questions=40,
    score_percentage=87.5,
    time_taken_seconds=650,
    violations_count=0,
    violation_logs="[]",
    status="completed"
)
submit_res = demo_submit(submit_req, req)
print("Submit result:", submit_res)
assert submit_res.get("success") is True

print("\n--- 4. Testing Admin Demo Analytics Endpoint ---")
analytics = get_admin_demo_analytics()
print("Summary:", {
    "total_sessions": analytics.get("total_sessions"),
    "completed_sessions": analytics.get("completed_sessions"),
    "unique_candidates": analytics.get("unique_candidates"),
    "average_score": analytics.get("average_score"),
    "logs_count": len(analytics.get("logs", []))
})
assert analytics.get("total_sessions") >= 1
assert analytics.get("completed_sessions") >= 1

print("\n--- 5. Testing Demo Excel Export Endpoint ---")
excel_resp = export_demo_excel()
content = excel_resp.body if hasattr(excel_resp, 'body') else excel_resp.content
print("Excel content length:", len(content))
assert len(content) > 1000

print("\n--- 6. Cleaning Up Test Record ---")
cursor.execute("DELETE FROM demo_practice_logs WHERE session_id = ?", (session_id,))
conn.commit()
conn.close()
print("Test record cleaned up successfully.")
print("\n>>> ALL TESTS PASSED SUCCESSFULLY! <<<")
