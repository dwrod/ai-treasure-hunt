# moomoo price source — light-touch adapter

This fork adds one optional price source to the signal engine. The frozen formulas,
universe, timing rules, journal mechanics and prompts are unchanged; the journal gains two
provenance fields described below. The engine still defaults to Yahoo; moomoo is opt-in per run.

```sh
python -m src.run_signal_engine --source moomoo
```

## What changed

| File | Change |
| --- | --- |
| `src/data_moomoo.py` | New. Fetches forward-adjusted daily bars from the moomoo Open API and returns the same frame shape the Yahoo path returns. |
| `src/moomoo_login.py` | New. Browser login (OAuth 2.1 with PKCE; `quote:read` required, broader Moomoo grants accepted) that stores a token for the engine; the same consent page the MCP clients use. |
| `src/run_signal_engine.py` | A `--source {yahoo,moomoo}` flag; credentials checked before any run artifact is created; one dispatch branch in the download loop; `price_source` recorded in the run manifest, on every new SIGNAL event and every new ENTRY event; the adapter's hash recorded in the manifest of moomoo runs. |
| `README.md`, `START_HERE.md`, `SIGNAL_ENGINE.md`, `RESEARCH_LOG.md` | A short optional-moomoo section, a clarified broker sentence, an operating note, and a dated log entry. |
| `PUBLIC_RUNTIME_LOCK.json` | Hashes refreshed for the five edited files above. The adapter and login helper are deliberately not locked, like the Yahoo client; the adapter's hash is evidence in each moomoo run manifest, not a gate. `FROZEN_LOCK.json` is unchanged. |
| `AGENTS.md`, `CLAUDE.md` | New. Tell Codex and Claude Code how to run the engine, how to connect the user's moomoo account, and what never to do. |
| `tests/test_data_moomoo.py`, `tests/test_moomoo_login.py` | Adapter, paging, HTTP-layer and login tests with fakes; no network. Signing tests skip when `cryptography` is absent. |
| `requirements-moomoo.txt` | Engine requirements plus `cryptography` for AppKey signing. |

`src/data.py`, `src/signals.py`, `src/config.py`, `src/pipeline.py`, `src/frozen.py` and the
historical evaluators and result documents are byte-identical to the upstream public export.

## Where the data comes from

The adapter talks to the hosted REST surface at `webapi.moomoo.com`, the same backend the
moomoo MCP server exposes to Claude Code, Cursor and Codex. There is no local gateway to
install and no SDK. Per symbol it makes one request for forward-adjusted daily bars over the
engine's fixed history window and returns `Open, High, Low, Close, Adj Close, Volume` with
`Adj Close` equal to `Close`. The engine's own `adjust_ohlc` then applies a factor of one, so
the adjusted series it computes is the vendor's returned forward-adjusted series unchanged.
The production history endpoint currently accepts only adjustment modes 0–2; the adapter uses
mode 1 (forward adjustment excluding cash dividends). Snapshot CSVs from this source therefore
hold forward-adjusted prices, not raw prints; the manifest's `price_source` says which source
produced each snapshot. This adjustment convention differs from Yahoo's dividend-inclusive
`Adj Close`, so do not mix the sources in a journal unless that difference is deliberate.

Requests page backwards from the end date. The loop continues while the vendor reports more
data or returns a full page, stops when a page fails to move the window earlier, treats an
empty page that still claims more data as an error, and refuses more than twelve pages for
one window. Rate-limit and server-error responses, and transport errors, are retried with
bounded back-off honouring `Retry-After` in either seconds or HTTP-date form, up to sixty
seconds per request. Vendor errors and anomalies are passed through, never repaired:
duplicate or unexpected session dates reach the engine's own audit and quarantine logic,
exactly as Yahoo frames do. Optional Yahoo sector labels are fetched on every live run
regardless of price source, as before.

## Connecting your moomoo account

Two things can connect to moomoo, and they are separate:

1. **Your coding agent.** Claude Code, Cursor or Codex connect to the moomoo MCP server with one
   command (`claude mcp add moomoo-mcp --transport http https://mcp.moomoo.com/mcp`, or the
   equivalent config block plus `codex mcp login`), then open a browser for you to log in. That
   gives the agent quotes, history, the paper account and order drafting in natural language.
   The repository needs nothing for this.
