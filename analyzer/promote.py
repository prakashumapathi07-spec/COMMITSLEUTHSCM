"""SCM Promotion Gate: Validates build quality, approved change requests, and authorization before promoting configuration items."""
import argparse
import datetime
import os
import re
import subprocess
import sys
from common import q, ex, log_audit, ROOT

def git(*args):
    res = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    return res.stdout.strip()

def evaluate_promotion(item="CommitSleuth Suite", frm="Development", to="Testing", approver="CCB", tests_passed=True, cr_id=None, tag=None):
    """
    Evaluates whether a configuration item can be promoted across levels.
    Returns: (is_passed: bool, reasons: list of str, record_id: int)
    """
    reasons = []
    
    # 1. Gate: Automated test verification
    if not tests_passed:
        reasons.append("Automated unit and integration tests have not passed")

    # 2. Gate: Traceable change request in HEAD commit
    head_msg = git("log", "--no-merges", "-1", "--pretty=%s")
    head_hash = git("rev-parse", "--short", "HEAD")
    m = re.search(r"(CR-\d+)", head_msg)
    detected_cr = cr_id or (m.group(1) if m else None)

    if not detected_cr:
        reasons.append(f"HEAD commit ({head_hash}) has no traceable Change Request ID (expected format CR-xxx)")
    else:
        row = q("SELECT status, decision FROM change_requests WHERE cr_id=?", (detected_cr,))
        if not row:
            reasons.append(f"Change Request {detected_cr} is not registered in the SCM Change Management Register")
        elif row[0]["status"] not in ("Approved", "Implemented"):
            reasons.append(f"Change Request {detected_cr} status is '{row[0]['status']}' (decision: '{row[0]['decision']}'), must be Approved or Implemented")

    # 3. Gate: Production promotion requires explicit admin approval
    if to == "Production" and approver in ("Viewer", "guest", "none"):
        reasons.append("Production promotion requires authorized Configuration Control Board (CCB) or Admin approval")

    result = "BLOCKED" if reasons else "PASSED"
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    reason_str = "; ".join(reasons) if reasons else "All SCM verification gates successfully satisfied"

    pid = ex(
        """INSERT INTO promotions (item, from_level, to_level, promo_date, approver, result, reason, release_tag)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (item, frm, to, now, approver, result, reason_str, tag)
    )

    log_audit(approver, f"Promotion Evaluation: {frm} -> {to}", f"Item: {item}, Result: {result}, Reasons: {reason_str}")
    return (result == "PASSED", reasons, pid)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SCM Promotion Gate Evaluator")
    parser.add_argument("--item", default="CommitSleuth demo app", help="Configuration item name")
    parser.add_argument("--from", dest="frm", required=True, help="Current promotion level (Development/Testing)")
    parser.add_argument("--to", required=True, help="Target promotion level (Testing/Production)")
    parser.add_argument("--approver", default="CCB", help="Approver username or board name")
    parser.add_argument("--tests-passed", action="store_true", help="Flag indicating automated test execution succeeded")
    parser.add_argument("--cr", default=None, help="Explicit Change Request ID")
    parser.add_argument("--tag", default=None, help="Associated release tag")
    args = parser.parse_args()

    passed, reasons, pid = evaluate_promotion(
        item=args.item,
        frm=args.frm,
        to=args.to,
        approver=args.approver,
        tests_passed=args.tests_passed,
        cr_id=args.cr,
        tag=args.tag
    )

    if passed:
        print(f"PROMOTION PASSED: {args.frm} -> {args.to} (Approved by {args.approver})")
        sys.exit(0)
    else:
        print(f"PROMOTION BLOCKED: {args.frm} -> {args.to}")
        for r in reasons:
            print(f"  - Gate Failure: {r}")
        sys.exit(1)
