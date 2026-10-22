"""Configuration Status Accounting (CSA) Reporter.
Generates comprehensive CSAR reports and CSV exports directly from the SQLite status database.
"""
import csv
import datetime
import io
import os
import subprocess
from common import q, ROOT

def git(*args):
    res = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    return res.stdout.strip()

def counts(sql):
    return {r[0]: r[1] for r in q(sql)}

def build_csar():
    """Generates a structured text Configuration Status Accounting Report (CSAR)."""
    cis = q("SELECT * FROM ci_register")
    approved = sum(1 for c in cis if "Baselined" in (c["status"] or "") or c["approval"] == "Approved")
    planned = sum(1 for c in cis if (c["status"] or "").startswith("Planned"))
    dev = len(cis) - approved - planned

    crs = counts("SELECT status, COUNT(*) FROM change_requests GROUP BY status")
    builds = counts("SELECT result, COUNT(*) FROM builds GROUP BY result")
    probs = counts("SELECT status, COUNT(*) FROM problems GROUP BY status")
    promos = counts("SELECT result, COUNT(*) FROM promotions GROUP BY result")
    audits = counts("SELECT status, COUNT(*) FROM audit_observations GROUP BY status")
    
    tags = git("tag").split()
    latest_commit = git("rev-parse", "--short", "HEAD")
    current_branch = git("rev-parse", "--abbrev-ref", "HEAD")

    n = max(len(cis), 1)
    lines = [
        "=" * 72,
        "    COMMIT SLEUTH — CONFIGURATION STATUS ACCOUNTING REPORT (CSAR)",
        "=" * 72,
        f"Report ID        : CSAR-FINAL-REVIEW-001",
        f"Project          : CommitSleuth — Intelligent CI Failure Attribution",
        f"Course           : ISWE403L — Software Configuration Management",
        f"Generated At     : {datetime.datetime.now().strftime('%d %b %Y, %H:%M:%S')} (via status_reporter.py)",
        f"Source Branch    : {current_branch} @ {latest_commit}",
        "-" * 72,
        "1. CONFIGURATION ITEM (CI) STATUS ACCOUNTING",
        f"   Total CIs under Control      : {len(cis)}",
        f"   • Approved & Baselined       : {approved} ({approved * 100 // n}%)",
        f"   • In Development / Progress  : {dev} ({dev * 100 // n}%)",
        f"   • Planned / Pending          : {planned} ({planned * 100 // n}%)",
        "-" * 72,
        "2. CHANGE MANAGEMENT METRICS",
        f"   Total Change Requests Raised : {sum(crs.values())}",
        f"   • Implemented / Verified     : {crs.get('Implemented', 0)}",
        f"   • Approved (Pending Release) : {crs.get('Approved', 0)}",
        f"   • Under Review (CCB)         : {crs.get('Under Review', 0) + crs.get('Raised', 0)}",
        f"   • Rejected                   : {crs.get('Rejected', 0)}",
        "-" * 72,
        "3. CI/CD PIPELINE & QUALITY VERIFICATION",
        f"   Total Recorded Builds        : {sum(builds.values())}",
        f"   • Successful Builds          : {builds.get('SUCCESS', 0)}",
        f"   • Failed Builds              : {builds.get('FAILURE', 0)}",
        f"   • Unstable Builds            : {builds.get('UNSTABLE', 0)}",
        "-" * 72,
        "4. PROBLEM TRACKING & FAILURE ATTRIBUTION",
        f"   Total Problems Tracked       : {sum(probs.values())}",
        f"   • Open / Investigating       : {probs.get('Open', 0) + probs.get('Assigned', 0)}",
        f"   • Fixed & Verified           : {probs.get('Fixed', 0) + probs.get('Verified', 0)}",
        f"   • Closed                     : {probs.get('Closed', 0)}",
        "-" * 72,
        "5. PROMOTIONAL MANAGEMENT & RELEASES",
        f"   Total Promotion Decisions    : {sum(promos.values())}",
        f"   • PASSED (Promoted)          : {promos.get('PASSED', 0)}",
        f"   • BLOCKED (Quality Gate)     : {promos.get('BLOCKED', 0)}",
        f"   Git Release Tags             : {', '.join(tags) if tags else 'None'}",
        "-" * 72,
        "6. CONFIGURATION AUDITING SYSTEM (CAS) OBSERVATIONS",
        f"   Total Audit Observations     : {sum(audits.values())}",
        f"   • Closed Observations        : {audits.get('Closed', 0)}",
        f"   • Open / In-Progress         : {audits.get('Open', 0) + audits.get('In Progress', 0)}",
        "=" * 72,
        "End of Configuration Status Accounting Report."
    ]
    return "\n".join(lines)

def export_csar_csv():
    """Exports all Configuration Items with their current accounting details to CSV format."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["CI ID", "Configuration Item Name", "Version", "Lifecycle Status", "Owner", "Approval Status", "Baseline", "Category", "Last Modified"])
    for r in q("SELECT * FROM ci_register ORDER BY ci_id"):
        writer.writerow([r["ci_id"], r["name"], r["version"], r["status"], r["owner"], r["approval"], r["baseline"], r["category"], r["last_modified"]])
    return output.getvalue()

if __name__ == "__main__":
    report_text = build_csar()
    print(report_text)
    
    os.makedirs(os.path.join(ROOT, "reports"), exist_ok=True)
    report_file = os.path.join(ROOT, "reports", f"CSAR-{datetime.date.today():%Y%m%d}.txt")
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report_text + "\n")
    print(f"\nReport written to: {report_file}")

    csv_file = os.path.join(ROOT, "reports", f"CSAR-Register-{datetime.date.today():%Y%m%d}.csv")
    with open(csv_file, "w", encoding="utf-8", newline="") as f:
        f.write(export_csar_csv())
    print(f"CSV exported to: {csv_file}")
