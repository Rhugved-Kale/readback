# Reliability brief

## The problem

Agents report success from what the provider said during the write. They rarely read the state afterwards. So state diverges across apps, quietly, and nobody finds out until a customer does.

## What Readback does

Readback runs multi-step ops requests across Stripe, Notion and Slack. Once every effect is applied, it re-reads live state from each app with a fresh request. It then runs cross-app checks that read a fact from a different app than wrote it. Success is reported only when every read-back and cross-app check passes. Otherwise it walks its write-ahead log backwards and reverses what it committed.

## Architecture

### Uniform adapter interface

Every app sits behind one shape: `plan`, `apply`, `verify`, `compensate`. Stripe, Notion, Slack and the in-memory fake implement the same four, so the runner never knows which provider it is talking to. That lets the harness swap real for fake and measure the loop, not the vendor.

### Write-ahead log

Intent is fsynced to `runs/{run_id}/wal.jsonl` before the provider call, not after. Every effect carries an idempotency key derived from the logical write (order id, product key), never a timestamp, and on retry anything already COMMITTED is skipped. A crash between the write landing and me hearing about it is what this is for.

### Read-back

`verify()` issues a new request every time and never inspects what `apply()` returned, because the provider's response is the thing under suspicion. Using it would make read-back a tautology. It resolves its target from the effect, so a restarted process reaches the same verdict from the log.

### Cross-app checks

Per-effect verify catches a dropped write, but not every write landing while the apps disagree. `price_coherence` reads Stripe's live `default_price` against the Notion catalog row's number and price id. `refund_coherence` compares Stripe's refunded total to the Notion audit row Amount, so neither app confirms its own claim.

### Compensation and irreversibility

Reversible effects roll back from state captured before the write. A refund cannot, so irreversible effects run last and a failing plan gets its best chance to fail while rollback is total. If a run fails after one committed, it reverses the rest and reports PARTIAL_MANUAL_REMEDIATION naming the exact Stripe object, never success.

### Risk gate

Three rules run before the first provider call: unbounded scope, effect count over 5, money over $500. A held plan costs zero writes and posts to Slack with the rule, the threshold, the order ids and the total, plus Approve and Cancel. An approved run keeps `hold` and adds RELEASED BY, so an overridden run is never mistaken for a safe one.

## How I know it works

1120 runs. With read-back on, 0 of 560 reported success while the world was wrong; with it off, 165 of 560 did. Same planner, same executor, same fakes, same seeds, one boolean. The judge is independent: no runner, no adapter verify, no cross-check, and it never sees the receipt, so a `verify()` hardcoded to True scores zero. Both matrix runs were byte-identical, and a stranger reproduces it in a minute, no credentials. See [EVAL.md](EVAL.md).

## What the build found

**The WAL masked a committed write.** A retry logs intent before consulting the log, so a fresh INTENDED record sat on an earlier COMMITTED one and the guard re-applied the write. The crash-recovery test caught it, which is what the log is for.

**I trusted a field on a write response.** Stripe's idempotent replay returns a price as first created, `active=true`, even after compensation archived it. I promoted that stale object and three live runs failed before I read it back fresh. That is the mistake this project exists to prevent, in my own `apply()`.

**The test suite went green on nothing.** With a hardcoded refund order, the first run spent it and later runs re-refunded an already-refunded charge. Stripe rejected the duplicate, but verify passed on state an earlier run created, so the refund path went untested. Tests now claim a fresh order each run.

**A 13.6% forbidden-effect rate was instrument error.** The fake adapter ignored the irreversibility flag and deleted a refund record the real Stripe adapter refuses to touch. The runner was correct and production never broke the invariant, so a contract test now drives fake and real through one set of assertions.

## Limitations

Request parsing is hardcoded regex shapes, not an LLM. Fakes are not providers, and live coverage is a subset. Recovery times are sub-microsecond because fake state is a dict in memory, so they are not a latency claim. The three silent fault profiles are synthetic. Under injection, Notion's verify expects the drifted value, so each app stays internally consistent; that is deliberate, and it leaves only the cross-app check able to see the gap. One operator, one run at a time.
