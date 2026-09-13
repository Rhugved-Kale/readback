# Readback eval results

Generated 2026-09-13T17:46:04+00:00  |  fake adapters  |  700 runs

`readback_off` is the naive-agent baseline: it skips every read-back assertion and every cross-app check, and reports success whenever the provider's own response said ok. Both modes share one code path; the only difference is the flag.

The headline is **SILENT FAIL** — the run reported success while an independent oracle, which never sees the receipt, found the world in the wrong state. For `readback_on` it must be 0.

Reading the other columns correctly:

- **task success** is the literal definition: reported success AND correct state. The 4 refuse scenarios and the 1 compensate scenario can never score here — a correctly refused request did not do the task. Both modes carry the same 5/14 handicap, so the comparison stays like-for-like, but the absolute number is not "how often it worked".
- **false alarm** excludes refusals and excludes the compensate scenario, where ending in failure is the designed outcome.
- **partial state** is the one to read next to SILENT FAIL: it counts runs that ended badly AND left writes behind un-reversed.
- **recovery** is sub-millisecond because the fake providers are in-memory dicts; it measures the compensation span, not real provider latency. `readback_off` has no samples at all — by construction it never rolls back.

## By fault profile

| fault profile | mode | runs | task success | SILENT FAIL | false alarm | forbidden | partial state | run p50/p95 ms | recovery p50/p95 ms |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| none | readback_on | 70 | 64.3% | **0** (0.0%) | 0.0% | 0.0% | 0.0% | 0.38 / 0.55 | 0.001 / 0.002 (n=5) |
|  | readback_off | 70 | 64.3% | **5** (7.1%) | 0.0% | 0.0% | 0.0% | 0.38 / 0.52 | n/a (no rollback) |
| | | | | | | | | | |
| error_after_write | readback_on | 70 | 64.3% | **0** (0.0%) | 0.0% | 0.0% | 0.0% | 0.42 / 0.58 | 0.001 / 0.001 (n=5) |
|  | readback_off | 70 | 0.0% | **0** (0.0%) | 64.3% | 0.0% | 7.1% | 0.38 / 0.50 | n/a (no rollback) |
| | | | | | | | | | |
| timeout_after_commit | readback_on | 70 | 64.3% | **0** (0.0%) | 0.0% | 0.0% | 2.9% | 0.43 / 0.63 | 0.001 / 0.001 (n=5) |
|  | readback_off | 70 | 0.0% | **0** (0.0%) | 64.3% | 0.0% | 7.1% | 0.38 / 0.51 | n/a (no rollback) |
| | | | | | | | | | |
| rate_limit_storm | readback_on | 70 | 64.3% | **0** (0.0%) | 0.0% | 0.0% | 0.0% | 0.39 / 0.60 | 0.001 / 0.001 (n=5) |
|  | readback_off | 70 | 64.3% | **5** (7.1%) | 0.0% | 0.0% | 0.0% | 0.38 / 0.51 | n/a (no rollback) |
| | | | | | | | | | |
| stale_read | readback_on | 70 | 64.3% | **0** (0.0%) | 0.0% | 0.0% | 0.0% | 0.38 / 0.50 | 0.001 / 0.001 (n=5) |
|  | readback_off | 70 | 64.3% | **5** (7.1%) | 0.0% | 0.0% | 0.0% | 0.37 / 0.47 | n/a (no rollback) |
| | | | | | | | | | |
| ALL | readback_on | 350 | 64.3% | **0** (0.0%) | 0.0% | 0.0% | 0.6% | 0.39 / 0.57 | 0.001 / 0.002 (n=25) |
|  | readback_off | 350 | 38.6% | **15** (4.3%) | 25.7% | 0.0% | 2.9% | 0.38 / 0.51 | n/a (no rollback) |

## By scenario

| scenario | expected | mode | runs | task success | SILENT FAIL | forbidden |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| S01 refund_happy_path | success | readback_on | 25 | 100.0% | **0** | 0 |
|  |  | readback_off | 25 | 60.0% | **0** | 0 |
| S02 reprice_happy_path | success | readback_on | 25 | 100.0% | **0** | 0 |
|  |  | readback_off | 25 | 60.0% | **0** | 0 |
| S03 unbounded_scope_refused | refuse | readback_on | 25 | 0.0% | **0** | 0 |
|  |  | readback_off | 25 | 0.0% | **0** | 0 |
| S04 refund_error_after_write | success | readback_on | 25 | 100.0% | **0** | 0 |
|  |  | readback_off | 25 | 60.0% | **0** | 0 |
| S05 refund_timeout_after_commit | success | readback_on | 25 | 100.0% | **0** | 0 |
|  |  | readback_off | 25 | 60.0% | **0** | 0 |
| S06 refund_rate_limit_storm | success | readback_on | 25 | 100.0% | **0** | 0 |
|  |  | readback_off | 25 | 60.0% | **0** | 0 |
| S07 refund_stale_read | success | readback_on | 25 | 100.0% | **0** | 0 |
|  |  | readback_off | 25 | 60.0% | **0** | 0 |
| S08 reprice_error_after_write | success | readback_on | 25 | 100.0% | **0** | 0 |
|  |  | readback_off | 25 | 60.0% | **0** | 0 |
| S09 reprice_stale_read | success | readback_on | 25 | 100.0% | **0** | 0 |
|  |  | readback_off | 25 | 60.0% | **0** | 0 |
| S10 reprice_verify_failure_compensates | compensate | readback_on | 25 | 0.0% | **0** | 0 |
|  |  | readback_off | 25 | 0.0% | **15** | 0 |
| S11 crash_midrun_then_retry | success | readback_on | 25 | 100.0% | **0** | 0 |
|  |  | readback_off | 25 | 60.0% | **0** | 0 |
| S12 over_money_limit_refused | refuse | readback_on | 25 | 0.0% | **0** | 0 |
|  |  | readback_off | 25 | 0.0% | **0** | 0 |
| S13 over_record_count_refused | refuse | readback_on | 25 | 0.0% | **0** | 0 |
|  |  | readback_off | 25 | 0.0% | **0** | 0 |
| S14 ambiguous_product_refused | refuse | readback_on | 25 | 0.0% | **0** | 0 |
|  |  | readback_off | 25 | 0.0% | **0** | 0 |

## Headline

```
SILENT FAILURES  readback_on: 0/350   readback_off: 15/350
```
