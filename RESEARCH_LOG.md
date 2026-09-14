# Research log

## Reader guide — added during public preparation

This is a chronological laboratory record. Early provisional choices are not the final rules; later decisions supersede them without erasing history. For the executable definitions use FROZEN_SPECIFICATION.md; for the final interpretation use RESEARCH_DECISION.md.

- [Initial specification](#2026-09-08--stage-1-initial-research-specification-version-01)
- [GitHub concepts](#2026-09-08--github-treasure-hunt-source-review-and-timing-decision)
- [Human override and baseline](#2026-09-08--v0-specification-and-human-directed-v1-hypothesis)
- [Preregistration](#2026-09-08--preregistration-frozen-v0-and-human-origin-v1)
- [Full first-pass report](FIRST_PASS_RESULTS.md)
- [Robustness and failures](ROBUSTNESS_REPORT.md)
- [Long-term-trend diagnostic](LONG_TERM_TREND_DIAGNOSTIC.md)
- [Decision D](RESEARCH_DECISION.md)
- [Engine operating guide](SIGNAL_ENGINE.md) and [first live run](FIRST_LIVE_RUN.md)
- [Prompt chronology](PROMPTS.md) and [public release audit](PUBLIC_RELEASE_AUDIT.md)

All detailed original entries remain below. Files under data/ and output/ referenced by historical entries are local artifacts deliberately excluded from the public distribution; reports preserve the findings, but this does not promise exact archive reconstruction from fresh vendor downloads.


## 2026-09-08 — Stage 1: initial research specification, version 0.1

Status: specification drafted; provisional choices below await the user's review. No market data has been acquired, no ranking hypothesis selected, and no results produced. This entry defines an experiment, not an investment recommendation.

### 1. Exact research question

Within a user-supplied, fixed universe of approximately 50 liquid U.S. stocks, does a simple, economically explainable ranking rule, specified before examining its evaluation results and using only information available after each signal day's close, order stocks by their subsequent 10-trading-day returns relative to SPY during the most recent 12-month evaluation window?

The rule itself is deliberately unspecified. The question is conditional on this universe and period; it does not establish that the rule generalizes to all stocks or market conditions.

### 2. Prediction target, benchmark, and clock

**User-set:** SPY is the benchmark; the horizon is 10 trading days; output is a daily ranking.

**Provisional timing:** Generate the ranking after the regular U.S. trading session closes on signal day t, once that day's required data is available. The earliest assumed entry is the next trading session's open, t+1. Measure the return through the open of t+11: exactly 10 open-to-open trading intervals. For example, an entry at one Monday's open exits at the open two Mondays later when no exchange holidays intervene. Use an exchange-session calendar, not calendar-day arithmetic.

No same-close execution is assumed. If required inputs were not available before the next open, that date cannot be presented as an actionable next-open ranking. An opening print is a measurement convention, not a guarantee of an obtainable execution price.

For stock i, define its forward simple return as its consistently adjusted exit-open price divided by its adjusted entry-open price, minus one. Compute SPY's return over the identical interval. The prediction target is:

**Stock excess return = stock forward return − SPY forward return**, expressed in percentage points.

Positive excess return means outperformance, even if both assets lost money. This arithmetic difference is not a return ratio or a risk-adjusted alpha estimate. Because SPY's return is common to every stock on a given date, ranking stocks by excess return produces the same within-date order as ranking by their raw returns. SPY still matters for the magnitude and frequency of outperformance.

**Provisional return convention:** Use split- and dividend-adjusted prices as a total-return proxy for both stocks and SPY. Validate the vendor's adjustment behavior, especially for opening prices and corporate actions, before implementation. If the data cannot support this convention faithfully, record the limitation and ask for a methodology decision. Do not silently substitute raw prices. Future outcomes and later corporate actions may inform realized labels; they must not leak into historical ranking inputs.

**Decision required later:** Accept or revise the timing and return conventions before any backtest. Rank direction will be highest expected excess return first; score units and construction remain undefined.

### 3. Universe assumptions

- The user will provide approximately 50 ticker symbols before data acquisition. No symbols are selected now.
- Provisionally interpret the universe as U.S.-listed common stocks, excluding SPY, with one fixed list throughout evaluation. Confirm share-class and security-type exceptions with the supplied list.
- Treat liquidity as a property of the supplied list; do not invent or optimize a historical liquidity filter. Document how and when the list was chosen.
- A list chosen today can embed survivorship and hindsight selection. Historical results will describe that selected list, not a contemporaneously investable broad-market universe.
- Confirm ticker changes, listing dates, mergers, delistings, and duplicate share classes during the data audit. Do not replace a failed company with a survivor or drop it because its outcome is inconvenient.
- A stock is eligible for ranking only when the inputs required by the eventual frozen hypothesis are available as of the signal date. Record missing inputs and daily eligible counts. Do not forward-fill missing prices to fabricate trades.
- Unknown future outcomes must not determine ranking eligibility. If an eventual outcome cannot be measured, preserve the original ranking and disclose the missing label, reason, and effect on coverage. Resolve material missingness before interpreting aggregate performance.

**Decision required later:** Supply and freeze the universe, explain its selection, and approve how material data exceptions will be handled.

### 4. Evaluation period and required history

**User-set:** Evaluate only the most recent 12 months.

**Provisional window:** At the start of the approved data stage, freeze an as-of date D representing the latest fully completed trading session available in the data. The evaluation window is the trailing 12 calendar months ending on D, inclusive. Record exact calendar boundaries, retrieval time, and actual trading sessions before inspecting ranking results. Do not move this frozen window to improve results.

For the primary evaluation, the signal, entry, and exit must all lie inside this window. Dates near the end whose 10-day outcomes have not matured remain unlabeled and are excluded from outcome statistics, not assigned zero returns. Explain that the final signal dates therefore have shorter outcome coverage than the full 12-month calendar span.

Required historical data will include:

- Daily open, high, low, close, volume, adjusted close or documented adjustment factors, and corporate-action information for each universe member and SPY. This is a data inventory, not feature selection.
- Session dates, symbol identities, and missing-data diagnostics.
- Enough pre-window history to compute the eventual hypothesis's longest backward-looking input at the first evaluated signal date. The exact warm-up length is unknown until that hypothesis is approved; it must not be chosen for attractive results.
- A reproducible data snapshot, retrieval timestamp, adjustment settings, and package versions at the implementation stage. Confirm what Yahoo-derived data may be redistributed before including it in a public repository.

Yahoo history downloaded today may contain later corrections and retrospective adjustments. A current download alone does not prove what was visible on a past date. Audit whether chosen inputs are affected, disclose any remaining point-in-time limitations, and do not call the reconstruction perfectly point-in-time without evidence.

**Decision required later:** Confirm this window interpretation and freeze its actual dates at acquisition. Older history is for input preparation only, not expanding the evaluation period.

### 5. How daily rankings will be evaluated

Evaluate ordering quality first. No trading portfolio or capital allocation is being specified.

**Primary descriptive metric:** On each eligible signal date, calculate Spearman rank correlation between the predicted scores and realized 10-day excess returns across stocks with measurable labels. Higher scores mean stronger expected performance. Average these daily correlations with equal weight per date. Report the median and fraction of dates with positive correlation as context. Use average ranks for ties; correlation is undefined when a vector is constant and must be reported as undefined, not zero.

**Secondary diagnostics, provisionally fixed now:**

- Split each day's eligible ranked universe into five groups from highest to lowest score. Use a deterministic near-equal partition; at 50 stocks, each group has 10. Set an exact tie and partition rule before implementation; an alphabetical display tiebreak conveys no predictive information.
- Report each group's equal-weight mean 10-day excess return, averaged equally across dates. Check whether the ordering of outcomes broadly follows the predicted ordering without requiring every group difference to be positive.
- Report the top group's mean and median 10-day excess return, its fraction of stock observations outperforming SPY, and its fraction of dates with positive group mean excess return. These last two denominators answer different questions.
- Report top-minus-bottom mean return as an ordering diagnostic, not an executable long-short strategy result.
- Compare the top group with the entire eligible universe's equal-weight mean return over matching dates and measurable stocks. This distinguishes stock-selection value from a universe that happens to outperform SPY as a whole.
- Report coverage: attempted dates, ranked stocks, matured outcomes, missing labels, and the actual counts behind every metric. With partial outcomes, flag affected dates and any distortion of the originally selected groups.
- Report monthly summaries within the same window, the worst observed top-group cohort return, and top-group membership turnover. These describe instability and implementation burden, not independent validation samples.

Ten-day outcomes from adjacent signal dates overlap. Stocks on the same date also share market exposures. Do not treat every stock-date row as an independent observation or use a naive significance test. With only 12 months, aggregate metrics are mainly descriptive. Any later uncertainty method must account for dependence and be specified before use.

Daily cohort returns must not be compounded into a strategy equity curve: they represent overlapping hypothetical holdings. Annualized return, Sharpe ratio, portfolio drawdown, and net trading performance require separately approved capital, overlap, execution, and cost rules. They are outside this stage.

**Decision required later:** Accept the primary metric and fixed secondary diagnostics before seeing results. No metric shopping or tuning group sizes after results are known.

### 6. Most important ways we could fool ourselves

1. **Lookahead:** using future prices, full-period normalization, revised information, or future label availability to determine past inputs or eligibility. Keep historical inputs and outcome labels separate; each input needs an availability rule.
2. **Survivorship and selection:** choosing today's successful or liquid companies retrospectively. Record the universe's origin and constrain claims accordingly.
3. **Timing mismatch:** computing a score from a closing price and pretending to trade at that same close, or comparing stocks and SPY over different sessions.
4. **Data defects:** incorrect splits, dividends, adjusted opens, stale prices, ticker mappings, or silently omitted failed companies. Audit exceptions before interpreting results.
5. **Overlapping observations and common exposures:** an apparently large sample can contain far less independent information. Market, sector, or risk exposure may explain excess returns without demonstrating unique stock-selection ability.
6. **Repeated experimentation:** trying many hypotheses against the same year makes that year part of development. Log every attempt, never call a reused window untouched out-of-sample evidence, and do not optimize without authorization.
7. **Short period and regime dependence:** one recent year cannot establish persistent predictive power or behavior in other market conditions.
8. **Implementation gap:** gross outcomes omit spreads, slippage, fees, taxes, execution delays, and capital constraints. Ranking quality alone is not evidence of tradable net profit.

### 7. What success means—and does not mean

**A successful experiment** produces a reproducible, auditable answer to the frozen question, including an honest null, negative, or inconclusive result. A hypothesis can fail while the experiment succeeds. All failures and exclusions remain in the record.

**Evidence supporting a later ranking hypothesis** would provisionally include positive average rank correlation and higher top-group outcomes than lower-ranked stocks and the universe baseline, with coverage and monthly diagnostics showing how concentrated that evidence is. These are descriptive directions, not a numerical pass threshold or proof of statistical significance. A numerical decision threshold, if desired, must be agreed before inspecting results.

**Success would not establish** guaranteed outperformance, a profitable executable strategy, causal insight, risk-adjusted alpha, robustness outside the supplied universe and year, or a recommendation to invest. Favorable retrospective evidence would motivate a separately authorized forward test, not a claim that the search is finished.

### 8. Major stages and user decision gates

1. **Specify the question (current stage):** document target, timing, constraints, metrics, and biases. Stop for user review.
2. **Freeze universe and data protocol:** obtain the user's list, resolve timing and window choices, then acquire and audit data only with authorization for that stage. Stop for review of data quality and limitations.
3. **Register one hypothesis:** propose one simple economic rationale and fixed ranking method, required history, tie rules, and expectations. No parameter search. Stop for approval before testing.
4. **Implement and validate:** build the smallest pipeline needed; verify timestamps, alignment, labels, and bias protections. Stop before running the research evaluation unless that run is explicitly included in the stage authorization.
5. **Run the frozen evaluation:** preserve configuration, metrics, exceptions, and unattractive results. Separate observations from explanations. Stop for interpretation and a user decision.
6. **Try to break the hypothesis:** propose and approve targeted robustness checks before running them. Record failed checks; any new hypothesis is a new logged experiment. Stop before revising the research.
7. **Build a repeatable daily process:** after a user decision to proceed, generate timestamped rankings, monitor data failures, and accumulate prospective outcomes. No automated trading is implied. Stop for review.
8. **Prepare the public laboratory:** document reproduction, learning, limitations, and the viewer's own question-building workflow; create the deferred onboarding files and review public-data permissions. Publishing requires a later user instruction.

### 9. Decision register and evidence ledger

**User-fixed:** 10 trading days, SPY, approximately 50 user-supplied stocks, daily ranking, most recent 12 months, simple preferred stack, no optimization, and stage-by-stage user control.

**Provisional, requiring review before dependent work:** after-close signals; next-open entry and t+11-open exit; adjusted return proxy; full-containment evaluation window; common-stock universe interpretation; daily rank correlation as primary metric; five-group diagnostics. Exact universe, dates, warm-up, data exception rules, and tie implementation remain pending.

**Evidence:** Only the user's initial instructions and these definitions exist. No empirical performance evidence exists.

**Interpretation:** This design can test relative ordering within a selected universe. It cannot yet answer whether any ranking method works.

**Changes and failures:** No prior methodology, tested hypotheses, or empirical failures to report. Future entries must retain and explain them.

**Next decision:** Does the user accept the proposed signal-to-outcome clock—rank after the close, enter at the next open, and measure 10 open-to-open trading intervals?

**Stage boundary:** Stage 1 complete. Stopped pending the user's next instruction.

## 2026-09-08 — GitHub treasure hunt: source review and timing decision

Status: research-only stage complete. No dependencies installed, implementation written, market data acquired, strategies executed, parameters optimized, or third-party code copied into the project. Repository documentation and selected source functions were inspected, not comprehensively audited or run.

### Approved timing and stage amendment

The user approved this continuing convention: calculate signals from information available at the market close; assume entry at the next trading day's open; measure forward performance over 10 trading days from entry; measure SPY over the identical interval. Using the Stage 1 session notation, entry is the open of t+1 and exit is the open of t+11, ten open-to-open trading intervals later. This resolves the earlier provisional clock and supersedes the pending timing decision in the historical Stage 1 entry. It does not authorize same-close execution.

The user explicitly inserted a GitHub idea-review stage before implementation. This supersedes the initial specification-only prohibition on GitHub research for this stage, while preserving the prohibitions on implementation, optimization, and searching for the most profitable strategy. Other Stage 1 provisional methodology choices are not silently promoted to approved decisions by this entry.

### Search and selection criteria

Searched GitHub through web search and inspected repository pages, documentation, license texts, and selected Python source. Queries covered Python daily stock signals, Yahoo/yfinance, SMA crossover, momentum, RSI, Bollinger Bands, ATR filtering, and breakouts. No selection was made using reported backtest profitability.

Prioritized simple and explainable formulas; identifiable readable source and documentation; compatibility with daily OHLCV or its close-price subset; adaptation to the fixed universe and 10-day outcome; explicit reuse licensing; and community adoption where available. Popularity is evidence of adoption or interest, not investment edge, correctness, maintenance quality, or validation of a particular signal.

The five finalists below are the strongest fits among the inspected sources, not a claim of an exhaustive GitHub ranking. Three are frameworks containing small signal examples/components; two are indicator libraries. They are references for building blocks, not proposals to add their frameworks or packages. None of the inspected examples is already our complete 50-stock, next-open, fixed-10-day ranking experiment.

Popularity figures are approximate GitHub page displays observed during this review, potentially rounded or cached; they are not an exact API snapshot. Links reference upstream branches and may change. Before any actual code reuse, record the exact commit and applicable file license.

### Five selected candidates

#### 1. pmorissette/bt — relative momentum selection

- Repository: [pmorissette/bt](https://github.com/pmorissette/bt). About 3.0k stars and 498 forks. [MIT license](https://github.com/pmorissette/bt/blob/master/LICENSE).
- Inspected source: [bt/algos.py](https://github.com/pmorissette/bt/blob/master/bt/algos.py), specifically SelectMomentum, StatTotalReturn, and SelectN.
- Plain English: compare each asset's percentage gain over a backward-looking interval and select the strongest. The source already performs cross-sectional ordering; retaining all scores rather than just the selected names would produce a ranking.
- Inputs: a date-by-security price table, historical lookback, optional lag, and number selected. Daily adjusted closes from Yahoo OHLCV can supply the price input; this concept does not require volume or intraday data.
- 10-day fit (our assessment): easy to evaluate over 10 forward sessions. The backward lookback is a separate choice and does not have to equal the prediction horizon. Recent winners could continue or reverse; source availability establishes neither outcome.
- Adaptation: low for the mathematical concept in pandas; moderate if adopting its portfolio engine. Retain all roughly 50 scores, use session-based lookbacks, and attach our separate next-open forward labels and SPY outcomes. No need to adopt bt or its ffn dependency.
- Concerns: date-offset lookbacks in the source are not automatically trading-session counts; selection and rebalancing mechanics are different from our ranking evaluation. Ensure complete input history and avoid interpreting missing-data selection as unbiased coverage. Price-return calculations only represent total-return proxies when supplied appropriately adjusted prices.

#### 2. kernc/backtesting.py — SMA crossover, with an ATR-stop extension

- Repository: [kernc/backtesting.py](https://github.com/kernc/backtesting.py). About 8.9k stars and 1.5k forks. [AGPL-3.0 license](https://github.com/kernc/backtesting.py/blob/master/LICENSE.md).
- Inspected examples: [Quick Start User Guide](https://github.com/kernc/backtesting.py/blob/master/doc/examples/Quick%20Start%20User%20Guide.py) and [Strategies Library](https://github.com/kernc/backtesting.py/blob/master/doc/examples/Strategies%20Library.py); also [backtesting/lib.py](https://github.com/kernc/backtesting.py/blob/master/backtesting/lib.py).
- Plain English: a short moving average rising through a longer average flags a possible upward trend. The introductory example uses 10/20-bar averages; the composable ATR-stop example uses 10/25. These are source defaults, not approved project parameters.
- Inputs: close prices and two rolling means; high, low, and prior close for ATR in the extension. Accepts OHLC DataFrames, so daily Yahoo data is a natural source after formatting and adjustment checks.
- 10-day fit (our assessment): interpretable hypothesis, but crosses may be infrequent and trend development can take longer than 10 days. Whipsaws are possible.
- Adaptation: low for the averages, moderate for a ranking specification. A binary crossover creates many ties and no fresh event on most days; a continuous normalized average spread would be a separately approved adaptation, not the same signal. Replace variable trade exits with our fixed forward measurement; do not import the engine.
- Concerns: tutorial optimization is out of scope; the original examples are trade simulations, not cross-sectional forecasts. Inspected TrailingStrategy computes a rolling ATR and then backward-fills missing early values. This can introduce future information if those values are used before ATR warm-up completes. Its optional percentage-stop conversion also uses a full-series average; the reviewed crossover example uses a fixed ATR multiple instead. These are specific source observations, not a claim that every use of the framework leaks.

#### 3. bukosabino/ta — RSI, Bollinger Bands, and Donchian breakout building blocks

- Repository: [bukosabino/ta](https://github.com/bukosabino/ta). About 5.2k stars and 1.2k forks. [MIT license](https://github.com/bukosabino/ta/blob/master/LICENSE).
- Inspected source: [ta/momentum.py](https://github.com/bukosabino/ta/blob/master/ta/momentum.py), including RSIIndicator and the available momentum definitions, and [ta/volatility.py](https://github.com/bukosabino/ta/blob/master/ta/volatility.py), including BollingerBands, AverageTrueRange, and the DonchianChannel implementation.
- Plain English: RSI compares recent gains with recent losses; Bollinger Bands describe price relative to its recent average and variability; Donchian channels describe recent highs and lows. These can support distinct continuation, reversal, or breakout hypotheses. The library supplies measurements, not a validated choice among those hypotheses.
- Inputs: closes for RSI and Bollinger Bands; high/low for Donchian channels; high/low/prior close for ATR. Source defaults include RSI 14 and Bollinger 20 with a two-standard-deviation band; no defaults are adopted here.
- 10-day fit (our assessment): recent price extension or a range break can be tested at this horizon, but neither an extreme RSI nor a band touch guarantees reversal. Trend continuation is a competing interpretation requiring a separate predeclared hypothesis.
- Adaptation: low for extracting per-stock daily measurements from yfinance Series; moderate for selecting one direction and ranking rule. No need to install ta or calculate every available indicator.
- Concerns: smoothing and standard-deviation conventions differ across libraries. Warm-up must be explicit; the ATR implementation initializes early entries to zero, which must not be mistaken for observed low volatility. For a breakout above a prior range, exclude the signal day's high from the reference range. An indicator library is not a backtest-validation service.

#### 4. peerchemist/finta — volatility squeeze

- Repository: [peerchemist/finta](https://github.com/peerchemist/finta). About 2.3k stars and 715 forks. [LGPL-3.0 license](https://github.com/peerchemist/finta/blob/master/LICENSE). Archived September 2, 2022.
- Inspected source: [finta/finta.py](https://github.com/peerchemist/finta/blob/master/finta/finta.py), specifically SQZMI and its Bollinger/Keltner construction.
- Plain English: flag a quiet period when Bollinger Bands sit inside Keltner Channels. This describes volatility contraction that could precede a larger move in either direction.
- Inputs: daily high, low, close; rolling means, standard deviation, and ATR-based Keltner width. The source expects lowercase OHLC column names.
- 10-day fit (our assessment): useful for a contraction/expansion hypothesis, but quiet conditions may persist longer than 10 days, and volatility does not identify which stock will outperform SPY.
- Adaptation: moderate. Normalize Yahoo column names, preserve valid warm-up, and specify a directional hypothesis plus a continuous cross-stock score if the user chooses this family. The inspected SQZMI returns a Boolean squeeze flag despite its name; it does not supply a directional momentum ranking.
- Concerns: archived status and the README's explicit indicator-accuracy warning make this a reference to validate, not a dependency recommendation. A false squeeze flag alone is not evidence of a new squeeze release; a release needs a transition from a prior valid true state. Extra choices reduce its appeal as our first baseline.

#### 5. mementum/backtrader — minimal SMA signal example

- Repository: [mementum/backtrader](https://github.com/mementum/backtrader). About 23.2k stars and 5.3k forks. [GPL-3.0 license](https://github.com/mementum/backtrader/blob/master/LICENSE).
- Inspected source: [samples/sigsmacross/sigsmacross2.py](https://github.com/mementum/backtrader/blob/master/samples/sigsmacross/sigsmacross2.py); the README and [stop-loss examples](https://github.com/mementum/backtrader/blob/master/samples/stop-trading/stop-loss-approaches.py) provide additional context.
- Plain English: signal a trend change when the 10-bar average crosses the 30-bar average. Its tiny strategy class is a second clear teaching reference for crossover logic, although the engine underneath is substantial.
- Inputs: closing prices for the two averages, and OHLC data for execution. Supports pandas data feeds; Yahoo daily OHLCV can be supplied through that route. The example's historical direct Yahoo downloader should not be assumed to work unchanged today.
- 10-day fit (our assessment): testable, but its 30-bar trend reference does not imply a 10-day predictive edge. Like the other crossover candidate, it generates sparse events and potentially late signals.
- Adaptation: low for the formula, moderate for a full daily ranking, and high relative to our needs if adopting the framework. Extract the concept into the approved stack only after user approval; do not bring over broker abstractions.
- Concerns: cumulative stars do not prove current maintenance or example compatibility. Sparse events require an explicit tie/ranking design; the framework's optional execution shortcuts and variable exits must not override our timing or horizon. This is an alternative source for the same family, not independent confirmation that crossovers work.

### MA crossover plus ATR or volatility filtering: exact finding

**Confirmed among the finalists:** kernc/backtesting.py's Strategies Library example combines SMA crossover with an ATR-based trailing stop at two times ATR. This is volatility-dependent exit management, not a volatility gate on entry. Importing that stop into the prediction target would change our fixed 10-day question and is not proposed.

**Not confirmed in the inspected finalist examples:** a ready-made SMA-crossover-plus-ATR entry filter. Availability of separate SMA and ATR functions does not prove a combined strategy exists. The finta squeeze combines volatility bands, not fast/slow MA crossover.

An additional search result, [Elaine-764/Moving-Average-Backtest](https://github.com/Elaine-764/Moving-Average-Backtest), explicitly documents an MA crossover with an ATR entry filter in its README. It was not selected because no explicit reuse license was visible in the reviewed root/README, adoption was minimal (0 stars/0 forks displayed), and the filter code was not audited. The README's performance claims were not used as evidence for or against our hypothesis. This documents a lead, not verified reusable code.

### Other repositories screened and not selected

- [BSoybilgen/simple-trade](https://github.com/BSoybilgen/simple-trade): direct yfinance daily examples, RSI/SMA combinations, and AGPL-3.0 licensing, but only about 2 stars/1 fork displayed. The README emphasizes optimization, and deeper source retrieval was unsuccessful in this review. Less compelling than the inspected finalists for auditable adaptation. No code was executed.
- [alejandroquilez/sma-backtester](https://github.com/alejandroquilez/sma-backtester): simple SMA focus, but the reviewed root listing did not show a license and showed only one commit; not selected as a reusable source.
- [ar3vind/quant-sma-backtest](https://github.com/ar3vind/quant-sma-backtest): simple 20/100 crossover, but no license visible in the reviewed listing, minimal adoption, and less immediate short-horizon relevance. No conclusion drawn about its profitability.
- [galafis/Real-Time-Stock-Analytics](https://github.com/galafis/Real-Time-Stock-Analytics): MIT-licensed Yahoo indicator dashboard, but little displayed adoption and a UI focus beyond this experiment's needs.
- [JamieWells1/quant_trading_backtester](https://github.com/JamieWells1/trading-algorithm-boilerplate): search result describes Yahoo/SMA/RSI/ATR support, but emphasizes Monte Carlo optimization and a larger dashboard/risk-management architecture. Not selected; no detailed code or license audit performed.

### Licensing notes for eventual public reuse

The finalists have explicit open-source licenses. MIT is the simplest reuse fit among these choices; its [ta license text](https://github.com/bukosabino/ta/blob/master/LICENSE) and [bt license text](https://github.com/pmorissette/bt/blob/master/LICENSE) require preserving the copyright and permission notice in copies or substantial portions. GPL, AGPL, and LGPL are conditional copyleft licenses, not equivalent to MIT; copying or modifying their implementation can bring source, notice, and licensing obligations. The AGPL also addresses modified software used over a network. Any later reuse must follow the linked license and the particular file's notices, and be compatible with our chosen project license. No project license has been chosen here.

Studying a standard mathematical concept and writing our own minimal implementation is a different activity from copying upstream code. Retain conceptual attribution even when independently implementing formulas. We have not copied third-party implementation code, and nothing in this review approves installing any framework.

### Recommended baseline — proposal only

**Recommend simple trailing-return momentum**, using the SelectMomentum concept in pmorissette/bt as an educational reference and an independently written pandas calculation if subsequently approved.

Proposed concrete starting specification: rank stocks from highest to lowest percentage change in consistently adjusted closing prices over the last **20 trading sessions**, measured through signal day t. In notation: score(i,t) = adjusted_close(i,t) / adjusted_close(i,t−20) − 1. Twenty sessions is a provisional round one-month lookback chosen for explainability, not a tuned value or a claim that it is optimal. It needs user approval before implementation.

Why this baseline: one understandable calculation, one historical lookback, a continuous comparable score for every eligible stock, readable reference code, and no threshold, oscillator-smoothing rule, exit logic, or extra dependency. It directly matches the cross-sectional ranking question. This recommendation is our methodological judgment, not a finding from historical performance.

The hypothesis would be that recent relative winners tend to outperform weaker recent stocks over the next 10 sessions. It can fail through reversal or exposure effects. Subtracting the same trailing SPY return from every stock does not change the within-date ordering; SPY remains the forward outcome benchmark. RSI's name does not mean relative performance versus SPY.

A moving-average crossover is also easy to explain visually, but converting its occasional binary events into a full daily ranking introduces another design decision. Do not silently replace crossover with average spread, add an ATR filter, try many lookbacks, or combine the shortlisted indicators.

**Evidence:** accessible source, documentation, licenses, displayed adoption, and the specific implementation observations above. **Interpretation:** suitability and adaptation judgments, including the preferred baseline. **Performance evidence for our experiment:** none.

**Next user decision:** approve or revise the proposed single 20-session momentum ranking hypothesis before any implementation. The user still needs to provide the fixed universe and resolve the remaining data protocol choices before data acquisition or testing. Stop here.

## 2026-09-08 — V0 specification and human-directed V1 hypothesis

Status: specification only. The human researcher selected moving-average crossover as the baseline family. The exact V0 specification below is proposed for review, not an authorization to implement or test. No market data was acquired, no code implemented, no backtest run, and no parameters optimized.

### Human decision and superseded AI recommendation

The human researcher explicitly rejected the AI's proposed 20-session momentum baseline and selected **moving-average crossover** because it provides a simple reference for a separate hypothesis: bullish crosses may be more informative after meaningful contraction in ATR as a percentage of price. This is a research-design choice made before observing results, not a response to an unattractive backtest. Momentum was never approved or tested. Its earlier recommendation remains in this log as history and is now superseded.

### V0 — GITHUB BASELINE

#### Source selection and comparison

Use the bullish branch of the **10/20 simple-moving-average crossover concept in kernc/backtesting.py's introductory Quick Start example**. Sources rechecked on 2026-09-08:

- [Quick Start User Guide](https://github.com/kernc/backtesting.py/blob/master/doc/examples/Quick%20Start%20User%20Guide.py): initial example sets fast 10 and slow 20, computed from closing prices. It includes both bullish and bearish actions and later optimization; our reference is only its initial bullish crossover concept. Neither the optimization section nor its reported returns informed selection.
- [crossover helper](https://github.com/kernc/backtesting.py/blob/master/backtesting/lib.py): verifies the strict prior-below/current-above definition recorded below.
- [Strategies Library example](https://github.com/kernc/backtesting.py/blob/master/doc/examples/Strategies%20Library.py): uses 10/25 and an ATR trailing stop. Its transition from not-above to above also handles prior equality differently from the introductory helper. Do not blend these examples or import that stop into V0.
- [mementum/backtrader SMA example](https://github.com/mementum/backtrader/blob/master/samples/sigsmacross/sigsmacross2.py): uses 10/30. This is a clear alternative already identified, but the introductory backtesting.py 10/20 pair offers a shorter reference window with no additional volatility component.

Selection rests on directly documented defaults, simplicity, source fidelity, and a short historical reference window. It is not an empirical comparison of 10/20, 10/25, and 10/30. No claim is made that 10/20 is optimal or more profitable. These source links track upstream branches; record an exact source revision before future code reuse rather than inventing a commit identifier now.

#### Exact proposed signal specification

Let t denote a completed regular U.S. trading session, and C(t) the stock's consistently adjusted daily closing-price series on a basis appropriate to information available by t. The proposed price convention is split- and dividend-adjusted closes, consistent with the earlier adjusted-price proposal. Confirm Yahoo's adjustment and availability semantics in the later data audit before implementation; raw-close substitution would be a recorded methodological change. Do not mistake today's downloaded adjusted history for verified historical data availability.

- **Fast SMA:** arithmetic mean of the 10 session closes C(t−9) through C(t), inclusive.
- **Slow SMA:** arithmetic mean of the 20 session closes C(t−19) through C(t), inclusive.
- **Bullish crossover on t:** fast SMA(t−1) **<** slow SMA(t−1), AND fast SMA(t) **>** slow SMA(t).
- **Equality:** equality on either of those comparison dates is not a trigger. For example, below → equal → above across three sessions produces no V0 event under this strict two-session rule. This intentionally follows the selected repository helper. Do not silently substitute a less-than-or-equal comparison, tolerance, or last-nonzero-sign rule.
- **Event, not persistent state:** fast-above-slow on subsequent days does not produce repeated buy signals. An intraday cross that disappears by the close does not qualify.
- **Direction:** bullish/buy events only. A bearish cross is neither a short signal nor an early exit rule for this experiment. Absence of a bullish event is not a sell recommendation.
- **Warm-up:** require 21 consecutive valid session closes, C(t−20) through C(t), to calculate both today's and yesterday's slow averages. Require valid fast averages too. Missing history means ineligible/unavailable, not a false signal manufactured by filling prices or shortened windows. Do not skip a missing session and count the next available row as if the gap never occurred.
- **Filters:** none. No ATR, volume, slope, minimum crossover size, market-regime condition, or price-above-SMA requirement is added.

The provisional adjusted-price convention is a project-specific data choice; the upstream example simply consumes its supplied Close column. Our specification is GitHub-derived, not a claim of identical reproduction of the upstream trading simulation.

#### Why 10/20 is defensible for a 10-session outcome

Ten and twenty sessions represent roughly two and four trading weeks. Their comparison asks whether recent prices have strengthened relative to a somewhat longer recent baseline. These windows are short enough to frame a near-term question and are directly taken from the source's introductory example, reducing discretionary parameter invention.

This is a design rationale, not performance evidence: the 10-session fast average is not a forecast of the next 10 sessions. Averages lag price, crosses can whipsaw, and a move can already be exhausted at the signal. No parameter sweep or retrospective selection is authorized.

#### Information timing and forward outcome

Calculate the event only after session t has closed and its required closing-price data is available. Today's regular-session OHLCV and earlier observations may then be known; V0 uses only closing prices and past averages. Tomorrow's open and every later price remain unknown when deciding whether an event exists. Data revisions or adjustment information unavailable at t cannot be used to determine that historical decision without disclosing a reconstruction limitation.

Preserve the user-approved clock: entry at the open of t+1, exit measurement at the open of t+11, exactly 10 open-to-open trading intervals. Measure SPY over precisely those same endpoints. The forward label remains stock return minus SPY return in percentage points, with the adjusted-return proxy and frozen 12-month window subject to the previously recorded data protocol.

Waiting until the next open separates a decision requiring the completed close from its assumed execution, preventing the same-close execution lookahead error. It does not cure future-data leakage elsewhere. If inputs were unavailable before the next open, flag the event as non-actionable under this clock rather than retrospectively pretending an order could have been placed. Opening gaps remain part of entry pricing; the signal-to-entry overnight move is not earned by the assumed position.

Every detected event is a research observation with its own 10-session outcome; a later bearish cross does not truncate that outcome. Any overlapping events remain identifiable and dependent, not independent trades in a compounded equity curve. Missing future labels must not erase the original event. Portfolio sizing, order management, costs, and event-overlap trading policies are not specified or implemented here.

#### Relation to the original daily-ranking objective

At this stage V0 is a **binary bullish-event baseline**, not a complete ranking of all 50 stocks. This follows the user's explicit bullish-signal direction and is recorded as a change in the immediate research focus. The eventual daily-ranking objective remains open; do not create a new score to resolve it silently.

Dates can have zero or several events, and all simultaneous events are equally signaled by V0. Display order would not indicate expected performance. Stage 1 rank-correlation and quintile proposals must not be mechanically presented as the primary validation of this event experiment. Before testing, explicitly agree an event-based evaluation protocol, aggregation weights, treatment of overlap, and any later relationship to a daily ranking. Keep the fixed universe and SPY benchmark.

#### Implementation and attribution decision

The cleaner later implementation is to write the documented arithmetic means and Boolean event rule ourselves in pandas, with numpy/yfinance only as already planned. No backtesting.py installation or strategy-engine adaptation is needed. Preserve conceptual attribution to kernc/backtesting.py, the Quick Start, and its crossover helper, and label our bullish-only/fixed-horizon design as an adaptation of the concept rather than a replication of its full simulation.

The upstream [license is AGPL-3.0](https://github.com/kernc/backtesting.py/blob/master/LICENSE.md). If upstream implementation or substantial text is copied or modified later, attribution alone is insufficient: retain applicable notices, identify modifications, and comply with the license's source and distribution/network-use provisions as applicable. Independently expressing a standard mathematical rule is distinct from copying the licensed implementation; conceptual attribution remains part of our research record. This stage copies no third-party implementation code and chooses no license for our eventual public repository.

### V1 — ATR-CONTRACTION + SMA CROSSOVER

**Human-origin hypothesis, documented only:**

1. ATR expressed as a percentage of price contracts materially.
2. A bullish V0 SMA crossover subsequently occurs.
3. Ask whether those setups have better subsequent 10-trading-day excess returns versus SPY than the V0 crossover alone.

V1 is a proposed conditioning of the same V0 bullish-event definition. Keep the SMA pair, crossover equality rule, price convention, universe, entry time, benchmark, and outcome horizon unchanged in that comparison. It is not an ATR stop, an early exit, or a volatility-dependent holding period.

**Intentionally undefined:** ATR lookback; ATR smoothing/initialization; price denominator convention; how to measure contraction and its reference level/window; how much contraction is material; required duration; how long before crossover it may occur; expiry and sequencing rules; handling of repeated contractions; and missing-history eligibility. No numerical values, defaults, percentiles, thresholds, or formulas for these decisions are selected now.

The ordering “contraction, then crossover” must be translated into an explicit historical timing rule before testing. Every component of the contraction decision must use information already available at its designated observation time; no full-period thresholds or future volatility may determine past eligibility.

**Evaluation decisions to make before testing:** define what “better” means (primary excess-return metric and aggregation), distinguish V1's qualifying subset from the full V0 event set and the nonqualifying V0 events, compare coverage on common data eligibility, account for dependent outcomes, and state how sample size limits interpretation. Conditioning on contraction could select different stocks, dates, sectors, or regimes; a difference would not by itself establish causality. No evaluation protocol is implemented or silently finalized here.

Freeze those decisions before examining V1 outcomes. Do not tune them to obtain an improvement or change V0 after seeing the comparison. Retain inconclusive or adverse results. The hypothesis can fail, including by generating too few qualifying events.

### Decision and evidence ledger

- **User-approved:** bullish moving-average crossover family; rejection of momentum; purpose of creating a baseline for the user's future ATR-contraction hypothesis; unchanged next-open/10-session/SPY timing.
- **Proposed exact V0:** strict 10/20-SMA bullish crossover from backtesting.py's introductory example, on valid adjusted daily closing prices, with no filters and no bearish actions.
- **Pending:** review of this exact V0, universe delivery, price/data audit, event-evaluation protocol, and every listed ATR-contraction definition.
- **Evidence:** inspected upstream defaults, SMA and crossover definitions, and license. **Interpretation:** the educational and horizon rationale. **Performance evidence:** none for either V0 or V1.
- **Next decision:** settle and preregister the meaning and timing of a material contraction in ATR as a percentage of price, plus the comparison metric, before adding or testing V1. This entry supplies no ATR parameters.
- **Stop:** specification stage complete; wait for the user's next instruction. No implementation or testing authorization is inferred.

## 2026-09-08 — Preregistration: frozen V0 and human-origin V1

Status: preregistered before any V0 or V1 performance calculation or inspection in this project. Documentation only; no pipeline, market-data acquisition, historical results, backtest, or optimization. This is a dated local research record, not an externally timestamped registration service.

### Provenance, authority, and purpose

The user has now frozen V0's exact bullish 10/20-SMA rule. V0 derives from the [kernc/backtesting.py introductory crossover concept](https://github.com/kernc/backtesting.py/blob/master/doc/examples/Quick%20Start%20User%20Guide.py) and its [strict crossover helper](https://github.com/kernc/backtesting.py/blob/master/backtesting/lib.py). Existing attribution and licensing notes remain applicable.

V1 is the **human researcher's added hypothesis**, not a GitHub strategy claim or an AI-selected optimization. The human selected ATR period 14, closing-price normalization, a prior-20-session maximum, and a 20% contraction threshold BEFORE looking at any V0 or V1 performance in this experiment. The purpose is to test whether the added ATR clue improves the GitHub baseline, not to manufacture a profitable result. The rejected momentum proposal remains superseded.

This entry supersedes earlier statements that these V0/V1 parameters or the primary event metric were undecided. It also resolves the earlier conceptual sequencing question: the two conditions are evaluated on the SAME signal date. No separate earlier contraction event, minimum contraction duration, or waiting period is required. The historical maximum comes from prior sessions.

### V0 — GITHUB BASELINE: frozen rule

Index completed regular trading sessions by t. Let C(t) be the consistent closing-price input. Define F(t) as the arithmetic mean of C(t−9) through C(t), and S(t) as the arithmetic mean of C(t−19) through C(t).

**V0(t) = [F(t−1) < S(t−1)] AND [F(t) > S(t)].**

Equality does not trigger a signal. Being above the slow SMA without a fresh strict crossover is not a new event. Require 21 consecutive valid closes to evaluate the two dates. Bullish events only; no bearish trades or early exits.

Calculate after the current close is available. Hypothetical entry is the open of t+1. Measure through the open of t+11, ten open-to-open trading intervals after entry. SPY uses those identical endpoints. Future entry/exit prices are outcome inputs, never signal inputs. Next-open execution prevents assuming a fill at the close needed to form the decision, but does not eliminate data-revision or adjustment lookahead elsewhere.

### V1 — ATR CONTRACTION + SMA CROSSOVER: frozen human parameters

Let A(t) = ATR14(t) / C(t). This ratio is called ATR%; multiplying every A value by 100 merely changes display units and does not change the test.

Let M(t) = max[A(t−20), A(t−19), ..., A(t−1)]. This is exactly the prior 20 trading sessions, **excluding t**. Require all 20 values to be valid; do not use a shorter available window or a full-period maximum.

**Contraction(t) = [A(t) <= 0.80 × M(t)].**

**V1(t) = V0(t) AND Contraction(t).**

Equality at the 0.80 threshold qualifies. The decline is 20% relative to the prior maximum, not a decline of 20 percentage points. Only information available by t's close enters the calculation. No future volatility, later maximum, extra confirmation session, or intraday observation is allowed. V1 has the same signal clock, entry, outcome horizon, and benchmark as V0; it is a subset filter, not a stop-loss or position-sizing rule.

The user freezes fast SMA 10, slow SMA 20, ATR period 14, contraction reference window 20, and multiplier 0.80. No change to these, or any agreed methodology, without an explicit later user-authorized research amendment. Preserve this entry and all failed results when recording amendments.

### Explicit mathematical implementation conventions

The user specified ATR(14), but did not specify its smoothing or seed. To remove that ambiguity, the assistant records the following explicit convention before results: **Wilder smoothing, seeded by the mean of the first 14 valid true ranges**. This convention is assistant-specified, not misattributed to the human's parameter selection.

True range on session t is the maximum of H(t)−L(t), abs[H(t)−C(t−1)], and abs[L(t)−C(t−1)]. After the seed, ATR14(t) = [13 × ATR14(t−1) + TR(t)] / 14. This is not a 14-session simple rolling average and not an EMA with coefficient 2/15. Do not silently substitute another library's definition or seed.

Use consistent price units and adjustment treatment across H, L, C, and prior C. The previously proposed split/dividend-adjusted data convention still requires the later data audit; do not mix raw high/low with adjusted close. The frozen signal formulas do not certify Yahoo history as point-in-time data. Freeze the retrieval settings, historical start, seed location, and price-adjustment protocol before outcome calculation.

At the mathematical minimum, V1 needs 35 consecutive OHLC sessions: one initial close, 14 subsequent true ranges to seed ATR, then 20 further sessions so the current ATR% has 20 prior valid ATR% observations. Earlier history can stabilize the recursive initialization; its acquisition start must be fixed before testing and not selected for performance. V0 requires only 21 closes. Acquire sufficient pre-evaluation history to avoid truncating the evaluation window differently merely because V1 has a longer warm-up.

Require positive finite closing prices, finite consistent OHLC, and complete valid reference values. Missing ATR history is **unavailable**, not a failed contraction. Never backward-fill indicators from future values. After missing data, do not bridge a gap with invented observations; flag affected windows and require a fresh valid seed/history before resuming ATR eligibility. If the valid prior ATR% maximum is zero, retain the literal frozen inequality: current zero qualifies. Flag such degenerate data for audit rather than silently adding a new filter.

### Preregistered V1-versus-V0 evaluation

One observation is one stock's qualifying bullish signal on one date. Give each measurable signal equal weight; a date with multiple signals contributes multiple observations. This explicit per-signal interpretation replaces the earlier provisional per-date ranking metric for the V0/V1 event comparison. It is not portfolio allocation or a daily ranking score.

For each event, compute the stock's simple return from entry open to exit open and subtract SPY's simple return over the same endpoints. Express excess return in percentage points. Use the previously proposed adjusted-return proxy subject to the data audit.

| Priority | Metric | Definition |
| --- | --- | --- |
| Primary | Average 10-session excess return | Arithmetic mean of measurable signal excess returns |
| Secondary | Median excess return | Median of those same excess returns |
| Secondary | Hit rate | 100 × count(excess return > 0) / measurable signal count; exactly zero is not a hit |
| Secondary | Signal count | Total detected signals, measurable outcomes, and unavailable/pending outcomes reported separately |

Compare **V0: all qualifying strict bullish 10/20 crossovers** with **V1: the subset also satisfying the ATR condition**. Report the metrics side by side, the V1-minus-V0 differences, and V1's retained signal fraction and sample-size reduction. If there are no measurable signals, return undefined metrics and count zero, not fabricated zeros for mean/median/hit rate.

Preserve V0 events even if ATR classification is unavailable. Show those coverage exceptions explicitly; if material, also show V0 on the common ATR-evaluable event set so data availability is not mistaken for the filter's effect. Keep the headline all-V0 results. Missing or immature outcomes do not erase signal records. No inclusion decision may depend on whether the later return is attractive.

The fixed approximately 50-stock universe and most recent 12-month evaluation constraint remain. Actual universe, dates, and data settings are still pending; no evaluation window is selected from performance. Preserve the prior full-containment window convention unless the user changes it.

### Interpretation commitments before results

Do not label V1 “better” solely because one metric improves. Assess the primary mean alongside median, hit rate, and signal retention; describe disagreements or tradeoffs rather than collapsing them into a success claim. No statistical significance threshold or minimum effect size is invented here.

Check whether an apparent difference is concentrated in a few stocks, sectors, or dates. Report counts and excess-return contributions by stock, sector where a documented mapping is available, and signal date, with calendar-month summaries. An unavailable sector mapping is a disclosed limitation, not grounds to add a new vendor silently or claim sector robustness. These are diagnostic breakdowns, not a search for subgroups to keep.

V1 is nested within V0, so they are not independent samples. Outcomes can overlap in time and share stock, sector, and market exposures. Do not use naive independent-observation claims, compound overlapping cohort returns into a strategy curve, optimize thresholds after results, or claim statistical proof or a validated trading edge from one year. Retain negative, mixed, and inconclusive outcomes.

Conceptual weaknesses identified in advance:

- A single prior volatility spike can set a high maximum, making later normalization look like meaningful contraction.
- ATR% can decline because price rises, even if absolute ATR does not decline; the filter is not a pure measure of shrinking absolute trading ranges.
- A low current ratio relative to a maximum does not require a steady or sustained contraction. Today's ratio can even be rising while still meeting the threshold.
- Smoothed ATR can lag changes; the crossover day's range can affect whether the filter qualifies at that same close.
- The filter may remove informative events, reduce an already sparse sample, or change stock/sector/date composition rather than add general predictive information.
- Crossover lag, universe-selection bias, retrospective data revisions, overlapping outcomes, and omitted execution costs remain relevant.

### Next infrastructure and stage boundary

Next authorized work will need the user's fixed ticker list; daily stock and SPY OHLCV plus adjustment/corporate-action information; adequate pre-window history; a frozen 12-month window and reproducible data snapshot; a session calendar; minimal pandas/numpy calculations; separate signal and forward-outcome tables; and checks for warm-up, prior-window exclusion, equality, timestamps, alignment, and coverage. Sector-concentration diagnostics need a documented sector mapping. Keep the approved simple stack and explain any proposed additions first.

No pipeline is needed to establish these equations. None was implemented. No historical outcomes were calculated or inspected. Stop after this preregistration and wait for the user's next instruction.

## 2026-09-08 — Infrastructure implementation and validation, no performance review

Status: the user authorized market-data acquisition, signal/outcome implementation, and automated validation. Those tasks are complete. Historical outcomes were calculated and saved as explicitly permitted, but their values were not displayed, summarized, compared, or interpreted. No legitimate V0-versus-V1 performance comparison has yet occurred. Pipeline freeze and that comparison remain a later human decision.

### Exact fixed universe

AAPL, MSFT, NVDA, AMZN, GOOGL, META, AVGO, AMD, ORCL, CRM, JPM, BAC, GS, MS, V, MA, XOM, CVX, COP, SLB, CAT, GE, RTX, ETN, HON, DE, WMT, COST, HD, MCD, NKE, SBUX, LLY, UNH, JNJ, ABBV, MRK, NFLX, DIS, T, VZ, TSLA, QCOM, TXN, IBM, AMAT, MU, LOW, PEP, KO.

All 50 user-supplied symbols are retained, unique, and separate from benchmark SPY. This is a fixed human-selected experimental universe, not a point-in-time historical S&P 500 membership list. Today's selection can embed survivorship, liquidity, sector, and hindsight biases. Results will be conditional on these names and dates, not representative evidence about all historical U.S. stocks.

### Snapshot and evaluation dates frozen before acquisition

- History request: 2025-03-08 through 2026-09-08; exclusive yfinance end 2026-09-09.
- Expected sessions: 2025-03-10 through 2026-09-08, 377 sessions. The acquisition began after the September 8 regular close.
- Evaluation window: 2025-09-08 through 2026-09-08 inclusive, 252 sessions. Pre-evaluation history: 125 sessions, more than the required SMA/ATR/contraction initialization.
- Under the full-containment convention, the last signal date with a mature t+11 endpoint is 2026-08-21. The final 11 session dates retain pending outcomes, not zero returns. No future data is available or fabricated.
- Expected dates were established independently from weekdays and the bounded NYSE holiday list, then compared with every stock and SPY. Half days remain sessions. Calendar sources: [NYSE/ICE 2025–2027 announcement](https://ir.theice.com/press/news-details/2024/NYSE-Group-Announces-2025-2026-and-2027-Holiday-and-Early-Closings-Calendar/default.aspx), [NYSE hours/calendar](https://www.nyse.com/trade/hours-calendars).

### Data source, adjustments, and implementation

Used installed Python 3.13.2, yfinance 0.2.66, pandas 2.3.3, and numpy 2.3.3. Direct dependencies are pinned in requirements.txt. No technical-analysis package, ML, optimization framework, or research database was introduced. Tests use the Python standard library's unittest.

Yahoo history is requested daily with auto_adjust=False, back_adjust=False, actions=True, repair=False, keepna=True, prepost=False, rounding=False. Retain the vendor OHLCV, Adj Close, and available action columns. Apply factor = Adj Close / Close consistently to ALL four OHLC fields in a separate calculation copy. This matches auto_adjust=True's price transformation in the installed yfinance version, verified by reading its local auto_adjust function: adjusted Open/High/Low are scaled and adjusted Close equals Adj Close. No adjusted Close/unadjusted High-Low mixing occurs. Volume/actions are not scaled by the price factor. Source: [versioned yfinance adjustment implementation](https://github.com/ranaroussi/yfinance/blob/0.2.66/yfinance/utils.py).

The vendor snapshot is not described as exchange-original raw prices: Yahoo may already incorporate splits and can revise history. Adjusted opening-price ratios are the preregistered total-return proxy, not a cash-dividend portfolio model or proof of point-in-time availability. The audit limitation remains explicit.

Created src/, data/, output/, tests/, requirements.txt, .gitignore, and PIPELINE.md. The latter documents reproducible commands, output schemas, data settings, timing, exceptions, and source attribution. README.md, START_HERE.md, and SOCRATES_MODE.md remain deferred.

SMA10/20, strict crossover equality behavior, Wilder ATR14 mean seed/recurrence, ATR/Close normalization, shifted prior-20 maximum, inclusive 0.80 threshold, and V1 conjunction follow the frozen equations. SMA and ATR missing-history conditions remain nullable rather than silently becoming negative signals. ATR initialization starts at the frozen data boundary and resets after unavailable bars. No stop, short signal, optimization, or ranking score was added.

Signal generation admits only High, Low, Close. The separate outcome module uses aligned stock/SPY Open series: t+1 entry, t+11 exit, identical dates, ten trading intervals. Return fields are saved as fractions. Outcome and event files were written without inspecting their historical return values. There is no performance-summary command in this stage.

Each vendor file has a retrieval timestamp and hash. The completed manifest records configuration, versions, and SHA-256 hashes for source, tests, data, and output files. Existing completed outputs cannot be overwritten by the pipeline command. Saved vendor responses are reused on resume. Data/output/cache directories are gitignored; this does not assert permission to redistribute Yahoo data. No machine-specific paths or credentials were added to public documentation.

### Technical issues and transparent data exception

1. **Restricted network:** the first attempt failed through the environment's refusing proxy for AAPL, MSFT, and NVDA and stopped early. These were transport failures, not evidence of unavailable stocks. Authorized execution with network access restored downloaded all 51 instruments without changing source or parameters. The project-local yfinance cache avoids reliance on external cache permissions; yfinance's incidental cookie/timezone cache is not our research database.
2. **KO inconsistent bar:** the initial quality gate stopped before outcomes because KO's 2026-09-08 vendor Open was below its reported Low. A separate direct Yahoo recheck returned the same discrepancy. Original and recheck responses were preserved. No auto-repair, replacement ticker, revised threshold, or shifted date was used.
3. **Missing-data handling made explicit:** the calculation copy quarantines the entire inconsistent KO OHLCV row as unavailable, retaining its place in the calendar. This operationalizes the preregistered invalid/missing-data rule; it is not a corrected price claim. It can make the current signal or an endpoint-dependent historical label unavailable, but cannot remove an unattractive return selectively. The software can finish while the report flags data_exceptions_require_review=true. Human review of this exception is required before claiming a clean snapshot or approving the first comparison.

### Validation evidence — no performance statistics

- All 50 stocks and SPY downloaded: **51/51**; no substituted or failed tickers after the network retry.
- **377 dates per instrument**, zero missing vendor session rows, zero duplicate dates, and zero zero-volume rows. All dates match the independently specified session calendar.
- **49 stocks plus SPY fully clean** under the checks. KO is retained and usable apart from the one quarantined session. No additional invalid bars were identified.
- Initial evaluation warm-up complete for all 50 stocks.
- **20 synthetic automated tests passed.** Coverage includes exact universe size, strict crossover and equality, SMA windows, Wilder seed/recurrence, overnight gaps, prior-20 exclusion/expiration, threshold equality, a positive V1 synthetic example, subset membership, prefix causality, future mutation, missing-data reset, outcome-column isolation, next-open and t+11 arithmetic, matched SPY dates, missing/pending endpoints, consistent OHLC adjustment, and calendar/data-quality checks.
- Actual-data invariant checks passed for every stock: V1 subset of V0, prefix invariance at several cutoffs, outcome-column isolation, first-evaluation warm-up, aligned endpoint dates and exactly ten entry-to-exit intervals. These checks do not inspect or summarize investment performance.
- The first strict data build failed on KO and generated no outcomes. After the documented quarantine handling was implemented, the final infrastructure build completed. This engineering failure and resolution are retained rather than hidden.

Evidence artifacts: output/pipeline_2026-09-08/data_quality.json and output/pipeline_2026-09-08/manifest.json. They contain quality/provenance, not a mean, median, hit rate, or V0/V1 return comparison. No signal counts are needed for the stage report.

### What remains before the first legitimate comparison

The pipeline is implemented and validated, with an explicit KO data exception. The next human decision is whether to accept the documented quarantine for the frozen snapshot or resolve that bar before freezing the pipeline. This stage does not silently choose a different as-of date or replace the original snapshot. Sector-concentration analysis still needs a documented sector mapping; no sector assignments were inferred or fetched here. Any such preparatory additions must precede interpretation and be recorded.

Even after approval, one recent year, overlapping events, selected survivors, retrospective adjustments, opening-price execution assumptions, and omitted costs limit the evidence. Passing software checks does not establish a trading edge.

Stop: implementation and validation stage complete. No V0/V1 performance report or comparison was run. Wait for the user's instruction to freeze and proceed.

## 2026-09-08 — KO resolved, sectors fixed, infrastructure release 1 frozen

Authority: the human researcher explicitly instructed resolution of KO using objective Yahoo evidence if possible, fixed diagnostic sectors, a full infrastructure freeze, and final validation before any performance review. This stage is complete. No research parameter was changed, and no historical return statistic was inspected or summarized.

### KO investigation and mechanical resolution

Affected ticker/date: **KO, 2026-09-08**. The retained daily response reports Open [HISTORICAL YAHOO VALUE NOT DISTRIBUTED] and Low [HISTORICAL YAHOO VALUE NOT DISTRIBUTED]. The opening price below the daily low violates the OHLC ordering constraint. All values are finite and positive; volume is positive. Close and Adj Close both equal 88.36000061035156, making the adjustment factor 1. Dividends and Stock Splits on that row are zero. The contradiction is present in the vendor response before any adjustment, so it is not caused by mixing adjusted and unadjusted prices, a zero/missing value, or our arithmetic.

A new Yahoo daily query still returned the same inconsistent field. A Yahoo one-minute regular-session query supplied **390 contiguous expected minutes from 09:30 through 15:59 Eastern**, no missing/duplicate minutes, and valid OHLC bounds throughout. The minimum minute Low is **[HISTORICAL YAHOO VALUE NOT DISTRIBUTED]**, matching both the daily Open and first minute Open/Low. This same-source evidence supports a mechanical replacement of the inconsistent daily Low with the observed regular-session minimum.

**Resolution applied:** replace KO's 2026-09-08 Low only, from [HISTORICAL YAHOO VALUE NOT DISTRIBUTED] to [HISTORICAL YAHOO VALUE NOT DISTRIBUTED], before the consistent OHLC adjustment. Do not alter Open, High, Close, Adj Close, Volume, or corporate-action fields. The original daily snapshot remains untouched. reference/data_corrections.json records the exact old/new values, rule, evidence files, source URL, retrieval timestamp, and scope. Exact-original-value verification prevents applying this patch to an unexpected changed source. Frozen hashes include the original snapshot and supporting minute/daily evidence.

Classification: an apparent **Yahoo daily OHLC field inconsistency**, with a correction supported by Yahoo's complete regular-session minute record. We do not claim to have diagnosed the upstream vendor mechanism or independently certified the exchange low. Minute aggregate Close and Volume differ from the daily fields, so they were not used to replace the entire daily bar; session/auction coverage can differ. The correction is limited to the demonstrably inconsistent Low corroborated by daily Open and minute Low.

KO remains in the exact 50-stock universe. With the correction, all KO rows pass the checks; there are **zero remaining quarantined observations**. Earlier quarantine outputs are retained as history and are not the frozen calculation inputs. The authoritative corrected frames are output/frozen_2026-09-08/adjusted/. No discretion based on outcomes, alternate stock, shifted window, or research-parameter change was involved.

### Fixed sector mapping

Created **reference/sectors.csv**, exactly one row for each of the 50 stocks. Yahoo company profiles were accessed for sector classification only, retaining source label, normalized label, URL, and retrieval timestamp. No quote, return, valuation, target, or financial-statistic fields were inspected for research or retained in the mapping.

Normalize Yahoo labels to broad GICS-style categories: Technology → Information Technology; Financial Services → Financials; Healthcare → Health Care; Consumer Cyclical → Consumer Discretionary; Consumer Defensive → Consumer Staples. Communication Services, Industrials, and Energy retain their names. These are fixed present-day diagnostic labels, not official licensed GICS classification history or point-in-time sector membership.

Coverage: Information Technology 12; Communication Services 6; Consumer Discretionary 7; Consumer Staples 4; Financials 6; Health Care 5; Industrials 6; Energy 4. Total 50, with no duplicate/missing ticker. Visa and Mastercard are Financials; Alphabet and Meta are Communication Services. Each row links its Yahoo profile as the source.

Sector data is attached only after signal and outcome calculation, for later diagnostics. A test changes sector labels arbitrarily and confirms signals remain identical. The metadata does not filter, score, rank, or otherwise alter V0 or V1.

### Infrastructure freeze

Created **FROZEN_SPECIFICATION.md**, release 1, with exact plain-English and mathematical definitions for universe, SPY, Yahoo source and settings, adjustment convention, SMA10/20, strict crossover, Wilder ATR14 seed/recurrence, ATR/Close, prior-20 maximum excluding today, 0.80 contraction, same-date V1 conjunction, close signal timing, t+1 Open entry, t+11 Open exit, stock-minus-SPY outcome, evaluation window, per-signal metrics, sector mapping, KO correction, missingness, and interpretation limits.

Its machine-readable settings block is tested against every uppercase src/config.py setting. Metrics are frozen as definitions/metadata for the later evaluator; this stage contains no performance-metric calculation or reporting function. The primary remains per-signal mean excess return; median, strictly positive hit rate, counts, reduction in sample size, and concentration remain the secondary/contextual framework. No optimization or metric shopping is permitted.

Created **FROZEN_LOCK.json**, covering 120 files by SHA-256, including source, tests, specification, dependency versions, reference metadata, original vendor data, retrieval metadata, and KO evidence. Frozen build verifies these hashes and the specification before doing calculations. Preparation/acquisition are disabled after freeze; a rebuild uses the locked snapshot. Corrected frames are written into the new output rather than overwriting historical adjusted files. Any future methodology/data/sector change requires an explicitly authorized new version; do not regenerate the lock merely to bypass a mismatch. This is local audit/change detection, not external tamper-proof certification.

The source snapshot retains its original 18-month range and the evaluation window remains **2025-09-08 through 2026-09-08**, unchanged. No previously preregistered parameter was altered. The human has authorized this freeze; there is no remaining KO or sector decision before the later performance stage.

### Final validation

- Reran **all 26 automated tests: passed**, with no skips in this environment. Added tests cover the single-cell KO correction, exact original-value matching, complete Yahoo minute evidence, correction consistency after adjustment, sector coverage/provenance, sector isolation, specification/config equivalence, and frozen hashes.
- Reran the full pipeline from the retained source snapshot into **output/frozen_2026-09-08/**. All **50 stocks and SPY** processed successfully across **377 aligned sessions**. Complete instruments: **51/51**; missing session rows: zero; remaining quarantines: zero; data_exceptions_require_review=false. Initial warm-up is sufficient for every stock.
- Confirmed V1 is contained in V0 and is a **proper subset** in this snapshot: at least one observed V0 event fails the filter. This is a Boolean membership check, not a count/return comparison. No performance statistic was needed or printed.
- Causal prefix checks, future-mutation tests, outcome-column isolation, sector isolation, identical SPY endpoint dates, and exactly ten entry-to-exit intervals all passed. The implementation and locked specification agree. These establish calculation timing and isolation, not perfect point-in-time vendor history.
- Only data-quality reports, source code, mapping metadata, KO market-data evidence, and file hashes were inspected. Historical outcome/event files were written but their return fields were not displayed, summarized, compared, or interpreted. The first legitimate performance comparison remains unperformed.
- Final quality and provenance: output/frozen_2026-09-08/data_quality.json and output/frozen_2026-09-08/manifest.json. Final frozen-file verification returned true.

### Remaining structural limitations and next decision

Fixed-universe selection/survivorship, one recent year, current static sector labels, overlapping/dependent observations, vendor revisions, source-derived Low reconstruction, idealized opening-price execution, and omitted transaction costs remain. The ATR% filter may still respond to an old spike or a changing price denominator rather than durable contraction. Passing infrastructure checks supplies no evidence of an investment edge.

**V0 and V1 infrastructure are now frozen and ready for the first legitimate comparison when the user authorizes that next stage.** Stop here; no returns or performance summaries are revealed.


## 2026-09-08 — FIRST legitimate performance comparison: MIXED

User authorization: Prompt 007. Complete first-pass report follows; frozen definitions and inputs were not changed. Earlier statements that no performance had been viewed describe earlier stages and are superseded by this explicitly authorized evaluation.

### First observed results

Observed on 2026-09-08. **Descriptive classification: MIXED.**

The ATR filter improves the average excess return, but worsens the median and hit rate, removes 82.83% of completed signals, and leaves a result sensitive to a few outcomes and sector composition. It does not establish a validated trading strategy, statistical proof, or a recommendation to trade.

#### Population and integrity

Used the unchanged frozen 2025-09-08 through 2026-09-08 evaluation window and the corrected, locked Yahoo snapshot. Only complete next-open through t+11-open outcomes are included. Latest possible mature signal date is 2026-08-21. V0 has 343 detected events: 332 completed and 11 pending. V1 has 62 detected events: 57 completed and 5 pending. No missing-endpoint events and no unknown ATR classifications occur among evaluated events. Pending observations are retained in the signals file and excluded from statistics, never treated as zero or failures.

Before evaluation, verified all frozen-file hashes and saved-output hashes. Independently recomputed saved labels from the frozen adjusted stock/SPY endpoint opens and checked dates, differences, duplicates, sectors, and evaluation inclusion. Group counts/contributions reconcile to the totals, and mean excess equals mean stock minus mean benchmark. Three new synthetic reporting tests passed. Frozen parameters, sector mapping, source data, source code, tests and specification remained unchanged. This new evaluator lives separately in analysis/ and is not V2.

Additional reporting conventions were stated before the first calculation: equal weight per completed stock-signal; linear-interpolated percentiles; sample standard deviation (ddof=1); strictly positive returns for hit/positive-absolute rates; best/worst reported for both excess and stock returns. These descriptive additions were explicitly requested in this stage and do not change the frozen primary metric. matplotlib 3.10.7, already installed, was used only for the requested static charts. CSVs use the existing pandas implementation; no workbook or strategy framework was introduced.

#### Complete headline results

Return columns ending in pct are percentages. Excess-return columns ending in pp are percentage points. Hit/positive-return rates are percentages. Counts are integers. Statistics below are displayed to six decimals; CSV outputs retain 15 significant digits. Blank CSV statistics mean unavailable, not zero.

| Metric | V0 | V1 |
| --- | --- | --- |
| signal_count | 332.000000 | 57.000000 |
| average_stock_return_pct | 0.356529 | 0.629587 |
| average_spy_return_pct | 0.745371 | 0.274119 |
| average_excess_return_pp | -0.388842 | 0.355467 |
| median_excess_return_pp | -0.259629 | -0.456418 |
| hit_rate_pct | 48.493976 | 47.368421 |
| positive_stock_return_pct | 50.903614 | 49.122807 |
| q25_excess_return_pp | -4.791084 | -4.609197 |
| q75_excess_return_pp | 3.626756 | 3.979292 |
| std_excess_return_pp | 7.070080 | 7.860473 |
| best_excess_return_pp | 43.096432 | 28.908575 |
| worst_excess_return_pp | -30.536809 | -18.308160 |
| best_stock_return_pct | 45.009966 | 31.048371 |
| worst_stock_return_pct | -31.060655 | -19.645297 |
| sum_excess_return_pp_not_portfolio | -129.095427 | 20.261630 |
| detected_signals | 343.000000 | 62.000000 |
| pending_signals | 11.000000 | 5.000000 |
| missing_outcome_signals | 0.000000 | 0.000000 |
| atr_classification_unavailable | 0.000000 | 0.000000 |

#### V1 minus V0

| average_excess_return_pp | median_excess_return_pp | hit_rate_pct | signals_removed | signal_reduction_pct | signal_retention_pct |
| --- | --- | --- | --- | --- | --- |
| 0.744309 | -0.196789 | -1.125555 | 275 | 82.831325 | 17.168675 |

The mean improves by +0.744309 pp; the median worsens by −0.196789 pp and hit rate by −1.125555 percentage points. The filter retains 17.168675% of completed V0 signals. On detected signals including pending events, it retains 62 of 343 and removes 281 (81.924198%); the primary count comparison is based on completed outcomes only.

V1's average stock return increases only about 0.273057 pp, while its matched SPY average is about 0.471251 pp lower. SPY's two averages differ because the filter selects different stock-signal dates. These are signal-weighted benchmark returns, not SPY's return over the whole year; the difference helps explain the larger excess-return change.

#### Distribution and individual outcomes

V0's middle 50% spans −4.791084 to +3.626756 pp; V1's spans −4.609197 to +3.979292 pp. Both medians are negative. V1's dispersion is larger (7.860473 versus 7.070080 pp sample standard deviation). The mean therefore does not describe a typical successful signal or a uniform distributional improvement.

| version | outcome | ticker | signal_date | entry_date | exit_date | stock_return_pct | spy_return_pct | excess_return_pp |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| V0 | best_excess | AMD | 2025-09-25 | 2025-09-26 | 2025-10-10 | 45.009966 | 1.913534 | 43.096432 |
| V0 | worst_excess | IBM | 2026-07-06 | 2026-07-07 | 2026-07-21 | -31.060655 | -0.523845 | -30.536809 |
| V0 | best_stock | AMD | 2025-09-25 | 2025-09-26 | 2025-10-10 | 45.009966 | 1.913534 | 43.096432 |
| V0 | worst_stock | IBM | 2026-07-06 | 2026-07-07 | 2026-07-21 | -31.060655 | -0.523845 | -30.536809 |
| V1 | best_excess | QCOM | 2026-04-16 | 2026-04-17 | 2026-05-01 | 31.048371 | 2.139796 | 28.908575 |
| V1 | worst_excess | MU | 2026-03-18 | 2026-03-19 | 2026-04-02 | -19.645297 | -1.337138 | -18.308160 |
| V1 | best_stock | QCOM | 2026-04-16 | 2026-04-17 | 2026-05-01 | 31.048371 | 2.139796 | 28.908575 |
| V1 | worst_stock | MU | 2026-03-18 | 2026-03-19 | 2026-04-02 | -19.645297 | -1.337138 | -18.308160 |

The best V1 event is QCOM's 2026-04-16 signal, +28.908575 pp excess return. Removing that single event from V1 as an influence diagnostic changes its mean to −0.154410 pp (56 events). The reported headline remains +0.355467 pp with all 57 events. This diagnostic does not authorize discarding the event or selecting rules around it. Large positive and negative events warrant independent data review before interpreting them as economic effects.

Excess-return empirical distributions (generated chart not distributed; local path: `output/v0_v1_distribution.png`)

The curves show cumulative shares on their full observed ranges, without a fitted distribution or tail trimming. V0 includes V1; the curves are not independent samples.

#### Monthly signal cohorts

| signal_month | V0_signal_count | V0_average_excess_return_pp | V1_signal_count | V1_average_excess_return_pp |
| --- | --- | --- | --- | --- |
| 2025-09 | 17 | 3.380385 | 1 | 17.998463 |
| 2025-10 | 40 | -0.764458 | 0 | n/a |
| 2025-11 | 20 | 0.269904 | 2 | -0.713264 |
| 2025-12 | 39 | 1.524051 | 16 | 1.054244 |
| 2026-01 | 30 | 3.015318 | 7 | 0.039973 |
| 2026-02 | 18 | -2.937221 | 1 | 4.452933 |
| 2026-03 | 21 | -2.255174 | 5 | -3.702202 |
| 2026-04 | 39 | -2.520774 | 6 | 1.708864 |
| 2026-05 | 25 | -0.094103 | 3 | -0.418153 |
| 2026-06 | 23 | -0.036022 | 0 | n/a |
| 2026-07 | 30 | -2.789023 | 3 | 5.235476 |
| 2026-08 | 30 | -0.862956 | 13 | -1.854238 |
| 2026-09 | 0 | n/a | 0 | n/a |

September 2025 is a partial beginning month. August 2026 ends at the last mature signal date. September 2026 has no completed outcomes. A zero count is not a zero-return month. V1 has a higher monthly mean in only 4 of the 10 months with completed observations in both groups. Several V1 month counts are just 1–3; do not treat these as reliable monthly effects.

The largest positive V1 contribution months are September 2025 (one signal, about +17.998463 pp summed excess) and December 2025 (16 signals, about +16.867907 pp summed excess). Together their summed contribution exceeds V1's net total because other months offset it. Excluding those same two months from both groups, solely as a concentration diagnostic, leaves V1 at −0.365119 pp (40 signals) and V0 at −0.891304 pp (276 signals). Thus the positive sign of V1's mean is sensitive to these months, but its relative mean advantage persists in that diagnostic.

Removing any single month leaves V1's mean above V0's. Its positive mean becomes very small when September 2025, December 2025, or July 2026 is individually omitted. This supports caution about the level and tails, not a claim that one month alone explains the entire relative mean difference.

Monthly cohorts (generated chart not distributed; local path: `output/v0_v1_monthly.png`)

#### Sector consistency

| sector | V0_signal_count | V0_average_excess_return_pp | V1_signal_count | V1_average_excess_return_pp |
| --- | --- | --- | --- | --- |
| Communication Services | 38 | -2.074835 | 7 | -1.276690 |
| Consumer Discretionary | 47 | -0.526415 | 5 | 0.632160 |
| Consumer Staples | 28 | -1.696764 | 2 | -5.938564 |
| Energy | 25 | 1.686682 | 6 | 5.394960 |
| Financials | 33 | 0.850125 | 2 | -0.187888 |
| Health Care | 35 | 0.536411 | 2 | -0.658872 |
| Industrials | 42 | -0.839305 | 6 | -4.808591 |
| Information Technology | 84 | -0.377924 | 27 | 1.336670 |

Information Technology contributes 27 of 57 V1 signals (47.368421%), compared with 84 of 332 V0 signals (25.301205%). Excluding that same sector from both groups changes the remaining means to V1 −0.527616 pp (30 signals) versus V0 −0.392540 pp (248 signals), reversing the mean ordering by −0.135076 pp. The apparent aggregate advantage is therefore sensitive to IT composition.

Energy has the strongest V1 sector mean, +5.394960 pp, from only six events. Without Energy, V1's mean becomes −0.237414 pp versus V0 −0.557858 pp: its positive sign disappears, although the relative advantage remains. Information Technology and Energy provide positive contributions that offset substantial negative contributions elsewhere, notably Industrials. V1 sector samples range from 2 to 27; even the largest is limited and dependent. All sector rows are shown, with sparse samples explicitly treated as descriptive only.

#### Stock concentration

Most V0 signals: NVDA, AVGO, ETN, MRK and IBM tie at nine each. Most V1 signals: AMD, QCOM and MU tie at four each; IBM and AMAT follow at three each. Counts below include only complete outcomes.

Largest positive summed excess contributions: V0 — AMD +60.150191 pp, AMAT +30.953553 pp, QCOM +23.270164 pp, XOM +20.731276 pp, MU +17.561763 pp. V1 — QCOM +31.241333 pp, AMD +19.166693 pp, XOM +18.708027 pp, TSLA +11.803365 pp, CVX +8.316858 pp.

Largest negative summed excess contributions: V0 — IBM −46.305842 pp, ORCL −40.597093 pp, META −39.048234 pp, WMT −27.768010 pp, AVGO −26.183430 pp. V1 — RTX −15.776880 pp, NKE −10.309093 pp, META −9.151811 pp, MSFT −9.058891 pp, CAT −8.150876 pp.

These sums are additive diagnostics over overlapping events, NOT portfolio returns or compounded wealth. A stock's contribution to the overall mean is its summed excess divided by the whole strategy sample count. Removing QCOM as a diagnostic makes V1's mean −0.207164 pp; removing AMD or XOM leaves means of about +0.020659 or +0.028247 pp. These results identify influence, not stocks to drop.

The largest V1 count on any one signal date is three, occurring on 2026-01-05, 2026-08-17 and 2026-08-21. Low same-date counts do not make overlapping ten-interval outcomes independent.

The following complete stock table retains every stock, including those with no V1 signals. Zero summed contribution for an empty group is an additive identity; its mean remains unavailable.

| ticker | V0_signal_count | V1_signal_count | V0_average_excess_return_pp | V1_average_excess_return_pp | V0_sum_excess_return_pp_not_portfolio | V1_sum_excess_return_pp_not_portfolio |
| --- | --- | --- | --- | --- | --- | --- |
| AAPL | 4 | 0 | 0.295129 | n/a | 1.180517 | 0.000000 |
| MSFT | 8 | 2 | -3.029579 | -4.529445 | -24.236635 | -9.058891 |
| NVDA | 9 | 2 | -1.090017 | 1.744502 | -9.810155 | 3.489003 |
| AMZN | 7 | 2 | 1.096656 | 0.833264 | 7.676589 | 1.666527 |
| GOOGL | 5 | 1 | 0.880066 | 2.632197 | 4.400330 | 2.632197 |
| META | 8 | 2 | -4.881029 | -4.575906 | -39.048234 | -9.151811 |
| AVGO | 9 | 2 | -2.909270 | -1.534969 | -26.183430 | -3.069937 |
| AMD | 6 | 4 | 10.025032 | 4.791673 | 60.150191 | 19.166693 |
| ORCL | 7 | 2 | -5.799585 | -3.494713 | -40.597093 | -6.989427 |
| CRM | 6 | 0 | -2.471211 | n/a | -14.827266 | 0.000000 |
| JPM | 5 | 0 | -0.704174 | n/a | -3.520869 | 0.000000 |
| BAC | 5 | 0 | 1.559637 | n/a | 7.798186 | 0.000000 |
| GS | 5 | 1 | 0.701851 | 1.205253 | 3.509256 | 1.205253 |
| MS | 5 | 1 | 0.961049 | -1.581030 | 4.805243 | -1.581030 |
| V | 6 | 0 | 0.986202 | n/a | 5.917214 | 0.000000 |
| MA | 7 | 0 | 1.363587 | n/a | 9.545108 | 0.000000 |
| XOM | 5 | 2 | 4.146255 | 9.354014 | 20.731276 | 18.708027 |
| CVX | 7 | 1 | 2.102272 | 8.316858 | 14.715905 | 8.316858 |
| COP | 7 | 1 | 0.812308 | 3.182668 | 5.686155 | 3.182668 |
| SLB | 6 | 2 | 0.172287 | 1.081102 | 1.033725 | 2.162204 |
| CAT | 7 | 2 | 2.328843 | -4.075438 | 16.301900 | -8.150876 |
| GE | 6 | 0 | 0.732830 | n/a | 4.396983 | 0.000000 |
| RTX | 6 | 1 | -1.972124 | -15.776880 | -11.832742 | -15.776880 |
| ETN | 9 | 2 | -0.664587 | -2.362867 | -5.981283 | -4.725734 |
| HON | 6 | 1 | -3.993689 | -0.198058 | -23.962136 | -0.198058 |
| DE | 8 | 0 | -1.771690 | n/a | -14.173521 | 0.000000 |
| WMT | 7 | 1 | -3.966859 | -6.867589 | -27.768010 | -6.867589 |
| COST | 6 | 0 | -2.395585 | n/a | -14.373510 | 0.000000 |
| HD | 7 | 0 | -0.904310 | n/a | -6.330173 | 0.000000 |
| MCD | 7 | 0 | 0.271637 | n/a | 1.901462 | 0.000000 |
| NKE | 6 | 1 | -3.355270 | -10.309093 | -20.131617 | -10.309093 |
| SBUX | 8 | 0 | 0.976961 | n/a | 7.815685 | 0.000000 |
| LLY | 7 | 0 | 2.205997 | n/a | 15.441982 | 0.000000 |
| UNH | 5 | 1 | 3.485818 | 4.452933 | 17.429090 | 4.452933 |
| JNJ | 7 | 0 | -0.502225 | n/a | -3.515574 | 0.000000 |
| ABBV | 7 | 1 | -2.691253 | -5.770677 | -18.838769 | -5.770677 |
| MRK | 9 | 0 | 0.917517 | n/a | 8.257653 | 0.000000 |
| NFLX | 7 | 0 | -3.631147 | n/a | -25.418032 | 0.000000 |
| DIS | 7 | 1 | -0.785737 | 4.139613 | -5.500158 | 4.139613 |
| T | 5 | 2 | -3.269342 | -3.282805 | -16.346711 | -6.565611 |
| VZ | 6 | 1 | 0.511515 | 0.008786 | 3.069089 | 0.008786 |
| TSLA | 5 | 2 | -1.189628 | 5.901682 | -5.948140 | 11.803365 |
| QCOM | 6 | 4 | 3.878361 | 7.810333 | 23.270164 | 31.241333 |
| TXN | 7 | 1 | -0.414481 | -6.334127 | -2.901365 | -6.334127 |
| IBM | 9 | 3 | -5.145094 | -0.587377 | -46.305842 | -1.762132 |
| AMAT | 7 | 3 | 4.421936 | 1.977574 | 30.953553 | 5.932721 |
| MU | 6 | 4 | 2.926961 | 0.868715 | 17.561763 | 3.474859 |
| LOW | 7 | 0 | -1.389330 | n/a | -9.725311 | 0.000000 |
| PEP | 8 | 1 | -0.582262 | -5.009539 | -4.658094 | -5.009539 |
| KO | 7 | 0 | -0.101396 | n/a | -0.709773 | 0.000000 |

#### Classification and limits

**MIXED.** The primary mean improves, but the median, hit rate, absolute-positive rate and sample size move unfavorably, while dispersion increases. The favorable mean depends on influential events and sector composition. No numerical economic-materiality threshold or statistical test was preregistered, so neither significance nor a validated edge is claimed.

The experiment uses one recent year, a selected fixed universe, retrospective Yahoo prices, one documented source repair, static sector labels, idealized opening prints, and gross outcomes without execution costs. V1 is a nested subset of V0 and events overlap. The 57 V1 signals are not 57 independent trials. The same period is now observed and must not later be described as untouched out-of-sample evidence.

Next proposed stage, not run here: independently audit influential price events, then challenge whether the relative result survives comparisons that account for sector/date composition and dependence. Keep the frozen signal unchanged. No V2, threshold search, parameter changes, or recommendation to trade.

#### Reproducibility and output files

Evaluator: analysis/first_comparison.py. Synthetic reporting tests: analysis/test_first_comparison.py. Existing first-pass outputs cannot be overwritten by its command. Primary CSVs: output/v0_v1_summary.csv, output/v0_v1_monthly.csv, output/v0_v1_sector.csv, output/v0_v1_signals.csv. Additional diagnostics: output/v0_v1_difference.csv, output/v0_v1_stocks.csv, output/v0_v1_dates.csv, output/v0_v1_extremes.csv, output/v0_v1_influence.csv. The signals file retains pending events, membership flags, inclusion flags, and original fractional return columns. Aggregated CSV return units are explicitly pct/pp.

The evaluation manifest records the timestamp, frozen manifest/lock hashes, evaluator hash, percentile/dispersion conventions, and verification status. FIRST_PASS_RESULTS.md and the appended research-log entry provide a public-safe narrative and complete stock/month/sector results; vendor and generated data files remain gitignored under the existing publication policy.


---

# V1 adversarial robustness review

Date: 2026-09-08. **Overall classification: FRAGILE.** The official first-pass classification remains **MIXED**, and its 57-event V1 mean remains +0.355467 pp, median −0.456418 pp and hit rate 47.368421%. No parameter, universe, signal, data snapshot or official result was changed. No V2 was created.

The strongest explanation for a positive mean alongside a negative median and sub-50% hit rate is the magnitude of a few right-tail outcomes. The positive sum is a small remainder after large gains and losses offset. Stress tests are descriptive, selected after viewing first-pass results, and cannot supply independent confirmation, causal explanation or corrected significance.

## Methods and data integrity

Use exactly the 57 completed official V1 events, with V0's 332 completed events for execution comparisons. Pending signals remain excluded. Rank best/worst by excess return, with stock, SPY and excess shown separately. Individual event outcomes are equally weighted. All aggregate excess units are percentage points (pp); event CSV return fields retain fractions. Contribution means arithmetic sum of event excess returns, not a compounded or investable portfolio. Percentages of the net sum can exceed 100% because negative contributions offset winners.

The saved first-pass outputs and all frozen hashes passed before and after diagnostics. The original loader independently reconciles all official stock/SPY returns to adjusted endpoint opens. V1 indicators were recomputed over the full frozen histories, and ATR% and qualifying membership checked. All execution alternatives use matching stock/SPY dates and fields. Two new overlap boundary tests and three existing reporting tests passed. This verifies internal arithmetic and provenance, not whether Yahoo's extreme price moves are economically correct; no independent feed, exchange print or event-news audit was performed. The existing KO correction is untouched and KO has zero V1 events.

## 1. Largest winners and losers

Five best and five worst V1 excess-return observations:

| Ticker | Signal | Entry | Exit | Stock % | SPY % | Excess pp |
| --- | --- | --- | --- | --- | --- | --- |
| QCOM | 2026-04-16 | 2026-04-17 | 2026-05-01 | 31.048371 | 2.139796 | 28.908575 |
| AMAT | 2025-09-15 | 2025-09-16 | 2025-09-30 | 18.497042 | 0.498579 | 17.998463 |
| MU | 2026-04-15 | 2026-04-16 | 2026-04-30 | 16.950724 | 1.935639 | 15.015085 |
| MU | 2025-12-08 | 2025-12-09 | 2025-12-23 | 12.855331 | 0.408528 | 12.446803 |
| XOM | 2026-07-14 | 2026-07-15 | 2026-07-29 | 8.704942 | -1.891973 | 10.596915 |
| ETN | 2025-12-11 | 2025-12-12 | 2025-12-29 | -7.683945 | 0.203677 | -7.887621 |
| NKE | 2026-04-27 | 2026-04-28 | 2026-05-12 | -6.787132 | 3.521961 | -10.309093 |
| AMAT | 2026-08-12 | 2026-08-13 | 2026-08-27 | -12.170901 | -0.822073 | -11.348828 |
| RTX | 2026-04-14 | 2026-04-15 | 2026-04-29 | -13.512979 | 2.263900 | -15.776880 |
| MU | 2026-03-18 | 2026-03-19 | 2026-04-02 | -19.645297 | -1.337138 | -18.308160 |

Tail conventions were stated before this diagnostic calculation: ceil(5% × 57) = 3 events (5.263% of the sample). Excluding the best/worst 5% therefore equals excluding three. Winsorization caps those three at the fourth-best/fourth-worst observed excess return. Only excess is capped; synthetic capped stock/SPY metrics are intentionally blank. Also show exclusion of five events for the requested top-five contribution context. The two sides are treated symmetrically; deleting losses predictably improves the average and is not evidence of a better strategy.

| diagnostic | signal_count | average_excess_return_pp | median_excess_return_pp | hit_rate_pct |
| --- | --- | --- | --- | --- |
| official | 57 | 0.355467 | -0.456418 | 47.368421 |
| exclude_best_1 | 56 | -0.154410 | -0.487414 | 46.428571 |
| exclude_best_3 | 54 | -0.771491 | -0.521277 | 44.444444 |
| exclude_best_5 | 52 | -1.244312 | -0.620528 | 42.307692 |
| winsorize_best_5pct_3_events | 57 | -0.075791 | -0.456418 | 47.368421 |
| exclude_worst_1 | 56 | 0.688746 | -0.327238 | 48.214286 |
| exclude_worst_3 | 54 | 1.216583 | -0.094636 | 50.000000 |
| exclude_worst_5 | 52 | 1.613312 | 0.092657 | 51.923077 |
| winsorize_worst_5pct_3_events | 57 | 0.609969 | -0.456418 | 47.368421 |

Removing the best event changes the mean by −0.509877 pp, to −0.154410 pp. Removing the best three changes it by −1.126958 pp, to −0.771491 pp. Capping the best three, rather than deleting them, also makes the mean negative (−0.075791 pp). The downside equivalents are +0.688746 pp after removing the worst one, +1.216583 pp after the worst three, and +0.609969 pp after bottom-tail capping. Tail sensitivity is substantial in both directions.

## 2. Contribution concentration

Net summed V1 excess contribution is +20.261630 pp. Shares below use that net denominator, not gross positive returns:

| best_n | sum_excess_pp | percent_of_net_sum |
| --- | --- | --- |
| 1 | 28.908575 | 142.676453 |
| 3 | 61.922124 | 305.612742 |
| 5 | 84.965842 | 419.343563 |

The best three are QCOM, AMAT and MU; two of those signals are only one session apart (April 15–16, 2026). The three best contribute +61.922124 pp while the remaining 54 contribute −41.660494 pp. One observation contributes more than the entire positive net result. This is strong descriptive evidence of dependence on a few large winners, not proof that those winners are erroneous.

## 3. Month and calendar concentration

| signal_month | signal_count | average_excess_return_pp | sum_excess_return_pp_not_portfolio |
| --- | --- | --- | --- |
| 2025-09 | 1 | 17.998463 | 17.998463 |
| 2025-10 | 0 | n/a | 0.000000 |
| 2025-11 | 2 | -0.713264 | -1.426529 |
| 2025-12 | 16 | 1.054244 | 16.867907 |
| 2026-01 | 7 | 0.039973 | 0.279809 |
| 2026-02 | 1 | 4.452933 | 4.452933 |
| 2026-03 | 5 | -3.702202 | -18.511010 |
| 2026-04 | 6 | 1.708864 | 10.253186 |
| 2026-05 | 3 | -0.418153 | -1.254460 |
| 2026-06 | 0 | n/a | 0.000000 |
| 2026-07 | 3 | 5.235476 | 15.706427 |
| 2026-08 | 13 | -1.854238 | -24.105096 |
| 2026-09 | 0 | n/a | 0.000000 |

December has the most signals (16/57, 28.07%); August has 13/57 (22.81%). Together they account for 50.88% of V1. September's single AMAT event contributes +17.998463 pp (88.83% of the net aggregate), December +16.867907 pp (83.25%), and July +15.706427 pp (77.52%). No single month exclusively supplies the positive result: removing any one month leaves V1 positive. However, removing September and December together leaves −0.365119 pp; V0 with those same months removed is −0.891304 pp. Thus the positive level is fragile while the relative mean advantage survives that particular attack. March and August supply substantial negative contributions.

Five-session windows are descriptive rolling windows, not optimized partitions. Their overlaps mean they must not be added together. Largest examples: December 29–January 5 has seven signals in seven stocks; August 12–18 has seven in seven stocks; August 17–21 has seven in six stocks. Same-date counts peak at three (January 5, August 17 and August 21). The full date and rolling-window files show membership.

The April 15 MU and April 16 QCOM winners hold for nine shared open-to-open intervals. RTX's April 14 loss overlaps those same dates. These are simultaneous exposures, and MU/QCOM share the frozen IT sector; a particular common news catalyst cannot be established from OHLCV and dates alone. Broad market and industry influences can affect several outcomes at once, even after subtracting SPY.

## 4. Sector concentration

| sector | signal_count | average_excess_return_pp | sum_excess_return_pp_not_portfolio |
| --- | --- | --- | --- |
| Communication Services | 7 | -1.276690 | -8.936827 |
| Consumer Discretionary | 5 | 0.632160 | 3.160799 |
| Consumer Staples | 2 | -5.938564 | -11.877128 |
| Energy | 6 | 5.394960 | 32.369758 |
| Financials | 2 | -0.187888 | -0.375777 |
| Health Care | 2 | -0.658872 | -1.317745 |
| Industrials | 6 | -4.808591 | -28.851547 |
| Information Technology | 27 | 1.336670 | 36.090096 |

IT supplies 27/57 events (47.37%) and +36.090096 pp, 178.12% of the net aggregate. Energy supplies six events and +32.369758 pp, 159.76% of net. All other sectors combined contribute −48.198224 pp. Removing IT leaves V1 −0.527616 pp, below V0's corresponding −0.392540 pp. Removing Energy leaves V1 −0.237414 pp, although still above corresponding V0 −0.557858 pp. There is concentration in two favorable sectors, rather than broad sector confirmation. Sector counts of 2–27 are too sparse and dependent to establish sector-specific effects.

## 5. Stock concentration

All 50 frozen stocks are retained below. Zero-event mean is unavailable; a zero sum is only an additive identity. No stock has more than four V1 signals, so every stock mean is descriptive arithmetic, not a reliable estimate of a stock-specific effect.

| ticker | signal_count | average_excess_return_pp | sum_excess_return_pp_not_portfolio |
| --- | --- | --- | --- |
| AAPL | 0 | n/a | 0.000000 |
| MSFT | 2 | -4.529445 | -9.058891 |
| NVDA | 2 | 1.744502 | 3.489003 |
| AMZN | 2 | 0.833264 | 1.666527 |
| GOOGL | 1 | 2.632197 | 2.632197 |
| META | 2 | -4.575906 | -9.151811 |
| AVGO | 2 | -1.534969 | -3.069937 |
| AMD | 4 | 4.791673 | 19.166693 |
| ORCL | 2 | -3.494713 | -6.989427 |
| CRM | 0 | n/a | 0.000000 |
| JPM | 0 | n/a | 0.000000 |
| BAC | 0 | n/a | 0.000000 |
| GS | 1 | 1.205253 | 1.205253 |
| MS | 1 | -1.581030 | -1.581030 |
| V | 0 | n/a | 0.000000 |
| MA | 0 | n/a | 0.000000 |
| XOM | 2 | 9.354014 | 18.708027 |
| CVX | 1 | 8.316858 | 8.316858 |
| COP | 1 | 3.182668 | 3.182668 |
| SLB | 2 | 1.081102 | 2.162204 |
| CAT | 2 | -4.075438 | -8.150876 |
| GE | 0 | n/a | 0.000000 |
| RTX | 1 | -15.776880 | -15.776880 |
| ETN | 2 | -2.362867 | -4.725734 |
| HON | 1 | -0.198058 | -0.198058 |
| DE | 0 | n/a | 0.000000 |
| WMT | 1 | -6.867589 | -6.867589 |
| COST | 0 | n/a | 0.000000 |
| HD | 0 | n/a | 0.000000 |
| MCD | 0 | n/a | 0.000000 |
| NKE | 1 | -10.309093 | -10.309093 |
| SBUX | 0 | n/a | 0.000000 |
| LLY | 0 | n/a | 0.000000 |
| UNH | 1 | 4.452933 | 4.452933 |
| JNJ | 0 | n/a | 0.000000 |
| ABBV | 1 | -5.770677 | -5.770677 |
| MRK | 0 | n/a | 0.000000 |
| NFLX | 0 | n/a | 0.000000 |
| DIS | 1 | 4.139613 | 4.139613 |
| T | 2 | -3.282805 | -6.565611 |
| VZ | 1 | 0.008786 | 0.008786 |
| TSLA | 2 | 5.901682 | 11.803365 |
| QCOM | 4 | 7.810333 | 31.241333 |
| TXN | 1 | -6.334127 | -6.334127 |
| IBM | 3 | -0.587377 | -1.762132 |
| AMAT | 3 | 1.977574 | 5.932721 |
| MU | 4 | 0.868715 | 3.474859 |
| LOW | 0 | n/a | 0.000000 |
| PEP | 1 | -5.009539 | -5.009539 |
| KO | 0 | n/a | 0.000000 |

AMD, QCOM and MU tie at four signals each. QCOM contributes +31.241333 pp (154.19% of net); AMD +19.166693 pp (94.60%); XOM +18.708027 pp (92.33%). Removing QCOM's four signals leaves the other 53 with −0.207164 pp average excess. QCOM's best event accounts for most of that stock's contribution. Repeated stock identities matter, but the count leaders alone do not establish robustness: MU contains both the worst event and two of the best four. Largest negative stock totals are RTX −15.776880 pp, NKE −10.309093 pp and META −9.151811 pp.

## 6. Dependence and overlapping outcomes

Treat each holding period as the half-open interval [entry open, exit open). Shared exit/entry timestamps alone are not overlap. Count common trading open-to-open intervals for every unordered event pair:

| category | possible_pairs | overlapping_pairs | pair_overlap_pct | events_with_overlap |
| --- | --- | --- | --- | --- |
| same_stock | 36 | 2 | 5.555556 | 4 |
| different_stock | 1560 | 223 | 14.294872 | 56 |
| all | 1596 | 225 | 14.097744 | 56 |

56/57 events (98.25%) overlap at least one other stock's event. Two within-stock pairs overlap: NVDA by one interval and CAT by six. These involve four events (7.02% of 57); the 5.56% within-stock pair statistic has a different denominator, 36 possible same-stock pairs. Across stocks, 223/1,560 pairs overlap. Pair frequencies do not estimate an effective sample size.

Concurrent exposure peaks at 11 events: December 17 (11 stocks, four sectors), January 13 (11 stocks, five sectors), and August 24–26 (11 events, ten stocks, five sectors). Several nominal observations therefore reuse the same days and market shocks. A shared benchmark subtraction removes the same benchmark return, not every common exposure, beta difference or industry shock. Even non-overlapping events can share a regime. Fifty-seven outcomes cannot be treated as 57 independent experiments; no p-value, independence correction or effective sample size is manufactured.

## 7. Execution sensitivity

Same signals and completed cohort, matching SPY endpoints in every case. Official: entry O(t+1), exit O(t+11). First diagnostic changes entry only to C(t+1), preserving O(t+11) exit; this shortens exposure by the entry session. Second diagnostic uses C(t+1) to C(t+11), preserving ten close-to-close intervals. Neither changes the signal or official rule.

| version | convention | signal_count | average_excess_return_pp | median_excess_return_pp | hit_rate_pct |
| --- | --- | --- | --- | --- | --- |
| V0 | official_open_open | 332 | -0.388842 | -0.259629 | 48.493976 |
| V0 | next_close_original_exit_open | 332 | -0.325434 | -0.487282 | 46.987952 |
| V0 | next_close_t11_close | 332 | -0.334850 | -0.347611 | 46.987952 |
| V1 | official_open_open | 57 | 0.355467 | -0.456418 | 47.368421 |
| V1 | next_close_original_exit_open | 57 | 0.778858 | -0.293705 | 49.122807 |
| V1 | next_close_t11_close | 57 | 1.154423 | -0.039573 | 49.122807 |

This attack does NOT support dependence on favorable next-open execution: V1's mean rises to +0.778858 pp with the original exit open and +1.154423 pp with a matched exit close. V1−V0 mean differences rise from +0.744309 pp to +1.104292 and +1.489273 pp. Both alternative V1 medians remain negative and hit rates remain below 50%. Opening/closing prints are still idealized; no slippage, spreads, costs, capacity or executable fill study is included. The favorable alternative is not selected or recommended.

## 8. What the ATR rule selects

For each V1 date t, let p be the earliest maximum ATR% date among the prior 20 sessions. Exact identity: ATR%(t)/ATR%(p) = [ATR(t)/ATR(p)] / [Close(t)/Close(p)]. “Raw ATR” here means the absolute-price ATR computed from the frozen adjusted OHLC, before dividing by Close, not an unadjusted vendor series. These diagnostic flags overlap and are not new signal definitions.

- **Single-maximum dependence:** remove one maximum observation, use the second-largest prior ATR%, and ask whether the existing 0.80 rule would fail. This happens for 7/57 (12.28%). It measures numerical dependence on one point; it does not prove an unusual one-day volatility shock, since Wilder ATR is smoothed.
- **Price-denominator assistance:** 23/57 (40.35%) have ATR(t)/ATR(p) > 0.80 but pass after dividing by a higher price ratio. Price appreciation is necessary for the full 20% ratio decline in those cases. Nevertheless ATR itself declined in ALL 57; none is purely a price-rise case with flat or rising ATR relative to p.
- **Absolute ATR decline:** 34/57 (59.65%) have at least a 20% ATR decline from the reference peak without needing a rising-price denominator. The peak's median age is 16 sessions (range 8–20), so the rule often compares with an old high.
- **Broader-window diagnostic:** compare median absolute ATR over t−4 through t with the first five sessions of the prior window (t−20 through t−16). It declines in 52/57 (91.23%); it declines at least 20% in 20/57 (35.09%). The other five show no median decline despite passing the max-based rule. These five-session summaries were added for description, not optimized or used to admit signals.

Volatility decline is therefore common in the measured ATR series. The rule is not predominantly a single-point or purely price-denominator artifact. But peak-to-current contraction does not guarantee persistently low volatility, a quiet regime, or any causal connection to subsequent excess returns. Price and numerator contributions are algebraically linked; these observations cannot identify economic causation. No alternative ATR lookback or threshold was tested.

## Robustness scorecard

Ratings are qualitative post-result judgments, not preregistered numerical acceptance criteria. PASS means this particular attack did not reveal the proposed failure, not proof of a trading edge.

| Category | Rating | Reason |
| --- | --- | --- |
| Data integrity | PASS | Frozen hashes, original outputs, endpoints and signal calculations reconcile. Internal integrity only; no independent vendor confirmation. |
| Outlier dependence | FAIL | Removing one winner turns the mean negative; top-three capping also turns it negative. |
| Stock concentration | FAIL | QCOM alone contributes more than the net total; removing that stock makes the mean negative. |
| Sector concentration | FAIL | IT and Energy each exceed the net total; removing either makes V1 negative. |
| Date/regime concentration | CAUTION | Large December/August cohorts, influential sparse months and only one year. |
| Observation dependence | CAUTION | 56/57 events overlap another; independence is unjustified and no inference is claimed. |
| Execution sensitivity | PASS | Both requested next-close diagnostics retain and increase the positive mean; fill realism remains untested. |
| ATR mechanism | CAUTION | Real ATR declines are common, but price normalization and an old maximum materially affect selection. |

**Overall: FRAGILE.** The positive mean fails simple outlier and concentration attacks. Execution and ATR checks do not support every proposed skeptical explanation, so neither a universal failure claim nor a causal story is justified. The original MIXED result remains intact.

Remaining limits: one observed year, selected static universe/sectors, overlapping and regime-related events, revised vendor history, no independent price-event verification, idealized gross fills, and post-result diagnostic selection. These tests do not estimate future performance or establish statistical significance. The year is no longer untouched evidence.

Next lesson, without creating V2: a higher mean must be distinguished from typical-event improvement and broad independent support. Before another hypothesis is tested, specify how concentration, common exposure and numerator-versus-price effects will be judged, and preserve genuinely unobserved evidence. No new strategy or parameter is proposed here.

## Artifacts and preservation

All new diagnostic CSVs, a single outlier chart and their hashes are in output/robustness/. analysis/robustness.py performs calculations; analysis/test_robustness.py tests overlap boundaries; this report and RESEARCH_LOG.md record the complete findings. Original output/v0_v1_* files and frozen files remain hash-identical. No data download or frozen pipeline rewrite was performed.


## Long-term-trend diagnostic — human idea recorded before calculation

The human researcher originated the price-above-rising-SMA200 idea before this diagnostic. SMA200 rising means strictly greater than its value 20 trading sessions earlier. V0/V1 and all official outcomes remain frozen; this is an exploratory environment description, not V2. The same evaluation year has already been inspected. New earlier Yahoo data will be isolated, checked for adjustment continuity against the frozen overlap, and used solely for indicator warm-up.


---

# Learning from fragile V1: long-term trend environment

2026-09-08. **Classification: WEAK RATIONALE**, based on this diagnostic's evidence for the exact proposed next hypothesis. The general concept is economically coherent, but this observed period does not support the claim that price above a rising SMA200 would address V1's failures. This does not prove the concept false.

## Human origin and boundaries

The human researcher proposed Close > SMA200 and SMA200(t) > SMA200(t−20) before this diagnostic ran. That origin and the definitions were recorded in PROMPTS.md and RESEARCH_LOG.md before feature calculation. The proposal followed the observed V1 failures and is therefore already informed by this historical period. No V2 was created, no setting was optimized, no additional indicator family was searched, and all official V0/V1 outputs, prior robustness outputs and frozen files remain unchanged.

V1's official result is still 57 completed events, +0.355467 pp mean excess, −0.456418 pp median and 47.368421% hit rate. The frozen evaluation window remains 2025-09-08 through 2026-09-08. All 62 detected V1 signals receive trend features, including five pending outcomes. Only the original 57 complete next-open to t+11-open outcomes enter descriptive comparisons. Stock excess is measured against identical SPY endpoints with equal event weights.

## Conceptual motivation and what could be missing

ATR contraction describes declining recent price variability; it does not establish whether the stock is in a sustained advance, a rebound within a decline, or an extended advance vulnerable to reversal. A long-term trend condition could distinguish those environments. That is a coherent human hypothesis, not something the fragile mean alone demonstrates is missing.

Longer-horizon trend persistence has an established research context, but evidence on different assets and horizons does not validate this particular conjunction. For example, [Moskowitz, Ooi and Pedersen's time-series momentum research](https://www.aqr.com/insights/research/journal-article/time-series-momentum) and its [original data description](https://www.aqr.com/Insights/Datasets/Time-Series-Momentum-Original-Paper-Data) concern a 12-month momentum signal with monthly holding periods across futures asset classes. They do not establish this stock SMA200/ATR rule or its ten-session excess-return effect.

## Exact diagnostic definitions

Use the frozen adjusted Close convention. SMA200(t) = sum of Close(t−199) through Close(t), divided by 200. The earlier SMA200(t−20) averages Close(t−219) through Close(t−20). Thus the earliest feature requires 220 observed trading-session closes including the signal day, with no discretionary extra seed period for this finite-window average.

- Above: Close(t) > SMA200(t), strictly.
- Rising: SMA200(t) > SMA200(t−20), strictly. Equality means not rising.
- Distance: 100 × [Close(t)/SMA200(t) − 1], plus Close(t) − SMA200(t) in adjusted price units.
- Twenty-session change: 100 × [SMA200(t)/SMA200(t−20) − 1], plus the absolute SMA difference.
- A: above AND rising. B: above AND not rising. C: strictly below SMA200. Exact Close/SMA equality and unavailable values are retained separately, not silently classified as below. Neither occurs here.

Both indicators include only price observations dated on or before the signal close. They do not enter or modify V1. “Rising” compares two endpoints, not continuous daily increases. Because the two 200-session windows overlap by 180 sessions, the sign of their difference compares the latest 20 closes with the 20 observations displaced from the older end. It is slow-moving context, not a guarantee of a healthy trend or an attractive entry price.

## Minimal data extension and verification

Only 21 of the 33 stocks with detected V1 signals needed earlier history; the other 12 already had sufficient frozen history. Retrieved 582 additional pre-snapshot ticker-session observations in total. Start dates were individually chosen to provide exactly the missing warm-up at each stock's earliest signal. Earliest added date: 2024-10-28 for AMAT. Each request included the five existing March 10–14, 2025 sessions for continuity checks; those overlap prices never replace the frozen series. No new benchmark history was needed.

New Yahoo data are isolated in data/trend_warmup/. Settings remain yfinance auto_adjust=False, back_adjust=False, actions=True, repair=False, daily regular-session data, followed by the existing adjusted-Close convention. Every requested date is accounted for, with no duplicate or invalid OHLC/volume bars. Earlier exchange closures include Thanksgiving and Christmas 2024, New Year's Day, January 9 national mourning, MLK Day and Presidents' Day 2025; early closes remain sessions. Calendar references: [NYSE holiday announcement](https://ir.theice.com/press/news-details/2023/NYSE-Group-Announces-2024-2025-and-2026-Holiday-and-Early-Closings-Calendar/default.aspx), and [NYSE January 9 closure announcement](https://ir.theice.com/press/news-details/2024/The-New-York-Stock-Exchange-Will-Close-Markets-on-January-9-to-Honor-the-Passing-of-Former-President-Jimmy-Carter-on-National-Day-of-Mourning/default.aspx).

For every extended stock, all five overlapping unadjusted Close observations matched the saved vendor Close within 1e−8 absolute tolerance. To keep the earlier adjusted values in frozen units, multiply only the added prefix by median(frozen adjusted Close / newly retrieved Adj Close) over the overlap. A pre-calculation 1e−6 relative consistency tolerance rejects a nonconstant bridge. Observed scale factors are within approximately 1.1e−7 of one; the largest overlap relative residual is 2.11e−7. These tiny differences are compatible with adjustment rounding, not an identified substantive revision. Frozen prices are used unchanged from March 10 onward.

The new prices and adjustment factors are retrospective vendor history, not a reconstructed point-in-time corporate-action database. This inherits the frozen adjustment convention's limitation. No future price observation enters either moving-average window. Every event's features match a calculation truncated at its signal date and independently checked direct window means. All 62 events have complete features. Three synthetic tests cover exact windows/warm-up, equality/nonrising classification and immunity to future-price changes. Frozen, original result and robustness hashes pass; group totals reconcile to the 57-event official result.

## Descriptive environments

A = above a rising SMA200; B = above a nonrising SMA200; C = below SMA200. Return columns are percentage points; hit rates are percentages.

| environment | signal_count | average_excess_return_pp | median_excess_return_pp | hit_rate_pct |
| --- | --- | --- | --- | --- |
| A | 33 | -0.462757 | -0.716914 | 45.454545 |
| B | 3 | 8.597059 | 8.316858 | 66.666667 |
| C | 21 | 0.463878 | -0.198058 | 47.619048 |
| Equality | 0 | n/a | n/a | n/a |
| Unavailable | 0 | n/a | n/a | n/a |

Detected counts including pending observations are A=36, B=4, C=22. Pending counts are respectively 3, 1 and 1. They are not assigned zero or failed outcomes.

The proposed aligned environment A contains 33/57 completed events (57.89%), with a negative mean and median and sub-50% hit rate. Its mean is lower than both the full V1 mean and the below-SMA200 group's mean. Thus the proposed explanation receives no favorable descriptive support here.

The three-event B group consists of AMAT on September 15 (+17.998463 pp), AMZN on December 10 (−0.524143 pp) and CVX on December 31 (+8.316858 pp). Its high average cannot be treated as reliable evidence or used to pivot to a different trend rule. Group C includes the single largest QCOM winner. These groups differ in stocks, sectors, months and shared exposure; their contrasts do not isolate a causal trend effect.

## Learning from the largest winners and losers

Use the same five best and five worst excess outcomes examined in the prior robustness stage; no new tail cutoff was selected. The table includes the requested distances and slope changes, all calculated at the signal close.

| tail | ticker | Date | entry_date | exit_date | sector | environment | distance_pct | sma200_change_pct | stock_return_pct | spy_return_pct | excess_return_pp |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| best5 | QCOM | 2026-04-16 | 2026-04-17 | 2026-05-01 | Information Technology | C | -13.632120 | -1.424282 | 31.048371 | 2.139796 | 28.908575 |
| best5 | AMAT | 2025-09-15 | 2025-09-16 | 2025-09-30 | Information Technology | B | 2.126729 | -1.028170 | 18.497042 | 0.498579 | 17.998463 |
| best5 | MU | 2026-04-15 | 2026-04-16 | 2026-04-30 | Information Technology | A | 79.110396 | 12.535047 | 16.950724 | 1.935639 | 15.015085 |
| best5 | MU | 2025-12-08 | 2025-12-09 | 2025-12-23 | Information Technology | A | 83.771540 | 11.480557 | 12.855331 | 0.408528 | 12.446803 |
| best5 | XOM | 2026-07-14 | 2026-07-15 | 2026-07-29 | Energy | A | 7.213227 | 2.173221 | 8.704942 | -1.891973 | 10.596915 |
| worst5 | MU | 2026-03-18 | 2026-03-19 | 2026-04-02 | Information Technology | A | 102.265091 | 16.527261 | -19.645297 | -1.337138 | -18.308160 |
| worst5 | RTX | 2026-04-14 | 2026-04-15 | 2026-04-29 | Industrials | A | 15.590518 | 3.405322 | -13.512979 | 2.263900 | -15.776880 |
| worst5 | AMAT | 2026-08-12 | 2026-08-13 | 2026-08-27 | Information Technology | A | 42.265469 | 8.714679 | -12.170901 | -0.822073 | -11.348828 |
| worst5 | NKE | 2026-04-27 | 2026-04-28 | 2026-05-12 | Consumer Discretionary | C | -29.401676 | -3.107900 | -6.787132 | 3.521961 | -10.309093 |
| worst5 | ETN | 2025-12-11 | 2025-12-12 | 2025-12-29 | Industrials | A | 4.348526 | 1.035912 | -7.683945 | 0.203677 | -7.887621 |

**Weak long-term trends are not disproportionately associated with the largest losses.** Four of the five largest losers (80%) were in A, versus three of the five largest winners (60%) and 57.89% of all completed signals. Only NKE among the five largest losers was below SMA200. The proposed conjunction would retain MU, RTX, AMAT and ETN's large losses while omitting the largest QCOM winner and second-largest AMAT winner. This comparison is environment membership, not a newly implemented strategy.

MU illustrates the missing distinction between a rising trend and a favorable short-horizon outcome. Its largest loss occurred while price was about 102.27% above SMA200 and SMA200 had risen 16.53% over 20 sessions. Its two top-five wins also occurred well above a rising SMA200. A positive long-term trend is therefore neither sufficient protection against a sharp loss nor unique to winners. This observation does not authorize an overextension threshold or another indicator search.

**Sectors:** the five largest winners comprise four IT events and one Energy event; the five largest losers comprise two IT, two Industrials and one Consumer Discretionary event. For context, IT accounts for 27/57 total V1 signals and Industrials six. Industrials represent 40% of the worst five versus 10.53% of the full sample, but only two losses underlie that contrast. Sector composition remains a plausible confounder, not evidence for a new sector rule.

**Repeated stocks:** MU supplies two of the five largest winners and the largest loss. AMAT appears in both tails on different dates. The worst five contain five distinct names, so repeated losers in one stock do not explain that tail; repeated exposure to the same names across both tails still matters. These findings are inconsistent with a simple split between permanently good and bad stock identities.

**Dates/regimes:** MU and QCOM winners on April 15–16 share nine holding intervals, while RTX's April 14 loss overlaps both. NKE's April 27 loss belongs to that same month and overlaps part of their holding periods. December has both MU's December 8 winner and ETN's December 11 loser. The most extreme outcomes can share market dates but have opposing signs. Their economic dependence and sector exposures remain relevant; dates alone cannot identify a specific causal market event. No news-driven or regime indicator was added.

Complete environment, sector, stock and month counts for both tails and the full cohort are saved in tail_characteristics.csv. Five-event tails are far too small for reliable subgroup inference.

## Interpretation and decision

**WEAK RATIONALE** is the classification of the observed evidence supporting this exact candidate. The human idea remains conceptually sensible and falsifiable; the data do not make a positive empirical case for promoting it. A negative 33-event subgroup cannot prove the hypothesis false either, particularly with overlapping outcomes and unequal sector/date composition.

What V1's failure taught us: volatility contraction and a short-term bullish crossover do not guarantee a broad improvement in typical outcomes. A favorable aggregate mean can depend on a few names and events. This diagnostic adds that a positive long-term trend alone does not explain away the large losses. Additional conditions must have a reason independent of chasing attractive subgroups.

Candidate under discussion only: **V1 + Close > SMA200 + SMA200(t) > SMA200(t−20)**. No V2 has been created or preregistered by this stage. These results do not justify treating it as the preferred improvement. If the human still wants to investigate the independent theory, preregister that exact candidate, unchanged shared infrastructure and an untouched future/out-of-sample evaluation plan before testing; keep the present period explicitly exploratory. Do not substitute B, change slope/lookbacks or optimize on the observed groups.

We have already examined this year, used its V1 failure to motivate another question, and now inspected its trend subgroups. Any candidate arising from this process is exploratory and requires genuinely unobserved future/out-of-sample validation. It is not validated, statistically proven or recommended for trading. No p-values or causal claims are made.

## Outputs

output/trend_diagnostic/v1_trend_features.csv: all 62 historical V1 features and unchanged outcomes/status. environments.csv: complete-outcome descriptive summaries. extremes.csv: original five best/five worst with trend features. tail_characteristics.csv: comparison counts. data_audit.json: per-stock retrieval/quality/adjustment bridge. manifest.json: source/code/output hashes. No chart is needed for this three-group comparison.


---

# Research decision gate — retain signals, do not promote a strategy

Decision date: 2026-09-08.

**D. DO NOT PROMOTE A STRATEGY — KEEP V0/V1 AS RESEARCH SIGNALS.**

This decision uses only the evidence already generated. No new data, return calculation, indicator, subgroup search, optimization or strategy version was introduced. Prospective tracking has not begun. V0/V1 and their original results remain unchanged.

## Supported by the evidence

| Stage | Documented observation | Bounded conclusion |
| --- | --- | --- |
| V0: GitHub-derived strict bullish SMA10/SMA20 crossover | 332 completed events; mean excess −0.388842 pp; median −0.259629 pp; hit rate 48.493976% | An understandable, reproducible research baseline; this sample does not justify promotion. GitHub adoption is not investment edge. |
| V1: human-origin, preregistered ATR contraction | 57 completed events; mean excess +0.355467 pp; median −0.456418 pp; hit rate 47.368421% | The filter improves the mean by +0.744309 pp but worsens median and hit rate while removing 82.83% of completed signals. First-pass classification remains MIXED. |
| V1 robustness | Mean becomes −0.154410 pp without the best event and −0.771491 pp without the best three; outlier, stock and sector concentration checks fail | The positive mean is FRAGILE. A few large gains outweigh more frequent underperformance. Diagnostic exclusions do not replace the official result. |
| Long-term-trend diagnostic | Above a rising SMA200: 33 events; mean −0.462757 pp; median −0.716914 pp; hit rate 45.454545%; four of five worst losses | WEAK RATIONALE for the exact proposed trend addition. The human idea was coherent but did not explain away the losses. It will not be promoted to V2. |
| Observation dependence | 56 of 57 V1 events overlap another stock's holding period; two same-stock pairs overlap | The 57 observations are not automatically 57 independent experiments. Common dates, sectors and regimes limit information in the sample. |

These are equal-event-weighted, gross, ten-trading-interval excess returns against SPY, not portfolio returns. The studied signal window is 2025-09-08 through 2026-09-08, with only mature outcomes included. Pending events were not treated as zeros or failures.

The skeptical review did not support every proposed failure story: next-close execution diagnostics increased V1's mean, and absolute ATR declined from the reference peak in every V1 event. Those findings remain part of the record. Internal integrity checks passed, but they do not independently verify vendor prices or prove economic validity.

## Not supported by the evidence

- Calling V0 or V1 a validated, statistically established or implementable trading edge.
- Calling V1 broadly better solely because its primary mean improved, or calling V0 superior simply because V1 is fragile.
- Claiming that price above a rising SMA200 fixes V1, creating V2 from that diagnosis, or promoting the attractive three-event nonrising-trend subgroup.
- Treating GitHub popularity, a successful code test or an internally consistent data pipeline as evidence of profitability.
- Treating diagnostic deletions as permission to discard losing stocks, sectors or dates from the official record.
- Assuming a higher hit rate is necessary or sufficient for profitability. Here the negative median and lower hit rate weaken the claim of broad improvement; neither statistic alone decides whether an edge exists.
- Declaring the general SMA, ATR or trend concepts permanently disproven. This experiment is bounded by its period, universe and design.

## Still unknown

- Whether either unchanged signal has positive expected excess return on genuinely new data, and whether V1 has a reproducible incremental benefit over V0.
- Whether any effect persists across independent market periods and remains economically meaningful after realistic execution costs and risk exposure are considered.
- How much confidence is warranted after accounting for overlapping holdings, repeated stocks, shared sectors and market regimes. No defensible effective sample size or uncertainty interval was established here.
- Whether the influential vendor price events would survive independent price/corporate-action verification, and how revised history affects reproducibility.
- Whether a separately specified portfolio construction, sizing and execution process could turn event-level signals into an investable strategy. That has not been studied or authorized.
- What economic mechanism, if any, causes the observed differences. Descriptive subgroup comparisons do not identify causation.

## Decision and why stopping is success

Choose D. Neither signal has sufficient evidence for promotion, and the narrow follow-up supplied no persuasive reason to create V2. The project has succeeded at distinguishing a reproducible signal from demonstrated predictive value, exposing fragility, and documenting a plausible human idea that did not earn support.

**We explicitly chose not to manufacture a better backtest by continuing to search the same historical sample.** The previously examined year remains observed research data; changing its label or rerunning another filter cannot make it untouched evidence. Stopping preserves an honest negative/mixed result, the original hypotheses, useful infrastructure and the opportunity to learn prospectively. It prevents a research exercise from becoming repeated selection for a favorable answer.

This is a stop to modification and promotion, not proof that further learning is impossible. The retained artifacts are an auditable research case study and frozen signal definitions, not trading recommendations.

## Clean prospective experiment — proposed, not started

1. **Preregister before collection.** A later, explicitly authorized protocol should record its start date after registration, duration/end date, scheduled review dates, data-handling rules and decision criteria before any new outcomes are inspected. Select the duration and evidence target using a justified precision/power plan that allows for clustering; do not invent a magic raw signal count. Do not stop because cumulative performance first looks positive. No dates, numerical promotion thresholds or tracking automation are activated by this document.

2. **Carry forward both frozen hypotheses.** Retain the fixed 50-stock universe, SPY benchmark, Yahoo adjustment convention, strict crossover, ATR settings, timing and metrics. V0 requires SMA10(t−1) < SMA20(t−1) and SMA10(t) > SMA20(t). V1 adds ATR14(t)/Close(t) <= 0.80 times the maximum of that ratio over t−20 through t−1, using the frozen Wilder ATR definition. No SMA200 condition is added. Future operational calendar/history support must be isolated from the archived frozen snapshot, with sufficient warm-up and an auditable exchange calendar; it must not silently change signal definitions.

3. **Create an append-only, timestamped signal ledger.** After each completed market close, capture the available data snapshot, retrieval timestamp, code/specification hashes, quality status and both signals for every universe member. Record qualifying signals and indicator values before the next open and before their forward outcomes are known. Retain no-signal days and missing/late-data incidents for audit. Predefine an incident policy: a signal reconstructed late cannot be passed off as an on-time prospective call. Preserve original data and separately log corrections rather than rewriting the prediction history.

4. **Measure the identical outcomes.** Hypothetical entry remains O(t+1); exit remains O(t+11), ten open-to-open intervals later. Compute stock return O(t+11)/O(t+1)−1, identical-date SPY return, and their difference. Record actual available endpoint data after each endpoint occurs. Pending events stay pending; unavailable prices follow the preregistered missing-data policy. Previously observed historical signals, including their pending outcomes, remain in the original cohort and are not relabeled as new prospective signals.

5. **Accumulate and review without adaptation.** Keep each outcome linked to the earlier immutable signal record. Use the same equal-event-weighted mean excess as primary, with median, hit rate and sample size as secondary; show concentration and overlap diagnostics. Set review dates in advance and do not change the rule after individual wins, losses or disappointing reviews. Any future authorized change must be a distinct hypothesis with a new timestamp and new validation evidence, not a repaired V0/V1 history.

6. **Plan uncertainty and economic validation before making promotion claims.** The future analysis plan must account for V1 being nested inside V0 and for dependence across dates/stocks; do not use independent-sample reasoning by default. Specify an appropriate cluster-aware estimation method and sensitivity analyses before evaluating new outcomes. Preserve gross frozen metrics for comparability; any cost-adjusted layer should be separately preregistered, not substituted retrospectively for the official outcome. Promotion would also require data/event verification, realistic execution and cost assessment, risk/portfolio feasibility, and replication or further unobserved evidence sufficient to support an economically meaningful effect. A positive mean or a single favorable statistical test is insufficient.

What we could build later is a transparent prospective signal journal and evaluation dashboard, alongside an educational account of falsification and disciplined stopping. This stage only defines that possibility; it does not begin data acquisition, signal generation, tracking, paper trading or portfolio implementation.

## Evidence record and preservation

Sources are the existing project records only: FIRST_PASS_RESULTS.md, ROBUSTNESS_REPORT.md, LONG_TERM_TREND_DIAGNOSTIC.md and FROZEN_SPECIFICATION.md. Existing frozen inputs and original first-pass, robustness and trend output hashes were verified. RESEARCH_LOG.md and PROMPTS.md record this decision. No existing performance artifact was changed.


## Chapter 7 — Building the system, not claiming success (2026-09-08)

The human authorized a repeatable command-line prospective research signal engine after decision D. Built `python -m src.run_signal_engine` using the unchanged frozen V0/V1 indicator functions, universe, sectors, Yahoo adjustment convention, seed history and t+1/t+11 open endpoints. No V2, optimization, SMA200 addition or historical performance revision occurred. Chapter 7 is about BUILDING THE SYSTEM, not claiming success.

Created current_signal_scan.csv, current_signals_only.csv and prospective_signal_journal.csv as empty production templates pending the next-stage live scan. No live signal acquisition or prospective record has been made in this build stage. The command will populate the two current files and append new signal records when run. Added an authoritative append-only, hash-chained prospective_signal_events.jsonl ledger (created on first recorded event); the requested journal CSV is its atomic materialized view. Duplicate stock-date-version IDs are rejected; original signal features and first observed entry prices cannot be revised. ENTRY and COMPLETE additions supply later information; returns stay blank/PENDING until the full exit window and all endpoints are available. Later adjustment revisions are handled by separate same-snapshot valuation entry fields, preserving original entry observations. Completed outcomes are immutable.

Only live signals after the already-observed September 8 boundary recorded after signal close and strictly before next open are PROSPECTIVE. Late and offline records are explicitly RETROSPECTIVE; replay is prohibited in the production directory, clock override is prohibited in live mode, and missed days are not silently backfilled. Each run saves raw vendor snapshots, scan, data quality, source/code/spec hashes and errors. Partial/unavailable data are not false signals. Reused only the previously authorized exact KO correction, with original data retained.

Added pinned exchange-calendars 4.13.2 for operational sessions and open/close times; frozen requirements.txt and frozen research files were not edited. Workspace-local dependencies are isolated; requirements-engine.txt documents reproducible installation. The calendar agrees with the frozen session list and handles early closes. Current scans use only completed sessions, with a post-download timestamp for prospectivity. Calendar/clock accuracy, future closures, vendor revisions, network availability and idealized gross fills remain limitations. Logging is not statistical validation; review/precision/inference and promotion criteria remain to be preregistered before outcome-based decisions.

Validation: all 10 new engine tests and 26 frozen tests passed. Tests cover deduplication, immutable features, pending maturity, unavailable/future bars, append-only outcomes and adjustment consistency, V1 subset, no skipped-date backfill, late/replay classification, calendar agreement, and deterministic offline command replay. A separate offline end-to-end command processed all 50 stocks for the already-observed September 8 snapshot, producing three V0 and two V1 memberships (five retrospective journal rows, zero prospective). This is operational validation, not a new performance test or today's live result. The production CSVs remain empty pending the first live command. All existing first-pass, robustness and trend output hashes remain unchanged.

Operating guidance: SIGNAL_ENGINE.md. No public README/START_HERE package, scheduler, broker integration, orders, strategy promotion or additional indicator testing was created. The next step is the first live run and inspection of its current scan.


---

# First live frozen-engine run — 2026-09-08

Command: `python -m src.run_signal_engine`. Successful run ID: 20260908T234600_a319c2a9. Recorded at 2026-09-08 23:46:06.796072 UTC (19:46:06.796072 America/New_York). Latest completed market-data date: **2026-09-08**. Yahoo supplied that completed session for all 50 stocks and SPY; no fallback to an earlier day was necessary. This is a live source acquisition, not a new performance test.

## Current signals

**V0: NVDA, GS, UNH (3). V1: GS, UNH (2).** V1 membership overlaps V0; there are three distinct stock-date signals, not five independent events. Prices and SMAs below use the frozen adjusted convention. ATR ratios are displayed as percentages; saved engine CSVs retain fractions.

| Ticker | Sector | Close | SMA10 | SMA20 | ATR% | Prior-20 max ATR% | Contraction | Membership |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| GS | Financials | 1036.5300 | 1029.4806 | 1029.4500 | 2.4378% | 3.2856% | Yes | V0 + V1 |
| UNH | Health Care | 400.8400 | 396.9890 | 396.5170 | 2.2397% | 2.8578% | Yes | V0 + V1 |
| NVDA | Information Technology | 225.7300 | 221.5410 | 220.4910 | 3.3165% | 3.5224% | No | V0 only |

## Educational Top 10 watchlist

Ordering follows the human request only: current V1, then V0-only, then usable inactive stocks with SMA10 at or below SMA20, closest from below. Within active categories use alphabetical ticker order. Signed gap = 100 × (SMA10/SMA20 − 1); inactive candidates are sorted from zero downward, with alphabetical ties. Already-above noncrossovers are not represented as approaching a bullish cross. No new predictive score, signal rule or journal membership is created. A near signal may never cross, and equality does not satisfy the frozen prior-day strictly-below rule.

| Order | Ticker | Status | Signed SMA gap |
| --- | --- | --- | --- |
| 1 | GS | ACTIVE V1 (also V0) | +0.002976% |
| 2 | UNH | ACTIVE V1 (also V0) | +0.119037% |
| 3 | NVDA | ACTIVE V0 ONLY | +0.476210% |
| 4 | MS | NEAR SIGNAL — NOT ACTIVE | -0.148770% |
| 5 | IBM | NEAR SIGNAL — NOT ACTIVE | -0.167662% |
| 6 | PEP | NEAR SIGNAL — NOT ACTIVE | -0.168784% |
| 7 | SBUX | NEAR SIGNAL — NOT ACTIVE | -0.292845% |
| 8 | JPM | NEAR SIGNAL — NOT ACTIVE | -0.387258% |
| 9 | XOM | NEAR SIGNAL — NOT ACTIVE | -0.535893% |
| 10 | GOOGL | NEAR SIGNAL — NOT ACTIVE | -0.563873% |

## Journal and prospective boundary

Before this run the production journal was empty. The engine appended **five version-level records**: NVDA/V0, GS/V0, GS/V1, UNH/V0 and UNH/V1. **Genuinely prospective additions: zero.** All are explicitly RETROSPECTIVE because the signal date is inside the already-examined research period ending September 8, even though the engine was run after close and before the next open. The classification is unchanged engine behavior; this live acquisition is not fresh out-of-sample evidence.

Only current-day signals were recorded; no older missed signal dates were backfilled. Pending: five version records (three stock-date events). Complete: zero. Entry and outcome fields remain blank. Duplicates prevented in this first run: zero, since the journal was empty; five unique IDs and no duplicates were verified. No additional live run was performed merely to increment a duplicate counter. Prior tests establish repeat-run deduplication.

## Operational checks

- Successful network-enabled run: 51/51 source series available and validated; 50/50 current stock rows usable. No failed downloads, stale tickers, missing sessions, extra dates, duplicate dates, zero-volume bars or remaining invalid prices were reported.
- Reapplied only the already-frozen KO September 8 correction: Low [HISTORICAL YAHOO VALUE NOT DISTRIBUTED] to [HISTORICAL YAHOO VALUE NOT DISTRIBUTED], using the earlier documented complete Yahoo minute-bar evidence. The original response is retained; no new repair was inferred.
- No calendar or journal integrity issue was reported on the successful run. The calendar selected the completed September 8 session. Source snapshots remain retrospective vendor data and can be revised later.
- An initial sandboxed attempt was interrupted before completing acquisition or publishing outputs; the interrupted process had exited, and its leftover lock was removed before retrying the unchanged command with network access. Its incomplete run directory is retained. This operational retry did not alter methodology or add journal records.
- Frozen research and prior first-pass/robustness/trend outputs remain hash-identical. No historical performance was recalculated or reinterpreted.

## Saved outputs and interpretation

Updated output/current_signal_scan.csv, output/current_signals_only.csv and output/prospective_signal_journal.csv. Created output/current_watchlist_top10.csv. The journal ledger and per-run raw data/manifest preserve provenance. The watchlist is educational monitoring only and its seven inactive rows do not enter the signal journal.

We started with an idea, tested it, discovered that it was not robust, refused to overfit it, and built a system capable of recording new evidence prospectively. This first live snapshot demonstrates operation, not a validated trading edge or investment recommendation. Decision D remains in force. The next packaging task is to make the complete experiment inspectable and reproducible; no public README/START_HERE package was created in this run.


## Public educational release preparation — 2026-09-08

Prepared README.md, START_HERE.md, THIRD_PARTY_NOTICES.md, a prompt-purpose/result index and this navigation guide. No unfavorable results or human overrides were removed. FROZEN_SPECIFICATION.md was reviewed for ATR seed/recurrence, adjustment formula, strict inequalities, prior-window exclusion, t+1/t+11 endpoints, SPY, universe and metrics and retained byte-for-byte with its lock.

Clean-checkout review found the daily engine depended on ignored archived Yahoo data through strict verify_freeze(). Added src/release_integrity.py for public runtime: all shipped frozen files remain mandatory/hash-checked and present archive files are verified, while absent vendor archive files are explicitly reported rather than blocking a new scan. Original strict historical verifier, frozen methodology, historical source code and results are unchanged. Tests demonstrate missing private data is permitted and modified required source is rejected. Added src/build_watchlist.py to reproduce only the already-authorized educational ordering, without affecting journal membership.

Public scope excludes data/cache/output/installed dependency/temporary directories; records remain locally intact. Public sources and human-readable reports retain failed paths and observed outcomes. The original archive is not redistributed or silently replaced, so exact historical reproduction requires that archive and fresh Yahoo data may differ. Requirements include separate optional historical plotting dependencies. Live engine can fetch its own data without a private archive.

Recommended MIT for original code/documentation subject to owner approval and rights/attribution confirmation; no LICENSE silently applied. THIRD_PARTY_NOTICES.md distinguishes concept review from source copying and from installed dependency or Yahoo-data rights. Socrates Mode is a labeled navigation placeholder only; building it remains next. No new strategy, optimization, live signal run, GitHub remote, commit or publication was performed in this stage. PUBLIC_RELEASE_AUDIT.md records checks and remaining publication steps.

Public-release verification completed: isolated public copy and Python 3.13 environment installed successfully; pip check/Yahoo import passed; 33 clean-copy checks passed with four explicit archive-dependent skips; synthetic engine processed 50/50 stocks plus SPY. Public text audit and local-link checks found no issues. Personal production outputs and all prior research artifacts remain unchanged. License/owner/repository approval and actual GitHub publication remain pending.


## Socrates Mode — viewer question discovery and final review (2026-09-08)

Replaced the planned SOCRATES_MODE.md placeholder with a complete pasteable conversation instruction. The human goal is to help viewers investigate their own curiosity, not reproduce a supposed trading edge. The flow is one adaptive question at a time, a concise TREASURE HUNT BRIEF and explicit user approval before implementation. It addresses observable outcomes, comparison, timing/data access, assumptions, systems relationships, biases, falsification, small tests and stop conditions. It welcomes prediction, comparison, risk, process automation and non-finance inquiry rather than forcing every question into a trading model.

Included the requested opening, an explicit “what would convince you that your idea is wrong” question, the nine required brief fields, honest handling of unknown data and inconclusive results, open-source capability/license verification and the distinction between adoption and effectiveness. No code, data acquisition, engine run or file editing is allowed during that interview. Approval covers only the agreed first experiment; a revision or silence is not approval. New experiments stay separate from this frozen reference. The file is an instruction, not an installed plugin or autonomous program.

Added seven concise question examples (ETFs, mutual funds, earnings revisions, crypto, portfolio risk, customer onboarding and school-library reminders), simple usage steps, and the empowerment/agency philosophy. Updated the prominent README link and beginner guide; preserved the chronological history of the earlier placeholder. The instructions were reviewed against ambiguous language, early requests to code, uncertainty about data, revising rather than approving a brief, non-finance goals and unverified tool suggestions. This was a document/flow review, not a claim of measured conversation success across AI products.

Final public review checks local links, stale current instructions, private identity/path/credential patterns and Git exclusions. The previous isolated-environment reproducibility results remain applicable because this stage changes documentation only. No source, requirement, frozen formula, research result, live scan, watchlist or journal was changed. No publication occurred. License/copyright approval, public account/repository selection, final staged-file review and the approved GitHub publication remain outstanding.

Socrates final audit completed: all 50 Git-visible public files reviewed; no broken local file links, private identity/machine-path/obvious credential findings, unmatched code fences or stale placeholder claims in current reader guides. Required brief headings and approval/stop instructions checked. Source/tests, frozen archive and existing analysis/live output hashes unchanged. No new code tests were needed for this documentation-only stage; no publication occurred.


## Full-prompt audit — 2026-09-09

Checked PROMPTS.md at the human researcher’s request: all 14 numbered entries exist, but the file contains labeled edited summaries/instructions, not all original prompts in full. The full-text requirement is therefore not met. Added source-by-source original restoration/verification as a required pre-publication gate in PUBLIC_RELEASE_AUDIT.md. No conclusion about accidental omissions can be made without that comparison. No prompt wording was invented, no historical research changed and nothing was published.


## Publication maintenance — restore all original prompts (2026-09-09)

The human required “ALL 14 PROMPTS — EXACTLY AS USED” and explicitly prohibited treating this maintenance request as Prompt 15. Recovered all 14 authoritative originals: seven original submitted text attachments (1, 5, 7, 8, 11, 13, 14) and seven original conversation user messages (2, 3, 4, 6, 9, 10, 12). No source was missing and no wording was reconstructed.

Replaced PROMPTS.md's summaries with complete verbatim original blocks, retaining separate stage/purpose metadata and short result/decision summaries. Verified every written block byte-for-byte against its source and recorded UTF-8 lengths and SHA-256 values. All original wording, punctuation, Markdown and line endings are preserved. Review found no sensitive prompt-body material requiring redaction; generated attachment path wrappers are not part of the original attached prompts. The final table marks all 14 VERBATIM VERIFIED, with ALL 14 ORIGINAL PROMPTS VERIFIED FOR PUBLICATION: YES.

The previous count-only/summary audit is preserved as the historical reason for this repair and is now resolved in PUBLIC_RELEASE_AUDIT.md. No Prompt 15 was added. No research results, code, frozen specifications or historical decisions were modified. The full-prompt publication requirement is ready; separate license/copyright and GitHub-publication approvals remain outstanding. Nothing was published.

## Publication maintenance — GitHub approval package (2026-09-09)

The owner requested preparation only, with no remote creation, push or publication. Proposed ai-treasure-hunt / AI Treasure Hunt and the broader curiosity-to-experiment laboratory message. Created GITHUB_PUBLICATION_REVIEW.md with the exact 51-file candidate manifest, ignored data/output/environment categories, four human-review files, license/copyright recommendation, privacy findings, beginner/Socrates/reproducibility review and approval checklist. Recommended MIT for original code/docs and Copyright (c) 2026 Visser Labs LLC, subject to ownership and explicit owner approval; no LICENSE applied. Updated README opening, START_HERE and THIRD_PARTY_NOTICES. This is publication maintenance, not a fifteenth research prompt. The fourteen original prompts, research results, frozen methodology and historical decisions remain unchanged. No strategy was promoted or new market run performed.

## Public packaging maintenance — private Yahoo references removed

The human authorized public packaging changes only. Original formulas, historical results/conclusions and all 14 prompt bodies remain unchanged. A KO anomaly was identified, quarantined, mechanically investigated and corrected before the frozen backtest. This remains private historical evidence; public export omits its Yahoo-derived values. Original sector labels were retrieved through Yahoo/yfinance and are not redistributed.

Public runs use freshly retrieved prices, normal validation/quarantine and optional current Yahoo sectors. Sector failure does not block signals. The engine never reads the private correction. Original archives/references and original frozen documents remain locally intact. An owner-only export creates a distinct public folder with labeled vendor-value omissions in historical prose, unchanged formulas/settings/prompts and separate public hashes. This is packaging, not Prompt 15, V2 or a revised backtest. No publication occurred.

## Public packaging verification — executed 2026-09-09

The public copy had no reference/sectors.csv, reference/data_corrections.json or historical archives. Twenty formula/data tests passed; twelve engine/public-integrity tests passed with two historical-archive tests explicitly skipped. Sector retrieval failure and anomaly quarantine were tested synthetically. An actual Yahoo network scan then downloaded all 50 stocks plus SPY, retrieved all 50 current sector labels, and generated 3 V0 / 2 V1 signals on the latest completed date, 2026-09-08. Zero invalid bars and zero historical corrections were applied. Five version records were correctly retrospective, with no completed outcomes; all test outputs stayed isolated and are not shipped. Initial sandbox network access failed; the authorized network-enabled retry succeeded. This was packaging validation, not a new performance comparison.

The public export explicitly omits historical vendor literals in FIRST_LIVE_RUN.md, FROZEN_SPECIFICATION.md and RESEARCH_LOG.md. Links to excluded generated charts become explicit omission notes in the public copy; reported numbers are unchanged. Reported research returns, mathematical definitions and all 14 original prompts remain intact; prompts compare byte-for-byte. The private original specification, lock, references and historical results are preserved. Socrates Mode is unchanged and available without market data. Publish only the final export and its manifest, not the private source workspace or generated test outputs.

Clean Python 3.13 environment creation and installation from the public requirements succeeded; pip check reported no broken requirements. Initial restricted ensurepip execution failed; the authorized environment-creation retry succeeded. No dependencies or research parameters were changed. Public release is ready for final owner authorization, with ownership/account decisions outstanding.

## 2026-09-14 — Fork maintenance: optional moomoo price source

Recorded by the fork owner (David Rodriguez, dwrod/ai-treasure-hunt), not by the original author. This entry satisfies constitution rules 11 and 14 for the fork; it does not amend the historical experiment.

Why: viewers who follow the video to a brokerage with paper trading need the engine to read prices from that brokerage's data API rather than an unofficial Yahoo scraper that rate-limits first runs. The requester is the fork owner; the original author has not yet reviewed this change.

What was added: `src/data_moomoo.py` (one forward-adjusted daily-bar request per symbol from the hosted moomoo Open API, returning the frame shape the engine already consumes), `src/moomoo_login.py` (browser login, OAuth 2.1 with PKCE, `quote:read` scope only, broader grants refused), a `--source {yahoo,moomoo}` flag, `price_source`/`entry_price_source` provenance fields on new SIGNAL and ENTRY events, AGENTS.md/CLAUDE.md for coding agents, and the package `cryptography` in a separate `requirements-moomoo.txt` for optional AppKey signing. Yahoo remains the default; frozen formulas, universe, timing and the historical lock are untouched; public-lock hashes were refreshed for README.md, START_HERE.md, SIGNAL_ENGINE.md, RESEARCH_LOG.md and src/run_signal_engine.py.

Evidence: replaying the 2026-09-08 scan on moomoo bars reproduces FIRST_LIVE_RUN membership (V0 NVDA, GS, UNH; V1 GS, UNH). Details and limits in MOOMOO_ADAPTER.md. No live 51-name moomoo run has been executed yet. No strategy claim changes.
