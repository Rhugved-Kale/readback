# Readback

An ops agent in Slack that re-reads the state of every app it touched before it reports anything.

**Demo video:** https://drive.google.com/file/d/1kgxf09QgJB5-Mln5helpTa0uFVhgxFhF/view?usp=sharing

## The three apps

- **Stripe** (test mode): payments and prices
- **Notion**: product catalog and audit log
- **Slack**: the interface, and where it posts what it did

## Results

```
success_correctness       readback_on: 62.5% (360)    readback_off: 37.5% (360)
refusal_correctness       readback_on: 100.0% (160)   readback_off: 100.0% (160)
compensation_correctness  readback_on: 100.0% (40)    readback_off: 0.0% (40)
SILENT FAILURES  readback_on: 0/560   readback_off: 165/560
```

A silent failure is a run that reported success while an independent oracle found the world in the wrong state.

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

1120 runs: 14 scenarios, 8 fault profiles, 2 modes, 5 repeats. Deterministic, so two
invocations produce identical results. Typical timing on a laptop: **~8s setup,
~1s to run**, once the clone and download are done.

**`python3.11` is not optional.** On macOS `python3` is 3.9, which cannot resolve the
pinned dependencies. If `python3.11` is missing: `brew install python@3.11`.

Full results, methodology and limitations: **[EVAL.md](EVAL.md)**.

## What it does

1. Plans the request into a list of effects, one per app.
2. Runs a risk gate on the plan before any provider call.
3. Writes intent to a write-ahead log, fsynced, before each write.
4. Executes, sending an idempotency key wherever the provider supports one.
5. Reads back from every app it touched, with a fresh request each time.
6. Runs cross-app checks that read a fact from a different app than the one that wrote it, then reports success or reverses everything it committed.

## The three demo requests

**`refund order 4417 and log the reason`**
The happy path. Stripe refund, Notion audit row, Slack post, then three read-backs and a cross-app check that the audit amount matches what Stripe says was refunded.

**`move Pro to $79 everywhere`**
A change that has to land in three places at once. The cross-app check compares Stripe's live default price against the number in the Notion catalog.

**`move Team to $59 everywhere --inject notion_drift`**
A deliberate fault. Notion commits a price that disagrees with Stripe, both return success, and each app is internally consistent. Only the cross-app check sees it. Every surface is labelled FAULT INJECTED, and injection is refused unless `READBACK_ALLOW_INJECTION=1`.

## More

- **[BRIEF.md](BRIEF.md)**: how it works and what the build found.
- **[EVAL.md](EVAL.md)**: the numbers, the method, the limitations.
- **[SCENARIOS.md](SCENARIOS.md)**: the 14 eval scenarios.

---

## Full setup

The eval harness and the unit tests need nothing. Running against real providers needs
credentials.

```bash
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
pytest -q
python -m readback.cli --demo 1
```

Copy `.env.example` to `.env` and fill in:

```
STRIPE_SECRET_KEY           Stripe test-mode secret key (sk_test_...)
NOTION_TOKEN                Notion integration token
NOTION_CATALOG_DB           Notion database id for the product catalog
NOTION_AUDIT_DB             Notion database id for the audit log
SLACK_BOT_TOKEN             Slack bot token (xoxb-...)
SLACK_APP_TOKEN             Slack app-level token for Socket Mode (xapp-...)
SLACK_CHANNEL_ID            the channel Readback listens in
ANTHROPIC_API_KEY           reserved for LLM parsing, not used yet
READBACK_ALLOW_INJECTION    set to 1 to allow deliberate fault injection
```

Seed the providers once, then run the Slack app:

```bash
python -m readback.seed                        # products, prices, catalog rows, demo orders
python -m readback.seed --orders 9001-9020     # 20 refundable test orders for evals
python -m readback.slack_app                   # Socket Mode listener
```

Trigger it with an @mention or a message starting with `readback:`.

Other commands:

```bash
python -m readback.cli "refund order 4417 and log the reason" --live
python -m readback.reset      # restore demo starting state between takes
pytest -m live                # live suite, deselected by default
```

## Order range rule

| Range | Who may touch it |
| --- | --- |
| 4417 to 4419 | Demo only. No test, no eval run. |
| 9001 to 9020 | Eval and live tests only. |

A refund cannot be undone. A test pointed at a demo order spends it, and the next take
has to rebuild it by hand. `python -m readback.seed --orders 9001-9020` replenishes the
eval range. The Slack app refuses any request naming an order in it.

## Provenance

Built during the hackathon window. The git history reflects it, including the wrong
turns.
