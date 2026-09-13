# Readback

## Reproduce our numbers in 60 seconds

**No credentials. No `.env`. No network. No API keys.** The eval harness runs entirely
against in-memory fake providers.

```bash
git clone https://github.com/Rhugved-Kale/readback.git
cd readback
python3.11 -m venv .venv          # Python 3.11+ required
.venv/bin/pip install -r requirements.txt
.venv/bin/pip install -e .
.venv/bin/python -m readback.evals.run
```

Expected final lines:

```
success_correctness       readback_on: 62.5% (360)    readback_off: 37.5% (360)
refusal_correctness       readback_on: 100.0% (160)   readback_off: 100.0% (160)
compensation_correctness  readback_on: 100.0% (40)    readback_off: 0.0% (40)
SILENT FAILURES  readback_on: 0/560   readback_off: 165/560
```

1120 runs: 14 scenarios × 8 fault profiles × 2 modes × 5 repeats. Deterministic —
two invocations produce identical results. Typical timing on a laptop: **~8s setup,
~1s to run**, once the clone and download are done.

**`python3.11` is not optional.** On macOS `python3` is 3.9, which cannot resolve the
pinned dependencies. If `python3.11` is missing: `brew install python@3.11`.

Full results, methodology and limitations: **[EVAL.md](EVAL.md)**.

---

An ops agent that executes multi-step requests across Stripe, Notion and Slack, then re-reads live state from every app it touched before reporting anything — and reverses its own writes when a read-back assertion fails.

## Why

The provider's response to a write is the least trustworthy thing in the system. A 500 often follows a write that committed; a 200 sometimes precedes one that did not. Readback never reports success from a return value — only from a fresh read of live state.

## Run it

```bash
python3.11 -m venv .venv && source .venv/bin/activate   # 3.11+ required
pip install -r requirements.txt
pip install -e .
pytest -q
python -m readback.cli --demo 1
python -m readback.evals.run          # the eval harness — no credentials needed
```

The CLI and the default test run use in-memory fake adapters: no network, no credentials.
Add `--live` to run against real Stripe/Notion/Slack (requires `.env`, spends real
money, posts publicly). The live tests are deselected by default — `pytest -m live`.

## Order ID ranges — the rule

| Range | Who may touch it |
| --- | --- |
| `4417`, `4418`, `4419` | **Demo only.** Reserved for the demo video. No test, no eval run, no scratch run. |
| `9001`–`9020` | **Test/eval only.** The live suite and the eval harness use this range exclusively. |

```bash
python -m readback.seed --orders 9001-9020
```

Creates 20 refundable $99 test-mode PaymentIntents. Burn them freely and re-run
to replenish. The separation exists because **refunds cannot be undone** — a test
pointed at a demo order costs a re-shoot.

```bash
python -m readback.reset
```

Restores demo starting state (Pro back to $99, catalog and audit log cleaned,
recent bot messages removed, spent demo orders replaced) so a take can be
repeated. Safe to run repeatedly.

## Layout

| Path | What it is |
| --- | --- |
| `SCENARIOS.md` | The 14 scenarios the eval harness runs |
| `src/readback/adapters/base.py` | The four-method adapter contract |
| `src/readback/adapters/fake.py` | In-memory adapter + fault injection |
| `src/readback/adapters/{stripe,notion,slack}_adapter.py` | The three live adapters |
| `src/readback/core/retry.py` | Shared backoff: 429/5xx only, never 4xx |
| `src/readback/core/crosscheck.py` | Assertions that read one app to test another's claim |
| `src/readback/core/wal.py` | fsynced append-only write-ahead log |
| `src/readback/core/riskgate.py` | Scope / count / money thresholds |
| `src/readback/core/runner.py` | plan → gate → apply → read back → compensate |
| `src/readback/core/receipt.py` | JSON + text run receipts |
| `src/readback/seed.py` | Real-API seed script (run manually) |
| `src/readback/reset.py` | Restores demo starting state between takes |

## TODO

- [ ] Replace the hardcoded regex table in `planner.py` with Anthropic tool-use parsing (see the module docstring for the constraints that must survive the swap).
- [ ] Build the eval harness that runs all 14 scenarios in `SCENARIOS.md` and asserts the expected outcome for each.
- [ ] Run the live suite (`pytest -m live`) — written but never yet executed against real APIs.
- [ ] Surface `PARTIAL_MANUAL_REMEDIATION` runs somewhere durable; a Slack post is easy to miss.
