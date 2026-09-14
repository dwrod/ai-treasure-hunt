# Instructions for coding agents

This is a frozen research laboratory, not a trading system. Read README.md and
RESEARCH_CONSTITUTION.md before changing anything. Two locks apply:

- Files listed in FROZEN_LOCK.json are the historical record. Never edit them.
- Files listed in PUBLIC_RUNTIME_LOCK.json are public packaging. You may edit
  one only if you refresh its hash in that file in the same change and
  `python -m src.release_integrity` passes afterwards; the engine refuses to
  run otherwise. MOOMOO_ADAPTER.md shows the one-line refresh.

Do not edit or delete anything under output/, and never connect the engine to
live order placement. New questions belong in a separate experiment; start with
SOCRATES_MODE.md.

## Running the engine

```sh
python -m src.run_signal_engine            # Yahoo, the default
python -m src.run_signal_engine --source moomoo
python -m src.build_watchlist
python -m unittest discover -s tests
```

Run after the market close and before the next open if the user wants a
prospective journal record. See SIGNAL_ENGINE.md for what the outputs mean.
Results are research signals, not recommendations; say so when reporting them.

## Using the user's moomoo account

Two connections exist and each is a one-time browser approval on moomoo's own
login page. Never ask the user for a password, never type one, and never paste
a token into a repository file, a config file or a chat. The login helper keeps
its own token under .cache/, which git ignores.

1. **The engine's data source.** If `--source moomoo` fails with
   "moomoo credentials missing", run

   ```sh
   python -m src.moomoo_login
   ```

   and tell the user to approve the request in the browser that opens. Only the
   quote read scope is requested, and a broader grant is refused rather than
   stored. The token is stored under .cache/ and refreshes itself afterwards.
   If the port is busy, add `--port 0`. Environment variables `MOOMOO_ACCESS_TOKEN`, or
   `MOOMOO_API_KEY` plus `MOOMOO_PRIVATE_KEY_FILE`, take precedence when set.
   Details in MOOMOO_ADAPTER.md.

2. **Your own moomoo tools** (quotes, history, the paper account, order
   drafting), if the user wants them. Claude Code:

   ```sh
   claude mcp add moomoo-mcp --transport http https://mcp.moomoo.com/mcp
   ```

   Codex: add `[mcp_servers.moomoo]` with `url = "https://mcp.moomoo.com/mcp"`
   to the config, then `codex mcp login moomoo`. The first moomoo request opens
   the same approval page. Prefer the simulated (paper) account. Any order,
   paper or live, requires the user's explicit confirmation of that specific
   order; do not place orders on your own initiative.
