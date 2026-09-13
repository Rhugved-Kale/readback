# Readback

An ops agent that executes multi-step requests across Stripe, Notion and Slack, then re-reads live state from every app it touched before reporting anything — and reverses its own writes when a read-back assertion fails.

## Why

The provider's response to a write is the least trustworthy thing in the system. A 500 often follows a write that committed; a 200 sometimes precedes one that did not. Readback never reports success from a return value — only from a fresh read of live state.

## Run it

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
pytest -q
python -m readback.cli --demo 1
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
