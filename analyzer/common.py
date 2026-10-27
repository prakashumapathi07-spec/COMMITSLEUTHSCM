
"""Common utilities for CommitSleuth:
Database connection, schema initialization, configuration management,
and audit logging.
"""

import os
import sqlite3
import datetime
import yaml


# Project root directory
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Database path: use CS_DB when configured; otherwise use the project DB.
DB = os.environ.get(
    "CS_DB",
    os.path.join(ROOT, "database", "commitsleuth.db")
)

# Database schema file
SCHEMA_FILE = os.path.join(ROOT, "database", "schema.sql")

# Configuration file
CFG_FILE = os.path.join(ROOT, "scoring_config.yaml")


def connect():
    """Connect to the configured SQLite database."""
    db_directory = os.path.dirname(os.path.abspath(DB))
    os.makedirs(db_directory, exist_ok=True)

    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")

    return con


def q(sql, args=()):
    """Execute a query and return all matching rows."""
    with connect() as con:
        return con.execute(sql, args).fetchall()


def ex(sql, args=()):
    """Execute an INSERT, UPDATE, or DELETE statement."""
    with connect() as con:
        cur = con.execute(sql, args)
        con.commit()
        return cur.lastrowid


def initialize_schema():
    """
    Initialize all application tables from database/schema.sql.

    Existing tables and records are preserved because the schema uses
    CREATE TABLE IF NOT EXISTS. This does not migrate existing tables
    whose columns or constraints differ from the schema.
    """
    if not os.path.isfile(SCHEMA_FILE):
        raise FileNotFoundError(
            f"Database schema file not found: {SCHEMA_FILE}"
        )

    with open(SCHEMA_FILE, "r", encoding="utf-8") as file:
        schema_sql = file.read()

    with connect() as con:
        con.executescript(schema_sql)

    print(f"Database schema initialized: {os.path.abspath(DB)}")


def check_table_exists(table_name):
    """Check whether a table exists in the configured database."""
    row = q(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table' AND name = ?
        """,
        (table_name,)
    )

    return bool(row)


def initialize_database():
    """Initialize the schema and return the database path and tables."""
    initialize_schema()

    with connect() as con:
        tables = [
            row["name"]
            for row in con.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type = 'table'
                ORDER BY name
                """
            ).fetchall()
        ]

    return {
        "database": os.path.abspath(DB),
        "tables": tables
    }


def log_audit(username, action, details=""):
    """Record an audit event without interrupting the main operation."""
    try:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        ex(
            """
            INSERT INTO audit_trail
                (timestamp, username, action, details)
            VALUES (?, ?, ?, ?)
            """,
            (now, username or "system", action, details)
        )
    except sqlite3.Error as error:
        print(f"Warning: audit logging failed: {error}")


def load_cfg():
    """Load configuration or return default settings."""
    if not os.path.exists(CFG_FILE):
        return {
            "weights": {
                "file_match": 0.55,
                "pom_change": 0.25,
                "recency": 0.10,
                "change_size": 0.10
            },
            "rollback": {
                "confidence_threshold": 0.60,
                "max_files_for_isolation": 3
            },
            "notification": {
                "enabled": True,
                "channel": "log",
                "template": (
                    "Build #{build_no} FAILED ({failure_type}). "
                    "Suspect commit {commit} by {author}, confidence "
                    "{confidence}. Action: {action}"
                )
            },
            "project": {
                "repo_url": (
                    "https://github.com/"
                    "prakashumapathi07-spec/COMMITSLEUTHSCM.git"
                ),
                "jenkins_url": (
                    "http://localhost:8080/job/CommitSleuth-CI/"
                )
            }
        }

    with open(CFG_FILE, "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    return config or {}


def save_cfg(cfg_dict):
    """Save configuration to the YAML file."""
    with open(CFG_FILE, "w", encoding="utf-8") as file:
        yaml.safe_dump(
            cfg_dict,
            file,
            sort_keys=False,
            default_flow_style=False
        )


def get_database_path():
    """Return the absolute path of the configured database."""
    return os.path.abspath(DB)


if __name__ == "__main__":
    info = initialize_database()

    print("\nCommitSleuth Database Check")
    print("=" * 35)
    print("Database:", info["database"])
    print("\nTables found:")

    for table in info["tables"]:
        print(f" - {table}")

    print(f"\nTotal tables: {len(info['tables'])}")
