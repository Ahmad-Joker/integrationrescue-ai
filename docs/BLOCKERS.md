# Blockers

1. **No live model access.** `ANTHROPIC_API_KEY` unset and `ant` CLI not installed. Live agent mode cannot be run or
   evaluated. Recovery: founder provides a key in `.env` / environment (or installs `ant` and runs `ant auth login`),
   then `cd backend; ..\.venv\Scripts\python -m integrationrescue.evaluation --provider claude --seeds 101`.
   Expected cost is small but non-zero; default cap 30 model calls per incident.
2. ~~No GitHub remote~~ — resolved 2026-10-31: public repo https://github.com/Ahmad-Joker/integrationrescue-ai.
3. **Docker Desktop fails to start** (WSL bootstrap error). Not needed for the prototype; affects container isolation.
4. **Official competition rules not verified** — press reports conflict on the deadline.
