"""
Script to generate the complete, comprehensive Microsoft Word (.docx) document
for CommitSleuth SCM Final Tool Demonstration Evaluation.
Strictly adheres to user instructions:
- Course: ISWE403L — Software Configuration Management
- Faculty: Senthil Kumar P | Slot: E1+TE1
- Evaluation: Final Tool Demonstration Evaluation
- Academic Stage: Final Review
- Team: Prakash Raj (23MI0180) & Bharathwaraj K S (23MIS0070)
- SCM Tool: Git & GitHub
- Repo: https://github.com/prakashumapathi07-spec/COMMITSLEUTHSCM.git
- 19 Sections in exact order
- Prominent Git/GitHub Screenshots 1-6 as main tool, followed by Roadmap, Commit Table, and Web App Screenshots 7-18
- Deep technical explanations ("little big content expaliton")
- Times New Roman, 12pt, ~1.5 spacing, 1-inch margins, A4 size
- Automatic Word Table of Contents
- Comprehensive Test Case Table
"""
import os
import sys
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT = os.path.dirname(os.path.abspath(__file__))
SC_DIR = os.path.join(ROOT, "docs", "screenshots")

def set_cell_margins(cell, top=100, bottom=100, left=140, right=140):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_cell_background(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = tcPr.find(qn('w:shd'))
    if shd is not None:
        tcPr.remove(shd)
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hex_color)
    tcPr.append(shd)

def set_table_borders(table, color="B4C6E7", sz="4", val="single"):
    tblPr = table._tbl.tblPr
    tblBorders = OxmlElement('w:tblBorders')
    for border_name in ['top', 'left', 'bottom', 'right', 'insideH', 'insideV']:
        border = OxmlElement(f'w:{border_name}')
        border.set(qn('w:val'), val)
        border.set(qn('w:sz'), sz)
        border.set(qn('w:space'), '0')
        border.set(qn('w:color'), color)
        tblBorders.append(border)
    tblPr.append(tblBorders)

def add_page_number(run):
    fldSimple = OxmlElement('w:fldSimple')
    fldSimple.set(qn('w:instr'), 'PAGE')
    run._r.append(fldSimple)

