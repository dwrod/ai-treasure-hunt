# AI Treasure Hunt

**Final owner authorization:** Visser Labs LLC confirmed ownership/licensing authority and approved MIT for original code/documentation, Copyright (c) 2026 Visser Labs LLC, and publication of this reviewed export at visser-labs/ai-treasure-hunt. See [LICENSE](LICENSE). Third-party software and data retain separate rights. Earlier pending-approval passages below are historical preparation records.


CURIOSITY → OPEN SOURCE → EXPERIMENT → FAIL → LEARN → ADAPT → BUILD

**“Don’t copy my treasure hunt. Start your own.”**

A transparent AI research laboratory: start with a question, test it, preserve failures, and build a repeatable research system. This stock experiment is a worked example for investigating your own questions.

> **No version has demonstrated a robust trading edge.** V0 and V1 are research signals, not investment recommendations. Our decision was to stop modifying the historical model, not to keep searching until a backtest looked profitable.

Want to investigate your own idea? Open [**Socrates Mode**](SOCRATES_MODE.md) and tell your AI: **“Use SOCRATES_MODE.md and interview me before building anything.”** It asks one question at a time, produces a TREASURE HUNT BRIEF, and waits for your approval before implementation. It is a conversation instruction, not an installed agent.

New here? Start with [START_HERE.md](START_HERE.md). Want the evidence? Read [the decision](RESEARCH_DECISION.md), [prompt history](PROMPTS.md) and [research log](RESEARCH_LOG.md).

## Why this project exists

Curiosity can become a disciplined investigation. We used Codex to help turn a broad idea into explicit rules, working code, tests and an honest research record. We looked for established building blocks rather than reinventing the wheel, then challenged our own additions.

The goal is empowerment and agency: learning to ask, build, inspect and revise your understanding. Failure is useful when it prevents an unjustified conclusion. The goal is to learn how to investigate ideas, not to copy this trading signal.

## The research question

Can a bullish moving-average crossover produce better subsequent ten-trading-day relative outcomes when preceded by meaningful ATR contraction?

We compared a simple crossover with the same crossover restricted to dates when recent volatility had contracted. Each signal was known after the close, with hypothetical entry at the next open and exit ten trading intervals later. SPY was measured over exactly the same dates.

## What came from GitHub

V0's conceptual origin is [kernc/backtesting.py](https://github.com/kernc/backtesting.py), specifically its [SMA crossover Quick Start](https://github.com/kernc/backtesting.py/blob/master/doc/examples/Quick%20Start%20User%20Guide.py) and [crossover helper](https://github.com/kernc/backtesting.py/blob/master/backtesting/lib.py). We independently implemented the documented mathematical concept in pandas. We did not import the backtesting framework or copy its strategy source.

V0 is SMA10 strictly below SMA20 yesterday and strictly above SMA20 today. Equality does not count. The periods were selected before performance review, not optimized. GitHub popularity was treated as software adoption, not evidence of alpha. The original AI momentum recommendation and the human override selecting crossover remain in the log.

Public runs retrieve optional current sector metadata and quarantine invalid prices without replaying historical corrections. See the public packaging boundary below.

The upstream project is AGPL-3.0; copying its implementation would require a fresh compliance review. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for attribution and dependency licenses. Original project code and documentation are released under [MIT](LICENSE).

## What we added

V1 was the human researcher's preregistered hypothesis: a crossover might carry more information after volatility contracts.

- ATR% = Wilder ATR14 / Close.
- Contraction = today's ATR% <= 0.80 × the maximum ATR% over the prior 20 trading sessions, excluding today.
- V1 = V0 AND contraction on the same signal date.

The exact seed, adjustment and timing formulas are in [FROZEN_SPECIFICATION.md](FROZEN_SPECIFICATION.md). ATR is not a direction forecast. A declining ratio can also reflect an old volatility peak or rising price.

## What happened

One observed evaluation year: September 8, 2025 through September 8, 2026; only complete outcomes included. Excess returns below are percentage points, equally weighted per stock-signal, not portfolio returns.

| Result | V0 | V1 |
| --- | ---: | ---: |
| Completed signals | 332 | 57 |
| Mean excess return | −0.389 pp | +0.355 pp |
| Median excess return | −0.260 pp | −0.456 pp |
| Hit rate versus SPY | 48.49% | 47.37% |

