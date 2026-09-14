"""Adapter shape, paging, HTTP handling, signing and failure behaviour; no network."""
import base64
import json
import unittest
from unittest.mock import patch
import numpy as np
import pandas as pd
import requests
from src import data_moomoo
from src.run_signal_engine import scan_frames, calendar

try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
except ImportError:  # requirements-engine.txt alone does not install cryptography
    Ed25519PrivateKey = None


def bars(dates):
    """A moomoo-shaped kline_list for the given sessions."""
    close = np.linspace(100, 110, len(dates))
    return [{"date": int(d.strftime("%Y%m%d")), "open": c - 0.5, "close": c, "high": c + 1, "low": c - 1,
             "volume": 1000, "time_key": 0} for d, c in zip(dates, close)]


class FakeSession:
    """Answers history-kline requests from an in-memory series, honouring start/end/num and has_more."""
    def __init__(self, dates, error=None, cap=None, stuck=False):
        self.rows = bars(dates); self.error = error; self.cap = cap; self.stuck = stuck; self.calls = []

    def get(self, path, params):
        self.calls.append((path, dict(params)))
        if self.error: raise RuntimeError(self.error)
        start, end = int(params["start"].replace("-", "")), int(params["end"].replace("-", ""))
        window = [r for r in self.rows if start <= r["date"] <= end]
        if self.stuck: window = list(self.rows)          # ignores end: a backend that never moves the window
        page = window[-min(params["num"], self.cap or params["num"]):]
        return {"kline_list": page, "volume_precision": 0, "pagination": {"has_more": len(page) < len(window)}}

    def close(self): pass


class FakeResponse:
    def __init__(self, status, body, headers=None):
        self.status_code, self.headers = status, headers or {}
        self.text = body if isinstance(body, str) else json.dumps(body)
    def json(self): return json.loads(self.text)


class FakeHttp:
    """Scripted sequence of responses or exceptions for Session.get."""
    def __init__(self, script): self.script = list(script); self.calls = []
    def get(self, url, headers=None, timeout=None):
        self.calls.append((url, headers))
        item = self.script.pop(0)
        if isinstance(item, Exception): raise item
        return item
    def close(self): pass


def ok(kline=None): return FakeResponse(200, {"ret_code": 0, "ret_msg": "success", "data": {"kline_list": kline or []}})


