"""CommitSleuth Web Application & SCM Review Dashboard.
Provides a modern, responsive interface for CI build failure attribution,
configuration status accounting, change management, auditing, and promotional gates.
"""
import os
import sys
import datetime
from functools import wraps
from flask import Flask, request, redirect, session, flash, get_flashed_messages, Response
from markupsafe import Markup, escape
from werkzeug.security import check_password_hash
import yaml

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "analyzer"))
from common import q, ex, log_audit, load_cfg, save_cfg, ROOT
import status_reporter
import promote

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "commitsleuth-scm-review-secret-key-2026")

JENKINS_URL = os.environ.get("JENKINS_URL", "http://localhost:8080")
GITHUB_URL = "https://github.com/prakashumapathi07-spec/COMMITSLEUTHSCM.git"

LIFECYCLE = ["Open", "Assigned", "Fixed", "Verified", "Closed"]

NAV = [
    ("/", "Dashboard", "📊"),
    ("/builds", "Build History", "🔨"),
    ("/problems", "Failure Attribution", "🔍"),
    ("/crs", "Change Requests", "📝"),
    ("/cis", "CI Register", "📋"),
    ("/baselines", "Baselines & Versions", "🏷️"),
    ("/promotions", "Promotions", "🚀"),
    ("/audits", "Audits (FCA/PCA)", "🛡️"),
    ("/report", "CSAR Report", "📑"),
    ("/config", "Customization", "⚙️"),
    ("/audit-trail", "Audit Trail", "🔒")
]

def current_user():
    return session.get("user")

def current_role():
    return session.get("role", "viewer")

def is_admin():
    return session.get("role") == "admin"

def is_maintainer():
    return session.get("role") in ("admin", "maintainer")

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated

def maintainer_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            return redirect("/login")
        if not is_maintainer():
            flash("Permission Denied: Requires Maintainer or Administrator privileges.", "error")
            return redirect("/")
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            return redirect("/login")
        if not is_admin():
            flash("Permission Denied: Administrator role required for this state change.", "error")
            return redirect("/")
        return f(*args, **kwargs)
    return decorated

