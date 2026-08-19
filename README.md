# PETcbt - Kwara State Staff Development College CBT Evaluation System

An interactive Computer-Based Testing (CBT) web application built for the **Kwara State Staff Development College** Productivity Enhancement Evaluation.

## 📌 Features

- **Simplified Candidate Onboarding**: Officers enter their Full Name, PSN (Public Service Number), Email, Cadre / Grade Level, and MDA to begin the test immediately.
- **Automated Question Bank**: 150 questions extracted across Grade Levels (`GL 06-07`, `GL 08`, `GL 09`).
- **Interactive CBT Engine**:
  - Live 45-minute countdown timer with auto-submit.
  - 1–50 question palette with real-time status indicators (🟢 Answered, ⚪ Unanswered, 🟣 Flagged, 🔵 Current).
  - Navigation controls & keyboard shortcuts (`A`, `B`, `C`, `D`, `N`, `P`, `F`).
- **Instant Official Result Slip**:
  - Automated grading upon submission.
  - Shows score percentage, marks obtained (out of 100), performance remark, time spent, and official reference code.
  - Print-ready A4 stylesheet (`@media print`) for 1-click printing or PDF export.
- **Admin Dashboard & Spreadsheet Export**:
  - Protected with username and password authentication (`admin` / `admin123`).
  - Real-time candidate monitoring and KPI summaries.
  - **1-Click Excel (`.xlsx`) Export** with official headers and formatting.
  - **1-Click CSV Export**.

## 🚀 Getting Started

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Launch the Application
- **On Windows**: Double-click `run_cbt.bat`
- **Or via Python**:
  ```bash
  python run_kwara_cbt.py
  ```

The server will automatically start at `http://127.0.0.1:8000` and open in your default web browser.

## 🔐 Administrator Login
- **Username**: `admin`
- **Password**: `admin123`
