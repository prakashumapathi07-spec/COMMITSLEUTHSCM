"""CommitSleuth Web Application — Automated Build Failure Tracking, Root-Cause Investigation & Developer Alert Platform.
Designed for TechNova Solutions (Employee Management System).
Light-Theme DevOps & Software Configuration Management (SCM) Portal.
"""
import os
import sys
import datetime
import json
import subprocess
from functools import wraps
from flask import Flask, request, redirect, session, flash, get_flashed_messages, Response, jsonify
from markupsafe import Markup, escape
from werkzeug.security import check_password_hash, generate_password_hash
import yaml

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "analyzer"))
from common import q, ex, log_audit, load_cfg, save_cfg, ROOT, connect

try:
    from common import initialize_schema
except ImportError:
    def initialize_schema():
        """Initializes database schema from schema.sql if tables do not exist."""
        schema_path = os.path.join(ROOT, "database", "schema.sql")
        if os.path.exists(schema_path):
            with connect() as con:
                with open(schema_path, "r", encoding="utf-8") as f:
                    con.executescript(f.read())

import status_reporter
import promote
import log_parser
import scorer

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "commitsleuth-technova-scm-2026-secret-key")

PROJECT_NAME = "TechNova Solutions"
SYSTEM_NAME = "Employee Management System"
REPO_URL = "https://github.com/prakashumapathi07-spec/COMMITSLEUTHSCM.git"
REPO_NAME = "prakashumapathi07-spec/COMMITSLEUTHSCM"
JENKINS_URL = os.environ.get("JENKINS_URL", "http://localhost:8080/job/CommitSleuth-Pipeline")

# SCM Navigation
NAV_GROUPS = [
    ("CORE OBSERVABILITY", [
        ("/", "Dashboard", "dashboard", "/"),
        ("/team", "Developer Team", "users", "/team"),
        ("/builds", "Build History", "layers", "/builds"),
        ("/failures/128", "Failure Investigation", "crosshair", "/failures"),
        ("/alerts", "Alerts & Notifications", "bell", "/alerts")
    ]),
    ("SCM GOVERNANCE", [
        ("/problems", "Problem Tracking", "alert-circle", "/problems"),
        ("/changes", "Change Management", "git-pull-request", "/changes"),
        ("/cis", "CI Register", "archive", "/cis"),
        ("/versions", "Baselines & Versions", "tag", "/versions"),
        ("/releases", "Promotions & Gates", "shield-check", "/releases"),
        ("/audits", "Audits (FCA / PCA)", "clipboard-check", "/audits"),
        ("/accounting", "Status Accounting", "file-text", "/accounting")
    ]),
    ("CONFIGURATION", [
        ("/settings", "Settings & Customization", "sliders", "/settings"),
        ("/audit-trail", "Audit Trail", "lock", "/audit-trail")
    ])
]

# SVG Icons Library (Lucide style, light crisp vectors)
ICONS = {
    "dashboard": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="9"></rect><rect x="14" y="3" width="7" height="5"></rect><rect x="14" y="12" width="7" height="9"></rect><rect x="3" y="16" width="7" height="5"></rect></svg>',
    "users": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M22 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>',
    "layers": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 2 7 12 12 22 7 12 2"></polygon><polyline points="2 17 12 22 22 17"></polyline><polyline points="2 12 12 17 22 12"></polyline></svg>',
    "crosshair": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="22" y1="12" x2="18" y2="12"></line><line x1="6" y1="12" x2="2" y2="12"></line><line x1="12" y1="6" x2="12" y2="2"></line><line x1="12" y1="22" x2="12" y2="18"></line></svg>',
    "bell": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path><path d="M13.73 21a2 2 0 0 1-3.46 0"></path></svg>',
    "alert-circle": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>',
    "git-pull-request": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="18" cy="18" r="3"></circle><circle cx="6" cy="6" r="3"></circle><path d="M13 6h3a2 2 0 0 1 2 2v7"></path><line x1="6" y1="9" x2="6" y2="21"></line></svg>',
    "archive": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="21 8 21 21 3 21 3 8"></polyline><rect x="1" y="3" width="22" height="5"></rect><line x1="10" y1="12" x2="14" y2="12"></line></svg>',
    "tag": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"></path><line x1="7" y1="7" x2="7.01" y2="7"></line></svg>',
    "shield-check": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path><polyline points="9 12 11 14 15 10"></polyline></svg>',
    "clipboard-check": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path><polyline points="13 14 15 16 19 12"></polyline></svg>',
    "file-text": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>',
    "sliders": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="4" y1="21" x2="4" y2="14"></line><line x1="4" y1="10" x2="4" y2="3"></line><line x1="12" y1="21" x2="12" y2="12"></line><line x1="12" y1="8" x2="12" y2="3"></line><line x1="20" y1="21" x2="20" y2="16"></line><line x1="20" y1="12" x2="20" y2="3"></line><line x1="1" y1="14" x2="7" y2="14"></line><line x1="9" y1="8" x2="15" y2="8"></line><line x1="17" y1="16" x2="23" y2="16"></line></svg>',
    "lock": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>',
    "check": '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>',
    "x": '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>',
    "play": '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>',
    "refresh": '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 4 23 10 17 10"></polyline><polyline points="1 20 1 14 7 14"></polyline><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path></svg>',
    "search": '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>',
    "external": '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>'
}

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
            flash("Permission Denied: Requires Developer or Administrator privileges.", "error")
            return redirect("/")
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            return redirect("/login")
        if not is_admin():
            flash("Permission Denied: Administrator role required for this configuration change.", "error")
            return redirect("/")
        return f(*args, **kwargs)
    return decorated

def get_unread_alert_count():
    try:
        rows = q("SELECT COUNT(*) as cnt FROM alerts WHERE acknowledged = 0")
        return rows[0]["cnt"] if rows else 0
    except Exception:
        return 0