def layout(title, content, active_path="/"):
    user = current_user()
    role = current_role()
    
    nav_html = ""
    for url, label, icon in NAV:
        is_active = "active" if url == active_path else ""
        nav_html += f'<a href="{url}" class="nav-item {is_active}"><span class="icon">{icon}</span> {escape(label)}</a>'

    messages = get_flashed_messages(with_categories=True)
    msg_html = ""
    for category, msg in messages:
        c_class = "msg-error" if category == "error" else "msg-success"
        msg_html += f'<div class="alert {c_class}">{escape(msg)}</div>'

    user_info = ""
    if user:
        user_info = f"""
        <div class="user-pill">
            <span class="avatar">👤</span>
            <div class="u-meta">
                <span class="uname">{escape(user)}</span>
                <span class="urole role-{role}">{escape(role.upper())}</span>
            </div>
            <a href="/logout" class="btn-logout" title="Sign out">✕</a>
        </div>
        """
    else:
        user_info = '<a href="/login" class="btn-login">Sign In</a>'

    return f"""<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>CommitSleuth — {escape(title)}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-base: #0b1120;
            --bg-card: #131d31;
            --bg-card-hover: #1a2744;
            --border-dim: #223254;
            --border-bright: #38bdf8;
            --text-main: #f1f5f9;
            --text-muted: #94a3b8;
            --accent-cyan: #0284c7;
            --accent-cyan-light: #38bdf8;
            --accent-emerald: #10b981;
            --accent-rose: #f43f5e;
            --accent-amber: #f59e0b;
            --accent-purple: #a855f7;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg-base);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
        }}
        /* Sidebar Navigation */
        aside {{
            width: 260px;
            background: #0f172a;
            border-right: 1px solid var(--border-dim);
            display: flex;
            flex-direction: column;
            position: fixed;
            height: 100vh;
            z-index: 10;
        }}
        .brand {{
            padding: 24px 20px;
            display: flex;
            align-items: center;
            gap: 12px;
            border-bottom: 1px solid var(--border-dim);
        }}
        .brand-logo {{
            width: 36px;
            height: 36px;
            background: linear-gradient(135deg, #0284c7, #38bdf8);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            box-shadow: 0 0 15px rgba(56, 189, 248, 0.35);
        }}
        .brand-text h1 {{
            font-size: 16px;
            font-weight: 800;
            letter-spacing: -0.02em;
            color: #fff;
        }}
        .brand-text span {{
            font-size: 11px;
            color: var(--accent-cyan-light);
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        .nav-list {{
            flex: 1;
            padding: 16px 12px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 4px;
        }}
        .nav-item {{
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 9px 14px;
            border-radius: 6px;
            color: var(--text-muted);
            text-decoration: none;
            font-size: 13.5px;
            font-weight: 500;
            transition: all 0.15s ease;
        }}
        .nav-item:hover {{
            background: rgba(56, 189, 248, 0.08);
            color: #fff;
        }}
        .nav-item.active {{
            background: linear-gradient(90deg, rgba(2, 132, 199, 0.25), rgba(56, 189, 248, 0.1));
            color: var(--accent-cyan-light);
            border-left: 3px solid var(--accent-cyan-light);
            font-weight: 600;
        }}
        .nav-item .icon {{ font-size: 16px; }}
        .nav-footer {{
            padding: 16px;
            border-top: 1px solid var(--border-dim);
            font-size: 12px;
            color: var(--text-muted);
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}
        .external-links {{
            display: flex;
            gap: 8px;
        }}
        .btn-ext {{
            flex: 1;
            text-align: center;
            padding: 6px;
            background: #1e293b;
            color: var(--text-main);
            border-radius: 4px;
            text-decoration: none;
            font-size: 11px;
            font-weight: 600;
            border: 1px solid var(--border-dim);
        }}
        .btn-ext:hover {{ border-color: var(--accent-cyan-light); color: var(--accent-cyan-light); }}
        /* Main Layout */
        .wrapper {{
            margin-left: 260px;
            flex: 1;
            display: flex;
            flex-direction: column;
            min-width: 0;
        }}
        header {{
            height: 64px;
            background: rgba(15, 23, 42, 0.8);
            backdrop-filter: blur(12px);
            border-bottom: 1px solid var(--border-dim);
            padding: 0 32px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            position: sticky;
            top: 0;
            z-index: 5;
        }}
        .page-title {{
            font-size: 18px;
            font-weight: 700;
            color: #fff;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .user-pill {{
            display: flex;
            align-items: center;
            gap: 10px;
            background: #1e293b;
            padding: 6px 12px;
            border-radius: 30px;
            border: 1px solid var(--border-dim);
        }}
        .avatar {{ font-size: 16px; }}
        .u-meta {{ display: flex; flex-direction: column; line-height: 1.1; }}
        .uname {{ font-size: 12px; font-weight: 600; color: #fff; }}
        .urole {{
            font-size: 9.5px;
            font-weight: 700;
            letter-spacing: 0.05em;
            padding: 1px 4px;
            border-radius: 3px;
            margin-top: 2px;
            display: inline-block;
        }}
        .role-admin {{ background: rgba(168, 85, 247, 0.25); color: #c084fc; }}
        .role-maintainer {{ background: rgba(56, 189, 248, 0.25); color: #38bdf8; }}
        .role-viewer {{ background: rgba(148, 163, 184, 0.25); color: #cbd5e1; }}
        .btn-logout {{
            color: var(--text-muted);
            text-decoration: none;
            font-size: 12px;
            margin-left: 4px;
            padding: 2px 6px;
            border-radius: 4px;
        }}
        .btn-logout:hover {{ color: var(--accent-rose); }}
        .btn-login {{
            background: var(--accent-cyan);
            color: #fff;
            padding: 8px 16px;
            border-radius: 6px;
            text-decoration: none;
            font-size: 13px;
            font-weight: 600;
        }}
        main {{
            padding: 32px;
            flex: 1;
            max-width: 1400px;
        }}
        /* Alerts */
        .alert {{
            padding: 12px 18px;
            border-radius: 6px;
            margin-bottom: 24px;
            font-size: 14px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .msg-success {{ background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.3); color: #6ee7b7; }}
        .msg-error {{ background: rgba(244, 63, 94, 0.15); border: 1px solid rgba(244, 63, 94, 0.3); color: #fda4af; }}
        /* Cards & Metrics */
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 18px;
            margin-bottom: 28px;
        }}
        .metric-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-dim);
            border-radius: 10px;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 6px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            transition: transform 0.15s ease, border-color 0.15s ease;
        }}
        .metric-card:hover {{
            transform: translateY(-2px);
            border-color: rgba(56, 189, 248, 0.4);
        }}
        .metric-label {{
            font-size: 12px;
            color: var(--text-muted);
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        .metric-val {{
            font-size: 28px;
            font-weight: 800;
            color: #fff;
            line-height: 1;
        }}
        .metric-sub {{
            font-size: 12px;
            color: var(--text-muted);
            margin-top: 4px;
        }}
        /* Tables */
        .card-panel {{
            background: var(--bg-card);
            border: 1px solid var(--border-dim);
            border-radius: 10px;
            padding: 24px;
            margin-bottom: 28px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }}
        .panel-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 18px;
        }}
        .panel-title {{
            font-size: 16px;
            font-weight: 700;
            color: #fff;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .table-responsive {{
            overflow-x: auto;
            width: 100%;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13.5px;
            text-align: left;
        }}
        th {{
            background: #1e293b;
            color: var(--text-muted);
            font-weight: 600;
            padding: 12px 14px;
            border-bottom: 1px solid var(--border-dim);
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }}
        td {{
            padding: 12px 14px;
            border-bottom: 1px solid rgba(51, 65, 85, 0.4);
            color: var(--text-main);
            vertical-align: middle;
        }}
        tr:hover td {{
            background: rgba(56, 189, 248, 0.03);
        }}
        /* Status Badges */
        .badge {{
            display: inline-flex;
            align-items: center;
            gap: 5px;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.02em;
        }}
        .badge-success {{ background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }}
        .badge-failure {{ background: rgba(244, 63, 94, 0.15); color: #fb7185; border: 1px solid rgba(244, 63, 94, 0.3); }}
        .badge-warning {{ background: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); }}
        .badge-info {{ background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.3); }}
        .badge-purple {{ background: rgba(168, 85, 247, 0.15); color: #c084fc; border: 1px solid rgba(168, 85, 247, 0.3); }}
        .badge-neutral {{ background: rgba(148, 163, 184, 0.15); color: #cbd5e1; border: 1px solid rgba(148, 163, 184, 0.3); }}
        /* Code & Monospace */
        .mono {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 12.5px;
            background: #0f172a;
            padding: 2px 6px;
            border-radius: 4px;
            border: 1px solid var(--border-dim);
            color: #38bdf8;
        }}
        /* Buttons & Forms */
        .btn {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: var(--accent-cyan);
            color: #fff;
            padding: 7px 14px;
            border-radius: 6px;
            border: none;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            text-decoration: none;
            transition: opacity 0.15s;
        }}
        .btn:hover {{ opacity: 0.9; }}
        .btn-sm {{ padding: 4px 8px; font-size: 11.5px; }}
        .btn-outline {{
            background: transparent;
            border: 1px solid var(--border-dim);
            color: var(--text-main);
        }}
        .btn-outline:hover {{ border-color: var(--accent-cyan-light); color: var(--accent-cyan-light); }}
        .btn-danger {{ background: var(--accent-rose); }}
        .btn-success {{ background: var(--accent-emerald); }}
        input, select, textarea {{
            background: #0f172a;
            border: 1px solid var(--border-dim);
            border-radius: 6px;
            color: #fff;
            padding: 8px 12px;
            font-size: 13.5px;
            font-family: inherit;
        }}
        input:focus, select:focus, textarea:focus {{
            outline: none;
            border-color: var(--accent-cyan-light);
            box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.2);
        }}
        .form-row {{
            display: flex;
            gap: 12px;
            align-items: flex-end;
            flex-wrap: wrap;
            margin-top: 14px;
        }}
        .form-group {{
            display: flex;
            flex-direction: column;
            gap: 6px;
            min-width: 160px;
            flex: 1;
        }}
        .form-group label {{
            font-size: 12px;
            color: var(--text-muted);
            font-weight: 600;
        }}
        pre {{
            background: #0f172a;
            border: 1px solid var(--border-dim);
            border-radius: 8px;
            padding: 16px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 13px;
            color: #e2e8f0;
            overflow-x: auto;
            line-height: 1.5;
        }}
        /* Progress bar */
        .conf-bar-wrap {{
            width: 100px;
            height: 8px;
            background: #1e293b;
            border-radius: 4px;
            overflow: hidden;
            display: inline-block;
            vertical-align: middle;
            margin-right: 6px;
        }}
        .conf-bar {{
            height: 100%;
            background: linear-gradient(90deg, #0284c7, #38bdf8);
            border-radius: 4px;
        }}
        .conf-high {{ background: linear-gradient(90deg, #f59e0b, #ef4444); }}
    </style>
</head>
<body>
    <aside>
        <div class="brand">
            <div class="brand-logo">🔍</div>
            <div class="brand-text">
                <h1>CommitSleuth</h1>
                <span>SCM Review III — VIT</span>
            </div>
        </div>
        <nav class="nav-list">
            {nav_html}
        </nav>
        <div class="nav-footer">
            <div style="font-weight: 600; color: #fff;">ISWE403L Project</div>
            <div>Prakash Raj U &amp; Bharathwaraj</div>
            <div class="external-links">
                <a href="{JENKINS_URL}" target="_blank" class="btn-ext">Jenkins CI</a>
                <a href="{GITHUB_URL}" target="_blank" class="btn-ext">GitHub</a>
            </div>
        </div>
    </aside>
    <div class="wrapper">
        <header>
            <div class="page-title">{escape(title)}</div>
            {user_info}
        </header>
        <main>
            {msg_html}
            {content}
        </main>
    </div>
</body>
</html>"""

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        rows = q("SELECT * FROM users WHERE username=?", (username,))
        if rows and check_password_hash(rows[0]["password_hash"], password):
            session["user"] = rows[0]["username"]
            session["role"] = rows[0]["role"]
            log_audit(username, "User Authenticated", f"Role: {rows[0]['role']}")
            flash(f"Welcome back, {rows[0]['full_name']}! Signed in as {rows[0]['role'].upper()}.", "success")
            return redirect("/")
        flash("Invalid username or password credentials.", "error")
        log_audit(username or "unknown", "Failed Login Attempt", "")

    content = """
    <div style="max-width: 440px; margin: 40px auto;">
        <div class="card-panel">
            <div style="text-align: center; margin-bottom: 24px;">
                <div style="font-size: 40px; margin-bottom: 8px;">🔐</div>
                <h2 style="font-size: 20px; color: #fff;">CommitSleuth Portal Access</h2>
                <p style="font-size: 13px; color: var(--text-muted); margin-top: 4px;">Role-Based Authentication & SCM Security Gate</p>
            </div>
            <form method="post">
                <div class="form-group" style="margin-bottom: 16px;">
                    <label>Username</label>
                    <input name="username" placeholder="e.g. prakash, bharath, viewer" required autofocus>
                </div>
                <div class="form-group" style="margin-bottom: 24px;">
                    <label>Password</label>
                    <input name="password" type="password" placeholder="••••••••" required>
                </div>
                <button type="submit" class="btn" style="width: 100%; justify-content: center; padding: 10px;">Sign In to SCM Portal</button>
            </form>
            <div style="margin-top: 24px; padding-top: 18px; border-top: 1px solid var(--border-dim); font-size: 12px; color: var(--text-muted);">
                <div style="font-weight: 600; color: #fff; margin-bottom: 6px;">Evaluation Demonstration Accounts:</div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                    <span><b>Administrator:</b> prakash</span> <code>admin123</code>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                    <span><b>Administrator:</b> bharath</span> <code>admin123</code>
                </div>
                <div style="display: flex; justify-content: space-between;">
                    <span><b>Auditor / Viewer:</b> viewer</span> <code>viewer123</code>
                </div>
            </div>
        </div>
    </div>
    """
    return layout("Authentication", content, "/login")

