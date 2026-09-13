# Readback eval results

Generated 2026-09-13T18:00:37+00:00  |  fake adapters  |  1120 runs

`readback_off` is the naive-agent baseline: it skips every read-back assertion and every cross-app check, and reports success whenever the provider's own response said ok. Both modes share one code path; the only difference is the flag.

The headline is **SILENT FAIL** — the run reported success while an independent oracle, which never sees the receipt, found the world in the wrong state. For `readback_on` it must be 0.

Reading the other columns correctly:

- **task success** is the literal definition: reported success AND correct state. The 4 refuse scenarios and the 1 compensate scenario can never score here — a correctly refused request did not do the task. Both modes carry the same 5/14 handicap, so the comparison stays like-for-like, but the absolute number is not "how often it worked".
- **false alarm** excludes refusals and excludes the compensate scenario, where ending in failure is the designed outcome.
- **partial state** is the one to read next to SILENT FAIL: it counts runs that ended badly AND left writes behind un-reversed.
- **recovery** is sub-millisecond because the fake providers are in-memory dicts; it measures the compensation span, not real provider latency. `readback_off` has no samples at all — by construction it never rolls back.

## By fault profile

| fault profile | mode | runs | success corr. | refusal corr. | compensation corr. | SILENT FAIL | false alarm | forbidden | partial state | run p50/p95 ms | recovery p50/p95 ms |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| none | readback_on | 70 | 100.0% (45) | 100.0% (20) | 100.0% (5) | **0** (0.0%) | 0.0% | 0.0% | 0.0% | 0.38 / 0.59 | 0.001 / 0.001 (n=5) |
|  | readback_off | 70 | 100.0% (45) | 100.0% (20) | 0.0% (5) | **5** (7.1%) | 0.0% | 0.0% | 0.0% | 0.37 / 0.58 | n/a (no rollback) |
| | | | | | | | | | |
| error_after_write | readback_on | 70 | 100.0% (45) | 100.0% (20) | 100.0% (5) | **0** (0.0%) | 0.0% | 0.0% | 0.0% | 0.45 / 0.60 | 0.001 / 0.001 (n=5) |
|  | readback_off | 70 | 0.0% (45) | 100.0% (20) | 0.0% (5) | **0** (0.0%) | 64.3% | 0.0% | 7.1% | 0.40 / 0.50 | n/a (no rollback) |
| | | | | | | | | | |
| timeout_after_commit | readback_on | 70 | 100.0% (45) | 100.0% (20) | 100.0% (5) | **0** (0.0%) | 0.0% | 0.0% | 0.0% | 0.43 / 0.56 | 0.001 / 0.002 (n=5) |
|  | readback_off | 70 | 0.0% (45) | 100.0% (20) | 0.0% (5) | **0** (0.0%) | 64.3% | 0.0% | 7.1% | 0.38 / 0.50 | n/a (no rollback) |
| | | | | | | | | | |
| rate_limit_storm | readback_on | 70 | 100.0% (45) | 100.0% (20) | 100.0% (5) | **0** (0.0%) | 0.0% | 0.0% | 0.0% | 0.38 / 0.51 | 0.001 / 0.001 (n=5) |
|  | readback_off | 70 | 100.0% (45) | 100.0% (20) | 0.0% (5) | **5** (7.1%) | 0.0% | 0.0% | 0.0% | 0.37 / 0.47 | n/a (no rollback) |
| | | | | | | | | | |
| stale_read | readback_on | 70 | 100.0% (45) | 100.0% (20) | 100.0% (5) | **0** (0.0%) | 0.0% | 0.0% | 0.0% | 0.38 / 0.51 | 0.001 / 0.001 (n=5) |
|  | readback_off | 70 | 100.0% (45) | 100.0% (20) | 0.0% (5) | **5** (7.1%) | 0.0% | 0.0% | 0.0% | 0.37 / 0.47 | n/a (no rollback) |
| | | | | | | | | | |
| silent_write_drop | readback_on | 70 | 0.0% (45) | 100.0% (20) | 100.0% (5) | **0** (0.0%) | 0.0% | 0.0% | 0.0% | 0.49 / 0.63 | 0.001 / 0.002 (n=50) |
|  | readback_off | 70 | 0.0% (45) | 100.0% (20) | 0.0% (5) | **50** (71.4%) | 0.0% | 0.0% | 0.0% | 0.37 / 0.51 | n/a (no rollback) |
| | | | | | | | | | |
| silent_partial_write | readback_on | 70 | 0.0% (45) | 100.0% (20) | 100.0% (5) | **0** (0.0%) | 0.0% | 0.0% | 0.0% | 0.48 / 0.57 | 0.001 / 0.001 (n=50) |
|  | readback_off | 70 | 0.0% (45) | 100.0% (20) | 0.0% (5) | **50** (71.4%) | 0.0% | 0.0% | 0.0% | 0.37 / 0.49 | n/a (no rollback) |
| | | | | | | | | | |
| divergent_write | readback_on | 70 | 0.0% (45) | 100.0% (20) | 100.0% (5) | **0** (0.0%) | 0.0% | 0.0% | 0.0% | 0.48 / 0.61 | 0.001 / 0.001 (n=50) |
|  | readback_off | 70 | 0.0% (45) | 100.0% (20) | 0.0% (5) | **50** (71.4%) | 0.0% | 0.0% | 0.0% | 0.37 / 0.49 | n/a (no rollback) |
| | | | | | | | | | |
| ALL | readback_on | 560 | 62.5% (360) | 100.0% (160) | 100.0% (40) | **0** (0.0%) | 0.0% | 0.0% | 0.0% | 0.42 / 0.57 | 0.001 / 0.001 (n=175) |
|  | readback_off | 560 | 37.5% (360) | 100.0% (160) | 0.0% (40) | **165** (29.5%) | 16.1% | 0.0% | 1.8% | 0.37 / 0.51 | n/a (no rollback) |

