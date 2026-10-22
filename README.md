# CommitSleuth — Automated Build Failure Tracking & Developer Alert Platform

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Maven 3.9](https://img.shields.io/badge/Maven-3.9-C71A36.svg)](https://maven.apache.org/)
[![Jenkins CI](https://img.shields.io/badge/Jenkins-Declarative%20Pipeline-D24939.svg)](https://www.jenkins.io/)
[![Flask 3.1](https://img.shields.io/badge/Flask-3.1-000000.svg)](https://flask.palletsprojects.com/)
[![SQLite 3](https://img.shields.io/badge/SQLite-3.45-003B57.svg)](https://www.sqlite.org/)
[![pytest](https://img.shields.io/badge/pytest-22%20Passed-brightgreen.svg)]()
[![JUnit 5](https://img.shields.io/badge/JUnit-20%20Tests%20Passed-brightgreen.svg)]()
[![Java 17](https://img.shields.io/badge/JDK-17%20LTS-orange.svg)]()

> **Course:** ISWE403L — Software Configuration Management (SCM)  
> **Review:** SCM Final Review — Tool Implementation (Review-III)  
> **Institution:** School of Computer Science Engineering and Information Systems (SCOPE), Vellore Institute of Technology (VIT), Vellore  
> **Project Team Members:**  
> * **Bharathwaraj K S** — Register No: **23MIS0070**  
> * **Prakash Raj U** — Register No: **23MIS0180**  
> **Repository:** [https://github.com/prakashumapathi07-spec/COMMITSLEUTHSCM.git](https://github.com/prakashumapathi07-spec/COMMITSLEUTHSCM.git)

---

## 🏢 Scenario: TechNova Solutions (Employee Management System)

CommitSleuth demonstrates an enterprise DevOps failure tracking and SCM governance platform for a fictional engineering company called **TechNova Solutions**, where four developers collaborate on an **Employee Management System** across dedicated feature branches:

* **Prakash Raj** — Employee module — `feature/employee` (`EmployeeService.java`)
* **Bharathwaraj** — Authentication module — `feature/login` (`AuthService.java`)
* **Karthik** — Reports module — `feature/reports` (`ReportService.java`)
* **Divya** — Database module — `feature/database` (`DatabaseService.java`)

### Central Scenario:
1. **Defect Introduced:** Karthik introduces an intentional defect in `ReportService.java` under Change Request **CR-009** and pushes commit `a91bc42` to `feature/reports`.
2. **Build Break:** Jenkins triggers Build **#128** running `mvn test`. `ReportServiceTest` fails with `AssertionFailedError: expected <95000.0> but was <0.0>`.
3. **Automated Attribution:** CommitSleuth intercepts the failure, attributes it to Karthik with **88.5% confidence**, opens Problem **BUG-024**, and dispatches Alert **ALT-001**.
4. **Investigation & Fix:** Karthik inspects the terminal log and fix suggestions on `/failures/128`, acknowledges the alert, and submits corrective commit `c48fe19` (**CR-010**).
5. **Verified Resolution:** Build **#129** passes all 20 tests. BUG-024 is marked `Resolved`.
6. **Promotion Gate:** Promotion gate blocks Build #128 and approves Build #129 across Development $\rightarrow$ Testing $\rightarrow$ Release Candidate $\rightarrow$ Production.

---

## 🎨 UI/UX Design Direction

CommitSleuth is designed with a **Pure Light Theme** layout inspired by modern enterprise cloud dashboards:
* **Background:** Soft slate-50 (`#f8fafc`) with white card surfaces (`#ffffff`) and subtle borders (`#e2e8f0`).
* **Header & Navigation:** Sticky top header with project selector, repository badge, search input, unread alert counter, and instant scenario persona switcher.
* **Charts:** Interactive SVG Stacked Area Chart (Build Trends) and Stacked Bar Chart (Build Status by Module).
* **Investigation View:** Interactive line-numbered log terminal with colored PASS/FAIL markers, root-cause card, evidence breakdown, and syntax-highlighted fix suggestions.
* **Responsive:** Full desktop, tablet, and mobile support.

---

## 🚀 Quickstart Guide

### 1. Prerequisites
* **Python 3.10+**
* **Java SE JDK 17+**
* **Apache Maven 3.8+**
* **Git 2.40+**

### 2. Setup and Database Initialization
```powershell
# Clone repository
git clone https://github.com/prakashumapathi07-spec/COMMITSLEUTHSCM.git
cd COMMITSLEUTHSCM

# Install Python requirements
pip install -r requirements.txt

# Seed the TechNova scenario database
python database/seed.py --reset
```

### 3. Run Automated Tests
```powershell
# Run Python SCM test suite (22 tests)
pytest

# Run Java Maven test suite (20 unit tests)
mvn -B -f maven/pom.xml test
```

### 4. Launch the Web Application
```powershell
python dashboard/app.py
```
Open your browser to: **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

#### Persona Accounts:
* **Prakash Raj (Lead / Admin):** `prakash` / `admin123`
* **Bharathwaraj (Auth / Admin):** `bharath` / `admin123`
* **Karthik (Reports / Dev):** `karthik` / `maint123`
* **Divya (Database / Dev):** `divya` / `maint123`
* **SCM Auditor / Reviewer:** `viewer` / `viewer123`

---

## 📋 Complete SCM Activities Coverage

| SCM Activity | Implementation in CommitSleuth | Key File / Artifact |
|---|---|---|
| **Tool Implementation** | Jenkins declarative pipeline, Maven Surefire, Python attribution engine, Flask portal | `jenkins/Jenkinsfile`, `dashboard/app.py` |
| **Version Management** | Git feature branches (`feature/*`), tags (`v0.1.0`..`v1.0.0`), commit-msg hooks | `hooks/commit-msg`, `/versions` |
| **Change Management** | Formal CCB change requests (CR-001..CR-010) with impact and approval tracking | `database/schema.sql`, `/changes` |
| **Problem Tracking** | Automated defect lifecycle: `Open` $\rightarrow$ `Fix Submitted` $\rightarrow$ `Resolved` | `analyzer/record_build.py`, `/problems` |
| **Promotional Management** | Environment gates (Dev $\rightarrow$ Test $\rightarrow$ RC $\rightarrow$ Prod) blocking failed builds | `analyzer/promote.py`, `/releases` |
| **System Accounting** | CSAR report generation and live dynamic CSV export | `analyzer/status_reporter.py`, `/accounting` |
| **Configuration Audits (CAS)** | FCA (requirements verification) & PCA (checksum and manifest verification) | `audit_observations` table, `/audits` |
| **Access & Security** | Role-Based Access Control (Admin, Maintainer, Viewer) and immutable audit trail | `/settings`, `/audit-trail` |
| **Customization** | Configurable YAML ranking weights and CI server endpoints | `scoring_config.yaml`, `/settings` |
| **Web Enabling** | Fully responsive modern web portal | `dashboard/app.py` |

---

## 📌 Interactive Demo Workflow
Use the **Scenario Controller** in the sidebar:
1. Click **"1. Karthik Defect (#128)"** $\rightarrow$ Triggers failing build, opens BUG-024, dispatches alert.
2. Click **"2. Karthik Fix (#129)"** $\rightarrow$ Submits corrective commit c48fe19, passes 20/20 tests, resolves BUG-024, unlocks promotion to Production.
3. Click **"Reset State"** $\rightarrow$ Restores clean baseline database.