The first-pass classification was **MIXED**. V1 improved the mean but worsened median and hit rate, removing 82.83% of completed signals. Robustness classification: **FRAGILE**. Removing its single best event reduced its mean to −0.154 pp; removing its best three reduced it to −0.771 pp. Stock and sector concentration failed checks.

The human then proposed long-term trend alignment. Above a rising SMA200, 33 V1 events averaged −0.463 pp with a 45.45% hit rate; four of the five worst losses occurred there. Classification: **WEAK RATIONALE**. We did not create V2.

**Decision D: do not promote a strategy; retain V0/V1 as research signals.** Next-close execution and ATR-mechanism checks did not support every skeptical explanation; those findings are preserved too.

Read [first-pass results](FIRST_PASS_RESULTS.md), [robustness](ROBUSTNESS_REPORT.md), [trend diagnostic](LONG_TERM_TREND_DIAGNOSTIC.md) and [the decision gate](RESEARCH_DECISION.md). The [first live run](FIRST_LIVE_RUN.md) used September 8, 2026 data: its five version-level records were retrospective because that date was already observed. Live acquisition alone is not out-of-sample evidence.

## What we built

A command-line research engine that fetches Yahoo data, validates it, calculates frozen features for 50 stocks and records current signals. It produces:

- `output/current_signal_scan.csv`: all stocks, features and quality status.
- `output/current_signals_only.csv`: active signals.
- `output/prospective_signal_journal.csv`: original features plus later entry/outcome fields.
- `output/prospective_signal_events.jsonl`: authoritative append-only journal.
- `output/current_watchlist_top10.csv`: optional monitoring view, generated separately below.

The watchlist orders V1 first, V0-only next, then stocks closest from below to a crossover. Near rows are **NEAR SIGNAL — NOT ACTIVE**, never journal signals. No ranking model is invented. Journal outcomes are appended only after maturity; late or historical records are labeled retrospective. There are no broker connections, orders or automatic trades; reading prices from a broker's data API with a read-only token is a data source, not a broker connection.

## How to run it

Install Python 3.13 and download/clone this folder. Open a terminal in the folder containing this README.

