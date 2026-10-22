"""Unit tests for the SCM Promotion Gate."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "analyzer"))
import promote

def test_promotion_blocked_when_tests_fail():
    passed, reasons, _ = promote.evaluate_promotion(
        item="Test Suite", frm="Development", to="Testing", approver="CCB",
        tests_passed=False, cr_id="CR-001"
    )
    assert not passed
    assert any("tests have not passed" in r for r in reasons)

def test_promotion_blocked_on_unapproved_cr():
    passed, reasons, _ = promote.evaluate_promotion(
        item="Test Suite", frm="Development", to="Testing", approver="CCB",
        tests_passed=True, cr_id="CR-008"  # CR-008 is Rejected
    )
    assert not passed
    assert any("Rejected" in r for r in reasons)

def test_promotion_passed_when_all_gates_met():
    passed, reasons, _ = promote.evaluate_promotion(
        item="Test Suite", frm="Development", to="Testing", approver="CCB",
        tests_passed=True, cr_id="CR-001"  # CR-001 is Implemented/Approved
    )
    assert passed
    assert len(reasons) == 0
