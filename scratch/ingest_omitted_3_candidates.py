import os
import sys
import sqlite3
import openpyxl

# Candidate definitions
omitted_8 = [
    {
        "sn": 1,
        "name": "Oniremu Oluseye Oyetokunbo",
        "psn": "127610",
        "csc_file": "S.16282087",
        "sex": "F",
        "present_rank": "Assistant Chief Nursing Officer",
        "present_gl": "13",
        "proposed_rank": "Chief Nursing Officer",
        "proposed_gl": "14",
        "mda": "KWSUTH",
        "group_category": "GROUP A",
        "exam_code": "KWSUTH/A4",
        "exam_date": "Tuesday, 29th September 2026",
        "batch_session": "Session 1",
        "batch_time": "10:00 AM - 11:00 AM",
        "accreditation_time": "09:30 AM",
        "code_1": "A-24792",
        "phone": "08038271918",
        "email": "127610@cbt.kw.gov.ng",
        "lga": "Ifelodun"
    },
    {
        "sn": 2,
        "name": "Agboola Oyetunji Adeyemi",
        "psn": "135733",
        "csc_file": "S.319152302",
        "sex": "M",
        "present_rank": "Principal Store Officer II",
        "present_gl": "10",
        "proposed_rank": "Principal Store Officer I",
        "proposed_gl": "12",
        "mda": "OHOS",
        "group_category": "GROUP B",
        "exam_code": "OHOS/B4",
        "exam_date": "Tuesday, 29th September 2026",
        "batch_session": "Session 5",
        "batch_time": "02:00 PM - 03:00 PM",
        "accreditation_time": "01:30 PM",
        "code_1": "B-97785",
        "phone": "07062739105",
        "email": "135733@cbt.kw.gov.ng",
        "lga": "Oyun"
    },
    {
        "sn": 3,
        "name": "Hammed Ibrahim Olawale",
        "psn": "141443",
        "csc_file": "S.082131",
        "sex": "M",
        "present_rank": "Higher Store Officer",
        "present_gl": "8",
        "proposed_rank": "Senior Store Officer",
        "proposed_gl": "9",
        "mda": "OHOS",
        "group_category": "GROUP C",
        "exam_code": "OHOS/C3",
        "exam_date": "Wednesday, 30th September 2026",
        "batch_session": "Session 2",
        "batch_time": "11:00 AM - 12:00 PM",
        "accreditation_time": "10:30 AM",
        "code_1": "C-61121",
        "phone": "08140505550",
        "email": "141443@cbt.kw.gov.ng",
        "lga": "Offa"
    },
    {
        "sn": 4,
        "name": "Amuzat Aminat",
        "psn": "128645",
        "csc_file": "S.318694",
        "sex": "F",
        "present_rank": "Principal Nursing Officer",
        "present_gl": "12",
        "proposed_rank": "Assistant Chief Nursing Officer",
        "proposed_gl": "13",
        "mda": "KWSUTH",
        "group_category": "GROUP B",
        "exam_code": "KWSUTH/B4",
        "exam_date": "Tuesday, 29th September 2026",
        "batch_session": "Session 3",
        "batch_time": "12:00 PM - 01:00 PM",
        "accreditation_time": "11:30 AM",
        "code_1": "B-30883",
        "phone": "08135545164",
        "email": "128645@cbt.kw.gov.ng",
        "lga": "Ogbomosho North"
    },
    {
        "sn": 5,
        "name": "Akinrinmade Ayoola",
        "psn": "128042",
        "csc_file": "S.318619",
        "sex": "F",
        "present_rank": "Assistant Chief Nursing Supt.",
        "present_gl": "13",
        "proposed_rank": "Chief Nursing Supt.",
        "proposed_gl": "14",
        "mda": "HMB",
        "group_category": "GROUP A",
        "exam_code": "HMB/A3",
        "exam_date": "Tuesday, 29th September 2026",
        "batch_session": "Session 1",
        "batch_time": "10:00 AM - 11:00 AM",
        "accreditation_time": "09:30 AM",
        "code_1": "A-98542",
        "phone": "08023309439",
        "email": "128042@cbt.kw.gov.ng",
        "lga": "Ifelodun"
    },
    {
        "sn": 6,
        "name": "Mohammed Suleiman",
        "psn": "137515",
        "csc_file": "S.708",
        "sex": "M",
        "present_rank": "Senior Nursing Supt.",
        "present_gl": "9",
        "proposed_rank": "Principal Nursing Supt. II",
        "proposed_gl": "10",
        "mda": "HMB",
        "group_category": "GROUP C",
        "exam_code": "HMB/C3",
        "exam_date": "Wednesday, 30th September 2026",
        "batch_session": "Session 1",
        "batch_time": "10:00 AM - 11:00 AM",
        "accreditation_time": "09:30 AM",
        "code_1": "C-21835",
        "phone": "080664938",
        "email": "137515@cbt.kw.gov.ng",
        "lga": "Edu"
    },
    {
        "sn": 7,
        "name": "Giwa Aminat",
        "psn": "135667",
        "csc_file": "135667",
        "sex": "F",
        "present_rank": "CHEW",
        "present_gl": "7",
        "proposed_rank": "Higher (CHEW)",
        "proposed_gl": "8",
        "mda": "PHCDA",
        "group_category": "GROUP D",
        "exam_code": "PHCDA/D1",
        "exam_date": "Wednesday, 30th September 2026",
        "batch_session": "Session 3",
        "batch_time": "12:00 PM - 01:00 PM",
        "accreditation_time": "11:30 AM",
        "code_1": "D-73857",
        "phone": "07066721337",
        "email": "135667@cbt.kw.gov.ng",
        "lga": "Ilorin East"
    },
    {
        "sn": 8,
        "name": "Zubair Dupe Olayinka",
        "psn": "135073",
        "csc_file": "135073",
        "sex": "F",
        "present_rank": "Higher (CHEW)",
        "present_gl": "8",
        "proposed_rank": "Senior (CHEW)",
        "proposed_gl": "9",
        "mda": "PHCDA",
        "group_category": "GROUP C",
        "exam_code": "PHCDA/C1",
        "exam_date": "Wednesday, 30th September 2026",
        "batch_session": "Session 3",
        "batch_time": "12:00 PM - 01:00 PM",
        "accreditation_time": "11:30 AM",
        "code_1": "C-48205",
        "phone": "08039401871",
        "email": "135073@cbt.kw.gov.ng",
        "lga": "Ifelodun"
    }
]

