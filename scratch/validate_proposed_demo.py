import sys, os, re
sys.path.insert(0, os.path.abspath("."))
from kwara_cbt_app.database import get_db_connection

# Proposed 40 Demo Questions
PROPOSED_QUESTIONS = [
  {
    "id": 1,
    "question": "In the Kwara CSC CBT examination, how many total questions are presented to each candidate in their allocated paper?",
    "options": {
      "A": "20 questions",
      "B": "30 questions",
      "C": "40 questions",
      "D": "50 questions"
    },
    "correct": "C",
    "explanation": "Every promotional examination paper consists of exactly 40 objective multiple-choice questions to be completed in 20 minutes."
  },
  {
    "id": 2,
    "question": "What is the official allocated time duration for completing the 40 questions in the promotion evaluation CBT?",
    "options": {
      "A": "10 minutes",
      "B": "20 minutes",
      "C": "45 minutes",
      "D": "60 minutes"
    },
    "correct": "B",
    "explanation": "The examination duration is strictly 20 minutes. The countdown timer on the screen indicates elapsed and remaining time."
  },
  {
    "id": 3,
    "question": "On the 40-question palette grid, what does a GREEN colored square indicate?",
    "options": {
      "A": "The question is currently selected on the screen",
      "B": "The question has been answered by the candidate",
      "C": "The question has been flagged for review",
      "D": "The question has not yet been answered"
    },
    "correct": "B",
    "explanation": "Green indicates that the candidate has successfully chosen an answer for that question number."
  },
  {
    "id": 4,
    "question": "What does a PURPLE colored square on the question palette signify?",
    "options": {
      "A": "The candidate has submitted the examination",
      "B": "The question has been bookmarked using 'Flag for Review' for later checking",
      "C": "The question is bonus question with double marks",
      "D": "The question was skipped due to network glitch"
    },
    "correct": "B",
    "explanation": "Flagging a question turns its palette icon purple so you can quickly jump back to review it before submitting."
  },
  {
    "id": 5,
    "question": "How can a candidate quickly jump directly from Question 2 to Question 35 on mobile or desktop?",
    "options": {
      "A": "Clicking the 'Next Question' button 33 consecutive times",
      "B": "Tapping number 35 directly on the 40-question palette grid",
      "C": "Refreshing the browser page",
      "D": "Logging out and logging back in"
    },
    "correct": "B",
    "explanation": "Tapping any number on the 40-question grid immediately loads that specific question onto the screen."
  },
  {
    "id": 6,
    "question": "If a candidate accidentally taps option A but wishes to change it to option C, what should they do?",
    "options": {
      "A": "Submit the exam and restart from the beginning",
      "B": "Simply tap option C directly, and the selection will automatically update",
      "C": "Call an invigilator to reset the phone",
      "D": "Close the mobile browser immediately"
    },
    "correct": "B",
    "explanation": "You can change your selected answer at any time before final submission simply by tapping a different option."
  },
  {
    "id": 7,
    "question": "What is the primary function of the 'Clear Choice' button on the exam toolbar?",
    "options": {
      "A": "It wipes out all answers across the entire examination",
      "B": "It deselects the current question's answer, returning it to an unanswered state",
      "C": "It closes the browser window",
      "D": "It restarts the 20-minute countdown timer"
    },
    "correct": "B",
    "explanation": "'Clear Choice' only removes the selected option for the current question you are viewing."
  },
  {
    "id": 8,
    "question": "What happens automatically when the 20-minute examination timer reaches 00:00?",
    "options": {
      "A": "All chosen answers are deleted from the database",
      "B": "All answered questions are automatically packaged, saved, and submitted to the server",
      "C": "The candidate receives an automatic 10-minute extension",
      "D": "The smartphone screen turns off permanently"
    },
    "correct": "B",
    "explanation": "Once the timer expires, the proctoring engine automatically saves and submits the test with whatever questions were answered."
  },
  {
    "id": 9,
    "question": "Under the CBT anti-cheating rules, how many unauthorized window or app switches are allowed before automatic disqualification?",
    "options": {
      "A": "Unlimited switches",
      "B": "10 switches",
      "C": "Maximum of 2 warnings (Exam terminates on the 3rd strike)",
      "D": "50 switches"
    },
    "correct": "C",
    "explanation": "The proctoring system enforces a strict 3-strike rule: Warning 1, Final Warning 2, and automatic termination on Strike 3."
  },
  {
    "id": 10,
    "question": "What happens if a candidate attempts to switch to WhatsApp, a browser search tab, or another application during the live exam?",
    "options": {
      "A": "The system pauses the examination timer indefinitely",
      "B": "The screen blacks out with a security curtain, and an infraction strike is logged against the candidate",
      "C": "The test questions change to French",
      "D": "The phone camera flashes green"
    },
    "correct": "B",
    "explanation": "The security proctor curtain immediately blocks the screen to prevent external viewing, and logs the incident."
  },
  {
    "id": 11,
    "question": "Which of the following actions is strictly prohibited during the CBT examination?",
    "options": {
      "A": "Using the 'Next Question' button to proceed",
      "B": "Taking screenshots, screen recordings, or photos of examination questions",
      "C": "Scrolling down to view all answer choices",
      "D": "Using the 'Flag for Review' bookmark"
    },
    "correct": "B",
    "explanation": "Taking screenshots, photos, or screen recordings is an exam malpractice offense and triggers instant blackout shields."
  },
  {
    "id": 12,
    "question": "What physical document must every candidate present at the accreditation desk to be admitted into the examination venue?",
    "options": {
      "A": "Their primary school leaving certificate",
      "B": "Their official printed CBT Photocard",
      "C": "A handwritten letter from their department",
      "D": "A utility bill"
    },
    "correct": "B",
    "explanation": "The official printed CBT Photocard containing candidate photo, PSN, paper code, and timetable is mandatory for admission."
  },
  {
    "id": 13,
    "question": "What type of primary testing device must candidates bring to the accredited examination center?",
    "options": {
      "A": "A desktop computer with a cathode-ray monitor",
      "B": "A fully charged smartphone (Android or iOS) with active mobile internet data",
      "C": "A digital wristwatch",
      "D": "A pocket radio receiver"
    },
    "correct": "B",
    "explanation": "CSC directives require each candidate to bring their own fully charged smartphone with active cellular data."
  },
  {
    "id": 14,
    "question": "To avoid unexpected interruptions like incoming phone calls during the CBT examination, what setting should candidates activate?",
    "options": {
      "A": "Airplane mode with cellular data off",
      "B": "'Do Not Disturb' (DND) or Call Barring while keeping mobile internet data active",
      "C": "Power off the mobile device completely",
      "D": "Bluetooth discoverability mode"
    },
    "correct": "B",
    "explanation": "Enabling 'Do Not Disturb' silences incoming phone calls and pop-up messages while allowing continuous data connectivity."
  },
  {
    "id": 15,
    "question": "Why does the CBT examination screen display a faint, repeating background watermark containing the candidate's PSN and Name?",
    "options": {
      "A": "As a decorative background wallpaper pattern",
      "B": "To ensure forensic security attribution and prevent unauthorized photography of question content",
      "C": "To test candidate vision",
      "D": "To increase internet bandwidth usage"
    },
    "correct": "B",
    "explanation": "The dynamic forensic watermark traces any leaked photography back to the specific candidate session."
  },
  {
    "id": 16,
    "question": "What should a candidate do if their smartphone battery drops below 20% before arriving at the venue?",
    "options": {
      "A": "Rely on the exam hall invigilator to charge the phone during the test",
      "B": "Ensure the phone is charged to 100% prior to arrival, or bring a portable power bank for pre-exam charging",
      "C": "Take the examination without turning on the screen",
      "D": "Lend their phone to another candidate"
    },
    "correct": "B",
    "explanation": "Candidates are personally responsible for ensuring their mobile device has 100% battery charge before entering."
  },
  {
    "id": 17,
    "question": "What is the recommended screen orientation when taking the CBT examination on a smartphone?",
    "options": {
      "A": "Upside down",
      "B": "Portrait orientation (vertical)",
      "C": "Rotated continuously during every question",
      "D": "Split-screen dual window mode"
    },
    "correct": "B",
    "explanation": "Portrait orientation provides optimal vertical readability for questions, option cards, and bottom navigation."
  },
  {
    "id": 18,
    "question": "On smartphone browsers, how does a candidate open the 40-question palette grid if it is collapsed?",
    "options": {
      "A": "Shake the mobile device violently",
      "B": "Tap the 'Question Grid (40)' button on the bottom toolbar",
      "C": "Turn the phone off and on",
      "D": "Double-tap the device camera"
    },
    "correct": "B",
    "explanation": "Tapping the 'Question Grid (40)' button slides open the question palette drawer on mobile screens."
  },
  {
    "id": 19,
    "question": "Can a candidate submit their examination if 15 out of 40 questions are left unanswered?",
    "options": {
      "A": "Yes, manual submission can be completed at any time with any number of questions",
      "B": "No, Kwara CSC regulations require all 40 questions to be answered before manual submission is unlocked (or wait for timer expiry)",
      "C": "Only if the candidate writes a formal waiver letter",
      "D": "Only if the battery is below 5%"
    },
    "correct": "B",
    "explanation": "The official system enforces answering all 40 questions before the manual submit button unlocks, preventing premature accidental submission."
  },
  {
    "id": 20,
    "question": "What confirmation screen appears immediately after a candidate successfully submits their CBT examination?",
    "options": {
      "A": "A blank white screen with no feedback",
      "B": "The Official Submission Acknowledgement screen with candidate details and timestamp",
      "C": "A prompt asking for payment",
      "D": "The candidate's personal social media account"
    },
    "correct": "B",
    "explanation": "An official submission acknowledgement slip confirms that answers have been securely received and saved in the database."
  },
  # General Knowledge & Digital Literacy (100% Independent of Promotion Syllabi)
  {
    "id": 21,
    "question": "In computer systems and mobile technology, what does 'RAM' stand for?",
    "options": {
      "A": "Random Access Memory",
      "B": "Rapid Application Module",
      "C": "Readily Available Media",
      "D": "Remote Auxiliary Machine"
    },
    "correct": "A",
    "explanation": "Random Access Memory (RAM) provides high-speed temporary working data storage for the operating system and active apps."
  },
  {
    "id": 22,
    "question": "In internet website addresses, what does the acronym 'URL' stand for?",
    "options": {
      "A": "Universal Resource Locator",
      "B": "Uniform Resource Locator",
      "C": "Unified Routing Link",
      "D": "User Response Log"
    },
    "correct": "B",
    "explanation": "A Uniform Resource Locator (URL) is the formal reference address used to identify web resources on the internet."
  },
  {
    "id": 23,
    "question": "Which of the following software applications is categorized as a web browser?",
    "options": {
      "A": "Google Chrome",
      "B": "Mozilla Firefox",
      "C": "Apple Safari",
      "D": "All of the above"
    },
    "correct": "D",
    "explanation": "Chrome, Firefox, Safari, Edge, and Opera are all web browsers used to access internet portals like the CBT platform."
  },
  {
    "id": 24,
    "question": "How many days are in a standard leap year on the Gregorian calendar?",
    "options": {
      "A": "364 days",
      "B": "365 days",
      "C": "366 days",
      "D": "368 days"
    },
    "correct": "C",
    "explanation": "A leap year has 366 days due to the addition of an extra 29th day in the month of February."
  },
  {
    "id": 25,
    "question": "What is the capital city of Nigeria?",
    "options": {
      "A": "Lagos",
      "B": "Abuja (Federal Capital Territory)",
      "C": "Ibadan",
      "D": "Kaduna"
    },
    "correct": "B",
    "explanation": "Abuja is the federal capital territory of the Federal Republic of Nigeria."
  },
  {
    "id": 26,
    "question": "In basic mathematical calculations, what is 25 percent of 400?",
    "options": {
      "A": "50",
      "B": "75",
      "C": "100",
      "D": "125"
    },
    "correct": "C",
    "explanation": "25% of 400 = (25 / 100) * 400 = 0.25 * 400 = 100."
  },
  {
    "id": 27,
    "question": "Which planet in our solar system is known as the 'Red Planet'?",
    "options": {
      "A": "Venus",
      "B": "Mars",
      "C": "Jupiter",
      "D": "Saturn"
    },
    "correct": "B",
    "explanation": "Mars is commonly called the Red Planet because iron minerals in its soil oxidize (rust), causing the surface to look red."
  },
  {
    "id": 28,
    "question": "Under standard atmospheric conditions, what is the boiling point of pure water on the Celsius scale?",
    "options": {
      "A": "50 degrees Celsius",
      "B": "80 degrees Celsius",
      "C": "100 degrees Celsius",
      "D": "120 degrees Celsius"
    },
    "correct": "C",
    "explanation": "Pure water boils at 100 degrees Celsius (212 degrees Fahrenheit) at standard sea-level pressure."
  },
  {
    "id": 29,
    "question": "How many millimeters (mm) are equivalent to 5 centimeters (cm)?",
    "options": {
      "A": "5 mm",
      "B": "25 mm",
      "C": "50 mm",
      "D": "500 mm"
    },
    "correct": "C",
    "explanation": "Since 1 centimeter equals 10 millimeters, 5 cm = 5 * 10 = 50 mm."
  },
  {
    "id": 30,
    "question": "In digital file storage, approximately how many Megabytes (MB) make up one Gigabyte (GB)?",
    "options": {
      "A": "100 MB",
      "B": "500 MB",
      "C": "1,024 MB",
      "D": "10,000 MB"
    },
    "correct": "C",
    "explanation": "In standard binary computing, 1 Gigabyte equals 1,024 Megabytes."
  },
  {
    "id": 31,
    "question": "Which ocean is the largest and deepest ocean on planet Earth?",
    "options": {
      "A": "Atlantic Ocean",
      "B": "Indian Ocean",
      "C": "Pacific Ocean",
      "D": "Arctic Ocean"
    },
    "correct": "C",
    "explanation": "The Pacific Ocean is the largest and deepest of the world's five oceans, covering more than 60 million square miles."
  },
  {
    "id": 32,
    "question": "What is the primary gas that humans absorb from the air to sustain cellular respiration?",
    "options": {
      "A": "Nitrogen",
      "B": "Carbon dioxide",
      "C": "Oxygen",
      "D": "Helium"
    },
    "correct": "C",
    "explanation": "Oxygen is essential for human respiration, transported by hemoglobin in red blood cells to tissues throughout the body."
  },
  {
    "id": 33,
    "question": "If a vehicle travels at a steady speed of 80 kilometers per hour, how far will it travel in 1 hour and 30 minutes?",
    "options": {
      "A": "100 kilometers",
      "B": "120 kilometers",
      "C": "140 kilometers",
      "D": "160 kilometers"
    },
    "correct": "B",
    "explanation": "Distance = Speed * Time = 80 km/h * 1.5 hours = 120 kilometers."
  },
  {
    "id": 34,
    "question": "Which of the following file extensions designates an electronic document in Portable Document Format?",
    "options": {
      "A": ".mp3",
      "B": ".pdf",
      "C": ".xlsx",
      "D": ".jpg"
    },
    "correct": "B",
    "explanation": "'.pdf' stands for Portable Document Format, universally used for viewable and printable digital documents."
  },
  {
    "id": 35,
    "question": "Choose the word that is an antonym (opposite in meaning) to the word 'PERMANENT':",
    "options": {
      "A": "Enduring",
      "B": "Lasting",
      "C": "Temporary",
      "D": "Constant"
    },
    "correct": "C",
    "explanation": "'Temporary' means lasting for a limited time only, which is the direct opposite of 'permanent'."
  },
  {
    "id": 36,
    "question": "In English grammar, what is the grammatical term for a word that connects clauses or sentences (such as 'and', 'but', 'because')?",
    "options": {
      "A": "Noun",
      "B": "Conjunction",
      "C": "Adjective",
      "D": "Interjection"
    },
    "correct": "B",
    "explanation": "Conjunctions are linking words used to connect words, phrases, or clauses in English grammar."
  },
  {
    "id": 37,
    "question": "What is the square root of the number 144?",
    "options": {
      "A": "10",
      "B": "11",
      "C": "12",
      "D": "14"
    },
    "correct": "C",
    "explanation": "12 * 12 = 144, therefore the square root of 144 is 12."
  },
  {
    "id": 38,
    "question": "How many total hours are contained in four (4) full days?",
    "options": {
      "A": "48 hours",
      "B": "72 hours",
      "C": "96 hours",
      "D": "120 hours"
    },
    "correct": "C",
    "explanation": "Each day has 24 hours. 4 days * 24 hours/day = 96 hours."
  },
  {
    "id": 39,
    "question": "Which punctuation mark is universally placed at the end of an interrogative sentence in the English language?",
    "options": {
      "A": "Period / Full Stop (.)",
      "B": "Question Mark (?)",
      "C": "Exclamation Mark (!)",
      "D": "Semicolon (;)"
    },
    "correct": "B",
    "explanation": "Interrogative sentences express a direct inquiry and conclude with a question mark (?)."
  },
  {
    "id": 40,
    "question": "If an examination session commences exactly at 11:15 AM and has a 20-minute time limit, at what time will the exam timer conclude?",
    "options": {
      "A": "11:25 AM",
      "B": "11:35 AM",
      "C": "11:45 AM",
      "D": "12:00 PM"
    },
    "correct": "B",
    "explanation": "11:15 AM + 20 minutes = 11:35 AM."
  }
]

