import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)
import os
import random
import pandas as pd
import psycopg2
import psycopg2.extras

NEON_URL = "postgresql://neondb_owner:npg_Rl0zv1crIkTY@ep-purple-heart-axjsakzf-pooler.c-4.us-east-2.aws.neon.tech/neondb?sslmode=require"

excel_path = r"C:\Users\hp\Downloads\FINAL SAM  EDITED CSC CBT 2026 EXAM  SUBJECT CODING.xlsx"

print("=" * 65)
print("PHASE 1: LOADING MASTER CANDIDATE WORKBOOK")
print("=" * 65)

excel_dict = pd.read_excel(excel_path, sheet_name=None)
print(f"Loaded {len(excel_dict)} sheets from FINAL SAM.")

all_records = []

for sheet_name, df in excel_dict.items():
    if sheet_name in ["Sheet31", "Sheet32"] or df.empty or len(df.columns) < 3:
        continue
    
    cols = df.columns.tolist()
    name_col, psn_col, exam_code_col, rank_col, gl_col, mda_col = None, None, None, None, None, None

    for c in cols:
        c_str = str(c).strip().upper()
        if "NAME" in c_str and not name_col:
            name_col = c
        elif "PSN" in c_str and not psn_col:
            psn_col = c
        elif ("EXAM CODE" in c_str or "SUBJECT" in c_str or "CODE" in c_str or c_str == "UNNAMED: 3") and not exam_code_col:
            exam_code_col = c
        elif ("PROP" in c_str or "RANK" in c_str) and not rank_col:
            rank_col = c
        elif ("GL" in c_str or "GRADE" in c_str) and not gl_col:
            gl_col = c
        elif ("MDA" in c_str or "MINISTRY" in c_str) and not mda_col:
            mda_col = c

    if not exam_code_col and len(cols) >= 4:
        for c in cols:
            sample_val = str(df[c].dropna().iloc[0]) if not df[c].dropna().empty else ""
            if "/" in sample_val or "GL" in sample_val or "-" in sample_val:
                exam_code_col = c
                break

    for _, row in df.iterrows():
        name = str(row[name_col]).strip() if name_col and pd.notna(row[name_col]) else ""
        psn = str(row[psn_col]).strip() if psn_col and pd.notna(row[psn_col]) else ""
        
        if not name or name.lower() in ["nan", "name", "names", "total", "sn", "s/n", "cadre"]:
            continue
        if not psn or psn.lower() in ["nan", "psn", "none", "nil"]:
            continue

        if psn.endswith(".0"):
            psn = psn[:-2]

        exam_code = str(row[exam_code_col]).strip() if exam_code_col and pd.notna(row[exam_code_col]) else ""
        if exam_code.lower() == "nan":
            exam_code = ""

        rank = str(row[rank_col]).strip() if rank_col and pd.notna(row[rank_col]) else ""
        gl = str(row[gl_col]).strip() if gl_col and pd.notna(row[gl_col]) else ""
        if gl.endswith(".0"):
            gl = gl[:-2]

        mda_val = str(row[mda_col]).strip() if mda_col and pd.notna(row[mda_col]) else sheet_name
        if not mda_val or mda_val.lower() == "nan":
            mda_val = sheet_name

        all_records.append({
            "name": name,
            "psn": psn,
            "exam_code": exam_code,
            "rank": rank,
            "gl": gl,
            "mda": mda_val,
            "sheet": sheet_name
        })

df_all = pd.DataFrame(all_records)
# Drop duplicates by PSN, keep first
df_unique = df_all.drop_duplicates(subset=["psn"]).copy()
print(f"Total Unique Officers to Ingest: {len(df_unique)}")

# Determine Group Category
def assign_group(row):
    gl = str(row['gl']).strip()
    code = str(row['exam_code']).upper()
    
    if "17" in gl or "DIRECTOR" in code:
        return "GL 17"
    if gl in ["14", "15", "16"] or "/A" in code or "-A" in code:
        return "GROUP A"
    if gl in ["12", "13"] or "/B" in code or "-B" in code:
        return "GROUP B"
    if gl in ["9", "10", "09"] or "/C" in code or "-C" in code:
        return "GROUP C"
    if gl in ["7", "8", "07", "08"] or "/D" in code or "-D" in code:
        return "GROUP D"
    # Fallback to Group B if undetermined
    return "GROUP B"

df_unique['group_category'] = df_unique.apply(assign_group, axis=1)

print("\nBreakdown by Group Category:")
print(df_unique['group_category'].value_counts().to_string())

