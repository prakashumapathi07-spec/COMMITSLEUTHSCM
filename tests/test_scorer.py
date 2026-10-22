"""Unit tests for the Commit Ranking Engine and Attribution Scorer."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "analyzer"))
import scorer

CFG = {
    "weights": {"file_match": 0.55, "pom_change": 0.25, "recency": 0.10, "change_size": 0.10},
    "rollback": {"confidence_threshold": 0.60, "max_files_for_isolation": 3}
}

def test_file_in_log_ranks_first():
    commits = [
        {"hash": "a111", "author": "Prakash", "message": "CR-001: update calc", "files": ["Calculator.java"]},
        {"hash": "b222", "author": "Bharath", "message": "CR-002: update readme", "files": ["README.md"]}
    ]
    log = "[ERROR] Calculator.java:[9,31] error in syntax"
    r = scorer.rank(commits, log, "compile", CFG)
    assert r[0]["hash"] == "a111"
    assert r[0]["score"] > r[1]["score"]
    assert "Calculator.java" in r[0]["evidence_details"]

def test_confidence_sums_to_one():
    commits = [
        {"hash": f"hash_{i}", "author": "dev", "message": f"CR-00{i}: mod", "files": [f"file_{i}.java"]}
        for i in range(4)
    ]
    r = scorer.rank(commits, "file_1 file_2", "test", CFG)
    assert abs(sum(c["score"] for c in r) - 1.0) < 0.02

def test_test_name_correlates_to_source_file():
    commits = [
        {"hash": "c001", "author": "Prakash", "message": "CR-009: calc logic", "files": ["maven/src/main/java/com/commitsleuth/demo/Calculator.java"]},
        {"hash": "c002", "author": "Bharath", "message": "CR-007: docs", "files": ["docs/notes.md"]}
    ]
    log = "[ERROR]   CalculatorTest.addsTwoNumbers:8 ==> expected: <5> but was: <6>"
    r = scorer.rank(commits, log, "test", CFG)
    assert r[0]["hash"] == "c001"
    assert r[0]["attribution_status"] == "Probable Cause"

def test_pom_change_scored_on_dependency_failure():
    commits = [
        {"hash": "p001", "author": "Bharath", "message": "CR-003: pom update", "files": ["maven/pom.xml"]},
        {"hash": "p002", "author": "Prakash", "message": "CR-004: validator update", "files": ["Validator.java"]}
    ]
    log = "[ERROR] Could not resolve dependencies for project"
    r = scorer.rank(commits, log, "dependency", CFG)
    assert r[0]["hash"] == "p001"

def test_decide_rollback_isolated_vs_unisolated():
    isolated_top = {"hash": "c123", "score": 0.75, "files": ["Calculator.java"]}
    decision = scorer.decide(isolated_top, CFG)
    assert "Rollback recommended: git revert c123" in decision

    unisolated_top = {"hash": "c456", "score": 0.75, "files": ["A.java", "B.java", "C.java", "D.java"]}
    decision_unisolated = scorer.decide(unisolated_top, CFG)
    assert "touches 4 files" in decision_unisolated
