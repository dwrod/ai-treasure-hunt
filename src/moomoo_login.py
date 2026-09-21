"""Browser login for the moomoo price source.

    python -m src.moomoo_login

Opens the moomoo consent page in your browser, the same one Claude Code, Cursor
or Codex open when they connect to the moomoo MCP server, and stores the
resulting token locally so `python -m src.run_signal_engine --source moomoo`
can run without an API key or a dashboard visit.

The flow is OAuth 2.1 with PKCE against the documented endpoints. Moomoo's
consent page determines the granted scopes; the returned token must include
`quote:read`, while additional granted scopes are accepted. The adapter itself
uses only quote endpoints. No password is ever typed here; you log in on
moomoo's own page. Tokens are written to .cache/moomoo/token.json (ignored by
git) with owner-only permissions, and refreshed automatically by the adapter.
"""
import argparse
import base64
import hashlib
import http.server
import json
import os
import secrets
import stat
import sys
import threading
import time
import webbrowser
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlparse
import requests

ROOT = Path(__file__).resolve().parents[1]
TOKEN_FILE = ROOT / ".cache" / "moomoo" / "token.json"
METADATA_URL = "https://mcp.moomoo.com/.well-known/oauth-authorization-server"
DEFAULT_ENDPOINTS = {
    "authorization_endpoint": "https://webapi.moomoo.com/oauth2/authorize/confirm",
    "token_endpoint": "https://webapi.moomoo.com/oauth2/token",
    "registration_endpoint": "https://webapi.moomoo.com/oauth2/register",
}
REQUIRED_SCOPE = "quote:read"
DEFAULT_PORT = 8765                  # 0 lets the operating system pick a free port
CLIENT_NAME = "AI Treasure Hunt signal engine"
REFRESH_MARGIN_SECONDS = 60
REQUIRED_KEYS = ("client_id", "token_endpoint", "access_token", "refresh_token", "expires_at")
RELOGIN = "run `python -m src.moomoo_login`"


def pkce_pair():
    verifier = secrets.token_urlsafe(32)
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    return verifier, challenge


def endpoints(http):
    """The documented endpoints, or the metadata document if it supplies all three."""
    try:
        response = http.get(METADATA_URL, timeout=15)
        data = response.json() if response.status_code == 200 else {}
    except (requests.RequestException, ValueError):
        data = {}
    if all(isinstance(data.get(key), str) for key in DEFAULT_ENDPOINTS):
        return {key: data[key] for key in DEFAULT_ENDPOINTS}
    return dict(DEFAULT_ENDPOINTS)


def register(http, registration_endpoint, redirect_uri):
    """Dynamic client registration for a public (PKCE) client. Returns the client id."""
    body = {"client_name": CLIENT_NAME, "redirect_uris": [redirect_uri],
            "grant_types": ["authorization_code", "refresh_token"], "response_types": ["code"],
            "token_endpoint_auth_method": "none"}
    response = http.post(registration_endpoint, json=body, timeout=30)
    if response.status_code not in (200, 201):
        raise RuntimeError(f"moomoo client registration failed (HTTP {response.status_code}): {response.text[:200]}")
    return response.json()["client_id"]


def exchange(http, token_endpoint, client_id, redirect_uri, code, verifier):
    form = {"grant_type": "authorization_code", "code": code, "redirect_uri": redirect_uri,
            "client_id": client_id, "code_verifier": verifier}
    return _token_response(http.post(token_endpoint, data=form, timeout=30), require_scope=True)


def refresh(http, token_endpoint, client_id, refresh_token):
    form = {"grant_type": "refresh_token", "refresh_token": refresh_token, "client_id": client_id}
    return _token_response(http.post(token_endpoint, data=form, timeout=30))


def _token_response(response, require_scope=False):
    if response.status_code != 200:
        raise RuntimeError(f"moomoo token request failed (HTTP {response.status_code}): {response.text[:200]}")
    data = response.json()
    if "access_token" not in data:
        raise RuntimeError(f"moomoo token response had no access_token: {json.dumps(data)[:200]}")
    if require_scope or data.get("scope"):
        check_scope(data.get("scope"))
    return data


def check_scope(scope):
    """Require quote:read while permitting additional scopes from moomoo consent."""
    granted = set((scope or "").split())
    if REQUIRED_SCOPE not in granted:
        raise RuntimeError(f"moomoo grant is missing required {REQUIRED_SCOPE} scope; token not stored")


def save_token(store, path=None):
    """Write the token file owner-only from the first byte; never echo its contents."""
    path = path or TOKEN_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, stat.S_IRUSR | stat.S_IWUSR)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(json.dumps(store, indent=2) + "\n")
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def load_token(path=None):
    """The stored login, validated, or None when no file exists."""
    path = path or TOKEN_FILE
    if not path.exists():
        return None
    try:
        with open(path, encoding="utf-8") as handle:
            store = json.load(handle)
    except (OSError, ValueError) as exc:
        raise RuntimeError(f"stored moomoo login at {path} is unreadable ({exc}); {RELOGIN}") from exc
    missing = [key for key in REQUIRED_KEYS if not isinstance(store, dict) or key not in store]
    if missing:
        raise RuntimeError(f"stored moomoo login at {path} is missing {', '.join(missing)}; {RELOGIN}")
    check_scope(store.get("scope"))
    return store


