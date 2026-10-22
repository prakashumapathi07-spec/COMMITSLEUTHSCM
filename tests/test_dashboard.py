"""Integration tests for the CommitSleuth Flask Dashboard and Role-Based Access Control."""
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "dashboard"))
from app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test-secret"
    with app.test_client() as client:
        yield client

def test_login_redirect_when_unauthenticated(client):
    response = client.get("/")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]

def test_login_page_renders(client):
    response = client.get("/login")
    assert response.status_code == 200
    assert b"CommitSleuth Portal Access" in response.data

def test_login_success(client):
    response = client.post("/login", data={"username": "prakash", "password": "admin123"}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Executive SCM Dashboard" in response.data
    assert b"prakash" in response.data

def test_viewer_role_access(client):
    with client.session_transaction() as sess:
        sess["user"] = "viewer"
        sess["role"] = "viewer"
    
    # Viewer can view dashboard
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"Executive SCM Dashboard" in resp.data

    # Viewer cannot raise CR
    resp_cr = client.post("/cr/new", data={"cr_id": "CR-999", "title": "t", "description": "d", "impact": "i", "branch": "b"}, follow_redirects=True)
    assert b"Permission Denied" in resp_cr.data

def test_routes_accessible_by_authenticated_user(client):
    with client.session_transaction() as sess:
        sess["user"] = "bharath"
        sess["role"] = "admin"

    routes = ["/builds", "/problems", "/crs", "/cis", "/baselines", "/promotions", "/audits", "/report", "/config", "/audit-trail"]
    for r in routes:
        resp = client.get(r)
        assert resp.status_code == 200, f"Route {r} failed with status {resp.status_code}"

def test_csv_export(client):
    with client.session_transaction() as sess:
        sess["user"] = "prakash"
        sess["role"] = "admin"
    resp = client.get("/report/csv")
    assert resp.status_code == 200
    assert resp.mimetype == "text/csv"
    assert b"CI ID,Configuration Item Name,Version" in resp.data