@app.route("/logout")
def logout():
    user = session.get("user")
    if user:
        log_audit(user, "User Signed Out", "")
    session.clear()
    flash("You have been securely signed out.", "success")
    return redirect("/login")

@app.route("/")
@login_required
def home():
    def count(sql): return q(sql)[0][0]
    total_builds = count("SELECT COUNT(*) FROM builds")
    success_builds = count("SELECT COUNT(*) FROM builds WHERE result='SUCCESS'")
    failed_builds = count("SELECT COUNT(*) FROM builds WHERE result='FAILURE'")
    open_problems = count("SELECT COUNT(*) FROM problems WHERE status!='Closed'")
    baselined_cis = count("SELECT COUNT(*) FROM ci_register WHERE status LIKE '%Baselined%' OR approval='Approved'")
    passed_promotions = count("SELECT COUNT(*) FROM promotions WHERE result='PASSED'")

    rate = f"{(success_builds * 100 // total_builds)}%" if total_builds > 0 else "N/A"

    latest_build = q("SELECT * FROM builds ORDER BY build_no DESC LIMIT 1")
    latest_prob = q("SELECT * FROM problems ORDER BY id DESC LIMIT 1")

    banner_html = ""
    if latest_build:
        b = latest_build[0]
        b_class = "badge-success" if b["result"] == "SUCCESS" else "badge-failure"
        attr_btn = ""
        if latest_prob and b['result'] == 'FAILURE':
            attr_btn = f'<a href="/problem/{latest_prob[0]["id"]}" class="btn btn-sm btn-danger">View Failure Attribution</a>'
        banner_html = f"""
        <div class="card-panel" style="background: linear-gradient(135deg, rgba(30, 41, 59, 0.7), rgba(15, 23, 42, 0.9)); border-color: rgba(56, 189, 248, 0.2);">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px;">
                <div>
                    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 6px;">
                        <span class="badge {b_class}">{b['result']}</span>
                        <span style="font-size: 18px; font-weight: 700; color: #fff;">CI Build #{b['build_no']}</span>
                        <span class="mono">{escape(b['commit_hash'])}</span>
                        <span class="badge badge-info">{escape(b['branch'])}</span>
                    </div>
                    <div style="font-size: 13px; color: var(--text-muted);">
                        Triggered on {escape(b['created'])} &bull; Duration: {b['duration_sec']}s &bull; {escape(b['test_summary'] or 'Execution complete')}
                    </div>
                </div>
                <div style="display: flex; gap: 8px;">
                    <a href="/builds" class="btn btn-outline btn-sm">All Builds</a>
                    {attr_btn}
                </div>
            </div>
        </div>
        """

    recent_problems_rows = ""
    for p in q("SELECT * FROM problems ORDER BY id DESC LIMIT 5"):
        s_badge = "badge-failure" if p["status"] == "Open" else "badge-warning" if p["status"] in ("Assigned", "Fixed") else "badge-success"
        p_code = p["problem_code"] or f"P-{p['id']:03d}"
        recent_problems_rows += f"""
        <tr>
            <td><a href="/problem/{p['id']}" style="color: var(--accent-cyan-light); font-weight: 600; text-decoration: none;">{escape(p_code)}</a></td>
            <td>Build #{p['build_no']}</td>
            <td><span class="badge badge-purple">{escape(p['failure_type'])}</span></td>
            <td><span class="mono">{escape(p['suspect_commit'])}</span></td>
            <td><b>{p['confidence'] * 100:.1f}%</b></td>
            <td>{escape(p['assignee'])}</td>
            <td><span class="badge {s_badge}">{escape(p['status'])}</span></td>
            <td><a href="/problem/{p['id']}" class="btn btn-outline btn-sm">Inspect</a></td>
        </tr>
        """

    recent_activity_rows = ""
    for a in q("SELECT * FROM audit_trail ORDER BY id DESC LIMIT 6"):
        recent_activity_rows += f"""
        <tr>
            <td style="color: var(--text-muted); font-size: 12px;">{escape(a['timestamp'])}</td>
            <td><b>{escape(a['username'])}</b></td>
            <td>{escape(a['action'])}</td>
            <td style="color: var(--text-muted); font-size: 12.5px;">{escape(a['details'])}</td>
        </tr>
        """

    content = f"""
    {banner_html}
    <div class="metrics-grid">
        <div class="metric-card">
            <span class="metric-label">Pipeline Builds</span>
            <span class="metric-val">{total_builds}</span>
            <span class="metric-sub">{success_builds} passed / {failed_builds} failed</span>
        </div>
        <div class="metric-card">
            <span class="metric-label">Build Success Rate</span>
            <span class="metric-val" style="color: var(--accent-emerald);">{rate}</span>
            <span class="metric-sub">Across all CI triggers</span>
        </div>
        <div class="metric-card">
            <span class="metric-label">Open Problems</span>
            <span class="metric-val" style="color: {'var(--accent-rose)' if open_problems > 0 else 'var(--accent-emerald)'};">{open_problems}</span>
            <span class="metric-sub">Attributed defects pending closure</span>
        </div>
        <div class="metric-card">
            <span class="metric-label">Configuration Items</span>
            <span class="metric-val">{baselined_cis}/20</span>
            <span class="metric-sub">100% Identified &amp; Baselined</span>
        </div>
        <div class="metric-card">
            <span class="metric-label">Approved Promotions</span>
            <span class="metric-val" style="color: var(--accent-cyan-light);">{passed_promotions}</span>
            <span class="metric-sub">Passed SCM Quality Gates</span>
        </div>
    </div>

    <div style="display: grid; grid-template-columns: 3fr 2fr; gap: 24px;">
        <div class="card-panel">
            <div class="panel-header">
                <div class="panel-title">🚨 Recent Build Failure Attributions</div>
                <a href="/problems" class="btn btn-outline btn-sm">View Register</a>
            </div>
            <div class="table-responsive">
                <table>
                    <thead>
                        <tr>
                            <th>Problem</th>
                            <th>Build</th>
                            <th>Category</th>
                            <th>Suspect Commit</th>
                            <th>Confidence</th>
                            <th>Assignee</th>
                            <th>Status</th>
                            <th></th>
                        </tr>
                    </thead>
                    <tbody>
                        {recent_problems_rows or '<tr><td colspan="8" style="text-align: center; color: var(--text-muted);">No build failures recorded yet.</td></tr>'}
                    </tbody>
                </table>
            </div>
        </div>

        <div class="card-panel">
            <div class="panel-header">
                <div class="panel-title">🛡️ SCM Audit Activity</div>
                <a href="/audit-trail" class="btn btn-outline btn-sm">View Trail</a>
            </div>
            <div class="table-responsive">
                <table>
                    <thead>
                        <tr>
                            <th>Time</th>
                            <th>User</th>
                            <th>Action</th>
                            <th>Details</th>
                        </tr>
                    </thead>
                    <tbody>
                        {recent_activity_rows or '<tr><td colspan="4" style="text-align: center; color: var(--text-muted);">No activity recorded.</td></tr>'}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    """
    return layout("Executive SCM Dashboard", content, "/")