def merge_token(store, data):
    """Fold a token response into the stored record; refresh tokens may rotate."""
    out = dict(store)
    out["access_token"] = data["access_token"]
    if data.get("refresh_token"):
        out["refresh_token"] = data["refresh_token"]
    out["expires_at"] = time.time() + float(data.get("expires_in") or 7200)
    if data.get("scope"):
        out["scope"] = data["scope"]
    return out


def refresh_store(store, http=None, path=None):
    """Refresh unconditionally, save, and return (access_token, store)."""
    if not store.get("refresh_token"):
        raise RuntimeError(f"moomoo token expired and cannot be refreshed; {RELOGIN}")
    http = http or requests.Session()
    data = refresh(http, store["token_endpoint"], store["client_id"], store["refresh_token"])
    store = merge_token(store, data)
    save_token(store, path)
    return store["access_token"], store


def fresh_access_token(store, http=None, path=None):
    """Return a usable access token, refreshing and re-saving if it is near expiry."""
    if store.get("expires_at", 0) - time.time() > REFRESH_MARGIN_SECONDS:
        return store["access_token"], store
    return refresh_store(store, http, path)


class _Callback(http.server.BaseHTTPRequestHandler):
    """Receives the single redirect from the consent page."""
    timeout = 10   # applied to each accepted connection; an idle preconnect cannot stall the wait

    def do_GET(self):
        params = {k: v[0] for k, v in parse_qs(urlparse(self.path).query).items()}
        if "code" in params or "error" in params:
            self.server.result = params
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        message = "Login received. You can close this window and return to the terminal." if "code" in params \
            else "Login did not complete. Return to the terminal for details."
        self.wfile.write(f"<html><body style='font-family:sans-serif'><p>{message}</p></body></html>".encode())

    def log_message(self, *args):  # keep the terminal quiet
        pass


def bind(port):
    """Bind the loopback callback server before anything is shown to the user."""
    try:
        server = http.server.HTTPServer(("127.0.0.1", port), _Callback)
    except OSError as exc:
        raise RuntimeError(f"could not listen on 127.0.0.1:{port} ({exc.strerror}); pass --port with a free port, or --port 0") from exc
    server.timeout = 1
    server.result = None
    return server


def wait_for_code(server, expected_state, timeout):
    deadline = time.time() + timeout
    try:
        while time.time() < deadline and server.result is None:
            server.handle_request()
    finally:
        server.server_close()
    result = server.result
    if result is None:
        raise RuntimeError(f"No login received within {timeout} seconds")
    if result.get("state") != expected_state:
        raise RuntimeError("Login response did not match this session (state mismatch); try again")
    if "code" not in result:
        raise RuntimeError(f"Login was not granted: {result.get('error', 'unknown error')} {result.get('error_description', '')}".strip())
    return result["code"]


def login(port=DEFAULT_PORT, timeout=300, http=None, open_browser=webbrowser.open, path=None):
    path = path or TOKEN_FILE
    http = http or requests.Session()
    urls = endpoints(http)
    server = bind(port)
    try:
        redirect_uri = f"http://127.0.0.1:{server.server_address[1]}/callback"
        stored = load_token(path) or {}
        reuse = stored.get("redirect_uri") == redirect_uri and stored.get("token_endpoint") == urls["token_endpoint"]
        client_id = stored["client_id"] if reuse else register(http, urls["registration_endpoint"], redirect_uri)
        verifier, challenge = pkce_pair()
        state = secrets.token_urlsafe(16)
        query = urlencode({"response_type": "code", "client_id": client_id, "redirect_uri": redirect_uri,
                           "state": state, "code_challenge": challenge, "code_challenge_method": "S256"})
        url = f"{urls['authorization_endpoint']}?{query}"
        print("Opening the moomoo login page in your browser. If it does not open, paste this address into a browser:")
        print(url)
        threading.Thread(target=lambda: open_browser(url), daemon=True).start()
        code = wait_for_code(server, state, timeout)
    except BaseException:
        server.server_close()
        raise
    data = exchange(http, urls["token_endpoint"], client_id, redirect_uri, code, verifier)
    store = merge_token({"client_id": client_id, "redirect_uri": redirect_uri, "token_endpoint": urls["token_endpoint"]}, data)
    save_token(store, path)
    return store


def main(argv=None):
    parser = argparse.ArgumentParser(description=f"Log in to moomoo in your browser and store a token with {REQUIRED_SCOPE} for --source moomoo.")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="local port for the login redirect (0 = any free port)")
    parser.add_argument("--timeout", type=int, default=300, help="seconds to wait for the browser login")
    args = parser.parse_args(argv)
    store = login(port=args.port, timeout=args.timeout)
    print(f"Logged in. Scope: {store.get('scope', REQUIRED_SCOPE)}. Token stored at {TOKEN_FILE.relative_to(ROOT)}.")
    print("Run the engine with: python -m src.run_signal_engine --source moomoo")
    return 0


if __name__ == "__main__":
    sys.exit(main())
