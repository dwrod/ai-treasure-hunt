# Chapter 7 — building the research system

Public-release update: the first live run is documented in FIRST_LIVE_RUN.md. A public clone intentionally has no personal journal or Yahoo archive; its CSVs are created on its first run. The build-stage status below is historical. The runtime now uses src.release_integrity to verify shipped frozen methodology and any archive files present; strict original archive verification remains in src.frozen. See README.md for clean setup and src.build_watchlist for the separately generated educational watchlist.

Run from the project directory:

```powershell
python -m src.run_signal_engine
```

This is a research journal, not an automated trading system. No strategy was validated. V0/V1 failed to demonstrate a robust edge in the historical experiment. The purpose is to collect new out-of-sample evidence without changing the signals. Decision D remains in force. This document is operating guidance, not the deferred public README/START_HERE package.

## Installation and first-run status

The engine is installed and tested in this workspace. The production CSVs are initialized with headers; they are empty because no live scan has been run in this build stage. Empty templates do not mean there are zero current signals. The first live run is the next requested stage. Offline validation lives separately in output/engine_validation/ and must not be mistaken for a current scan.

For another Python 3.13 environment, install the pinned requirements once:

```powershell
python -m pip install -r requirements-engine.txt
```

This workspace uses an isolated .engine_dependencies/ directory for the calendar package and dependencies; the engine can also use a normally installed package. The existing frozen requirements.txt was not changed. The new exchange-calendars 4.13.2 dependency provides the XNYS session calendar, including holidays, early closes and UTC open/close timestamps. References: [package release](https://pypi.org/project/exchange_calendars/4.13.2/) and [calendar API](https://github.com/gerrymanoim/exchange_calendars/blob/master/exchange_calendars/exchange_calendar.py). This calendar dependency supplies operational dates, not an additional indicator or research parameter.

## Run behavior

Run after a completed market close and before the next session's open to record new signals prospectively. No code edits are required between days. Intraday/weekend runs use the most recent completed XNYS session; an incomplete daily bar is never scanned as a close signal. Eligibility is checked using the actual clock after downloading, so a slow run crossing the next open is labeled late.

Each run fetches all 50 fixed stocks plus SPY from Yahoo, retaining raw responses in a new output/signal_engine_runs/<run-id>/ snapshot. It requests the fixed March 2025 history origin through the selected completed session, preserving the frozen Wilder ATR seed convention rather than introducing a moving warm-up cutoff. This is intentionally simple full-history refresh, not a database or incremental-cache merge. The saved source responses and scan receive hashes and a run manifest with data quality and errors.

The original src.signals equations and src.data adjustment convention are reused unchanged. SMA10 and SMA20 include today's Close; the crossover uses strictly below yesterday and strictly above today. V1 adds ATR14/Close <= 0.80 times its prior-20-session maximum, excluding today. ATR values use the frozen Wilder seed and recurrence. No SMA200 rule, parameter search or V2 exists.

Missing or invalid bars are not filled. They are masked on the common calendar; indicators remain unavailable where their dependencies are incomplete and Wilder ATR restarts after gaps as in the frozen implementation. Only the already-authorized exact KO correction is reused when the matching original value is present; no new inferred repairs are made. Download failure or unavailable features produce an explicit status and blank flags, not a FALSE signal. Partial scans print a caution and return exit code 2; fatal integrity errors fail the command. Earlier gaps and vendor anomalies are recorded in the manifest even if current features have enough valid history to resume.

## Current outputs

- output/current_signal_scan.csv: one row per fixed stock, with target market date, latest received data date, Close, SMA10/SMA20, both prior-day SMAs, ATR14, ATR%, prior-20 maximum, contraction threshold, V0/V1 flags, frozen sector, status and run timestamp.
- output/current_signals_only.csv: only usable current V0 signals. V1 is always a subset, indicated by its flag. An empty completed scan here means no qualifying signals; inspect the all-stock scan for failures before drawing that conclusion.
- output/prospective_signal_journal.csv: the cumulative readable signal-and-outcome journal.

ATR% and return columns are fractions: 0.02 means 2%. The contraction threshold is 0.80 × prior20_max_ATR_pct, in the same fractional units. Prices and ATR use adjusted price units. Current CSVs are replaceable views of the latest run; archived snapshots and original journal signal events are retained.

## Immutable signals and append-only outcomes

The authoritative file is output/prospective_signal_events.jsonl. It is append-only and hash-chained. The requested journal CSV is a rebuildable projection of that ledger. SIGNAL events contain immutable signal-date features and their first recording timestamp, snapshot path, specification/code hashes and record class. Later ENTRY and COMPLETE events append only permitted fields; neither can rewrite a SIGNAL event. The CSV is atomically replaced to display those additions. Do not manually edit either file or delete the ledger; a nonempty journal with a missing ledger causes the engine to refuse a run.

IDs are market-date:ticker:version. A V1-qualified event produces a V0 row and a V1 row, so comparisons can select version directly. These are two memberships for one stock-date, not two independent observations. Repeated runs cannot duplicate those IDs or revise their original features, even if Yahoo subsequently changes its history or the signal disappears from a refreshed scan.

PROSPECTIVE requires all of the following: live acquisition, a market date after the already-observed September 8, 2026 boundary, and registration after that session's close but strictly before the hypothetical next open. Anything recorded late is RETROSPECTIVE. Offline replays are always RETROSPECTIVE and cannot write into the default production output directory. The command scans only its selected latest completed date; it does not silently fill in skipped signal dates. Missing a run can therefore mean missing prospective evidence, which must not later be repaired by calling a backfill prospective.

An ENTRY event records the next-session Open for the stock and SPY once the completed daily bar is available. The engine deliberately waits until that session's close to ingest its daily Open. This conservative data-availability delay does not change the hypothetical execution price or date. Returns remain blank and status PENDING until the exit daily bar and both stock/SPY endpoints exist.

For signal session t, entry is O(t+1) and exit is O(t+11): exactly ten open-to-open trading intervals. COMPLETE records stock_return = stock_exit/stock_entry − 1, the identical SPY return, and excess_return = stock_return − spy_return. Missing endpoints remain PENDING with source issues visible in run manifests; they are not assigned zero returns.

Dividend adjustments can revise historical adjusted Open levels between entry observation and maturity. The originally observed entry_price and spy_entry_price therefore remain unchanged, while valuation_entry_price and valuation_spy_entry_price record the entry values from the SAME maturity snapshot as the exit values used for returns. This preserves the frozen adjusted-price methodology without mixing two adjustment scales. It also makes revisions visible instead of silently overwriting the observed entry. Once COMPLETE, the outcome is not recalculated or rewritten on later refreshes. Any future correction process requires an explicit separately documented amendment.

## Reproducibility and operational limits

Snapshots make each recorded calculation auditable; a fresh Yahoo fetch may differ because vendor history can be revised. Re-running the same inputs and clock is deterministic for feature and membership values, while run IDs and physical snapshot paths are intentionally unique. A directory lock prevents concurrent journal writers. Interrupted writes, a leftover lock or hash mismatch require inspection; never bypass an integrity failure by deleting research history. Keep backups of the ledger and referenced snapshots. The hash chain detects accidental modification, but is not external timestamp notarization or protection against someone rewriting the entire chain.

This is a manual command, not a scheduler. There are no orders, broker connections, trades or performance-promotion rules. It relies on the machine's clock, network/Yahoo availability and the pinned exchange calendar; unexpected closures, vendor corrections or a stale calendar can require operational maintenance. Such maintenance must preserve signal rules and archived records. Full-history acquisition grows over time. No live-network scan was performed during this build, so operational behavior on the next live run remains to be checked.

The engine implements evidence collection, not a statistical validation plan. Review dates, sample/precision targets, dependence-aware inference, realistic costs and criteria for promotion still require prospective registration before performance-based decisions. Signal logging alone cannot validate an edge.

## Verification

```powershell
python -m unittest analysis.test_signal_engine
python -m unittest discover -s tests
```

New tests cover duplicate prevention, immutable features despite revisions, pending outcomes staying pending, append-only completion, preservation of original entry under adjustment changes, no skipped-day backfill, prospective/retrospective boundaries, rejection of feature rewrites, V1 subset, missing latest data, calendar agreement with the frozen period and command replay reproducibility. Existing frozen tests also pass.

Optional offline verification, explicitly separate from production:

```powershell
python -m src.run_signal_engine --fixture-dir data/snapshot_2026-09-08/vendor --output-dir output/engine_validation --now 2026-09-08T22:00Z
```

The --now clock override is forbidden in live mode. No historical replay is fresh out-of-sample evidence.


## Public packaging boundary — current instructions

**ORIGINAL HISTORICAL EXPERIMENT:** Published research conclusions and V0/V1 results describe the original frozen experiment. Original sectors were retrieved through Yahoo/yfinance. A KO anomaly was quarantined, mechanically investigated and corrected before the backtest. The underlying Yahoo values, static sector table, correction file and original archives are not distributed.

**PUBLIC REPRODUCTION:** Run the unchanged SMA/ATR formulas, universe, adjustment rules and timing on newly retrieved Yahoo data. Current sector labels are optionally retrieved at runtime from Yahoo/yfinance, kept only in ignored local outputs, and may differ from historical labels. Missing sectors are UNAVAILABLE and never block signals. No official GICS assignments or substitute classifications are supplied. Invalid bars are quarantined and reported; the public engine never applies the private historical correction. Exact byte-for-byte historical reproduction is not promised.

The public export preserves the historical specification's formulas and settings but explicitly omits its vendor price literals. PUBLIC_RUNTIME_LOCK.json records public file hashes and these documentary exceptions; FROZEN_LOCK.json remains the original historical record, not a claim that omitted data is shipped. The private archive-specific freeze test is excluded; public settings, formula, quarantine, sector-failure and journal tests remain available.

Use `python -m unittest discover -s tests` and `python -m unittest analysis.test_signal_engine analysis.test_release_integrity analysis.test_public_runtime` for public checks. Historical evaluators and report writers require private evidence and are retained for inspection, not turnkey historical reconstruction.

## Price source (fork addition)

`--source moomoo` reads forward-adjusted daily bars from the moomoo Open API instead of Yahoo; formulas, timing and journal rules are unchanged. SIGNAL events written by this version carry `price_source` and ENTRY events carry `entry_price_source` (the one additional permitted ENTRY field); the run manifest carries `price_source` and, for moomoo runs, the adapter's hash. Records written earlier show these columns blank in the journal CSV and were Yahoo. See MOOMOO_ADAPTER.md.