@app.route("/builds")
@login_required
def builds():
    rows = ""
    for r in q("SELECT * FROM builds ORDER BY build_no DESC"):
        badge_cls = "badge-success" if r["result"] == "SUCCESS" else "badge-failure"
        prob = q("SELECT id, problem_code FROM problems WHERE build_no=?", (r["build_no"],))
        prob_link = ""
        if prob:
            p_code = prob[0]["problem_code"] or f"P-{prob[0]['id']:03d}"
            prob_link = f'<a href="/problem/{prob[0]["id"]}" class="badge badge-purple" style="text-decoration:none;">{escape(p_code)}</a>'

        rows += f"""
        <tr>
            <td><b>#{r['build_no']}</b></td>
            <td><span class="badge {badge_cls}">{r['result']}</span></td>
            <td><span class="mono">{escape(r['commit_hash'])}</span></td>
            <td><span class="badge badge-info">{escape(r['branch'] or 'main')}</span></td>
            <td>{escape(r['test_summary'] or 'Build passed')}</td>
            <td>{r['duration_sec']}s</td>
            <td style="color: var(--text-muted); font-size: 12.5px;">{escape(r['created'])}</td>
            <td>{prob_link}</td>
        </tr>
        """
    content = f"""
    <div class="card-panel">
        <div class="panel-header">
            <div class="panel-title">🔨 Continuous Integration Build History</div>
            <div style="font-size: 13px; color: var(--text-muted);">Synchronized with Jenkins Pipeline</div>
        </div>
        <div class="table-responsive">
            <table>
                <thead>
                    <tr>
                        <th>Build #</th>
                        <th>Result</th>
                        <th>Commit</th>
                        <th>Branch</th>
                        <th>Execution / Test Summary</th>
                        <th>Duration</th>
                        <th>Timestamp</th>
                        <th>Linked Problem</th>
                    </tr>
                </thead>
                <tbody>
                    {rows or '<tr><td colspan="8" style="text-align: center; color: var(--text-muted);">No builds in database. Run pipeline to populate.</td></tr>'}
                </tbody>
            </table>
        </div>
    </div>
    """
    return layout("CI Build History", content, "/builds")

@app.route("/problems")
@login_required
def problems():
    rows = ""
    for p in q("SELECT * FROM problems ORDER BY id DESC"):
        s_cls = "badge-failure" if p["status"] == "Open" else "badge-warning" if p["status"] in ("Assigned", "Fixed") else "badge-success"
        
        advance_btn = ""
        if is_maintainer() and p["status"] in LIFECYCLE[:-1]:
            next_state = LIFECYCLE[LIFECYCLE.index(p["status"]) + 1]
            advance_btn = f"""
            <form method="post" action="/problem/{p['id']}/advance" style="display:inline;">
                <button type="submit" class="btn btn-outline btn-sm" title="Transition to {next_state}">Advance &rarr; {next_state}</button>
            </form>
            """

        conf = p["confidence"] or 0.0
        bar_cls = "conf-high" if conf >= 0.6 else ""
        p_code = p["problem_code"] or f"P-{p['id']:03d}"

        rows += f"""
        <tr>
            <td><a href="/problem/{p['id']}" style="color: var(--accent-cyan-light); font-weight: 700; text-decoration: none;">{escape(p_code)}</a></td>
            <td>Build #{p['build_no']}</td>
            <td><span class="badge badge-purple">{escape(p['failure_type'])}</span></td>
            <td><span class="mono">{escape(p['suspect_commit'])}</span></td>
            <td>
                <div class="conf-bar-wrap"><div class="conf-bar {bar_cls}" style="width: {conf * 100:.0f}%;"></div></div>
                <b>{conf * 100:.1f}%</b>
            </td>
            <td><span class="badge badge-neutral">{escape(p['attribution_status'] or 'Candidate')}</span></td>
            <td>{escape(p['assignee'])}</td>
            <td><span class="badge {s_cls}">{escape(p['status'])}</span></td>
            <td>
                <a href="/problem/{p['id']}" class="btn btn-sm">Inspect</a>
                {advance_btn}
            </td>
        </tr>
        """

    content = f"""
    <div class="card-panel">
        <div class="panel-header">
            <div class="panel-title">🔍 SCM Problem Tracking &amp; Failure Attribution Register</div>
            <div style="font-size: 13px; color: var(--text-muted);">Defect Lifecycle: Open &rarr; Assigned &rarr; Fixed &rarr; Verified &rarr; Closed</div>
        </div>
        <div class="table-responsive">
            <table>
                <thead>
                    <tr>
                        <th>Problem ID</th>
                        <th>Build #</th>
                        <th>Type</th>
                        <th>Suspect Commit</th>
                        <th>Confidence</th>
                        <th>Attribution</th>
                        <th>Assignee</th>
                        <th>Lifecycle Status</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {rows or '<tr><td colspan="9" style="text-align: center; color: var(--text-muted);">No open problems reported.</td></tr>'}
                </tbody>
            </table>
        </div>
    </div>
    """
    return layout("Problem Tracking Register", content, "/problems")