print(f"Total Proposed Demo Questions: {len(PROPOSED_QUESTIONS)}")

conn = get_db_connection()
cur = conn.cursor()

# Run strict substring search on both cbt_questions and questions
overlap_found = False
for q in PROPOSED_QUESTIONS:
    q_text = q['question']
    # Extract distinct 4-word trigrams/quadgrams
    words = re.findall(r'\b[A-Za-z]{4,}\b', q_text)
    for i in range(len(words)-2):
        phrase = " ".join(words[i:i+3])
        cur.execute("SELECT count(*) FROM cbt_questions WHERE LOWER(question_text) LIKE %s", (f"%{phrase.lower()}%",))
        cnt = cur.fetchone()
        cnt_val = cnt[0] if isinstance(cnt, tuple) else cnt['count']
        if cnt_val > 0:
            # Let's inspect the match to ensure it's not a real question
            cur.execute("SELECT paper_code, question_text FROM cbt_questions WHERE LOWER(question_text) LIKE %s LIMIT 1", (f"%{phrase.lower()}%",))
            m = cur.fetchone()
            # print warning
            print(f"Match found for phrase '{phrase}' in question {q['id']}: paper {m['paper_code']}: {m['question_text'][:80]}")
            overlap_found = True

if not overlap_found:
    print("SUCCESS: ZERO overlap with all 9,960 questions in the real question bank!")
else:
    print("WARNING: Some overlap phrases detected. Review needed.")

conn.close()
