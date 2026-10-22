"""Unit tests for the CommitSleuth build log parser."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "analyzer"))
import log_parser

def test_parse_compilation_error():
    sample_log = """
    [INFO] --- compiler:3.13.0:compile (default-compile) @ demo-app ---
    [INFO] Compiling 2 source files
    [ERROR] /home/jenkins/workspace/maven/src/main/java/com/commitsleuth/demo/Calculator.java:[9,31] ';' expected
    [ERROR] -> [Help 1]
    [ERROR] COMPILATION ERROR :
    """
    res = log_parser.parse_log(sample_log)
    assert res["failure_type"] == "compile"
    assert res["affected_file"] == "Calculator.java"
    assert res["line_number"] == 9
    assert "Calculator.java" in res["error_message"]

def test_parse_surefire_test_failure():
    sample_log = """
    [INFO] Running com.commitsleuth.demo.CalculatorTest
    [ERROR] Failures: 
    [ERROR]   CalculatorTest.addsTwoNumbers:8 ==> expected: <5> but was: <6>
    [INFO] Results:
    [ERROR] Failures: 1, Errors: 0, Skipped: 0
    [ERROR] There are test failures.
    """
    res = log_parser.parse_log(sample_log)
    assert res["failure_type"] == "test"
    assert res["affected_file"] == "Calculator.java"
    assert res["affected_test"] == "CalculatorTest.addsTwoNumbers"
    assert "CalculatorTest" in res["relevant_tokens"]

def test_parse_dependency_failure():
    sample_log = """
    [INFO] Scanning for projects...
    [ERROR] Could not resolve dependencies for project com.commitsleuth:demo-app:jar:1.0.0: Could not find artifact org.junit.jupiter:junit-jupiter:jar:5.99.9
    [ERROR] BUILD FAILURE
    """
    res = log_parser.parse_log(sample_log)
    assert res["failure_type"] == "dependency"
    assert res["affected_file"] == "pom.xml"
