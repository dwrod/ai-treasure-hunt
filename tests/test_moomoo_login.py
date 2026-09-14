"""Browser-login helper: PKCE, discovery, registration, exchange, storage, scope and refresh; no browser."""
import base64
import hashlib
import json
import os
import socket
import stat
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import patch
import requests
from src import moomoo_login, data_moomoo


class FakeResponse:
    def __init__(self, status, body, headers=None):
        self.status_code, self.headers = status, headers or {}
        self.text = json.dumps(body); self._body = body
    def json(self): return self._body


class FakeHttp:
    def __init__(self, metadata=None, register=None, token=None):
        self.metadata, self.register, self.token, self.posts = metadata, register, token, []
    def get(self, url, timeout=None, headers=None):
        if url == moomoo_login.METADATA_URL:
            return FakeResponse(200, self.metadata) if self.metadata is not None else FakeResponse(503, {})
        return FakeResponse(200, {"ret_code": 0, "data": {}})
    def post(self, url, json=None, data=None, timeout=None):
        self.posts.append((url, json, data))
        if url.endswith("/register"): return FakeResponse(201, self.register)
        return FakeResponse(200, self.token)


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0)); return s.getsockname()[1]


def good_store(**extra):
    store = {"client_id": "c", "token_endpoint": "https://t/oauth2/token", "access_token": "a",
             "refresh_token": "r", "expires_at": time.time() + 3600, "scope": "quote:read"}
    store.update(extra); return store


class LoginTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.path = Path(self.tmp.name) / "token.json"
    def tearDown(self):
        self.tmp.cleanup()

    def test_pkce_challenge_is_s256_of_verifier(self):
        verifier, challenge = moomoo_login.pkce_pair()
        expected = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
        self.assertEqual(challenge, expected); self.assertGreaterEqual(len(verifier), 43)

    def test_endpoints_are_taken_wholesale_or_defaulted_wholesale(self):
        self.assertEqual(moomoo_login.endpoints(FakeHttp(metadata=None)), moomoo_login.DEFAULT_ENDPOINTS)
        partial = {"token_endpoint": "https://example.test/token"}          # missing keys: never mixed with defaults
        self.assertEqual(moomoo_login.endpoints(FakeHttp(metadata=partial)), moomoo_login.DEFAULT_ENDPOINTS)
        full = {k: f"https://example.test/{k}" for k in moomoo_login.DEFAULT_ENDPOINTS}
        self.assertEqual(moomoo_login.endpoints(FakeHttp(metadata=full)), full)

    def test_token_file_is_owner_only_from_creation_and_round_trips(self):
        real_open = os.open; seen = {}
        def spy(path, flags, mode=0o777):
            seen["mode"] = mode; return real_open(path, flags, mode)
        with patch.object(moomoo_login.os, "open", spy):
            moomoo_login.save_token(good_store(), self.path)
        self.assertEqual(seen["mode"], 0o600)
        self.assertEqual(stat.S_IMODE(os.stat(self.path).st_mode), 0o600)
        self.assertEqual(moomoo_login.load_token(self.path)["client_id"], "c")
        self.assertIsNone(moomoo_login.load_token(self.path.with_name("missing.json")))
        self.assertFalse(self.path.with_suffix(".tmp").exists())

    def test_unreadable_or_incomplete_token_file_explains_relogin(self):
        self.path.write_text("{not json")
        with self.assertRaisesRegex(RuntimeError, "unreadable.*moomoo_login"):
            moomoo_login.load_token(self.path)
        self.path.write_text(json.dumps({"access_token": "a"}))
        with self.assertRaisesRegex(RuntimeError, "missing client_id.*moomoo_login"):
            moomoo_login.load_token(self.path)

    def test_broader_scope_is_refused_everywhere(self):
        with self.assertRaisesRegex(RuntimeError, "trade:write.*not stored"):
            moomoo_login._token_response(FakeResponse(200, {"access_token": "a", "scope": "quote:read trade:write"}))
        moomoo_login.save_token(good_store(scope="quote:read accid:*"), self.path)
        with self.assertRaisesRegex(RuntimeError, "accid"):
            moomoo_login.load_token(self.path)
        moomoo_login.check_scope(None); moomoo_login.check_scope("quote:read")   # accepted

    def test_fresh_token_refreshes_near_expiry_and_keeps_rotated_refresh_token(self):
        store = good_store(expires_at=time.time() + 10, access_token="old", refresh_token="r1")
        http = FakeHttp(token={"access_token": "new", "refresh_token": "r2", "expires_in": 7200})
        token, store = moomoo_login.fresh_access_token(store, http, self.path)
        self.assertEqual(token, "new"); self.assertEqual(store["refresh_token"], "r2")
        self.assertEqual(json.loads(self.path.read_text())["access_token"], "new")
        _, _, form = http.posts[0]
        self.assertEqual(form["grant_type"], "refresh_token"); self.assertEqual(form["client_id"], "c")
        http.posts.clear()
        token, _ = moomoo_login.fresh_access_token(store, http, self.path)   # still valid: no network call
        self.assertEqual(token, "new"); self.assertEqual(http.posts, [])
        with self.assertRaisesRegex(RuntimeError, "moomoo_login"):
            moomoo_login.refresh_store(good_store(refresh_token=""), http, self.path)

    def test_full_login_flow_binds_before_browser_registers_exchanges_and_stores(self):
        http = FakeHttp(metadata=None, register={"client_id": "cid"},
                        token={"access_token": "acc", "refresh_token": "ref", "expires_in": 7200, "scope": "quote:read"})
        captured = {}
        def fake_browser(url):
            from urllib.parse import urlparse, parse_qs
            q = {k: v[0] for k, v in parse_qs(urlparse(url).query).items()}
            captured["url"] = url; captured["q"] = q
            # The server is already listening when the browser opens, so this succeeds immediately.
            requests.get(f"{q['redirect_uri']}?code=CODE123&state={q['state']}", timeout=5)
        port = free_port()
        store = moomoo_login.login(port=port, timeout=10, http=http, open_browser=fake_browser, path=self.path)
        self.assertEqual(store["access_token"], "acc"); self.assertEqual(store["client_id"], "cid")
        self.assertEqual(captured["q"]["scope"], "quote:read"); self.assertEqual(captured["q"]["code_challenge_method"], "S256")
        self.assertEqual(captured["q"]["redirect_uri"], f"http://127.0.0.1:{port}/callback")
        reg_url, reg_json, _ = http.posts[0]
        self.assertEqual(reg_json["token_endpoint_auth_method"], "none")
        _, _, form = http.posts[1]
        self.assertEqual(form["grant_type"], "authorization_code"); self.assertEqual(form["code"], "CODE123")
        self.assertIn("code_verifier", form)
        self.assertEqual(stat.S_IMODE(os.stat(self.path).st_mode), 0o600)
        http.posts.clear()   # same port and endpoints: the registered client is reused
        moomoo_login.login(port=port, timeout=10, http=http, open_browser=fake_browser, path=self.path)
        self.assertTrue(all(not u.endswith("/register") for u, _, _ in http.posts))

    def test_busy_port_fails_before_the_browser_opens(self):
        holder = socket.socket(); holder.bind(("127.0.0.1", 0)); holder.listen(1)
        try:
            opened = []
            with self.assertRaisesRegex(RuntimeError, "--port"):
                moomoo_login.login(port=holder.getsockname()[1], timeout=1, http=FakeHttp(register={"client_id": "x"}),
                                   open_browser=opened.append, path=self.path)
            self.assertEqual(opened, [])
        finally:
            holder.close()

    def test_idle_connection_does_not_block_the_real_redirect(self):
        server = moomoo_login.bind(0); port = server.server_address[1]
        idle = socket.create_connection(("127.0.0.1", port))            # connects, never sends a request line
        def redirect():
            time.sleep(0.2); requests.get(f"http://127.0.0.1:{port}/callback?code=OK&state=s", timeout=5)
        threading.Thread(target=redirect, daemon=True).start()
        with patch.object(moomoo_login._Callback, "timeout", 0.5):
            started = time.time()
            self.assertEqual(moomoo_login.wait_for_code(server, "s", timeout=10), "OK")
        self.assertLess(time.time() - started, 5)
        idle.close()

    def test_state_mismatch_and_denied_login_are_rejected(self):
        for query, message in [("code=X&state=wrong", "state mismatch"), ("error=access_denied&state=right", "access_denied")]:
            server = moomoo_login.bind(0); port = server.server_address[1]
            threading.Timer(0.05, lambda: requests.get(f"http://127.0.0.1:{port}/callback?{query}", timeout=5)).start()
            with self.assertRaisesRegex(RuntimeError, message):
                moomoo_login.wait_for_code(server, "right", timeout=5)


class AdapterUsesStoredLoginTests(unittest.TestCase):
    def test_connect_prefers_environment_then_stored_login_then_explains(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "token.json"
            with patch.dict(data_moomoo.os.environ, {}, clear=True), patch.object(moomoo_login, "TOKEN_FILE", path):
                with self.assertRaisesRegex(RuntimeError, "python -m src.moomoo_login"):
                    data_moomoo.connect()
                moomoo_login.save_token(good_store(access_token="stored"), path)
                session = data_moomoo.connect()
                self.assertEqual(session.access_token, "stored"); self.assertIsNotNone(session.refresh)
                moomoo_login.save_token(good_store(scope="quote:read trade:read"), path)
                with self.assertRaisesRegex(RuntimeError, "trade:read"):
                    data_moomoo.connect()
            with patch.dict(data_moomoo.os.environ, {"MOOMOO_ACCESS_TOKEN": "env"}, clear=True), patch.object(moomoo_login, "TOKEN_FILE", path):
                self.assertEqual(data_moomoo.connect().access_token, "env")


if __name__ == "__main__":
    unittest.main()