@app.route("/problem/<int:pid>")
@login_required
def problem_detail(pid):
    p_rows = q("SELECT * FROM problems WHERE id=?", (pid,))
    if not p_rows:
        flash("Problem record not found.", "error")
        return redirect("/problems")
    p = p_rows[0]
    p_code = p["problem_code"] or f"P-{p['id']:03d}"

    scores = q("SELECT * FROM commit_scores WHERE problem_id=? ORDER BY score DESC", (pid,))
    
    score_rows = ""
    for idx, s in enumerate(scores):
        rank_badge = f'<span class="badge badge-failure">Rank #1 Culprit</span>' if idx == 0 else f'<span class="badge badge-neutral">Candidate #{idx+1}</span>'
        score_rows += f"""
        <tr>
            <td>{rank_badge}</td>
            <td><span class="mono">{escape(s['commit_hash'])}</span></td>
            <td><b>{escape(s['author'])}</b></td>
            <td>{escape(s['message'])}</td>
            <td><span class="mono" style="font-size: 11px;">{escape(s['files'] or 'None')}</span></td>
            <td>
                <div class="conf-bar-wrap"><div class="conf-bar" style="width: {s['score'] * 100:.0f}%;"></div></div>
                <b>{s['score'] * 100:.1f}%</b>
            </td>
            <td style="font-size: 12px; color: #cbd5e1;">{escape(s['evidence_details'] or 'Scored based on recency and scope')}</td>
        </tr>
        """

    advance_btn = ""
    if is_maintainer() and p["status"] != "Closed":
        advance_btn = f"""
        <form method="post" action="/problem/{p['id']}/advance">
            <button type="submit" class="btn btn-success">Advance Lifecycle State &rarr;</button>
        </form>
        """

    content = f"""
    <div style="display: flex; gap: 12px; margin-bottom: 20px;">
        <a href="/problems" class="btn btn-outline btn-sm">&larr; Back to Problem Register</a>
    </div>

    <div class="card-panel" style="border-left: 4px solid var(--accent-rose);">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 16px;">
            <div>
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                    <h2 style="font-size: 22px; color: #fff;">{escape(p_code)} — Build #{p['build_no']} Attribution Report</h2>
                    <span class="badge badge-purple">{escape(p['failure_type'].upper())}</span>
                    <span class="badge badge-failure">{escape(p['status'])}</span>
                </div>
                <p style="font-size: 14px; color: var(--text-muted); margin-bottom: 12px;">
                    Reported at {escape(p['created'])} &bull; Assigned to: <b>{escape(p['assignee'])}</b>
                </p>
            </div>
            <div>
                {advance_btn}
            </div>
        </div>

        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; margin-top: 16px;">
            <div style="background: #0f172a; padding: 16px; border-radius: 8px; border: 1px solid var(--border-dim);">
                <div style="font-size: 11px; color: var(--text-muted); font-weight: 700; text-transform: uppercase;">Primary Culprit Commit</div>
                <div style="font-size: 18px; font-weight: 800; color: #fff; margin: 6px 0;">
                    <span class="mono" style="font-size: 16px;">{escape(p['suspect_commit'])}</span>
                </div>
                <div style="font-size: 13px; color: var(--text-muted);">Attribution Confidence: <b style="color: var(--accent-rose);">{p['confidence'] * 100:.1f}%</b></div>
            </div>

            <div style="background: #0f172a; padding: 16px; border-radius: 8px; border: 1px solid var(--border-dim);">
                <div style="font-size: 11px; color: var(--text-muted); font-weight: 700; text-transform: uppercase;">Affected File / Component</div>
                <div style="font-size: 15px; font-weight: 700; color: var(--accent-cyan-light); margin: 6px 0;">
                    {escape(p['affected_file'] or 'Inferred from log')}
                </div>
                <div style="font-size: 12px; color: var(--text-muted);">{escape(p['error_message'] or 'Maven error')}</div>
            </div>

            <div style="background: #0f172a; padding: 16px; border-radius: 8px; border: 1px solid var(--border-dim);">
                <div style="font-size: 11px; color: var(--text-muted); font-weight: 700; text-transform: uppercase;">Rollback &amp; SCM Action Recommendation</div>
                <div style="font-size: 13px; font-weight: 600; color: #fbbf24; margin-top: 6px;">
                    {escape(p['action'] or 'Manual investigation required')}
                </div>
            </div>
        </div>

        <div style="margin-top: 18px; padding-top: 14px; border-top: 1px solid var(--border-dim);">
            <div style="font-size: 12px; color: var(--text-muted); font-weight: 600;">Automated Notification Dispatch:</div>
            <pre style="margin-top: 6px;">{escape(p['notification'] or 'No notification recorded')}</pre>
        </div>
    </div>

    <div class="card-panel">
        <div class="panel-header">
            <div class="panel-title">⚖️ Candidate Commit Ranking &amp; Multi-Factor Evidence Matrix</div>
            <div style="font-size: 12.5px; color: var(--text-muted);">Evaluated candidate window since last passing baseline</div>
        </div>
        <div class="table-responsive">
            <table>
                <thead>
                    <tr>
                        <th>Rank</th>
                        <th>Commit</th>
                        <th>Author</th>
                        <th>Message</th>
                        <th>Changed Files</th>
                        <th>Score</th>
                        <th>Evidence Breakdown</th>
                    </tr>
                </thead>
                <tbody>
                    {score_rows or '<tr><td colspan="7">No candidate scores saved.</td></tr>'}
                </tbody>
            </table>
        </div>
    </div>
    """
    return layout(f"Problem {p_code}", content, "/problems")

@app.route("/problem/<int:pid>/advance", methods=["POST"])
@maintainer_required
def problem_advance(pid):
    p = q("SELECT status, problem_code FROM problems WHERE id=?", (pid,))
    if p and p[0]["status"] in LIFECYCLE[:-1]:
        cur = p[0]["status"]
        nxt = LIFECYCLE[LIFECYCLE.index(cur) + 1]
        resolved = f"{datetime.date.today():%Y-%m-%d}" if nxt == "Closed" else None
        ex("UPDATE problems SET status=?, resolved_date=? WHERE id=?", (nxt, resolved, pid))
        p_code = p[0]["problem_code"] or f"P-{pid:03d}"
        log_audit(current_user(), f"Problem Status Advanced: {cur} -> {nxt}", f"Problem {p_code}")
        flash(f"Problem {p_code} advanced from '{cur}' to '{nxt}'.", "success")
    return redirect(f"/problem/{pid}")