print("=== 1. Ingesting into SQLite cbt.db ===")
db_path = os.path.abspath("kwara_cbt_app/cbt.db")
conn = sqlite3.connect(db_path)
cur = conn.cursor()

for c in omitted_8:
    cur.execute("SELECT id, name, code_1 FROM candidate_roster WHERE psn = ? AND name = ?", (c["psn"], c["name"]))
    existing = cur.fetchone()
    if existing:
        print(f"Updating existing record ID {existing[0]}: {c['name']} (PSN: {c['psn']})")
        cur.execute("""
            UPDATE candidate_roster SET
                code_1 = ?, mda = ?, exam_code = ?, proposed_rank = ?, proposed_gl = ?,
                group_category = ?, exam_date = ?, batch_session = ?, batch_time = ?,
                accreditation_time = ?, phone = ?, email = ?
            WHERE id = ?
        """, (
            c["code_1"], c["mda"], c["exam_code"], c["proposed_rank"], c["proposed_gl"],
            c["group_category"], c["exam_date"], c["batch_session"], c["batch_time"],
            c["accreditation_time"], c["phone"], c["email"], existing[0]
        ))
    else:
        print(f"Inserting new candidate: {c['name']} (PSN: {c['psn']}, Code 1: {c['code_1']})")
        cur.execute("""
            INSERT INTO candidate_roster (
                psn, name, code_1, mda, exam_code, proposed_rank, proposed_gl,
                group_category, exam_date, batch_session, batch_time,
                accreditation_time, test_duration_minutes, phone, email,
                registration_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 60, ?, ?, 'pending')
        """, (
            c["psn"], c["name"], c["code_1"], c["mda"], c["exam_code"],
            c["proposed_rank"], c["proposed_gl"], c["group_category"],
            c["exam_date"], c["batch_session"], c["batch_time"],
            c["accreditation_time"], c["phone"], c["email"]
        ))

conn.commit()
cur.execute("SELECT count(*) FROM candidate_roster")
print(f"SQLite candidate_roster count now: {cur.fetchone()[0]}")
conn.close()

print("\n=== 2. Updating Master Excel Workbook ===")
master_path = "Kwara_CSC_2026_CBT_Candidate_Registration_Slips_Master.xlsx"
wb = openpyxl.load_workbook(master_path)
ws = wb.active

# Find last row
last_row = ws.max_row
existing_names = set()
for r in ws.iter_rows(values_only=True):
    if r and len(r) > 2 and r[2]:
        existing_names.add(str(r[2]).strip().lower())

added_count = 0
for c in omitted_8:
    if c["name"].strip().lower() not in existing_names:
        last_row += 1
        ws.append([
            last_row - 1, # SN
            c["psn"],
            c["name"],
            c["code_1"],
            c["proposed_rank"],
            c["proposed_gl"],
            c["mda"],
            c["group_category"],
            c["exam_code"],
            c["exam_date"],
            c["batch_session"],
            c["batch_time"],
            c["accreditation_time"],
            "1. Enter PSN + Code 1 -> 2. Upload Passport -> 3. Print Photocard"
        ])
        existing_names.add(c["name"].strip().lower())
        added_count += 1
        print(f"Appended to Master Excel: {c['name']} (PSN: {c['psn']}, Code 1: {c['code_1']})")
    else:
        print(f"Already in Master Excel: {c['name']} (PSN: {c['psn']})")

wb.save(master_path)
print(f"Saved {master_path} with {added_count} newly appended candidates!")

# Sync copy to kwara_cbt_app/static/
static_copy = os.path.join("kwara_cbt_app", "static", "Kwara_CSC_2026_CBT_Candidate_Registration_Slips_Master.xlsx")
wb.save(static_copy)
print(f"Synced copy to {static_copy}")

print("\nIngestion complete!")