# Separate Day 1 and Day 2 candidates
# Day 1: Group A + Group B
# Day 2: Group C + Group D + GL 17
day1_df = df_unique[df_unique['group_category'].isin(["GROUP A", "GROUP B"])].copy()
day2_df = df_unique[df_unique['group_category'].isin(["GROUP C", "GROUP D", "GL 17"])].copy()

# Sort Day 1: Group A first, then Group B, then MDA, then Name
day1_df['grp_order'] = day1_df['group_category'].map({"GROUP A": 1, "GROUP B": 2})
day1_df = day1_df.sort_values(by=['grp_order', 'mda', 'name']).reset_index(drop=True)

# Sort Day 2: Group C first, then Group D, then GL 17, then MDA, then Name
day2_df['grp_order'] = day2_df['group_category'].map({"GROUP C": 1, "GROUP D": 2, "GL 17": 3})
day2_df = day2_df.sort_values(by=['grp_order', 'mda', 'name']).reset_index(drop=True)

print(f"\nTotal Day 1 Candidates: {len(day1_df)}")
print(f"Total Day 2 Candidates: {len(day2_df)}")

# Allocate Day 1 into 5 batches (~313 candidates each)
d1_len = len(day1_df)
d1_batch_sizes = [d1_len // 5] * 5
for i in range(d1_len % 5):
    d1_batch_sizes[i] += 1

d1_timings = [
    ("Session 1", "10:00 AM - 11:00 AM", "09:30 AM"),
    ("Session 2", "11:00 AM - 12:00 PM", "10:30 AM"),
    ("Session 3", "12:00 PM - 01:00 PM", "11:30 AM"),
    ("Session 4", "01:00 PM - 02:00 PM", "12:30 PM"),
    ("Session 5", "02:00 PM - 03:00 PM", "01:30 PM"),
]

idx = 0
for b_num, (b_name, b_time, b_accred) in enumerate(d1_timings):
    size = d1_batch_sizes[b_num]
    day1_df.loc[idx:idx+size-1, 'exam_date'] = "Tuesday, 29th September 2026"
    day1_df.loc[idx:idx+size-1, 'batch_session'] = b_name
    day1_df.loc[idx:idx+size-1, 'batch_time'] = b_time
    day1_df.loc[idx:idx+size-1, 'accreditation_time'] = b_accred
    idx += size

# Allocate Day 2 into 3 batches (~325 candidates each)
d2_len = len(day2_df)
d2_batch_sizes = [d2_len // 3] * 3
for i in range(d2_len % 3):
    d2_batch_sizes[i] += 1

d2_timings = [
    ("Session 1", "10:00 AM - 11:00 AM", "09:30 AM"),
    ("Session 2", "11:00 AM - 12:00 PM", "10:30 AM"),
    ("Session 3", "12:00 PM - 01:00 PM", "11:30 AM"),
]

idx = 0
for b_num, (b_name, b_time, b_accred) in enumerate(d2_timings):
    size = d2_batch_sizes[b_num]
    day2_df.loc[idx:idx+size-1, 'exam_date'] = "Wednesday, 30th September 2026"
    day2_df.loc[idx:idx+size-1, 'batch_session'] = b_name
    day2_df.loc[idx:idx+size-1, 'batch_time'] = b_time
    day2_df.loc[idx:idx+size-1, 'accreditation_time'] = b_accred
    idx += size

combined_roster = pd.concat([day1_df, day2_df], ignore_index=True)

# Generate Code 1: [GROUP_LETTER]-[5 DIGITS]
used_code1 = set()
code1_list = []

for _, r in combined_roster.iterrows():
    grp = r['group_category']
    letter = grp.replace("GROUP ", "").strip()
    if letter not in ["A", "B", "C", "D"]:
        letter = "D" if "17" in grp else "A"
    
    while True:
        num = random.randint(10000, 99999)
        code = f"{letter}-{num}"
        if code not in used_code1:
            used_code1.add(code)
            code1_list.append(code)
            break

combined_roster['code_1'] = code1_list

print("\n--- SAMPLE 10 SCHEDULED CANDIDATES ---")
sample_cols = ['name', 'psn', 'code_1', 'exam_code', 'group_category', 'exam_date', 'batch_session', 'batch_time']
print(combined_roster[sample_cols].head(10).to_string())

print("\n=" * 65)
print("PHASE 2: SEEDING CANDIDATE ROSTER & TOKENS INTO NEON POSTGRESQL")
print("=" * 65)

conn = psycopg2.connect(NEON_URL)
conn.autocommit = True
cur = conn.cursor()

# 1. Create candidate_roster table
cur.execute("""
CREATE TABLE IF NOT EXISTS candidate_roster (
    id SERIAL PRIMARY KEY,
    psn VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    amended_name VARCHAR(255),
    code_1 VARCHAR(20) UNIQUE NOT NULL,
    mda VARCHAR(255) NOT NULL,
    exam_code VARCHAR(100) NOT NULL,
    proposed_rank VARCHAR(255),
    proposed_gl VARCHAR(10),
    group_category VARCHAR(20) NOT NULL,
    exam_date VARCHAR(50) NOT NULL,
    batch_session VARCHAR(50) NOT NULL,
    batch_time VARCHAR(100) NOT NULL,
    accreditation_time VARCHAR(100) NOT NULL,
    test_duration_minutes INT DEFAULT 20,
    phone VARCHAR(50),
    email VARCHAR(255),
    passport_photo TEXT,
    registration_status VARCHAR(50) DEFAULT 'unverified',
    registered_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_roster_psn ON candidate_roster(psn);
CREATE INDEX IF NOT EXISTS idx_roster_code1 ON candidate_roster(code_1);
""")
print("candidate_roster table created/verified.")

# 2. Insert or update candidate_roster
insert_sql = """
INSERT INTO candidate_roster (
    psn, name, code_1, mda, exam_code, proposed_rank, proposed_gl,
    group_category, exam_date, batch_session, batch_time, accreditation_time
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (psn) DO UPDATE SET
    name = EXCLUDED.name,
    code_1 = EXCLUDED.code_1,
    mda = EXCLUDED.mda,
    exam_code = EXCLUDED.exam_code,
    proposed_rank = EXCLUDED.proposed_rank,
    proposed_gl = EXCLUDED.proposed_gl,
    group_category = EXCLUDED.group_category,
    exam_date = EXCLUDED.exam_date,
    batch_session = EXCLUDED.batch_session,
    batch_time = EXCLUDED.batch_time,
    accreditation_time = EXCLUDED.accreditation_time;
"""

roster_rows = []
for _, r in combined_roster.iterrows():
    roster_rows.append((
        str(r['psn']).strip(),
        str(r['name']).strip(),
        str(r['code_1']).strip(),
        str(r['mda']).strip(),
        str(r['exam_code']).strip(),
        str(r['rank']).strip(),
        str(r['gl']).strip(),
        str(r['group_category']).strip(),
        str(r['exam_date']).strip(),
        str(r['batch_session']).strip(),
        str(r['batch_time']).strip(),
        str(r['accreditation_time']).strip()
    ))

psycopg2.extras.execute_batch(cur, insert_sql, roster_rows, page_size=500)
print(f"Successfully seeded {len(roster_rows)} candidate records into candidate_roster!")

# 3. Create exam_tokens table
cur.execute("""
CREATE TABLE IF NOT EXISTS exam_tokens (
    id SERIAL PRIMARY KEY,
    token_code VARCHAR(10) UNIQUE NOT NULL,
    status VARCHAR(20) DEFAULT 'unassigned',
    assigned_to_psn VARCHAR(50),
    activated_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_token_code ON exam_tokens(token_code);
CREATE INDEX IF NOT EXISTS idx_token_psn ON exam_tokens(assigned_to_psn);
""")
print("exam_tokens table created/verified.")

# 4. Generate 3,500 pure 5-digit tokens
cur.execute("SELECT COUNT(*) FROM exam_tokens;")
existing_tokens = cur.fetchone()[0]

if existing_tokens < 3000:
    print(f"Generating 3,500 pure 5-digit unassigned tokens...")
    all_5digits = set(random.sample(range(10000, 99999), 3500))
    token_rows = [(str(t),) for t in all_5digits]
    token_insert_sql = "INSERT INTO exam_tokens (token_code) VALUES (%s) ON CONFLICT (token_code) DO NOTHING;"
    psycopg2.extras.execute_batch(cur, token_insert_sql, token_rows, page_size=500)
    print("3,500 pure 5-digit scratch tokens generated and seeded successfully!")
else:
    print(f"Pool of {existing_tokens} exam tokens already present in database.")

# Save a copy locally as CSV
combined_roster.to_csv(r"C:\Users\hp\Desktop\DataClassPython\master_scheduled_candidates.csv", index=False)
print(f"Saved master scheduled candidate roster to: C:\\Users\\hp\\Desktop\\DataClassPython\\master_scheduled_candidates.csv")

cur.close()
conn.close()
print("PHASE 1 COMPLETE!")
