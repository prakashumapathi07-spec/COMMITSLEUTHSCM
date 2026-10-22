"""Database seed script for CommitSleuth.
Populates initial SCM data for TechNova Solutions — Employee Management System:
Developers (Prakash Raj, Bharathwaraj, Karthik, Divya),
20 Configuration Items, Change Requests CR-001..CR-010, Baselines BL-01..BL-05,
Audit observations AO-01..AO-07, historical builds, alerts, problems, and promotions.
Usage: python database/seed.py [--reset]
"""
import datetime
import hashlib
import os
import sys
from werkzeug.security import generate_password_hash

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "analyzer"))
import common
from common import connect, ROOT

def seed():
    if "--reset" in sys.argv and os.path.exists(common.DB):
        try:
            os.remove(common.DB)
            print("Removed existing database.")
        except Exception as e:
            print(f"Warning: could not remove DB file: {e}")

    con = connect()
    schema_sql = open(os.path.join(ROOT, "database", "schema.sql"), "r", encoding="utf-8").read()
    con.executescript(schema_sql)

    # 1. Users with RBAC (Admin, Maintainer, Viewer)
    users = [
        ("prakash", generate_password_hash("admin123"), "admin", "Prakash Raj U (23MIS0180)", "23mis0180@vitstudent.ac.in"),
        ("bharath", generate_password_hash("admin123"), "admin", "Bharathwaraj K S (23MIS0070)", "23mis0070@vitstudent.ac.in"),
        ("karthik", generate_password_hash("maint123"), "maintainer", "Karthik R (TechNova Reports)", "karthik@technova.com"),
        ("divya", generate_password_hash("maint123"), "maintainer", "Divya S (TechNova Database)", "divya@technova.com"),
        ("admin", generate_password_hash("admin123"), "admin", "Administrator", "admin@commitsleuth.org"),
        ("viewer", generate_password_hash("viewer123"), "viewer", "SCM Reviewer / Auditor", "reviewer@vit.ac.in")
    ]
    con.executemany("INSERT OR REPLACE INTO users VALUES (?,?,?,?,?)", users)

    # 2. Four TechNova Developers & Git Identities
    devs = [
        ("Prakash Raj", "prakash", "prakashraj-vit", "23mis0180@vitstudent.ac.in", "Team Lead / Developer", "Employee module", "feature/employee", "#2563eb", "2026-10-22 17:40"),
        ("Bharathwaraj", "bharath", "bharath-vit", "23mis0070@vitstudent.ac.in", "Senior Developer", "Authentication module", "feature/login", "#10b981", "2026-10-22 16:15"),
        ("Karthik", "karthik", "karthik-technova", "karthik@technova.com", "Developer", "Reports module", "feature/reports", "#f59e0b", "2026-10-22 18:05"),
        ("Divya", "divya", "divya-technova", "divya@technova.com", "Database Engineer", "Database module", "feature/database", "#8b5cf6", "2026-10-22 15:30")
    ]
    con.executemany("""
        INSERT OR REPLACE INTO developers (name, username, github_username, email, role, module, branch, avatar_color, last_commit_time)
        VALUES (?,?,?,?,?,?,?,?,?)
    """, devs)

    # 3. 20 Configuration Items (Review-1 & Review-2 Table 1 & Table 3)
    B, P = "Bharathwaraj K S", "Prakash Raj U"
    cis = [
        ("CSDOC01", "Project Proposal", "v1.0", "Baselined (BL-01)", B, "Approved", "BL-01", "Documentation", "2026-08-07"),
        ("CSDOC02", "Software Requirement Specification (SRS)", "v1.0", "Baselined (BL-01)", P, "Approved", "BL-01", "Documentation", "2026-08-12"),
        ("CSDOC03", "Software Configuration Management Plan", "v1.0", "Baselined (BL-01)", B, "Approved", "BL-01", "Documentation", "2026-08-14"),
        ("CSDOC04", "System Design Document", "v1.0", "Baselined (BL-02)", P, "Approved", "BL-02", "Documentation", "2026-09-04"),
        ("CSSRC01", "Source Code (Java & Python modules)", "v1.0.0", "Baselined (BL-04)", P, "Approved", "BL-04", "Source Code", "2026-10-22"),
        ("CSSRC02", "Git Repository", "v1.0.0", "Baselined (BL-02)", B, "Approved", "BL-02", "Repository", "2026-10-22"),
        ("CSBLD01", "Jenkinsfile (Declarative CI)", "v1.0", "Tested, Baselined (BL-03)", B, "Approved", "BL-03", "Build & CI", "2026-09-02"),
        ("CSBLD02", "Maven Configuration (pom.xml)", "v1.0", "Tested, Baselined (BL-03)", B, "Approved", "BL-03", "Build & CI", "2026-09-02"),
        ("CSMOD01", "Build Log Parser", "v1.0", "Baselined (BL-04)", B, "Approved", "BL-04", "Core Module", "2026-10-22"),
        ("CSMOD02", "pom.xml Diff Analyzer", "v1.0", "Baselined (BL-04)", P, "Approved", "BL-04", "Core Module", "2026-10-22"),
        ("CSMOD03", "Commit Ranking Engine", "v1.0", "Baselined (BL-04)", P, "Approved", "BL-04", "Core Module", "2026-10-22"),
        ("CSMOD04", "Notification & Alert Module", "v1.0", "Baselined (BL-04)", B, "Approved", "BL-04", "Core Module", "2026-10-22"),
        ("CSMOD05", "Rollback Recommendation Module", "v1.0", "Baselined (BL-04)", P, "Approved", "BL-04", "Core Module", "2026-10-22"),
        ("CSMOD06", "Dashboard Portal Module", "v1.0", "Baselined (BL-05)", P, "Approved", "BL-05", "Core Module", "2026-10-22"),
        ("CSDB01", "Database (SQLite SCM Status Repository)", "v1.0", "Baselined (BL-02)", P, "Approved", "BL-02", "Database", "2026-10-22"),
        ("CSDOC05", "Test Plan", "v1.0", "Baselined (BL-05)", B, "Approved", "BL-05", "Documentation", "2026-10-22"),
        ("CSDOC06", "Test Cases (JUnit & Pytest)", "v1.0", "Baselined (BL-05)", P, "Approved", "BL-05", "Documentation", "2026-10-22"),
        ("CSDOC07", "User Manual & API Guide", "v1.0", "Baselined (BL-05)", P, "Approved", "BL-05", "Documentation", "2026-10-22"),
        ("CSDOC08", "Deployment & Verification Guide", "v1.0", "Baselined (BL-05)", B, "Approved", "BL-05", "Documentation", "2026-10-22"),
        ("CSREL01", "Release Package (CommitSleuth_v1.0)", "v1.0.0", "Baselined (BL-05)", B, "Approved", "BL-05", "Release", "2026-10-22")
    ]
    con.executemany("INSERT OR REPLACE INTO ci_register VALUES (?,?,?,?,?,?,?,?,?)", cis)

    # 4. Change Requests (CR-001 through CR-010)
    crs = [
        ("CR-001", "SRS Batching Problem Specification", "Add batching-problem definition to SRS", B, "SRS Document", "High", "Critical requirement for batch commit triage", "Implemented", "Approved by CCB", "2026-08-12", "feature/srs-batching", "PR #1", "557c19c"),
        ("CR-002", "SRS Dependency & Isolation Requirements", "Add pom.xml diff and isolation requirements to SRS", P, "SRS Document", "High", "Rollback safety boundary definition", "Implemented", "Approved by CCB", "2026-08-12", "feature/srs-isolation", "PR #2", "52b2e16"),
        ("CR-003", "Jenkins Post-Failure Hook", "Add post-failure hook and artifact archiving to Jenkinsfile", B, "Jenkinsfile", "High", "Automated log retrieval on pipeline break", "Implemented", "Approved by CCB", "2026-09-02", "feature/jenkins-hook", "PR #3", "760667e"),
        ("CR-004", "Database Schema Extension", "Add change_requests and problems tables to database schema", P, "Database Schema", "High", "Persistent SCM status accounting", "Implemented", "Approved by CCB", "2026-09-03", "feature/db-schema", "PR #4", "725a755"),
        ("CR-005", "Surefire XML Parser Support", "Add XML report and test assertion parsing to Build Log Parser", B, "Build Log Parser", "Medium", "Enhanced extraction of failing JUnit test cases", "Implemented", "Approved by CCB", "2026-09-18", "feature/parser-xml", "PR #5", "760667e"),
        ("CR-006", "Configurable Scoring Weights", "Make scoring weights configurable via YAML file", P, "Ranking Engine", "Medium", "Dynamic weighting adaptation without code edits", "Implemented", "Approved by CCB", "2026-09-19", "feature/scoring-config", "PR #6", "99bbeb5"),
        ("CR-007", "Responsive Modern Dashboard Redesign", "Redesign dashboard layout with clean light-theme metrics and auditing", P, "Dashboard Module", "Medium", "Interactive SCM review demonstration", "Implemented", "Approved by CCB", "2026-10-21", "feature/dashboard-redesign", "PR #7", "f0ad7d0"),
        ("CR-008", "Replace Jenkins CI with Alternative Tool", "Replace Jenkins with external cloud CI server", B, "Jenkinsfile, Pipeline", "High", "Disruptive architecture change", "Rejected", "Rejected by CCB: Uncontrolled design drift", "2026-09-20", "", "", ""),
        ("CR-009", "Refactor Monthly Compensation Reports", "Update salary aggregation formulas in ReportService.java", "Karthik", "Reports Module", "High", "Seeded defect commit in CI pipeline causing test break", "Implemented", "Approved by CCB", "2026-10-22", "feature/reports", "PR #9", "a91bc42"),
        ("CR-010", "Resolve ReportService Defect & Restore Build", "Correct salary aggregation in ReportService.java and verify JUnit tests pass", "Karthik", "Reports Module", "High", "Fix seeded calculation defect in CI pipeline", "Implemented", "Approved by CCB", "2026-10-22", "feature/reports", "PR #10", "c48fe19")
    ]
    con.executemany("INSERT OR REPLACE INTO change_requests VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", crs)

    # 5. Baselines (BL-01 to BL-05)
    baselines = [
        ("BL-01", "Requirements Baseline", "v1.0", "v0.1.0-req", "557c19c", "Approved initial project proposal, SRS, and SCM plan", "2026-08-14", "Faculty Guide / CCB", "Approved"),
        ("BL-02", "Design & Repository Baseline", "v1.0", "v0.1.0", "557c19c", "System architecture, class diagrams, database schema v0.5, git repo", "2026-09-04", "Faculty Guide / CCB", "Approved"),
        ("BL-03", "CI / Build Baseline", "v1.0", "v0.1.0", "557c19c", "Jenkins declarative pipeline and Maven pom.xml configuration", "2026-09-04", "Faculty Guide / CCB", "Approved"),
        ("BL-04", "Analysis Module Baseline", "v0.2.0", "v0.2.0", "f0ad7d0", "Integrated log parser, commit ranking engine, scoring config YAML", "2026-09-25", "Faculty Guide / CCB", "Approved"),
        ("BL-05", "Final Release Baseline", "v1.0.0", "v1.0.0", "HEAD", "Complete SCM system with full 9 activities, dashboard, and verified demo app", "2026-10-22", "Faculty Guide / CCB", "Approved")
    ]
    con.executemany("INSERT OR REPLACE INTO baselines VALUES (?,?,?,?,?,?,?,?,?)", baselines)

    # 6. Historical Builds (Demonstrating four modules and central scenario)
    builds_data = [
        (121, "SUCCESS", "b110a2f", "feature/employee", "None", "All 20 tests passed", 38.5, None, "2026-10-22 09:15:00", "Prakash Raj", "Add department lookup in EmployeeService [CR-001]", "GitHub Push", "None", 20, 0, 20, "backend/employee-service"),
        (122, "SUCCESS", "c220b3a", "feature/login", "None", "All 20 tests passed", 42.1, None, "2026-10-22 10:20:00", "Bharathwaraj", "Implement session timeout verification [CR-002]", "GitHub Push", "None", 20, 0, 20, "backend/auth-service"),
        (123, "SUCCESS", "d330c4b", "feature/database", "None", "All 20 tests passed", 35.8, None, "2026-10-22 11:05:00", "Divya", "Connection pool health checks and validation [CR-004]", "GitHub Push", "None", 20, 0, 20, "backend/db-service"),
        (124, "SUCCESS", "e440d5c", "feature/reports", "None", "All 20 tests passed", 39.4, None, "2026-10-22 12:40:00", "Karthik", "Add initial compensation report structure [CR-005]", "GitHub Push", "None", 20, 0, 20, "backend/report-service"),
        (125, "UNSTABLE", "f550e6d", "feature/employee", "flaky-test", "Slow network response in ValidatorTest", 48.2, None, "2026-10-22 13:55:00", "Prakash Raj", "Update employee validation checks", "Jenkins Polling", "Unit Testing", 20, 0, 20, "backend/employee-service"),
        (126, "SUCCESS", "760667e", "main", "None", "All 20 tests passed", 36.0, None, "2026-10-22 14:30:00", "Bharathwaraj", "Baseline verification merge PR #3 [CR-003]", "Merge Webhook", "None", 20, 0, 20, "backend/main-pipeline"),
        (127, "SUCCESS", "f0ad7d0", "feature/reports", "None", "All 20 tests passed", 37.2, None, "2026-10-22 15:10:00", "Karthik", "Prepare monthly summary metrics [CR-007]", "GitHub Push", "None", 20, 0, 20, "backend/report-service"),
        (128, "FAILURE", "a91bc42", "feature/reports", "test", "ReportServiceTest.testCalculateMonthlyDepartmentExpenses - AssertionFailedError: expected <95000.0> but was <0.0>", 41.5, "build.log", "2026-10-22 16:30:00", "Karthik", "Refactor monthly compensation reports and aggregate formula [CR-009]", "GitHub Push", "Unit Testing & Test Report", 20, 2, 18, "backend/report-service"),
        (129, "SUCCESS", "c48fe19", "feature/reports", "None", "All 20 tests passed (100% green)", 36.8, None, "2026-10-22 17:15:00", "Karthik", "Fix salary aggregation formula in ReportService.java [CR-010]", "GitHub Push", "None", 20, 0, 20, "backend/report-service")
    ]
    con.executemany("""
        INSERT OR REPLACE INTO builds (
            build_no, result, commit_hash, branch, failure_type, test_summary, duration_sec, log_path, created,
            author, commit_message, trigger_type, failed_stage, tests_total, tests_failed, tests_passed, job_name
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, builds_data)

    # 7. Problem Records (BUG-024 central scenario)
    prob_sql = """
        INSERT OR REPLACE INTO problems (
            id, problem_code, build_no, failure_type, error_message, affected_file,
            suspect_commit, confidence, attribution_status, assignee, status,
            action, notification, created, resolved_date, title, description,
            root_cause_category, corrective_action, corrective_commit, verification_build, closure_notes
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """
    problems_data = [
        (1, "BUG-024", 128, "test",
         "ReportServiceTest.testCalculateMonthlyDepartmentExpenses:31 Monthly engineering expenses must equal sum of employee salaries ==> expected: <95000.0> but was: <0.0>",
         "ReportService.java", "a91bc42", 0.885, "Probable Cause", "Karthik", "Resolved",
         "Rollback recommended: git revert a91bc42 (touches 1 file: ReportService.java)",
         "Build #128 FAILED (test). Suspect commit a91bc42 by Karthik, confidence 0.885. Action: Fix formula or revert commit.",
         "2026-10-22 16:30:15", "2026-10-22 17:15:30",
         "ReportServiceTest assertion failure in monthly expense aggregation",
         "Karthik introduced intentional defect in commit a91bc42 causing calculateDepartmentTotalExpense() to return 0.0 instead of accumulated employee salaries.",
         "Logic / Calculation Defect",
         "Corrected aggregation loop to accumulate employee salary for matching department.",
         "c48fe19", 129,
         "Build #129 passed with 20/20 green tests. Verified and approved by Team Lead Prakash Raj.")
    ]
    con.executemany(prob_sql, problems_data)

    # 8. Commit Scores for BUG-024
    scores_data = [
        (1, "a91bc42", "Karthik", "Refactor monthly compensation reports and aggregate formula [CR-009]",
         "ReportService.java", 0.885,
         "Direct match with affected file 'ReportService.java' (+0.55) | Commit recency index 2/2 (+0.10) | Scope: 1 file(s) changed (+0.10)"),
        (1, "f0ad7d0", "Karthik", "Prepare monthly summary metrics [CR-007]",
         "ReportService.java", 0.115,
         "Historical commit | Commit recency index 1/2 (+0.05) | Lower relevance score")
    ]
    con.executemany("""
        INSERT OR REPLACE INTO commit_scores (problem_id, commit_hash, author, message, files, score, evidence_details)
        VALUES (?,?,?,?,?,?,?)
    """, scores_data)

    # 9. Alerts
    alerts_data = [
        ("ALT-001", 128, "Karthik", "Critical", "Pipeline Break: Unit Test Failure",
         "Build #128 failed on branch feature/reports. ReportServiceTest assertion error in monthly expense calculation.",
         "2026-10-22 16:30:20", 1, "Karthik", "2026-10-22 16:32:00", "BUG-024", "Acknowledged"),
        ("ALT-002", 125, "Prakash Raj", "Medium", "Pipeline Warning: Flaky Test",
         "Build #125 unstable due to high network latency in ValidatorTest.",
         "2026-10-22 13:55:10", 1, "Prakash Raj", "2026-10-22 14:00:00", None, "Resolved")
    ]
    con.executemany("""
        INSERT OR REPLACE INTO alerts (alert_code, build_no, developer, severity, notification_type, summary, created_at, acknowledged, acknowledged_by, acknowledged_at, problem_code, status)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
    """, alerts_data)

    # 10. Configuration Auditing System (FCA & PCA Observations AO-01..AO-07)
    audits = [
        ("AUD-01", "PCA", "Required-file presence", "Deployment instructions missing from root README", "README.md review against PCA checklist", "Minor", B, "Closed", "2026-09-20"),
        ("AUD-02", "FCA", "Naming convention verification", "Initial branch naming omitted standard feature/ prefix", "Git branch log audit", "Minor", P, "Closed", "2026-09-22"),
        ("AUD-03", "PCA", "Build reproducibility", "Maven Surefire plugin version was unpinned", "pom.xml configuration inspection", "Major", B, "Closed", "2026-09-02"),
        ("AUD-04", "FCA", "Requirements traceability", "Verification of SRS FR-01 through FR-14 mapping to unit test cases", "Traceability Matrix review", "Conforming", P, "Closed", "2026-09-19"),
        ("AUD-05", "PCA", "Database schema parity", "Column names in schema.sql matched System Design Document v1.0", "Schema comparison with SDD Table 12", "Conforming", P, "Closed", "2026-09-21"),
        ("AUD-06", "FCA", "Failure attribution verification", "Validation of ranking engine accuracy against compiler and test failures", "Test execution report on seeded defect", "Conforming", B, "Closed", "2026-10-22"),
        ("AUD-07", "PCA", "Release package integrity", "Verification of SHA-256 checksums and release manifest for CommitSleuth v1.0.0", "Release manifest and binary checksum verification", "Conforming", P, "Closed", "2026-10-22")
    ]
    con.executemany("INSERT OR REPLACE INTO audit_observations (audit_id, audit_type, checklist_item, observation, evidence, severity, owner, status, closure_date) VALUES (?,?,?,?,?,?,?,?,?)", audits)

    # 11. Releases
    sample_sha = hashlib.sha256(b"CommitSleuth-v1.0.0-verified-release-package").hexdigest()
    releases = [
        ("CS-REL-01", "v0.1.0", "v0.1.0", "557c19c", 100, "reports/release-v0.1.0.tar.gz", hashlib.sha256(b"v0.1.0").hexdigest(), "Approved", "CCB", "2026-09-04"),
        ("CS-REL-02", "v0.2.0", "v0.2.0", "f0ad7d0", 101, "reports/release-v0.2.0.tar.gz", hashlib.sha256(b"v0.2.0").hexdigest(), "Approved", "CCB", "2026-09-25"),
        ("CS-REL-03", "v1.0.0", "v1.0.0", "HEAD", 129, "reports/CommitSleuth-v1.0.0.zip", sample_sha, "Approved", "Faculty Guide / CCB", "2026-10-22")
    ]
    con.executemany("INSERT OR REPLACE INTO releases VALUES (?,?,?,?,?,?,?,?,?,?)", releases)

    # 12. Promotions
    promotions = [
        ("Employee Management System", "Development", "Testing", "2026-09-04 10:30", "Bharathwaraj", "PASSED", "All unit tests passed; CR-003 approved", "v0.1.0"),
        ("Employee Management System", "Testing", "Production", "2026-09-04 14:15", "CCB", "PASSED", "Baseline BL-03 verified and approved", "v0.1.0"),
        ("Employee Management System", "Development", "Testing", "2026-09-25 11:00", "Prakash Raj", "PASSED", "Sprint 3/4 tests passed; CR-006 approved", "v0.2.0"),
        ("Employee Management System", "Development", "Testing", "2026-10-22 16:31", "CCB", "BLOCKED", "Automated tests did not pass (ReportServiceTest assertion failure in Build #128)", None),
        ("Employee Management System", "Development", "Testing", "2026-10-22 17:20", "Prakash Raj", "PASSED", "Verification Build #129 passed with 20/20 tests green (CR-010 verified)", "v1.0.0"),
        ("Employee Management System", "Testing", "Release Candidate", "2026-10-22 17:35", "CCB", "PASSED", "FCA and PCA audit requirements satisfied", "v1.0.0"),
        ("Employee Management System", "Release Candidate", "Production", "2026-10-22 18:00", "CCB", "PASSED", "Final Review release baseline BL-05 approved", "v1.0.0")
    ]
    con.executemany("INSERT OR REPLACE INTO promotions (item, from_level, to_level, promo_date, approver, result, reason, release_tag) VALUES (?,?,?,?,?,?,?,?)", promotions)

    con.commit()
    con.close()
    print("Database schema and core SCM records successfully populated at:", common.DB)

if __name__ == "__main__":
    seed()