class AdapterTests(unittest.TestCase):
    def setUp(self):
        self.dates = pd.bdate_range("2026-08-03", "2026-08-28")

    def test_shape_and_adjustment_convention(self):
        session = FakeSession(self.dates)
        with patch.object(data_moomoo.time, "sleep"):
            frame = data_moomoo.history(session, "TEST", "2026-08-03", "2026-08-29")
        self.assertEqual(list(frame.columns), data_moomoo.PRICE_COLUMNS)
        self.assertEqual(frame.index.name, "Date"); self.assertIsNone(frame.index.tz)
        self.assertEqual(len(frame), len(self.dates))
        np.testing.assert_allclose(frame["Close"], [r["close"] for r in session.rows])
        np.testing.assert_allclose(frame["Adj Close"], frame["Close"])   # factor one: vendor forward adjustment
        path, params = session.calls[0]
        self.assertEqual(path, "/api/v1.0/quote/US.TEST/history-kline")
        self.assertEqual(params["end"], "2026-08-28")   # exclusive end translated
        self.assertEqual(data_moomoo.ADJUST_FORWARD, 3)  # Moomoo: forward adjustment including dividends.
        self.assertEqual(params["autype"], 3)
        self.assertEqual(len(session.calls), 1)          # one request per symbol

    def test_windows_longer_than_a_page_are_walked_backwards(self):
        dates = pd.bdate_range("2025-03-10", "2026-09-08")   # 390 sessions > 370
        session = FakeSession(dates)
        with patch.object(data_moomoo.time, "sleep"):
            frame = data_moomoo.history(session, "TEST", "2025-03-08", "2026-09-09")
        self.assertEqual(len(frame), len(dates))
        self.assertEqual(str(frame.index.min().date()), "2025-03-10")
        self.assertEqual(len(session.calls), 2)

    def test_has_more_is_honoured_even_when_page_is_short(self):
        dates = pd.bdate_range("2026-01-05", "2026-08-28")   # 170 sessions, well under PAGE
        session = FakeSession(dates, cap=100)               # backend returns short pages but says has_more
        with patch.object(data_moomoo.time, "sleep"):
            frame = data_moomoo.history(session, "TEST", "2026-01-05", "2026-08-29")
        self.assertEqual(len(frame), len(dates))
        self.assertEqual(len(session.calls), 2)

    def test_paging_that_does_not_advance_is_an_error(self):
        dates = pd.bdate_range("2025-03-10", "2026-09-08")
        with patch.object(data_moomoo.time, "sleep"):
            with self.assertRaisesRegex(RuntimeError, "did not advance"):
                data_moomoo.history(FakeSession(dates, stuck=True), "TEST", "2025-03-08", "2026-09-09")

    def test_duplicate_dates_are_passed_through_not_repaired(self):
        session = FakeSession(self.dates); session.rows.append(dict(session.rows[-1]))
        with patch.object(data_moomoo.time, "sleep"):
            frame = data_moomoo.history(session, "TEST", "2026-08-03", "2026-08-29")
        self.assertTrue(frame.index.duplicated().any())

    def test_vendor_error_is_raised_not_masked(self):
        with self.assertRaisesRegex(RuntimeError, "Symbol not found"):
            data_moomoo.history(FakeSession(self.dates, error="Symbol not found"), "TEST", "2026-08-03", "2026-08-29")

    def test_empty_response_is_explicit(self):
        with self.assertRaisesRegex(ValueError, "Empty"):
            data_moomoo.history(FakeSession(self.dates[:0]), "TEST", "2026-08-03", "2026-08-29")

    def test_missing_credentials_are_explicit(self):
        from src import moomoo_login
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as tmp, patch.dict(data_moomoo.os.environ, {}, clear=True), \
                patch.object(moomoo_login, "TOKEN_FILE", Path(tmp) / "token.json"):   # never the user's real login
            with self.assertRaisesRegex(RuntimeError, "credentials missing"):
                data_moomoo.connect()

    def test_empty_page_while_vendor_reports_more_is_an_error(self):
        session = FakeSession(self.dates)
        session.get = lambda path, params: {"kline_list": [], "pagination": {"has_more": True}}
        with self.assertRaisesRegex(RuntimeError, "empty page"):
            data_moomoo.history(session, "TEST", "2026-08-03", "2026-08-29")

    def test_engine_accepts_adapter_output_unchanged(self):
        now = pd.Timestamp("2026-09-09T22:00Z"); cal = calendar(now)
        target = pd.Timestamp("2026-09-09"); sessions = cal.sessions_in_range(cal.first_session, target)
        with patch.object(data_moomoo.time, "sleep"):
            frame = data_moomoo.history(FakeSession(sessions), "AAPL", "2025-03-08", "2026-09-10")
        scans, adjusted, audits = scan_frames({"AAPL": frame}, target, cal, now, {"AAPL": "UNAVAILABLE"})
        self.assertEqual(scans[0]["data_status"], "OK")
        self.assertEqual(audits["AAPL"]["invalid_adjustment_or_bar_dates"], [])
        np.testing.assert_allclose(adjusted["AAPL"]["Close"].dropna(), frame["Close"])


