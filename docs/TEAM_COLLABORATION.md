# CommitSleuth — Multi-Developer Collaborative SCM Workflow
**Course:** ISWE403L — Software Configuration Management (SCM)  
**Project:** An Intelligent Build Failure Attribution System for Continuous Integration Pipelines Using SCM  
**Repository:** [https://github.com/prakashumapathi07-spec/COMMITSLEUTHSCM.git](https://github.com/prakashumapathi07-spec/COMMITSLEUTHSCM.git)

---

## 1. Collaborative Team Structure (4 Members)

| Team Member | Registration No. | SCM Role | Email Address | Assigned Component |
|---|---|---|---|---|
| **Bharathwaraj K S** | 23MIS0070 | Lead Architect & Developer | `23mis0070@vitstudent.ac.in` | Input Validation & Build Architecture (`Validator.java`, `pom.xml`) |
| **Prakash Raj U** | 23MIS0180 | SCM Engineer & Developer (Primary Contributor) | `23mis0180@vitstudent.ac.in` | Core Business Logic & SCM Automation (`Calculator.java`, `scorer.py`) |
| **Arun Kumar** | 23MIS0245 | DevOps & SCM Maintainer | `arun.kumar2026@vitstudent.ac.in` | Scoring Configuration & CI Pipelines (`scoring_config.yaml`, `Jenkinsfile`) |
| **Kavya Sharma** | 23MIS0310 | QA Engineer & SCM Auditor | `kavya.sharma2026@vitstudent.ac.in` | Verification Suites & SCM Documentation (`docs/`, `ValidatorTest.java`) |

---

## 2. Multi-Developer Batch Commit Scenario

In high-throughput continuous integration environments, multiple developers commit changes concurrently during a development sprint. When multiple commits are batched into a single CI build run, an automated build failure requires intelligent Software Configuration Management to identify which specific developer's commit introduced the defect.

```
       [Branch: feature/multi-developer-collab]
          │
          ├─► Commit CR-010: Bharathwaraj K S (Validator.java)
          │
          ├─► Commit CR-011: Prakash Raj U (Calculator.java - DEFECT SEEDED)
          │
          ├─► Commit CR-012: Arun Kumar (scoring_config.yaml)
          │
          └─► Commit CR-013: Kavya Sharma (TEAM_COLLABORATION.md)
                    │
                    ▼
          [CI Build #102: FAILED]
          JUnit Failure: CalculatorTest.addsTwoNumbers()
                    │
                    ▼
          [CommitSleuth Attribution Engine]
          ┌────────────────────────────────────────────────────────┐
          │ 1. Prakash Raj U     | Score: 75.3% | CULPRIT (Rank #1)│
          │ 2. Bharathwaraj K S  | Score: 10.0% | Unlikely         │
          │ 3. Arun Kumar        | Score:  9.8% | Unlikely         │
          │ 4. Kavya Sharma      | Score:  4.9% | Unlikely         │
          └────────────────────────────────────────────────────────┘
                    │
                    ▼
          [Notification Sent to: 23mis0180@vitstudent.ac.in]
          [Problem Ticket P-001 Opened & Assigned to Prakash Raj U]
                    │
                    ▼
          Commit CR-014: Prakash Raj U alters Calculator.java (FIX SEEDED)
                    │
                    ▼
          [CI Build #103: PASSED (100% Green)]
          [Problem Ticket P-001 Status -> Closed]
          [Promotion Gate: Promoted to Production Baseline BL-05 / v1.0.0]
```

---

## 3. Commit Attribution Breakdown

| Developer | Commit ID | Files Changed | Lines Changed | Class Match ($W_f$) | POM Weight ($W_p$) | Recency ($W_r$) | Size ($W_s$) | Composite Score | Culpability Verdict |
|---|---|---|---|---|---|---|---|---|---|
| **Prakash Raj U** | `CR-011` | `Calculator.java` | +1, -1 | **1.0 (55.0%)** | 0.0 (0.0%) | 0.90 (9.0%) | 0.13 (1.3%) | **75.3%** | **Identified Culprit (Rank #1)** |
| **Bharathwaraj K S** | `CR-010` | `Validator.java`, `ValidatorTest.java` | +8, -0 | 0.0 (0.0%) | 0.0 (0.0%) | 0.80 (8.0%) | 0.20 (2.0%) | **10.0%** | Non-culpable (Unrelated Module) |
| **Arun Kumar** | `CR-012` | `scoring_config.yaml` | +6, -0 | 0.0 (0.0%) | 0.0 (0.0%) | 0.95 (9.5%) | 0.03 (0.3%) | **9.8%** | Non-culpable (Config Tuning) |
| **Kavya Sharma** | `CR-013` | `TEAM_COLLABORATION.md` | +45, -0 | 0.0 (0.0%) | 0.0 (0.0%) | 1.00 (10.0%) | 0.00 (0.0%) | **4.9%** | Non-culpable (Documentation) |

---

## 4. Problem Ticket & SCM Lifecycle

- **Problem ID:** `P-001`
- **Initial State:** `Open`
- **Assigned Developer:** `Prakash Raj U (23mis0180@vitstudent.ac.in)`
- **Resolution Commit:** `CR-014` (`commit ...`)
- **Verification Build:** `Build #103` (Passed)
- **Final SCM State:** `Closed`
