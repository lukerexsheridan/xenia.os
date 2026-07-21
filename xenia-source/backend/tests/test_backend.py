"""Backend API tests for Xenia MVP + iteration 4 additions.

Endpoints under test:
- GET /api/  -> health/root
- POST /api/access -> create/idempotent, 422 on invalid
- GET /api/access -> list
- POST /api/admin/login -> wrong pw (401), correct pw (200 with token)
- GET /api/admin/leads -> without auth (401), with valid token (200)
- POST /api/chat/stream -> empty text (422), streams SSE with real Claude tokens
"""

import os
import uuid
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
# Fallback to frontend .env if env var isn't in shell
if not BASE_URL:
    try:
        with open("/app/frontend/.env") as f:
            for line in f:
                if line.startswith("REACT_APP_BACKEND_URL="):
                    BASE_URL = line.split("=", 1)[1].strip().rstrip("/")
                    break
    except Exception:
        pass

assert BASE_URL, "REACT_APP_BACKEND_URL is required"

ADMIN_PASSWORD = "xenia-admin-2026"


@pytest.fixture(scope="module")
def api():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


# --- Root ---
def test_root(api):
    r = api.get(f"{BASE_URL}/api/", timeout=15)
    assert r.status_code == 200
    assert r.json() == {"message": "Xenia"}


# --- Access: create ---
def test_create_access_valid(api):
    email = f"test_{uuid.uuid4().hex[:10]}@example.com"
    payload = {"email": email, "role": "Growth Lead"}
    r = api.post(f"{BASE_URL}/api/access", json=payload, timeout=15)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["email"] == email.lower()
    assert body["role"] == "Growth Lead"
    assert "id" in body and isinstance(body["id"], str)
    assert "created_at" in body


def test_create_access_idempotent(api):
    email = f"test_{uuid.uuid4().hex[:10]}@example.com"
    r1 = api.post(f"{BASE_URL}/api/access", json={"email": email, "role": "A"}, timeout=15)
    assert r1.status_code == 200
    id1 = r1.json()["id"]

    r2 = api.post(f"{BASE_URL}/api/access", json={"email": email, "role": "B"}, timeout=15)
    assert r2.status_code == 200
    id2 = r2.json()["id"]
    assert id1 == id2, "Idempotency broken - new id created for existing email"

    lst = api.get(f"{BASE_URL}/api/access", timeout=15).json()
    matches = [x for x in lst if x["email"] == email.lower()]
    assert len(matches) == 1


def test_create_access_invalid_email(api):
    r = api.post(f"{BASE_URL}/api/access", json={"email": "not-an-email"}, timeout=15)
    assert r.status_code == 422


# --- Access: list ---
def test_list_access_includes_created(api):
    email = f"test_{uuid.uuid4().hex[:10]}@example.com"
    create = api.post(f"{BASE_URL}/api/access", json={"email": email}, timeout=15)
    assert create.status_code == 200

    r = api.get(f"{BASE_URL}/api/access", timeout=15)
    assert r.status_code == 200
    rows = r.json()
    assert isinstance(rows, list)
    emails = [row["email"] for row in rows]
    assert email.lower() in emails


# --- Admin: login ---
def test_admin_login_wrong_password(api):
    r = api.post(f"{BASE_URL}/api/admin/login", json={"password": "wrongpw"}, timeout=15)
    assert r.status_code == 401
    body = r.json()
    assert "detail" in body


def test_admin_login_success(api):
    r = api.post(f"{BASE_URL}/api/admin/login", json={"password": ADMIN_PASSWORD}, timeout=15)
    assert r.status_code == 200, r.text
    body = r.json()
    assert "token" in body and isinstance(body["token"], str) and len(body["token"]) > 20
    assert "expires_at" in body


@pytest.fixture(scope="module")
def admin_token(api):
    r = api.post(f"{BASE_URL}/api/admin/login", json={"password": ADMIN_PASSWORD}, timeout=15)
    assert r.status_code == 200, r.text
    return r.json()["token"]


