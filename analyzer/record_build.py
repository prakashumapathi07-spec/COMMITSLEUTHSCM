"""CommitSleuth Build Recorder and Automated Failure Attribution Agent.
Invoked by Jenkins post-build steps or via automated CLI triggers.
"""
import argparse
import datetime
import os
import re
import subprocess
import smtplib
from email.message import EmailMessage

from common import q, ex, log_audit, load_cfg, ROOT
import log_parser
import scorer

def git(*args):
    """Executes a git command in the repository root and returns trimmed stdout."""
    res = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    return res.stdout.strip()

def commits_since_last_success():
    """Identifies the candidate commits introduced since the last successful build."""
    row = q("SELECT commit_hash FROM builds WHERE result='SUCCESS' ORDER BY id DESC LIMIT 1")
    rng = []
    if row and row[0]["commit_hash"]:
        last_success = row[0]["commit_hash"]
        # Check if last_success is a valid commit object
        chk = git("cat-file", "-t", last_success)
        if chk == "commit":
            rng = [f"{last_success}..HEAD"]
    
    if not rng:
        rng = ["-n", "5"]

    log_output = git("log", "--reverse", "--no-merges", "--pretty=%h|%an|%s", *rng)
    if not log_output:
        # Fallback to at least current HEAD commit
        log_output = git("log", "-1", "--pretty=%h|%an|%s")

    commits = []
    for line in log_output.splitlines():
        if not line.strip() or "|" not in line:
            continue
        parts = line.split("|", 2)
        h = parts[0].strip()
        a = parts[1].strip() if len(parts) > 1 else "Unknown"
        m = parts[2].strip() if len(parts) > 2 else ""
        
        # Collect changed files for this commit
        files_raw = git("show", "--name-only", "--pretty=format:", h)
        files = [f.strip().replace("\\", "/") for f in files_raw.splitlines() if f.strip()]
        commits.append({
            "hash": h,
            "author": a,
            "message": m,
            "files": files
        })
    return commits

def notify(text, cfg):
    """Dispatches notification via log file, console, and configured notification channels."""
    n_cfg = cfg.get("notification", {})
    if not n_cfg.get("enabled", True):
        return

    os.makedirs(os.path.join(ROOT, "reports"), exist_ok=True)
    log_path = os.path.join(ROOT, "reports", "notifications.log")
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {text}\n")
    print(f"NOTIFY: {text}")

    if n_cfg.get("channel") == "email" and os.environ.get("SMTP_HOST") and os.environ.get("NOTIFY_TO"):
        try:
            msg = EmailMessage()
            msg["Subject"] = f"CommitSleuth Build Failure Alert"
            msg["From"] = os.environ.get("SMTP_USER", "commitsleuth-ci@example.com")
            msg["To"] = os.environ["NOTIFY_TO"]
            msg.set_content(text)
            with smtplib.SMTP_SSL(os.environ["SMTP_HOST"], int(os.environ.get("SMTP_PORT", 465))) as s:
                s.login(os.environ["SMTP_USER"], os.environ["SMTP_PASS"])
                s.send_message(msg)
        except Exception as e:
            print(f"Failed to dispatch email notification: {e}")

def get_next_problem_code():
    rows = q("SELECT COUNT(*) AS cnt FROM problems")
    cnt = rows[0]["cnt"] if rows else 0
    return f"P-{cnt + 1:03d}"

def store_failure(build_no, log_text, commits, ftype_override=None):
    """Performs failure analysis, attribution, records problem, and saves scores."""
    cfg = load_cfg()
    parsed = log_parser.parse_log(log_text)
    ftype = ftype_override or parsed["failure_type"]
    err_msg = parsed["error_message"]
    affected_file = parsed["affected_file"]

    ranked = scorer.rank(commits, log_text, ftype, cfg)
    if not ranked:
        return None

    top = ranked[0]
    action = scorer.decide(top, cfg)
    prob_code = get_next_problem_code()
    attribution_status = top.get("attribution_status", "Probable Cause")

    template = cfg.get("notification", {}).get("template", "Build #{build_no} FAILED ({failure_type}). Suspect commit {commit} by {author}, confidence {confidence}. Action: {action}")
    notif_text = template.format(
        build_no=build_no,
        failure_type=ftype,
        commit=top["hash"],
        author=top["author"],
        confidence=f"{top['score']:.3f}",
        action=action
    )

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pid = ex(
        """INSERT INTO problems (
            problem_code, build_no, failure_type, error_message, affected_file,
            suspect_commit, confidence, attribution_status, assignee, status,
            action, notification, created
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (prob_code, build_no, ftype, err_msg, affected_file,
         top["hash"], top["score"], attribution_status, top["author"], "Open",
         action, notif_text, now)
    )

    for r in ranked:
        ex(
            """INSERT INTO commit_scores (
                problem_id, commit_hash, author, message, files, score, evidence_details
            ) VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (pid, r["hash"], r["author"], r["message"], ", ".join(r.get("files", [])),
             r["score"], r.get("evidence_details", ""))
        )

    notify(notif_text, cfg)
    log_audit("Jenkins-Agent", f"Recorded Build Failure #{build_no}", f"Attributed to {top['hash']} ({top['author']}) with confidence {top['score']}")
    return pid

def read_log_file(path):
    """Safely reads a log file detecting UTF-16 BOM (from PowerShell redirection) or UTF-8."""
    if not os.path.exists(path):
        return ""
    try:
        with open(path, "rb") as f:
            raw = f.read()
        if raw.startswith(b"\xff\xfe") or raw.startswith(b"\xfe\xff"):
            return raw.decode("utf-16", errors="ignore")
        try:
            return raw.decode("utf-8-sig")
        except UnicodeDecodeError:
            return raw.decode("cp1252", errors="ignore")
    except Exception:
        return ""

def record(build_no, result, log_file="build.log", branch=None):
    branch = branch or git("rev-parse", "--abbrev-ref", "HEAD") or "main"
    head = git("rev-parse", "--short", "HEAD")
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    log_text = ""
    ftype = "None"
    test_summary = "All tests passed"

    if result == "FAILURE":
        log_text = read_log_file(log_file)
        parsed = log_parser.parse_log(log_text)
        ftype = parsed["failure_type"]
        test_summary = parsed["error_message"]

    # Insert build record first to satisfy foreign key in problems table
    ex(
        """INSERT OR REPLACE INTO builds (
            build_no, result, commit_hash, branch, failure_type, test_summary, duration_sec, log_path, created
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (build_no, result, head, branch, ftype, test_summary, 12.5, log_file if os.path.exists(log_file) else None, now)
    )

    if result == "FAILURE":
        commits = commits_since_last_success()
        if commits:
            store_failure(build_no, log_text, commits, ftype)

    log_audit("Jenkins-Agent", f"Build #{build_no} Finished: {result}", f"Commit {head} on branch {branch}")
    print(f"Build #{build_no} recorded: {result} at commit {head} ({branch})")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Record build result and trigger failure attribution.")
    parser.add_argument("--result", required=True, choices=["SUCCESS", "FAILURE", "UNSTABLE"])
    parser.add_argument("--build", type=int, required=True, help="Jenkins or pipeline build number")
    parser.add_argument("--log", default="build.log", help="Path to build console output log")
    parser.add_argument("--branch", default=None, help="Git branch name")
    args = parser.parse_args()

    record(args.build, args.result, args.log, args.branch)
