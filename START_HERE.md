# Start here — no programming background required

**Final owner authorization:** Visser Labs LLC confirmed ownership/licensing authority and approved MIT for original code/documentation, Copyright (c) 2026 Visser Labs LLC, and publication of this reviewed export at visser-labs/ai-treasure-hunt. See [LICENSE](LICENSE). Third-party software and data retain separate rights. Earlier pending-approval passages below are historical preparation records.


## What this is

A repository is a project folder with files and a history of changes. GitHub is a place to share those folders. This one documents an investment research idea that did not earn promotion to a trading strategy. It includes the failures, not just the code.

Python runs the calculations. Codex or another AI coding environment can help explain and edit files. You can read the research without installing either.

## What you can do with it

Read the conclusion, follow the human/AI conversation through PROMPTS.md, inspect the rules, run a research scan, or use the structure for another question. It does not tell you what to buy. Start with [README.md](README.md) and [RESEARCH_DECISION.md](RESEARCH_DECISION.md).

## Clone or download

On the published GitHub page, select **Code → Download ZIP**, unzip it, and open the extracted folder. This is the simplest route without Git.

If you already use Git, copy the repository's HTTPS address from its Code menu and run `git clone` followed by that address. No repository address is invented here: the owner must first publish the project and share its URL. Keep your own copy and personal output files private unless you deliberately review them for sharing.

## Open the folder in an AI coding environment

Open your coding tool and select the downloaded project folder—the one containing README.md. For Codex setup and sign-in, follow the [official quickstart](https://developers.openai.com/codex/quickstart); interfaces and account requirements can change. You do not need to configure an OpenAI API key to run this repository's engine. Do not paste private credentials into a prompt or commit them to GitHub.

## Your first instruction

**“Use SOCRATES_MODE.md and interview me before building anything.”**

The interview identifies your curiosity, required data and existing open-source building blocks, asks what could prove the hypothesis wrong, and creates a TREASURE HUNT BRIEF. It asks one question at a time and stops for your approval before implementation.

## Ask the AI to explain first

Try this instruction:

> Read README.md, RESEARCH_CONSTITUTION.md and RESEARCH_DECISION.md. Explain the question, what failed and how the files fit together as if I have never programmed. Do not change files, run downloads or suggest trades. Show me the exact command before helping me run it.

Then ask it to explain SMA, ATR, information timing and the difference between a signal and evidence for an edge. Verify its answers against the specification.

## Discover your own question with Socrates Mode

You do not have to run the stock signal to use this laboratory. After downloading the folder and opening it in your AI coding environment:

1. Open [SOCRATES_MODE.md](SOCRATES_MODE.md).
2. Tell the AI: **“Use SOCRATES_MODE.md and interview me before building anything.”** If it cannot read the file, copy the complete instruction block into your conversation.
3. Answer one question at a time. Say when something is unclear or you do not know yet.
4. Review the **TREASURE HUNT BRIEF**: the question, smallest experiment, data needs, possible traps and evidence that would count against the idea.
5. Approve the brief before implementation, or ask for a revision. Approval covers the agreed first experiment only; it does not authorize trading or changing this frozen project.

Socrates Mode is a prompt you use with your AI, not a program to install. You can explore finance, a business process or something outside finance. No code or download should begin during the interview.

## Run the existing system

Install Python 3.13. Open a terminal in this project folder and use the Windows or macOS/Linux commands in [README.md](README.md). A terminal is a window where you enter commands; a virtual environment is an isolated set of Python packages for this project. You can ask the AI to guide you through each command and explain errors.

The engine downloads market data and writes CSV files in output/. A CSV is a plain table you can open in a spreadsheet app. Start with current_signal_scan.csv, checking dates and data_status, then current_signals_only.csv. Run the separate watchlist command if wanted. Read [SIGNAL_ENGINE.md](SIGNAL_ENGINE.md) before relying on journal labels. A missing result is not a failed trade, and a near signal is not active.

Do not delete a journal because the results disappoint. Do not connect the engine to a broker for orders; reading prices from moomoo is a data source, not a broker connection (see [MOOMOO_ADAPTER.md](MOOMOO_ADAPTER.md)). This is an educational research record, not a validated system for live trading.

## Change the question, rather than copy the signal

Keep this frozen project as an untouched reference. In a separate experiment, explain your curiosity in plain English, choose a target and benchmark, establish what was knowable at the time, and define what would count against your idea before testing.

This stock experiment uses Yahoo Finance because it fits THIS question. The laboratory is not limited conceptually to Yahoo Finance. A different question may require different data, APIs, open-source tools, benchmarks, universes and methodologies; the current Python engine remains specific to the frozen stock experiment.

Possible questions involve ETFs, mutual funds, different stock universes or horizons, earnings revisions, crypto, or risk analysis. These are separate designs, not suggestions to search this sample for a winning combination. Mutual funds may not have exchange opening prices; crypto trades on a different calendar; earnings revisions need point-in-time publication data. Reconsider the data and timing before reusing code.

Ask: “Help me define a falsifiable question about my chosen topic. Do not select indicators or optimize yet.” See the preserved examples in [PROMPTS.md](PROMPTS.md). [Socrates Mode](SOCRATES_MODE.md) guides that interview and stops for approval of your research brief.

**“Don’t copy my treasure hunt. Start your own.”**

Original project reuse is licensed under MIT; see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).


## Public packaging boundary — current instructions

**ORIGINAL HISTORICAL EXPERIMENT:** Published research conclusions and V0/V1 results describe the original frozen experiment. Original sectors were retrieved through Yahoo/yfinance. A KO anomaly was quarantined, mechanically investigated and corrected before the backtest. The underlying Yahoo values, static sector table, correction file and original archives are not distributed.

**PUBLIC REPRODUCTION:** Run the unchanged SMA/ATR formulas, universe, adjustment rules and timing on newly retrieved Yahoo data. Current sector labels are optionally retrieved at runtime from Yahoo/yfinance, kept only in ignored local outputs, and may differ from historical labels. Missing sectors are UNAVAILABLE and never block signals. No official GICS assignments or substitute classifications are supplied. Invalid bars are quarantined and reported; the public engine never applies the private historical correction. Exact byte-for-byte historical reproduction is not promised.

The public export preserves the historical specification's formulas and settings but explicitly omits its vendor price literals. PUBLIC_RUNTIME_LOCK.json records public file hashes and these documentary exceptions; FROZEN_LOCK.json remains the original historical record, not a claim that omitted data is shipped. The private archive-specific freeze test is excluded; public settings, formula, quarantine, sector-failure and journal tests remain available.

Use `python -m unittest discover -s tests` and `python -m unittest analysis.test_signal_engine analysis.test_release_integrity analysis.test_public_runtime` for public checks. Historical evaluators and report writers require private evidence and are retained for inspection, not turnkey historical reconstruction.
