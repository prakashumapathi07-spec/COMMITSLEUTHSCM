"""Database seed script for CommitSleuth.
Populates initial SCM data: Users, 20 CIs, CR-001..CR-009, Baselines BL-01..BL-05,
Audit observations AO-01..AO-07, historical builds, problems, and promotions.
Usage: python database/seed.py [--reset] [--demo]
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
        ("arun", generate_password_hash("maint123"), "maintainer", "Arun Kumar (23MIS0245)", "arun.kumar2026@vitstudent.ac.in"),
        ("kavya", generate_password_hash("maint123"), "maintainer", "Kavya Sharma (23MIS0310)", "kavya.sharma2026@vitstudent.ac.in"),
        ("admin", generate_password_hash("admin123"), "admin", "Administrator", "admin@commitsleuth.org"),
        ("viewer", generate_password_hash("viewer123"), "viewer", "SCM Reviewer / Auditor", "reviewer@vit.ac.in")
    ]
    con.executemany("INSERT OR REPLACE INTO users VALUES (?,?,?,?,?)", users)

    # 2. 20 Configuration Items (Review-1 & Review-2 Table 1 & Table 3)
    B, P = "Bharathwaraj K S", "Prakash Raj U"
    cis = [
        ("CSDOC01", "Project Proposal", "v1.0", "Baselined (BL-01)", B, "Approved", "BL-01", "Documentation", "2026-08-07"),
        ("CSDOC02", "Software Requirement Specification (SRS)", "v1.0", "Baselined (BL-01)", P, "Approved", "BL-01", "Documentation", "2026-08-12"),
        ("CSDOC03", "Software Configuration Management Plan", "v1.0", "Baselined (BL-01)", B, "Approved", "BL-01", "Documentation", "2026-08-14"),
        ("CSDOC04", "System Design Document", "v1.0", "Baselined (BL-02)", P, "Approved", "BL-02", "Documentation", "2026-09-04"),
        ("CSSRC01", "Source Code (Python modules)", "v1.0.0", "Baselined (BL-04)", P, "Approved", "BL-04", "Source Code", "2026-10-22"),
        ("CSSRC02", "Git Repository", "v1.0.0", "Baselined (BL-02)", B, "Approved", "BL-02", "Repository", "2026-10-22"),
        ("CSBLD01", "Jenkinsfile", "v1.0", "Tested, Baselined (BL-03)", B, "Approved", "BL-03", "Build & CI", "2026-09-02"),
        ("CSBLD02", "Maven Configuration (pom.xml)", "v1.0", "Tested, Baselined (BL-03)", B, "Approved", "BL-03", "Build & CI", "2026-09-02"),
        ("CSMOD01", "Build Log Parser", "v1.0", "Baselined (BL-04)", B, "Approved", "BL-04", "Core Module", "2026-10-22"),
        ("CSMOD02", "pom.xml Diff Analyzer", "v1.0", "Baselined (BL-04)", P, "Approved", "BL-04", "Core Module", "2026-10-22"),
        ("CSMOD03", "Commit Ranking Engine", "v1.0", "Baselined (BL-04)", P, "Approved", "BL-04", "Core Module", "2026-10-22"),
        ("CSMOD04", "Notification Module", "v1.0", "Baselined (BL-04)", B, "Approved", "BL-04", "Core Module", "2026-10-22"),
        ("CSMOD05", "Rollback Recommendation Module", "v1.0", "Baselined (BL-04)", P, "Approved", "BL-04", "Core Module", "2026-10-22"),
        ("CSMOD06", "Dashboard Module", "v1.0", "Baselined (BL-05)", P, "Approved", "BL-05", "Core Module", "2026-10-22"),
        ("CSDB01", "Database (build history and reports)", "v1.0", "Baselined (BL-02)", P, "Approved", "BL-02", "Database", "2026-10-22"),
        ("CSDOC05", "Test Plan", "v1.0", "Baselined (BL-05)", B, "Approved", "BL-05", "Documentation", "2026-10-22"),
        ("CSDOC06", "Test Cases", "v1.0", "Baselined (BL-05)", P, "Approved", "BL-05", "Documentation", "2026-10-22"),
        ("CSDOC07", "User Manual", "v1.0", "Baselined (BL-05)", P, "Approved", "BL-05", "Documentation", "2026-10-22"),
        ("CSDOC08", "Deployment Guide", "v1.0", "Baselined (BL-05)", B, "Approved", "BL-05", "Documentation", "2026-10-22"),
        ("CSREL01", "Release Package (CommitSleuth_v1.0)", "v1.0.0", "Baselined (BL-05)", B, "Approved", "BL-05", "Release", "2026-10-22")
    ]
    con.executemany("INSERT OR REPLACE INTO ci_register VALUES (?,?,?,?,?,?,?,?,?)", cis)

    # 3. Change Requests (CR-001 through CR-009)
    crs = [
        ("CR-001", "SRS Batching Problem Specification", "Add batching-problem definition to SRS", B, "SRS Document", "High", "Critical requirement for batch commit triage", "Implemented", "Approved by CCB", "2026-08-12", "feature/srs-batching", "PR #1", "557c19c"),
        ("CR-002", "SRS Dependency & Isolation Requirements", "Add pom.xml diff and isolation requirements to SRS", P, "SRS Document", "High", "Rollback safety boundary definition", "Implemented", "Approved by CCB", "2026-08-12", "feature/srs-isolation", "PR #2", "52b2e16"),
        ("CR-003", "Jenkins Post-Failure Hook", "Add post-failure hook and artifact archiving to Jenkinsfile", B, "Jenkinsfile", "High", "Automated log retrieval on pipeline break", "Implemented", "Approved by CCB", "2026-09-02", "feature/jenkins-hook", "PR #3", "760667e"),
        ("CR-004", "Database Schema Extension", "Add change_requests and problems tables to database schema", P, "Database Schema", "High", "Persistent SCM status accounting", "Implemented", "Approved by CCB", "2026-09-03", "feature/db-schema", "PR #4", "725a755"),
        ("CR-005", "Surefire XML Parser Support", "Add XML report and test assertion parsing to Build Log Parser", B, "Build Log Parser", "Medium", "Enhanced extraction of failing JUnit test cases", "Implemented", "Approved by CCB", "2026-09-18", "feature/parser-xml", "PR #5", "760667e"),
        ("CR-006", "Configurable Scoring Weights", "Make scoring weights configurable via YAML file", P, "Ranking Engine", "Medium", "Dynamic weighting adaptation without code edits", "Implemented", "Approved by CCB", "2026-09-19", "feature/scoring-config", "PR #6", "99bbeb5"),
        ("CR-007", "Responsive Modern Dashboard Redesign", "Redesign dashboard layout with glassmorphic metrics, RBAC, and auditing", P, "Dashboard Module", "Medium", "Interactive SCM review demonstration", "Implemented", "Approved by CCB", "2026-10-21", "feature/dashboard-redesign", "PR #7", "f0ad7d0"),
        ("CR-008", "Replace Jenkins CI with Alternative Tool", "Replace Jenkins with external cloud CI server", B, "Jenkinsfile, Pipeline", "High", "Disruptive architecture change", "Rejected", "Rejected by CCB: Uncontrolled design drift", "2026-09-20", "", "", ""),
        ("CR-009", "Resolve Calculator Defect & Restore Build", "Correct addition method in Calculator.java and verify JUnit tests pass", P, "Java Demo Application", "High", "Fix seeded calculation defect in CI pipeline", "Implemented", "Approved by CCB", "2026-10-22", "bugfix/demo-calc-failure", "PR #8", "HEAD")
    ]
    con.executemany("INSERT OR REPLACE INTO change_requests VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", crs)

    # 4. Baselines (BL-01 to BL-05)
    baselines = [
        ("BL-01", "Requirements Baseline", "v1.0", "v0.1.0-req", "557c19c", "Approved initial project proposal, SRS, and SCM plan", "2026-08-14", "Faculty Guide / CCB", "Approved"),
        ("BL-02", "Design & Repository Baseline", "v1.0", "v0.1.0", "557c19c", "System architecture, class diagrams, database schema v0.5, git repo", "2026-09-04", "Faculty Guide / CCB", "Approved"),
        ("BL-03", "CI / Build Baseline", "v1.0", "v0.1.0", "557c19c", "Jenkins declarative pipeline and Maven pom.xml configuration", "2026-09-04", "Faculty Guide / CCB", "Approved"),
        ("BL-04", "Analysis Module Baseline", "v0.2.0", "v0.2.0", "f0ad7d0", "Integrated log parser, commit ranking engine, scoring config YAML", "2026-09-25", "Faculty Guide / CCB", "Approved"),
        ("BL-05", "Final Release Baseline", "v1.0.0", "v1.0.0", "HEAD", "Complete SCM system with full 9 activities, dashboard, and verified demo app", "2026-10-22", "Faculty Guide / CCB", "Approved")
    ]
    con.executemany("INSERT OR REPLACE INTO baselines VALUES (?,?,?,?,?,?,?,?,?)", baselines)

    # 5. Configuration Auditing System (FCA & PCA Observations AO-01..AO-07)
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

    # 6. Releases
    sample_sha = hashlib.sha256(b"CommitSleuth-v1.0.0-verified-release-package").hexdigest()
    releases = [
        ("CS-REL-01", "v0.1.0", "v0.1.0", "557c19c", 100, "reports/release-v0.1.0.tar.gz", hashlib.sha256(b"v0.1.0").hexdigest(), "Approved", "CCB", "2026-09-04"),
        ("CS-REL-02", "v0.2.0", "v0.2.0", "f0ad7d0", 101, "reports/release-v0.2.0.tar.gz", hashlib.sha256(b"v0.2.0").hexdigest(), "Approved", "CCB", "2026-09-25"),
        ("CS-REL-03", "v1.0.0", "v1.0.0", "HEAD", 103, "reports/CommitSleuth-v1.0.0.zip", sample_sha, "Approved", "Faculty Guide / CCB", "2026-10-22")
    ]
    con.executemany("INSERT OR REPLACE INTO releases VALUES (?,?,?,?,?,?,?,?,?,?)", releases)

    # 7. Promotions
    promotions = [
        ("CommitSleuth demo app", "Development", "Testing", "2026-09-04 10:30", "BKS", "PASSED", "All unit tests passed; CR-003 approved", "v0.1.0"),
        ("CommitSleuth demo app", "Testing", "Production", "2026-09-04 14:15", "CCB", "PASSED", "Baseline BL-03 verified and approved", "v0.1.0"),
        ("CommitSleuth Suite", "Development", "Testing", "2026-09-25 11:00", "PRU", "PASSED", "Sprint 3/4 tests passed; CR-006 approved", "v0.2.0"),
        ("CommitSleuth Suite", "Development", "Testing", "2026-10-22 10:15", "CCB", "BLOCKED", "Automated tests did not pass (CalculatorTest failure)", None),
        ("CommitSleuth Suite", "Development", "Testing", "2026-10-22 11:30", "PRU", "PASSED", "All SCM verification gates successfully satisfied (CR-009)", "v1.0.0"),
        ("CommitSleuth Suite", "Testing", "Production", "2026-10-22 12:00", "CCB", "PASSED", "Final Review release baseline BL-05 approved", "v1.0.0")
    ]
    con.executemany("INSERT OR REPLACE INTO promotions (item, from_level, to_level, promo_date, approver, result, reason, release_tag) VALUES (?,?,?,?,?,?,?,?)", promotions)

    con.commit()
    con.close()
    print("Database schema and core SCM records successfully populated at:", common.DB)

if __name__ == "__main__":
    seed()