## By scenario

| scenario | expected | mode | runs | task success | SILENT FAIL | forbidden |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| S01 refund_happy_path | success | readback_on | 40 | 62.5% | **0** | 0 |
|  |  | readback_off | 40 | 37.5% | **15** | 0 |
| S02 reprice_happy_path | success | readback_on | 40 | 62.5% | **0** | 0 |
|  |  | readback_off | 40 | 37.5% | **15** | 0 |
| S03 unbounded_scope_refused | refuse | readback_on | 40 | 0.0% | **0** | 0 |
|  |  | readback_off | 40 | 0.0% | **0** | 0 |
| S04 refund_error_after_write | success | readback_on | 40 | 62.5% | **0** | 0 |
|  |  | readback_off | 40 | 37.5% | **15** | 0 |
| S05 refund_timeout_after_commit | success | readback_on | 40 | 62.5% | **0** | 0 |
|  |  | readback_off | 40 | 37.5% | **15** | 0 |
| S06 refund_rate_limit_storm | success | readback_on | 40 | 62.5% | **0** | 0 |
|  |  | readback_off | 40 | 37.5% | **15** | 0 |
| S07 refund_stale_read | success | readback_on | 40 | 62.5% | **0** | 0 |
|  |  | readback_off | 40 | 37.5% | **15** | 0 |
| S08 reprice_error_after_write | success | readback_on | 40 | 62.5% | **0** | 0 |
|  |  | readback_off | 40 | 37.5% | **15** | 0 |
| S09 reprice_stale_read | success | readback_on | 40 | 62.5% | **0** | 0 |
|  |  | readback_off | 40 | 37.5% | **15** | 0 |
| S10 reprice_verify_failure_compensates | compensate | readback_on | 40 | 0.0% | **0** | 0 |
|  |  | readback_off | 40 | 0.0% | **30** | 0 |
| S11 crash_midrun_then_retry | success | readback_on | 40 | 62.5% | **0** | 0 |
|  |  | readback_off | 40 | 37.5% | **15** | 0 |
| S12 over_money_limit_refused | refuse | readback_on | 40 | 0.0% | **0** | 0 |
|  |  | readback_off | 40 | 0.0% | **0** | 0 |
| S13 over_record_count_refused | refuse | readback_on | 40 | 0.0% | **0** | 0 |
|  |  | readback_off | 40 | 0.0% | **0** | 0 |
| S14 ambiguous_product_refused | refuse | readback_on | 40 | 0.0% | **0** | 0 |
|  |  | readback_off | 40 | 0.0% | **0** | 0 |

## Headline

```
success_correctness       readback_on: 62.5% (360)    readback_off: 37.5% (360)
refusal_correctness       readback_on: 100.0% (160)   readback_off: 100.0% (160)
compensation_correctness  readback_on: 100.0% (40)    readback_off: 0.0% (40)
SILENT FAILURES  readback_on: 0/560   readback_off: 165/560
```

## Silent failure breakdown (readback_off)

| scenario | fault profile | silent failures |
| --- | --- | ---: |
| S01 refund_happy_path | divergent_write | 5 |
| S01 refund_happy_path | silent_partial_write | 5 |
| S01 refund_happy_path | silent_write_drop | 5 |
| S02 reprice_happy_path | divergent_write | 5 |
| S02 reprice_happy_path | silent_partial_write | 5 |
| S02 reprice_happy_path | silent_write_drop | 5 |
| S04 refund_error_after_write | divergent_write | 5 |
| S04 refund_error_after_write | silent_partial_write | 5 |
| S04 refund_error_after_write | silent_write_drop | 5 |
| S05 refund_timeout_after_commit | divergent_write | 5 |
| S05 refund_timeout_after_commit | silent_partial_write | 5 |
| S05 refund_timeout_after_commit | silent_write_drop | 5 |
| S06 refund_rate_limit_storm | divergent_write | 5 |
| S06 refund_rate_limit_storm | silent_partial_write | 5 |
| S06 refund_rate_limit_storm | silent_write_drop | 5 |
| S07 refund_stale_read | divergent_write | 5 |
| S07 refund_stale_read | silent_partial_write | 5 |
| S07 refund_stale_read | silent_write_drop | 5 |
| S08 reprice_error_after_write | divergent_write | 5 |
| S08 reprice_error_after_write | silent_partial_write | 5 |
| S08 reprice_error_after_write | silent_write_drop | 5 |
| S09 reprice_stale_read | divergent_write | 5 |
| S09 reprice_stale_read | silent_partial_write | 5 |
| S09 reprice_stale_read | silent_write_drop | 5 |
| S10 reprice_verify_failure_compensates | divergent_write | 5 |
| S10 reprice_verify_failure_compensates | none | 5 |
| S10 reprice_verify_failure_compensates | rate_limit_storm | 5 |
| S10 reprice_verify_failure_compensates | silent_partial_write | 5 |
| S10 reprice_verify_failure_compensates | silent_write_drop | 5 |
| S10 reprice_verify_failure_compensates | stale_read | 5 |
| S11 crash_midrun_then_retry | divergent_write | 5 |
| S11 crash_midrun_then_retry | silent_partial_write | 5 |
| S11 crash_midrun_then_retry | silent_write_drop | 5 |
| **total** | | **165** |
