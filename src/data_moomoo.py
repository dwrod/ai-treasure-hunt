"""moomoo Open API price source for the frozen signal engine.

Talks to the hosted REST surface (https://webapi.moomoo.com), the same backend
the moomoo MCP server exposes to Claude Code, Cursor and Codex. No local OpenD
gateway and no SDK. Returns the frame the engine already consumes from Yahoo:
a Date-indexed table of Open, High, Low, Close, Adj Close and Volume in local
session dates. Nothing here computes a feature, adjusts a price or touches the
journal; the engine's frozen src.data.adjust_ohlc keeps doing that from
Adj Close / Close.

One request per symbol: the vendor's forward-adjusted daily bars, which fold in
cash dividends and splits the way Yahoo's Adj Close does. Adj Close is set equal
to Close, so the engine's adjustment factor is one and the adjusted series it
computes is the vendor's forward-adjusted series unchanged. This is the path the
September 8 acceptance replay validated. Snapshot CSVs written from this source
therefore hold forward-adjusted prices, not raw prints.

Vendor anomalies are passed through, never repaired: duplicate or unexpected
session dates reach the engine's own audit and quarantine logic.

Credentials, in order of preference:
  python -m src.moomoo_login              browser login; token stored under .cache/
                                          and refreshed here automatically, or
  MOOMOO_ACCESS_TOKEN                     OAuth bearer token (scope quote:read), or
  MOOMOO_API_KEY + MOOMOO_PRIVATE_KEY_FILE AppKey id plus the PEM private key
                                          registered at open.moomoo.com/dashboard
                                          (Ed25519 or RSA-SHA256).
Environment variables win when set; nothing is written by this module.
"""
import base64
import hashlib
import os
import secrets
import time
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import urlencode
import pandas as pd
import requests
from .data import OHLC

BASE_URL = "https://webapi.moomoo.com"
MARKET = "US"
PRICE_COLUMNS = [*OHLC, "Adj Close", "Volume"]
KLINE_DAY = 2
ADJUST_FORWARD = 3  # Forward adjustment including cash dividends.
PAGE = 370             # documented maximum bars per request
MAX_PAGES = 12         # hard stop for the backwards walk; the engine window needs two
MAX_RETRIES = 5        # per request, for 429, 5xx and transport errors
MAX_WAIT_SECONDS = 60  # total back-off per request before giving up on the symbol
RETRIABLE_STATUS = {429, 500, 502, 503, 504}
MISSING_CREDENTIALS = ("moomoo credentials missing: run `python -m src.moomoo_login`, or set MOOMOO_ACCESS_TOKEN, "
                       "or MOOMOO_API_KEY and MOOMOO_PRIVATE_KEY_FILE")


