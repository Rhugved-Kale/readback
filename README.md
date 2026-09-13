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

The CLI and the tests run against in-memory fake adapters: no network, no credentials.

## Layout

| Path | What it is |
| --- | --- |
| `SCENARIOS.md` | The 14 scenarios the eval harness runs |
| `src/readback/adapters/base.py` | The four-method adapter contract |
| `src/readback/adapters/fake.py` | In-memory adapter + fault injection |
| `src/readback/core/wal.py` | fsynced append-only write-ahead log |
| `src/readback/core/riskgate.py` | Scope / count / money thresholds |
| `src/readback/core/runner.py` | plan → gate → apply → read back → compensate |
| `src/readback/core/receipt.py` | JSON + text run receipts |
| `src/readback/seed.py` | Real-API seed script (run manually) |

## TODO

- [ ] Implement `StripeAdapter`, `NotionAdapter` and `SlackAdapter` against the real APIs — each currently raises `NotImplementedError` with the exact call it will make.
- [ ] Replace the hardcoded regex table in `planner.py` with Anthropic tool-use parsing (see the module docstring for the constraints that must survive the swap).
- [ ] Build the eval harness that runs all 14 scenarios in `SCENARIOS.md` and asserts the expected outcome for each.
- [ ] Decide the honest compensation story for irreversible effects (a Stripe refund has no inverse).
