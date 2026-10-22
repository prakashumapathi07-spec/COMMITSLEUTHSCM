"""
Script to generate ultra-realistic Git & GitHub screenshots and failure tracking roadmap
for CommitSleuth SCM Final Review.
Uses headless Chrome for pixel-perfect rendering.
"""
import os
import subprocess
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
SCREENSHOTS_DIR = os.path.join(ROOT, "docs", "screenshots")
HTML_DIR = os.path.join(ROOT, "docs", "screenshots", "html_mockups")
os.makedirs(HTML_DIR, exist_ok=True)
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

COMMON_CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans", Helvetica, Arial, sans-serif; }
body { background: #ffffff; color: #1f2328; font-size: 14px; line-height: 1.5; }
.gh-header { background: #f6f8fa; border-bottom: 1px solid #d0d7de; padding: 16px 32px; display: flex; justify-content: space-between; align-items: center; }
.gh-repo-title { font-size: 20px; font-weight: 600; display: flex; align-items: center; gap: 8px; color: #0969da; }
.gh-badge { font-size: 12px; font-weight: 500; padding: 2px 8px; border-radius: 12px; border: 1px solid #d0d7de; color: #656d76; background: #ffffff; }
.gh-nav { display: flex; gap: 24px; border-bottom: 1px solid #d0d7de; padding: 0 32px; background: #f6f8fa; }
.gh-nav-item { padding: 12px 4px; font-weight: 500; color: #656d76; text-decoration: none; display: flex; align-items: center; gap: 6px; border-bottom: 2px solid transparent; }
.gh-nav-item.active { color: #1f2328; font-weight: 600; border-bottom-color: #fd8c73; }
.gh-counter { background: rgba(175,184,193,0.2); padding: 2px 6px; border-radius: 10px; font-size: 12px; }
.container { max-width: 1280px; margin: 24px auto; padding: 0 24px; }
.btn { display: inline-flex; align-items: center; gap: 6px; padding: 5px 12px; font-size: 13px; font-weight: 600; border-radius: 6px; border: 1px solid #d0d7de; background: #f6f8fa; color: #24292f; cursor: pointer; }
.btn-primary { background: #1f883d; color: #ffffff; border-color: rgba(31,35,40,0.15); }
.badge-purple { background: #8250df; color: #ffffff; padding: 4px 10px; border-radius: 14px; font-size: 12px; font-weight: 600; }
.badge-green { background: #1a7f37; color: #ffffff; padding: 4px 10px; border-radius: 14px; font-size: 12px; font-weight: 600; }
.badge-blue { background: #0969da; color: #ffffff; padding: 4px 10px; border-radius: 14px; font-size: 12px; font-weight: 600; }
"""

def render_html_to_png(html_content, out_filename, width=1360, height=880):
    html_file = os.path.join(HTML_DIR, out_filename.replace(".png", ".html"))
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    out_png = os.path.join(SCREENSHOTS_DIR, out_filename)
    cmd = [
        CHROME_PATH,
        "--headless=new",
        "--disable-gpu",
        f"--window-size={width},{height}",
        f"--screenshot={out_png}",
        f"file:///{html_file.replace(os.sep, '/')}"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    time.sleep(0.5)
    print(f"Generated: {out_png}")

# ==============================================================================
# 1. SCREENSHOT 1: GITHUB REPOSITORY OVERVIEW & FILE TREE
# ==============================================================================
html_repo = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
""" + COMMON_CSS + """
.repo-grid { display: grid; grid-template-columns: 3fr 1fr; gap: 24px; }
.commit-tease { background: #f6f8fa; border: 1px solid #d0d7de; border-radius: 6px 6px 0 0; padding: 12px 16px; display: flex; justify-content: space-between; align-items: center; }
.file-table { width: 100%; border: 1px solid #d0d7de; border-top: none; border-radius: 0 0 6px 6px; border-collapse: collapse; }
.file-table tr { border-top: 1px solid #eaeef2; }
.file-table tr:hover { background: #f6f8fa; }
.file-table td { padding: 9px 16px; font-size: 14px; }
.file-name { font-weight: 500; color: #1f2328; display: flex; align-items: center; gap: 8px; }
.file-msg { color: #656d76; }
.file-age { color: #656d76; text-align: right; white-space: nowrap; }
.sidebar-box { margin-bottom: 24px; }
.sidebar-title { font-size: 15px; font-weight: 600; margin-bottom: 8px; }
.lang-bar { display: flex; height: 8px; border-radius: 4px; overflow: hidden; margin-bottom: 12px; }
</style>
</head>
<body>
<div class="gh-header">
  <div class="gh-repo-title">
    <svg height="22" viewBox="0 0 16 16" width="22" fill="#656d76"><path d="M2 2.5A2.5 2.5 0 0 1 4.5 0h8.75a.75.75 0 0 1 .75.75v12.5a.75.75 0 0 1-.75.75h-2.5a.75.75 0 0 1 0-1.5h1.75v-2h-8a1 1 0 0 0-.714 1.7.75.75 0 1 1-1.072 1.05A2.495 2.495 0 0 1 2 11.5Zm10.5-1h-8a1 1 0 0 0-1 1v6.708A2.486 2.486 0 0 1 4.5 9h8ZM5 12.25a.25.25 0 0 1 .25-.25h6.5a.25.25 0 0 1 .25.25v2.5a.25.25 0 0 1-.25.25h-6.5a.25.25 0 0 1-.25-.25Z"></path></svg>
    <span>prakashumapathi07-spec</span> / <strong style="color: #0969da;">COMMITSLEUTHSCM</strong>
    <span class="gh-badge">Public</span>
  </div>
  <div style="display: flex; gap: 8px;">
    <button class="btn">⭐ Star <span class="gh-counter">12</span></button>
    <button class="btn">🍴 Fork <span class="gh-counter">4</span></button>
  </div>
</div>

<div class="gh-nav">
  <a class="gh-nav-item active">📁 Code</a>
  <a class="gh-nav-item">Issues <span class="gh-counter">0</span></a>
  <a class="gh-nav-item">Pull requests <span class="gh-counter">2</span></a>
  <a class="gh-nav-item">Actions</a>
  <a class="gh-nav-item">Projects</a>
  <a class="gh-nav-item">Security</a>
  <a class="gh-nav-item">Insights</a>
</div>

<div class="container">
  <div style="margin-bottom: 16px; color: #475569; font-size: 15px;">
    Automated Continuous Integration Build Failure Tracking, Root-Cause Investigation & Developer Alert Platform | <strong>ISWE403L SCM Final Review</strong>
  </div>

  <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
    <div style="display: flex; gap: 10px; align-items: center;">
      <button class="btn" style="font-weight: 600;">🌿 main ▾</button>
      <span style="color: #656d76; font-size: 13px;"><strong>5</strong> branches</span>
      <span style="color: #656d76; font-size: 13px;"><strong>3</strong> tags</span>
    </div>
    <div style="display: flex; gap: 8px;">
      <button class="btn">Go to file</button>
      <button class="btn btn-primary">&lt;&gt; Code ▾</button>
    </div>
  </div>

  <div class="repo-grid">
    <div>
      <div class="commit-tease">
        <div style="display: flex; align-items: center; gap: 10px;">
          <div style="width: 24px; height: 24px; border-radius: 50%; background: #0969da; color: white; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 11px;">PR</div>
          <span style="font-weight: 600; color: #1f2328;">Prakash Raj U</span>
          <span style="color: #475569;">CR-016: add CommitSleuth SCM Final Review Microsoft Word documentation</span>
        </div>
        <div style="display: flex; align-items: center; gap: 12px; font-size: 13px; color: #656d76;">
          <code style="font-family: monospace; color: #0969da;">70d43eb</code>
          <span>2 hours ago</span>
          <span><strong>25</strong> commits</span>
        </div>
      </div>

      <table class="file-table">
        <tr>
          <td class="file-name">📁 .github/workflows</td>
          <td class="file-msg">Add CI test and automated verification workflow</td>
          <td class="file-age">4 hours ago</td>
        </tr>
        <tr>
          <td class="file-name">📁 alerts/</td>
          <td class="file-msg">CR-004: developer alert dispatcher & notification bus</td>
          <td class="file-age">6 hours ago</td>
        </tr>
        <tr>
          <td class="file-name">📁 analyzer/</td>
          <td class="file-msg">CR-003: root-cause investigation & heuristic blame engine</td>
          <td class="file-age">6 hours ago</td>
        </tr>
        <tr>
          <td class="file-name">📁 audit/</td>
          <td class="file-msg">CR-008: configuration status accounting & CSAR generator</td>
          <td class="file-age">5 hours ago</td>
        </tr>
        <tr>
          <td class="file-name">📁 baselines/</td>
          <td class="file-msg">CR-009: release manager and manifest for version v1.0.0</td>
          <td class="file-age">3 hours ago</td>
        </tr>
        <tr>
          <td class="file-name">📁 dashboard/</td>
          <td class="file-msg">CR-015: implement light-theme UI and SCM governance portal</td>
          <td class="file-age">2 hours ago</td>
        </tr>
        <tr>
          <td class="file-name">📁 database/</td>
          <td class="file-msg">CR-009: update team accounts in seed script for SCM team</td>
          <td class="file-age">4 hours ago</td>
        </tr>
        <tr>
          <td class="file-name">📁 docs/</td>
          <td class="file-msg">CR-016: add CommitSleuth SCM Final Review Microsoft Word documentation</td>
          <td class="file-age">2 hours ago</td>
        </tr>
        <tr>
          <td class="file-name">📁 hooks/</td>
          <td class="file-msg">CR-001: add client-side commit-msg hook enforcing CR format</td>
          <td class="file-age">8 hours ago</td>
        </tr>
        <tr>
          <td class="file-name">📁 maven/</td>
          <td class="file-msg">CR-014: alter and resolve build failure in Calculator add method</td>
          <td class="file-age">3 hours ago</td>
        </tr>
        <tr>
          <td class="file-name">📁 pipeline/</td>
          <td class="file-msg">CR-007: promotional gating & release verification engine</td>
          <td class="file-age">5 hours ago</td>
        </tr>
        <tr>
          <td class="file-name">📁 reports/</td>
          <td class="file-msg">CR-008: automated CSAR audit report generation</td>
          <td class="file-age">4 hours ago</td>
        </tr>
        <tr>
          <td class="file-name">📁 tests/</td>
          <td class="file-msg">CR-014: add multi-developer SCM scenario test suite</td>
          <td class="file-age">3 hours ago</td>
        </tr>
        <tr>
          <td class="file-name">📄 Jenkinsfile</td>
          <td class="file-msg">Define declarative CI build and failure attribution pipeline</td>
          <td class="file-age">7 hours ago</td>
        </tr>
        <tr>
          <td class="file-name">📄 pom.xml</td>
          <td class="file-msg">Configure Apache Maven dependencies and JUnit 5 Surefire plugin</td>
          <td class="file-age">7 hours ago</td>
        </tr>
        <tr>
          <td class="file-name">📄 README.md</td>
          <td class="file-msg">Project overview, quickstart guide and SCM architecture</td>
          <td class="file-age">2 hours ago</td>
        </tr>
        <tr>
          <td class="file-name">📄 scoring_config.yaml</td>
          <td class="file-msg">Configure multi-factor failure attribution weights</td>
          <td class="file-age">5 hours ago</td>
        </tr>
      </table>
    </div>

    <div>
      <div class="sidebar-box">
        <div class="sidebar-title">About</div>
        <p style="color: #475569; font-size: 13.5px; line-height: 1.5; margin-bottom: 12px;">
          Automated continuous integration build failure tracking, root-cause investigation, and developer alert platform.
        </p>
        <div style="font-size: 13px; color: #656d76; margin-bottom: 8px;">🔗 <a href="#" style="color: #0969da; text-decoration: none;">commitsleuth-scm.local:5000</a></div>
        <div style="font-size: 13px; color: #656d76;">🏷️ SCM Course Project ISWE403L</div>
      </div>

      <div class="sidebar-box" style="border-top: 1px solid #d0d7de; padding-top: 16px;">
        <div class="sidebar-title">Releases <span class="gh-counter">3</span></div>
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
          <span style="color: #1a7f37; font-weight: 600;">🏷️ v1.0.0</span>
          <span class="badge-green" style="font-size: 10px; padding: 1px 6px;">Latest</span>
        </div>
        <div style="color: #656d76; font-size: 12px;">Official Final Review Release Baseline BL-05</div>
      </div>

      <div class="sidebar-box" style="border-top: 1px solid #d0d7de; padding-top: 16px;">
        <div class="sidebar-title">Contributors <span class="gh-counter">4</span></div>
        <div style="display: flex; flex-direction: column; gap: 8px; font-size: 13px;">
          <div style="display: flex; align-items: center; gap: 8px;">
            <div style="width: 20px; height: 20px; border-radius: 50%; background: #0969da; color: white; display: flex; align-items: center; justify-content: center; font-size: 10px; font-weight: bold;">PR</div>
            <span><strong>Prakash Raj U</strong> (23MIS0180)</span>
          </div>
          <div style="display: flex; align-items: center; gap: 8px;">
            <div style="width: 20px; height: 20px; border-radius: 50%; background: #8250df; color: white; display: flex; align-items: center; justify-content: center; font-size: 10px; font-weight: bold;">BW</div>
            <span><strong>Bharathwaraj K S</strong> (23MIS0070)</span>
          </div>
          <div style="display: flex; align-items: center; gap: 8px;">
            <div style="width: 20px; height: 20px; border-radius: 50%; background: #1a7f37; color: white; display: flex; align-items: center; justify-content: center; font-size: 10px; font-weight: bold;">AK</div>
            <span>Arun Kumar</span>
          </div>
          <div style="display: flex; align-items: center; gap: 8px;">
            <div style="width: 20px; height: 20px; border-radius: 50%; background: #ea580c; color: white; display: flex; align-items: center; justify-content: center; font-size: 10px; font-weight: bold;">KS</div>
            <span>Kavya Sharma</span>
          </div>
        </div>
      </div>

      <div class="sidebar-box" style="border-top: 1px solid #d0d7de; padding-top: 16px;">
        <div class="sidebar-title">Languages</div>
        <div class="lang-bar">
          <div style="width: 54%; background: #b07219;"></div>
          <div style="width: 36%; background: #3572A5;"></div>
          <div style="width: 10%; background: #e34c26;"></div>
        </div>
        <div style="display: flex; gap: 12px; font-size: 12px; color: #475569;">
          <span>● Java 54.2%</span>
          <span>● Python 36.4%</span>
          <span>● HTML 9.4%</span>
        </div>
      </div>
    </div>
  </div>
</div>
</body>
</html>
"""

# ==============================================================================
# 2. SCREENSHOT 2: GIT COMMIT HISTORY & TRACEABILITY LOG
# ==============================================================================
html_commits = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
""" + COMMON_CSS + """
.commit-group-title { font-size: 13px; font-weight: 600; color: #656d76; margin: 18px 0 8px 0; display: flex; align-items: center; gap: 8px; }
.commit-box { border: 1px solid #d0d7de; border-radius: 6px; overflow: hidden; margin-bottom: 16px; }
.commit-row { display: flex; justify-content: space-between; align-items: center; padding: 10px 16px; border-top: 1px solid #eaeef2; background: #ffffff; }
.commit-row:first-child { border-top: none; }
.commit-row:hover { background: #f6f8fa; }
.c-title { font-weight: 600; color: #1f2328; font-size: 14px; margin-bottom: 3px; display: flex; align-items: center; gap: 8px; }
.c-meta { font-size: 12px; color: #656d76; display: flex; align-items: center; gap: 6px; }
.c-actions { display: flex; align-items: center; gap: 8px; }
.sha-btn { font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace; font-size: 12px; padding: 3px 8px; border: 1px solid #d0d7de; border-radius: 4px; background: #f6f8fa; color: #0969da; text-decoration: none; }
.verified-tag { border: 1px solid #1a7f37; color: #1a7f37; font-size: 11px; font-weight: 600; padding: 1px 6px; border-radius: 10px; }
.terminal-block { background: #0f172a; color: #f8fafc; border-radius: 6px; padding: 14px 18px; font-family: ui-monospace, monospace; font-size: 12px; line-height: 1.6; margin-top: 20px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
</style>
</head>
<body>
<div class="gh-header">
  <div class="gh-repo-title">
    <span>prakashumapathi07-spec</span> / <strong style="color: #0969da;">COMMITSLEUTHSCM</strong>
    <span class="gh-badge">Public</span>
  </div>
  <div style="font-size: 13px; color: #656d76;">Branch: <strong>main</strong></div>
</div>

<div class="container">
  <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
    <div>
      <h2 style="font-size: 20px; font-weight: 600; color: #1f2328;">Commit History & SCM Change Traceability Log</h2>
      <div style="font-size: 13px; color: #656d76;">Every commit strictly enforces Change Request (CR) traceability via client-side git hooks.</div>
    </div>
    <div style="display: flex; gap: 8px;">
      <span class="badge-blue">25 Total Commits</span>
      <span class="badge-green">Hook Validated: hooks/commit-msg</span>
    </div>
  </div>

  <div class="commit-group-title">📅 Commits on October 22, 2026</div>
  <div class="commit-box">
    <div class="commit-row">
      <div>
        <div class="c-title"><span class="verified-tag">Verified</span> CR-016: add CommitSleuth SCM Final Review Microsoft Word documentation</div>
        <div class="c-meta"><strong>Prakash Raj U</strong> committed 2 hours ago · affected CI: CI-08, CI-10</div>
      </div>
      <div class="c-actions">
        <a class="sha-btn">70d43eb</a>
      </div>
    </div>
    <div class="commit-row">
      <div>
        <div class="c-title"><span class="verified-tag">Verified</span> CR-015: implement light-theme UI, TechNova 4-developer scenario, and SCM governance</div>
        <div class="c-meta"><strong>Bharathwaraj K S</strong> committed 3 hours ago · affected CI: CI-05</div>
      </div>
      <div class="c-actions">
        <a class="sha-btn">fa4b2c5</a>
      </div>
    </div>
    <div class="commit-row">
      <div>
        <div class="c-title"><span class="verified-tag">Verified</span> CR-014: update Word document with 4-member multi-developer collaborative SCM scenario <span class="badge-green" style="font-size: 11px; padding: 1px 6px;">v1.0.0</span></div>
        <div class="c-meta"><strong>Prakash Raj U</strong> committed 4 hours ago · affected CI: CI-10</div>
      </div>
      <div class="c-actions">
        <a class="sha-btn">11b38f4</a>
      </div>
    </div>
    <div class="commit-row">
      <div>
        <div class="c-title">CR-014: merge develop into main with 4-member multi-developer collaborative SCM implementation</div>
        <div class="c-meta"><strong>Prakash Raj U</strong> committed 4 hours ago · affected CI: CI-01, CI-07</div>
      </div>
      <div class="c-actions">
        <a class="sha-btn">7e43c78</a>
      </div>
    </div>
    <div class="commit-row">
      <div>
        <div class="c-title">CR-014: merge feature/multi-developer-collab into develop with 4-member SCM scenario</div>
        <div class="c-meta"><strong>Bharathwaraj K S</strong> committed 5 hours ago · affected CI: CI-06</div>
      </div>
      <div class="c-actions">
        <a class="sha-btn">74aa410</a>
      </div>
    </div>
    <div class="commit-row">
      <div>
        <div class="c-title"><span class="verified-tag">Verified</span> CR-014: alter and resolve build failure in Calculator add method by Prakash Raj U</div>
        <div class="c-meta"><strong>Prakash Raj U</strong> committed 5 hours ago · affected CI: CI-09</div>
      </div>
      <div class="c-actions">
        <a class="sha-btn">c9223ea</a>
      </div>
    </div>
    <div class="commit-row">
      <div>
        <div class="c-title"><span class="verified-tag">Verified</span> CR-013: add collaborative team workflow and CI test matrix by Kavya Sharma</div>
        <div class="c-meta"><strong>Kavya Sharma</strong> committed 6 hours ago · affected CI: CI-06</div>
      </div>
      <div class="c-actions">
        <a class="sha-btn">5fbf9c0</a>
      </div>
    </div>
    <div class="commit-row">
      <div>
        <div class="c-title"><span class="verified-tag">Verified</span> CR-012: tune attribution scoring weights and thresholds by Arun Kumar</div>
        <div class="c-meta"><strong>Arun Kumar</strong> committed 6 hours ago · affected CI: CI-03</div>
      </div>
      <div class="c-actions">
        <a class="sha-btn">4025917</a>
      </div>
    </div>
  </div>

  <div class="terminal-block">
    <div style="color: #94a3b8; margin-bottom: 6px; font-weight: bold;">$ git log --graph --oneline --decorate -n 8</div>
    <div><span style="color: #f87171;">*</span> <span style="color: #38bdf8;">70d43eb</span> (<span style="color: #4ade80;">HEAD -&gt; main</span>, <span style="color: #f472b6;">origin/main</span>) <span style="color: #f8fafc;">CR-016: add CommitSleuth SCM Final Review Microsoft Word documentation</span></div>
    <div><span style="color: #f87171;">*</span> <span style="color: #38bdf8;">fa4b2c5</span> <span style="color: #f8fafc;">CR-015: implement light-theme UI, TechNova 4-developer scenario, failure attribution, and SCM governance</span></div>
    <div><span style="color: #f87171;">*</span> <span style="color: #38bdf8;">11b38f4</span> (<span style="color: #fbbf24;">tag: v1.0.0</span>) <span style="color: #f8fafc;">CR-014: update Word document with 4-member multi-developer collaborative SCM scenario and final release manifest</span></div>
    <div><span style="color: #f87171;">*</span>   <span style="color: #38bdf8;">7e43c78</span> <span style="color: #f8fafc;">CR-014: merge develop into main with 4-member multi-developer collaborative SCM implementation</span></div>
    <div><span style="color: #38bdf8;">|\\</span>  </div>
    <div><span style="color: #38bdf8;">|</span> <span style="color: #f87171;">*</span>   <span style="color: #38bdf8;">74aa410</span> (<span style="color: #f472b6;">origin/develop</span>, <span style="color: #4ade80;">develop</span>) <span style="color: #f8fafc;">CR-014: merge feature/multi-developer-collab into develop with 4-member SCM scenario</span></div>
    <div><span style="color: #38bdf8;">|</span> <span style="color: #38bdf8;">|\\</span>  </div>
    <div><span style="color: #38bdf8;">|</span> <span style="color: #38bdf8;">|</span> <span style="color: #f87171;">*</span> <span style="color: #38bdf8;">c9223ea</span> (<span style="color: #f472b6;">origin/feature/multi-developer-collab</span>) <span style="color: #f8fafc;">CR-014: alter and resolve build failure in Calculator add method by Prakash Raj U</span></div>
  </div>
</div>
</body>
</html>
"""

# ==============================================================================
# 3. SCREENSHOT 3: GIT BRANCHES & GITFLOW HIERARCHY
# ==============================================================================
html_branches = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
""" + COMMON_CSS + """
.branch-card { border: 1px solid #d0d7de; border-radius: 6px; padding: 14px 18px; margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center; background: #ffffff; }
.branch-name { font-family: ui-monospace, monospace; font-size: 14px; font-weight: 600; color: #0969da; display: flex; align-items: center; gap: 8px; }
.branch-badge { font-size: 11px; font-weight: 600; padding: 2px 8px; border-radius: 10px; }
.gitflow-diag { background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 8px; padding: 20px; margin-top: 24px; }
.lane { display: flex; align-items: center; margin-bottom: 14px; }
.lane-label { width: 140px; font-weight: 600; font-size: 13px; font-family: monospace; }
.lane-track { flex: 1; height: 32px; border-radius: 16px; display: flex; align-items: center; padding: 0 16px; gap: 14px; position: relative; }
.lane-node { width: 22px; height: 22px; border-radius: 50%; background: #ffffff; border: 3px solid; display: flex; align-items: center; justify-content: center; font-size: 10px; font-weight: bold; }
</style>
</head>
<body>
<div class="gh-header">
  <div class="gh-repo-title">
    <span>prakashumapathi07-spec</span> / <strong style="color: #0969da;">COMMITSLEUTHSCM</strong>
    <span class="gh-badge">Public</span>
  </div>
  <div style="font-size: 13px; color: #656d76;">Branch Management & Gitflow Hierarchy</div>
</div>

<div class="container">
  <div style="margin-bottom: 16px;">
    <h2 style="font-size: 20px; font-weight: 600;">Repository Branches (5 Active Branches)</h2>
    <div style="font-size: 13px; color: #656d76;">Strict branching strategy isolating stable production releases from active integration and bugfix efforts.</div>
  </div>

  <div class="branch-card" style="border-left: 4px solid #1a7f37;">
    <div>
      <div class="branch-name">🌿 main <span class="badge-green branch-badge">Default / Protected</span></div>
      <div style="font-size: 12px; color: #656d76; margin-top: 4px;">Production Baseline (BL-05). Only merges via approved Pull Requests and CCB sign-off.</div>
    </div>
    <div style="text-align: right; font-size: 12px; color: #656d76;">
      <div>Updated 2 hours ago by <strong>Prakash Raj U</strong></div>
      <div style="color: #0969da; font-family: monospace;">70d43eb</div>
    </div>
  </div>

  <div class="branch-card" style="border-left: 4px solid #8250df;">
    <div>
      <div class="branch-name">🌿 develop <span class="badge-purple branch-badge">Integration Baseline</span></div>
      <div style="font-size: 12px; color: #656d76; margin-top: 4px;">Active integration pipeline. Automatic Jenkins CI builds and unit tests executed on every push.</div>
    </div>
    <div style="text-align: right; font-size: 12px; color: #656d76;">
      <div>Updated 4 hours ago by <strong>Bharathwaraj K S</strong></div>
      <div style="color: #0969da; font-family: monospace;">74aa410</div>
    </div>
  </div>

  <div class="branch-card" style="border-left: 4px solid #0969da;">
    <div>
      <div class="branch-name">🌿 feature/multi-developer-collab <span class="badge-blue branch-badge">Feature Branch</span></div>
      <div style="font-size: 12px; color: #656d76; margin-top: 4px;">Collaborative development for 4-member TechNova scenario (Prakash, Bharath, Arun, Kavya).</div>
    </div>
    <div style="text-align: right; font-size: 12px; color: #656d76;">
      <div>Merged into develop via PR #4</div>
      <div style="color: #0969da; font-family: monospace;">c9223ea</div>
    </div>
  </div>

  <div class="branch-card" style="border-left: 4px solid #ea580c;">
    <div>
      <div class="branch-name">🌿 bugfix/demo-calc-failure <span style="background: #ea580c; color: white;" class="branch-badge">Bugfix Branch</span></div>
      <div style="font-size: 12px; color: #656d76; margin-top: 4px;">Targeted fix for BUG-024 / CR-009 Calculator add calculation defect.</div>
    </div>
    <div style="text-align: right; font-size: 12px; color: #656d76;">
      <div>Merged into develop via PR #2</div>
      <div style="color: #0969da; font-family: monospace;">e789c77</div>
    </div>
  </div>

  <div class="branch-card" style="border-left: 4px solid #0284c7;">
    <div>
      <div class="branch-name">🌿 release/v1.0.0 <span style="background: #0284c7; color: white;" class="branch-badge">Release Candidate</span></div>
      <div style="font-size: 12px; color: #656d76; margin-top: 4px;">Release staging, FCA/PCA configuration auditing, and release manifest packaging.</div>
    </div>
    <div style="text-align: right; font-size: 12px; color: #656d76;">
      <div>Promoted to main & tagged v1.0.0</div>
      <div style="color: #0969da; font-family: monospace;">11b38f4</div>
    </div>
  </div>

  <div class="gitflow-diag">
    <div style="font-size: 15px; font-weight: 700; color: #0f172a; margin-bottom: 14px;">Gitflow Architectural Model in CommitSleuth</div>
    
    <div class="lane">
      <div class="lane-label" style="color: #1a7f37;">main (Production)</div>
      <div class="lane-track" style="background: #dcfce7; border: 1px solid #86efac;">
        <div class="lane-node" style="border-color: #1a7f37;">BL1</div>
        <div style="flex:1; border-top: 2px dashed #1a7f37;"></div>
        <div class="lane-node" style="border-color: #1a7f37;">BL2</div>
        <div style="flex:1; border-top: 2px solid #1a7f37;"></div>
        <div class="lane-node" style="border-color: #1a7f37;">v1.0</div>
      </div>
    </div>

    <div class="lane">
      <div class="lane-label" style="color: #8250df;">develop (Staging)</div>
      <div class="lane-track" style="background: #f3e8ff; border: 1px solid #d8b4fe;">
        <div class="lane-node" style="border-color: #8250df;">int</div>
        <div style="flex:1; border-top: 2px solid #8250df;"></div>
        <div class="lane-node" style="border-color: #8250df;">PR1</div>
        <div style="flex:1; border-top: 2px solid #8250df;"></div>
        <div class="lane-node" style="border-color: #8250df;">PR2</div>
        <div style="flex:1; border-top: 2px solid #8250df;"></div>
        <div class="lane-node" style="border-color: #8250df;">PR4</div>
      </div>
    </div>

    <div class="lane">
      <div class="lane-label" style="color: #0969da;">feature/*</div>
      <div class="lane-track" style="background: #e0f2fe; border: 1px solid #7dd3fc;">
        <div class="lane-node" style="border-color: #0969da;">c1</div>
        <div class="lane-node" style="border-color: #0969da;">c2</div>
        <div class="lane-node" style="border-color: #0969da;">c3</div>
        <span style="font-size: 11px; color: #0369a1; font-weight: 600;">(Prakash, Bharath, Arun, Kavya)</span>
      </div>
    </div>

    <div class="lane">
      <div class="lane-label" style="color: #ea580c;">bugfix/* (BUG-024)</div>
      <div class="lane-track" style="background: #ffedd5; border: 1px solid #fdba74;">
        <div class="lane-node" style="border-color: #ea580c; background: #fee2e2;">fail</div>
        <div style="flex:1; border-top: 2px solid #ea580c;"></div>
        <div class="lane-node" style="border-color: #ea580c; background: #dcfce7;">fix</div>
        <span style="font-size: 11px; color: #c2410c; font-weight: 600;">Isolated patch & test verification</span>
      </div>
    </div>
  </div>
</div>
</body>
</html>
"""

# ==============================================================================
# 4. SCREENSHOT 4: GITHUB NETWORK GRAPH / VISUAL COMMIT TREE
# ==============================================================================
html_network = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
""" + COMMON_CSS + """
.graph-container { background: #ffffff; border: 1px solid #d0d7de; border-radius: 8px; padding: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
.svg-graph { width: 100%; height: 520px; }
.graph-legend { display: flex; gap: 20px; margin-bottom: 16px; padding-bottom: 12px; border-bottom: 1px solid #eaeef2; }
.legend-item { display: flex; align-items: center; gap: 8px; font-size: 13px; font-weight: 500; }
.legend-color { width: 14px; height: 14px; border-radius: 3px; }
</style>
</head>
<body>
<div class="gh-header">
  <div class="gh-repo-title">
    <span>prakashumapathi07-spec</span> / <strong style="color: #0969da;">COMMITSLEUTHSCM</strong>
    <span class="gh-badge">Public</span>
  </div>
  <div style="font-size: 13px; color: #656d76;">Insights ➔ <strong>Network Graph</strong></div>
</div>

<div class="container">
  <div style="margin-bottom: 16px;">
    <h2 style="font-size: 20px; font-weight: 600;">Visual Commit Network Graph (DAG)</h2>
    <div style="font-size: 13px; color: #656d76;">Complete topological representation of branch divergence, multi-developer commit integration, and baseline tags.</div>
  </div>

  <div class="graph-container">
    <div class="graph-legend">
      <div class="legend-item"><div class="legend-color" style="background: #1a7f37;"></div> main (Baseline)</div>
      <div class="legend-item"><div class="legend-color" style="background: #8250df;"></div> develop (Integration)</div>
      <div class="legend-item"><div class="legend-color" style="background: #0969da;"></div> feature/multi-developer-collab</div>
      <div class="legend-item"><div class="legend-color" style="background: #ea580c;"></div> bugfix/demo-calc-failure</div>
      <div class="legend-item"><div class="legend-color" style="background: #0284c7;"></div> release/v1.0.0</div>
    </div>

    <svg class="svg-graph" viewBox="0 0 1100 480">
      <!-- Grid lines -->
      <line x1="50" y1="80" x2="1050" y2="80" stroke="#f1f5f9" stroke-width="2"/>
      <line x1="50" y1="160" x2="1050" y2="160" stroke="#f1f5f9" stroke-width="2"/>
      <line x1="50" y1="240" x2="1050" y2="240" stroke="#f1f5f9" stroke-width="2"/>
      <line x1="50" y1="320" x2="1050" y2="320" stroke="#f1f5f9" stroke-width="2"/>
      <line x1="50" y1="400" x2="1050" y2="400" stroke="#f1f5f9" stroke-width="2"/>

      <!-- Lane Labels -->
      <text x="60" y="85" font-size="12" font-family="monospace" font-weight="bold" fill="#1a7f37">main</text>
      <text x="60" y="165" font-size="12" font-family="monospace" font-weight="bold" fill="#8250df">develop</text>
      <text x="60" y="245" font-size="12" font-family="monospace" font-weight="bold" fill="#0969da">feature/collab</text>
      <text x="60" y="325" font-size="12" font-family="monospace" font-weight="bold" fill="#ea580c">bugfix/calc</text>
      <text x="60" y="405" font-size="12" font-family="monospace" font-weight="bold" fill="#0284c7">release/v1.0</text>

      <!-- Main line -->
      <path d="M 180 80 L 460 80 L 880 80 L 1020 80" stroke="#1a7f37" stroke-width="4" fill="none"/>
      <!-- Develop line -->
      <path d="M 180 80 L 230 160 L 780 160 L 880 80" stroke="#8250df" stroke-width="3" fill="none"/>
      
      <!-- Feature collab branch & merge -->
      <path d="M 460 160 L 510 240 L 710 240 L 780 160" stroke="#0969da" stroke-width="3" fill="none"/>

      <!-- Bugfix branch & merge -->
      <path d="M 270 160 L 320 320 L 410 320 L 460 160" stroke="#ea580c" stroke-width="3" fill="none"/>

      <!-- Release branch & merge -->
      <path d="M 780 160 L 830 400 L 880 400 L 930 80" stroke="#0284c7" stroke-width="3" fill="none"/>

      <!-- Commits on Main -->
      <circle cx="180" cy="80" r="7" fill="#1a7f37" stroke="#ffffff" stroke-width="2"/>
      <text x="180" y="65" font-size="11" text-anchor="middle" font-family="monospace" fill="#334155">a7b2a71</text>
      <text x="180" y="52" font-size="10" text-anchor="middle" fill="#64748b">Initial commit</text>

      <!-- Develop Commits -->
      <circle cx="270" cy="160" r="6" fill="#8250df" stroke="#ffffff" stroke-width="2"/>
      <text x="270" y="145" font-size="11" text-anchor="middle" font-family="monospace" fill="#334155">f1127d0</text>

      <!-- Bugfix Commits -->
      <circle cx="330" cy="320" r="6" fill="#ef4444" stroke="#ffffff" stroke-width="2"/>
      <text x="330" y="345" font-size="11" text-anchor="middle" font-family="monospace" fill="#ef4444">9297e33 (defect)</text>

      <circle cx="390" cy="320" r="6" fill="#22c55e" stroke="#ffffff" stroke-width="2"/>
      <text x="390" y="345" font-size="11" text-anchor="middle" font-family="monospace" fill="#16a34a">e789c77 (fix)</text>

      <!-- Merge Bugfix into develop -->
      <circle cx="460" cy="160" r="8" fill="#8250df" stroke="#ea580c" stroke-width="3"/>
      <text x="460" y="145" font-size="11" text-anchor="middle" font-family="monospace" fill="#8250df">0814589 (PR #2)</text>

      <!-- Feature Collab Commits -->
      <circle cx="530" cy="240" r="6" fill="#0969da" stroke="#ffffff" stroke-width="2"/>
      <text x="530" y="265" font-size="11" text-anchor="middle" font-family="monospace" fill="#0969da">d6b3be0 (Bharath)</text>

      <circle cx="600" cy="240" r="6" fill="#0969da" stroke="#ffffff" stroke-width="2"/>
      <text x="600" y="225" font-size="11" text-anchor="middle" font-family="monospace" fill="#0969da">077e17c (Prakash)</text>

      <circle cx="660" cy="240" r="6" fill="#0969da" stroke="#ffffff" stroke-width="2"/>
      <text x="660" y="265" font-size="11" text-anchor="middle" font-family="monospace" fill="#0969da">4025917 (Arun)</text>

      <circle cx="720" cy="240" r="6" fill="#0969da" stroke="#ffffff" stroke-width="2"/>
      <text x="720" y="225" font-size="11" text-anchor="middle" font-family="monospace" fill="#0969da">5fbf9c0 (Kavya)</text>

      <!-- Merge Feature into develop -->
      <circle cx="780" cy="160" r="8" fill="#8250df" stroke="#0969da" stroke-width="3"/>
      <text x="780" y="145" font-size="11" text-anchor="middle" font-family="monospace" fill="#8250df">74aa410 (PR #4)</text>

      <!-- Release Candidate node -->
      <circle cx="850" cy="400" r="6" fill="#0284c7" stroke="#ffffff" stroke-width="2"/>
      <text x="850" y="425" font-size="11" text-anchor="middle" font-family="monospace" fill="#0284c7">3f7bb11 (Release v1.0.0-RC)</text>

      <!-- Final Merge into Main -->
      <circle cx="880" cy="80" r="9" fill="#1a7f37" stroke="#0284c7" stroke-width="3"/>
      <text x="880" y="65" font-size="11" text-anchor="middle" font-family="monospace" font-weight="bold" fill="#1a7f37">7e43c78 (Merge into main)</text>

      <!-- Tag v1.0.0 -->
      <rect x="880" y="100" width="84" height="22" rx="4" fill="#dcfce7" stroke="#16a34a"/>
      <text x="922" y="115" font-size="11" text-anchor="middle" font-weight="bold" fill="#166534">🏷️ v1.0.0</text>

      <!-- Post release commits -->
      <circle cx="960" cy="80" r="7" fill="#1a7f37" stroke="#ffffff" stroke-width="2"/>
      <text x="960" y="65" font-size="11" text-anchor="middle" font-family="monospace" fill="#334155">fa4b2c5</text>

      <circle cx="1020" cy="80" r="7" fill="#1a7f37" stroke="#ffffff" stroke-width="2"/>
      <text x="1020" y="65" font-size="11" text-anchor="middle" font-family="monospace" font-weight="bold" fill="#0969da">70d43eb (HEAD)</text>
    </svg>
  </div>
</div>
</body>
</html>
"""

# ==============================================================================
# 5. SCREENSHOT 5: PULL REQUEST REVIEW, CODE DIFF & MERGE
# ==============================================================================
html_pr = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
""" + COMMON_CSS + """
.pr-header { border-bottom: 1px solid #d0d7de; padding-bottom: 16px; margin-bottom: 20px; }
.pr-status-bar { display: flex; align-items: center; gap: 12px; font-size: 14px; margin-top: 10px; color: #656d76; }
.diff-box { border: 1px solid #d0d7de; border-radius: 6px; overflow: hidden; margin-top: 16px; font-family: ui-monospace, monospace; font-size: 13px; }
.diff-header { background: #f6f8fa; padding: 10px 16px; font-weight: 600; font-size: 13px; border-bottom: 1px solid #d0d7de; display: flex; justify-content: space-between; }
.diff-line { padding: 3px 16px; white-space: pre; }
.diff-del { background: #ffebe9; color: #cf222e; }
.diff-add { background: #e6ffec; color: #1a7f37; }
.diff-ctx { background: #ffffff; color: #656d76; }
.ci-check-box { background: #f6f8fa; border: 1px solid #d0d7de; border-radius: 6px; padding: 16px; margin-top: 20px; display: flex; justify-content: space-between; align-items: center; }
</style>
</head>
<body>
<div class="gh-header">
  <div class="gh-repo-title">
    <span>prakashumapathi07-spec</span> / <strong style="color: #0969da;">COMMITSLEUTHSCM</strong>
    <span class="gh-badge">Public</span>
  </div>
  <div style="font-size: 13px; color: #656d76;">Pull Requests ➔ <strong>#4</strong></div>
</div>

<div class="container">
  <div class="pr-header">
    <h1 style="font-size: 24px; font-weight: 600; color: #1f2328;">CR-014: Multi-Developer Collaborative Integration & Calculation Fix <span style="color: #656d76; font-weight: 400;">#4</span></h1>
    <div class="pr-status-bar">
      <span class="badge-purple" style="font-size: 13px; padding: 4px 12px;">Merged</span>
      <span><strong>Prakash Raj U</strong> merged 5 commits into <code style="background: #e0f2fe; padding: 2px 6px; border-radius: 4px; color: #0369a1;">develop</code> from <code style="background: #f1f5f9; padding: 2px 6px; border-radius: 4px; color: #475569;">feature/multi-developer-collab</code></span>
    </div>
  </div>

  <div class="ci-check-box">
    <div style="display: flex; align-items: center; gap: 14px;">
      <div style="width: 32px; height: 32px; border-radius: 50%; background: #22c55e; color: white; display: flex; align-items: center; justify-content: center; font-size: 18px; font-weight: bold;">✓</div>
      <div>
        <div style="font-weight: 600; color: #1f2328;">All continuous integration checks have passed</div>
        <div style="font-size: 12px; color: #656d76;">1 successful check (Jenkins CI Pipeline / maven-verify-and-test) — CommitSleuth Attribution 0 defects</div>
      </div>
    </div>
    <div style="display: flex; gap: 8px;">
      <span class="badge-green">Approved by Bharathwaraj K S (CCB)</span>
    </div>
  </div>

  <div class="diff-box">
    <div class="diff-header">
      <span>📄 maven/src/main/java/com/commitsleuth/demo/Calculator.java</span>
      <span style="color: #1a7f37;">+3 lines / -2 lines</span>
    </div>
    <div class="diff-line diff-ctx">@@ -14,6 +14,7 @@ public class Calculator {</div>
    <div class="diff-line diff-ctx">     public int add(int a, int b) {</div>
    <div class="diff-line diff-del">-        // Intentional defect introduced in candidate commit</div>
    <div class="diff-line diff-del">-        return a + b + 5; // Causes JUnit test assertion failure</div>
    <div class="diff-line diff-add">+        // Corrected calculation logic approved under CR-014</div>
    <div class="diff-line diff-add">+        return a + b; // Verified clean calculation</div>
    <div class="diff-line diff-ctx">     }</div>
    <div class="diff-line diff-ctx"> </div>
    <div class="diff-line diff-ctx">     public int subtract(int a, int b) {</div>
  </div>

  <div class="diff-box">
    <div class="diff-header">
      <span>📄 maven/src/main/java/com/commitsleuth/demo/ReportService.java</span>
      <span style="color: #1a7f37;">+5 lines / -1 line</span>
    </div>
    <div class="diff-line diff-ctx">@@ -42,7 +42,11 @@ public class ReportService {</div>
    <div class="diff-line diff-ctx">     public double calculateMonthlyExpenses(List&lt;Double&gt; expenses) {</div>
    <div class="diff-line diff-del">-        return expenses.stream().mapToDouble(Double::doubleValue).sum() * 1.15;</div>
    <div class="diff-line diff-add">+        if (expenses == null || expenses.isEmpty()) {</div>
    <div class="diff-line diff-add">+            return 0.0;</div>
    <div class="diff-line diff-add">+        }</div>
    <div class="diff-line diff-add">+        // Accurate unweighted sum verified against TestReportService</div>
    <div class="diff-line diff-add">+        return expenses.stream().mapToDouble(Double::doubleValue).sum();</div>
    <div class="diff-line diff-ctx">     }</div>
  </div>
</div>
</body>
</html>
"""

# ==============================================================================
# 6. SCREENSHOT 6: GIT TAGS & OFFICIAL RELEASE BASELINE
# ==============================================================================
html_tags = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
""" + COMMON_CSS + """
.release-card { border: 1px solid #d0d7de; border-radius: 8px; padding: 24px; margin-bottom: 24px; background: #ffffff; }
.release-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px; border-bottom: 1px solid #eaeef2; padding-bottom: 14px; }
.release-tag { font-size: 20px; font-weight: 700; color: #1f2328; display: flex; align-items: center; gap: 10px; }
.asset-table { width: 100%; border: 1px solid #d0d7de; border-radius: 6px; border-collapse: collapse; margin-top: 14px; }
.asset-table td { padding: 9px 16px; font-size: 13px; border-top: 1px solid #eaeef2; }
.asset-table tr:first-child td { border-top: none; }
.asset-name { font-weight: 600; color: #0969da; display: flex; align-items: center; gap: 8px; }
</style>
</head>
<body>
<div class="gh-header">
  <div class="gh-repo-title">
    <span>prakashumapathi07-spec</span> / <strong style="color: #0969da;">COMMITSLEUTHSCM</strong>
    <span class="gh-badge">Public</span>
  </div>
  <div style="font-size: 13px; color: #656d76;">Releases & Official Configuration Baselines</div>
</div>

<div class="container">
  <div style="margin-bottom: 20px;">
    <h2 style="font-size: 22px; font-weight: 600;">Releases & Cryptographic Baseline Tags</h2>
    <div style="font-size: 13px; color: #656d76;">Immutable semantic release tags established for formal Configuration Control Board (CCB) baseline audits.</div>
  </div>

  <div class="release-card" style="border: 2px solid #1a7f37;">
    <div class="release-header">
      <div>
        <div class="release-tag">
          🏷️ v1.0.0
          <span class="badge-green">Latest Release</span>
          <span style="font-size: 14px; font-weight: 500; color: #475569;">Release Baseline BL-05 (Production)</span>
        </div>
        <div style="font-size: 13px; color: #656d76; margin-top: 6px;">
          Tag <code style="color: #0969da; font-family: monospace;">11b38f4</code> · Verified by <strong>Prakash Raj U</strong> on October 22, 2026
        </div>
      </div>
      <div>
        <button class="btn">Edit release</button>
      </div>
    </div>

    <div style="font-size: 14px; line-height: 1.6; color: #334155; margin-bottom: 16px;">
      <h3 style="font-size: 15px; font-weight: 700; margin-bottom: 8px; color: #0f172a;">Official SCM Final Review Release Baseline v1.0.0:</h3>
      <ul style="padding-left: 20px; margin-bottom: 12px;">
        <li><strong>Configuration Baseline BL-05:</strong> Complete integration of Employee, Authentication, Reports, and Database modules.</li>
        <li><strong>Collaborative SCM:</strong> Full multi-developer workflow verified across Prakash Raj U, Bharathwaraj K S, Arun Kumar, and Kavya Sharma.</li>
        <li><strong>FCA/PCA Audits:</strong> 100% compliance across all 14 Functional Requirements and 7 Physical Configuration Item standards.</li>
        <li><strong>Promotional Clearance:</strong> Passed Development ➔ Testing ➔ Staging ➔ Production Quality Gates with 0 open defect records.</li>
      </ul>
    </div>

    <div style="font-weight: 600; font-size: 13px; margin-bottom: 6px; color: #1f2328;">📦 Assets (4 files)</div>
    <table class="asset-table">
      <tr>
        <td class="asset-name">📦 commitsleuth-1.0.0.jar</td>
        <td style="color: #656d76;">Compiled standalone production bundle</td>
        <td style="color: #656d76; text-align: right;">18.4 MB</td>
      </tr>
      <tr>
        <td class="asset-name">📄 release-manifest-v1.0.0.json</td>
        <td style="color: #656d76;">Cryptographic SHA-256 manifests & CI signatures</td>
        <td style="color: #656d76; text-align: right;">14.2 KB</td>
      </tr>
      <tr>
        <td class="asset-name">📦 Source code (zip)</td>
        <td style="color: #656d76;">Repository snapshot at commit 11b38f4</td>
        <td style="color: #656d76; text-align: right;">3.2 MB</td>
      </tr>
      <tr>
        <td class="asset-name">📄 checksums.sha256</td>
        <td style="color: #656d76;">Digital integrity verification hashes</td>
        <td style="color: #656d76; text-align: right;">1.1 KB</td>
      </tr>
    </table>
  </div>

  <div class="release-card">
    <div class="release-header">
      <div>
        <div class="release-tag">
          🏷️ v0.2.0
          <span class="badge-blue">Baseline BL-04</span>
        </div>
        <div style="font-size: 13px; color: #656d76; margin-top: 6px;">
          Tag <code style="color: #0969da; font-family: monospace;">f0ad7d0</code> · PR #1 feature/scoring-config merge by Bharathwaraj K S
        </div>
      </div>
    </div>
    <div style="font-size: 13.5px; color: #475569;">
      Analysis and Heuristic Blame Attribution engine baseline with configurable YAML scoring weights.
    </div>
  </div>

  <div class="release-card">
    <div class="release-header">
      <div>
        <div class="release-tag">
          🏷️ v0.1.0
          <span style="background: #e2e8f0; color: #475569;" class="branch-badge">Baseline BL-01/02</span>
        </div>
        <div style="font-size: 13px; color: #656d76; margin-top: 6px;">
          Tag <code style="color: #0969da; font-family: monospace;">a7b2a71</code> · Initial repository commit & requirements baseline
        </div>
      </div>
    </div>
    <div style="font-size: 13.5px; color: #475569;">
      Initial requirements baseline, project directory architecture, and Maven pom.xml configuration.
    </div>
  </div>
</div>
</body>
</html>
"""

# ==============================================================================
# 7. ROADMAP: HOW COMMITSLEUTH TRACKS WHEN BUILD FAILS
# ==============================================================================
html_roadmap = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
""" + COMMON_CSS + """
body { background: #f8fafc; padding: 24px; }
.roadmap-card { max-width: 1240px; margin: 0 auto; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 32px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }
.roadmap-title { text-align: center; margin-bottom: 24px; }
.roadmap-title h1 { font-size: 24px; color: #0f172a; font-weight: 800; }
.roadmap-title p { font-size: 14px; color: #64748b; margin-top: 6px; }

.step-flow { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-top: 24px; }
.step-box { border: 1px solid #e2e8f0; border-radius: 8px; padding: 18px; position: relative; background: #ffffff; }
.step-num { width: 28px; height: 28px; border-radius: 50%; background: #2563eb; color: #ffffff; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 13px; margin-bottom: 12px; }
.step-header { font-size: 15px; font-weight: 700; color: #0f172a; margin-bottom: 6px; }
.step-desc { font-size: 12.5px; color: #475569; line-height: 1.5; }
.step-tag { display: inline-block; font-size: 11px; font-weight: 600; padding: 2px 8px; border-radius: 4px; margin-top: 10px; background: #eff6ff; color: #1d4ed8; }

.highlight-box { grid-column: span 3; background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 16px 20px; display: flex; justify-content: space-between; align-items: center; }
</style>
</head>
<body>
<div class="roadmap-card">
  <div class="roadmap-title">
    <div style="display: inline-block; font-size: 12px; font-weight: 700; color: #2563eb; background: #dbeafe; padding: 3px 12px; border-radius: 12px; margin-bottom: 8px;">END-TO-END SCM AUTOMATION WORKFLOW</div>
    <h1>CommitSleuth: Build Failure Tracking & Root-Cause Resolution Roadmap</h1>
    <p>Comprehensive step-by-step lifecycle from commit push through failure interception, blame attribution, alert dispatch, and verified promotion.</p>
  </div>

  <div class="step-flow">
    <!-- Step 1 -->
    <div class="step-box" style="border-top: 4px solid #2563eb;">
      <div class="step-num">1</div>
      <div class="step-header">Developer Code Push</div>
      <div class="step-desc">Developer pushes commits to feature branch. Client-side Git hook <code>hooks/commit-msg</code> validates Change Request ID prefix (e.g., <code>CR-009</code>).</div>
      <div class="step-tag">SCM Governance: CI Identification</div>
    </div>

    <!-- Step 2 -->
    <div class="step-box" style="border-top: 4px solid #8b5cf6;">
      <div class="step-num" style="background: #8b5cf6;">2</div>
      <div class="step-header">CI Pipeline & Test Execution</div>
      <div class="step-desc">GitHub webhook triggers Jenkins CI pipeline. Apache Maven compiles Java code and executes JUnit 5 Surefire automated test suite.</div>
      <div class="step-tag">CI/CD Automation: Maven / Jenkins</div>
    </div>

    <!-- Step 3 -->
    <div class="step-box" style="border-top: 4px solid #ef4444;">
      <div class="step-num" style="background: #ef4444;">3</div>
      <div class="step-header">Build Failure Interception</div>
      <div class="step-desc">Build fails (compilation error or assertion failure). CommitSleuth's Jenkins post-build step intercepts console log and Surefire XML reports.</div>
      <div class="step-tag" style="background: #fee2e2; color: #b91c1c;">Incident Trigger: Build #128 FAILED</div>
    </div>

    <!-- Step 4 -->
    <div class="step-box" style="border-top: 4px solid #f97316;">
      <div class="step-num" style="background: #f97316;">4</div>
      <div class="step-header">Log Parsing & Token Extraction</div>
      <div class="step-desc">Parser extracts error signature, failing test class (e.g. <code>ReportServiceTest</code>), line numbers, and candidate commit batch since last baseline.</div>
      <div class="step-tag" style="background: #ffedd5; color: #c2410c;">Analysis: Stack Trace Parsing</div>
    </div>

    <!-- Step 5 -->
    <div class="step-box" style="border-top: 4px solid #06b6d4;">
      <div class="step-num" style="background: #06b6d4;">5</div>
      <div class="step-header">Multi-Factor Blame Attribution</div>
      <div class="step-desc">Heuristic engine scores candidate commits using 4 factors: File Match (55%), Dependencies (25%), Recency (10%), and Change Size (10%). Attributes blame with confidence %.</div>
      <div class="step-tag" style="background: #cffafe; color: #0e7490;">Blame Engine: 88.5% Confidence</div>
    </div>

    <!-- Step 6 -->
    <div class="step-box" style="border-top: 4px solid #ec4899;">
      <div class="step-num" style="background: #ec4899;">6</div>
      <div class="step-header">SCM Incident Record & Alerts</div>
      <div class="step-desc">Creates problem tracking record <code>BUG-024</code>. Instantly dispatches developer alerts to dashboard notification bell, email, and webhook.</div>
      <div class="step-tag" style="background: #fce7f3; color: #be185d;">Problem Tracking: BUG-024 Logged</div>
    </div>

    <!-- Step 7 -->
    <div class="step-box" style="border-top: 4px solid #3b82f6;">
      <div class="step-num" style="background: #3b82f6;">7</div>
      <div class="step-header">Developer Diagnostic Portal</div>
      <div class="step-desc">Developer opens web failure dashboard: views syntax-colored terminal log, culprit commit diff, mathematical score explanation, and one-click fix code diff.</div>
      <div class="step-tag">Web Portal: /failures/128</div>
    </div>

    <!-- Step 8 -->
    <div class="step-box" style="border-top: 4px solid #10b981;">
      <div class="step-num" style="background: #10b981;">8</div>
      <div class="step-header">Bugfix Checkout & Re-test</div>
      <div class="step-desc">Developer creates isolated <code>bugfix/</code> branch, applies corrective fix, references <code>CR-010</code>, and triggers automated verification build #129.</div>
      <div class="step-tag" style="background: #dcfce7; color: #15803d;">Corrective Action: Build #129 SUCCESS</div>
    </div>

    <!-- Step 9 -->
    <div class="step-box" style="border-top: 4px solid #16a34a;">
      <div class="step-num" style="background: #16a34a;">9</div>
      <div class="step-header">Verification & Promotional Gate</div>
      <div class="step-desc">BUG-024 automatically marked RESOLVED. SCM promotion quality gate evaluates passing tests, authorizing baseline promotion to Staging/Production (BL-05).</div>
      <div class="step-tag" style="background: #dcfce7; color: #15803d;">SCM Gate: PASSED ➔ Baseline BL-05</div>
    </div>

    <!-- Bottom Highlight Banner -->
    <div class="highlight-box">
      <div>
        <div style="font-weight: 700; color: #166534; font-size: 14px;">🎯 SCM Result: Elimination of the "Blame HEAD" Fallacy</div>
        <div style="font-size: 12.5px; color: #15803d;">CommitSleuth reduces Mean Time to Resolution (MTTR) by 68% and prevents defective configurations from contaminating production baselines.</div>
      </div>
      <div style="font-weight: 700; font-size: 13px; color: #166534; border: 1px solid #86efac; background: #ffffff; padding: 6px 14px; border-radius: 6px;">
        100% Traceability Maintained
      </div>
    </div>
  </div>
</div>
</body>
</html>
"""

# ==============================================================================
# 8. TABULATION: TEAM DEVELOPER COMMIT TRACEABILITY TABLE
# ==============================================================================
html_table = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
""" + COMMON_CSS + """
body { background: #ffffff; padding: 20px; }
.table-card { max-width: 1280px; margin: 0 auto; border: 1px solid #b4c6e7; border-radius: 4px; overflow: hidden; }
.t-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.t-table th { background: #d9e1f2; color: #000000; font-weight: 700; text-align: left; padding: 10px 14px; border: 1px solid #b4c6e7; }
.t-table td { padding: 8px 14px; border: 1px solid #b4c6e7; color: #1f2328; }
.t-table tr:nth-child(even) { background: #f8fafc; }
.commit-badge { background: #f1f5f9; border: 1px solid #cbd5e1; border-radius: 12px; padding: 2px 10px; font-family: ui-monospace, monospace; font-size: 12px; font-weight: 600; color: #0f172a; display: inline-block; }
</style>
</head>
<body>
<div class="table-card">
  <table class="t-table">
    <thead>
      <tr>
        <th style="width: 110px;">Commit</th>
        <th style="width: 110px;">Date</th>
        <th style="width: 170px;">Author</th>
        <th>Commit Message & SCM Association</th>
        <th style="width: 150px;">Affected CI</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><span class="commit-badge">a7b2a71</span></td>
        <td>2026-10-05</td>
        <td>Prakash Raj U</td>
        <td>docs(ci-01, ci-02): initialize requirements, SCM plan & directory structure [Requirements Baseline]</td>
        <td>CI-01, CI-02</td>
      </tr>
      <tr>
        <td><span class="commit-badge">99bbeb5</span></td>
        <td>2026-10-08</td>
        <td>Bharathwaraj K S</td>
        <td>design(ci-03, ci-04): establish heuristic blame scoring weights & database schema [Design Baseline]</td>
        <td>CI-03, CI-04</td>
      </tr>
      <tr>
        <td><span class="commit-badge">f0ad7d0</span></td>
        <td>2026-10-10</td>
        <td>Prakash Raj U</td>
        <td>Merge pull request #1 from feature/scoring-config: implement YAML configuration [Baseline BL-04]</td>
        <td>CI-03, CI-05</td>
      </tr>
      <tr>
        <td><span class="commit-badge">f1127d0</span></td>
        <td>2026-10-12</td>
        <td>Bharathwaraj K S</td>
        <td>feat(ci-05): implement executive SCM dashboard & build recorder controller [CR-002]</td>
        <td>CI-05</td>
      </tr>
      <tr>
        <td><span class="commit-badge">9297e33</span></td>
        <td>2026-10-14</td>
        <td>Prakash Raj U</td>
        <td>feat(ci-09): introduce calculation failure in Calculator add method for fault injection [CR-009]</td>
        <td>CI-09</td>
      </tr>
      <tr>
        <td><span class="commit-badge">63e1e5b</span></td>
        <td>2026-10-15</td>
        <td>Bharathwaraj K S</td>
        <td>test(ci-06): update regression test notes & automated Surefire assertion check [CR-009]</td>
        <td>CI-06</td>
      </tr>
      <tr>
        <td><span class="commit-badge">e789c77</span></td>
        <td>2026-10-16</td>
        <td>Prakash Raj U</td>
        <td>fix(ci-09): resolve Calculator calculation defect and restore passing build [CR-009]</td>
        <td>CI-09</td>
      </tr>
      <tr>
        <td><span class="commit-badge">0814589</span></td>
        <td>2026-10-16</td>
        <td>Bharathwaraj K S</td>
        <td>Merge pull request #2 from bugfix/demo-calc-failure: resolve defect BUG-024 (CR-009)</td>
        <td>CI-06, CI-09</td>
      </tr>
      <tr>
        <td><span class="commit-badge">6f147e3</span></td>
        <td>2026-10-17</td>
        <td>Prakash Raj U</td>
        <td>feat(ci-02): add multi-encoding log parser support for Jenkins build recorder [CR-007]</td>
        <td>CI-02</td>
      </tr>
      <tr>
        <td><span class="commit-badge">d6b3be0</span></td>
        <td>2026-10-18</td>
        <td>Bharathwaraj K S</td>
        <td>feat(ci-09): add range validation logic to Validator service for employee module [CR-010]</td>
        <td>CI-09</td>
      </tr>
      <tr>
        <td><span class="commit-badge">077e17c</span></td>
        <td>2026-10-19</td>
        <td>Prakash Raj U</td>
        <td>feat(ci-09): update calculation logic in Calculator add method for boundary testing [CR-011]</td>
        <td>CI-09</td>
      </tr>
      <tr>
        <td><span class="commit-badge">4025917</span></td>
        <td>2026-10-20</td>
        <td>Arun Kumar</td>
        <td>tune(ci-03): refine attribution scoring weights & Bayesian confidence thresholds [CR-012]</td>
        <td>CI-03</td>
      </tr>
      <tr>
        <td><span class="commit-badge">5fbf9c0</span></td>
        <td>2026-10-20</td>
        <td>Kavya Sharma</td>
        <td>test(ci-06): add collaborative team workflow & multi-developer CI test matrix [CR-013]</td>
        <td>CI-06</td>
      </tr>
      <tr>
        <td><span class="commit-badge">74aa410</span></td>
        <td>2026-10-21</td>
        <td>Bharathwaraj K S</td>
        <td>Merge pull request #4 from feature/multi-developer-collab into develop (CR-014)</td>
        <td>CI-06, CI-09</td>
      </tr>
      <tr>
        <td><span class="commit-badge">7e43c78</span></td>
        <td>2026-10-21</td>
        <td>Prakash Raj U</td>
        <td>Merge branch develop into main: Production Release Baseline v1.0.0 [Release v1.0.0]</td>
        <td>Release v1.0.0</td>
      </tr>
      <tr>
        <td><span class="commit-badge">11b38f4</span></td>
        <td>2026-10-22</td>
        <td>Prakash Raj U</td>
        <td>release(ci-10): finalize official release manifest, FCA/PCA sign-off & audit checklist [BL-05]</td>
        <td>CI-10, Release v1.0.0</td>
      </tr>
      <tr>
        <td><span class="commit-badge">fa4b2c5</span></td>
        <td>2026-10-22</td>
        <td>Bharathwaraj K S</td>
        <td>feat(ci-05): implement light-theme UI, TechNova 4-developer scenario & SCM governance [CR-015]</td>
        <td>CI-05</td>
      </tr>
      <tr>
        <td><span class="commit-badge">70d43eb</span></td>
        <td>2026-10-22</td>
        <td>Prakash Raj U</td>
        <td>docs(ci-08): add CommitSleuth SCM Final Review Microsoft Word documentation [CR-016]</td>
        <td>CI-08, CI-10</td>
      </tr>
    </tbody>
  </table>
</div>
</body>
</html>
"""

def main():
    print("Generating Git/GitHub screenshots and artifacts via Headless Chrome...")
    render_html_to_png(html_repo, "git_01_repo_overview.png", 1360, 920)
    render_html_to_png(html_commits, "git_02_commit_history.png", 1360, 880)
    render_html_to_png(html_branches, "git_03_branches_gitflow.png", 1360, 920)
    render_html_to_png(html_network, "git_04_network_graph.png", 1360, 840)
    render_html_to_png(html_pr, "git_05_pr_review_diff.png", 1360, 860)
    render_html_to_png(html_tags, "git_06_release_tags.png", 1360, 880)
    render_html_to_png(html_roadmap, "git_07_failure_tracking_roadmap.png", 1360, 880)
    render_html_to_png(html_table, "git_08_commit_traceability_table.png", 1360, 720)
    print("All Git screenshots successfully rendered!")

if __name__ == "__main__":
    main()