@app.route("/crs")
@login_required
def crs():
    rows = ""
    for r in q("SELECT * FROM change_requests ORDER BY cr_id"):
        s_cls = "badge-success" if r["status"] == "Implemented" else "badge-info" if r["status"] == "Approved" else "badge-warning" if r["status"] == "Under Review" else "badge-failure"
        
        actions = ""
        if is_admin():
            actions = f"""
            <div style="display: flex; gap: 4px;">
                <form method="post" action="/cr/{r['cr_id']}/approve" style="display:inline;">
                    <button class="btn btn-outline btn-sm btn-success" title="Approve CR">Approve</button>
                </form>
                <form method="post" action="/cr/{r['cr_id']}/reject" style="display:inline;">
                    <button class="btn btn-outline btn-sm btn-danger" title="Reject CR">Reject</button>
                </form>
                <form method="post" action="/cr/{r['cr_id']}/implement" style="display:inline;">
                    <button class="btn btn-outline btn-sm" title="Mark Implemented">Verify</button>
                </form>
            </div>
            """

        rows += f"""
        <tr>
            <td><b>{escape(r['cr_id'])}</b></td>
            <td><b>{escape(r['title'] or r['description'])}</b><br><span style="font-size: 12px; color: var(--text-muted);">{escape(r['description'])}</span></td>
            <td>{escape(r['requester'])}</td>
            <td><span class="badge badge-purple">{escape(r['priority'] or 'Medium')}</span></td>
            <td>{escape(r['impact'])}</td>
            <td><span class="badge {s_cls}">{escape(r['status'])}</span></td>
            <td>{escape(r['decision'] or 'Pending')}<br><span style="font-size: 11px; color: var(--text-muted);">{escape(r['decision_date'] or '')}</span></td>
            <td><span class="mono">{escape(r['branch'] or 'main')}</span></td>
            <td>{actions}</td>
        </tr>
        """

    form_html = ""
    if is_maintainer():
        form_html = """
        <div class="card-panel">
            <div class="panel-header">
                <div class="panel-title">📝 Raise a New Software Change Request (CR)</div>
                <div style="font-size: 12.5px; color: var(--text-muted);">Configuration Control Board (CCB) Workflow</div>
            </div>
            <form method="post" action="/cr/new">
                <div class="form-row">
                    <div class="form-group" style="flex: 1; max-width: 140px;">
                        <label>CR Identifier</label>
                        <input name="cr_id" placeholder="CR-010" required>
                    </div>
                    <div class="form-group" style="flex: 2;">
                        <label>Title</label>
                        <input name="title" placeholder="Brief change summary" required>
                    </div>
                    <div class="form-group" style="flex: 1; max-width: 160px;">
                        <label>Priority</label>
                        <select name="priority">
                            <option>High</option>
                            <option selected>Medium</option>
                            <option>Low</option>
                        </select>
                    </div>
                    <div class="form-group" style="flex: 1; max-width: 200px;">
                        <label>Branch</label>
                        <input name="branch" placeholder="feature/new-module" required>
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group" style="flex: 2;">
                        <label>Full Technical Description &amp; Scope</label>
                        <input name="description" placeholder="Describe the change, rationale, and target components" required>
                    </div>
                    <div class="form-group" style="flex: 1;">
                        <label>Impact Assessment</label>
                        <input name="impact" placeholder="e.g. Jenkinsfile, Calculator.java, DB" required>
                    </div>
                    <div style="display: flex; align-items: flex-end;">
                        <button type="submit" class="btn">Submit Change Request</button>
                    </div>
                </div>
            </form>
        </div>
        """

    content = f"""
    <div class="card-panel">
        <div class="panel-header">
            <div class="panel-title">📋 Change Request (CR) Register</div>
            <div style="font-size: 13px; color: var(--text-muted);">CCB Managed Change Tracking</div>
        </div>
        <div class="table-responsive">
            <table>
                <thead>
                    <tr>
                        <th>CR ID</th>
                        <th>Title &amp; Description</th>
                        <th>Requester</th>
                        <th>Priority</th>
                        <th>Impact</th>
                        <th>Status</th>
                        <th>CCB Decision</th>
                        <th>Branch</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
        </div>
    </div>
    {form_html}
    """
    return layout("Change Request Register", content, "/crs")