2. **The engine.** The Python run needs its own token. Log in once in the browser:

   ```sh
   python -m src.moomoo_login
   ```

   It binds a local callback port first, then opens the same moomoo consent page. The consent
   page determines the grant: `quote:read` is required, while broader scopes and Moomoo's
   account-context marker are accepted. The engine itself still calls only quote endpoints.
   The token lives under `.cache/moomoo/` (ignored by git, owner-only from the moment it is
   created) and refreshes itself; if a refresh ever fails, the run stops calling moomoo and
   tells you to log in again. If the default port is busy, pass `--port 0`. No password is
   typed into the terminal, ever.

For servers or scheduled jobs, environment variables take precedence over the stored login:

- `MOOMOO_ACCESS_TOKEN` — an OAuth bearer token (scope `quote:read` is sufficient).
- `MOOMOO_API_KEY` and `MOOMOO_PRIVATE_KEY_FILE` — an AppKey id and the path to the PEM
  private key registered at `open.moomoo.com/dashboard` (Ed25519 or RSA-SHA256). Requests are
  signed per the Open API "Traditional API Key" specification.

The engine makes one cheap authenticated call before creating the run directory, so a missing,
malformed or expired credential fails once, up front, with a clear message and no orphaned run.

## Provenance and mixed sources

Every SIGNAL event written by this version carries `price_source`, every ENTRY event carries
`entry_price_source`, and every run manifest carries `price_source`. Records written before
this version show a blank in those columns of the journal CSV; they were Yahoo. A replay from
`--fixture-dir` records `fixture:<source>`, so pass `--source moomoo` when the fixture holds
moomoo bars. Keep one source for a journal unless the mix is deliberate: the two vendors apply
dividend adjustments on slightly different days, which shows up as a level shift between
`entry_price` and `valuation_entry_price`.

## Acceptance check against the first live run

The published `FIRST_LIVE_RUN.md` records the September 8, 2026 scan from Yahoo. The same scan
was replayed offline (`--fixture-dir … --now 2026-09-08T22:00Z`) on moomoo forward-adjusted
bars and on Yahoo bars fetched the same day, September 14, for GS, UNH, NVDA, MS and SPY.

- Signal membership matches the first live run exactly: V0 = NVDA, GS, UNH; V1 = GS, UNH;
  MS not a signal.
- GS, NVDA and MS features agree between moomoo and Yahoo to within about 1e-8 relative on
  closes and moving averages and within about 1e-4 on ATR-based values.
- UNH shows a uniform 0.6 percent level shift on moomoo because UNH went ex-dividend on
  September 14 and moomoo had already applied the adjustment when Yahoo had not. Ratios
  such as ATR percent agree to within 1e-4, so the signal flags are identical. This is the
  vendor-revision effect the engine already documents, not a data disagreement.
- GS ATR percent is 0.024381 on both vendors today versus 0.024378 in the first live run; both
  sources moved together, so this is a small post-run revision in the shared history.

The replay used the dividend-inclusive forward-adjusted bars available during the
acceptance work. Production now accepts only modes 0–2, so it cannot be treated as a
like-for-like replay until its dividend-inclusive modes are restored. A full 51-name live
run through `--source moomoo` needs a login and has not been executed yet.

## Maintaining the public lock

Editing a file listed in `PUBLIC_RUNTIME_LOCK.json` requires refreshing its hash in the same
change, or the engine refuses to run. The file is CRLF; this keeps it that way:

```sh
python - <<'EOF'
import json, hashlib
p='PUBLIC_RUNTIME_LOCK.json'; d=json.loads(open(p,'rb').read())
d['sha256']={k:hashlib.sha256(open(k,'rb').read()).hexdigest() for k in d['sha256']}
open(p,'wb').write((json.dumps(d,indent=2).replace('\n','\r\n')+'\r\n').encode())
EOF
python -m src.release_integrity
```

Files in `FROZEN_LOCK.json` are the historical record and are never edited.

## Limits worth knowing

- Historical candlestick quota is per symbol on a rolling seven days and depends on account
  tier. The 51-symbol universe fits the base tier; confirm before running a larger universe.
- Volume is passed through as received; the engine only range-checks it and the signal
  formulas never read it.
- Replayed runs are always retrospective, as before. Prospective records require a live run
  after the close and before the next open, exactly as `SIGNAL_ENGINE.md` describes.
- The documented test command works from `requirements-engine.txt` alone; the two signing
  tests are skipped unless `cryptography` from `requirements-moomoo.txt` is installed.
