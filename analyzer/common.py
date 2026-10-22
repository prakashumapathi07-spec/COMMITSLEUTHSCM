"""Common utilities for CommitSleuth: Database connection, configuration management, and audit logging."""
import os
import sqlite3
import datetime
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.environ.get("CS_DB", os.path.join(ROOT, "database", "commitsleuth.db"))
CFG_FILE = os.path.join(ROOT, "scoring_config.yaml")

def connect():
    os.makedirs(os.path.dirname(DB), exist_ok=True)
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con

def q(sql, args=()):
    with connect() as con:
        return con.execute(sql, args).fetchall()

def ex(sql, args=()):
    with connect() as con:
        cur = con.execute(sql, args)
        con.commit()
        return cur.lastrowid

def log_audit(username, action, details=""):
    try:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ex("INSERT INTO audit_trail(timestamp, username, action, details) VALUES (?, ?, ?, ?)",
           (now, username or "system", action, details))
    except Exception:
        pass

def load_cfg():
    if not os.path.exists(CFG_FILE):
        return {
            "weights": {"file_match": 0.55, "pom_change": 0.25, "recency": 0.10, "change_size": 0.10},
            "rollback": {"confidence_threshold": 0.60, "max_files_for_isolation": 3},
            "notification": {"enabled": True, "channel": "log", "template": "Build #{build_no} FAILED ({failure_type}). Suspect commit {commit} by {author}, confidence {confidence}. Action: {action}"},
            "project": {"repo_url": "https://github.com/prakashumapathi07-spec/COMMITSLEUTHSCM.git", "jenkins_url": "http://localhost:8080/job/CommitSleuth-Pipeline"}
        }
    with open(CFG_FILE, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def save_cfg(cfg_dict):
    with open(CFG_FILE, "w", encoding="utf-8") as f:
        yaml.safe_dump(cfg_dict, f, sort_keys=False, default_flow_style=False)