@app.route("/cr/new", methods=["POST"])
@maintainer_required
def cr_new():
    f = request.form
    cr_id = f["cr_id"].strip()
    title = f["title"].strip()
    desc = f["description"].strip()
    impact = f["impact"].strip()
    priority = f.get("priority", "Medium")
    branch = f["branch"].strip()

    ex("""INSERT INTO change_requests (cr_id, title, description, requester, impact, priority, reason, status, decision, decision_date, branch, pull_request)
          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
       (cr_id, title, desc, current_user(), impact, priority, desc, "Raised", "Awaiting CCB Review", f"{datetime.date.today():%Y-%m-%d}", branch, ""))
    
    log_audit(current_user(), f"Raised Change Request {cr_id}", f"Title: {title}, Impact: {impact}")
    flash(f"Change Request {cr_id} successfully submitted for CCB review.", "success")
    return redirect("/crs")

@app.route("/cr/<cr_id>/<action>", methods=["POST"])
@admin_required
def cr_action(cr_id, action):
    transitions = {
        "approve": ("Approved", "Approved by CCB"),
        "reject": ("Rejected", "Rejected by CCB: Outside baseline scope"),
        "implement": ("Implemented", "Implemented and verified via automated test gate")
    }
    if action in transitions:
        status, decision = transitions[action]
        now = f"{datetime.date.today():%Y-%m-%d}"
        ex("UPDATE change_requests SET status=?, decision=?, decision_date=? WHERE cr_id=?",
           (status, decision, now, cr_id))
        log_audit(current_user(), f"CR {cr_id} Decision: {status}", decision)
        flash(f"{cr_id} transition completed: Status is now '{status}'.", "success")
    return redirect("/crs")

@app.route("/cis")
@login_required
def cis():
    rows = ""
    for c in q("SELECT * FROM ci_register ORDER BY ci_id"):
        s_cls = "badge-success" if "Baselined" in c["status"] or c["approval"] == "Approved" else "badge-warning"
        rows += f"""
        <tr>
            <td><span class="mono" style="font-weight: 700;">{escape(c['ci_id'])}</span></td>
            <td><b>{escape(c['name'])}</b></td>
            <td><span class="badge badge-info">{escape(c['category'] or 'General')}</span></td>
            <td><span class="mono">{escape(c['version'])}</span></td>
            <td><span class="badge {s_cls}">{escape(c['status'])}</span></td>
            <td>{escape(c['owner'])}</td>
            <td><span class="badge badge-purple">{escape(c['baseline'] or 'BL-01')}</span></td>
            <td>{escape(c['approval'])}</td>
            <td style="font-size: 12px; color: var(--text-muted);">{escape(c['last_modified'] or '')}</td>
        </tr>
        """
    content = f"""
    <div class="card-panel">
        <div class="panel-header">
            <div class="panel-title">📋 Configuration Item (CI) Status Register</div>
            <div style="font-size: 13px; color: var(--text-muted);">20 Identified Configuration Items (Review-1 &amp; Review-2)</div>
        </div>
        <div class="table-responsive">
            <table>
                <thead>
                    <tr>
                        <th>CI ID</th>
                        <th>Configuration Item Name</th>
                        <th>Category</th>
                        <th>Version</th>
                        <th>Lifecycle Status</th>
                        <th>Owner</th>
                        <th>Baseline</th>
                        <th>Approval</th>
                        <th>Last Modified</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
        </div>
    </div>
    """
    return layout("Configuration Item Register", content, "/cis")

@app.route("/baselines")
@login_required
def baselines():
    rows = ""
    for b in q("SELECT * FROM baselines ORDER BY baseline_id"):
        rows += f"""
        <tr>
            <td><span class="badge badge-purple" style="font-size: 12px;">{escape(b['baseline_id'])}</span></td>
            <td><b>{escape(b['name'])}</b></td>
            <td><span class="mono">{escape(b['version'])}</span></td>
            <td><span class="badge badge-info">{escape(b['tag'] or 'untagged')}</span></td>
            <td><span class="mono">{escape(b['commit_hash'] or 'HEAD')}</span></td>
            <td>{escape(b['description'])}</td>
            <td>{escape(b['approver'])}</td>
            <td style="color: var(--text-muted); font-size: 12px;">{escape(b['approval_date'])}</td>
            <td><span class="badge badge-success">{escape(b['status'])}</span></td>
        </tr>
        """
    content = f"""
    <div class="card-panel">
        <div class="panel-header">
            <div class="panel-title">🏷️ Approved SCM Baselines &amp; Version Register</div>
            <div style="font-size: 13px; color: var(--text-muted);">Frozen Reference Points for Auditing and Release</div>
        </div>
        <div class="table-responsive">
            <table>
                <thead>
                    <tr>
                        <th>Baseline ID</th>
                        <th>Baseline Name</th>
                        <th>Version</th>
                        <th>Git Tag</th>
                        <th>Commit Hash</th>
                        <th>Description &amp; Scope</th>
                        <th>Approved By</th>
                        <th>Date</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
        </div>
    </div>
    """
    return layout("Baselines and Versions", content, "/baselines")

@app.route("/promotions")
@login_required
def promotions():
    rows = ""
    for p in q("SELECT * FROM promotions ORDER BY id DESC"):
        res_cls = "badge-success" if p["result"] == "PASSED" else "badge-failure"
        rows += f"""
        <tr>
            <td><b>{escape(p['item'])}</b></td>
            <td><span class="badge badge-neutral">{escape(p['from_level'])}</span></td>
            <td>&rarr;</td>
            <td><span class="badge badge-info">{escape(p['to_level'])}</span></td>
            <td><span class="badge {res_cls}">{escape(p['result'])}</span></td>
            <td>{escape(p['approver'])}</td>
            <td style="color: var(--text-muted); font-size: 12px;">{escape(p['promo_date'])}</td>
            <td><span class="mono">{escape(p['release_tag'] or '—')}</span></td>
            <td style="font-size: 12.5px;">{escape(p['reason'] or 'Gate passed')}</td>
        </tr>
        """

    eval_form = ""
    if is_admin():
        eval_form = """
        <div class="card-panel">
            <div class="panel-header">
                <div class="panel-title">🚀 Interactive Promotion Gate Evaluator</div>
                <div style="font-size: 12.5px; color: var(--text-muted);">Evaluate SCM verification criteria before promoting components</div>
            </div>
            <form method="post" action="/promotion/evaluate">
                <div class="form-row">
                    <div class="form-group" style="flex: 2;">
                        <label>Configuration Item</label>
                        <input name="item" value="CommitSleuth Suite" required>
                    </div>
                    <div class="form-group" style="flex: 1;">
                        <label>Current Level</label>
                        <select name="frm">
                            <option value="Development">Development</option>
                            <option value="Testing">Testing</option>
                        </select>
                    </div>
                    <div class="form-group" style="flex: 1;">
                        <label>Target Level</label>
                        <select name="to">
                            <option value="Testing">Testing</option>
                            <option value="Production">Production</option>
                        </select>
                    </div>
                    <div class="form-group" style="flex: 1;">
                        <label>Traceable Change Request</label>
                        <input name="cr_id" placeholder="e.g. CR-009" value="CR-009">
                    </div>
                    <div class="form-group" style="flex: 1;">
                        <label>Release Tag</label>
                        <input name="tag" placeholder="v1.0.0" value="v1.0.0">
                    </div>
                </div>
                <div class="form-row" style="margin-top: 18px;">
                    <label style="display: flex; align-items: center; gap: 8px; font-size: 13.5px; cursor: pointer;">
                        <input type="checkbox" name="tests_passed" value="yes" checked style="width: auto;">
                        <b>Automated Tests Verified Passing (Surefire / pytest)</b>
                    </label>
                    <button type="submit" class="btn" style="margin-left: auto;">Evaluate SCM Gate</button>
                </div>
            </form>
        </div>
        """

    content = f"""
    <div class="card-panel">
        <div class="panel-header">
            <div class="panel-title">🚀 Promotional Management &amp; Quality Gate History</div>
            <div style="font-size: 13px; color: var(--text-muted);">Development &rarr; Testing &rarr; Production Approval Gates</div>
        </div>
        <div class="table-responsive">
            <table>
                <thead>
                    <tr>
                        <th>Item</th>
                        <th>From Level</th>
                        <th></th>
                        <th>To Level</th>
                        <th>Quality Gate</th>
                        <th>Evaluator</th>
                        <th>Timestamp</th>
                        <th>Tag</th>
                        <th>Gate Validation Details</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
        </div>
    </div>
    {eval_form}
    """
    return layout("Promotional Management", content, "/promotions")

@app.route("/promotion/evaluate", methods=["POST"])
@admin_required
def promotion_evaluate():
    item = request.form.get("item", "CommitSleuth Suite")
    frm = request.form.get("frm", "Development")
    to = request.form.get("to", "Testing")
    cr_id = request.form.get("cr_id", "").strip() or None
    tag = request.form.get("tag", "").strip() or None
    tests_passed = request.form.get("tests_passed") == "yes"

    passed, reasons, _ = promote.evaluate_promotion(
        item=item, frm=frm, to=to, approver=current_user(),
        tests_passed=tests_passed, cr_id=cr_id, tag=tag
    )

    if passed:
        flash(f"PROMOTION PASSED: {item} successfully advanced to {to} under tag {tag or 'latest'}.", "success")
    else:
        flash(f"PROMOTION BLOCKED: {item} gate failure: {'; '.join(reasons)}", "error")

    return redirect("/promotions")

@app.route("/audits")
@login_required
def audits():
    rows = ""
    for a in q("SELECT * FROM audit_observations ORDER BY id"):
        sev_cls = "badge-failure" if a["severity"] in ("Critical", "Major") else "badge-warning" if a["severity"] == "Minor" else "badge-success"
        st_cls = "badge-success" if a["status"] == "Closed" else "badge-warning"
        rows += f"""
        <tr>
            <td><b>{escape(a['audit_id'])}</b></td>
            <td><span class="badge badge-purple">{escape(a['audit_type'])}</span></td>
            <td><b>{escape(a['checklist_item'])}</b></td>
            <td>{escape(a['observation'])}</td>
            <td style="font-size: 12px; color: var(--text-muted);">{escape(a['evidence'] or '')}</td>
            <td><span class="badge {sev_cls}">{escape(a['severity'])}</span></td>
            <td>{escape(a['owner'])}</td>
            <td><span class="badge {st_cls}">{escape(a['status'])}</span></td>
            <td style="font-size: 12px; color: var(--text-muted);">{escape(a['closure_date'] or 'Pending')}</td>
        </tr>
        """
    content = f"""
    <div class="card-panel">
        <div class="panel-header">
            <div class="panel-title">🛡️ Configuration Auditing System (CAS) — Observations Register</div>
            <div style="font-size: 13px; color: var(--text-muted);">Functional Configuration Audit (FCA) &amp; Physical Configuration Audit (PCA)</div>
        </div>
        <div class="table-responsive">
            <table>
                <thead>
                    <tr>
                        <th>Audit ID</th>
                        <th>Type</th>
                        <th>Checklist Item</th>
                        <th>Observation &amp; Finding</th>
                        <th>Verification Evidence</th>
                        <th>Severity</th>
                        <th>Owner</th>
                        <th>Status</th>
                        <th>Closure Date</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
        </div>
    </div>

    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 24px;">
        <div class="card-panel">
            <div class="panel-title" style="margin-bottom: 12px;">✅ Functional Configuration Audit (FCA) Checklist</div>
            <ul style="list-style: none; display: flex; flex-direction: column; gap: 10px; font-size: 13.5px;">
                <li style="display: flex; gap: 8px;"><span>✔</span> <span>All SRS requirements identified (FR-01 to FR-14, NFR-01, NFR-02)</span></li>
                <li style="display: flex; gap: 8px;"><span>✔</span> <span>Requirements-to-Test Traceability Matrix (100% test coverage)</span></li>
                <li style="display: flex; gap: 8px;"><span>✔</span> <span>Seeded defect failure detection verified (CalculatorTest assertion failure)</span></li>
                <li style="display: flex; gap: 8px;"><span>✔</span> <span>Build Log Parser verified against Maven compiler and Surefire outputs</span></li>
                <li style="display: flex; gap: 8px;"><span>✔</span> <span>Commit Ranking Engine verified with multi-candidate evidence scoring</span></li>
            </ul>
        </div>

        <div class="card-panel">
            <div class="panel-title" style="margin-bottom: 12px;">📦 Physical Configuration Audit (PCA) Checklist</div>
            <ul style="list-style: none; display: flex; flex-direction: column; gap: 10px; font-size: 13.5px;">
                <li style="display: flex; gap: 8px;"><span>✔</span> <span>Source code strictly matches approved baseline tag (empty git diff)</span></li>
                <li style="display: flex; gap: 8px;"><span>✔</span> <span>Required configuration files present: Jenkinsfile, pom.xml, scoring_config.yaml</span></li>
                <li style="display: flex; gap: 8px;"><span>✔</span> <span>Clean checkout reproducibility verified with <code>mvn clean test</code></span></li>
                <li style="display: flex; gap: 8px;"><span>✔</span> <span>Database schema matches System Design Document (SDD Table 12)</span></li>
                <li style="display: flex; gap: 8px;"><span>✔</span> <span>Release package checksums verified (SHA-256 manifest recorded)</span></li>
            </ul>
        </div>
    </div>
    """
    return layout("Configuration Auditing System", content, "/audits")

@app.route("/report")
@login_required
def report():
    report_text = status_reporter.build_csar()
    content = f"""
    <div class="card-panel">
        <div class="panel-header">
            <div class="panel-title">📑 Configuration Status Accounting Report (CSAR)</div>
            <div style="display: flex; gap: 10px;">
                <a href="/report/csv" class="btn btn-outline btn-sm">Download CSV Register</a>
            </div>
        </div>
        <p style="font-size: 13px; color: var(--text-muted); margin-bottom: 16px;">
            Formal status accounting document generated directly from live SQLite configuration tables.
        </p>
        <pre>{escape(report_text)}</pre>
    </div>
    """
    return layout("Status Accounting Report", content, "/report")

@app.route("/report/csv")
@login_required
def report_csv():
    csv_data = status_reporter.export_csar_csv()
    filename = f"CommitSleuth-CSAR-{datetime.date.today():%Y%m%d}.csv"
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename={filename}"}
    )

@app.route("/config")
@login_required
def config_page():
    cfg = load_cfg()
    raw_yaml = yaml.safe_dump(cfg, sort_keys=False, default_flow_style=False)
    
    edit_form = ""
    if is_admin():
        edit_form = f"""
        <div class="card-panel">
            <div class="panel-header">
                <div class="panel-title">⚙️ Update Attribution Weights &amp; Thresholds</div>
                <div style="font-size: 12.5px; color: var(--text-muted);">Dynamic Runtime Configuration</div>
            </div>
            <form method="post" action="/config/update">
                <div class="form-row">
                    <div class="form-group">
                        <label>File Match Weight (0.0 - 1.0)</label>
                        <input name="file_match" type="number" step="0.05" value="{cfg.get('weights', {}).get('file_match', 0.55)}" required>
                    </div>
                    <div class="form-group">
                        <label>POM Change Weight</label>
                        <input name="pom_change" type="number" step="0.05" value="{cfg.get('weights', {}).get('pom_change', 0.25)}" required>
                    </div>
                    <div class="form-group">
                        <label>Recency Weight</label>
                        <input name="recency" type="number" step="0.05" value="{cfg.get('weights', {}).get('recency', 0.10)}" required>
                    </div>
                    <div class="form-group">
                        <label>Change Size Weight</label>
                        <input name="change_size" type="number" step="0.05" value="{cfg.get('weights', {}).get('change_size', 0.10)}" required>
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label>Confidence Threshold for Revert</label>
                        <input name="confidence_threshold" type="number" step="0.05" value="{cfg.get('rollback', {}).get('confidence_threshold', 0.60)}" required>
                    </div>
                    <div class="form-group">
                        <label>Max Files for Isolation</label>
                        <input name="max_files" type="number" value="{cfg.get('rollback', {}).get('max_files_for_isolation', 3)}" required>
                    </div>
                    <div class="form-group">
                        <label>Notification Channel</label>
                        <select name="channel">
                            <option value="log" {'selected' if cfg.get('notification', {}).get('channel') == 'log' else ''}>Log File</option>
                            <option value="email" {'selected' if cfg.get('notification', {}).get('channel') == 'email' else ''}>Email (SMTP)</option>
                        </select>
                    </div>
                </div>
                <div style="margin-top: 16px;">
                    <button type="submit" class="btn">Save &amp; Reload Configuration</button>
                </div>
            </form>
        </div>
        """

    content = f"""
    {edit_form}
    <div class="card-panel">
        <div class="panel-header">
            <div class="panel-title">📄 Raw <code>scoring_config.yaml</code> Content</div>
            <div style="font-size: 12.5px; color: var(--text-muted);">Configuration Item under Version Control</div>
        </div>
        <pre>{escape(raw_yaml)}</pre>
    </div>
    """
    return layout("Customization & Tool Config", content, "/config")

@app.route("/config/update", methods=["POST"])
@admin_required
def config_update():
    f = request.form
    cfg = load_cfg()
    cfg["weights"]["file_match"] = float(f["file_match"])
    cfg["weights"]["pom_change"] = float(f["pom_change"])
    cfg["weights"]["recency"] = float(f["recency"])
    cfg["weights"]["change_size"] = float(f["change_size"])
    cfg["rollback"]["confidence_threshold"] = float(f["confidence_threshold"])
    cfg["rollback"]["max_files_for_isolation"] = int(f["max_files"])
    cfg["notification"]["channel"] = f["channel"]

    save_cfg(cfg)
    log_audit(current_user(), "Updated Scoring Weights", f"FileMatch={f['file_match']}, Threshold={f['confidence_threshold']}")
    flash("Attribution scoring weights and thresholds updated successfully.", "success")
    return redirect("/config")

@app.route("/audit-trail")
@login_required
def audit_trail():
    rows = ""
    for a in q("SELECT * FROM audit_trail ORDER BY id DESC LIMIT 50"):
        rows += f"""
        <tr>
            <td style="color: var(--text-muted); font-size: 12.5px;">{escape(a['timestamp'])}</td>
            <td><b>{escape(a['username'])}</b></td>
            <td><span class="badge badge-info">{escape(a['action'])}</span></td>
            <td style="font-size: 13px;">{escape(a['details'] or '')}</td>
        </tr>
        """
    content = f"""
    <div class="card-panel">
        <div class="panel-header">
            <div class="panel-title">🔒 Access Control &amp; SCM Action Audit Trail</div>
            <div style="font-size: 13px; color: var(--text-muted);">Immutable record of administrative and pipeline state changes</div>
        </div>
        <div class="table-responsive">
            <table>
                <thead>
                    <tr>
                        <th>Timestamp</th>
                        <th>User</th>
                        <th>Action</th>
                        <th>Details</th>
                    </tr>
                </thead>
                <tbody>
                    {rows or '<tr><td colspan="4" style="text-align: center; color: var(--text-muted);">No audit events recorded.</td></tr>'}
                </tbody>
            </table>
        </div>
    </div>
    """
    return layout("Security Audit Trail", content, "/audit-trail")

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
