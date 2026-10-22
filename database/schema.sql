-- CommitSleuth Relational Schema for Software Configuration Management
-- Compatible with SQLite3 and supports all SCM Activities

CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('admin', 'maintainer', 'viewer')),
    full_name TEXT NOT NULL,
    email TEXT
);

CREATE TABLE IF NOT EXISTS developers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    username TEXT NOT NULL UNIQUE,
    github_username TEXT NOT NULL,
    email TEXT NOT NULL,
    role TEXT NOT NULL,
    module TEXT NOT NULL,
    branch TEXT NOT NULL,
    avatar_color TEXT DEFAULT '#3b82f6',
    last_commit_time TEXT
);

CREATE TABLE IF NOT EXISTS ci_register (
    ci_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    version TEXT NOT NULL,
    status TEXT NOT NULL,
    owner TEXT NOT NULL,
    approval TEXT NOT NULL,
    baseline TEXT,
    category TEXT,
    last_modified TEXT
);

CREATE TABLE IF NOT EXISTS change_requests (
    cr_id TEXT PRIMARY KEY,
    title TEXT,
    description TEXT NOT NULL,
    requester TEXT NOT NULL,
    impact TEXT NOT NULL,
    priority TEXT DEFAULT 'Medium',
    reason TEXT,
    status TEXT NOT NULL CHECK(status IN ('Raised', 'Under Review', 'Approved', 'Implemented', 'Rejected')),
    decision TEXT,
    decision_date TEXT,
    branch TEXT,
    pull_request TEXT,
    related_commit TEXT
);

CREATE TABLE IF NOT EXISTS builds (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    build_no INTEGER NOT NULL UNIQUE,
    result TEXT NOT NULL CHECK(result IN ('SUCCESS', 'FAILURE', 'UNSTABLE', 'ABORTED', 'RUNNING')),
    commit_hash TEXT NOT NULL,
    branch TEXT DEFAULT 'main',
    failure_type TEXT DEFAULT 'None',
    test_summary TEXT,
    duration_sec REAL DEFAULT 0.0,
    log_path TEXT,
    created TEXT NOT NULL,
    author TEXT DEFAULT 'Prakash Raj',
    commit_message TEXT DEFAULT 'Routine update',
    trigger_type TEXT DEFAULT 'GitHub Push',
    failed_stage TEXT DEFAULT 'None',
    tests_total INTEGER DEFAULT 20,
    tests_failed INTEGER DEFAULT 0,
    tests_passed INTEGER DEFAULT 20,
    job_name TEXT DEFAULT 'backend/report-service'
);

CREATE TABLE IF NOT EXISTS problems (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    problem_code TEXT UNIQUE,
    build_no INTEGER NOT NULL,
    failure_type TEXT NOT NULL CHECK(failure_type IN ('compile', 'test', 'dependency', 'unknown')),
    error_message TEXT,
    affected_file TEXT,
    suspect_commit TEXT,
    confidence REAL DEFAULT 0.0,
    attribution_status TEXT DEFAULT 'Probable Cause',
    assignee TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('Open', 'Investigating', 'Assigned', 'Fix Submitted', 'Verification Pending', 'Fixed', 'Verified', 'Closed', 'Resolved')),
    action TEXT,
    notification TEXT,
    created TEXT NOT NULL,
    resolved_date TEXT,
    title TEXT,
    description TEXT,
    root_cause_category TEXT DEFAULT 'Logic Error',
    corrective_action TEXT,
    corrective_commit TEXT,
    verification_build INTEGER,
    closure_notes TEXT,
    FOREIGN KEY(build_no) REFERENCES builds(build_no)
);

CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alert_code TEXT UNIQUE,
    build_no INTEGER NOT NULL,
    developer TEXT NOT NULL,
    severity TEXT NOT NULL CHECK(severity IN ('Critical', 'High', 'Medium', 'Low')),
    notification_type TEXT NOT NULL,
    summary TEXT NOT NULL,
    created_at TEXT NOT NULL,
    acknowledged INTEGER DEFAULT 0,
    acknowledged_by TEXT,
    acknowledged_at TEXT,
    problem_code TEXT,
    status TEXT DEFAULT 'Unread',
    FOREIGN KEY(build_no) REFERENCES builds(build_no)
);

CREATE TABLE IF NOT EXISTS commit_scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    problem_id INTEGER NOT NULL,
    commit_hash TEXT NOT NULL,
    author TEXT NOT NULL,
    message TEXT NOT NULL,
    files TEXT,
    score REAL NOT NULL,
    evidence_details TEXT,
    FOREIGN KEY(problem_id) REFERENCES problems(id)
);

CREATE TABLE IF NOT EXISTS promotions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item TEXT NOT NULL,
    from_level TEXT NOT NULL,
    to_level TEXT NOT NULL,
    promo_date TEXT NOT NULL,
    approver TEXT NOT NULL,
    result TEXT NOT NULL CHECK(result IN ('PASSED', 'BLOCKED')),
    reason TEXT,
    release_tag TEXT
);

CREATE TABLE IF NOT EXISTS baselines (
    baseline_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    version TEXT NOT NULL,
    tag TEXT,
    commit_hash TEXT,
    description TEXT,
    approval_date TEXT NOT NULL,
    approver TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Approved'
);

CREATE TABLE IF NOT EXISTS audit_observations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    audit_id TEXT NOT NULL,
    audit_type TEXT NOT NULL CHECK(audit_type IN ('FCA', 'PCA', 'SCM-General')),
    checklist_item TEXT NOT NULL,
    observation TEXT NOT NULL,
    evidence TEXT,
    severity TEXT NOT NULL CHECK(severity IN ('Critical', 'Major', 'Minor', 'Conforming')),
    owner TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('Open', 'In Progress', 'Closed')),
    closure_date TEXT
);

CREATE TABLE IF NOT EXISTS releases (
    release_id TEXT PRIMARY KEY,
    version TEXT NOT NULL,
    git_tag TEXT NOT NULL,
    commit_hash TEXT NOT NULL,
    build_no INTEGER,
    artifact_path TEXT,
    checksum_sha256 TEXT,
    approval_status TEXT NOT NULL DEFAULT 'Approved',
    approver TEXT NOT NULL,
    created TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS audit_trail (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    username TEXT NOT NULL,
    action TEXT NOT NULL,
    details TEXT
);