class HttpLayerTests(unittest.TestCase):
    def session(self, script):
        return data_moomoo.Session(access_token="t", http=FakeHttp(script))

    def test_bearer_header_and_data_extraction(self):
        s = self.session([ok([{"date": 20260901}])])
        data = s.get("/api/v1.0/quote/US.GS/history-kline", {"end": "2026-09-01"})
        self.assertEqual(data["kline_list"][0]["date"], 20260901)
        url, headers = s.http.calls[0]
        self.assertEqual(headers, {"Authorization": "Bearer t"})
        self.assertTrue(url.startswith("https://webapi.moomoo.com/api/v1.0/quote/US.GS/history-kline?end="))

    def test_rate_limit_numeric_and_http_date_retry_after(self):
        s = self.session([FakeResponse(429, "", {"Retry-After": "1"}),
                          FakeResponse(429, "", {"Retry-After": "Wed, 21 Oct 2015 07:28:00 GMT"}), ok()])
        with patch.object(data_moomoo.time, "sleep") as sleep:
            self.assertEqual(s.get("/p", {}), {"kline_list": []})
        self.assertEqual([round(c.args[0]) for c in sleep.call_args_list], [1, 0])

    def test_server_errors_and_transport_errors_are_retried(self):
        s = self.session([FakeResponse(503, "busy"), requests.Timeout(), requests.ConnectionError(), ok()])
        with patch.object(data_moomoo.time, "sleep"):
            self.assertEqual(s.get("/p", {}), {"kline_list": []})

    def test_back_off_is_bounded(self):
        s = self.session([FakeResponse(429, "slow", {"Retry-After": "3600"})])
        with patch.object(data_moomoo.time, "sleep") as sleep:
            with self.assertRaisesRegex(RuntimeError, "persisted"):
                s.get("/p", {})
        sleep.assert_not_called()

    def test_credential_rejection_null_data_non_json_and_error_bodies(self):
        with self.assertRaisesRegex(RuntimeError, "rejected the credentials"):
            self.session([FakeResponse(401, {"code": -12006})]).get("/p", {})
        self.assertEqual(self.session([FakeResponse(200, {"ret_code": 0, "data": None})]).get("/p", {}), {})
        with self.assertRaisesRegex(RuntimeError, "non-JSON"):
            self.session([FakeResponse(200, "<html>proxy</html>")]).get("/p", {})
        with self.assertRaisesRegex(RuntimeError, "HTTP 404 for /p: .*ret_msg"):
            self.session([FakeResponse(404, {"ret_code": -7, "ret_msg": "Symbol not found"})]).get("/p", {})
        with self.assertRaisesRegex(RuntimeError, "error -7 for /p: Symbol not found"):
            self.session([FakeResponse(200, {"ret_code": -7, "ret_msg": "Symbol not found"})]).get("/p", {})

    def test_refresh_on_401_is_outside_the_retry_budget(self):
        # Four retriable responses exhaust nothing: the refresh still runs and the fresh token is sent.
        http = FakeHttp([FakeResponse(503, ""), FakeResponse(502, ""), requests.Timeout(), FakeResponse(429, "", {"Retry-After": "1"}),
                         FakeResponse(401, {"code": -12006}), ok([{"date": 1}])])
        s = data_moomoo.Session(access_token="stale", http=http, refresh=lambda: "fresh")
        with patch.object(data_moomoo.time, "sleep"):
            self.assertEqual(s.get("/p", {})["kline_list"], [{"date": 1}])
        self.assertEqual(http.calls[-1][1], {"Authorization": "Bearer fresh"})
        self.assertEqual(http.calls[-2][1], {"Authorization": "Bearer stale"})

    def test_failed_refresh_is_sticky_and_stops_calling_the_vendor(self):
        def broken(): raise RuntimeError("token request failed (HTTP 400)")
        http = FakeHttp([FakeResponse(401, {"code": -12006})])
        s = data_moomoo.Session(access_token="stale", http=http, refresh=broken)
        with self.assertRaisesRegex(RuntimeError, "could not be refreshed.*moomoo_login"):
            s.get("/p", {})
        with self.assertRaisesRegex(RuntimeError, "could not be refreshed"):
            s.get("/q", {})                       # no further HTTP call for later symbols
        self.assertEqual(len(http.calls), 1)

    def test_second_401_after_refresh_is_a_rejection(self):
        http = FakeHttp([FakeResponse(401, {"code": -12006}), FakeResponse(401, {"code": -12006})])
        s = data_moomoo.Session(access_token="stale", http=http, refresh=lambda: "fresh")
        with self.assertRaisesRegex(RuntimeError, "rejected the credentials"):
            s.get("/p", {})

    def test_probe_uses_a_cheap_authenticated_call(self):
        s = self.session([FakeResponse(200, {"ret_code": 0, "data": {"trading_days": []}})])
        s.probe()
        self.assertIn("/api/v1.0/quote/trading-days?market=US", s.http.calls[0][0])

    @unittest.skipUnless(Ed25519PrivateKey, "cryptography not installed (requirements-moomoo.txt)")
    def test_signature_follows_documented_template_and_verifies(self):
        key = Ed25519PrivateKey.generate()
        query = "start=2026-09-01&end=2026-09-08&ktype=2&autype=3&num=370"
        message = data_moomoo.string_to_sign(1700000000000, "GET", "/api/v1.0/quote/US.GS/history-kline", query)
        self.assertEqual(message, "1700000000000\nGET\n/api/v1.0/quote/US.GS/history-kline\n" + query + "\n")
        signature = data_moomoo.sign(key, 1700000000000, "GET", "/api/v1.0/quote/US.GS/history-kline", query)
        key.public_key().verify(base64.b64decode(signature), message.encode())   # raises if wrong

    @unittest.skipUnless(Ed25519PrivateKey, "cryptography not installed (requirements-moomoo.txt)")
    def test_api_key_headers_are_set_and_rsa_branch_signs(self):
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric import rsa
        pem = Ed25519PrivateKey.generate().private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
                                                         serialization.NoEncryption())
        s = data_moomoo.Session(api_key="k", private_key_pem=pem, http=FakeHttp([ok()]))
        s.get("/p", {"a": 1})
        headers = s.http.calls[0][1]
        self.assertEqual(headers["X-Api-Key"], "k")
        self.assertEqual(set(headers), {"X-Api-Key", "Authorization", "X-Timestamp", "X-Nonce"})
        self.assertNotIn("Bearer", headers["Authorization"])
        rsa_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        sig = data_moomoo.sign(rsa_key, 1, "GET", "/p", "a=1")
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import padding
        rsa_key.public_key().verify(base64.b64decode(sig), data_moomoo.string_to_sign(1, "GET", "/p", "a=1").encode(),
                                    padding.PKCS1v15(), hashes.SHA256())


if __name__ == "__main__":
    unittest.main()