# --- Admin: leads ---
def test_admin_leads_no_auth(api):
    r = api.get(f"{BASE_URL}/api/admin/leads", timeout=15)
    assert r.status_code == 401


def test_admin_leads_bad_token(api):
    r = api.get(
        f"{BASE_URL}/api/admin/leads",
        headers={"Authorization": "Bearer not-a-real-token"},
        timeout=15,
    )
    assert r.status_code == 401


def test_admin_leads_with_valid_token(api, admin_token):
    # Ensure at least one lead exists so list is non-trivial
    email = f"test_admin_{uuid.uuid4().hex[:10]}@example.com"
    api.post(f"{BASE_URL}/api/access", json={"email": email}, timeout=15)

    r = api.get(
        f"{BASE_URL}/api/admin/leads",
        headers={"Authorization": f"Bearer {admin_token}"},
        timeout=15,
    )
    assert r.status_code == 200, r.text
    rows = r.json()
    assert isinstance(rows, list)
    # The one we just created should be in the list
    assert any(row["email"] == email.lower() for row in rows)


# --- Chat stream ---
def test_chat_stream_empty_text(api):
    r = api.post(
        f"{BASE_URL}/api/chat/stream",
        json={"session_id": "unit-test", "text": ""},
        timeout=15,
    )
    # Pydantic min length not enforced - server explicitly raises 422 in handler when stripped text is empty.
    assert r.status_code == 422


# --- Chat summarise (iteration 6) ---
def test_chat_summarise_empty_messages(api):
    r = api.post(f"{BASE_URL}/api/chat/summarise", json={"messages": []}, timeout=15)
    assert r.status_code == 422
    body = r.json()
    assert "detail" in body


def test_chat_summarise_no_user_messages(api):
    # only assistant messages -> 422
    payload = {
        "messages": [
            {"from": "xenia", "text": "Hi, I'm Xenia."},
            {"from": "xenia", "text": "How can I help?"},
        ]
    }
    r = api.post(f"{BASE_URL}/api/chat/summarise", json=payload, timeout=15)
    assert r.status_code == 422, r.text
    body = r.json()
    assert "no user messages to summarise" in str(body.get("detail", "")).lower()


def test_chat_summarise_success(api):
    payload = {
        "messages": [
            {"from": "xenia", "text": "Hi"},
            {"from": "user", "text": "Tell me about Northlake Robotics Series B"},
            {"from": "xenia", "text": "Northlake closed a Series B. Strong signal."},
        ]
    }
    r = api.post(f"{BASE_URL}/api/chat/summarise", json=payload, timeout=60)
    assert r.status_code == 200, r.text
    body = r.json()
    assert "summary" in body
    assert isinstance(body["summary"], str)
    assert len(body["summary"].strip()) > 0
    # Explicit acceptance: system prompt forbids exclamation marks
    assert "!" not in body["summary"], f"summary must not contain '!': {body['summary']!r}"


def test_chat_stream_returns_sse_tokens(api):
    """Live Claude call — verify SSE 'data:' lines arrive and stream terminates."""
    session_id = f"unit-test-{uuid.uuid4().hex[:8]}"
    with api.post(
        f"{BASE_URL}/api/chat/stream",
        json={"session_id": session_id, "text": "Give me a one-sentence briefing."},
        stream=True,
        timeout=45,
    ) as r:
        assert r.status_code == 200, r.text
        ctype = r.headers.get("content-type", "")
        assert "text/event-stream" in ctype, f"unexpected content-type: {ctype}"
        got_data_line = False
        got_done = False
        collected = ""
        for raw in r.iter_lines(decode_unicode=True):
            if raw is None:
                continue
            if raw.startswith("data: "):
                got_data_line = True
                collected += raw[6:]
            elif raw.startswith("event: done"):
                got_done = True
                # read one more data line then break
            if got_done and got_data_line:
                # once we've seen done + at least one data, break early
                break
            if len(collected) > 500:
                break
        assert got_data_line, "No 'data: ...' SSE lines received from /api/chat/stream"
        assert len(collected) > 0