Windows PowerShell (activation is unnecessary):

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-engine.txt
.\.venv\Scripts\python.exe -m src.release_integrity
.\.venv\Scripts\python.exe -m src.run_signal_engine
.\.venv\Scripts\python.exe -m src.build_watchlist
```

macOS/Linux:

```sh
python3.13 -m venv .venv
.venv/bin/python -m pip install -r requirements-engine.txt
.venv/bin/python -m src.release_integrity
.venv/bin/python -m src.run_signal_engine
.venv/bin/python -m src.build_watchlist
```

Inside an activated environment the daily command is simply `python -m src.run_signal_engine`. Internet access is required; Yahoo availability/rate limits can interrupt runs. No API key or Codex subscription is required by this Python engine. Codex is optional assistance for understanding and development.

Run after the market close and before the next open to record prospective signals. Check market date and data_status; unavailable flags are not FALSE. Do not erase the journal to recover from an error. Read [SIGNAL_ENGINE.md](SIGNAL_ENGINE.md) for timing, adjustments, partial downloads, snapshots and recovery limits.

Offline checks, with the same environment's Python:

```sh
python -m unittest discover -s tests
python -m unittest analysis.test_signal_engine analysis.test_release_integrity
```

Original Yahoo archives and personal journals are deliberately excluded. Archive-dependent tests skip in a public checkout. The public runtime verifies shipped methodology and public documentary hashes; missing private archives and references do not prevent new scans. Exact reproduction of the published historical numbers requires the original snapshot: fresh Yahoo downloads may have revisions. The historical evaluators are retained for inspection but are archive-dependent and are not a one-command reconstruction promise. Optional historical chart dependencies are in `requirements-research.txt`.

### Optional: moomoo as the price source

This fork can read daily bars from the moomoo Open API instead of Yahoo. It is a price source only: the frozen formulas, universe and timing rules are unchanged, the journal gains two provenance columns recording which source priced each record, and there are still no orders or broker connections.

```sh
.venv/bin/python -m pip install -r requirements-moomoo.txt
.venv/bin/python -m src.moomoo_login
.venv/bin/python -m src.run_signal_engine --source moomoo
```

The login command opens moomoo's own page in your browser. Approve a grant that includes quote read; Moomoo may add account context or other scopes, which the engine accepts, while the engine itself calls only quote endpoints. The engine keeps its token refreshed and never asks for a password in the terminal. Read [MOOMOO_ADAPTER.md](MOOMOO_ADAPTER.md) for how the adapter works, the credential options for servers, and the check against the first live run. [AGENTS.md](AGENTS.md) tells Codex or Claude Code the same things.

## Important limitations

Fixed hand-selected universe; one recent year; overlapping outcomes; retrospective vendor revisions; static sectors; one documented KO correction; idealized adjusted opening prices without realistic costs, sizing or portfolio construction. Fifty-seven V1 events are not 57 independent trials. This year has already been examined. Future signal logging still needs a prespecified evaluation/inference plan before any promotion decision. **Educational research only; no validated edge.**

## Project structure

| File/folder | Purpose |
| --- | --- |
| RESEARCH_CONSTITUTION.md | Rules for honest inquiry |
| PROMPTS.md / RESEARCH_LOG.md | Chronological instructions, decisions and failures |
| FROZEN_SPECIFICATION.md / FROZEN_LOCK.json | Exact historical definitions and integrity record |
| src/ | Frozen equations, data handling and current engine |
| tests/ / analysis/test_*.py | Synthetic and optional archive-dependent checks |
| analysis/ | Original evaluators, diagnostics and report writers |
| reference/ | Historical private references are excluded from the public export |
| data/ / output/ | Local, ignored data, snapshots and personal journals |
| SOCRATES_MODE.md | One-question-at-a-time interview, research brief and approval gate |
| MOOMOO_ADAPTER.md | Optional moomoo price source: design, login, limits and acceptance check |
| src/data_moomoo.py / src/moomoo_login.py | The moomoo adapter and its browser login |
| AGENTS.md / CLAUDE.md | Instructions for Codex and Claude Code: commands, moomoo login, what never to do |
| THIRD_PARTY_NOTICES.md | Concept provenance and dependency licensing |
| PUBLIC_RELEASE_AUDIT.md | Release checks and remaining publication decisions |

## Start your own treasure hunt

Read [START_HERE.md](START_HERE.md), inspect [PROMPTS.md](PROMPTS.md), and use [SOCRATES_MODE.md](SOCRATES_MODE.md) to discover a question of your own before writing code.

**“Don’t copy my treasure hunt. Start your own.”**

Preserve this experiment as a reference. Define a different question, information timing and failure criteria before building a separate experiment; do not rewrite these frozen records to improve their results.


## Public packaging boundary — current instructions

**ORIGINAL HISTORICAL EXPERIMENT:** Published research conclusions and V0/V1 results describe the original frozen experiment. Original sectors were retrieved through Yahoo/yfinance. A KO anomaly was quarantined, mechanically investigated and corrected before the backtest. The underlying Yahoo values, static sector table, correction file and original archives are not distributed.

**PUBLIC REPRODUCTION:** Run the unchanged SMA/ATR formulas, universe, adjustment rules and timing on newly retrieved Yahoo data. Current sector labels are optionally retrieved at runtime from Yahoo/yfinance, kept only in ignored local outputs, and may differ from historical labels. Missing sectors are UNAVAILABLE and never block signals. No official GICS assignments or substitute classifications are supplied. Invalid bars are quarantined and reported; the public engine never applies the private historical correction. Exact byte-for-byte historical reproduction is not promised.

The public export preserves the historical specification's formulas and settings but explicitly omits its vendor price literals. PUBLIC_RUNTIME_LOCK.json records public file hashes and these documentary exceptions; FROZEN_LOCK.json remains the original historical record, not a claim that omitted data is shipped. The private archive-specific freeze test is excluded; public settings, formula, quarantine, sector-failure and journal tests remain available.

Use `python -m unittest discover -s tests` and `python -m unittest analysis.test_signal_engine analysis.test_release_integrity analysis.test_public_runtime` for public checks. Historical evaluators and report writers require private evidence and are retained for inspection, not turnkey historical reconstruction.

Yahoo Finance was used for THIS experiment. Other questions may require different data, APIs, open-source tools, benchmarks, universes and methodologies.