class Session:
    """One authenticated HTTP session against the moomoo Open API."""

    def __init__(self, access_token=None, api_key=None, private_key_pem=None, base_url=BASE_URL, http=None, refresh=None):
        if not access_token and not (api_key and private_key_pem):
            raise RuntimeError(MISSING_CREDENTIALS)
        self.access_token = access_token
        self.api_key = api_key
        self.private_key = _load_private_key(private_key_pem) if private_key_pem else None
        self.base_url = base_url.rstrip("/")
        self.http = http or requests.Session()
        self.refresh = refresh          # optional callable returning a new access token
        self.refresh_failed = None      # sticky: once a refresh fails, stop trying

    def headers(self, method, path, query):
        if self.access_token:
            return {"Authorization": f"Bearer {self.access_token}"}
        timestamp = str(int(time.time() * 1000))
        signature = sign(self.private_key, timestamp, method, path, query, body=b"")
        return {"X-Api-Key": self.api_key, "Authorization": signature,
                "X-Timestamp": timestamp, "X-Nonce": secrets.token_hex(16)}

    def get(self, path, params):
        """GET a JSON endpoint; returns the `data` object ({} when null) or raises."""
        if self.refresh_failed:
            raise RuntimeError(self.refresh_failed)
        query = urlencode(params)
        url = f"{self.base_url}{path}?{query}"
        response = self._request(url, path, query)
        if response.status_code == 401 and self.refresh is not None:
            # A stored login can expire mid-run: refresh once, outside the retry budget, and resend.
            self._refresh_access_token()
            response = self._request(url, path, query)
        if response.status_code in (401, 403):
            raise RuntimeError(f"moomoo Open API rejected the credentials (HTTP {response.status_code}): {response.text[:200]}")
        if response.status_code != 200:
            raise RuntimeError(f"moomoo Open API HTTP {response.status_code} for {path}: {response.text[:200]}")
        try:
            payload = response.json()
        except ValueError as exc:
            raise RuntimeError(f"moomoo Open API returned a non-JSON body for {path}: {response.text[:120]!r}") from exc
        if not isinstance(payload, dict):
            raise RuntimeError(f"moomoo Open API returned an unexpected body for {path}: {response.text[:120]!r}")
        code = payload.get("ret_code", payload.get("code", 0))
        if code != 0:
            raise RuntimeError(f"moomoo Open API error {code} for {path}: {payload.get('ret_msg', '')}")
        return payload.get("data") or {}

    def _request(self, url, path, query):
        """One GET with bounded retries for rate limits, server errors and transport errors."""
        waited = 0.0
        for attempt in range(MAX_RETRIES):
            try:
                response = self.http.get(url, headers=self.headers("GET", path, query), timeout=30)
            except (requests.ConnectionError, requests.Timeout) as exc:
                reason, delay = type(exc).__name__, float(2 ** attempt)
            else:
                if response.status_code not in RETRIABLE_STATUS:
                    return response
                reason = f"HTTP {response.status_code}"
                delay = retry_after_seconds(response.headers.get("Retry-After"), 2 ** attempt)
            # Every retry costs at least one second of budget so a zero Retry-After cannot spin.
            if attempt == MAX_RETRIES - 1 or waited + max(delay, 1.0) > MAX_WAIT_SECONDS:
                raise RuntimeError(f"moomoo Open API {reason} persisted after {attempt + 1} attempts "
                                   f"and {waited:.0f}s of back-off for {path}")
            time.sleep(delay)
            waited += max(delay, 1.0)
        raise RuntimeError(f"moomoo Open API request did not complete for {path}")

    def _refresh_access_token(self):
        try:
            self.access_token = self.refresh()
        except Exception as exc:
            self.refresh_failed = f"moomoo login could not be refreshed ({exc}); run `python -m src.moomoo_login`"
            raise RuntimeError(self.refresh_failed) from exc

    def probe(self):
        """One cheap authenticated call so bad or expired credentials fail up front."""
        today = datetime.now(timezone.utc).date()
        self.get("/api/v1.0/quote/trading-days",
                 {"market": MARKET, "start": str(today - timedelta(days=7)), "end": str(today)})

    def close(self):
        self.http.close()


def retry_after_seconds(header, default):
    """Retry-After as seconds, accepting the delta-seconds and HTTP-date forms."""
    if header is None:
        return float(default)
    try:
        return max(0.0, float(header))
    except ValueError:
        pass
    try:
        when = parsedate_to_datetime(header)
    except (TypeError, ValueError):
        return float(default)
    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone.utc)
    return max(0.0, (when - datetime.now(timezone.utc)).total_seconds())


def connect():
    """Build a Session from the environment, else from the stored browser login. Caller closes it."""
    pem = None
    key_file = os.environ.get("MOOMOO_PRIVATE_KEY_FILE")
    if key_file:
        with open(os.path.expanduser(key_file), "rb") as handle:
            pem = handle.read()
    base_url = os.environ.get("MOOMOO_API_BASE", BASE_URL)
    access_token = os.environ.get("MOOMOO_ACCESS_TOKEN")
    if access_token or (os.environ.get("MOOMOO_API_KEY") and pem):
        return Session(access_token=access_token, api_key=os.environ.get("MOOMOO_API_KEY"),
                       private_key_pem=pem, base_url=base_url)
    from . import moomoo_login
    store = moomoo_login.load_token()
    if not store:
        raise RuntimeError(MISSING_CREDENTIALS)
    http = requests.Session()
    token, store = moomoo_login.fresh_access_token(store, http)

    def refresh_now():
        nonlocal store
        token, store = moomoo_login.refresh_store(store, http)
        return token

    return Session(access_token=token, base_url=base_url, http=http, refresh=refresh_now)


