
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

from common import (
    q,
    ex,
    log_audit,
    load_cfg,
    ROOT,
    connect,
    initialize_database,
)
import log_parser
import scorer


def git(*args):
    """Execute a Git command in the repository root."""
    try:
        res = subprocess.run(
            ["git", *args],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        return res.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def table_exists(table_name):
    """Check whether a table exists in the configured SQLite database."""
    with connect() as con:
        row = con.execute(
            """
            SELECT 1
            FROM sqlite_master
            WHERE type = 'table' AND name = ?
            """,
            (table_name,),
        ).fetchone()
        return row is not None


def get_table_columns(table_name):
    """Return existing columns for a table."""
    with connect() as con:
        rows = con.execute(
            f'PRAGMA table_info("{table_name}")'
        ).fetchall()
        return {row["name"] for row in rows}


def ensure_builds_table():
    """
    Create the builds table if it is missing.

    Existing tables are left unchanged. The columns below match the
    INSERT statement used by this recorder.
    """
    with connect() as con:
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS builds (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                build_no INTEGER NOT NULL UNIQUE,
                result TEXT NOT NULL,
                commit_hash TEXT,
                branch TEXT,
                failure_type TEXT,
                test_summary TEXT,
                duration_sec REAL,
                log_path TEXT,
                created TEXT NOT NULL
            )
            """
        )
        con.commit()


def commits_since_last_success():
    """Identify candidate commits introduced since the last successful build."""
    if not table_exists("builds"):
        return []

    rows = q(
        """
        SELECT commit_hash
        FROM builds
        WHERE result = 'SUCCESS'
        ORDER BY id DESC
        LIMIT 1
        """
    )

    ranges = []

    if rows and rows[0]["commit_hash"]:
        last_success = rows[0]["commit_hash"]
        check = git("cat-file", "-t", last_success)

        if check == "commit":
            ranges = [f"{last_success}..HEAD"]

    if not ranges:
        ranges = ["-n", "5"]

    log_output = git(
        "log",
        "--reverse",
        "--no-merges",
        "--pretty=%h|%an|%s",
        *ranges,
    )

    if not log_output:
        log_output = git("log", "-1", "--pretty=%h|%an|%s")

    commits = []

    for line in log_output.splitlines():
        if not line.strip() or "|" not in line:
            continue

        parts = line.split("|", 2)
        commit_hash = parts[0].strip()
        author = parts[1].strip() if len(parts) > 1 else "Unknown"
        message = parts[2].strip() if len(parts) > 2 else ""

        files_raw = git(
            "show",
            "--name-only",
            "--pretty=format:",
            commit_hash,
        )

        files = [
            item.strip().replace("\\", "/")
            for item in files_raw.splitlines()
            if item.strip()
        ]

        commits.append(
            {
                "hash": commit_hash,
                "author": author,
                "message": message,
                "files": files,
            }
        )

    return commits


def notify(text, cfg):
    """Write notifications to a log and optionally send email."""
    notification_cfg = cfg.get("notification", {})

    if not notification_cfg.get("enabled", True):
        return

    reports_dir = os.path.join(ROOT, "reports")
    os.makedirs(reports_dir, exist_ok=True)

    log_path = os.path.join(reports_dir, "notifications.log")
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(log_path, "a", encoding="utf-8") as file:
        file.write(f"[{timestamp}] {text}\n")

    print(f"NOTIFY: {text}")

    if (
        notification_cfg.get("channel") == "email"
        and os.environ.get("SMTP_HOST")
        and os.environ.get("NOTIFY_TO")
    ):
        try:
            message = EmailMessage()
            message["Subject"] = "CommitSleuth Build Failure Alert"
            message["From"] = os.environ.get(
                "SMTP_USER",
                "commitsleuth-ci@example.com",
            )
            message["To"] = os.environ["NOTIFY_TO"]
            message.set_content(text)

            with smtplib.SMTP_SSL(
                os.environ["SMTP_HOST"],
                int(os.environ.get("SMTP_PORT", "465")),
            ) as server:
                server.login(
                    os.environ["SMTP_USER"],
                    os.environ["SMTP_PASS"],
                )
                server.send_message(message)

        except Exception as error:
            print(f"Failed to dispatch email notification: {error}")


def get_next_problem_code():
    """Generate the next problem identifier."""
    if not table_exists("problems"):
        raise RuntimeError(
            "The 'problems' table does not exist. "
            "Initialize the CommitSleuth database schema first."
        )

    rows = q("SELECT COUNT(*) AS cnt FROM problems")
    count = rows[0]["cnt"] if rows else 0

    return f"P-{count + 1:03d}"


def store_failure(build_no, log_text, commits, failure_type_override=None):
    """Analyze a failed build and record attribution when possible."""
    cfg = load_cfg()
    parsed = log_parser.parse_log(log_text)

    failure_type = failure_type_override or parsed["failure_type"]
    error_message = parsed["error_message"]
    affected_file = parsed["affected_file"]

    ranked = scorer.rank(
        commits,
        log_text,
        failure_type,
        cfg,
    )

    if not ranked:
        print(
            f"No candidate commits found for build #{build_no}; "
            "failure details remain recorded in builds."
        )
        return None

    if not table_exists("problems"):
        print(
            "Warning: 'problems' table is missing. "
            "The build result was recorded, but failure attribution "
            "could not be saved."
        )
        return None

    if not table_exists("commit_scores"):
        print(
            "Warning: 'commit_scores' table is missing. "
            "Failure attribution could not be saved."
        )
        return None

    top = ranked[0]
    action = scorer.decide(top, cfg)
    problem_code = get_next_problem_code()
    attribution_status = top.get(
        "attribution_status",
        "Probable Cause",
    )

    template = cfg.get("notification", {}).get(
        "template",
        (
            "Build #{build_no} FAILED ({failure_type}). "
            "Suspect commit {commit} by {author}, confidence "
            "{confidence}. Action: {action}"
        ),
    )

    notification_text = template.format(
        build_no=build_no,
        failure_type=failure_type,
        commit=top["hash"],
        author=top["author"],
        confidence=f"{top['score']:.3f}",
        action=action,
    )

    created = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    problem_id = ex(
        """
        INSERT INTO problems (
            problem_code,
            build_no,
            failure_type,
            error_message,
            affected_file,
            suspect_commit,
            confidence,
            attribution_status,
            assignee,
            status,
            action,
            notification,
            created
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            problem_code,
            build_no,
            failure_type,
            error_message,
            affected_file,
            top["hash"],
            top["score"],
            attribution_status,
            top["author"],
            "Open",
            action,
            notification_text,
            created,
        ),
    )

    for item in ranked:
        ex(
            """
            INSERT INTO commit_scores (
                problem_id,
                commit_hash,
                author,
                message,
                files,
                score,
                evidence_details
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                problem_id,
                item["hash"],
                item["author"],
                item["message"],
                ", ".join(item.get("files", [])),
                item["score"],
                item.get("evidence_details", ""),
            ),
        )

    notify(notification_text, cfg)

    log_audit(
        "Jenkins-Agent",
        f"Recorded Build Failure #{build_no}",
        (
            f"Attributed to {top['hash']} ({top['author']}) "
            f"with confidence {top['score']}"
        ),
    )

    return problem_id


def read_log_file(path):
    """Read a Jenkins log with support for common Windows encodings."""
    if not os.path.exists(path):
        return ""

    try:
        with open(path, "rb") as file:
            raw = file.read()

        if raw.startswith((b"\xff\xfe", b"\xfe\xff")):
            return raw.decode("utf-16", errors="replace")

        try:
            return raw.decode("utf-8-sig")
        except UnicodeDecodeError:
            return raw.decode("cp1252", errors="replace")

    except OSError as error:
        print(f"Could not read build log '{path}': {error}")
        return ""


def record(build_no, result, log_file="build.log", branch=None):
    """Record the Jenkins build and analyze failures when possible."""
    # This creates only the builds table if missing. Other application
    # tables must be initialized using the project's existing schema.
    ensure_builds_table()

    branch = (
        branch
        or git("rev-parse", "--abbrev-ref", "HEAD")
        or "main"
    )

    head = git("rev-parse", "--short", "HEAD") or None
    created = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    log_text = ""
    failure_type = "None"
    test_summary = "All tests passed"

    if result in ("FAILURE", "UNSTABLE"):
        log_text = read_log_file(log_file)
        parsed = log_parser.parse_log(log_text)
        failure_type = parsed.get("failure_type", "Unknown")
        test_summary = parsed.get("error_message", "Build did not succeed")

    # Insert or update the build record before recording related problems.
    ex(
        """
        INSERT INTO builds (
            build_no,
            result,
            commit_hash,
            branch,
            failure_type,
            test_summary,
            duration_sec,
            log_path,
            created
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(build_no) DO UPDATE SET
            result = excluded.result,
            commit_hash = excluded.commit_hash,
            branch = excluded.branch,
            failure_type = excluded.failure_type,
            test_summary = excluded.test_summary,
            duration_sec = excluded.duration_sec,
            log_path = excluded.log_path,
            created = excluded.created
        """,
        (
            build_no,
            result,
            head,
            branch,
            failure_type,
            test_summary,
            None,
            log_file if os.path.exists(log_file) else None,
            created,
        ),
    )

    print(
        f"Build #{build_no} recorded: {result} "
        f"at commit {head} ({branch})"
    )

    if result in ("FAILURE", "UNSTABLE"):
        try:
            commits = commits_since_last_success()

            if commits:
                store_failure(
                    build_no,
                    log_text,
                    commits,
                    failure_type,
                )
            else:
                print(
                    "No candidate commits found; build result "
                    "was still recorded."
                )

        except Exception as error:
            # Keep the build result recorded even if attribution fails.
            print(
                "Warning: build result was recorded, but failure "
                f"attribution failed: {error}"
            )

    log_audit(
        "Jenkins-Agent",
        f"Build #{build_no} Finished: {result}",
        f"Commit {head} on branch {branch}",
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "Record build result and trigger failure attribution."
        )
    )

    parser.add_argument(
        "--result",
        required=True,
        choices=["SUCCESS", "FAILURE", "UNSTABLE"],
    )

    parser.add_argument(
        "--build",
        type=int,
        required=True,
        help="Jenkins or pipeline build number",
    )

    parser.add_argument(
        "--log",
        default="build.log",
        help="Path to build console output log",
    )

    parser.add_argument(
        "--branch",
        default=None,
        help="Git branch name",
    )

    args = parser.parse_args()

    try:
        record(
            args.build,
            args.result,
            args.log,
            args.branch,
        )
    except Exception as error:
        print(f"ERROR: Failed to record build: {error}")
        raise