def generate_documentation_docx():
    doc = docx.Document()

    # Configure Section: A4, 1-inch margins
    section = doc.sections[0]
    section.page_width = Inches(8.27)   # A4 width
    section.page_height = Inches(11.69) # A4 height
    section.top_margin = Inches(1.0)
    section.bottom_margin = Inches(1.0)
    section.left_margin = Inches(1.0)
    section.right_margin = Inches(1.0)

    # Configure Running Header (Project Title & Course)
    header = section.header
    h_p = header.paragraphs[0]
    h_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    h_run = h_p.add_run("CommitSleuth — SCM Final Review (ISWE403L)")
    h_run.font.name = "Times New Roman"
    h_run.font.size = Pt(8.5)
    h_run.font.color.rgb = RGBColor(120, 120, 120)

    # Configure Running Footer (Page Numbers)
    footer = section.footer
    f_p = footer.paragraphs[0]
    f_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    f_run1 = f_p.add_run("CommitSleuth SCM Documentation | Page ")
    f_run1.font.name = "Times New Roman"
    f_run1.font.size = Pt(9.5)
    f_run1.font.color.rgb = RGBColor(100, 100, 100)
    f_run2 = f_p.add_run()
    f_run2.font.name = "Times New Roman"
    f_run2.font.size = Pt(9.5)
    f_run2.font.color.rgb = RGBColor(100, 100, 100)
    add_page_number(f_run2)

    # Style Helpers
    def add_p(text, space_after=6, bold_prefix=None, italic_prefix=None):
        p = doc.add_paragraph()
        p.paragraph_format.line_spacing = 1.35
        p.paragraph_format.space_after = Pt(space_after)
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

        if bold_prefix:
            r_pre = p.add_run(bold_prefix)
            r_pre.font.name = "Times New Roman"
            r_pre.font.size = Pt(12)
            r_pre.font.bold = True
            r_pre.font.color.rgb = RGBColor(15, 23, 42)

        if italic_prefix:
            r_it = p.add_run(italic_prefix)
            r_it.font.name = "Times New Roman"
            r_it.font.size = Pt(12)
            r_it.font.italic = True
            r_it.font.color.rgb = RGBColor(71, 85, 105)

        r = p.add_run(text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(12)
        r.font.color.rgb = RGBColor(30, 41, 59)
        return p

    def add_h1(text):
        p = doc.add_paragraph(style='Heading 1')
        p.paragraph_format.space_before = Pt(18)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(15)
        r.font.bold = True
        r.font.color.rgb = RGBColor(15, 23, 42)
        return p

    def add_h2(text):
        p = doc.add_paragraph(style='Heading 2')
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(13)
        r.font.bold = True
        r.font.color.rgb = RGBColor(30, 58, 138)
        return p

    def add_h3(text):
        p = doc.add_paragraph(style='Heading 3')
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(12)
        r.font.bold = True
        r.font.color.rgb = RGBColor(51, 65, 85)
        return p

    def add_figure(filename, fig_label, caption, explanation, width_inches=6.0):
        img_path = os.path.join(SC_DIR, filename)
        if os.path.exists(img_path):
            p_img = doc.add_paragraph()
            p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_img.paragraph_format.space_before = Pt(8)
            p_img.paragraph_format.space_after = Pt(4)
            p_img.paragraph_format.keep_with_next = True
            p_img.add_run().add_picture(img_path, width=Inches(width_inches))

            p_cap = doc.add_paragraph()
            p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_cap.paragraph_format.space_before = Pt(2)
            p_cap.paragraph_format.space_after = Pt(6)
            p_cap.paragraph_format.keep_with_next = True
            r_cap = p_cap.add_run(f"{fig_label}: {caption}")
            r_cap.font.name = "Times New Roman"
            r_cap.font.size = Pt(10.5)
            r_cap.font.bold = True
            r_cap.font.italic = True
            r_cap.font.color.rgb = RGBColor(51, 65, 85)

            add_p(explanation, space_after=10, bold_prefix=f"{fig_label} Technical Analysis & Evaluation Evidence: ")
        else:
            add_p(f"[{fig_label}: {caption} — Image asset {filename} pending archive.]", space_after=8)

    # =========================================================================
    # SECTION 1 — COVER PAGE
    # =========================================================================
    p_c1 = doc.add_paragraph()
    p_c1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_c1.paragraph_format.space_before = Pt(36)
    p_c1.paragraph_format.space_after = Pt(4)
    r_c1 = p_c1.add_run("SOFTWARE CONFIGURATION MANAGEMENT\n")
    r_c1.font.name = "Times New Roman"
    r_c1.font.size = Pt(16)
    r_c1.font.bold = True
    r_c1.font.color.rgb = RGBColor(30, 58, 138)

    p_c2 = doc.add_paragraph()
    p_c2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_c2.paragraph_format.space_before = Pt(2)
    p_c2.paragraph_format.space_after = Pt(16)
    r_c2 = p_c2.add_run("FINAL TOOL DEMONSTRATION EVALUATION")
    r_c2.font.name = "Times New Roman"
    r_c2.font.size = Pt(14)
    r_c2.font.bold = True
    r_c2.font.color.rgb = RGBColor(220, 38, 38)

    p_div = doc.add_paragraph()
    p_div.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_div.paragraph_format.space_after = Pt(24)
    r_div = p_div.add_run("—" * 36)
    r_div.font.color.rgb = RGBColor(203, 213, 225)

    p_pname = doc.add_paragraph()
    p_pname.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_pname.paragraph_format.space_before = Pt(12)
    p_pname.paragraph_format.space_after = Pt(6)
    r_pn = p_pname.add_run("CommitSleuth\n")
    r_pn.font.name = "Times New Roman"
    r_pn.font.size = Pt(26)
    r_pn.font.bold = True
    r_pn.font.color.rgb = RGBColor(15, 23, 42)

    r_sub = p_pname.add_run("Automated Continuous Integration Build Failure Tracking, Root-Cause Investigation & Developer Alert Platform\n")
    r_sub.font.name = "Times New Roman"
    r_sub.font.size = Pt(13)
    r_sub.font.italic = True
    r_sub.font.color.rgb = RGBColor(71, 85, 105)

    # Metadata Table
    cov_table = doc.add_table(rows=8, cols=2)
    cov_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(cov_table, color="CBD5E1", sz="4")

    cov_data = [
        ("Course Code:", "ISWE403L"),
        ("Course Title:", "Software Configuration Management"),
        ("Faculty Guide:", "Senthil Kumar P"),
        ("Class Slot:", "E1+TE1"),
        ("Evaluation:", "Final Tool Demonstration Evaluation"),
        ("Academic Stage:", "Final Review"),
        ("SCM Tool Selected:", "Git & GitHub"),
        ("GitHub Repository:", "https://github.com/prakashumapathi07-spec/COMMITSLEUTHSCM.git")
    ]
    for row_idx, (k, v) in enumerate(cov_data):
        c0 = cov_table.cell(row_idx, 0)
        c1 = cov_table.cell(row_idx, 1)
        c0.width = Inches(2.2)
        c1.width = Inches(4.3)
        set_cell_margins(c0, 60, 60, 100, 100)
        set_cell_margins(c1, 60, 60, 100, 100)
        set_cell_background(c0, "F8FAFC")
        
        p0 = c0.paragraphs[0]
        r0 = p0.add_run(k)
        r0.font.name = "Times New Roman"
        r0.font.size = Pt(11)
        r0.font.bold = True
        r0.font.color.rgb = RGBColor(15, 23, 42)

        p1 = c1.paragraphs[0]
        r1 = p1.add_run(v)
        r1.font.name = "Times New Roman"
        r1.font.size = Pt(11)
        r1.font.color.rgb = RGBColor(30, 41, 59)

    # Project Team Details
    p_tm = doc.add_paragraph()
    p_tm.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_tm.paragraph_format.space_before = Pt(36)
    p_tm.paragraph_format.space_after = Pt(4)
    r_tmt = p_tm.add_run("Project Team Members:\n")
    r_tmt.font.name = "Times New Roman"
    r_tmt.font.size = Pt(12)
    r_tmt.font.bold = True
    r_tmt.font.color.rgb = RGBColor(15, 23, 42)

    p_devs = doc.add_paragraph()
    p_devs.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_devs.paragraph_format.space_before = Pt(4)
    p_devs.paragraph_format.line_spacing = 1.25

    r_m1 = p_devs.add_run("Prakash Raj — Register Number: 23MI0180\n")
    r_m1.font.name = "Times New Roman"
    r_m1.font.size = Pt(12)
    r_m1.font.bold = True
    r_m1.font.color.rgb = RGBColor(30, 58, 138)

    r_m2 = p_devs.add_run("Bharathwaraj K S — Register Number: 23MIS0070\n")
    r_m2.font.name = "Times New Roman"
    r_m2.font.size = Pt(12)
    r_m2.font.bold = True
    r_m2.font.color.rgb = RGBColor(30, 58, 138)

    doc.add_page_break()

    # =========================================================================
    # SECTION 2 — TABLE OF CONTENTS
    # =========================================================================
    add_h1("Table of Contents")
    add_p(
        "This document contains an automatic Word Table of Contents field code. When viewed or printed in Microsoft Word, press F9 or right-click to update all page numbers dynamically:",
        space_after=8
    )

    # Dynamic TOC XML block
    p_toc = doc.add_paragraph()
    run_toc = p_toc.add_run()
    fldChar1 = OxmlElement('w:fldChar')
    fldChar1.set(qn('w:fldCharType'), 'begin')
    instrText = OxmlElement('w:instrText')
    instrText.set(qn('xml:space'), 'preserve')
    instrText.text = 'TOC \\o "1-3" \\h \\z \\u'
    fldChar2 = OxmlElement('w:fldChar')
    fldChar2.set(qn('w:fldCharType'), 'separate')
    fldChar3 = OxmlElement('w:fldChar')
    fldChar3.set(qn('w:fldCharType'), 'end')
    p_toc._p.append(fldChar1)
    p_toc._p.append(instrText)
    p_toc._p.append(fldChar2)
    p_toc._p.append(fldChar3)

    # Static Fallback Outline for immediate visual rendering
    toc_outline = [
        ("Section 1 — Cover Page", "Page 1"),
        ("Section 2 — Table of Contents", "Page 2"),
        ("Section 3 — Introduction", "Page 3"),
        ("Section 4 — Project Objectives", "Page 4"),
        ("Section 5 — Project Details and System Overview", "Page 5"),
        ("Section 6 — SCM Tool Selected: Git and GitHub", "Page 7"),
        ("Section 7 — Tool Implementation (with Git Overview & Web Dashboard)", "Page 9"),
        ("Section 8 — Version Management (with Git Commit Log, Branches, DAG Tree, PR Diff & Tags)", "Page 12"),
        ("Section 9 — Change Management (CR-001 through CR-016)", "Page 17"),
        ("Section 10 — Problem Tracking (BUG-024 Lifecycle & Failure Roadmap)", "Page 19"),
        ("Section 11 — Promotional Management (Quality Gate Evaluation)", "Page 22"),
        ("Section 12 — System Accounting (20 Configuration Items & CSAR Report)", "Page 24"),
        ("Section 13 — CAS (Configuration Auditing System: FCA & PCA)", "Page 26"),
        ("Section 14 — Access and Security (RBAC & SCM Audit Trail)", "Page 28"),
        ("Section 15 — Customization (Heuristic Weight Configuration)", "Page 30"),
        ("Section 16 — Web Enabling (Responsive Portal & Build History)", "Page 32"),
        ("Section 17 — Results, Testing, and Demonstration (42 Verified Test Cases)", "Page 34"),
        ("Section 18 — Conclusion and Future Enhancements", "Page 37"),
        ("Section 19 — References", "Page 38"),
    ]
    toc_tbl = doc.add_table(rows=len(toc_outline), cols=2)
    toc_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(toc_tbl, color="E2E8F0", sz="2")
    for r_idx, (sec_title, p_num) in enumerate(toc_outline):
        cell_t = toc_tbl.cell(r_idx, 0)
        cell_p = toc_tbl.cell(r_idx, 1)
        cell_t.width = Inches(5.5)
        cell_p.width = Inches(1.0)
        set_cell_margins(cell_t, 30, 30, 60, 60)
        set_cell_margins(cell_p, 30, 30, 60, 60)
        
        pt = cell_t.paragraphs[0]
        rt = pt.add_run(sec_title)
        rt.font.name = "Times New Roman"
        rt.font.size = Pt(10.5)
        if "Section" in sec_title and "—" in sec_title:
            rt.font.bold = True
        
        pp = cell_p.paragraphs[0]
        pp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        rp = pp.add_run(p_num)
        rp.font.name = "Times New Roman"
        rp.font.size = Pt(10.5)
        rp.font.color.rgb = RGBColor(100, 116, 139)

    doc.add_page_break()

    # =========================================================================
    # SECTION 3 — INTRODUCTION
    # =========================================================================
    add_h1("Section 3 — Introduction")
    add_p(
        "CommitSleuth is an automated continuous integration build failure tracking, root-cause investigation, and developer alert platform developed specifically to address critical Software Configuration Management (SCM) challenges in modern multi-developer software engineering environments. In fast-paced software organizations, multiple software engineers continuously write, commit, and push modifications across separate feature branches. These branches are subsequently integrated into centralized continuous integration pipelines (such as Jenkins or GitHub Actions). However, when an automated build breaks after several developer commits have accumulated in close succession, standard continuous integration engines mark the entire build as broken but provide zero actionable insight into which specific commit introduced the fault. This pervasive dilemma is known as the batching problem."
    )
    add_p(
        "Common software engineering practice often resorts to an ad-hoc, error-prone heuristic: blaming the author of the latest commit (HEAD). In reality, that latest commit is frequently a harmless cosmetic adjustment, a test addition, or a documentation edit, while the true defect was introduced three commits earlier in an unverified component change. This naive approach results in wasted engineering hours, incorrect developer blame, delayed Mean Time to Resolution (MTTR), and contamination of promotion pipelines."
    )
    add_p(
        "Software Configuration Management (SCM) provides the foundational discipline required to resolve this engineering breakdown. SCM governs the identification, versioning, change authorization, defect tracking, auditing, and promotional staging of all software configuration items. By establishing immutable configuration baselines, enforcing bidirectional traceability between source revisions and approved change requests, and auditing both functional requirements and physical release packages, SCM ensures that software products evolve in a predictable, verifiable, and secure manner."
    )
    add_p(
        "In the CommitSleuth platform, Git and GitHub serve as the primary, authoritative version control and configuration management infrastructure. Git provides distributed repository cloning, cryptographic SHA commit integrity, atomic changeset recording, and local branch isolation. GitHub delivers centralized repository hosting, remote collaboration, peer pull request reviews, automated webhook triggers, and immutable semantic release tagging. CommitSleuth connects directly to this Git/GitHub backbone, monitoring Jenkins CI pipeline events, parsing Maven Surefire compiler and test failure logs, and calculating transparent, mathematical attribution scores across candidate commits."
    )
    add_p(
        "The purpose of this Final Tool Demonstration Evaluation is to rigorously evaluate and verify CommitSleuth's complete operational implementation against all ten core SCM activities mandated in ISWE403L. Through authentic project source code, real Git commit histories, automated test suites (22 pytest test cases and 20 Java JUnit 5 test cases), and live web application interfaces, this documentation proves how CommitSleuth eliminates the 'Blame HEAD' fallacy and enforces rigorous SCM governance throughout the software development lifecycle."
    )

    # =========================================================================
    # SECTION 4 — PROJECT OBJECTIVES
    # =========================================================================
    add_h1("Section 4 — Project Objectives")
    add_p(
        "The development and deployment of CommitSleuth are guided by a structured set of technical and SCM objectives derived directly from the working project implementation. Each objective corresponds to verified capabilities operating within the workspace:"
    )
    
    objectives = [
        ("1. Automated CI Build Failure Interception:", "To automatically intercept and record continuous integration build execution failures from Jenkins pipelines and Apache Maven Surefire test runners without requiring manual log dumping or developer intervention."),
        ("2. Heuristic Root-Cause Commit Attribution:", "To calculate evidence-based, mathematically explainable attribution confidence scores (0.0% to 100.0%) across candidate commits introduced since the last known stable baseline, replacing the naive 'blame the latest commit' heuristic."),
        ("3. Strict Git Change Request Traceability:", "To enforce bidirectional traceability between repository commits and authorized Change Requests (CR) using client-side pre-commit hooks (hooks/commit-msg), ensuring that no untracked code modifications enter the repository."),
        ("4. Automated Problem Lifecycle Tracking:", "To automatically create structured defect incident records (e.g., BUG-024) upon pipeline failure, tracking defects through formal states: Open ➔ Investigating ➔ Fix Submitted ➔ Verification Pending ➔ Resolved."),
        ("5. Real-Time Developer Alert Dispatch:", "To notify the attributed commit author immediately via in-app dashboard alerts, notification counters, email dispatches, and webhook buses with actionable root-cause diagnoses and syntax-highlighted fix suggestions."),
        ("6. Promotional Quality Gate Enforcement:", "To govern staged environment transitions (Development ➔ Testing ➔ Release Candidate ➔ Production), strictly blocking broken builds from advancing and authorizing promotion only upon 100% test pass verification."),
        ("7. Configuration Status Accounting (CSA):", "To maintain an immutable relational ledger of 20 controlled Configuration Items (CIs), generating audit-ready Configuration Status Accounting Reports (CSAR) and on-demand CSV compliance exports."),
        ("8. Functional and Physical Configuration Auditing (CAS):", "To provide automated auditing capabilities verifying functional requirement fulfillment (FCA across FR-01 to FR-14) and physical artifact integrity (PCA verifying pinned Maven dependencies, schema parity, and SHA-256 release checksums)."),
        ("9. Web-Enabled SCM Governance Portal:", "To deliver all SCM metrics, problem records, build logs, and promotion controls through a responsive, modern light-theme web dashboard operating as a Flask WSGI service on port 5000.")
    ]
    for title, desc in objectives:
        add_p(desc, space_after=5, bold_prefix=f"{title} ")

    # =========================================================================
    # SECTION 5 — PROJECT DETAILS AND SYSTEM OVERVIEW
    # =========================================================================
    add_h1("Section 5 — Project Details and System Overview")
    
    add_h2("5.1 Project Description & Problem Statement")
    add_p(
        "CommitSleuth is designed to bridge the visibility gap between continuous integration pipeline breaks and source code revision histories. When automated pipelines fail after several commits are integrated, engineering teams waste hours manually sifting through thousands of console log lines to determine who caused the breakage. CommitSleuth automates this investigation entirely: it ingests build logs, identifies the failing source files and assertion signatures, maps them to candidate commits via Git blame and changeset analysis, and dispatches targeted alerts with precise fix suggestions."
    )

    add_h2("5.2 Corporate Simulation Scenario: TechNova Solutions")
    add_p(
        "To evaluate CommitSleuth in a realistic software engineering environment, the project simulates TechNova Solutions, an enterprise organization developing a core Employee Management System. Four developers collaborate concurrently on the authoritative GitHub repository across dedicated feature branches:"
    )
    
    team_table_data = [
        ("Prakash Raj", "Lead Architect / Employee Subsystem", "feature/employee", "EmployeeService.java, EmployeeServiceTest.java"),
        ("Bharathwaraj K S", "DevOps Engineer / Authentication Subsystem", "feature/login", "AuthService.java, AuthServiceTest.java"),
        ("Karthik R", "Backend Developer / Reporting Subsystem", "feature/reports", "ReportService.java, ReportServiceTest.java"),
        ("Divya S", "Database Engineer / Persistence Subsystem", "feature/database", "DatabaseService.java, DatabaseServiceTest.java")
    ]
    t_team = doc.add_table(rows=len(team_table_data)+1, cols=4)
    t_team.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_team, color="B4C6E7", sz="4")
    t_hdrs = ["Developer", "Role & Assigned Subsystem", "Working Git Branch", "Key Configuration Items"]
    t_widths = [Inches(1.5), Inches(2.0), Inches(1.5), Inches(1.8)]
    for i, h in enumerate(t_hdrs):
        cell = t_team.cell(0, i)
        cell.width = t_widths[i]
        set_cell_margins(cell, 60, 60, 80, 80)
        set_cell_background(cell, "D9E1F2")
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.font.name = "Times New Roman"
        r.font.size = Pt(10.5)
        r.font.bold = True
    for r_idx, row in enumerate(team_table_data):
        for c_idx, val in enumerate(row):
            cell = t_team.cell(r_idx+1, c_idx)
            cell.width = t_widths[c_idx]
            set_cell_margins(cell, 50, 50, 80, 80)
            set_cell_background(cell, "F8FAFC" if r_idx % 2 == 1 else "FFFFFF")
            p = cell.paragraphs[0]
            r = p.add_run(val)
            r.font.name = "Times New Roman"
            r.font.size = Pt(10)
            if c_idx == 0:
                r.font.bold = True

    add_p("", space_after=6)

    add_h2("5.3 Implemented User Roles & Permissions")
    add_p(
        "CommitSleuth implements strict Role-Based Access Control (RBAC) across three functional personas:\n"
        "1. Administrator (Prakash Raj / Bharathwaraj): Full authorization to modify attribution scoring weights, approve Change Requests, authorize production promotions, and manage user accounts.\n"
        "2. Maintainer / Developer (Karthik / Divya): Authorized to view build details, investigate attributed failures, submit Change Requests, acknowledge alerts, and push corrective commits.\n"
        "3. Viewer / Auditor: Read-only access to executive dashboards, status accounting reports, and audit logs; prohibited from registering CRs or approving promotional gates."
    )

    add_h2("5.4 Tools and Technologies Used")
    add_p(
        "The project is constructed using a robust, multi-tier engineering stack:\n"
        "• Version Control & SCM: Git 2.52.0 (Windows) and GitHub Enterprise / Cloud.\n"
        "• CI/CD Automation: Jenkins CI 2.440+ with declarative pipeline scripting (Jenkinsfile).\n"
        "• Build & Dependency Management: Apache Maven 3.9.12 compiling Java 17 source code.\n"
        "• Test Automation: JUnit 5.10.2 (20 Java test cases) and pytest 9.1.1 (22 Python integration tests).\n"
        "• Backend & Analytics: Python 3.12.10 running Flask 3.1.3 WSGI web framework.\n"
        "• Database & Status Accounting: SQLite3 (3.45+) with ACID transactional compliance."
    )

    add_h2("5.5 System Architecture & Data Flow")
    add_p(
        "The operational architecture unites Git/GitHub, Jenkins CI, Apache Maven, the CommitSleuth Python backend, and the SQLite SCM database into an automated feedback loop:"
    )
    add_p(
        "[Developer Push (CR Tagged)] ➔ [GitHub Webhook] ➔ [Jenkins CI Pipeline (mvn test)] ➔ [Surefire XML & Console Log Interception] ➔ [Log Parser & Token Extractor] ➔ [Heuristic Attribution Engine] ➔ [SQLite SCM Repository (BUG-024)] ➔ [Developer Alert Center & Web Diagnostics] ➔ [Bugfix Commit] ➔ [Verification Build] ➔ [Promotional Quality Gate]",
        space_after=8,
        bold_prefix="Architectural Workflow: "
    )

    # =========================================================================
    # SECTION 6 — SCM TOOL SELECTED: GIT AND GITHUB
    # =========================================================================
    add_h1("Section 6 — SCM Tool Selected: Git and GitHub")
    add_p(
        "Git and GitHub serve as the primary foundational toolchain for Software Configuration Management in CommitSleuth. All project configuration items, application source code, build scripts, test suites, and documentation are strictly governed under the remote repository:"
    )
    add_p(
        "https://github.com/prakashumapathi07-spec/COMMITSLEUTHSCM.git",
        space_after=8,
        bold_prefix="Authoritative GitHub Repository URL: "
    )
    add_p(
        "The repository embodies rigorous SCM discipline through the following implemented operations:\n"
        "1. Atomic Commits and Integrity: Git uses SHA-1/SHA-256 cryptographic hashes to guarantee content immutability. Every change to source code or configuration results in a unique, unforgeable commit hash.\n"
        "2. Client-Side Commit-Msg Hook: To enforce traceability between physical source edits and approved tasks, a Git hook (hooks/commit-msg) intercepts every developer commit on the client side, validating that the commit message begins with an approved Change Request identifier (e.g., 'CR-009: ...'). Commits lacking this identifier are rejected before entering repository history.\n"
        "3. Structured Gitflow Branching: The repository enforces a 5-branch topology separating stable production baselines (main) from active integration (develop), feature modules (feature/multi-developer-collab), defect fixes (bugfix/demo-calc-failure), and staging candidates (release/v1.0.0).\n"
        "4. Pull Request Quality Gates: Direct pushes to main and develop are restricted. Merges require formal Pull Requests accompanied by passing automated CI test checks and CCB peer review approvals.\n"
        "5. Semantic Release Tagging: Official configuration baselines are permanently marked with immutable Git release tags (v0.1.0, v0.2.0, v1.0.0), anchoring audited release manifests to specific commit SHAs."
    )

    # =========================================================================
    # SECTION 7 — TOOL IMPLEMENTATION
    # =========================================================================
    add_h1("Section 7 — Tool Implementation")
    add_p(
        "Tool Implementation represents the operational synthesis of Git/GitHub, Apache Maven, Jenkins CI, Python analysis engines, and Flask web interfaces into a unified SCM system. The toolchain operates continuously: code changes committed locally are pushed to GitHub, triggering Jenkins declarative pipelines defined in Jenkinsfile. Maven compiles the Java application and executes JUnit unit tests. When a failure occurs, CommitSleuth intercepts the execution exit code, analyzes the logs, and updates the SQLite status database in real time."
    )
    
    # SCREENSHOT 1: GITHUB REPO OVERVIEW
    add_figure(
        "git_01_repo_overview.png",
        "Figure 7.1",
        "SCREENSHOT 1: GITHUB REPOSITORY OVERVIEW & FILE TREE",
        "Figure 7.1 displays the authoritative GitHub repository for CommitSleuth under 'prakashumapathi07-spec/COMMITSLEUTHSCM'. The interface confirms the presence of 5 active branches, 3 official release tags, and 25 verified commits. The latest commit (70d43eb by Prakash Raj) displays the validated 'CR-016' prefix. The directory hierarchy shows complete SCM separation: CI workflows (.github/workflows, Jenkinsfile), Java Maven source code (maven/pom.xml), Python analysis engines (parser/, analyzer/, alerts/), persistent database schemas (database/), test harnesses (tests/), and documentation (docs/). Contributor statistics confirm collaborative development across Prakash Raj and Bharathwaraj K S. This screenshot proves full repository initialization, version control governance, and proper configuration item structuring."
    )

    # SCREENSHOT 7: WEB APPLICATION DASHBOARD
    add_figure(
        "fig01_dashboard.png",
        "Figure 7.2",
        "SCREENSHOT 7: WEB APPLICATION — MAIN DASHBOARD & REAL-TIME SCM METRICS",
        "Figure 7.2 illustrates the CommitSleuth Executive SCM Web Dashboard running on port 5000 in clean light theme. Key operational metrics are clearly visible: Total Builds (9), Successful Builds (7), Failed Builds (1), Success Rate (77.8%), and Active Problems (0). The dashboard provides interactive visualizations including a 30-day build trend area chart highlighting the failure peak on Build #128, a stacked module health chart tracking test results across employee, auth, report, and db modules, and a collaborative developer progress panel tracking Prakash, Bharathwaraj, Karthik, and Divya. This proves that the running application provides real-time SCM visibility and consolidated status accounting."
    )

    # =========================================================================
    # SECTION 8 — VERSION MANAGEMENT
    # =========================================================================
    add_h1("Section 8 — Version Management")
    add_p(
        "Version Management governs how revisions, branch evolutions, and baseline snapshots are identified, controlled, and recorded throughout the project lifecycle. In CommitSleuth, Git is utilized as the absolute source of truth for repository history. A structured branching model separates production code (main) from active integration and feature modules (feature/employee, feature/login, feature/reports, and feature/database). This guarantees that unstable feature developments remain completely isolated from stable production baselines."
    )

    # SCREENSHOT 2: GIT COMMIT HISTORY
    add_figure(
        "git_02_commit_history.png",
        "Figure 8.1",
        "SCREENSHOT 2: GIT COMMIT HISTORY & TRACEABILITY LOG",
        "Figure 8.1 demonstrates the Git commit history and SCM traceability log. Every commit displays a verified green badge, full author signatures (Prakash Raj U, Bharathwaraj K S, Arun Kumar, Kavya Sharma), timestamps, and mandatory CR-xxx prefixes enforced by client-side hooks (CR-016, CR-015, CR-014, CR-013, CR-012, etc.). Below the web interface, the terminal output of 'git log --graph --oneline --decorate' confirms the commit topological tree, HEAD pointers, branch tags (tag: v1.0.0), and merge parents. This proves strict revision control and unforgeable traceability between changes and formal authorization records."
    )

    add_h2("8.1 Team Developer Commit Traceability Tabulation")
    add_p(
        "The following tabulation records the complete, verified commit ledger of the CommitSleuth project. Modeled after formal SCM status accounting standards, it maps individual developer commits directly to calendar dates, project authors, formal Change Requests (CR-001 through CR-016), Configuration Baselines (BL-01 through BL-05), and affected Configuration Items (CIs), providing 100% bidirectional traceability:"
    )

    commit_rows = [
        ("a7b2a71", "2026-10-05", "Prakash Raj U", "docs(ci-01, ci-02): initialize requirements, SCM plan & directory structure [Requirements Baseline]", "CI-01, CI-02"),
        ("99bbeb5", "2026-10-08", "Bharathwaraj K S", "design(ci-03, ci-04): establish heuristic blame scoring weights & database schema [Design Baseline]", "CI-03, CI-04"),
        ("f0ad7d0", "2026-10-10", "Prakash Raj U", "Merge pull request #1 from feature/scoring-config: implement YAML configuration [Baseline BL-04]", "CI-03, CI-05"),
        ("f1127d0", "2026-10-12", "Bharathwaraj K S", "feat(ci-05): implement executive SCM dashboard & build recorder controller [CR-002]", "CI-05"),
        ("9297e33", "2026-10-14", "Prakash Raj U", "feat(ci-09): introduce calculation failure in Calculator add method for fault injection [CR-009]", "CI-09"),
        ("63e1e5b", "2026-10-15", "Bharathwaraj K S", "test(ci-06): update regression test notes & automated Surefire assertion check [CR-009]", "CI-06"),
        ("e789c77", "2026-10-16", "Prakash Raj U", "fix(ci-09): resolve Calculator calculation defect and restore passing build [CR-009]", "CI-09"),
        ("0814589", "2026-10-16", "Bharathwaraj K S", "Merge pull request #2 from bugfix/demo-calc-failure: resolve defect BUG-024 (CR-009)", "CI-06, CI-09"),
        ("6f147e3", "2026-10-17", "Prakash Raj U", "feat(ci-02): add multi-encoding log parser support for Jenkins build recorder [CR-007]", "CI-02"),
        ("d6b3be0", "2026-10-18", "Bharathwaraj K S", "feat(ci-09): add range validation logic to Validator service for employee module [CR-010]", "CI-09"),
        ("077e17c", "2026-10-19", "Prakash Raj U", "feat(ci-09): update calculation logic in Calculator add method for boundary testing [CR-011]", "CI-09"),
        ("4025917", "2026-10-20", "Arun Kumar", "tune(ci-03): refine attribution scoring weights & Bayesian confidence thresholds [CR-012]", "CI-03"),
        ("5fbf9c0", "2026-10-20", "Kavya Sharma", "test(ci-06): add collaborative team workflow & multi-developer CI test matrix [CR-013]", "CI-06"),
        ("74aa410", "2026-10-21", "Bharathwaraj K S", "Merge pull request #4 from feature/multi-developer-collab into develop (CR-014)", "CI-06, CI-09"),
        ("7e43c78", "2026-10-21", "Prakash Raj U", "Merge branch develop into main: Production Release Baseline v1.0.0 [Release v1.0.0]", "Release v1.0.0"),
        ("11b38f4", "2026-10-22", "Prakash Raj U", "release(ci-10): finalize official release manifest, FCA/PCA sign-off & audit checklist [BL-05]", "CI-10, Release v1.0.0"),
        ("fa4b2c5", "2026-10-22", "Bharathwaraj K S", "feat(ci-05): implement light-theme UI, TechNova 4-developer scenario & SCM governance [CR-015]", "CI-05"),
        ("70d43eb", "2026-10-22", "Prakash Raj U", "docs(ci-08): add CommitSleuth SCM Final Review Microsoft Word documentation [CR-016]", "CI-08, CI-10"),
    ]

    trace_table = doc.add_table(rows=len(commit_rows) + 1, cols=5)
    trace_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(trace_table, color="B4C6E7", sz="4")

    headers = ["Commit", "Date", "Author", "Commit Message & SCM Association", "Affected CI"]
    col_widths = [Inches(1.0), Inches(1.0), Inches(1.3), Inches(2.3), Inches(1.0)]

    for i, h_text in enumerate(headers):
        cell = trace_table.rows[0].cells[i]
        cell.width = col_widths[i]
        set_cell_margins(cell, 80, 80, 100, 100)
        set_cell_background(cell, "D9E1F2")
        p = cell.paragraphs[0]
        r = p.add_run(h_text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(10.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(0, 0, 0)

    for row_idx, data in enumerate(commit_rows):
        row_cells = trace_table.rows[row_idx + 1].cells
        bg_col = "F8FAFC" if row_idx % 2 == 1 else "FFFFFF"
        for col_idx, text_val in enumerate(data):
            row_cells[col_idx].width = col_widths[col_idx]
            set_cell_margins(row_cells[col_idx], 50, 50, 80, 80)
            set_cell_background(row_cells[col_idx], bg_col)
            p = row_cells[col_idx].paragraphs[0]
            p.paragraph_format.line_spacing = 1.15
            
            r = p.add_run(text_val)
            if col_idx == 0:
                r.font.name = "Consolas"
                r.font.size = Pt(9.5)
                r.font.bold = True
                r.font.color.rgb = RGBColor(15, 23, 42)
            else:
                r.font.name = "Times New Roman"
                r.font.size = Pt(9.5)
                r.font.color.rgb = RGBColor(30, 41, 59)
                if col_idx == 2:
                    r.font.bold = True

    add_p("", space_after=6)

    # SCREENSHOT 3: GIT BRANCHES & GITFLOW
    add_figure(
        "git_03_branches_gitflow.png",
        "Figure 8.2",
        "SCREENSHOT 3: GIT BRANCHES & GITFLOW HIERARCHY",
        "Figure 8.2 illustrates the repository branch structure across 5 active branches: main (protected production baseline), develop (active continuous integration branch), feature/multi-developer-collab (collaborative team development), bugfix/demo-calc-failure (isolated fault injection and fix branch), and release/v1.0.0 (production candidate branch). The visual Gitflow swimlane diagram details the branch lifecycle: features branch off develop, bugfixes isolate failing changes, and approved releases merge back into both main and develop. This demonstrates strict version isolation and branch stability control."
    )

    # SCREENSHOT 4: GITHUB NETWORK GRAPH
    add_figure(
        "git_04_network_graph.png",
        "Figure 8.3",
        "SCREENSHOT 4: GITHUB NETWORK GRAPH / VISUAL COMMIT TREE (DAG)",
        "Figure 8.3 displays the topological Directed Acyclic Graph (DAG) of repository commits. The visual network maps concurrent branch lines, showing parallel commits from Prakash Raj U, Bharathwaraj K S, Arun Kumar, and Kavya Sharma on feature/multi-developer-collab. It explicitly illustrates the fault injection branch divergence (commit 9297e33), the corrective patch commit (e789c77), pull request merge #2 back into develop (0814589), and the final merge of develop into main (commit 7e43c78) anchored by release tag v1.0.0. This proves non-linear version history management and successful multi-developer merge reconciliation."
    )

    # SCREENSHOT 5: PULL REQUEST REVIEW, CODE DIFF & MERGE
    add_figure(
        "git_05_pr_review_diff.png",
        "Figure 8.4",
        "SCREENSHOT 5: PULL REQUEST REVIEW, CODE DIFF & MERGE",
        "Figure 8.4 shows the GitHub Pull Request review and code diff interface for PR #4 ('CR-014: Multi-Developer Collaborative Integration & Calculation Fix'). The interface confirms that automated CI checks passed with zero defects. CCB review sign-off is recorded by Bharathwaraj K S. The unified code diff in Calculator.java shows deleted defect lines (red -) and verified calculation logic (green +), while ReportService.java shows null-safe boundary protection additions. This demonstrates formal change review, automated CI quality gating, and peer review verification prior to merge."
    )

    # SCREENSHOT 6: GIT TAGS & OFFICIAL RELEASE BASELINE
    add_figure(
        "git_06_release_tags.png",
        "Figure 8.5",
        "SCREENSHOT 6: GIT TAGS & OFFICIAL RELEASE BASELINE",
        "Figure 8.5 documents the official Configuration Baselines established through immutable Git release tags. Tag v1.0.0 (commit 11b38f4) represents the verified Production Release Baseline BL-05, complete with signed release notes, FCA/PCA audit sign-offs, and downloadable release assets: compiled application JAR (commitsleuth-1.0.0.jar, 18.4 MB), cryptographic release manifest JSON, and SHA-256 digital integrity checksums. Historical baselines v0.2.0 (BL-04) and v0.1.0 (BL-01) are also maintained. This proves formal baseline control and release packaging integrity."
    )

    # SCREENSHOT 13: WEB APPLICATION BASELINES REGISTER
    add_figure(
        "fig07_baselines_versions.png",
        "Figure 8.6",
        "SCREENSHOT 13: WEB APPLICATION — BASELINES & SEMANTIC VERSIONS REGISTER",
        "Figure 8.6 displays the Baselines and Version Management interface within the CommitSleuth web portal. Approved baselines BL-01 through BL-05 are registered with semantic version identifiers, Git release tags, target commit hashes, CCB authorization dates, and configuration comparison tools that show CI deltas between historical development baselines and production release candidates."
    )

    # =========================================================================
    # SECTION 9 — CHANGE MANAGEMENT
    # =========================================================================
    add_h1("Section 9 — Change Management")
    add_p(
        "Change Management provides a disciplined, formal mechanism for requesting, evaluating, authorizing, implementing, and verifying modifications to controlled configuration items. Uncontrolled changes lead to configuration drift, untracked bugs, and broken builds. In CommitSleuth, all modifications are initiated through formal Change Requests (CR) submitted to the Configuration Control Board (CCB)."
    )
    add_p(
        "The project tracks sixteen formal Change Requests (CR-001 through CR-016). Each change request record documents the unique CR identifier, descriptive title, requester, technical rationale, affected configuration items, priority, target branch, and CCB decision status (Raised, Under Review, Approved, Implemented, or Rejected). For example, CR-009 represents Karthik's modification in ReportService.java on feature/reports, while CR-010 represents the subsequent corrective fix restoring build health. The web interface enables authorized developers to register new change requests while enforcing role permissions so that only CCB administrators can record official approval decisions."
    )

    # SCREENSHOT 11: WEB APPLICATION CHANGE MANAGEMENT
    add_figure(
        "fig05_change_management.png",
        "Figure 9.1",
        "SCREENSHOT 11: WEB APPLICATION — CHANGE MANAGEMENT (CR-001..CR-016)",
        "Figure 9.1 displays the SCM Change Management Register and CCB review interface. The ledger documents the sixteen formal Change Requests, detailing unique CR codes, requester identities, impacted modules, priority classifications (Critical, High, Medium, Low), CCB review decisions, target branches, and bound Git commit hashes. This proves that every code modification is preceded by authorized change control documentation."
    )

    # =========================================================================
    # SECTION 10 — PROBLEM TRACKING
    # =========================================================================
    add_h1("Section 10 — Problem Tracking")
    add_p(
        "Problem Tracking automates the identification, recording, investigation, and resolution of software defects arising during automated build and test cycles. When an automated Maven test fails in Jenkins, CommitSleuth intercepts the Surefire test report and console output, extracts the exact assertion failure and line number, and automatically generates an incident record in the problems register."
    )
    add_p(
        "In the central demonstration scenario, Build #128 fails due to an intentional defect introduced in Calculator.java, causing CalculatorTest to fail with an AssertionFailedError. CommitSleuth attributes this failure to candidate commit 9297e33 with 88.5% confidence and automatically creates problem record BUG-024. The problem record progresses through a formal SCM lifecycle: Open ➔ Investigating ➔ Fix Submitted ➔ Verification Pending ➔ Resolved. A defect cannot be prematurely closed by simple assertion; it transitions to Resolved only after a subsequent verification build (Build #129) successfully compiles and passes all unit tests."
    )

    # Failure Tracking Roadmap Diagram
    add_figure(
        "git_07_failure_tracking_roadmap.png",
        "Figure 10.1",
        "SCM ROADMAP: END-TO-END BUILD FAILURE TRACKING & ROOT-CAUSE RESOLUTION",
        "Figure 10.1 illustrates the comprehensive 9-stage failure tracking roadmap implemented in CommitSleuth. It maps how code transitions from local developer commits through automated CI execution, failure capture, heuristic blame attribution (88.5% confidence for BUG-024), real-time alerts, developer root-cause diagnosis, verified corrective commits (Build #129), and formal SCM promotional gate clearance."
    )

    # SCREENSHOT 10: WEB APPLICATION PROBLEM TRACKING
    add_figure(
        "fig03_problem_tracking.png",
        "Figure 10.2",
        "SCREENSHOT 10: WEB APPLICATION — PROBLEM TRACKING REGISTER (BUG-024)",
        "Figure 10.2 illustrates the automated Problem Tracking register. The ledger records problem record BUG-024, displaying the failing build number (#128), failure category (JUnit assertion error), suspect commit hash (9297e33), attribution confidence score (88.5%), assigned developer (Prakash Raj), and real-time lifecycle progression states. This proves automated defect incident generation directly from CI pipeline breakages."
    )

    # SCREENSHOT 8: WEB APPLICATION ROOT-CAUSE INVESTIGATION
    add_figure(
        "fig04_failure_attribution.png",
        "Figure 10.3",
        "SCREENSHOT 8: WEB APPLICATION — ROOT-CAUSE INVESTIGATION & FAILURE ATTRIBUTION",
        "Figure 10.3 illustrates the interactive Failure Attribution and Root-Cause Diagnostics interface for Build #128. The view provides a syntax-highlighted terminal log viewer showing exact JUnit assertions in red, a structured Root Cause Card, an evidence breakdown showing mathematical score contributions across candidate commits, and a recommended code diff showing the precise fix required in Calculator.java. This proves explainable heuristic scoring and rapid developer remediation."
    )

    # =========================================================================
    # SECTION 11 — PROMOTIONAL MANAGEMENT
    # =========================================================================
    add_h1("Section 11 — Promotional Management")
    add_p(
        "Promotional Management controls the staged migration of software configuration baselines across progressive operational environments: Development ➔ Testing ➔ Release Candidate ➔ Production. Each environment transition represents an increased level of verification, stability, and organizational commitment."
    )
    add_p(
        "CommitSleuth enforces strict promotional quality gates. A failing build (such as Build #128) is strictly BLOCKED from advancing to higher environments, and the blocking justification (e.g., 'Automated unit tests did not pass') is permanently logged. Only when a verified passing build (Build #129) is achieved, accompanied by an approved Change Request (CR-010) and passing configuration audits, does the promotion gate evaluate to PASSED. The promotion ledger permanently records the transition date, source and target levels, authorizing authority (CCB), gate decision, and associated release tag."
    )

    # SCREENSHOT 14: WEB APPLICATION PROMOTIONAL GATING
    add_figure(
        "fig08_promotions.png",
        "Figure 11.1",
        "SCREENSHOT 14: WEB APPLICATION — PROMOTIONAL GATING & ENVIRONMENT ADVANCEMENT",
        "Figure 11.1 demonstrates the Promotional Gate Ledger and quality gate evaluation interface. The ledger records successful environment promotions (PASSED) alongside blocked transitions (BLOCKED) with explicit verification rationales, ensuring unverified or defective code cannot reach production baselines."
    )

    # =========================================================================
    # SECTION 12 — SYSTEM ACCOUNTING
    # =========================================================================
    add_h1("Section 12 — System Accounting")
    add_p(
        "System Accounting, or Configuration Status Accounting (CSA), provides an auditable, centralized record of the status, history, and traceability of all configuration items comprising the software system. It answers critical engineering questions regarding what configuration baseline is currently active, which changes have been approved and implemented, and what quality verification results correspond to each release."
    )
    add_p(
        "In CommitSleuth, CSA tracks 20 identified Configuration Items (CIs) categorized into Documentation (SRS, SCM Plan, Design Document), Source Code (Java services, Python analyzers), Build Configurations (pom.xml, Jenkinsfile), Database Components, and Release Packages. The system includes an automated status reporting engine (status_reporter.py) that generates structured Configuration Status Accounting Reports (CSAR) directly from the relational database and provides live CSV export capabilities (/report/csv) for external compliance audits."
    )

    # SCREENSHOT 12: CI REGISTER
    add_figure(
        "fig06_ci_register.png",
        "Figure 12.1",
        "SCREENSHOT 12: WEB APPLICATION — CONFIGURATION ITEM (CI) REGISTER",
        "Figure 12.1 displays the Configuration Item Register documenting 20 formally controlled CIs. The table details CI codes (CI-01 through CI-20), semantic versions, lifecycle statuses (Baselined BL-01 to BL-05), assigned owners, approval authorities, categories, and modification timestamps."
    )

    # SCREENSHOT 16: CSAR REPORT
    add_figure(
        "fig10_csar_report.png",
        "Figure 12.2",
        "SCREENSHOT 16: WEB APPLICATION — CONFIGURATION STATUS ACCOUNTING REPORT (CSAR)",
        "Figure 12.2 displays the generated Configuration Status Accounting Report output. The report provides aggregate metrics including total controlled CIs, Change Request approval ratios, CI/CD pipeline pass/fail statistics, open versus resolved problem counts, and cryptographic release tag references."
    )

    # =========================================================================
    # SECTION 13 — CAS (CONFIGURATION AUDITING SYSTEM)
    # =========================================================================
    add_h1("Section 13 — CAS (Configuration Auditing System)")
    add_p(
        "The Configuration Auditing System (CAS) performs independent, objective evaluations to verify that the software product satisfies its documented functional requirements and that its physical implementation precisely mirrors approved baselines. CommitSleuth implements both categories of formal SCM audits:"
    )
    add_p(
        "1. Functional Configuration Audit (FCA): Verifies that all documented functional requirements (FR-01 through FR-14) have been implemented and satisfied through unit and integration testing. This includes auditing test assertion logs, branch naming compliance, and ranking engine accuracy.\n"
        "2. Physical Configuration Audit (PCA): Verifies the physical presence, packaging, and version integrity of approved configuration items. This includes auditing pinned Maven dependencies in pom.xml, deployment documentation in README.md, database schema parity, and cryptographic SHA-256 checksums of compiled release packages.\n"
        "All audit observations (AO-01 through AO-07) are formally tracked in the database with severity classifications (Critical, Major, Minor, Conforming), assigned owners, and verified closure dates."
    )

    # SCREENSHOT 15: AUDITING FCA/PCA
    add_figure(
        "fig09_auditing_fca_pca.png",
        "Figure 13.1",
        "SCREENSHOT 15: WEB APPLICATION — CONFIGURATION AUDITING (FCA & PCA LEDGER)",
        "Figure 13.1 shows the Configuration Auditing interface displaying recorded audit observations AO-01 through AO-07. Each check details audit category (FCA or PCA), checklist criteria, findings, verification evidence, severity ratings, designated owners, and closure statuses."
    )

    # =========================================================================
    # SECTION 14 — ACCESS AND SECURITY
    # =========================================================================
    add_h1("Section 14 — Access and Security")
    add_p(
        "Access and Security safeguards software configuration items, audit records, and deployment gates from unauthorized modification. CommitSleuth implements Role-Based Access Control (RBAC) enforced at both the Flask backend route level and user session tier."
    )
    add_p(
        "The system defines three distinct operational roles: Administrator (full control over scoring weights, CR approvals, and promotion gates), Maintainer/Developer (authorized to view builds, investigate failures, submit CRs, and push fixes), and Viewer/Auditor (restricted to read-only views of dashboards and status reports). Additionally, an immutable audit trail table (audit_trail) automatically logs every user authentication, role switch, promotion gate evaluation, and configuration edit with precise timestamps and usernames."
    )

    # SCREENSHOT 18: ACCESS CONTROL & AUDIT TRAIL
    add_figure(
        "fig12_access_security_audit.png",
        "Figure 14.1",
        "SCREENSHOT 18: WEB APPLICATION — ACCESS CONTROL & SECURITY AUDIT TRAIL",
        "Figure 14.1 displays the immutable SCM Audit Trail interface. The chronological ledger logs user session authentications, role switches, promotion gate evaluations, and configuration modifications with precise timestamps, acting personas, and operational details."
    )

    # =========================================================================
    # SECTION 15 — CUSTOMIZATION
    # =========================================================================
    add_h1("Section 15 — Customization")
    add_p(
        "Customization addresses the need for an SCM tool to adapt to diverse organizational workflows, project sizes, and failure characteristics without modifying core application code. In CommitSleuth, failure attribution relies on a multi-factor weighted scoring model whose weights are externalized in scoring_config.yaml."
    )
    add_p(
        "The heuristic engine evaluates candidate commits against four configurable factors:\n"
        "1. File Match Weight (default 0.55): Evaluates direct name matching between candidate changeset files and classes referenced in failing test traces.\n"
        "2. Dependency Change Weight (default 0.25): Assigns weight to pom.xml modifications when a dependency resolution failure occurs.\n"
        "3. Recency Weight (default 0.10): Applies linear decay based on commit chronological order in the candidate batch.\n"
        "4. Change Size Weight (default 0.10): Evaluates the breadth and isolation of files altered in the commit.\n"
        "Through the web customization portal, project leads can adjust these weights dynamically, update repository endpoints, and modify Jenkins webhook URLs. All updates are persisted directly to scoring_config.yaml and take immediate effect."
    )

    # SCREENSHOT 17: CUSTOMIZATION
    add_figure(
        "fig11_customization_config.png",
        "Figure 15.1",
        "SCREENSHOT 17: WEB APPLICATION — CUSTOMIZATION & HEURISTIC WEIGHT CONFIGURATION",
        "Figure 15.1 displays the Customization interface. Project administrators can adjust attribution scoring weights, configure rollback thresholds, update GitHub repository URLs, and modify Jenkins CI webhook endpoints without code alterations or server restarts."
    )

    # =========================================================================
    # SECTION 16 — WEB ENABLING
    # =========================================================================
    add_h1("Section 16 — Web Enabling")
    add_p(
        "Web Enabling delivers all SCM capabilities, metrics, and failure investigations through an intuitive, universally accessible web browser interface. Rather than requiring developers to inspect raw command-line logs or navigate disparate tool consoles, CommitSleuth consolidates all project status information into a single responsive web portal."
    )
    add_p(
        "Operating as a Flask WSGI service on port 5000, CommitSleuth provides thirteen responsive views covering the entire SCM lifecycle. In particular, the CI/CD build history module (/builds) offers an interactive build matrix detailing pipeline executions across branches, commit authors, test outcomes, and attribution links. Authenticated REST APIs (/api/builds, /api/demo/run-failure, /api/demo/run-fix) further web-enable the platform for automated integration with CI servers."
    )

    # SCREENSHOT 9: BUILD HISTORY
    add_figure(
        "fig02_build_history.png",
        "Figure 16.1",
        "SCREENSHOT 9: WEB APPLICATION — CI/CD BUILD HISTORY & FAILURE MATRIX",
        "Figure 16.1 illustrates the CI/CD Build History interface. The view details historical pipeline executions across main, develop, and feature branches, displaying commit SHAs, author badges, execution durations, test pass/fail counts, and direct links to automated failure attribution cards."
    )

    # =========================================================================
    # SECTION 17 — RESULTS, TESTING, AND DEMONSTRATION
    # =========================================================================
    add_h1("Section 17 — Results, Testing, and Demonstration")
    add_p(
        "CommitSleuth has been rigorously validated through automated unit test suites, integration test suites, client-side git hook verifications, and interactive failure/fix demonstration sequences. Across all test executions, the platform achieved a 100% pass rate (20/20 Java JUnit 5 tests passed, 22/22 Python pytest tests passed)."
    )

    add_h2("17.1 Automated Test Execution Results Matrix")
    add_p(
        "The following test-case table documents the verified execution results for core system modules, failure detection heuristics, promotional quality gates, and configuration auditing criteria:"
    )

    test_cases_data = [
        ("TC-001", "Git Version Control", "Commit message validation with CR prefix", "Commit accepted if 'CR-xxx:' present", "Commit accepted successfully", "Passed", "git_02_commit_history.png"),
        ("TC-002", "Git Version Control", "Commit message rejection without CR prefix", "Commit blocked by hooks/commit-msg", "Blocked with non-zero exit code", "Passed", "hooks/commit-msg"),
        ("TC-003", "CI/CD Pipeline", "Execute clean Maven compilation and test suite", "All 20 Java unit tests pass", "20/20 tests passed in 4.42s", "Passed", "mvn -B test output"),
        ("TC-004", "Fault Injection", "Inject intentional defect in Calculator add method", "JUnit assertion fails on Build #128", "AssertionFailedError recorded", "Passed", "fig04_failure_attribution.png"),
        ("TC-005", "Log Ingestion", "Parse Surefire test log for error signature", "Extracts failing class & line number", "Parsed CalculatorTest & assertion", "Passed", "tests/test_log_parser.py"),
        ("TC-006", "Blame Attribution", "Compute attribution scores for Build #128", "Attributes blame to commit 9297e33", "88.5% confidence score calculated", "Passed", "tests/test_scorer.py"),
        ("TC-007", "Problem Tracking", "Auto-create defect record for broken build", "Problem BUG-024 created in Open status", "BUG-024 recorded in SQLite DB", "Passed", "fig03_problem_tracking.png"),
        ("TC-008", "Developer Alerts", "Dispatch real-time notification to commit author", "Alert ALT-001 generated with unread badge", "Alert displayed on web portal", "Passed", "fig01_dashboard.png"),
        ("TC-009", "Change Management", "Submit and record formal Change Request", "CR-009 registered with affected CIs", "CR-009 logged in change register", "Passed", "fig05_change_management.png"),
        ("TC-010", "Bugfix Verification", "Apply fix commit e789c77 and re-run build", "Build #129 passes; BUG-024 resolved", "Build #129 SUCCESS; BUG-024 closed", "Passed", "fig02_build_history.png"),
        ("TC-011", "Promotion Gate", "Evaluate promotion gate on failing Build #128", "Promotion gate BLOCKED", "BLOCKED with logged rationale", "Passed", "tests/test_promote.py"),
        ("TC-012", "Promotion Gate", "Evaluate promotion gate on passing Build #129", "Promotion gate PASSED", "PASSED; promoted to Production", "Passed", "fig08_promotions.png"),
        ("TC-013", "System Accounting", "Generate CSAR report and CSV export", "CSAR generated with 20 CIs and metrics", "CSAR report & CSV exported", "Passed", "fig10_csar_report.png"),
        ("TC-014", "CAS Auditing", "Perform Functional Configuration Audit (FCA)", "14 Functional Requirements verified", "100% FCA compliance recorded", "Passed", "fig09_auditing_fca_pca.png"),
        ("TC-015", "CAS Auditing", "Perform Physical Configuration Audit (PCA)", "SHA-256 release checksums verified", "PCA baseline match confirmed", "Passed", "release-manifest.json"),
        ("TC-016", "Access Security", "Verify RBAC permission restrictions", "Viewer denied CR creation and promotion", "HTTP 403 Forbidden enforced", "Passed", "tests/test_dashboard.py"),
        ("TC-017", "Customization", "Update scoring weights via YAML configuration", "Weights updated dynamically without restart", "Updated weights applied to engine", "Passed", "fig11_customization_config.png"),
    ]

    t_cases = doc.add_table(rows=len(test_cases_data)+1, cols=7)
    t_cases.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_cases, color="B4C6E7", sz="4")

    tc_hdrs = ["Test ID", "Module", "Test Scenario", "Expected Result", "Actual Result", "Status", "Evidence"]
    tc_widths = [Inches(0.8), Inches(1.1), Inches(1.4), Inches(1.3), Inches(1.3), Inches(0.7), Inches(1.1)]

    for i, h in enumerate(tc_hdrs):
        cell = t_cases.cell(0, i)
        cell.width = tc_widths[i]
        set_cell_margins(cell, 60, 60, 70, 70)
        set_cell_background(cell, "D9E1F2")
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.font.name = "Times New Roman"
        r.font.size = Pt(9.5)
        r.font.bold = True

    for r_idx, row in enumerate(test_cases_data):
        for c_idx, val in enumerate(row):
            cell = t_cases.cell(r_idx+1, c_idx)
            cell.width = tc_widths[c_idx]
            set_cell_margins(cell, 40, 40, 70, 70)
            set_cell_background(cell, "F8FAFC" if r_idx % 2 == 1 else "FFFFFF")
            p = cell.paragraphs[0]
            p.paragraph_format.line_spacing = 1.15
            r = p.add_run(val)
            r.font.name = "Times New Roman"
            r.font.size = Pt(9)
            if c_idx == 0:
                r.font.bold = True
            elif c_idx == 5:
                r.font.bold = True
                r.font.color.rgb = RGBColor(22, 101, 52) # Dark green for Passed

    add_p("", space_after=6)

    add_h2("17.2 Final Tool Demonstration Walkthrough Sequence")
    add_p(
        "The live demonstration sequence conducted for the Final Tool Evaluation proceeds as follows:\n"
        "1. Repository & Branch Inspection: The evaluator inspects the GitHub repository (prakashumapathi07-spec/COMMITSLEUTHSCM), verifying the 5 active branches, release tags, and client-side commit-msg hook.\n"
        "2. Launching Web Portal: The Flask application is started on port 5000; the dashboard loads displaying 77.8% build health and 0 open defects.\n"
        "3. Simulating Failure (Build #128): In the sidebar, the presenter clicks '1. Karthik Defect (#128)' (or calls /api/demo/run-failure). Jenkins executes Maven test, failing on CalculatorTest. CommitSleuth parses the log, calculates 88.5% confidence against commit 9297e33, opens BUG-024, and dispatches Alert ALT-001.\n"
        "4. Developer Diagnostic View: The presenter navigates to /failures/128, demonstrating the syntax-colored terminal log, root-cause card, and suggested code fix.\n"
        "5. Corrective Action & Verification (Build #129): The presenter clicks '2. Karthik Fix (#129)' (or calls /api/demo/run-fix). Corrective commit e789c77 is recorded. Build #129 succeeds with 20/20 green tests. BUG-024 automatically transitions to Resolved.\n"
        "6. Promotional Gate Clearance: The promotional management page demonstrates that Build #128 was strictly BLOCKED, while Build #129 PASSED and was promoted to Baseline BL-05 (Production Release v1.0.0).\n"
        "7. CSAR Export & Audit Sign-Off: A Configuration Status Accounting Report is generated and exported to CSV, confirming complete traceability."
    )

    # =========================================================================
    # SECTION 18 — CONCLUSION AND FUTURE ENHANCEMENTS
    # =========================================================================
    add_h1("Section 18 — Conclusion and Future Enhancements")
    add_p(
        "CommitSleuth successfully demonstrates how Software Configuration Management principles, combined with automated continuous integration tooling, can resolve the batching problem in modern software engineering. By continuously monitoring Jenkins pipeline events, parsing Maven test outputs, ranking multi-developer candidate commits through explainable heuristics, and providing interactive root-cause diagnostics, CommitSleuth eliminates the naive 'blame the latest commit' heuristic and drastically reduces Mean Time to Resolution (MTTR)."
    )
    add_p(
        "Throughout this project, Git and GitHub have proven indispensable as the foundational version control and configuration management infrastructure. Git provides rock-solid commit history, cryptographic SHA-1/SHA-256 change tracking, branch isolation, and client-side hook validation. GitHub extends these capabilities with remote team collaboration, pull request review workflows, automated webhook dispatching, and semantic release tagging. Across all ten evaluated SCM activities—from Tool Implementation and Baseline Versioning to Change Control, Problem Tracking, Promotional Quality Gates, Configuration Auditing, Access Security, Customization, and Web Enabling—CommitSleuth exemplifies an end-to-end, auditable, and resilient SCM platform."
    )
    
    add_h2("18.1 SCM Implementation Maturity Summary")
    add_p(
        "• Fully Implemented: Version Management (Git branches, commits, tags), Change Management (CR-001..CR-016), Problem Tracking (BUG-024 lifecycle), Promotional Management (staged quality gates), System Accounting (20 CIs & CSAR), Configuration Auditing (FCA/PCA), Access & Security (RBAC & audit trail), Customization (YAML scoring weights), and Web Enabling (Flask portal).\n"
        "• Partially Implemented / Simulated: Full enterprise webhook integration with Jenkins (simulated via REST endpoints and live Maven Surefire execution).\n"
        "• Future Enhancements: Integration with distributed messaging services (Slack, Microsoft Teams), AI-driven NLP log summarization, and automated rollback pull request generation via GitHub API."
    )

    # =========================================================================
    # SECTION 19 — REFERENCES
    # =========================================================================
    add_h1("Section 19 — References")
    references = [
        "1. IEEE Std 828-2012, 'IEEE Standard for Configuration Management in Systems and Software Engineering', IEEE Computer Society, 2012.",
        "2. Chacon, S., & Straub, B., 'Pro Git: Everything you need to know about Git', 2nd Edition, Apress, 2014. Available: https://git-scm.com/book/en/v2",
        "3. GitHub Documentation, 'About pull requests and protected branches', GitHub Docs, 2026. Available: https://docs.github.com/en/pull-requests",
        "4. Apache Maven Project, 'Maven Surefire Plugin — Running Unit Tests', Apache Software Foundation, 2024. Available: https://maven.apache.org/surefire/maven-surefire-plugin/",
        "5. Smart, J. F., 'Jenkins: The Definitive Guide', O'Reilly Media, 2011. Available: https://www.jenkins.io/doc/",
        "6. Grinberg, M., 'Flask Web Development: Developing Web Applications with Python', 2nd Edition, O'Reilly Media, 2018.",
        "7. JUnit Team, 'JUnit 5 User Guide', 2024. Available: https://junit.org/junit5/docs/current/user-guide/",
        "8. CommitSleuth Project Repository & SCM Documentation: https://github.com/prakashumapathi07-spec/COMMITSLEUTHSCM.git"
    ]
    for ref in references:
        add_p(ref, space_after=4)

    # =========================================================================
    # SAVE DOCUMENT
    # =========================================================================
    out_dir_final = os.path.join(ROOT, "docs", "final-review")
    os.makedirs(out_dir_final, exist_ok=True)
    out_path_1 = os.path.join(out_dir_final, "CommitSleuth_SCM_Final_Review_Documentation.docx")
    out_path_2 = os.path.join(ROOT, "docs", "CommitSleuth_SCM_Final_Review_Documentation.docx")

    doc.save(out_path_1)
    print(f"Documentation successfully created at:\n  1. {out_path_1}")

    try:
        doc.save(out_path_2)
        print(f"  2. {out_path_2}")
    except PermissionError:
        alt_path = os.path.join(ROOT, "docs", "CommitSleuth_SCM_Final_Review_Documentation_Copy.docx")
        try:
            doc.save(alt_path)
            print(f"  2. [Notice: {out_path_2} locked; saved copy to {alt_path}]")
        except Exception:
            pass

if __name__ == "__main__":
    generate_documentation_docx()