def string_to_sign(timestamp_ms, method, path, query, body=b""):
    """Documented template: timestamp, method, path, raw query, sha256(body) or ''."""
    body_part = hashlib.sha256(body).hexdigest() if body else ""
    return "\n".join([str(timestamp_ms), method.upper(), path, query or "", body_part])


def sign(private_key, timestamp_ms, method, path, query, body=b""):
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import padding, rsa
    message = string_to_sign(timestamp_ms, method, path, query, body).encode()
    if isinstance(private_key, rsa.RSAPrivateKey):
        raw = private_key.sign(message, padding.PKCS1v15(), hashes.SHA256())
    else:
        raw = private_key.sign(message)
    return base64.b64encode(raw).decode()


def _load_private_key(pem):
    try:
        from cryptography.hazmat.primitives.serialization import load_pem_private_key
    except ImportError as exc:
        raise RuntimeError("AppKey signing needs the cryptography package: pip install -r requirements-moomoo.txt") from exc
    return load_pem_private_key(pem, password=None)


def _bars(session, symbol, start, end_inclusive):
    """All forward-adjusted daily bars in [start, end_inclusive].

    Pages backwards from the end date. Continues while the vendor reports more
    data or returns a full page, and stops if a page fails to move the window
    earlier, so a misbehaving backend cannot spin the loop.
    """
    rows = []
    end = end_inclusive
    for _ in range(MAX_PAGES):
        data = session.get(f"/api/v1.0/quote/{symbol}/history-kline",
                           {"start": start, "end": end, "ktype": KLINE_DAY, "autype": ADJUST_FORWARD, "num": PAGE})
        page = data.get("kline_list") or []
        pagination = data.get("pagination")
        has_more = bool(pagination.get("has_more")) if isinstance(pagination, dict) else False
        if not page:
            if has_more:
                raise RuntimeError(f"{symbol}: vendor returned an empty page while reporting more data")
            break
        rows.extend(page)
        if not has_more and len(page) < PAGE:
            break
        earliest = pd.Timestamp(str(min(int(r["date"]) for r in page)))
        if earliest <= pd.Timestamp(start):
            break
        next_end = str((earliest - pd.Timedelta(days=1)).date())
        if next_end >= end:
            raise RuntimeError(f"{symbol}: vendor paging did not advance (end {end} -> {next_end})")
        end = next_end
    else:
        raise RuntimeError(f"{symbol}: more than {MAX_PAGES} pages for one history window")
    if not rows:
        raise ValueError("Empty response")
    frame = pd.DataFrame(rows)
    frame["Date"] = pd.to_datetime(frame["date"].astype(int).astype(str), format="%Y%m%d")
    # No dedupe or clipping here: the engine audits duplicate or unexpected dates itself.
    return frame.set_index("Date").sort_index()


def history(session, ticker, start, end):
    """Daily bars for one ticker from start (inclusive) to end (exclusive).

    The exclusive end mirrors the engine's Yahoo call so the same date
    arithmetic serves both sources.
    """
    symbol = f"{MARKET}.{ticker}"
    end_inclusive = str((pd.Timestamp(end) - pd.Timedelta(days=1)).date())
    bars = _bars(session, symbol, start, end_inclusive)
    close = bars["close"].astype(float)
    out = pd.DataFrame({
        "Open": bars["open"].astype(float),
        "High": bars["high"].astype(float),
        "Low": bars["low"].astype(float),
        "Close": close,
        "Adj Close": close,
        # Volume is only range-checked downstream; vendor scaling is passed through as received.
        "Volume": bars["volume"].astype(float),
    }, index=bars.index)
    out.index.name = "Date"
    return out[PRICE_COLUMNS]
