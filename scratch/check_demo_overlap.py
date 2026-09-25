import sys, os
sys.path.insert(0, os.path.abspath("."))
from kwara_cbt_app.database import get_db_connection

conn = get_db_connection()
cur = conn.cursor()

# Check for orientation words in real questions
cur.execute("""
    SELECT count(*) FROM cbt_questions 
    WHERE LOWER(question_text) LIKE '%cbt%' 
       OR LOWER(question_text) LIKE '%palette%' 
       OR LOWER(question_text) LIKE '%flag for review%'
       OR LOWER(question_text) LIKE '%photocard%'
""")
row = cur.fetchone()
print("Real questions containing CBT/palette/flag/photocard:", row[0] if isinstance(row, tuple) else row['count'])

# Check for our old 40 demo questions against real questions
old_demo_snippets = [
    "statutory retirement age",
    "disciplinary penalty",
    "period of probation",
    "outside your Ministry",
    "constitutionally vested",
    "A.I.E.",
    "Annual Performance Evaluation Reports",
    "Minute refers to",
    "Local Government Areas",
    "Grade Level 14 is entitled to how many working days",
    "conveys general policy directives",
    "Anonymity",
    "Auditor-General for Kwara State",
    "formal Query",
    "Vote Book",
    "serious misconduct",
    "seat of Government of Kwara State",
    "transferring an officer",
    "official letter",
    "Cash Advance",
    "Accounting Officer of a Government Ministry",
    "standard file docket",
    "Code of Conduct Bureau",
    "Interdiction",
    "Maternity leave",
    "Statutory Board",
    "SECRET on an official document",
    "maturity period",
    "Store Issue Voucher",
    "Solicitor",
    "Merit",
    "KWSUTH",
    "AWOL",
    "Internal Audit unit"
]

matches = []
for snip in old_demo_snippets:
    cur.execute("SELECT id, paper_code, question_text FROM cbt_questions WHERE LOWER(question_text) LIKE %s", (f"%{snip.lower()}%",))
    found = cur.fetchall()
    if found:
        matches.append((snip, len(found), [r['paper_code'] for r in found[:3]]))

print(f"\nOf our 34 old snippets, {len(matches)} matched real promotion exam questions:")
for snip, count, papers in matches:
    print(f"  - '{snip}': matched {count} real questions in papers: {papers}")

conn.close()
