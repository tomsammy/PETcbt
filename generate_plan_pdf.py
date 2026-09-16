import os
import sys
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        if self._pageNumber > 1:
            self.setFillColor(colors.HexColor("#004D40"))
            self.rect(36, A4[1] - 30, A4[0] - 72, 3, fill=1, stroke=0)
            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(colors.HexColor("#004D40"))
            self.drawString(36, A4[1] - 24, "KWARA STATE CIVIL SERVICE COMMISSION — 2026 CBT PROMOTION EVALUATION")

        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.75)
        self.line(36, 38, A4[0] - 36, 38)
        
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        self.drawString(36, 25, "Official Civil Service Promotion CBT Blueprint — Strictly Confidential")
        self.drawRightString(A4[0] - 36, 25, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()

def build_pdf(filename):
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=38,
        bottomMargin=48
    )

    styles = getSampleStyleSheet()

    primary_color = colors.HexColor("#004D40")
    secondary_color = colors.HexColor("#00796B")
    dark_neutral = colors.HexColor("#0F172A")
    light_bg = colors.HexColor("#F8FAFC")

    title_style = ParagraphStyle('DocTitle', fontName='Helvetica-Bold', fontSize=17, leading=21, textColor=colors.white, alignment=1)
    subtitle_style = ParagraphStyle('DocSubTitle', fontName='Helvetica-Bold', fontSize=10.5, leading=14, textColor=colors.HexColor("#FFD54F"), alignment=1)
    h1_style = ParagraphStyle('H1', fontName='Helvetica-Bold', fontSize=12, leading=16, textColor=primary_color, spaceBefore=10, spaceAfter=4, keepWithNext=True)
    h2_style = ParagraphStyle('H2', fontName='Helvetica-Bold', fontSize=9.5, leading=13, textColor=secondary_color, spaceBefore=6, spaceAfter=3, keepWithNext=True)
    body_style = ParagraphStyle('Body', fontName='Helvetica', fontSize=8.5, leading=12, textColor=dark_neutral, spaceAfter=4)
    table_header_style = ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=colors.white, alignment=1)
    table_cell_style = ParagraphStyle('TD', fontName='Helvetica', fontSize=7.5, leading=10, textColor=dark_neutral)
    table_cell_center = ParagraphStyle('TDC', fontName='Helvetica', fontSize=7.5, leading=10, textColor=dark_neutral, alignment=1)
    table_cell_bold = ParagraphStyle('TDB', fontName='Helvetica-Bold', fontSize=7.5, leading=10, textColor=dark_neutral)

    story = []

    # Header Banner
    header_data = [
        [Paragraph("KWARA STATE CIVIL SERVICE COMMISSION & OFFICE OF THE HEAD OF SERVICE", title_style)],
        [Paragraph("2026 PROMOTION CBT: OPERATIONAL & TECHNICAL IMPLEMENTATION BLUEPRINT", subtitle_style)]
    ]
    header_table = Table(header_data, colWidths=[A4[0] - 72])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), primary_color),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 8))

    # Executive Metadata Box
    meta_data = [
        [Paragraph("<b>Target Exercise:</b> 2026 Civil Service Promotion CBT", table_cell_style),
         Paragraph("<b>Dates:</b> Day 1 (29th Sept) & Day 2 (30th Sept 2026)", table_cell_style)],
        [Paragraph("<b>Total Candidate Cohort:</b> 2,544 Officers across 30 MDAs", table_cell_style),
         Paragraph("<b>Batch Windows:</b> Exactly 1 Hour / Batch (Starts 10:00 AM)", table_cell_style)],
        [Paragraph("<b>Day 1 Structure:</b> 5 Batches (~313 candidates/batch) — Finishes 3:00 PM", table_cell_style),
         Paragraph("<b>Day 2 Structure:</b> 3 Batches (~325 candidates/batch) — Finishes 1:00 PM", table_cell_style)],
        [Paragraph("<b>CBT Test Duration:</b> 20-Minute Countdown Timer", table_cell_style),
         Paragraph("<b>Dual Codes:</b> Code 1 (Reg/Photo) & Code 2 (5-Digit Scratch Token)", table_cell_style)]
    ]
    meta_table = Table(meta_data, colWidths=[(A4[0] - 72)/2, (A4[0] - 72)/2])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F1F5F9")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0, 0), (-1, -1), 4.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 10))

    # 1. Section: The Dual-Code Security Architecture
    story.append(Paragraph("1. Dual-Code Architecture & 1-Hour Batch Turnover Logistics", h1_style))
    story.append(Paragraph(
        "Each 1-hour batch includes <b>15 minutes for hall entry/briefing, exactly 20 minutes for the CBT evaluation</b>, and 25 minutes for orderly exit:",
        body_style
    ))

    code_data = [
        [Paragraph("Code Classification", table_header_style), Paragraph("Format & Pinning", table_header_style), Paragraph("Issuance & Purpose", table_header_style)],
        [Paragraph("<b>CODE 1<br/>Registration Access Code</b>", table_cell_center),
         Paragraph("<code>[GROUP]-[5 DIGITS]</code><br/>e.g. <code>A-49201</code>, <code>B-73812</code><br/><b>Permanently Pinned to PSN</b>", table_cell_style),
         Paragraph("Printed on physical Pre-Screening Slip. Candidate enters PSN + Code 1 to verify bio-data, amend spelling typos, upload verified passport photo, and generate CBT Photocard.", table_cell_style)],
        [Paragraph("<b>CODE 2<br/>Exam Scratch Token</b>", table_cell_center),
         Paragraph("Pure <b>5-Digit Number</b><br/>e.g. <code>84920</code>, <code>19482</code><br/><b>Not Pinned in Advance</b>", table_cell_style),
         Paragraph("Distributed inside the exam hall. Officer sits at PC and inputs PSN + Code 2. The token instantly locks to that PSN, serves their exact departmental question paper, and starts the <b>20-minute countdown</b>.", table_cell_style)]
    ]
    code_table = Table(code_data, colWidths=[110, 140, A4[0] - 72 - 250])
    code_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, light_bg]),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(code_table)
    story.append(Spacer(1, 10))

    # Page Break for Timetable
    story.append(PageBreak())

    # 2. Section: Master Timetable (5 Batches on Day 1)
    story.append(Paragraph("2. Revised Master Timetable (5 Batches on Day 1, ~313 / Batch)", h1_style))
    story.append(Paragraph(
        "Day 1 is consolidated to <b>5 batches (~313 candidates each)</b>, fully concluding by <b>3:00 PM</b>. Day 2 is consolidated to <b>3 batches</b>, concluding by <b>1:00 PM</b>:",
        body_style
    ))

    sched_data = [
        [Paragraph("Day", table_header_style), Paragraph("Batch", table_header_style), Paragraph("Batch Window (1h)", table_header_style), Paragraph("CBT Test Time (20m)", table_header_style), Paragraph("Cap.", table_header_style), Paragraph("Target Group & Cadres", table_header_style)],
        # Day 1
        [Paragraph("<b>DAY 1<br/>(29th Sep)</b>", table_cell_center), Paragraph("Session 1", table_cell_center), Paragraph("10:00 AM – 11:00 AM", table_cell_center), Paragraph("10:15 AM – 10:35 AM", table_cell_center), Paragraph("313", table_cell_center), Paragraph("<b>GROUP A</b> (GL 14, 15, 16 — Directorate Part 1)", table_cell_style)],
        [Paragraph("<b>DAY 1<br/>(29th Sep)</b>", table_cell_center), Paragraph("Session 2", table_cell_center), Paragraph("11:00 AM – 12:00 PM", table_cell_center), Paragraph("11:15 AM – 11:35 AM", table_cell_center), Paragraph("313", table_cell_center), Paragraph("<b>GROUP A</b> (GL 14, 15, 16 — Directorate Part 2)", table_cell_style)],
        [Paragraph("<b>DAY 1<br/>(29th Sep)</b>", table_cell_center), Paragraph("Session 3", table_cell_center), Paragraph("12:00 PM – 01:00 PM", table_cell_center), Paragraph("12:15 PM – 12:35 PM", table_cell_center), Paragraph("313", table_cell_center), Paragraph("<b>GROUP A</b> (67) + <b>GROUP B</b> (246) <i>(All Group A Cleared)</i>", table_cell_style)],
        [Paragraph("<b>DAY 1<br/>(29th Sep)</b>", table_cell_center), Paragraph("Session 4", table_cell_center), Paragraph("01:00 PM – 02:00 PM", table_cell_center), Paragraph("01:15 PM – 01:35 PM", table_cell_center), Paragraph("314", table_cell_center), Paragraph("<b>GROUP B</b> (GL 12, 13 — Senior Officers Part 2)", table_cell_style)],
        [Paragraph("<b>DAY 1<br/>(29th Sep)</b>", table_cell_center), Paragraph("Session 5", table_cell_center), Paragraph("02:00 PM – 03:00 PM", table_cell_center), Paragraph("02:15 PM – 02:35 PM", table_cell_center), Paragraph("314", table_cell_center), Paragraph("<b>GROUP B</b> (GL 12, 13 — Final Cohort) <i>(All Group B Cleared)</i>", table_cell_style)],
        # Day 2
        [Paragraph("<b>DAY 2<br/>(30th Sep)</b>", table_cell_center), Paragraph("Session 1", table_cell_center), Paragraph("10:00 AM – 11:00 AM", table_cell_center), Paragraph("10:15 AM – 10:35 AM", table_cell_center), Paragraph("325", table_cell_center), Paragraph("<b>GROUP C</b> (GL 09 — Senior Officers Part 1)", table_cell_style)],
        [Paragraph("<b>DAY 2<br/>(30th Sep)</b>", table_cell_center), Paragraph("Session 2", table_cell_center), Paragraph("11:00 AM – 12:00 PM", table_cell_center), Paragraph("11:15 AM – 11:35 AM", table_cell_center), Paragraph("325", table_cell_center), Paragraph("<b>GROUP C</b> (GL 09 & GL 10 — Senior Officers Part 2)", table_cell_style)],
        [Paragraph("<b>DAY 2<br/>(30th Sep)</b>", table_cell_center), Paragraph("Session 3", table_cell_center), Paragraph("12:00 PM – 01:00 PM", table_cell_center), Paragraph("12:15 PM – 12:35 PM", table_cell_center), Paragraph("327", table_cell_center), Paragraph("<b>GROUP C</b> (101) + <b>GROUP D</b> (197) + <b>GL 17</b> (29) <i>(All Cleared)</i>", table_cell_style)],
    ]
    sched_table = Table(sched_data, colWidths=[55, 50, 100, 100, 25, A4[0] - 72 - 330])
    sched_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0, 1), (0, 5), [colors.white, light_bg]),
        ('BACKGROUND', (0, 6), (-1, 6), colors.HexColor("#E0F2F1")),
        ('ROWBACKGROUNDS', (0, 7), (-1, -1), [colors.white, light_bg]),
        ('TOPPADDING', (0, 0), (-1, -1), 3.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(sched_table)
    story.append(Spacer(1, 10))

    # 3. Section: Self-Service & Engine
    story.append(Paragraph("3. Portal Features & 20-Minute Countdown Engine", h1_style))
    features_data = [
        [Paragraph("<b>Self-Service Portal & Passport Photo</b>", h2_style), Paragraph("<b>20-Minute CBT Engine & Security</b>", h2_style)],
        [
            Paragraph("• <b>Dual-Key Access:</b> Candidate logs in with PSN + Code 1.<br/>"
                      "• <b>Record Rectification:</b> Pre-loaded data displayed; candidate verifies spelling, phone, and email.<br/>"
                      "• <b>Live Passport Capture:</b> File upload or webcam capture with client-side 1:1 square crop and compression (< 80KB).<br/>"
                      "• <b>Official Photocard:</b> Printable A4 slip with embedded photo, schedule, barcode, and exam rules.", body_style),
            Paragraph("• <b>First-Use Scratch Lock:</b> Invigilator gives pure 5-digit Code 2 in hall; login binds token permanently to PSN.<br/>"
                      "• <b>Auto-Paper Delivery:</b> System matches candidate's <code>EXAM CODE</code> and renders departmental questions.<br/>"
                      "• <b>20:00 Timer:</b> Countdown starts on first screen. Auto-submits strictly at 00:00:00.<br/>"
                      "• <b>Crash Recovery:</b> Power/reboot allows candidate to log back in with same PSN + Token and resume remaining time.", body_style)
        ]
    ]
    features_table = Table(features_data, colWidths=[(A4[0] - 72)/2, (A4[0] - 72)/2])
    features_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(features_table)
    story.append(Spacer(1, 10))

    # Sign-off
    sign_data = [
        [Paragraph("<b>Prepared by:</b> CBT Technical Development Team", table_cell_style),
         Paragraph("<b>Authorized by:</b> Kwara State Civil Service Commission", table_cell_style),
         Paragraph("<b>Status:</b> Approved for Rollout", table_cell_bold)]
    ]
    sign_table = Table(sign_data, colWidths=[(A4[0] - 72)/3, (A4[0] - 72)/3, (A4[0] - 72)/3])
    sign_table.setStyle(TableStyle([
        ('LINEABOVE', (0, 0), (-1, -1), 1, primary_color),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(sign_table)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF successfully regenerated: {filename}")

if __name__ == "__main__":
    out_dir = r"C:\Users\hp\Desktop\DataClassPython"
    out_file = os.path.join(out_dir, "Kwara_CBT_Promotion_Evaluation_Implementation_Plan.pdf")
    build_pdf(out_file)

    downloads_file = r"C:\Users\hp\Downloads\Kwara_CBT_Promotion_Evaluation_Implementation_Plan.pdf"
    import shutil
    shutil.copyfile(out_file, downloads_file)
    print(f"Copy also updated in: {downloads_file}")
