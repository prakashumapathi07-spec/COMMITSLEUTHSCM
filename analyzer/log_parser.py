"""Maven and Surefire build log parser for CommitSleuth.
Extracts failure types, error messages, affected files, line numbers, and test signatures.
"""
import re
import os

def parse_log(log_text):
    """
    Parses a build log string and returns a structured dictionary:
    {
        "failure_type": "compile" | "test" | "dependency" | "unknown",
        "error_message": str,
        "affected_file": str or None,
        "affected_test": str or None,
        "line_number": int or None,
        "relevant_tokens": list of str
    }
    """
    if not log_text:
        return {
            "failure_type": "unknown",
            "error_message": "Empty build log",
            "affected_file": None,
            "affected_test": None,
            "line_number": None,
            "relevant_tokens": []
        }

    # 1. Dependency Resolution Failure Check
    dep_match = re.search(r"(Could not resolve dependencies[^<\n\r]+|Could not find artifact[^<\n\r]+|Non-resolvable[^<\n\r]+)", log_text)
    if dep_match or "dependency:resolve" in log_text and "BUILD FAILURE" in log_text:
        msg = dep_match.group(1).strip() if dep_match else "Maven dependency resolution failure"
        return {
            "failure_type": "dependency",
            "error_message": msg,
            "affected_file": "pom.xml",
            "affected_test": None,
            "line_number": None,
            "relevant_tokens": ["pom.xml", "dependency", "pom"]
        }

    # 2. Compilation Failure Check
    if "COMPILATION ERROR" in log_text or re.search(r"\[ERROR\].*\.java:\[\d+,\d+\]", log_text):
        # Look for [ERROR] /path/to/File.java:[line,col] message
        comp_match = re.search(r"\[ERROR\]\s*(?:[A-Za-z]:[\\/]|/|[^\n\r]*[\\/])?([A-Za-z0-9_]+\.java):\[(\d+),\d+\]\s*(.*)", log_text)
        if comp_match:
            fname = comp_match.group(1)
            line_no = int(comp_match.group(2))
            err_msg = comp_match.group(3).strip()
            stem = os.path.splitext(fname)[0]
            return {
                "failure_type": "compile",
                "error_message": f"{fname}:{line_no} - {err_msg}",
                "affected_file": fname,
                "affected_test": None,
                "line_number": line_no,
                "relevant_tokens": [fname, stem]
            }
        # Fallback compilation error
        fallback_match = re.search(r"\[ERROR\]\s*Failed to execute goal org\.apache\.maven\.plugins:maven-compiler-plugin[^\n]+:\s*(.*)", log_text)
        msg = fallback_match.group(1).strip() if fallback_match else "Compilation failure in Java sources"
        return {
            "failure_type": "compile",
            "error_message": msg,
            "affected_file": None,
            "affected_test": None,
            "line_number": None,
            "relevant_tokens": ["compile", "java"]
        }

    # 3. Unit Test Failure Check (Surefire / JUnit)
    if "There are test failures" in log_text or "FAILURE" in log_text and "Tests run:" in log_text or re.search(r"\[ERROR\]\s*Failures:", log_text):
        # Look for surefire failure summary: [ERROR]   CalculatorTest.addsTwoNumbers:8 ==> expected: <5> but was: <6>
        test_fail_match = re.search(r"\[ERROR\]\s+([A-Za-z0-9_]+Test(?:\.[A-Za-z0-9_]+)?):?(\d+)?\s*(.*)", log_text)
        if not test_fail_match:
            test_fail_match = re.search(r"Running\s+([A-Za-z0-9_.]+Test)[\s\S]*?FAILURE", log_text)

        test_name = None
        affected_file = None
        tokens = ["test"]
        err_msg = "Surefire unit test assertion failure"

        if test_fail_match:
            full_test = test_fail_match.group(1).split(".")
            test_class = full_test[-2] if len(full_test) > 1 and full_test[-1] != "Test" else full_test[-1]
            test_method = full_test[-1] if len(full_test) > 1 and full_test[-1] != test_class else ""
            test_name = f"{test_class}.{test_method}" if test_method else test_class
            
            # If error message line exists:
            if len(test_fail_match.groups()) >= 3 and test_fail_match.group(3):
                err_msg = f"{test_name} - {test_fail_match.group(3).strip()}"
            else:
                err_msg = f"Unit test failure in {test_name}"

            # Infer source file: CalculatorTest -> Calculator.java
            source_stem = re.sub(r"Test$", "", test_class)
            affected_file = f"{source_stem}.java"
            tokens.extend([test_class, source_stem, f"{source_stem}.java", f"{test_class}.java"])

        return {
            "failure_type": "test",
            "error_message": err_msg,
            "affected_file": affected_file,
            "affected_test": test_name,
            "line_number": None,
            "relevant_tokens": tokens
        }

    return {
        "failure_type": "unknown",
        "error_message": "Uncategorized build failure detected in console output",
        "affected_file": None,
        "affected_test": None,
        "line_number": None,
        "relevant_tokens": []
    }
