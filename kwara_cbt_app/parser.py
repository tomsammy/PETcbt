import docx
import os
import re
import sqlite3
from database import get_db_connection, init_db

DOCS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "PETCBT"))

DOC_FILES = {
    "GL 06-07": os.path.join(DOCS_DIR, "GL 06 & 7 PROF CBT DRAFT QUESTIONS.docx"),
    "GL 08": os.path.join(DOCS_DIR, "CBT  GL 08 2026 Batch B  TEST.docx"),
    "GL 09": os.path.join(DOCS_DIR, "GL 09 PROF CBT DRAFT QUESTIONS.docx")
}

KNOWN_FIXES = {
    "GL 06-07": {
        32: {
            "correct_answer": "A"
        },
        44: {
            "correct_answer": "C"
        }
    },
    "GL 08": {
        24: {
            "correct_answer": "A"
        },
        44: {
            "correct_answer": "C"
        },
        50: {
            "question": "Unauthorized expenditure means:",
            "options": {
                "A": "Spending government money with proper approval",
                "B": "Spending government money without approval or outside budgetary provisions",
                "C": "Proper payment of approved staff vouchers",
                "D": "Lawful disbursement of public funds"
            },
            "correct_answer": "B"
        }
    },
    "GL 09": {
        24: {
            "correct_answer": "A"
        },
        44: {
            "correct_answer": "C"
        },
        50: {
            "question": "Unauthorized expenditure means:",
            "options": {
                "A": "Spending government money with proper approval",
                "B": "Spending government money without approval or outside budgetary provisions",
                "C": "Proper payment of approved staff vouchers",
                "D": "Lawful disbursement of public funds"
            },
            "correct_answer": "B"
        }
    }
}

def clean_text(t: str) -> str:
    if not t:
        return ""
    return (t.replace("\uFFFD", "-")
             .replace("\u2013", "-")
             .replace("\u2014", "-")
             .replace("\u2018", "'")
             .replace("\u2019", "'")
             .replace("\u201C", '"')
             .replace("\u201D", '"')
             .strip())

def parse_options(lines):
    options = {}
    current_opt = None
    
    # Filter out Correct Answer lines
    opt_lines = [l for l in lines if not re.search(r'Correct\s*Answer', l, re.I)]
    
    # Check if lines start with A., B., C., D.
    has_line_starts = any(re.match(r'^[A-D][\.\)]\s+', l) for l in opt_lines)
    
    if has_line_starts:
        for l in opt_lines:
            # If line has multiple options on same line (e.g. A. foo B. bar)
            if len(list(re.finditer(r'(?:^|[a-z0-9\s])(?=[A-D][\.\)]\s+)', l))) > 1:
                sub_parts = re.split(r'(?=[A-D][\.\)]\s+)', l)
                for sp in sub_parts:
                    m = re.match(r'^([A-D])[\.\)]\s*(.*)', sp.strip())
                    if m:
                        current_opt = m.group(1).upper()
                        options[current_opt] = m.group(2).strip()
            else:
                m = re.match(r'^([A-D])[\.\)]\s*(.*)', l.strip())
                if m:
                    current_opt = m.group(1).upper()
                    options[current_opt] = m.group(2).strip()
                elif current_opt:
                    options[current_opt] += " " + l.strip()
    else:
        # Combined lines
        full_text = " ".join(opt_lines)
        parts = re.split(r'(?=[A-D][\.\)]\s+)', full_text)
        for p in parts:
            m = re.match(r'^([A-D])[\.\)]\s*(.*)', p.strip())
            if m:
                options[m.group(1).upper()] = m.group(2).strip()
                
    return options

def parse_docx_questions(filepath: str, grade_level: str):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    
    doc = docx.Document(filepath)
    paras = [clean_text(p.text) for p in doc.paragraphs if clean_text(p.text)]
    full_text = "\n".join(paras)
    
    # Split blocks by numbering pattern e.g., "\n1. ", "\n2. "
    raw_blocks = re.split(r'\n(?=\d+[\.\)]\s+)', "\n" + full_text)
    raw_blocks = [b.strip() for b in raw_blocks if b.strip()]
    
    questions = []
    for idx, block in enumerate(raw_blocks, start=1):
        lines = [l.strip() for l in block.split("\n") if l.strip()]
        if not lines:
            continue
            
        first_line = lines[0]
        match_num = re.match(r'^(\d+)[\.\)]\s*(.*)', first_line)
        q_num = int(match_num.group(1)) if match_num else idx
        q_text = match_num.group(2).strip() if match_num else first_line
        
        # Handle cases where question text has nested numbering like "49. 11. Maternity leave..."
        nested_match = re.match(r'^\d+[\.\)]\s*(.*)', q_text)
        if nested_match:
            q_text = nested_match.group(1).strip()
            
        correct_ans = ""
        for line in lines[1:]:
            ca_match = re.search(r'Correct\s*Answer\s*[:\-]?\s*([A-D])', line, re.IGNORECASE)
            if ca_match:
                correct_ans = ca_match.group(1).upper()
                break
                
        options = parse_options(lines[1:])
            
        # Apply known overrides/fixes if present
        if grade_level in KNOWN_FIXES and q_num in KNOWN_FIXES[grade_level]:
            fix = KNOWN_FIXES[grade_level][q_num]
            if "question" in fix:
                q_text = fix["question"]
            if "options" in fix:
                options = fix["options"]
            if "correct_answer" in fix and not correct_ans:
                correct_ans = fix["correct_answer"]
                
        # Ensure default fallbacks if missing
        if "A" not in options or not options["A"]: options["A"] = "Option A"
        if "B" not in options or not options["B"]: options["B"] = "Option B"
        if "C" not in options or not options["C"]: options["C"] = "Option C"
        if "D" not in options or not options["D"]: options["D"] = "Option D"
        if not correct_ans: correct_ans = "A"
        
        questions.append({
            "grade_level": grade_level,
            "question_number": q_num,
            "question_text": q_text,
            "option_a": options.get("A", ""),
            "option_b": options.get("B", ""),
            "option_c": options.get("C", ""),
            "option_d": options.get("D", ""),
            "correct_answer": correct_ans
        })
        
    return questions

def seed_database():
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Clear existing questions
    cursor.execute("DELETE FROM questions")
    
    total_inserted = 0
    for grade_level, file_path in DOC_FILES.items():
        questions = parse_docx_questions(file_path, grade_level)
        
        for q in questions:
            cursor.execute("""
                INSERT INTO questions (
                    grade_level, question_number, question_text,
                    option_a, option_b, option_c, option_d, correct_answer
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                q["grade_level"], q["question_number"], q["question_text"],
                q["option_a"], q["option_b"], q["option_c"], q["option_d"],
                q["correct_answer"]
            ))
            total_inserted += 1
            
    conn.commit()
    conn.close()
    print(f"Database seeded successfully with {total_inserted} total questions across 3 grade levels!")

if __name__ == "__main__":
    seed_database()
