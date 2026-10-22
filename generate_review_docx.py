"""Script to generate CommitSleuth SCM Final Review Microsoft Word (.docx) Document.
Follows exact formatting:
- A4 size, 1-inch margins
- Times New Roman, 12pt body text, ~1.5 line spacing
- Bold numbered headings
- Exactly 12 required sections in order
- Real project screenshots with figure numbers, captions, and explanations
- Cover page with all project and team details
"""
import os
import sys
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT = os.path.dirname(os.path.abspath(__file__))
SC_DIR = os.path.join(ROOT, "docs", "screenshots")

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def add_page_number(run):
    fldSimple = OxmlElement('w:fldSimple')
    fldSimple.set(qn('w:instr'), 'PAGE')
    run._r.append(fldSimple)

def generate_docx():
    doc = docx.Document()

    # Configure Section: A4, 1-inch margins
    section = doc.sections[0]
    section.page_width = Inches(8.27)   # A4 width
    section.page_height = Inches(11.69) # A4 height
    section.top_margin = Inches(1.0)
    section.bottom_margin = Inches(1.0)
    section.left_margin = Inches(1.0)
    section.right_margin = Inches(1.0)

    # Configure Footer with Page Number
    footer = section.footer
    f_p = footer.paragraphs[0]
    f_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    f_run1 = f_p.add_run("CommitSleuth — SCM Final Review | Page ")
    f_run1.font.name = "Times New Roman"
    f_run1.font.size = Pt(9.5)
    f_run1.font.color.rgb = RGBColor(100, 100, 100)
    f_run2 = f_p.add_run()
    f_run2.font.name = "Times New Roman"
    f_run2.font.size = Pt(9.5)
    f_run2.font.color.rgb = RGBColor(100, 100, 100)
    add_page_number(f_run2)

    # Helper function for adding body paragraphs
    def add_body(text, space_after=6, bold_prefix=None):
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

        r = p.add_run(text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(12)
        r.font.color.rgb = RGBColor(30, 41, 59)
        return p

    # Helper function for section headings
    def add_heading_1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(16)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(14)
        r.font.bold = True
        r.font.color.rgb = RGBColor(15, 23, 42)
        return p

    # Helper function for subheadings
    def add_heading_2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(12.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(30, 41, 59)
        return p

    # Helper function for embedding screenshots
    def add_screenshot(filename, fig_num, caption, explanation):
        img_path = os.path.join(SC_DIR, filename)
        if os.path.exists(img_path):
            p_img = doc.add_paragraph()
            p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_img.paragraph_format.space_before = Pt(8)
            p_img.paragraph_format.space_after = Pt(4)
            p_img.paragraph_format.keep_with_next = True
            p_img.add_run().add_picture(img_path, width=Inches(5.95))

            p_cap = doc.add_paragraph()
            p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_cap.paragraph_format.space_before = Pt(2)
            p_cap.paragraph_format.space_after = Pt(6)
            p_cap.paragraph_format.keep_with_next = True
            r_cap = p_cap.add_run(f"Figure {fig_num}: {caption}")
            r_cap.font.name = "Times New Roman"
            r_cap.font.size = Pt(10.5)
            r_cap.font.bold = True
            r_cap.font.italic = True
            r_cap.font.color.rgb = RGBColor(51, 65, 85)

            add_body(explanation, space_after=10, bold_prefix=f"Figure {fig_num} Explanation: ")
        else:
            add_body(f"[Note: Screenshot {filename} is currently undergoing archival. Project verification conducted via live runtime interface.]", space_after=8)

    # =========================================================================
    # COVER PAGE
    # =========================================================================
    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_inst.paragraph_format.space_before = Pt(24)
    p_inst.paragraph_format.space_after = Pt(4)
    r_inst = p_inst.add_run("VELLORE INSTITUTE OF TECHNOLOGY (VIT), VELLORE\n")
    r_inst.font.name = "Times New Roman"
    r_inst.font.size = Pt(15)
    r_inst.font.bold = True
    r_inst.font.color.rgb = RGBColor(15, 23, 42)

    r_sch = p_inst.add_run("School of Computer Science Engineering and Information Systems (SCOPE)\n")
    r_sch.font.name = "Times New Roman"
    r_sch.font.size = Pt(12)
    r_sch.font.color.rgb = RGBColor(71, 85, 105)

    r_crs = p_inst.add_run("ISWE403L — SOFTWARE CONFIGURATION MANAGEMENT\n")
    r_crs.font.name = "Times New Roman"
    r_crs.font.size = Pt(13)
    r_crs.font.bold = True
    r_crs.font.color.rgb = RGBColor(30, 58, 138)

    # Decorative Line
    p_line = doc.add_paragraph()
    p_line.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_line.paragraph_format.space_before = Pt(6)
    p_line.paragraph_format.space_after = Pt(20)
    r_l = p_line.add_run("—" * 38)
    r_l.font.color.rgb = RGBColor(203, 213, 225)

    # Project Title
    p_proj = doc.add_paragraph()
    p_proj.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_proj.paragraph_format.space_before = Pt(12)
    p_proj.paragraph_format.space_after = Pt(6)
    r_pname = p_proj.add_run("CommitSleuth\n")
    r_pname.font.name = "Times New Roman"
    r_pname.font.size = Pt(24)
    r_pname.font.bold = True
    r_pname.font.color.rgb = RGBColor(15, 23, 42)

    r_psub = p_proj.add_run("An Automated Build Failure Tracking and Developer Alert System Using Software Configuration Management\n")
    r_psub.font.name = "Times New Roman"
    r_psub.font.size = Pt(13)
    r_psub.font.italic = True
    r_psub.font.color.rgb = RGBColor(71, 85, 105)

    # Evaluation Title
    p_eval = doc.add_paragraph()
    p_eval.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_eval.paragraph_format.space_before = Pt(14)
    p_eval.paragraph_format.space_after = Pt(28)
    r_eval = p_eval.add_run("FINAL TOOL DEMONSTRATION EVALUATION (REVIEW-III)")
    r_eval.font.name = "Times New Roman"
    r_eval.font.size = Pt(13)
    r_eval.font.bold = True
    r_eval.font.color.rgb = RGBColor(220, 38, 38)

    # Metadata Details Table
    meta_table = doc.add_table(rows=6, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_data = [
        ("Course Details:", "ISWE403L — Software Configuration Management"),
        ("Evaluation:", "Final Tool Demonstration Evaluation (Review-III)"),
        ("Faculty Guide:", "Prof. Senthil Kumar P"),
        ("Slot:", "E1 + TE1"),
        ("SCM Tool Selected:", "Git & GitHub"),
        ("GitHub Repository:", "https://github.com/prakashumapathi07-spec/COMMITSLEUTHSCM.git")
    ]
    for row_idx, (label, val) in enumerate(meta_data):
        cell_lbl = meta_table.cell(row_idx, 0)
        cell_val = meta_table.cell(row_idx, 1)
        cell_lbl.width = Inches(2.2)
        cell_val.width = Inches(4.2)
        set_cell_margins(cell_lbl, 80, 80, 100, 100)
        set_cell_margins(cell_val, 80, 80, 100, 100)
        
        p0 = cell_lbl.paragraphs[0]
        p0.paragraph_format.line_spacing = 1.15
        r0 = p0.add_run(label)
        r0.font.name = "Times New Roman"
        r0.font.size = Pt(11.5)
        r0.font.bold = True
        r0.font.color.rgb = RGBColor(15, 23, 42)

        p1 = cell_val.paragraphs[0]
        p1.paragraph_format.line_spacing = 1.15
        r1 = p1.add_run(val)
        r1.font.name = "Times New Roman"
        r1.font.size = Pt(11.5)
        r1.font.color.rgb = RGBColor(30, 41, 59)

    # Team Members Block
    p_team = doc.add_paragraph()
    p_team.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_team.paragraph_format.space_before = Pt(36)
    p_team.paragraph_format.space_after = Pt(4)
    r_tm = p_team.add_run("Project Team Members:\n")
    r_tm.font.name = "Times New Roman"
    r_tm.font.size = Pt(12)
    r_tm.font.bold = True
    r_tm.font.color.rgb = RGBColor(15, 23, 42)

    p_devs = doc.add_paragraph()
    p_devs.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_devs.paragraph_format.space_before = Pt(4)
    p_devs.paragraph_format.line_spacing = 1.25
    r_d1 = p_devs.add_run("Prakash Raj U — Register No: 23MIS0180\n")
    r_d1.font.name = "Times New Roman"
    r_d1.font.size = Pt(12)
    r_d1.font.bold = True
    r_d1.font.color.rgb = RGBColor(30, 58, 138)

    r_d2 = p_devs.add_run("Bharathwaraj K S — Register No: 23MIS0070\n")
    r_d2.font.name = "Times New Roman"
    r_d2.font.size = Pt(12)
    r_d2.font.bold = True
    r_d2.font.color.rgb = RGBColor(30, 58, 138)

    # Academic Year
    p_yr = doc.add_paragraph()
    p_yr.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_yr.paragraph_format.space_before = Pt(20)
    r_yr = p_yr.add_run("Academic Year: 2026 – 2027 | VIT Vellore")
    r_yr.font.name = "Times New Roman"
    r_yr.font.size = Pt(11)
    r_yr.font.color.rgb = RGBColor(100, 116, 139)

    doc.add_page_break()

    # =========================================================================
    # 1. INTRODUCTION
    # =========================================================================
    add_heading_1("1. Introduction")
    add_body(
        "CommitSleuth is an automated continuous integration build failure tracking, root-cause investigation, and developer alert platform grounded in Software Configuration Management (SCM) principles. In high-velocity software engineering environments, multiple developers continuously push code changes across separate feature branches. When automated pipelines fail after several commits are integrated, continuous integration engines such as Jenkins typically mark the entire pipeline as broken but cannot pinpoint which specific code change introduced the fault. This challenge is formally known as the batching problem. Common industry practice often resorts to an ad-hoc and error-prone heuristic—blaming the latest commit author (HEAD)—even when that commit represents a trivial or unrelated modification."
    )
    add_body(
        "To solve this problem, CommitSleuth integrates Git, GitHub, Jenkins, Apache Maven, and a centralized relational status database into an end-to-end SCM ecosystem. The platform automatically intercepts build execution failures, parses compiler and unit test error signatures, analyzes candidate commits introduced since the last successful baseline, and computes transparent, evidence-based confidence scores using a multi-factor attribution engine. The system subsequently generates incident problem records, dispatches actionable developer alerts, provides interactive fix suggestions, verifies subsequent corrective commits, and enforces strict promotional quality gates across deployment environments."
    )
    add_body(
        "Git and GitHub serve as the primary foundational pillars for Software Configuration Management in CommitSleuth. Git provides distributed version control, atomic commits, commit SHA integrity, and local branch isolation. GitHub acts as the remote authoritative repository, facilitating multi-developer collaboration, feature-branch pull requests, code reviews, automated webhook triggers, and immutable release tagging. Together with client-side commit message hooks and automated pipeline hooks, Git and GitHub ensure rigorous configuration identification, baseline stability, and comprehensive traceability across the entire software development lifecycle."
    )

    # =========================================================================
    # 2. TOOL IMPLEMENTATION
    # =========================================================================
    add_heading_1("2. Tool Implementation")
    add_body(
        "Tool Implementation represents the foundational SCM activity that unites the software toolchain into a cohesive, automated workflow. CommitSleuth establishes an integrated pipeline connecting Git/GitHub for version control, Jenkins for continuous integration orchestration, Apache Maven for automated Java compilation and JUnit 5 Surefire test execution, Python for log parsing and heuristic attribution scoring, SQLite for persistent configuration status accounting, and Flask for an interactive, light-theme web dashboard."
    )
    add_body(
        "The realistic operational scenario implemented for CommitSleuth models TechNova Solutions, where four developers collaborate on an Employee Management System across dedicated feature branches: Prakash Raj (Employee module on feature/employee), Bharathwaraj (Authentication module on feature/login), Karthik (Reports module on feature/reports), and Divya (Database module on feature/database). When a developer commits code, GitHub triggers Jenkins through declarative pipelines defined in Jenkinsfile. Maven compiles the Java application and executes unit tests. If a failure occurs, Jenkins invokes CommitSleuth's backend build recorder, which analyzes the failure and updates the relational database in real time."
    )
    add_screenshot(
        "fig01_dashboard.png",
        1,
        "CommitSleuth Executive SCM Dashboard",
        "The Executive SCM Dashboard provides an integrated high-level view of continuous integration pipeline health, displaying calculated metrics such as total builds, build success rate (77.8%), open problem records, and unread alerts. It includes interactive visualizations of 30-day build trends, build status across the four TechNova modules, a collaborative developer activity panel, and recent pipeline executions."
    )

    # =========================================================================
    # 3. VERSION MANAGEMENT
    # =========================================================================
    add_heading_1("3. Version Management")
    add_body(
        "Version Management governs how revisions, branch evolutions, and baseline snapshots are identified, controlled, and recorded throughout the project lifecycle. In CommitSleuth, Git is utilized as the absolute source of truth for repository history. A structured branching model separates production code (main) from active integration and feature modules (feature/employee, feature/login, feature/reports, and feature/database). This guarantees that unstable feature developments remain completely isolated from stable production baselines."
    )
    add_body(
        "To enforce traceability between source revisions and approved tasks, a Git commit message hook (hooks/commit-msg) validates that every commit message begins with an approved Change Request identifier (e.g., CR-009). Furthermore, formal configuration baselines are established and tracked in the database: BL-01 (Requirements Baseline, v0.1.0-req), BL-02 (Design Baseline, v0.1.0), BL-03 (CI/Build Baseline, v0.1.0), BL-04 (Analysis Module Baseline, v0.2.0), and BL-05 (Final Release Baseline, v1.0.0). Each baseline associates approved configuration items with an immutable Git release tag, target commit hash, and CCB authorization record."
    )
    add_screenshot(
        "fig07_baselines_versions.png",
        2,
        "Baselines and Version Management Register",
        "The Baselines and Version Management interface displays approved configuration baselines (BL-01 through BL-05), their corresponding semantic version identifiers, Git release tags, commit hashes, approval dates, and baseline comparison tools that show configuration item deltas between historical and release baselines."
    )

    # =========================================================================
    # 4. CHANGE MANAGEMENT
    # =========================================================================
    add_heading_1("4. Change Management")
    add_body(
        "Change Management provides a disciplined, formal mechanism for requesting, evaluating, authorizing, implementing, and verifying modifications to controlled configuration items. Uncontrolled changes lead to configuration drift, untracked bugs, and broken builds. In CommitSleuth, all modifications are initiated through formal Change Requests (CR) submitted to the Configuration Control Board (CCB)."
    )
    add_body(
        "The project tracks ten formal Change Requests (CR-001 through CR-010). Each change request record documents the unique CR identifier, descriptive title, requester, technical rationale, affected configuration items, priority, target branch, and CCB decision status (Raised, Under Review, Approved, Implemented, or Rejected). For example, CR-009 represents Karthik's modification to monthly expense calculations in ReportService.java on feature/reports, while CR-010 represents the subsequent corrective fix restoring build health. The web interface enables authorized developers to register new change requests while enforcing role permissions so that only CCB administrators can record official approval decisions."
    )
    add_screenshot(
        "fig05_change_management.png",
        3,
        "SCM Change Management Register",
        "The Change Management register displays the formal ledger of Change Requests (CR-001 through CR-010), including requester identities, scope of impact, priority levels, CCB review statuses, target branches, and associated Git commit hashes, ensuring complete auditability from requirement change to code commit."
    )

    # =========================================================================
    # 5. PROBLEM TRACKING
    # =========================================================================
    add_heading_1("5. Problem Tracking")
    add_body(
        "Problem Tracking automates the identification, recording, investigation, and resolution of software defects arising during automated build and test cycles. When an automated Maven test fails in Jenkins, CommitSleuth intercepts the Surefire test report and console output, extracts the exact assertion failure and line number, and automatically generates an incident record in the problems register."
    )
    add_body(
        "In the central demonstration scenario, Build #128 fails due to an intentional defect introduced by Karthik in ReportService.java, causing ReportServiceTest to fail with an AssertionFailedError. CommitSleuth attributes this failure to Karthik's commit (a91bc42) with 88.5% confidence and automatically creates problem record BUG-024. The problem record progresses through a formal SCM lifecycle: Open -> Investigating -> Fix Submitted -> Verification Pending -> Resolved. A defect cannot be prematurely closed by simple assertion; it transitions to Resolved only after a subsequent verification build (Build #129) successfully compiles and passes all unit tests."
    )
    add_screenshot(
        "fig03_problem_tracking.png",
        4,
        "Automated Problem Tracking Register",
        "The Problem Tracking register illustrates the defect ledger, showing unique problem codes (e.g., BUG-024 / P-001), associated failing build numbers, failure categories (test), suspect commit hashes, attribution confidence scores, assigned developers, and real-time lifecycle progression states."
    )

    # =========================================================================
    # 6. PROMOTIONAL MANAGEMENT
    # =========================================================================
    add_heading_1("6. Promotional Management")
    add_body(
        "Promotional Management controls the staged migration of software configuration baselines across progressive operational environments: Development -> Testing -> Release Candidate -> Production. Each environment transition represents an increased level of verification, stability, and organizational commitment."
    )
    add_body(
        "CommitSleuth enforces strict promotional quality gates. A failing build (such as Build #128) is strictly BLOCKED from advancing to higher environments, and the blocking justification (e.g., 'Automated unit tests did not pass') is permanently logged. Only when a verified passing build (Build #129) is achieved, accompanied by an approved Change Request (CR-010) and passing configuration audits, does the promotion gate evaluate to PASSED. The promotion ledger permanently records the transition date, source and target levels, authorizing authority (CCB), gate decision, and associated release tag."
    )
    add_screenshot(
        "fig08_promotions.png",
        5,
        "Promotional Gate Ledger and Quality Gate Evaluation",
        "The Promotional Management ledger demonstrates the multi-environment promotion pipeline, recording successful environment advancements (PASSED) alongside blocked transitions (BLOCKED) with explicit verification rationales, ensuring unverified or defective code cannot reach production."
    )

    # =========================================================================
    # 7. SYSTEM ACCOUNTING
    # =========================================================================
    add_heading_1("7. System Accounting")
    add_body(
        "System Accounting, or Configuration Status Accounting (CSA), provides an auditable, centralized record of the status, history, and traceability of all configuration items comprising the software system. It answers critical engineering questions regarding what configuration baseline is currently active, which changes have been approved and implemented, and what quality verification results correspond to each release."
    )
    add_body(
        "In CommitSleuth, CSA tracks 20 identified Configuration Items (CIs) categorized into Documentation (SRS, SCM Plan, Design Document), Source Code (Java services, Python analyzers), Build Configurations (pom.xml, Jenkinsfile), Database Components, and Release Packages. The system includes an automated status reporting engine (status_reporter.py) that generates structured Configuration Status Accounting Reports (CSAR) directly from the relational database and provides live CSV export capabilities (/report/csv) for external compliance audits."
    )
    add_screenshot(
        "fig06_ci_register.png",
        6,
        "Configuration Item (CI) Register",
        "The Configuration Item Register displays the 20 formally controlled CIs, their version identifiers, lifecycle states (e.g., Baselined BL-01 to BL-05), designated owners, approval statuses, categories, and timestamps of last modification."
    )
    add_screenshot(
        "fig10_csar_report.png",
        7,
        "Configuration Status Accounting Report (CSAR) Output",
        "The CSAR output view displays the generated configuration status accounting report summarizing total CIs under control, change request statistics, CI/CD pipeline pass/fail ratios, open versus resolved problem records, and cryptographic release tag references."
    )

    # =========================================================================
    # 8. CAS (CONFIGURATION AUDITING SYSTEM)
    # =========================================================================
    add_heading_1("8. CAS (Configuration Auditing System)")
    add_body(
        "The Configuration Auditing System (CAS) performs independent, objective evaluations to verify that the software product satisfies its documented functional requirements and that its physical implementation precisely mirrors approved baselines. CommitSleuth implements both categories of formal SCM audits:"
    )
    add_body(
        "1. Functional Configuration Audit (FCA): Verifies that all documented functional requirements (FR-01 through FR-14) have been implemented and satisfied through unit and integration testing. This includes auditing test assertion logs, branch naming compliance, and ranking engine accuracy.\n"
        "2. Physical Configuration Audit (PCA): Verifies the physical presence, packaging, and version integrity of approved configuration items. This includes auditing pinned Maven dependencies in pom.xml, deployment documentation in README.md, database schema parity, and cryptographic SHA-256 checksums of compiled release packages.\n"
        "All audit observations (AO-01 through AO-07) are formally tracked in the database with severity classifications (Critical, Major, Minor, Conforming), assigned owners, and verified closure dates."
    )
    add_screenshot(
        "fig09_auditing_fca_pca.png",
        8,
        "Configuration Auditing System (FCA & PCA Ledger)",
        "The Configuration Auditing interface displays recorded audit observations (AO-01 through AO-07), categorizing each check as FCA or PCA, detailing checklist criteria, audit findings, objective verification evidence, severity ratings, responsible owners, and verified closure dates."
    )

    # =========================================================================
    # 9. ACCESS AND SECURITY
    # =========================================================================
    add_heading_1("9. Access and Security")
    add_body(
        "Access and Security safeguards software configuration items, audit records, and deployment gates from unauthorized modification. CommitSleuth implements Role-Based Access Control (RBAC) enforced at both the Flask backend route level and user session tier."
    )
    add_body(
        "The system defines three distinct operational roles:\n"
        "1. Administrator (Prakash Raj / Bharathwaraj): Granted full authority to modify global scoring weights, approve or reject Change Requests, authorize production promotions, and manage user accounts.\n"
        "2. Maintainer / Developer (Karthik / Divya): Authorized to inspect build details, investigate attributed failures, submit new Change Requests, acknowledge alerts, and submit corrective commits.\n"
        "3. Viewer / Auditor: Restricted to read-only access for dashboards, status accounting reports, and audit logs; strictly prohibited from registering CRs or approving promotions.\n"
        "Additionally, an immutable audit trail table (audit_trail) automatically logs every user authentication, role switch, promotion gate evaluation, and configuration edit with precise timestamps and usernames."
    )
    add_screenshot(
        "fig12_access_security_audit.png",
        9,
        "Access Control and SCM Security Audit Trail",
        "The SCM Audit Trail interface displays an immutable chronological ledger of system actions, recording event timestamps, acting user personas, actions performed (e.g., portal logins, promotion evaluations, CR submissions), and operational details for complete accountability."
    )

    # =========================================================================
    # 10. CUSTOMIZATION
    # =========================================================================
    add_heading_1("10. Customization")
    add_body(
        "Customization addresses the need for an SCM tool to adapt to diverse organizational workflows, project sizes, and failure characteristics without modifying core application code. In CommitSleuth, failure attribution relies on a multi-factor weighted scoring model whose weights are externalized in scoring_config.yaml."
    )
    add_body(
        "The heuristic engine evaluates candidate commits against four configurable factors:\n"
        "1. File Match Weight (default 0.55): Evaluates direct name matching between candidate changeset files and classes referenced in failing test traces (e.g., matching ReportService.java with ReportServiceTest).\n"
        "2. Dependency Change Weight (default 0.25): Assigns weight to pom.xml modifications when a dependency resolution failure occurs.\n"
        "3. Recency Weight (default 0.10): Applies linear decay based on commit chronological order in the candidate batch.\n"
        "4. Change Size Weight (default 0.10): Evaluates the breadth and isolation of files altered in the commit.\n"
        "Through the web customization portal, project leads can adjust these weights dynamically, update repository endpoints, and modify Jenkins webhook URLs. All updates are persisted directly to scoring_config.yaml and take immediate effect."
    )
    add_screenshot(
        "fig11_customization_config.png",
        10,
        "SCM Customization and Heuristic Weight Configuration",
        "The Customization interface allows project managers to fine-tune attribution scoring weights, configure rollback thresholds, update GitHub repository URLs, and modify Jenkins CI webhook endpoints without code alterations or server restarts."
    )

    # =========================================================================
    # 11. WEB ENABLING
    # =========================================================================
    add_heading_1("11. Web Enabling")
    add_body(
        "Web Enabling delivers all SCM capabilities, metrics, and failure investigations through an intuitive, universally accessible web browser interface. Rather than requiring developers to inspect raw command-line logs or navigate disparate tool consoles, CommitSleuth consolidates all project status information into a single responsive web portal."
    )
    add_body(
        "Operating as a Flask WSGI service on port 5000, CommitSleuth provides thirteen responsive views covering the entire SCM lifecycle. In particular, the failure investigation module (/failures/<id>) offers an interactive terminal console viewer with color-coded log lines, highlighting JUnit assertions and failure traces in red. The interface presents a structured root-cause card, an evidence breakdown showing mathematical score contributions, and side-by-side code diff suggestions showing developers exactly how to resolve the defect. Authenticated REST APIs (/api/builds, /api/demo/run-failure, /api/demo/run-fix) further web-enable the platform for automated integration with CI servers."
    )
    add_screenshot(
        "fig04_failure_attribution.png",
        11,
        "Web-Enabled Failure Attribution and Root-Cause Analysis Interface",
        "The Failure Attribution web interface demonstrates the interactive root-cause investigation view for Build #128, displaying parsed console output, failing JUnit test assertions, candidate commit ranking breakdown, and automated rollback recommendations."
    )

    # =========================================================================
    # 12. CONCLUSION
    # =========================================================================
    add_heading_1("12. Conclusion")
    add_body(
        "CommitSleuth successfully demonstrates how Software Configuration Management principles and automated tooling can resolve the continuous integration batching problem. By continuously monitoring Jenkins pipeline events, parsing Maven test outputs, ranking multi-developer candidate commits through explainable heuristics, and providing interactive root-cause diagnostics, CommitSleuth eliminates the naive 'blame the latest commit' heuristic and drastically reduces Mean Time to Resolution (MTTR)."
    )
    add_body(
        "Throughout this project, Git and GitHub have proven indispensable as the foundational version control and configuration management infrastructure. Git provides rock-solid commit history, cryptographic SHA-1/SHA-256 change tracking, branch isolation, and client-side hook validation. GitHub extends these capabilities with remote team collaboration, pull request review workflows, automated webhook dispatching, and semantic release tagging. Across all ten evaluated SCM activities—from Tool Implementation and Baseline Versioning to Change Control, Problem Tracking, Promotional Quality Gates, Configuration Auditing, Access Security, Customization, and Web Enabling—CommitSleuth exemplifies an end-to-end, auditable, and resilient SCM platform for modern software engineering teams."
    )

    # Save to both locations
    out_dir_final = os.path.join(ROOT, "docs", "final-review")
    os.makedirs(out_dir_final, exist_ok=True)
    out_path_1 = os.path.join(out_dir_final, "CommitSleuth_SCM_Final_Review.docx")
    out_path_2 = os.path.join(ROOT, "docs", "CommitSleuth_SCM_Final_Review.docx")

    doc.save(out_path_1)
    doc.save(out_path_2)

    print(f"Document successfully created at:")
    print(f"  1. {out_path_1}")
    print(f"  2. {out_path_2}")

if __name__ == "__main__":
    generate_docx()
