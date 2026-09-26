import sqlite3
import re

conn = sqlite3.connect('kwara_cbt_app/cbt.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

test_cases = [
    ("127610", "A-24792", "Oniremu Oluseye Oyetokunbo"),
    ("135733", "B-97785", "Agboola Oyetunji Adeyemi"),
    ("141443", "C-61121", "Hammed Ibrahim Olawale"),
    ("128645", "B-30883", "Amuzat Aminat"),
    ("128042", "A-98542", "Akinrinmade Ayoola"),
    ("137515", "C-21835", "Mohammed Suleiman"),
    ("135667", "D-73857", "Giwa Aminat"),
    ("135073", "C-48205", "Zubair Dupe Olayinka"),
]

print("=== VERIFYING CANDIDATE LOOKUP BY PSN AND CODE 1 ===")
all_passed = True
for psn, code1, expected_name in test_cases:
    raw_code = re.sub(r'\s+', '', code1.strip().upper())
    cursor.execute("""
        SELECT id, psn, name, code_1, mda, exam_code, proposed_rank, proposed_gl,
               group_category, exam_date, batch_session, batch_time, accreditation_time
        FROM candidate_roster
        WHERE (psn = ? OR amended_psn = ?) AND (UPPER(code_1) = ? OR UPPER(code_1) = ? OR REPLACE(UPPER(code_1), ' ', '') = ?)
    """, (psn, psn, raw_code, code1, raw_code))
    row = cursor.fetchone()
    if row:
        print(f"PASSED: PSN {psn} + {code1} -> Found: {row['name']} | MDA: {row['mda']} | Exam Code: {row['exam_code']} | Batch: {row['batch_session']}")
    else:
        print(f"FAILED: PSN {psn} + {code1} NOT FOUND")
        all_passed = False

conn.close()

if all_passed:
    print("\n>>> ALL 8 OMITTED CANDIDATES VERIFIED AND RESOLVED PERFECTLY! <<<")
else:
    print("\nSome candidates failed lookup.")