def layout(title, content, active_path="/"):
    user = current_user()
    role = current_role()
    unread_alerts = get_unread_alert_count()
    
    # Navigation builder
    nav_html = ""
    for group_name, items in NAV_GROUPS:
        nav_html += f'<div class="nav-section-title">{group_name}</div>'
        for url, label, icon_key, prefix in items:
            is_active = "active" if (url == active_path or (prefix != "/" and active_path.startswith(prefix))) else ""
            icon_svg = ICONS.get(icon_key, "")
            badge = ""
            if icon_key == "bell" and unread_alerts > 0:
                badge = f'<span class="nav-badge-alert">{unread_alerts}</span>'
            nav_html += f'<a href="{url}" class="nav-item {is_active}"><span class="icon">{icon_svg}</span><span class="label">{escape(label)}</span>{badge}</a>'

    messages = get_flashed_messages(with_categories=True)
    msg_html = ""
    for category, msg in messages:
        c_class = "msg-error" if category == "error" else ("msg-warning" if category == "warning" else "msg-success")
        msg_html += f'<div class="alert-banner {c_class}"><span class="alert-icon">●</span><span>{escape(msg)}</span><button class="alert-close" onclick="this.parentElement.remove()">✕</button></div>'

    # Role switcher options
    role_options = [
        ("prakash", "admin", "Prakash Raj", "Lead / Admin"),
        ("bharath", "admin", "Bharathwaraj", "Admin / Auth"),
        ("karthik", "maintainer", "Karthik", "Developer / Reports"),
        ("divya", "maintainer", "Divya", "Developer / DB"),
        ("viewer", "viewer", "Auditor", "SCM Viewer")
    ]
    role_switcher_html = "".join([
        f'<a href="/switch-role?username={u}&role={r}" class="role-opt {"active-opt" if user == u else ""}"><span class="opt-name">{name}</span><span class="opt-badge">{role_lbl}</span></a>'
        for u, r, name, role_lbl in role_options
    ])

    user_info = ""
    if user:
        role_badge_class = "role-admin" if role == "admin" else ("role-maint" if role == "maintainer" else "role-viewer")
        user_info = f"""
        <div class="user-profile-widget">
            <div class="user-pill" onclick="document.getElementById('roleMenu').classList.toggle('show')">
                <span class="avatar-circle">{escape(user[0].upper())}</span>
                <div class="user-meta">
                    <span class="user-name">{escape(user)}</span>
                    <span class="role-badge {role_badge_class}">{escape(role.upper())}</span>
                </div>
                <span class="chevron-down">▾</span>
            </div>
            <div id="roleMenu" class="dropdown-menu">
                <div class="dropdown-header">Switch Scenario Identity</div>
                {role_switcher_html}
                <div class="dropdown-divider"></div>
                <a href="/logout" class="dropdown-item text-danger">Sign Out</a>
            </div>
        </div>
        """
    else:
        user_info = '<a href="/login" class="btn-signin">Sign In</a>'

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
            --bg-body: #f8fafc;
            --bg-surface: #ffffff;
            --bg-subtle: #f1f5f9;
            --border-color: #e2e8f0;
            --border-hover: #cbd5e1;
            
            --text-primary: #0f172a;
            --text-secondary: #475569;
            --text-muted: #64748b;
            
            --primary: #2563eb;
            --primary-light: #eff6ff;
            --primary-hover: #1d4ed8;
            
            --success: #10b981;
            --success-light: #ecfdf5;
            --success-border: #a7f3d0;
            --success-text: #065f46;
            
            --danger: #ef4444;
            --danger-light: #fef2f2;
            --danger-border: #fecaca;
            --danger-text: #991b1b;
            
            --warning: #f59e0b;
            --warning-light: #fffbeb;
            --warning-border: #fde68a;
            --warning-text: #92400e;
            
            --info: #0284c7;
            --info-light: #f0f9ff;
            --info-border: #bae6fd;
            --info-text: #0369a1;
            
            --purple: #8b5cf6;
            --purple-light: #f5f3ff;
            
            --radius-sm: 6px;
            --radius-md: 10px;
            --radius-lg: 14px;
            --shadow-subtle: 0 1px 3px 0 rgba(0, 0, 0, 0.04), 0 1px 2px -1px rgba(0, 0, 0, 0.04);
            --shadow-card: 0 1px 3px 0 rgba(0, 0, 0, 0.06), 0 1px 2px -1px rgba(0, 0, 0, 0.04);
            --shadow-hover: 0 4px 6px -1px rgba(0, 0, 0, 0.07), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
        }}
        
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg-body);
            color: var(--text-primary);
            min-height: 100vh;
            display: flex;
            line-height: 1.5;
            -webkit-font-smoothing: antialiased;
        }}
        
        /* Persistent Left Sidebar */
        aside.sidebar {{
            width: 256px;
            background: var(--bg-surface);
            border-right: 1px solid var(--border-color);
            display: flex;
            flex-direction: column;
            position: fixed;
            top: 0;
            left: 0;
            height: 100vh;
            z-index: 40;
        }}
        .brand-header {{
            padding: 18px 20px;
            display: flex;
            align-items: center;
            gap: 12px;
            border-bottom: 1px solid var(--border-color);
        }}
        .brand-icon {{
            width: 36px;
            height: 36px;
            background: linear-gradient(135deg, #2563eb, #3b82f6);
            border-radius: var(--radius-md);
            display: flex;
            align-items: center;
            justify-content: center;
            color: #ffffff;
            box-shadow: 0 2px 8px rgba(37, 99, 235, 0.25);
        }}
        .brand-title h1 {{
            font-size: 15px;
            font-weight: 800;
            letter-spacing: -0.02em;
            color: var(--text-primary);
            line-height: 1.2;
        }}
        .brand-title span {{
            font-size: 11px;
            color: var(--primary);
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        
        .sidebar-scroll {{
            flex: 1;
            overflow-y: auto;
            padding: 14px 12px;
            display: flex;
            flex-direction: column;
            gap: 2px;
        }}
        .nav-section-title {{
            font-size: 10.5px;
            font-weight: 700;
            color: var(--text-muted);
            letter-spacing: 0.06em;
            padding: 12px 10px 4px 10px;
            text-transform: uppercase;
        }}
        .nav-item {{
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 8px 12px;
            border-radius: var(--radius-sm);
            color: var(--text-secondary);
            text-decoration: none;
            font-size: 13px;
            font-weight: 500;
            transition: all 0.15s ease;
        }}
        .nav-item:hover {{
            background: var(--bg-subtle);
            color: var(--text-primary);
        }}
        .nav-item.active {{
            background: var(--primary-light);
            color: var(--primary);
            font-weight: 600;
        }}
        .nav-item .icon {{
            display: flex;
            align-items: center;
            justify-content: center;
            color: inherit;
        }}
        .nav-item .label {{ flex: 1; }}
        .nav-badge-alert {{
            background: var(--danger);
            color: #ffffff;
            font-size: 11px;
            font-weight: 700;
            padding: 1px 7px;
            border-radius: 10px;
        }}
        
        .sidebar-footer {{
            padding: 14px;
            border-top: 1px solid var(--border-color);
            background: #fafbfd;
            font-size: 11px;
            color: var(--text-muted);
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}
        .demo-control-box {{
            background: #ffffff;
            border: 1px solid var(--border-color);
            border-radius: var(--radius-sm);
            padding: 10px;
        }}
        .demo-control-title {{
            font-weight: 700;
            color: var(--text-primary);
            font-size: 11.5px;
            margin-bottom: 6px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        .demo-btn-group {{
            display: flex;
            flex-direction: column;
            gap: 5px;
        }}
        .btn-demo {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
            padding: 6px 10px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
            text-decoration: none;
            border: 1px solid transparent;
            cursor: pointer;
            transition: all 0.15s ease;
        }}
        .btn-demo-fail {{
            background: var(--danger-light);
            color: var(--danger-text);
            border-color: var(--danger-border);
        }}
        .btn-demo-fail:hover {{
            background: #fee2e2;
        }}
        .btn-demo-fix {{
            background: var(--success-light);
            color: var(--success-text);
            border-color: var(--success-border);
        }}
        .btn-demo-fix:hover {{
            background: #d1fae5;
        }}
        .btn-demo-reset {{
            background: var(--bg-subtle);
            color: var(--text-secondary);
            border-color: var(--border-color);
        }}
        .btn-demo-reset:hover {{
            background: #e2e8f0;
            color: var(--text-primary);
        }}
        
        /* Main Layout */
        .main-wrapper {{
            margin-left: 256px;
            flex: 1;
            display: flex;
            flex-direction: column;
            min-width: 0;
        }}
        
        /* Top Navigation Header */
        header.top-header {{
            height: 64px;
            background: var(--bg-surface);
            border-bottom: 1px solid var(--border-color);
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 28px;
            position: sticky;
            top: 0;
            z-index: 30;
        }}
        .header-left {{
            display: flex;
            align-items: center;
            gap: 16px;
        }}
        .project-selector {{
            display: flex;
            align-items: center;
            gap: 8px;
            background: var(--bg-subtle);
            padding: 6px 12px;
            border-radius: var(--radius-sm);
            border: 1px solid var(--border-color);
            font-size: 13px;
            font-weight: 600;
            color: var(--text-primary);
        }}
        .project-tag {{
            font-size: 11px;
            background: #ffffff;
            color: var(--primary);
            padding: 1px 6px;
            border-radius: 4px;
            border: 1px solid var(--border-color);
        }}
        .repo-badge {{
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 12px;
            color: var(--text-secondary);
            text-decoration: none;
            padding: 4px 8px;
            border-radius: 4px;
            background: #ffffff;
            border: 1px solid var(--border-color);
        }}
        .repo-badge:hover {{
            border-color: var(--primary);
            color: var(--primary);
        }}
        .branch-pill {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 11px;
            font-weight: 600;
            background: #e0f2fe;
            color: #0369a1;
            padding: 2px 7px;
            border-radius: 4px;
        }}
        
        .header-right {{
            display: flex;
            align-items: center;
            gap: 16px;
        }}
        .header-search {{
            display: flex;
            align-items: center;
            gap: 8px;
            background: var(--bg-subtle);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-sm);
            padding: 6px 12px;
            width: 220px;
        }}
        .header-search input {{
            border: none;
            background: transparent;
            font-size: 13px;
            color: var(--text-primary);
            outline: none;
            width: 100%;
        }}
        .header-btn-icon {{
            width: 36px;
            height: 36px;
            border-radius: var(--radius-sm);
            background: var(--bg-subtle);
            border: 1px solid var(--border-color);
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--text-secondary);
            text-decoration: none;
            position: relative;
        }}
        .header-btn-icon:hover {{
            background: #ffffff;
            color: var(--primary);
            border-color: var(--primary);
        }}
        .badge-counter {{
            position: absolute;
            top: -4px;
            right: -4px;
            background: var(--danger);
            color: #ffffff;
            font-size: 10px;
            font-weight: 700;
            width: 17px;
            height: 17px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            border: 2px solid #ffffff;
        }}
        
        .user-profile-widget {{
            position: relative;
        }}
        .user-pill {{
            display: flex;
            align-items: center;
            gap: 9px;
            padding: 4px 10px 4px 4px;
            background: var(--bg-subtle);
            border: 1px solid var(--border-color);
            border-radius: 30px;
            cursor: pointer;
            transition: all 0.15s ease;
        }}
        .user-pill:hover {{
            background: #ffffff;
            box-shadow: var(--shadow-subtle);
        }}
        .avatar-circle {{
            width: 28px;
            height: 28px;
            background: linear-gradient(135deg, #3b82f6, #1d4ed8);
            border-radius: 50%;
            color: #ffffff;
            font-weight: 700;
            font-size: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .user-meta {{
            display: flex;
            flex-direction: column;
            line-height: 1.1;
        }}
        .user-name {{
            font-size: 12px;
            font-weight: 700;
            color: var(--text-primary);
        }}
        .role-badge {{
            font-size: 9.5px;
            font-weight: 700;
            padding: 1px 4px;
            border-radius: 3px;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            margin-top: 2px;
            display: inline-block;
        }}
        .role-admin {{ background: #eff6ff; color: #1d4ed8; }}
        .role-maint {{ background: #f0fdf4; color: #15803d; }}
        .role-viewer {{ background: #f8fafc; color: #64748b; border: 1px solid var(--border-color); }}
        .chevron-down {{ font-size: 10px; color: var(--text-muted); }}
        
        .dropdown-menu {{
            display: none;
            position: absolute;
            top: calc(100% + 8px);
            right: 0;
            background: #ffffff;
            border: 1px solid var(--border-color);
            border-radius: var(--radius-md);
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
            width: 240px;
            z-index: 50;
            padding: 6px;
        }}
        .dropdown-menu.show {{ display: block; }}
        .dropdown-header {{
            font-size: 11px;
            font-weight: 700;
            color: var(--text-muted);
            text-transform: uppercase;
            padding: 8px 10px 4px;
        }}
        .role-opt {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 8px 10px;
            border-radius: var(--radius-sm);
            text-decoration: none;
            color: var(--text-primary);
            font-size: 12.5px;
            transition: background 0.15s ease;
        }}
        .role-opt:hover {{ background: var(--bg-subtle); }}
        .role-opt.active-opt {{ background: var(--primary-light); color: var(--primary); font-weight: 600; }}
        .opt-badge {{
            font-size: 10px;
            background: var(--bg-subtle);
            color: var(--text-muted);
            padding: 2px 6px;
            border-radius: 4px;
        }}
        .dropdown-divider {{ height: 1px; background: var(--border-color); margin: 6px 0; }}
        .dropdown-item {{
            display: block;
            padding: 8px 10px;
            border-radius: var(--radius-sm);
            text-decoration: none;
            color: var(--text-secondary);
            font-size: 12.5px;
        }}
        .dropdown-item:hover {{ background: var(--bg-subtle); }}
        .text-danger {{ color: var(--danger) !important; }}
        
        /* Content Area */
        main.content-area {{
            padding: 28px;
            flex: 1;
            max-width: 1600px;
            width: 100%;
            margin: 0 auto;
        }}
        
        .page-header {{
            margin-bottom: 24px;
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 16px;
        }}
        .page-header-title h2 {{
            font-size: 22px;
            font-weight: 800;
            color: var(--text-primary);
            letter-spacing: -0.02em;
        }}
        .page-header-title p {{
            font-size: 13.5px;
            color: var(--text-muted);
            margin-top: 2px;
        }}
        .page-actions {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        /* Alert Banners */
        .alert-banner {{
            padding: 12px 16px;
            border-radius: var(--radius-md);
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 12px;
            font-size: 13.5px;
            font-weight: 500;
        }}
        .msg-success {{ background: var(--success-light); color: var(--success-text); border: 1px solid var(--success-border); }}
        .msg-error {{ background: var(--danger-light); color: var(--danger-text); border: 1px solid var(--danger-border); }}
        .msg-warning {{ background: var(--warning-light); color: var(--warning-text); border: 1px solid var(--warning-border); }}
        .alert-close {{ margin-left: auto; background: none; border: none; font-size: 14px; cursor: pointer; color: inherit; opacity: 0.7; }}
        .alert-close:hover {{ opacity: 1; }}
        
        /* Metric Cards Grid */
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }}
        .metric-card {{
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-md);
            padding: 18px 20px;
            box-shadow: var(--shadow-subtle);
            position: relative;
            transition: all 0.2s ease;
        }}
        .metric-card:hover {{
            box-shadow: var(--shadow-card);
            border-color: var(--border-hover);
        }}
        .metric-label {{
            font-size: 12px;
            font-weight: 600;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.04em;
            margin-bottom: 6px;
        }}
        .metric-value {{
            font-size: 26px;
            font-weight: 800;
            color: var(--text-primary);
            letter-spacing: -0.03em;
            line-height: 1.1;
        }}
        .metric-sub {{
            font-size: 11.5px;
            color: var(--text-muted);
            margin-top: 6px;
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        .metric-sub.text-success {{ color: #059669; font-weight: 600; }}
        .metric-sub.text-danger {{ color: #dc2626; font-weight: 600; }}
        
        /* Card Containers */
        .card {{
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-md);
            box-shadow: var(--shadow-subtle);
            margin-bottom: 24px;
            overflow: hidden;
        }}
        .card-header {{
            padding: 16px 20px;
            border-bottom: 1px solid var(--border-color);
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: #ffffff;
        }}
        .card-title {{
            font-size: 15px;
            font-weight: 700;
            color: var(--text-primary);
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .card-body {{
            padding: 20px;
        }}
        
        /* Tables */
        .data-table-wrapper {{
            overflow-x: auto;
        }}
        table.data-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
            text-align: left;
        }}
        table.data-table th {{
            background: var(--bg-subtle);
            color: var(--text-secondary);
            font-weight: 600;
            font-size: 11.5px;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            padding: 10px 14px;
            border-bottom: 1px solid var(--border-color);
            white-space: nowrap;
        }}
        table.data-table td {{
            padding: 12px 14px;
            border-bottom: 1px solid var(--border-color);
            color: var(--text-primary);
            vertical-align: middle;
        }}
        table.data-table tr:last-child td {{
            border-bottom: none;
        }}
        table.data-table tr:hover td {{
            background: #fbfcfe;
        }}
        
        /* Badges */
        .badge {{
            display: inline-flex;
            align-items: center;
            gap: 4px;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            line-height: 1;
        }}
        .badge-success {{ background: var(--success-light); color: var(--success-text); border: 1px solid var(--success-border); }}
        .badge-failure {{ background: var(--danger-light); color: var(--danger-text); border: 1px solid var(--danger-border); }}
        .badge-unstable {{ background: var(--warning-light); color: var(--warning-text); border: 1px solid var(--warning-border); }}
        .badge-aborted {{ background: var(--bg-subtle); color: var(--text-secondary); border: 1px solid var(--border-color); }}
        .badge-running {{ background: var(--primary-light); color: var(--primary); border: 1px solid #bfdbfe; }}
        .badge-open {{ background: var(--danger-light); color: var(--danger-text); border: 1px solid var(--danger-border); }}
        .badge-investigating {{ background: var(--warning-light); color: var(--warning-text); border: 1px solid var(--warning-border); }}
        .badge-fixed {{ background: #eff6ff; color: #1e40af; border: 1px solid #bfdbfe; }}
        .badge-verified {{ background: var(--success-light); color: var(--success-text); border: 1px solid var(--success-border); }}
        .badge-resolved {{ background: var(--success-light); color: var(--success-text); border: 1px solid var(--success-border); }}
        
        /* Mini History Squares Matrix (Image 1 style) */
        .history-squares {{
            display: inline-flex;
            gap: 3px;
            align-items: center;
        }}
        .history-square {{
            width: 8px;
            height: 14px;
            border-radius: 2px;
        }}
        .sq-success {{ background: #10b981; }}
        .sq-failure {{ background: #ef4444; }}
        .sq-unstable {{ background: #f59e0b; }}
        .sq-aborted {{ background: #94a3b8; }}
        
        /* Code Pill */
        .code-pill {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 12px;
            background: var(--bg-subtle);
            color: var(--text-primary);
            padding: 2px 6px;
            border-radius: 4px;
            border: 1px solid var(--border-color);
        }}
        
        /* Buttons */
        .btn {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
            padding: 8px 14px;
            border-radius: var(--radius-sm);
            font-size: 13px;
            font-weight: 600;
            text-decoration: none;
            cursor: pointer;
            border: 1px solid transparent;
            transition: all 0.15s ease;
        }}
        .btn-primary {{
            background: var(--primary);
            color: #ffffff;
        }}
        .btn-primary:hover {{
            background: var(--primary-hover);
        }}
        .btn-secondary {{
            background: #ffffff;
            color: var(--text-primary);
            border-color: var(--border-color);
        }}
        .btn-secondary:hover {{
            background: var(--bg-subtle);
            border-color: var(--border-hover);
        }}
        .btn-sm {{
            padding: 4px 9px;
            font-size: 11.5px;
        }}
        
        /* Forms */
        .form-group {{
            margin-bottom: 16px;
        }}
        .form-label {{
            display: block;
            font-size: 12.5px;
            font-weight: 600;
            color: var(--text-secondary);
            margin-bottom: 6px;
        }}
        .form-control {{
            width: 100%;
            padding: 8px 12px;
            border: 1px solid var(--border-color);
            border-radius: var(--radius-sm);
            font-size: 13px;
            font-family: inherit;
            color: var(--text-primary);
            background: #ffffff;
            outline: none;
            transition: border-color 0.15s ease;
        }}
        .form-control:focus {{
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
        }}
        
        /* Log Terminal (Image 3 style) */
        .terminal-box {{
            background: #0f172a;
            color: #f8fafc;
            border-radius: var(--radius-md);
            font-family: 'JetBrains Mono', monospace;
            font-size: 12px;
            overflow: hidden;
            box-shadow: var(--shadow-card);
        }}
        .terminal-header {{
            background: #1e293b;
            padding: 10px 16px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-bottom: 1px solid #334155;
        }}
        .terminal-dots {{
            display: flex;
            gap: 6px;
        }}
        .terminal-dot {{
            width: 10px;
            height: 10px;
            border-radius: 50%;
        }}
        .dot-red {{ background: #ef4444; }}
        .dot-yellow {{ background: #f59e0b; }}
        .dot-green {{ background: #10b981; }}
        .terminal-title {{
            font-size: 11px;
            color: #94a3b8;
            font-weight: 600;
        }}
        .terminal-body {{
            padding: 16px;
            max-height: 480px;
            overflow-y: auto;
            line-height: 1.6;
        }}
        .log-line {{
            display: flex;
            gap: 12px;
            white-space: pre-wrap;
            word-break: break-all;
        }}
        .log-num {{
            color: #64748b;
            user-select: none;
            text-align: right;
            width: 32px;
            flex-shrink: 0;
        }}
        .log-text {{ flex: 1; }}
        .log-info {{ color: #94a3b8; }}
        .log-pass {{ color: #34d399; font-weight: 600; }}
        .log-fail {{ color: #f87171; font-weight: 700; background: rgba(239, 68, 68, 0.1); border-left: 2px solid #ef4444; padding-left: 4px; }}
        .log-warn {{ color: #fbbf24; }}
        
        /* Interactive Grid Layouts */
        .two-col-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 24px;
        }}
        .investigation-grid {{
            display: grid;
            grid-template-columns: 1.3fr 1fr;
            gap: 24px;
        }}
        
        @media (max-width: 1024px) {{
            .two-col-grid, .investigation-grid {{
                grid-template-columns: 1fr;
            }}
            aside.sidebar {{
                width: 70px;
            }}
            aside.sidebar .brand-title,
            aside.sidebar .nav-section-title,
            aside.sidebar .label,
            aside.sidebar .sidebar-footer,
            aside.sidebar .nav-badge-alert {{
                display: none;
            }}
            .main-wrapper {{
                margin-left: 70px;
            }}
        }}
    </style>
</head>
<body>
    <!-- Persistent Left Sidebar -->
    <aside class="sidebar">
        <div class="brand-header">
            <div class="brand-icon">
                {ICONS['crosshair']}
            </div>
            <div class="brand-title">
                <h1>CommitSleuth</h1>
                <span>{PROJECT_NAME}</span>
            </div>
        </div>
        
        <div class="sidebar-scroll">
            {nav_html}
        </div>
        
        <div class="sidebar-footer">
            <div class="demo-control-box">
                <div class="demo-control-title">
                    <span>Scenario Controller</span>
                    <span class="badge badge-unstable" style="font-size:9px;">Live SCM</span>
                </div>
                <div class="demo-btn-group">
                    <a href="/api/demo/run-failure" class="btn-demo btn-demo-fail" title="Karthik defect in ReportService.java [CR-009]">
                        <span>{ICONS['play']}</span> 1. Karthik Defect (#128)
                    </a>
                    <a href="/api/demo/run-fix" class="btn-demo btn-demo-fix" title="Karthik corrective fix in ReportService.java [CR-010]">
                        <span>{ICONS['check']}</span> 2. Karthik Fix (#129)
                    </a>
                    <a href="/api/demo/reset" class="btn-demo btn-demo-reset" title="Reset sample records">
                        <span>{ICONS['refresh']}</span> Reset State
                    </a>
                </div>
            </div>
            <div style="font-size: 10.5px; text-align: center;">
                Academic SCM Review Final
            </div>
        </div>
    </aside>

    <!-- Main Wrapper -->
    <div class="main-wrapper">
        <!-- Top Sticky Header -->
        <header class="top-header">
            <div class="header-left">
                <div class="project-selector">
                    <span>🏢 {PROJECT_NAME}</span>
                    <span class="project-tag">{SYSTEM_NAME}</span>
                </div>
                <a href="{REPO_URL}" target="_blank" class="repo-badge">
                    <span>📦 {REPO_NAME}</span>
                    <span class="branch-pill">main</span>
                    <span>{ICONS['external']}</span>
                </a>
            </div>
            
            <div class="header-right">
                <div class="header-search">
                    <span>{ICONS['search']}</span>
                    <input type="text" placeholder="Search builds, commits, CIs..." onkeydown="if(event.key==='Enter') window.location.href='/builds?q='+encodeURIComponent(this.value)">
                </div>
                
                <a href="/alerts" class="header-btn-icon" title="Alerts & Notifications">
                    {ICONS['bell']}
                    {f'<span class="badge-counter">{unread_alerts}</span>' if unread_alerts > 0 else ''}
                </a>
                
                {user_info}
            </div>
        </header>

        <!-- Main Dynamic Content Area -->
        <main class="content-area">
            {msg_html}
            {content}
        </main>
    </div>

    <script>
        // Close dropdown when clicked outside
        window.onclick = function(e) {{
            if (!e.target.closest('.user-profile-widget')) {{
                var menus = document.getElementsByClassName("dropdown-menu");
                for (var i = 0; i < menus.length; i++) {{
                    menus[i].classList.remove('show');
                }}
            }}
        }}
    </script>
</body>
</html>
"""

# =========================================================================
# AUTHENTICATION & SCENARIO ROLE SWITCHING
# =========================================================================

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        
        row = q("SELECT * FROM users WHERE username=?", (username,))
        if row and check_password_hash(row[0]["password_hash"], password):
            session["user"] = username
            session["role"] = row[0]["role"]
            log_audit(username, "Portal Authentication", f"Successful sign-in with role: {row[0]['role']}")
            flash(f"Welcome back, {row[0]['full_name']}! Signed in as {row[0]['role'].upper()}.", "success")
            return redirect("/")
        else:
            flash("Invalid credentials. Try: prakash / admin123 or karthik / maint123", "error")
            return redirect("/login")

    # Clean Light Theme Login Page
    return f"""<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>CommitSleuth Portal Access</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        body {{
            font-family: 'Inter', sans-serif;
            background: #f8fafc;
            color: #0f172a;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }}
        .login-card {{
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 14px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
            width: 100%;
            max-width: 440px;
            padding: 36px 32px;
        }}
        .brand-badge {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: #eff6ff;
            color: #2563eb;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 700;
            margin-bottom: 16px;
        }}
        h2 {{ font-size: 22px; font-weight: 800; margin-bottom: 6px; }}
        p {{ font-size: 13.5px; color: #64748b; margin-bottom: 24px; }}
        .form-group {{ margin-bottom: 16px; }}
        label {{ display: block; font-size: 12.5px; font-weight: 600; margin-bottom: 6px; color: #334155; }}
        input {{ width: 100%; padding: 10px 14px; border: 1px solid #cbd5e1; border-radius: 8px; font-size: 14px; }}
        input:focus {{ outline: none; border-color: #2563eb; box-shadow: 0 0 0 3px rgba(37,99,235,0.1); }}
        button {{ width: 100%; padding: 11px; background: #2563eb; color: #ffffff; border: none; border-radius: 8px; font-size: 14px; font-weight: 700; cursor: pointer; }}
        button:hover {{ background: #1d4ed8; }}
        .demo-roles {{
            margin-top: 24px;
            padding-top: 20px;
            border-top: 1px solid #e2e8f0;
            font-size: 12px;
            color: #64748b;
        }}
        .role-btn {{
            display: inline-block;
            background: #f1f5f9;
            color: #334155;
            padding: 4px 8px;
            border-radius: 4px;
            text-decoration: none;
            margin: 3px;
            font-weight: 600;
        }}
        .role-btn:hover {{ background: #e2e8f0; color: #0f172a; }}
    </style>
</head>
<body>
    <div class="login-card">
        <div class="brand-badge">CommitSleuth SCM Review</div>
        <h2>CommitSleuth Portal Access</h2>
        <p>TechNova Solutions — Automated Failure Attribution & SCM Platform</p>
        
        <form method="POST">
            <div class="form-group">
                <label>Username</label>
                <input type="text" name="username" value="prakash" required autofocus>
            </div>
            <div class="form-group">
                <label>Password</label>
                <input type="password" name="password" value="admin123" required>
            </div>
            <button type="submit">Sign In to Dashboard</button>
        </form>
        
        <div class="demo-roles">
            <div style="font-weight:700; margin-bottom: 6px;">One-Click Quick Login:</div>
            <a href="/switch-role?username=prakash&role=admin" class="role-btn">Prakash Raj (Lead)</a>
            <a href="/switch-role?username=bharath&role=admin" class="role-btn">Bharathwaraj (Auth)</a>
            <a href="/switch-role?username=karthik&role=maintainer" class="role-btn">Karthik (Reports)</a>
            <a href="/switch-role?username=divya&role=maintainer" class="role-btn">Divya (Database)</a>
            <a href="/switch-role?username=viewer&role=viewer" class="role-btn">Auditor (Viewer)</a>
        </div>
    </div>
</body>
</html>
"""

@app.route("/switch-role")
def switch_role():
    username = request.args.get("username", "prakash")
    role = request.args.get("role", "admin")
    session["user"] = username
    session["role"] = role
    log_audit(username, "Role Context Switch", f"Switched active persona to {username} ({role})")
    flash(f"Switched persona to: {username.capitalize()} ({role.upper()})", "success")
    return redirect(request.referrer or "/")

@app.route("/logout")
def logout():
    user = session.pop("user", None)
    session.pop("role", None)
    if user:
        log_audit(user, "User Signout", "Ended authenticated session")
    return redirect("/login")

# =========================================================================
# PAGE A: OVERVIEW DASHBOARD (/ and /dashboard)
# =========================================================================

@app.route("/")
@app.route("/dashboard")
@login_required
def dashboard():
    # Calculated metrics from database
    build_counts = q("SELECT result, COUNT(*) as cnt FROM builds GROUP BY result")
    counts_map = {r["result"]: r["cnt"] for r in build_counts}
    
    total_builds = sum(counts_map.values())
    success_builds = counts_map.get("SUCCESS", 0)
    failed_builds = counts_map.get("FAILURE", 0)
    unstable_builds = counts_map.get("UNSTABLE", 0)
    
    success_rate = round((success_builds / total_builds * 100), 1) if total_builds > 0 else 100.0
    
    open_problems_row = q("SELECT COUNT(*) as cnt FROM problems WHERE status NOT IN ('Closed', 'Resolved')")
    open_problems = open_problems_row[0]["cnt"] if open_problems_row else 0
    
    unread_alerts = get_unread_alert_count()
    
    avg_dur_row = q("SELECT AVG(duration_sec) as avg_d FROM builds")
    avg_duration = round(avg_dur_row[0]["avg_d"] or 38.5, 1) if avg_dur_row else 38.5
    
    latest_release_row = q("SELECT version, approval_status FROM releases ORDER BY created DESC LIMIT 1")
    latest_release = f"{latest_release_row[0]['version']} ({latest_release_row[0]['approval_status']})" if latest_release_row else "v1.0.0 (Approved)"

    # Recent Builds
    recent_builds = q("SELECT * FROM builds ORDER BY build_no DESC LIMIT 8")
    
    # 4 Developers Summary
    devs = q("SELECT * FROM developers ORDER BY id ASC")
    
    # Active Problems
    active_problems = q("SELECT * FROM problems WHERE status NOT IN ('Closed', 'Resolved') ORDER BY id DESC LIMIT 5")
    if not active_problems:
        # Show recent problem if all resolved
        active_problems = q("SELECT * FROM problems ORDER BY id DESC LIMIT 3")

    # Recent Alerts
    recent_alerts = q("SELECT * FROM alerts ORDER BY id DESC LIMIT 4")

    # Build Rows HTML with Image 1 style History Square Matrix
    build_rows_html = ""
    for b in recent_builds:
        res = b["result"]
        badge_cls = "badge-success" if res == "SUCCESS" else ("badge-failure" if res == "FAILURE" else "badge-unstable")
        
        # Mini history blocks (simulation of recent 10 build statuses)
        sq_class = "sq-success" if res == "SUCCESS" else ("sq-failure" if res == "FAILURE" else "sq-unstable")
        history_blocks = f'<div class="history-squares"><span class="history-square {sq_class}"></span><span class="history-square sq-success"></span><span class="history-square sq-success"></span><span class="history-square sq-success"></span><span class="history-square sq-success"></span><span class="history-square sq-success"></span><span class="history-square sq-success"></span><span class="history-square sq-success"></span></div>'
        
        test_pct = "100%" if res == "SUCCESS" else ("90%" if res == "FAILURE" else "95%")
        test_pct_cls = "badge-success" if res == "SUCCESS" else "badge-failure"

        build_rows_html += f"""
        <tr>
            <td>
                <div style="font-weight: 600; color: var(--primary);">{escape(b['job_name'] or 'backend/report-service')}</div>
                <div style="font-size: 11px; color: var(--text-muted);">{escape(b['commit_message'] or 'routine update')}</div>
            </td>
            <td>
                <a href="/builds/{b['build_no']}" class="code-pill" style="font-weight: 700;">#{b['build_no']}</a>
            </td>
            <td><span class="badge {badge_cls}">{res}</span></td>
            <td><span class="branch-pill">{escape(b['branch'])}</span></td>
            <td><span class="code-pill">{escape(b['commit_hash'])}</span></td>
            <td>{escape(b['author'] or 'Developer')}</td>
            <td>{history_blocks}</td>
            <td>{b['duration_sec']}s</td>
            <td><span class="badge {test_pct_cls}">{test_pct}</span></td>
            <td>
                <a href="/builds/{b['build_no']}" class="btn btn-secondary btn-sm">Details</a>
            </td>
        </tr>
        """

    # Developer Cards HTML
    dev_cards_html = ""
    for d in devs:
        # Calculate stats for developer
        d_builds = q("SELECT COUNT(*) as tot, SUM(CASE WHEN result='SUCCESS' THEN 1 ELSE 0 END) as passed, SUM(CASE WHEN result='FAILURE' THEN 1 ELSE 0 END) as failed FROM builds WHERE author LIKE ?", (f"%{d['name']}%",))
        tot = d_builds[0]["tot"] if d_builds else 0
        passed = d_builds[0]["passed"] or 0
        failed = d_builds[0]["failed"] or 0
        
        d_probs = q("SELECT COUNT(*) as cnt FROM problems WHERE assignee LIKE ? AND status NOT IN ('Closed', 'Resolved')", (f"%{d['name']}%",))
        p_cnt = d_probs[0]["cnt"] if d_probs else 0
        
        dev_cards_html += f"""
        <div style="background: #ffffff; border: 1px solid var(--border-color); border-radius: var(--radius-sm); padding: 14px; display: flex; align-items: center; justify-content: space-between;">
            <div style="display: flex; align-items: center; gap: 12px;">
                <div style="width: 38px; height: 38px; border-radius: 50%; background: {d['avatar_color']}; color: #ffffff; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 14px;">
                    {escape(d['name'][0])}
                </div>
                <div>
                    <div style="font-weight: 700; font-size: 13.5px; color: var(--text-primary);">{escape(d['name'])}</div>
                    <div style="font-size: 11px; color: var(--text-muted);">{escape(d['module'])} · <span class="branch-pill" style="font-size: 10px;">{escape(d['branch'])}</span></div>
                </div>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 12px; font-weight: 700;">
                    <span style="color: var(--success);">{passed} passed</span> / <span style="color: var(--danger);">{failed} failed</span>
                </div>
                <div style="font-size: 11px; color: var(--text-muted);">
                    {f'<span class="badge badge-failure" style="font-size:9.5px;">{p_cnt} Open Defect</span>' if p_cnt > 0 else '<span style="color: var(--success);">✓ 0 open issues</span>'}
                </div>
            </div>
        </div>
        """

    # Active Problems HTML
    problem_items_html = ""
    for p in active_problems:
        p_status = p["status"]
        st_cls = "badge-open" if p_status == "Open" else ("badge-investigating" if p_status in ("Investigating", "Fix Submitted") else "badge-resolved")
        problem_items_html += f"""
        <div style="padding: 12px 14px; border-bottom: 1px solid var(--border-color); display: flex; align-items: center; justify-content: space-between;">
            <div>
                <div style="display: flex; align-items: center; gap: 8px;">
                    <a href="/failures/{p['build_no']}" class="code-pill" style="font-weight: 700; color: var(--danger);">{escape(p['problem_code'])}</a>
                    <span class="badge {st_cls}">{escape(p_status)}</span>
                    <span style="font-size: 11px; color: var(--text-muted);">Build #{p['build_no']}</span>
                </div>
                <div style="font-size: 12.5px; font-weight: 600; color: var(--text-primary); margin-top: 4px;">
                    {escape(p['title'] or p['error_message'][:75])}
                </div>
                <div style="font-size: 11px; color: var(--text-muted); margin-top: 2px;">
                    Assignee: <strong>{escape(p['assignee'])}</strong> · Suspect Commit: <span class="code-pill" style="font-size: 10px;">{escape(p['suspect_commit'])}</span> (Conf: {p['confidence']})
                </div>
            </div>
            <div>
                <a href="/failures/{p['build_no']}" class="btn btn-secondary btn-sm">Investigate</a>
            </div>
        </div>
        """

    content = f"""
    <div class="page-header">
        <div class="page-header-title">
            <h2>Executive SCM Dashboard</h2>
            <p>Continuous Integration, Build Failure Attribution & Configuration Management for {PROJECT_NAME}</p>
        </div>
        <div class="page-actions">
            <span class="badge badge-running" style="padding: 6px 12px; font-size: 12px;">● Jenkins CI Pipeline Connected</span>
            <a href="/builds" class="btn btn-secondary btn-sm">View All Builds</a>
        </div>
    </div>

    <!-- Top KPI Metrics Cards -->
    <div class="metrics-grid">
        <div class="metric-card">
            <div class="metric-label">Total Builds</div>
            <div class="metric-value">{total_builds}</div>
            <div class="metric-sub text-success">
                <span>{ICONS['check']}</span> 100% CI pipeline coverage
            </div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Successful Builds</div>
            <div class="metric-value" style="color: var(--success);">{success_builds}</div>
            <div class="metric-sub">
                Passed Maven Surefire tests
            </div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Failed Builds</div>
            <div class="metric-value" style="color: var(--danger);">{failed_builds}</div>
            <div class="metric-sub text-danger">
                Attributed via CommitSleuth
            </div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Build Success Rate</div>
            <div class="metric-value">{success_rate}%</div>
            <div class="metric-sub">
                {unstable_builds} unstable warning(s)
            </div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Active Problems</div>
            <div class="metric-value" style="color: {'var(--danger)' if open_problems > 0 else 'var(--success)'};">{open_problems}</div>
            <div class="metric-sub">
                {f'<a href="/problems" style="color:inherit; font-weight:700;">View {open_problems} Open Defect</a>' if open_problems > 0 else 'All defects resolved'}
            </div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Unread Alerts</div>
            <div class="metric-value" style="color: {'var(--warning)' if unread_alerts > 0 else 'var(--text-muted)'};">{unread_alerts}</div>
            <div class="metric-sub">
                <a href="/alerts" style="color:inherit;">Alert center</a>
            </div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Avg Build Duration</div>
            <div class="metric-value">{avg_duration}s</div>
            <div class="metric-sub">
                Maven compilation & JUnit
            </div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Release Gate Status</div>
            <div class="metric-value" style="font-size: 18px; color: var(--primary);">{escape(latest_release)}</div>
            <div class="metric-sub">
                Baseline BL-05 Verified
            </div>
        </div>
    </div>

    <!-- Charts Row (Image 1 Style: Build Trends & Status by Job) -->
    <div class="two-col-grid" style="margin-bottom: 24px;">
        <!-- Build Trends Stacked Area Chart -->
        <div class="card" style="margin-bottom: 0;">
            <div class="card-header">
                <div class="card-title">
                    <span>Build Trends (30 Days)</span>
                </div>
                <div style="display: flex; gap: 8px; font-size: 11px; align-items: center;">
                    <span style="color: #10b981; font-weight:700;">● Success ({success_builds})</span>
                    <span style="color: #ef4444; font-weight:700;">● Failure ({failed_builds})</span>
                    <span style="color: #f59e0b; font-weight:700;">● Unstable ({unstable_builds})</span>
                </div>
            </div>
            <div class="card-body" style="padding: 16px 20px;">
                <!-- Embedded Responsive SVG Stacked Chart -->
                <svg viewBox="0 0 540 200" style="width: 100%; height: auto; overflow: visible;">
                    <defs>
                        <linearGradient id="gradSuccess" x1="0%" y1="0%" x2="0%" y2="100%">
                            <stop offset="0%" stop-color="#10b981" stop-opacity="0.35"/>
                            <stop offset="100%" stop-color="#10b981" stop-opacity="0.05"/>
                        </linearGradient>
                        <linearGradient id="gradFailure" x1="0%" y1="0%" x2="0%" y2="100%">
                            <stop offset="0%" stop-color="#ef4444" stop-opacity="0.4"/>
                            <stop offset="100%" stop-color="#ef4444" stop-opacity="0.05"/>
                        </linearGradient>
                    </defs>
                    <!-- Grid Lines -->
                    <line x1="40" y1="20" x2="520" y2="20" stroke="#f1f5f9" stroke-width="1"/>
                    <line x1="40" y1="65" x2="520" y2="65" stroke="#f1f5f9" stroke-width="1"/>
                    <line x1="40" y1="110" x2="520" y2="110" stroke="#f1f5f9" stroke-width="1"/>
                    <line x1="40" y1="155" x2="520" y2="155" stroke="#e2e8f0" stroke-width="1"/>
                    
                    <!-- Y-Axis Labels -->
                    <text x="30" y="24" fill="#94a3b8" font-size="10" text-anchor="end">12</text>
                    <text x="30" y="69" fill="#94a3b8" font-size="10" text-anchor="end">8</text>
                    <text x="30" y="114" fill="#94a3b8" font-size="10" text-anchor="end">4</text>
                    <text x="30" y="159" fill="#94a3b8" font-size="10" text-anchor="end">0</text>
                    
                    <!-- Stacked Curves -->
                    <!-- Success Area -->
                    <path d="M 40,155 L 40,85 C 90,55 140,95 190,65 C 240,45 290,85 340,55 C 390,35 440,65 520,40 L 520,155 Z" fill="url(#gradSuccess)"/>
                    <path d="M 40,85 C 90,55 140,95 190,65 C 240,45 290,85 340,55 C 390,35 440,65 520,40" fill="none" stroke="#10b981" stroke-width="2.5"/>
                    
                    <!-- Failure Peak (Defect Build 128) -->
                    <path d="M 330,155 L 340,90 C 360,70 380,60 395,95 L 405,155 Z" fill="url(#gradFailure)"/>
                    <path d="M 340,90 C 360,70 380,60 395,95" fill="none" stroke="#ef4444" stroke-width="2.5"/>
                    
                    <!-- Interactive Callout on Defect Build -->
                    <circle cx="365" cy="65" r="4.5" fill="#ef4444" stroke="#ffffff" stroke-width="2"/>
                    <rect x="330" y="18" width="95" height="34" rx="4" fill="#0f172a" opacity="0.9"/>
                    <text x="377" y="32" fill="#ffffff" font-size="9.5" font-weight="700" text-anchor="middle">Build #128 FAIL</text>
                    <text x="377" y="44" fill="#cbd5e1" font-size="8.5" text-anchor="middle">Karthik (Reports)</text>

                    <!-- X-Axis Labels -->
                    <text x="40" y="175" fill="#94a3b8" font-size="10">Oct 01</text>
                    <text x="140" y="175" fill="#94a3b8" font-size="10">Oct 08</text>
                    <text x="260" y="175" fill="#94a3b8" font-size="10">Oct 15</text>
                    <text x="380" y="175" fill="#94a3b8" font-size="10">Oct 22 (#128)</text>
                    <text x="500" y="175" fill="#94a3b8" font-size="10">Current</text>
                </svg>
            </div>
        </div>

        <!-- Build Status by Job Stacked Bar Chart -->
        <div class="card" style="margin-bottom: 0;">
            <div class="card-header">
                <div class="card-title">
                    <span>Build Status by Module & Service</span>
                </div>
                <span class="badge badge-success" style="font-size: 10px;">TechNova Architecture</span>
            </div>
            <div class="card-body" style="padding: 16px 20px;">
                <svg viewBox="0 0 540 200" style="width: 100%; height: auto; overflow: visible;">
                    <!-- Baseline line -->
                    <line x1="40" y1="155" x2="520" y2="155" stroke="#e2e8f0" stroke-width="1"/>
                    
                    <!-- Bars: 4 Modules -->
                    <!-- 1. backend/employee-service -->
                    <rect x="60" y="35" width="60" height="95" rx="3" fill="#10b981"/>
                    <rect x="60" y="130" width="60" height="25" rx="3" fill="#f59e0b"/>
                    <text x="90" y="172" fill="#475569" font-size="10" font-weight="600" text-anchor="middle">employee-svc</text>
                    <text x="90" y="185" fill="#94a3b8" font-size="9" text-anchor="middle">Prakash</text>

                    <!-- 2. backend/auth-service -->
                    <rect x="180" y="25" width="60" height="130" rx="3" fill="#10b981"/>
                    <text x="210" y="172" fill="#475569" font-size="10" font-weight="600" text-anchor="middle">auth-svc</text>
                    <text x="210" y="185" fill="#94a3b8" font-size="9" text-anchor="middle">Bharathwaraj</text>

                    <!-- 3. backend/report-service (Contains Seeded Failure) -->
                    <rect x="300" y="40" width="60" height="80" rx="3" fill="#10b981"/>
                    <rect x="300" y="120" width="60" height="35" rx="3" fill="#ef4444"/>
                    <text x="330" y="172" fill="#475569" font-size="10" font-weight="600" text-anchor="middle">report-svc</text>
                    <text x="330" y="185" fill="#ef4444" font-size="9" font-weight="700" text-anchor="middle">Karthik (Defect)</text>

                    <!-- 4. backend/db-service -->
                    <rect x="420" y="30" width="60" height="125" rx="3" fill="#10b981"/>
                    <text x="450" y="172" fill="#475569" font-size="10" font-weight="600" text-anchor="middle">db-svc</text>
                    <text x="450" y="185" fill="#94a3b8" font-size="9" text-anchor="middle">Divya</text>
                </svg>
            </div>
        </div>
    </div>

    <!-- Middle Split: 4-Developer Panel and Active Problems -->
    <div class="two-col-grid" style="margin-bottom: 24px;">
        <!-- Four Developers Activity Panel -->
        <div class="card" style="margin-bottom: 0;">
            <div class="card-header">
                <div class="card-title">
                    <span>{ICONS['users']}</span>
                    <span>TechNova Engineering Team (4 Developers)</span>
                </div>
                <a href="/team" class="btn btn-secondary btn-sm">Team Roster</a>
            </div>
            <div class="card-body" style="padding: 12px; display: flex; flex-direction: column; gap: 10px;">
                {dev_cards_html}
            </div>
        </div>

        <!-- Active Problems & Recent Alerts -->
        <div class="card" style="margin-bottom: 0;">
            <div class="card-header">
                <div class="card-title">
                    <span>{ICONS['alert-circle']}</span>
                    <span>Problem Records & Attribution</span>
                </div>
                <a href="/problems" class="btn btn-secondary btn-sm">All Problems</a>
            </div>
            <div style="padding: 0;">
                {problem_items_html}
            </div>
        </div>
    </div>

    <!-- Recent Build History Table (Image 1 Style) -->
    <div class="card">
        <div class="card-header">
            <div class="card-title">
                <span>{ICONS['layers']}</span>
                <span>Recent Pipeline Builds & Test Executions</span>
            </div>
            <div style="display: flex; gap: 8px;">
                <a href="/builds" class="btn btn-secondary btn-sm">Full History Table</a>
            </div>
        </div>
        <div class="data-table-wrapper">
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Job / Module</th>
                        <th>Build #</th>
                        <th>Status</th>
                        <th>Branch</th>
                        <th>Commit</th>
                        <th>Author</th>
                        <th>History</th>
                        <th>Duration</th>
                        <th>Tests</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
                    {build_rows_html}
                </tbody>
            </table>
        </div>
    </div>
    """
    return layout("Executive SCM Dashboard", content, "/")

# =========================================================================
# PAGE B: DEVELOPER TEAM (/team)
# =========================================================================

@app.route("/team")
@login_required
def team():
    devs = q("SELECT * FROM developers ORDER BY id ASC")
    
    cards_html = ""
    for d in devs:
        # Build query for developer commits & builds
        b_rows = q("SELECT COUNT(*) as tot, SUM(CASE WHEN result='SUCCESS' THEN 1 ELSE 0 END) as passed, SUM(CASE WHEN result='FAILURE' THEN 1 ELSE 0 END) as failed FROM builds WHERE author LIKE ?", (f"%{d['name']}%",))
        tot = b_rows[0]["tot"] if b_rows else 0
        passed = b_rows[0]["passed"] or 0
        failed = b_rows[0]["failed"] or 0
        rate = round((passed / tot * 100), 1) if tot > 0 else 100.0

        p_rows = q("SELECT * FROM problems WHERE assignee LIKE ?", (f"%{d['name']}%",))
        
        recent_commits = q("SELECT commit_hash, commit_message, created, result FROM builds WHERE author LIKE ? ORDER BY build_no DESC LIMIT 3", (f"%{d['name']}%",))
        commits_html = "".join([
            f'<div style="font-size: 11.5px; padding: 4px 0; border-bottom: 1px dashed var(--border-color); display: flex; justify-content: space-between;">'
            f'<span><span class="code-pill">{escape(c["commit_hash"])}</span> {escape(c["commit_message"][:40])}</span>'
            f'<span class="badge { "badge-success" if c["result"]=="SUCCESS" else "badge-failure" }" style="font-size:9px;">{c["result"]}</span>'
            f'</div>'
            for c in recent_commits
        ])

        cards_html += f"""
        <div class="card" style="margin-bottom: 0;">
            <div class="card-header" style="background: #ffffff;">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <div style="width: 44px; height: 44px; border-radius: 50%; background: {d['avatar_color']}; color: #ffffff; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 16px;">
                        {escape(d['name'][0])}
                    </div>
                    <div>
                        <div style="font-size: 16px; font-weight: 800; color: var(--text-primary);">{escape(d['name'])}</div>
                        <div style="font-size: 12px; color: var(--text-muted);">{escape(d['role'])} · GitHub: <a href="https://github.com/{d['github_username']}" target="_blank" style="color: var(--primary); text-decoration: none;">@{escape(d['github_username'])}</a></div>
                    </div>
                </div>
                <span class="badge badge-running" style="font-size: 10px;">Active Developer</span>
            </div>
            <div class="card-body">
                <div style="margin-bottom: 14px;">
                    <div style="font-size: 11px; font-weight: 700; color: var(--text-muted); text-transform: uppercase;">Assigned SCM Module</div>
                    <div style="font-size: 13.5px; font-weight: 600; color: var(--text-primary); margin-top: 2px;">{escape(d['module'])}</div>
                    <div style="margin-top: 4px;"><span class="branch-pill">🌿 {escape(d['branch'])}</span></div>
                </div>
                
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; background: var(--bg-subtle); padding: 12px; border-radius: var(--radius-sm); margin-bottom: 14px; text-align: center;">
                    <div>
                        <div style="font-size: 18px; font-weight: 800; color: var(--text-primary);">{tot}</div>
                        <div style="font-size: 10.5px; color: var(--text-muted);">Builds</div>
                    </div>
                    <div>
                        <div style="font-size: 18px; font-weight: 800; color: var(--success);">{passed}</div>
                        <div style="font-size: 10.5px; color: var(--text-muted);">Passed</div>
                    </div>
                    <div>
                        <div style="font-size: 18px; font-weight: 800; color: {'var(--danger)' if failed>0 else 'var(--text-muted)'};">{failed}</div>
                        <div style="font-size: 10.5px; color: var(--text-muted);">Failed</div>
                    </div>
                </div>

                <div style="margin-bottom: 14px;">
                    <div style="font-size: 11px; font-weight: 700; color: var(--text-muted); text-transform: uppercase; margin-bottom: 6px;">Recent Commits & Builds</div>
                    {commits_html or '<div style="font-size: 12px; color: var(--text-muted);">No recorded commits yet</div>'}
                </div>

                <div style="display: flex; gap: 8px; margin-top: 10px;">
                    <a href="/builds?developer={escape(d['name'])}" class="btn btn-secondary btn-sm" style="flex: 1;">Inspect Builds</a>
                    <a href="/switch-role?username={escape(d['username'])}&role={ 'admin' if 'Lead' in d['role'] else 'maintainer' }" class="btn btn-primary btn-sm">Switch Persona</a>
                </div>
            </div>
        </div>
        """

    content = f"""
    <div class="page-header">
        <div class="page-header-title">
            <h2>Developer Team Collaboration Roster</h2>
            <p>TechNova Solutions engineering team collaborating on {SYSTEM_NAME} across feature branches</p>
        </div>
        <div class="page-actions">
            <span class="badge badge-success" style="font-size: 11px;">4 Active Modules</span>
        </div>
    </div>

    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 20px;">
        {cards_html}
    </div>
    """
    return layout("Developer Team", content, "/team")

# =========================================================================
# PAGE C: BUILD HISTORY (/builds)
# =========================================================================

@app.route("/builds")
@login_required
def builds():
    q_filter = request.args.get("q", "").strip()
    status_filter = request.args.get("status", "").strip()
    branch_filter = request.args.get("branch", "").strip()
    dev_filter = request.args.get("developer", "").strip()

    sql = "SELECT * FROM builds WHERE 1=1"
    args = []
    
    if q_filter:
        sql += " AND (commit_hash LIKE ? OR commit_message LIKE ? OR test_summary LIKE ? OR author LIKE ?)"
        args.extend([f"%{q_filter}%", f"%{q_filter}%", f"%{q_filter}%", f"%{q_filter}%"])
    if status_filter:
        sql += " AND result = ?"
        args.append(status_filter)
    if branch_filter:
        sql += " AND branch = ?"
        args.append(branch_filter)
    if dev_filter:
        sql += " AND author LIKE ?"
        args.append(f"%{dev_filter}%")

    sql += " ORDER BY build_no DESC"
    all_builds = q(sql, tuple(args))

    table_rows = ""
    for b in all_builds:
        res = b["result"]
        badge_cls = "badge-success" if res == "SUCCESS" else ("badge-failure" if res == "FAILURE" else "badge-unstable")
        
        sq_class = "sq-success" if res == "SUCCESS" else ("sq-failure" if res == "FAILURE" else "sq-unstable")
        history_blocks = f'<div class="history-squares"><span class="history-square {sq_class}"></span><span class="history-square sq-success"></span><span class="history-square sq-success"></span><span class="history-square sq-success"></span><span class="history-square sq-success"></span><span class="history-square sq-success"></span></div>'

        investigate_btn = ""
        if res == "FAILURE":
            investigate_btn = f'<a href="/failures/{b["build_no"]}" class="btn btn-sm" style="background: var(--danger-light); color: var(--danger-text); border: 1px solid var(--danger-border); margin-right: 4px;">Investigate</a>'

        table_rows += f"""
        <tr>
            <td>
                <div style="font-weight: 700; color: var(--text-primary);">{escape(b['job_name'] or 'backend/report-service')}</div>
                <div style="font-size: 11.5px; color: var(--text-muted);">{escape(b['commit_message'] or 'routine commit')}</div>
            </td>
            <td><a href="/builds/{b['build_no']}" class="code-pill" style="font-weight:700;">#{b['build_no']}</a></td>
            <td><span class="badge {badge_cls}">{res}</span></td>
            <td><span class="branch-pill">{escape(b['branch'])}</span></td>
            <td><span class="code-pill">{escape(b['commit_hash'])}</span></td>
            <td>{escape(b['author'] or 'Developer')}</td>
            <td>{escape(b['trigger_type'] or 'GitHub Push')}</td>
            <td>{history_blocks}</td>
            <td>{b['duration_sec']}s</td>
            <td><span style="font-size: 11.5px; color: var(--text-muted);">{escape(b['created'])}</span></td>
            <td>
                {investigate_btn}
                <a href="/builds/{b['build_no']}" class="btn btn-secondary btn-sm">Details</a>
            </td>
        </tr>
        """

    content = f"""
    <div class="page-header">
        <div class="page-header-title">
            <h2>CI/CD Build History & Execution Ledger</h2>
            <p>Comprehensive auditable record of Jenkins pipeline executions, Maven compilations, and JUnit tests</p>
        </div>
        <div class="page-actions">
            <a href="/api/demo/run-failure" class="btn btn-secondary btn-sm" title="Simulate Karthik Defect">Simulate Failure #128</a>
            <a href="/api/demo/run-fix" class="btn btn-primary btn-sm" title="Simulate Karthik Fix">Simulate Fix #129</a>
        </div>
    </div>

    <!-- Filter Bar -->
    <div class="card" style="margin-bottom: 20px;">
        <div class="card-body" style="padding: 14px 20px;">
            <form method="GET" style="display: flex; gap: 12px; align-items: center; flex-wrap: wrap;">
                <input type="text" name="q" value="{escape(q_filter)}" class="form-control" style="width: 240px;" placeholder="Search commit, author, msg...">
                <select name="status" class="form-control" style="width: 140px;">
                    <option value="">All Statuses</option>
                    <option value="SUCCESS" {"selected" if status_filter=="SUCCESS" else ""}>SUCCESS</option>
                    <option value="FAILURE" {"selected" if status_filter=="FAILURE" else ""}>FAILURE</option>
                    <option value="UNSTABLE" {"selected" if status_filter=="UNSTABLE" else ""}>UNSTABLE</option>
                </select>
                <select name="branch" class="form-control" style="width: 170px;">
                    <option value="">All Branches</option>
                    <option value="main" {"selected" if branch_filter=="main" else ""}>main</option>
                    <option value="feature/employee" {"selected" if branch_filter=="feature/employee" else ""}>feature/employee</option>
                    <option value="feature/login" {"selected" if branch_filter=="feature/login" else ""}>feature/login</option>
                    <option value="feature/reports" {"selected" if branch_filter=="feature/reports" else ""}>feature/reports</option>
                    <option value="feature/database" {"selected" if branch_filter=="feature/database" else ""}>feature/database</option>
                </select>
                <button type="submit" class="btn btn-primary btn-sm">Filter</button>
                <a href="/builds" class="btn btn-secondary btn-sm">Reset</a>
            </form>
        </div>
    </div>

    <!-- Table -->
    <div class="card">
        <div class="data-table-wrapper">
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Job / Service</th>
                        <th>Build #</th>
                        <th>Result</th>
                        <th>Branch</th>
                        <th>Commit SHA</th>
                        <th>Author</th>
                        <th>Trigger</th>
                        <th>History</th>
                        <th>Duration</th>
                        <th>Timestamp</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows or '<tr><td colspan="11" style="text-align:center; padding: 24px;">No matching build records found.</td></tr>'}
                </tbody>
            </table>
        </div>
    </div>
    """
    return layout("Build History", content, "/builds")

# =========================================================================
# PAGE D: BUILD DETAILS (/builds/<build_id>)
# =========================================================================

@app.route("/builds/<int:build_id>")
@login_required
def build_details(build_id):
    row = q("SELECT * FROM builds WHERE build_no=?", (build_id,))
    if not row:
        flash(f"Build #{build_id} not found in repository status database.", "error")
        return redirect("/builds")
    b = row[0]

    # Associated problem if any
    prob_row = q("SELECT * FROM problems WHERE build_no=?", (build_id,))
    prob = prob_row[0] if prob_row else None

    # Five-stage pipeline timeline
    is_failed = b["result"] == "FAILURE"
    
    stages = [
        ("Checkout & SCM Identification", "PASSED", "Checked out commit " + b["commit_hash"], "1.2s"),
        ("SCM Environment Verification", "PASSED", "Verified JDK 17 & Maven 3.9", "0.8s"),
        ("Maven Dependency Resolution", "PASSED", "All pom.xml dependencies resolved", "4.5s"),
        ("Maven Clean & Compile", "PASSED", "Compiled 6 Java source files", "5.1s"),
        ("Unit Testing & Test Report", "FAILED" if is_failed else "PASSED", 
         b["test_summary"] if is_failed else "All 20 unit tests passed (100% green)", "8.2s")
    ]

    stages_html = ""
    for name, st, desc, dur in stages:
        st_cls = "badge-success" if st == "PASSED" else "badge-failure"
        icon_marker = ICONS['check'] if st == "PASSED" else ICONS['x']
        bg_color = "var(--success)" if st == "PASSED" else "var(--danger)"
        stages_html += f"""
        <div style="display: flex; gap: 14px; position: relative; padding-bottom: 20px;">
            <div style="width: 28px; height: 28px; border-radius: 50%; background: {bg_color}; color: #ffffff; display: flex; align-items: center; justify-content: center; flex-shrink: 0; z-index: 2;">
                {icon_marker}
            </div>
            <div style="flex: 1; background: var(--bg-subtle); padding: 12px 16px; border-radius: var(--radius-sm); border: 1px solid var(--border-color);">
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <div style="font-weight: 700; font-size: 13.5px; color: var(--text-primary);">{name}</div>
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span class="badge {st_cls}">{st}</span>
                        <span style="font-size: 11px; color: var(--text-muted);">{dur}</span>
                    </div>
                </div>
                <div style="font-size: 12px; color: var(--text-secondary); margin-top: 4px;">{escape(desc)}</div>
            </div>
        </div>
        """

    failure_cta = ""
    if is_failed:
        failure_cta = f"""
        <div class="alert-banner msg-error" style="margin-bottom: 24px;">
            <div>
                <strong>Pipeline Failure Detected:</strong> Unit testing stage failed. CommitSleuth has performed failure attribution and identified candidate commit.
            </div>
            <a href="/failures/{build_id}" class="btn btn-sm btn-primary" style="margin-left: auto;">Open Failure Investigation</a>
        </div>
        """

    content = f"""
    <div class="page-header">
        <div class="page-header-title">
            <div style="display: flex; align-items: center; gap: 10px;">
                <h2>Build #{b['build_no']} Details</h2>
                <span class="badge { 'badge-success' if b['result']=='SUCCESS' else 'badge-failure' }">{b['result']}</span>
            </div>
            <p>Executed on {escape(b['created'])} · Duration: {b['duration_sec']}s · Trigger: {escape(b['trigger_type'] or 'GitHub Push')}</p>
        </div>
        <div class="page-actions">
            <a href="{JENKINS_URL}/{build_id}" target="_blank" class="btn btn-secondary btn-sm">
                <span>{ICONS['external']}</span> Jenkins Console Log
            </a>
            <a href="/builds" class="btn btn-secondary btn-sm">Back to Builds</a>
        </div>
    </div>

    {failure_cta}

    <div class="two-col-grid" style="margin-bottom: 24px;">
        <!-- Left: Metadata -->
        <div class="card" style="margin-bottom: 0;">
            <div class="card-header">
                <div class="card-title">Build & Commit Metadata</div>
            </div>
            <div class="card-body">
                <table style="width: 100%; font-size: 13px; line-height: 2;">
                    <tr>
                        <td style="color: var(--text-muted); width: 140px;">Repository:</td>
                        <td><a href="{REPO_URL}" target="_blank" style="color: var(--primary);">{REPO_NAME}</a></td>
                    </tr>
                    <tr>
                        <td style="color: var(--text-muted);">Branch:</td>
                        <td><span class="branch-pill">🌿 {escape(b['branch'])}</span></td>
                    </tr>
                    <tr>
                        <td style="color: var(--text-muted);">Commit SHA:</td>
                        <td><span class="code-pill">{escape(b['commit_hash'])}</span></td>
                    </tr>
                    <tr>
                        <td style="color: var(--text-muted);">Author:</td>
                        <td><strong>{escape(b['author'] or 'Developer')}</strong></td>
                    </tr>
                    <tr>
                        <td style="color: var(--text-muted);">Commit Message:</td>
                        <td>{escape(b['commit_message'] or 'Routine commit')}</td>
                    </tr>
                    <tr>
                        <td style="color: var(--text-muted);">Tests Status:</td>
                        <td>{b['tests_passed']} / {b['tests_total']} Passed ({b['tests_failed']} Failed)</td>
                    </tr>
                    <tr>
                        <td style="color: var(--text-muted);">Associated Defect:</td>
                        <td>
                            {f'<a href="/failures/{build_id}" class="code-pill" style="color:var(--danger); font-weight:700;">{escape(prob["problem_code"])} ({escape(prob["status"])})</a>' if prob else '<span style="color:var(--success);">None (Healthy build)</span>'}
                        </td>
                    </tr>
                </table>
            </div>
        </div>

        <!-- Right: Pipeline Timeline -->
        <div class="card" style="margin-bottom: 0;">
            <div class="card-header">
                <div class="card-title">Declarative Pipeline Stage Timeline</div>
            </div>
            <div class="card-body" style="padding-top: 24px;">
                {stages_html}
            </div>
        </div>
    </div>
    """
    return layout(f"Build #{build_id}", content, "/builds")

# =========================================================================
# PAGE E: FAILURE INVESTIGATION (/failures/<failure_id>)
# Central Feature of CommitSleuth (Image 3 inspired)
# =========================================================================

@app.route("/failures/<int:build_id>")
@login_required
def failure_investigation(build_id):
    # Fetch build record
    b_rows = q("SELECT * FROM builds WHERE build_no=?", (build_id,))
    if not b_rows:
        flash(f"Build #{build_id} not found.", "error")
        return redirect("/builds")
    b = b_rows[0]

    # Fetch problem record
    p_rows = q("SELECT * FROM problems WHERE build_no=?", (build_id,))
    prob = dict(p_rows[0]) if p_rows else {
        "problem_code": "BUG-024",
        "failure_type": "test",
        "error_message": "ReportServiceTest.testCalculateMonthlyDepartmentExpenses - AssertionFailedError: expected <95000.0> but was <0.0>",
        "affected_file": "ReportService.java",
        "suspect_commit": "a91bc42",
        "confidence": 0.885,
        "attribution_status": "Probable Cause",
        "assignee": "Karthik",
        "status": "Open",
        "action": "Rollback recommended: git revert a91bc42 (touches 1 file: ReportService.java)",
        "corrective_commit": "c48fe19",
        "verification_build": 129
    }

    # Fetch scored commits for this problem
    scores_rows = q("SELECT * FROM commit_scores WHERE problem_id=? ORDER BY score DESC", (prob.get("id", 1),))
    scores = [dict(s) for s in scores_rows] if scores_rows else [
        {"commit_hash": "a91bc42", "author": "Karthik", "message": "Refactor monthly compensation reports and aggregate formula [CR-009]", "score": 0.885, "files": "ReportService.java", "evidence_details": "Direct match with affected file 'ReportService.java' (+0.55) | Commit recency index 2/2 (+0.10) | Scope: 1 file(s) changed (+0.10)"},
        {"commit_hash": "f0ad7d0", "author": "Karthik", "message": "Prepare monthly summary metrics [CR-007]", "score": 0.115, "files": "ReportService.java", "evidence_details": "Historical commit | Lower recency (+0.05)"}
    ]

    # Terminal Log with Image 3 style highlighting
    log_lines = [
        ("[INFO] Scanning for projects...", "info"),
        ("[INFO] ---------------------< com.commitsleuth:demo-app >----------------------", "info"),
        ("[INFO] Building demo-app 1.0.0", "info"),
        ("[INFO] --- compiler:3.13.0:compile (default-compile) @ demo-app ---", "info"),
        ("[INFO] Compiling 6 source files with javac [debug release 17] to target/classes", "info"),
        ("[INFO] --- surefire:3.2.5:test (default-test) @ demo-app ---", "info"),
        ("[INFO] Running com.commitsleuth.demo.AuthServiceTest", "info"),
        ("[INFO] Tests run: 3, Failures: 0, Errors: 0, Skipped: 0 -- in AuthServiceTest", "pass"),
        ("[INFO] Running com.commitsleuth.demo.EmployeeServiceTest", "info"),
        ("[INFO] Tests run: 3, Failures: 0, Errors: 0, Skipped: 0 -- in EmployeeServiceTest", "pass"),
        ("[INFO] Running com.commitsleuth.demo.DatabaseServiceTest", "info"),
        ("[INFO] Tests run: 3, Failures: 0, Errors: 0, Skipped: 0 -- in DatabaseServiceTest", "pass"),
        ("[INFO] Running com.commitsleuth.demo.ReportServiceTest", "info"),
        ("[ERROR] Tests run: 3, Failures: 2, Errors: 0, Skipped: 0 <<< FAILURE! -- in ReportServiceTest", "fail"),
        ("[ERROR] ReportServiceTest.testCalculateMonthlyDepartmentExpenses -- Time elapsed: 0.036 s <<< FAILURE!", "fail"),
        ("org.opentest4j.AssertionFailedError: Monthly engineering expenses must equal sum of employee salaries ==> expected: <95000.0> but was: <0.0>", "fail"),
        ("	at org.junit.jupiter.api.AssertionUtils.fail(AssertionUtils.java:55)", "fail"),
        ("	at org.junit.jupiter.api.AssertEquals.assertEquals(AssertEquals.java:86)", "fail"),
        ("	at com.commitsleuth.demo.ReportServiceTest.testCalculateMonthlyDepartmentExpenses(ReportServiceTest.java:31)", "fail"),
        ("[ERROR] ReportServiceTest.testCalculateAverageSalary:38 expected: <47500.0> but was: <0.0>", "fail"),
        ("[INFO] Results:", "info"),
        ("[ERROR] Failures: 2, Errors: 0, Skipped: 0", "fail"),
        ("[INFO] ------------------------------------------------------------------------", "info"),
        ("[INFO] BUILD FAILURE", "fail"),
        ("[INFO] Total time: 5.403 s", "info"),
        ("[ERROR] Failed to execute goal org.apache.maven.plugins:maven-surefire-plugin:3.2.5:test", "fail")
    ]

    terminal_html = ""
    for idx, (txt, kind) in enumerate(log_lines, start=1):
        cls_name = "log-info" if kind == "info" else ("log-pass" if kind == "pass" else "log-fail")
        terminal_html += f'<div class="log-line"><span class="log-num">{idx}</span><span class="log-text {cls_name}">{escape(txt)}</span></div>'

    # Candidate commit scores list
    scores_html = ""
    for s in scores:
        is_top = s["score"] >= 0.60
        pct = int(s["score"] * 100)
        scores_html += f"""
        <div style="background: {'#fef2f2' if is_top else 'var(--bg-subtle)'}; border: 1px solid {'#fecaca' if is_top else 'var(--border-color)'}; border-radius: var(--radius-sm); padding: 12px; margin-bottom: 10px;">
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <div>
                    <span class="code-pill" style="font-weight: 700;">{escape(s['commit_hash'])}</span>
                    <strong style="font-size: 13px; margin-left: 6px;">{escape(s['author'])}</strong>
                </div>
                <div style="font-size: 13px; font-weight: 800; color: {'var(--danger)' if is_top else 'var(--text-secondary)'};">
                    {pct}% Confidence
                </div>
            </div>
            <div style="font-size: 12px; color: var(--text-primary); margin: 6px 0;">{escape(s['message'])}</div>
            <div style="font-size: 11px; color: var(--text-muted); line-height: 1.4;">
                <strong>Evidence:</strong> {escape(s.get('evidence_details', ''))}
            </div>
        </div>
        """

    content = f"""
    <!-- Top Failure Alert Banner -->
    <div style="background: #ffffff; border: 1px solid #fecaca; border-left: 5px solid var(--danger); border-radius: var(--radius-md); padding: 16px 20px; margin-bottom: 24px; box-shadow: var(--shadow-subtle);">
        <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px;">
            <div>
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span class="badge badge-failure" style="font-size: 12px;">Build #{build_id} FAILURE</span>
                    <span class="code-pill" style="color: var(--danger); font-weight: 700;">{escape(prob.get('problem_code', 'BUG-024'))}</span>
                    <span class="badge badge-investigating">{escape(prob.get('status', 'Open'))}</span>
                </div>
                <div style="font-size: 15px; font-weight: 800; color: var(--text-primary); margin-top: 6px;">
                    {escape(prob.get('title', 'ReportServiceTest assertion failure in monthly expense aggregation'))}
                </div>
                <div style="font-size: 12.5px; color: var(--text-secondary); margin-top: 2px;">
                    Developer: <strong>{escape(prob.get('assignee', 'Karthik'))}</strong> · Branch: <span class="branch-pill">{escape(b['branch'])}</span> · Pipeline Stage: <strong>Maven test</strong> · Suspect Commit: <span class="code-pill">{escape(prob.get('suspect_commit', 'a91bc42'))}</span>
                </div>
            </div>
            <div style="display: flex; gap: 8px;">
                <a href="/api/demo/run-fix" class="btn btn-primary btn-sm">Submit Fix (#129)</a>
                <a href="/problems" class="btn btn-secondary btn-sm">Problem Register</a>
            </div>
        </div>
    </div>

    <!-- Main Investigation Split (Image 3 inspired) -->
    <div class="investigation-grid">
        <!-- Left Column: Terminal Build Console Log -->
        <div>
            <div class="terminal-box">
                <div class="terminal-header">
                    <div class="terminal-dots">
                        <span class="terminal-dot dot-red"></span>
                        <span class="terminal-dot dot-yellow"></span>
                        <span class="terminal-dot dot-green"></span>
                    </div>
                    <div class="terminal-title">build-console-output-#{build_id}.log</div>
                    <span class="badge badge-failure" style="font-size: 9.5px;">FAILURES: 2</span>
                </div>
                <div class="terminal-body">
                    {terminal_html}
                </div>
            </div>
        </div>

        <!-- Right Column: Root Cause, Evidence, and Fix Suggestions -->
        <div>
            <!-- Root Cause Card (Image 3 style) -->
            <div class="card" style="margin-bottom: 20px;">
                <div class="card-header" style="background: #ffffff;">
                    <div class="card-title" style="color: var(--danger);">
                        <span>{ICONS['alert-circle']}</span>
                        <span>Identified Root Cause</span>
                    </div>
                    <span class="badge badge-failure">High Severity</span>
                </div>
                <div class="card-body">
                    <div style="margin-bottom: 12px;">
                        <div style="font-size: 11px; font-weight: 700; color: var(--text-muted); text-transform: uppercase;">Error Type</div>
                        <div style="font-size: 14px; font-weight: 700; color: var(--text-primary);">{escape(prob.get('failure_type', 'test')).upper()} ASSERTION ERROR</div>
                    </div>
                    <div style="margin-bottom: 12px;">
                        <div style="font-size: 11px; font-weight: 700; color: var(--text-muted); text-transform: uppercase;">Failing Test Case</div>
                        <div class="code-pill" style="font-size: 12px; color: var(--danger); font-weight: 600;">ReportServiceTest.testCalculateMonthlyDepartmentExpenses</div>
                    </div>
                    <div style="margin-bottom: 12px;">
                        <div style="font-size: 11px; font-weight: 700; color: var(--text-muted); text-transform: uppercase;">Affected Source File</div>
                        <div class="code-pill" style="font-size: 12px; font-weight: 600;">ReportService.java (Method: calculateDepartmentTotalExpense)</div>
                    </div>
                    <div>
                        <div style="font-size: 11px; font-weight: 700; color: var(--text-muted); text-transform: uppercase;">Attribution Explanation</div>
                        <div style="font-size: 12.5px; color: var(--text-secondary); background: var(--bg-subtle); padding: 10px; border-radius: var(--radius-sm); margin-top: 4px;">
                            Potentially related commit: <strong>{escape(prob.get('suspect_commit', 'a91bc42'))}</strong>. This commit modified <code>ReportService.java</code>, which is referenced by the failing <code>ReportServiceTest</code>. This is a candidate cause and requires developer verification.
                        </div>
                    </div>
                </div>
            </div>

            <!-- Fix Suggestions Card (Image 3 style) -->
            <div class="card" style="margin-bottom: 20px;">
                <div class="card-header">
                    <div class="card-title" style="color: var(--success);">
                        <span>{ICONS['check']}</span>
                        <span>Recommended Corrective Fix</span>
                    </div>
                    <span class="badge badge-success">Solution</span>
                </div>
                <div class="card-body">
                    <p style="font-size: 12.5px; color: var(--text-secondary); margin-bottom: 10px;">
                        Restore the salary accumulation loop in <code>ReportService.java</code> to sum employee salaries for the specified department:
                    </p>
                    <div style="background: #0f172a; color: #f8fafc; padding: 12px; border-radius: var(--radius-sm); font-family: 'JetBrains Mono', monospace; font-size: 11.5px; line-height: 1.5; overflow-x: auto; position: relative;">
<span style="color: #f87171;">- return 0.0; // intentional defect in commit a91bc42</span>
<span style="color: #34d399;">+ double total = 0.0;</span>
<span style="color: #34d399;">+ for (Employee emp : employees) {{</span>
<span style="color: #34d399;">+     if (department.equalsIgnoreCase(emp.getDepartment())) {{</span>
<span style="color: #34d399;">+         total += emp.getSalary();</span>
<span style="color: #34d399;">+     }}</span>
<span style="color: #34d399;">+ }}</span>
<span style="color: #34d399;">+ return total;</span>
                    </div>
                    <div style="margin-top: 12px; display: flex; justify-content: flex-end;">
                        <a href="/api/demo/run-fix" class="btn btn-primary btn-sm">Apply Fix & Trigger Build #129</a>
                    </div>
                </div>
            </div>

            <!-- Candidate Commits & Evidence Breakdown -->
            <div class="card">
                <div class="card-header">
                    <div class="card-title">Evidence-Based Scored Commits</div>
                </div>
                <div class="card-body">
                    {scores_html}
                </div>
            </div>
        </div>
    </div>
    """
    return layout("Failure Investigation", content, "/failures")

# =========================================================================
# PAGE F: ALERTS AND NOTIFICATIONS (/alerts)
# =========================================================================

@app.route("/alerts")
@login_required
def alerts():
    all_alerts = q("SELECT * FROM alerts ORDER BY id DESC")
    unread = sum(1 for a in all_alerts if a["acknowledged"] == 0)

    alerts_html = ""
    for a in all_alerts:
        sev = a["severity"]
        sev_cls = "badge-failure" if sev in ("Critical", "High") else "badge-unstable"
        is_ack = a["acknowledged"] == 1

        ack_btn = ""
        if not is_ack:
            ack_btn = f'<a href="/api/alerts/{a["id"]}/ack" class="btn btn-primary btn-sm">Acknowledge</a>'

        alerts_html += f"""
        <div style="background: #ffffff; border: 1px solid var(--border-color); border-radius: var(--radius-md); padding: 16px 20px; margin-bottom: 12px; box-shadow: var(--shadow-subtle); display: flex; align-items: center; justify-content: space-between;">
            <div>
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span class="badge {sev_cls}">{sev}</span>
                    <span class="code-pill" style="font-weight: 700;">{escape(a['alert_code'])}</span>
                    <span style="font-size: 13.5px; font-weight: 700; color: var(--text-primary);">{escape(a['notification_type'])}</span>
                    <span style="font-size: 11px; color: var(--text-muted);">Build #{a['build_no']}</span>
                </div>
                <div style="font-size: 13px; color: var(--text-secondary); margin: 6px 0;">
                    {escape(a['summary'])}
                </div>
                <div style="font-size: 11px; color: var(--text-muted);">
                    Assigned: <strong>{escape(a['developer'])}</strong> · Created: {escape(a['created_at'])}
                    {f' · <span style="color:var(--success); font-weight:600;">✓ Acknowledged by {escape(a["acknowledged_by"] or "dev")} at {escape(a["acknowledged_at"] or "")}</span>' if is_ack else ' · <span style="color:var(--danger); font-weight:600;">● Unacknowledged</span>'}
                </div>
            </div>
            <div style="display: flex; gap: 8px;">
                {ack_btn}
                <a href="/failures/{a['build_no']}" class="btn btn-secondary btn-sm">View Failure</a>
            </div>
        </div>
        """

    content = f"""
    <div class="page-header">
        <div class="page-header-title">
            <h2>Alerts & Notification Center</h2>
            <p>Real-time automated incident dispatch for continuous integration build failures</p>
        </div>
        <div class="page-actions">
            <span class="badge badge-failure" style="font-size: 12px;">{unread} Unread Incident(s)</span>
        </div>
    </div>

    <div>
        {alerts_html or '<div class="card"><div class="card-body" style="text-align:center;">No alerts currently recorded.</div></div>'}
    </div>
    """
    return layout("Alerts & Notifications", content, "/alerts")

@app.route("/api/alerts/<int:alert_id>/ack")
@login_required
def acknowledge_alert(alert_id):
    user = current_user() or "Developer"
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ex("UPDATE alerts SET acknowledged=1, acknowledged_by=?, acknowledged_at=?, status='Acknowledged' WHERE id=?", (user, now, alert_id))
    log_audit(user, f"Acknowledged Alert #{alert_id}", f"Acknowledged by {user} at {now}")
    flash(f"Alert #{alert_id} acknowledged successfully.", "success")
    return redirect("/alerts")

# =========================================================================
# PAGE G: PROBLEM TRACKING (/problems)
# =========================================================================

@app.route("/problems")
@login_required
def problems():
    all_problems = [dict(r) for r in q("SELECT * FROM problems ORDER BY id DESC")]
    
    rows_html = ""
    for p in all_problems:
        st = p["status"]
        st_cls = "badge-open" if st == "Open" else ("badge-investigating" if st in ("Investigating", "Fix Submitted") else "badge-resolved")

        rows_html += f"""
        <tr>
            <td><a href="/failures/{p['build_no']}" class="code-pill" style="font-weight: 700; color: var(--danger);">{escape(p['problem_code'])}</a></td>
            <td><a href="/builds/{p['build_no']}" class="code-pill">#{p['build_no']}</a></td>
            <td>
                <div style="font-weight: 700; color: var(--text-primary);">{escape(p['title'] or p['error_message'][:60])}</div>
                <div style="font-size: 11px; color: var(--text-muted);">{escape(p['affected_file'] or 'ReportService.java')}</div>
            </td>
            <td><span class="code-pill">{escape(p['suspect_commit'])}</span></td>
            <td>{escape(p['assignee'])}</td>
            <td><span class="badge {st_cls}">{escape(st)}</span></td>
            <td><strong>{p['confidence']}</strong></td>
            <td>{p.get('verification_build') or 'Pending'}</td>
            <td>
                <a href="/failures/{p['build_no']}" class="btn btn-secondary btn-sm">Inspect</a>
            </td>
        </tr>
        """

    content = f"""
    <div class="page-header">
        <div class="page-header-title">
            <h2>Problem Tracking Register</h2>
            <p>Automated defect management and resolution lifecycle (Open → Fix Submitted → Verified → Resolved)</p>
        </div>
        <div class="page-actions">
            <span class="badge badge-success" style="font-size: 11px;">SCM Problem Control</span>
        </div>
    </div>

    <div class="card">
        <div class="data-table-wrapper">
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Problem ID</th>
                        <th>Build #</th>
                        <th>Title & Affected CI</th>
                        <th>Suspect Commit</th>
                        <th>Assignee</th>
                        <th>Status</th>
                        <th>Confidence</th>
                        <th>Verification Build</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
        </div>
    </div>
    """
    return layout("Problem Tracking", content, "/problems")

# =========================================================================
# PAGE H: CHANGE MANAGEMENT (/changes and /crs)
# =========================================================================

@app.route("/changes", methods=["GET", "POST"])
@app.route("/crs", methods=["GET", "POST"])
@login_required
def changes():
    all_crs = q("SELECT * FROM change_requests ORDER BY cr_id ASC")

    rows_html = ""
    for c in all_crs:
        st = c["status"]
        st_cls = "badge-success" if st in ("Approved", "Implemented") else ("badge-failure" if st == "Rejected" else "badge-unstable")

        rows_html += f"""
        <tr>
            <td><span class="code-pill" style="font-weight: 700;">{escape(c['cr_id'])}</span></td>
            <td>
                <div style="font-weight: 700; color: var(--text-primary);">{escape(c['title'] or c['description'][:50])}</div>
                <div style="font-size: 11px; color: var(--text-muted);">{escape(c['description'])}</div>
            </td>
            <td>{escape(c['requester'])}</td>
            <td><span class="code-pill" style="font-size: 11px;">{escape(c['impact'])}</span></td>
            <td><span class="badge {st_cls}">{escape(st)}</span></td>
            <td><span class="branch-pill">{escape(c['branch'] or 'main')}</span></td>
            <td><span class="code-pill">{escape(c['related_commit'] or '-')}</span></td>
            <td>{escape(c['decision'] or 'Pending CCB')}</td>
        </tr>
        """

    content = f"""
    <div class="page-header">
        <div class="page-header-title">
            <h2>Change Management Register</h2>
            <p>Formal Configuration Control Board (CCB) change requests and audit trail (CR-001 through CR-010)</p>
        </div>
        <div class="page-actions">
            <button onclick="document.getElementById('newCrModal').style.display='block'" class="btn btn-primary btn-sm">+ Raise Change Request</button>
        </div>
    </div>

    <div class="card">
        <div class="data-table-wrapper">
            <table class="data-table">
                <thead>
                    <tr>
                        <th>CR ID</th>
                        <th>Title & Description</th>
                        <th>Requester</th>
                        <th>Affected CI / Scope</th>
                        <th>Status</th>
                        <th>Branch</th>
                        <th>Commit</th>
                        <th>CCB Decision</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
        </div>
    </div>

    <!-- Modal for New Change Request -->
    <div id="newCrModal" style="display:none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 100; align-items: center; justify-content: center;">
        <div style="background: #ffffff; border-radius: var(--radius-md); max-width: 500px; width: 90%; margin: 60px auto; padding: 24px; box-shadow: var(--shadow-card);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                <h3 style="font-size: 18px; font-weight: 800;">Raise Change Request</h3>
                <button onclick="document.getElementById('newCrModal').style.display='none'" style="background: none; border: none; font-size: 18px; cursor: pointer;">✕</button>
            </div>
            <form action="/cr/new" method="POST">
                <div class="form-group">
                    <label class="form-label">CR ID</label>
                    <input type="text" name="cr_id" value="CR-011" class="form-control" required>
                </div>
                <div class="form-group">
                    <label class="form-label">Title</label>
                    <input type="text" name="title" placeholder="Summary of proposed change" class="form-control" required>
                </div>
                <div class="form-group">
                    <label class="form-label">Description & Rationale</label>
                    <textarea name="description" rows="3" class="form-control" placeholder="Detailed purpose and technical scope" required></textarea>
                </div>
                <div class="form-group">
                    <label class="form-label">Affected Configuration Item</label>
                    <input type="text" name="impact" value="ReportService.java" class="form-control" required>
                </div>
                <div class="form-group">
                    <label class="form-label">Target Branch</label>
                    <input type="text" name="branch" value="feature/reports" class="form-control" required>
                </div>
                <div style="display: flex; justify-content: flex-end; gap: 8px; margin-top: 20px;">
                    <button type="button" onclick="document.getElementById('newCrModal').style.display='none'" class="btn btn-secondary">Cancel</button>
                    <button type="submit" class="btn btn-primary">Submit to CCB</button>
                </div>
            </form>
        </div>
    </div>
    """
    return layout("Change Management", content, "/changes")

@app.route("/cr/new", methods=["POST"])
@login_required
def new_cr():
    if not is_maintainer():
        flash("Permission Denied: Viewer role cannot register Change Requests.", "error")
        return redirect("/changes")
    
    cr_id = request.form.get("cr_id", "").strip()
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    impact = request.form.get("impact", "").strip()
    branch = request.form.get("branch", "main").strip()
    requester = current_user() or "Developer"

    ex("""INSERT OR REPLACE INTO change_requests (cr_id, title, description, requester, impact, priority, reason, status, decision, decision_date, branch)
          VALUES (?, ?, ?, ?, ?, 'Medium', 'Standard CR Submission', 'Raised', 'Under Review by CCB', ?, ?)""",
       (cr_id, title, description, requester, impact, datetime.date.today().isoformat(), branch))
    
    log_audit(requester, f"Submitted Change Request {cr_id}", f"Title: {title}, Target Branch: {branch}")
    flash(f"Change Request {cr_id} successfully submitted to Configuration Control Board.", "success")
    return redirect("/changes")

# =========================================================================
# PAGE I: CI REGISTER (/cis)
# =========================================================================

@app.route("/cis")
@login_required
def cis():
    all_cis = q("SELECT * FROM ci_register ORDER BY ci_id ASC")

    rows_html = ""
    for c in all_cis:
        rows_html += f"""
        <tr>
            <td><span class="code-pill" style="font-weight: 700;">{escape(c['ci_id'])}</span></td>
            <td><strong>{escape(c['name'])}</strong></td>
            <td><span class="code-pill">{escape(c['version'])}</span></td>
            <td><span class="badge badge-success">{escape(c['status'])}</span></td>
            <td>{escape(c['owner'])}</td>
            <td><span class="branch-pill">{escape(c['baseline'] or 'BL-01')}</span></td>
            <td><span class="code-pill" style="font-size: 11px;">{escape(c['category'] or 'Core')}</span></td>
            <td>{escape(c['last_modified'] or '')}</td>
        </tr>
        """

    content = f"""
    <div class="page-header">
        <div class="page-header-title">
            <h2>Configuration Item (CI) Register</h2>
            <p>20 Audited Configuration Items under formal version and change control</p>
        </div>
        <div class="page-actions">
            <span class="badge badge-success" style="font-size: 11px;">20 Controlled CIs</span>
        </div>
    </div>

    <div class="card">
        <div class="data-table-wrapper">
            <table class="data-table">
                <thead>
                    <tr>
                        <th>CI ID</th>
                        <th>Configuration Item Name</th>
                        <th>Version</th>
                        <th>Lifecycle Status</th>
                        <th>Owner</th>
                        <th>Baseline</th>
                        <th>Category</th>
                        <th>Last Modified</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
        </div>
    </div>
    """
    return layout("CI Register", content, "/cis")

# =========================================================================
# PAGE J: BASELINES & VERSIONS (/versions and /baselines)
# =========================================================================

@app.route("/versions")
@app.route("/baselines")
@login_required
def baselines():
    all_baselines = q("SELECT * FROM baselines ORDER BY baseline_id ASC")

    rows_html = ""
    for b in all_baselines:
        rows_html += f"""
        <tr>
            <td><span class="code-pill" style="font-weight: 800; color: var(--primary);">{escape(b['baseline_id'])}</span></td>
            <td><strong>{escape(b['name'])}</strong></td>
            <td><span class="code-pill">{escape(b['version'])}</span></td>
            <td><span class="branch-pill">{escape(b['tag'] or 'v1.0.0')}</span></td>
            <td><span class="code-pill">{escape(b['commit_hash'] or 'HEAD')}</span></td>
            <td>{escape(b['description'])}</td>
            <td>{escape(b['approval_date'])}</td>
            <td><span class="badge badge-success">{escape(b['status'])}</span></td>
        </tr>
        """

    content = f"""
    <div class="page-header">
        <div class="page-header-title">
            <h2>Baselines & Version Management</h2>
            <p>Formal configuration baselines (BL-01 through BL-05) and Git release tags</p>
        </div>
        <div class="page-actions">
            <span class="badge badge-success" style="font-size: 11px;">BL-05 Final Review Baseline Active</span>
        </div>
    </div>

    <!-- Baselines Table -->
    <div class="card" style="margin-bottom: 24px;">
        <div class="card-header">
            <div class="card-title">Approved SCM Baselines</div>
        </div>
        <div class="data-table-wrapper">
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Baseline ID</th>
                        <th>Baseline Name</th>
                        <th>Version</th>
                        <th>Release Tag</th>
                        <th>Commit Hash</th>
                        <th>Scope & Verification</th>
                        <th>Approval Date</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
        </div>
    </div>

    <!-- Baseline Comparison Diff Tool (BL-04 vs BL-05) -->
    <div class="card">
        <div class="card-header">
            <div class="card-title">Baseline Comparison View (BL-04 vs. BL-05 Final Release)</div>
            <span class="badge badge-running">Delta Inspection</span>
        </div>
        <div class="card-body">
            <div style="font-size: 13px; color: var(--text-secondary); margin-bottom: 14px;">
                Shows configuration item deltas between Analysis Baseline BL-04 and Final Release Baseline BL-05:
            </div>
            <table class="data-table" style="font-size: 12.5px;">
                <thead>
                    <tr>
                        <th>Configuration Item</th>
                        <th>State in BL-04</th>
                        <th>State in BL-05</th>
                        <th>Change Rationale / PR</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><code>ReportService.java</code></td>
                        <td>Initial compensation model</td>
                        <td><span style="color:var(--success); font-weight:700;">Verified aggregate salary fix (CR-010)</span></td>
                        <td>PR #10 / Commit c48fe19</td>
                    </tr>
                    <tr>
                        <td><code>pom.xml</code></td>
                        <td>Surefire 3.2.0 unpinned</td>
                        <td><span style="color:var(--success); font-weight:700;">Surefire 3.2.5 pinned (Reproducible)</span></td>
                        <td>PCA Audit AUD-03</td>
                    </tr>
                    <tr>
                        <td><code>dashboard/app.py</code></td>
                        <td>Basic text dashboard</td>
                        <td><span style="color:var(--success); font-weight:700;">Full responsive Light-Theme Portal</span></td>
                        <td>CR-007</td>
                    </tr>
                    <tr>
                        <td><code>releases/CommitSleuth-v1.0.0.zip</code></td>
                        <td>Unpackaged</td>
                        <td><span style="color:var(--success); font-weight:700;">Packaged with SHA-256 Checksum</span></td>
                        <td>Release Gate BL-05</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
    """
    return layout("Baselines & Versions", content, "/versions")

# =========================================================================
# PAGE K: PROMOTIONS & GATES (/releases and /promotions)
# Inspired by Image 4 (Fianu Compliance & Change Gate Indicators)
# =========================================================================

@app.route("/releases")
@app.route("/promotions")
@login_required
def promotions():
    promos = q("SELECT * FROM promotions ORDER BY id DESC")

    rows_html = ""
    for p in promos:
        res = p["result"]
        res_cls = "badge-success" if res == "PASSED" else "badge-failure"
        rows_html += f"""
        <tr>
            <td><strong>{escape(p['item'])}</strong></td>
            <td><span class="branch-pill">{escape(p['from_level'])}</span></td>
            <td><span class="branch-pill" style="background:#eff6ff; color:#1d4ed8;">➔ {escape(p['to_level'])}</span></td>
            <td><span class="badge {res_cls}">{res}</span></td>
            <td>{escape(p['approver'])}</td>
            <td><span style="font-size: 11.5px; color: var(--text-secondary);">{escape(p['reason'] or '')}</span></td>
            <td><span class="code-pill">{escape(p['release_tag'] or '-')}</span></td>
            <td>{escape(p['promo_date'])}</td>
        </tr>
        """

    content = f"""
    <div class="page-header">
        <div class="page-header-title">
            <h2>Release Promotion & Quality Gate Management</h2>
            <p>Environment progression (Development → Testing → Release Candidate → Production) with automated verification gates</p>
        </div>
        <div class="page-actions">
            <span class="badge badge-success" style="font-size: 11px;">Enforced SCM Quality Gates</span>
        </div>
    </div>

    <!-- Image 4 Style: Governance & Compliance Cards Grid -->
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 16px; margin-bottom: 24px;">
        <div class="card" style="margin-bottom: 0;">
            <div class="card-header" style="padding: 12px 16px;">
                <div class="card-title" style="font-size: 13.5px;">Source Code Controls</div>
                <span class="badge badge-success">Passed</span>
            </div>
            <div class="card-body" style="padding: 14px; font-size: 12px; line-height: 1.8;">
                <div style="display:flex; justify-content:space-between;"><span>Commit Signature</span><span class="badge badge-success">Verified</span></div>
                <div style="display:flex; justify-content:space-between;"><span>Peer Code Review</span><span class="badge badge-success">2 Approvals</span></div>
                <div style="display:flex; justify-content:space-between;"><span>Branching Policy</span><span class="badge badge-success">Compliant</span></div>
            </div>
        </div>

        <div class="card" style="margin-bottom: 0;">
            <div class="card-header" style="padding: 12px 16px;">
                <div class="card-title" style="font-size: 13.5px;">Automated Testing Gate</div>
                <span class="badge badge-success">100% Passed</span>
            </div>
            <div class="card-body" style="padding: 14px; font-size: 12px; line-height: 1.8;">
                <div style="display:flex; justify-content:space-between;"><span>Unit Test Coverage</span><span class="badge badge-success">95% (+4%)</span></div>
                <div style="display:flex; justify-content:space-between;"><span>JUnit Test Executions</span><span class="badge badge-success">20/20 Green</span></div>
                <div style="display:flex; justify-content:space-between;"><span>Regression Verifications</span><span class="badge badge-success">All Passing</span></div>
            </div>
        </div>

        <div class="card" style="margin-bottom: 0;">
            <div class="card-header" style="padding: 12px 16px;">
                <div class="card-title" style="font-size: 13.5px;">Build Pipeline Security</div>
                <span class="badge badge-success">Secure</span>
            </div>
            <div class="card-body" style="padding: 14px; font-size: 12px; line-height: 1.8;">
                <div style="display:flex; justify-content:space-between;"><span>CI Build Artifact</span><span class="code-pill">demo-app-1.0.0.jar</span></div>
                <div style="display:flex; justify-content:space-between;"><span>Package Checksum</span><span class="badge badge-success">SHA-256 Valid</span></div>
                <div style="display:flex; justify-content:space-between;"><span>Secret Scanner</span><span class="badge badge-success">0 Leaks</span></div>
            </div>
        </div>

        <div class="card" style="margin-bottom: 0;">
            <div class="card-header" style="padding: 12px 16px;">
                <div class="card-title" style="font-size: 13.5px;">Change Gate Indicators</div>
                <span class="badge badge-success">Eligible</span>
            </div>
            <div class="card-body" style="padding: 14px; font-size: 12px; line-height: 1.8;">
                <div style="display:flex; justify-content:space-between;"><span>CCB Approved CR</span><span class="badge badge-success">CR-010</span></div>
                <div style="display:flex; justify-content:space-between;"><span>Verification Build</span><span class="badge badge-success">Build #129</span></div>
                <div style="display:flex; justify-content:space-between;"><span>Production Gate</span><span class="badge badge-success">Ready</span></div>
            </div>
        </div>
    </div>

    <!-- Promotion Decisions Table -->
    <div class="card">
        <div class="card-header">
            <div class="card-title">Promotional Gate Ledger & Audit History</div>
        </div>
        <div class="data-table-wrapper">
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Configuration Item</th>
                        <th>From Level</th>
                        <th>Target Level</th>
                        <th>Gate Result</th>
                        <th>Approver</th>
                        <th>Evaluation Rationale</th>
                        <th>Release Tag</th>
                        <th>Timestamp</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
        </div>
    </div>
    """
    return layout("Promotions & Releases", content, "/releases")

# =========================================================================
# PAGE L: AUDITS - FCA & PCA (/audits)
# =========================================================================

@app.route("/audits")
@login_required
def audits():
    all_audits = q("SELECT * FROM audit_observations ORDER BY id ASC")

    rows_html = ""
    for a in all_audits:
        sev = a["severity"]
        sev_cls = "badge-success" if sev == "Conforming" else ("badge-failure" if sev in ("Critical", "Major") else "badge-unstable")
        
        rows_html += f"""
        <tr>
            <td><span class="code-pill" style="font-weight: 700;">{escape(a['audit_id'])}</span></td>
            <td><span class="badge badge-running">{escape(a['audit_type'])}</span></td>
            <td><strong>{escape(a['checklist_item'])}</strong></td>
            <td>{escape(a['observation'])}</td>
            <td><span style="font-size: 11.5px; color: var(--text-muted);">{escape(a['evidence'] or '')}</span></td>
            <td><span class="badge {sev_cls}">{sev}</span></td>
            <td>{escape(a['owner'])}</td>
            <td><span class="badge badge-success">{escape(a['status'])}</span></td>
            <td>{escape(a['closure_date'] or '')}</td>
        </tr>
        """

    content = f"""
    <div class="page-header">
        <div class="page-header-title">
            <h2>Configuration Auditing System (CAS)</h2>
            <p>Functional Configuration Audit (FCA) and Physical Configuration Audit (PCA) observation ledger</p>
        </div>
        <div class="page-actions">
            <span class="badge badge-success" style="font-size: 11px;">All Observations Closed</span>
        </div>
    </div>

    <div class="card">
        <div class="data-table-wrapper">
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Audit ID</th>
                        <th>Type</th>
                        <th>Checklist Criterion</th>
                        <th>Observation & Findings</th>
                        <th>Verification Evidence</th>
                        <th>Severity</th>
                        <th>Owner</th>
                        <th>Status</th>
                        <th>Closure Date</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
        </div>
    </div>
    """
    return layout("Audits (FCA / PCA)", content, "/audits")

# =========================================================================
# PAGE M: STATUS ACCOUNTING & CSAR (/accounting and /report)
# =========================================================================

@app.route("/accounting")
@app.route("/report")
@login_required
def accounting():
    csar_text = status_reporter.build_csar()

    content = f"""
    <div class="page-header">
        <div class="page-header-title">
            <h2>Configuration Status Accounting Report (CSAR)</h2>
            <p>Traceable single-source-of-truth configuration accounting for {PROJECT_NAME}</p>
        </div>
        <div class="page-actions">
            <a href="/report/csv" class="btn btn-primary btn-sm">Export CSAR CSV</a>
            <button onclick="navigator.clipboard.writeText(document.getElementById('csarPre').innerText); alert('CSAR copied to clipboard!');" class="btn btn-secondary btn-sm">Copy Report</button>
        </div>
    </div>

    <div class="card">
        <div class="card-header">
            <div class="card-title">Live CSAR Text Output</div>
            <span class="badge badge-success">Generated via SQLite</span>
        </div>
        <div class="card-body" style="padding: 0;">
            <pre id="csarPre" style="background: #0f172a; color: #f8fafc; padding: 20px; font-family: 'JetBrains Mono', monospace; font-size: 12px; line-height: 1.6; max-height: 550px; overflow-y: auto; margin: 0;">{escape(csar_text)}</pre>
        </div>
    </div>
    """
    return layout("Status Accounting", content, "/accounting")

@app.route("/report/csv")
@login_required
def report_csv():
    csv_data = status_reporter.export_csar_csv()
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename=CSAR-Register-{datetime.date.today():%Y%m%d}.csv"}
    )

# =========================================================================
# PAGE N: SETTINGS & CUSTOMIZATION (/settings and /config)
# =========================================================================

@app.route("/settings", methods=["GET", "POST"])
@app.route("/config", methods=["GET", "POST"])
@login_required
def settings():
    cfg = load_cfg()
    
    if request.method == "POST":
        if not is_admin():
            flash("Permission Denied: Administrator role required to update SCM settings.", "error")
            return redirect("/settings")
        
        try:
            cfg["weights"]["file_match"] = float(request.form.get("weight_file", 0.55))
            cfg["weights"]["pom_change"] = float(request.form.get("weight_pom", 0.25))
            cfg["weights"]["recency"] = float(request.form.get("weight_recency", 0.10))
            cfg["weights"]["change_size"] = float(request.form.get("weight_size", 0.10))
            cfg["project"]["repo_url"] = request.form.get("repo_url", REPO_URL)
            cfg["project"]["jenkins_url"] = request.form.get("jenkins_url", JENKINS_URL)
            save_cfg(cfg)
            log_audit(current_user(), "Updated SCM Configuration", "Adjusted scoring weights and integration endpoints")
            flash("Configuration successfully saved to scoring_config.yaml", "success")
        except Exception as e:
            flash(f"Error saving configuration: {e}", "error")
        return redirect("/settings")

    weights = cfg.get("weights", {})

    content = f"""
    <div class="page-header">
        <div class="page-header-title">
            <h2>SCM Settings & Attribution Customization</h2>
            <p>Fine-tune ranking engine heuristics, weights, and CI server integration hooks</p>
        </div>
    </div>

    <div class="card" style="max-width: 800px;">
        <div class="card-header">
            <div class="card-title">Attribution Scoring Weights (Must sum to 1.00)</div>
        </div>
        <div class="card-body">
            <form method="POST">
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
                    <div class="form-group">
                        <label class="form-label">File Match Weight (0.00 – 1.00)</label>
                        <input type="number" step="0.05" name="weight_file" value="{weights.get('file_match', 0.55)}" class="form-control" required>
                        <small style="color:var(--text-muted); font-size:11px;">Correlation between source files and failing test/stack trace</small>
                    </div>
                    <div class="form-group">
                        <label class="form-label">POM Change Weight (0.00 – 1.00)</label>
                        <input type="number" step="0.05" name="weight_pom" value="{weights.get('pom_change', 0.25)}" class="form-control" required>
                        <small style="color:var(--text-muted); font-size:11px;">Weight for pom.xml modifications during dependency failures</small>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Commit Recency Weight (0.00 – 1.00)</label>
                        <input type="number" step="0.05" name="weight_recency" value="{weights.get('recency', 0.10)}" class="form-control" required>
                        <small style="color:var(--text-muted); font-size:11px;">Linear decay factor for candidate commit ordering</small>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Change Scope Weight (0.00 – 1.00)</label>
                        <input type="number" step="0.05" name="weight_size" value="{weights.get('change_size', 0.10)}" class="form-control" required>
                        <small style="color:var(--text-muted); font-size:11px;">Number of modified files in changeset</small>
                    </div>
                </div>

                <div class="form-group">
                    <label class="form-label">GitHub Repository URL</label>
                    <input type="text" name="repo_url" value="{cfg.get('project', {}).get('repo_url', REPO_URL)}" class="form-control" required>
                </div>
                <div class="form-group">
                    <label class="form-label">Jenkins CI Server Webhook URL</label>
                    <input type="text" name="jenkins_url" value="{cfg.get('project', {}).get('jenkins_url', JENKINS_URL)}" class="form-control" required>
                </div>

                <div style="margin-top: 20px;">
                    <button type="submit" class="btn btn-primary">Save Configuration</button>
                </div>
            </form>
        </div>
    </div>
    """
    return layout("Settings & Customization", content, "/settings")

# =========================================================================
# PAGE O: AUDIT TRAIL (/audit-trail)
# =========================================================================

@app.route("/audit-trail")
@login_required
def audit_trail():
    events = q("SELECT * FROM audit_trail ORDER BY id DESC LIMIT 100")

    rows_html = ""
    for ev in events:
        rows_html += f"""
        <tr>
            <td><span class="code-pill">{escape(ev['timestamp'])}</span></td>
            <td><strong>{escape(ev['username'])}</strong></td>
            <td><span class="badge badge-running">{escape(ev['action'])}</span></td>
            <td><span style="font-size: 12px; color: var(--text-secondary);">{escape(ev['details'] or '')}</span></td>
        </tr>
        """

    content = f"""
    <div class="page-header">
        <div class="page-header-title">
            <h2>Immutable SCM Audit Trail</h2>
            <p>Chronological security log of promotions, configuration edits, and build evaluations</p>
        </div>
    </div>

    <div class="card">
        <div class="data-table-wrapper">
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Timestamp</th>
                        <th>User Persona</th>
                        <th>Action Performed</th>
                        <th>Event Details</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html or '<tr><td colspan="4" style="text-align:center; padding:20px;">No audit events recorded yet.</td></tr>'}
                </tbody>
            </table>
        </div>
    </div>
    """
    return layout("Audit Trail", content, "/audit-trail")

# =========================================================================
# INTERACTIVE DEMO ENGINE ENDPOINTS
# =========================================================================

@app.route("/api/demo/run-failure")
def demo_run_failure():
    """Simulates Karthik pushing commit a91bc42 on feature/reports causing Build #128 failure."""
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Update or insert Build #128
    ex("""INSERT OR REPLACE INTO builds (
            build_no, result, commit_hash, branch, failure_type, test_summary, duration_sec, log_path, created,
            author, commit_message, trigger_type, failed_stage, tests_total, tests_failed, tests_passed, job_name
          ) VALUES (128, 'FAILURE', 'a91bc42', 'feature/reports', 'test',
                    'ReportServiceTest.testCalculateMonthlyDepartmentExpenses - AssertionFailedError: expected <95000.0> but was <0.0>',
                    41.5, 'build.log', ?, 'Karthik', 'Refactor monthly compensation reports and aggregate formula [CR-009]',
                    'GitHub Push', 'Unit Testing & Test Report', 20, 2, 18, 'backend/report-service')""",
       (now,))
    
    # Update or insert Problem BUG-024
    ex("""INSERT OR REPLACE INTO problems (
            id, problem_code, build_no, failure_type, error_message, affected_file,
            suspect_commit, confidence, attribution_status, assignee, status,
            action, notification, created, title, description, root_cause_category,
            corrective_commit, verification_build
          ) VALUES (1, 'BUG-024', 128, 'test',
                    'ReportServiceTest.testCalculateMonthlyDepartmentExpenses:31 Monthly engineering expenses must equal sum of employee salaries ==> expected: <95000.0> but was: <0.0>',
                    'ReportService.java', 'a91bc42', 0.885, 'Probable Cause', 'Karthik', 'Open',
                    'Rollback recommended: git revert a91bc42 (touches 1 file: ReportService.java)',
                    'Build #128 FAILED (test). Suspect commit a91bc42 by Karthik, confidence 0.885.',
                    ?, 'ReportServiceTest assertion failure in monthly expense aggregation',
                    'Karthik introduced intentional defect in commit a91bc42 causing calculateDepartmentTotalExpense() to return 0.0.',
                    'Logic / Calculation Defect', 'c48fe19', 129)""",
       (now,))

    # Insert or update Alert
    ex("""INSERT OR REPLACE INTO alerts (
            id, alert_code, build_no, developer, severity, notification_type, summary, created_at, acknowledged, problem_code, status
          ) VALUES (1, 'ALT-001', 128, 'Karthik', 'Critical', 'Pipeline Break: Unit Test Failure',
                    'Build #128 failed on branch feature/reports. ReportServiceTest assertion error in monthly expense calculation.',
                    ?, 0, 'BUG-024', 'Unread')""",
       (now,))

    # Record Promotion Block
    ex("""INSERT INTO promotions (item, from_level, to_level, promo_date, approver, result, reason)
          VALUES ('Employee Management System', 'Development', 'Testing', ?, 'CCB', 'BLOCKED',
                  'Automated tests did not pass (ReportServiceTest assertion failure in Build #128)')""",
       (now,))

    log_audit("DemoEngine", "Executed Failure Demonstration (Build #128)", "Karthik seeded defect triggered on feature/reports; BUG-024 created; alert dispatched.")
    flash("Demo Step 1 Executed: Karthik introduced defect in Build #128. Failure attributed to commit a91bc42, BUG-024 opened, alert dispatched!", "error")
    return redirect("/failures/128")

@app.route("/api/demo/run-fix")
def demo_run_fix():
    """Simulates Karthik submitting corrective commit c48fe19 on feature/reports restoring Build #129 to SUCCESS."""
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Record passing verification build #129
    ex("""INSERT OR REPLACE INTO builds (
            build_no, result, commit_hash, branch, failure_type, test_summary, duration_sec, log_path, created,
            author, commit_message, trigger_type, failed_stage, tests_total, tests_failed, tests_passed, job_name
          ) VALUES (129, 'SUCCESS', 'c48fe19', 'feature/reports', 'None',
                    'All 20 tests passed (100% green)', 36.8, NULL, ?,
                    'Karthik', 'Fix salary aggregation formula in ReportService.java [CR-010]',
                    'GitHub Push', 'None', 20, 0, 20, 'backend/report-service')""",
       (now,))

    # Mark Problem BUG-024 Resolved
    ex("""UPDATE problems SET status='Resolved', resolved_date=?, closure_notes='Build #129 passed with 20/20 green tests. Verified by Team Lead Prakash Raj.' WHERE problem_code='BUG-024'""",
       (now,))

    # Acknowledge and resolve alert ALT-001
    ex("""UPDATE alerts SET acknowledged=1, acknowledged_by='Karthik', acknowledged_at=?, status='Resolved' WHERE alert_code='ALT-001'""",
       (now,))

    # Record Passing Promotion
    ex("""INSERT INTO promotions (item, from_level, to_level, promo_date, approver, result, reason, release_tag)
          VALUES ('Employee Management System', 'Development', 'Testing', ?, 'Prakash Raj', 'PASSED',
                  'Verification Build #129 passed with 20/20 tests green (CR-010 verified)', 'v1.0.0')""",
       (now,))
    ex("""INSERT INTO promotions (item, from_level, to_level, promo_date, approver, result, reason, release_tag)
          VALUES ('Employee Management System', 'Testing', 'Release Candidate', ?, 'CCB', 'PASSED',
                  'FCA and PCA audit requirements satisfied', 'v1.0.0')""",
       (now,))

    log_audit("DemoEngine", "Executed Fix Demonstration (Build #129)", "Karthik submitted corrective commit c48fe19; Build #129 PASSED; BUG-024 marked Resolved; promotion gate passed.")
    flash("Demo Step 2 Executed: Karthik fixed defect in commit c48fe19. Build #129 PASSED (20/20 tests), BUG-024 Resolved, promotion gate unlocked!", "success")
    return redirect("/builds/129")

@app.route("/api/demo/reset")
def demo_reset():
    """Resets database to seeded baseline."""
    seed_script = os.path.join(ROOT, "database", "seed.py")
    subprocess.run([sys.executable, seed_script, "--reset"], cwd=ROOT, capture_output=True)
    log_audit("DemoEngine", "Reset Scenario Database", "Restored clean baseline records")
    flash("Demo database has been successfully reset to initial clean baseline.", "success")
    return redirect("/")

# =========================================================================
# WEBHOOK API: INGEST BUILDS FROM JENKINS OR EXTERNAL CI
# =========================================================================

@app.route("/api/builds", methods=["POST"])
def webhook_build():
    """Authenticated API endpoint to ingest build results from Jenkins or CLI."""
    auth_token = request.headers.get("X-CommitSleuth-Token") or request.args.get("token")
    expected_token = os.environ.get("CS_API_TOKEN", "commitsleuth-token-2026")
    if not app.testing and (not auth_token or auth_token != expected_token):
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json(silent=True) or request.form.to_dict()
    if not data:
        return jsonify({"error": "Missing build payload"}), 400

    build_no = int(data.get("build_no", data.get("build", 0)))
    result = data.get("result", "SUCCESS")
    branch = data.get("branch", "main")
    commit_hash = data.get("commit_hash", data.get("commit", "HEAD"))
    author = data.get("author", "Developer")
    msg = data.get("message", "CI Build")
    duration = float(data.get("duration", 30.0))
    log_text = data.get("log", "")

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Normalize failure_type to strictly one of: 'compile', 'test', 'dependency', 'unknown'
    raw_type = (data.get("failure_type") or ("test" if result == "FAILURE" else "None")).lower()
    if "compile" in raw_type or "compilation" in raw_type:
        norm_failure_type = "compile"
    elif "test" in raw_type or "assertion" in raw_type:
        norm_failure_type = "test"
    elif "depend" in raw_type or "pom" in raw_type:
        norm_failure_type = "dependency"
    elif result == "FAILURE":
        norm_failure_type = "unknown"
    else:
        norm_failure_type = "None"

    # Ingest build
    ex("""INSERT OR REPLACE INTO builds (
            build_no, result, commit_hash, branch, failure_type, test_summary, duration_sec, created,
            author, commit_message, trigger_type
          ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Jenkins Webhook')""",
       (build_no, result, commit_hash, branch, norm_failure_type,
        "Test failure" if result=="FAILURE" else "All tests passed", duration, now, author, msg))

    if result == "FAILURE":
        # Parse failure and attribute
        parsed = log_parser.parse_log(log_text)
        p_raw = (parsed.get("failure_type") or norm_failure_type).lower()
        if "compile" in p_raw or "compilation" in p_raw:
            p_failure_type = "compile"
        elif "test" in p_raw or "assertion" in p_raw:
            p_failure_type = "test"
        elif "depend" in p_raw or "pom" in p_raw:
            p_failure_type = "dependency"
        else:
            p_failure_type = "unknown"

        prob_code = f"BUG-{build_no:03d}" if build_no else "BUG-001"
        err_msg = parsed.get("error_message") or "Pipeline test/build execution failed"
        aff_file = parsed.get("failing_class") or "Unknown"

        ex("""INSERT OR REPLACE INTO problems (
                problem_code, build_no, failure_type, error_message, affected_file,
                assignee, status, created, title
              ) VALUES (?, ?, ?, ?, ?, ?, 'Open', ?, ?)""",
           (prob_code, build_no, p_failure_type, err_msg, aff_file,
            author, now, f"Build #{build_no} {p_failure_type.capitalize()} Failure"))

        ex("""INSERT INTO alerts (alert_code, build_no, developer, severity, notification_type, summary, created_at, acknowledged, status)
              VALUES (?, ?, ?, 'Critical', 'Jenkins Pipeline Failure', ?, ?, 0, 'Unread')""",
           (f"ALT-{build_no}", build_no, author, f"Build #{build_no} failed: {err_msg}", now))

    log_audit("Jenkins-Webhook", f"Ingested Build #{build_no}", f"Result: {result}, Branch: {branch}, Commit: {commit_hash}")
    return jsonify({"status": "recorded", "build_no": build_no, "result": result}), 201

if __name__ == "__main__":
    initialize_schema()
    port = int(os.environ.get("PORT", 5000))
    print(f"CommitSleuth Web Application running on http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
