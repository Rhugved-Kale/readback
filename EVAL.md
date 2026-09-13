# Readback eval results

**1120 runs.** 14 scenarios × 8 fault profiles × 2 modes × 5 repeats, against in-memory
fakes. No network.

```
success_correctness       readback_on: 62.5% (360)    readback_off: 37.5% (360)
refusal_correctness       readback_on: 100.0% (160)   readback_off: 100.0% (160)
compensation_correctness  readback_on: 100.0% (40)    readback_off: 0.0% (40)
SILENT FAILURES  readback_on: 0/560   readback_off: 165/560
```

A **silent failure** is a run reporting success while an independent oracle found the world
wrong. Failing loudly costs a retry; lying costs a refund nobody knows about.

## Why the comparison is fair

`readback_off` is not a strawman. It is the *same code*: same planner, risk gate, WAL,
effect ordering, fakes, faults and seeds. One boolean skips the read-back assertions and
cross-app checks, reporting success when every `apply()` returned ok — what most agents do
today: believe the provider. One execution path, so every difference is attributable to
read-back alone.

The three `silent_*` profiles drive the gap. The other five fail visibly (500, timeout,
429) and even a naive agent notices. The silent ones return a plausible `200` while leaving
state wrong, so the response carries no signal; the baseline reports success on a broken
world 71.4% of the time. Read-back catches every one, because it looks. Note
`success_correctness` is 0% for **both** modes there — a dropped write cannot be completed
by anyone. Read-back just knows.

## By fault profile

| fault profile | mode | runs | success corr. | refusal corr. | compensation corr. | SILENT FAIL | false alarm | forbidden | partial state | run p50/p95 ms |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| none | readback_on | 70 | 100.0% (45) | 100.0% (20) | 100.0% (5) | **0** (0.0%) | 0.0% | 0.0% | 0.0% | 0.38 / 0.59 |
| | readback_off | 70 | 100.0% (45) | 100.0% (20) | 0.0% (5) | **5** (7.1%) | 0.0% | 0.0% | 0.0% | 0.37 / 0.58 |
| error_after_write | readback_on | 70 | 100.0% (45) | 100.0% (20) | 100.0% (5) | **0** (0.0%) | 0.0% | 0.0% | 0.0% | 0.45 / 0.60 |
| | readback_off | 70 | 0.0% (45) | 100.0% (20) | 0.0% (5) | **0** (0.0%) | 64.3% | 0.0% | 7.1% | 0.40 / 0.50 |
| timeout_after_commit | readback_on | 70 | 100.0% (45) | 100.0% (20) | 100.0% (5) | **0** (0.0%) | 0.0% | 0.0% | 0.0% | 0.43 / 0.56 |
| | readback_off | 70 | 0.0% (45) | 100.0% (20) | 0.0% (5) | **0** (0.0%) | 64.3% | 0.0% | 7.1% | 0.38 / 0.50 |
| rate_limit_storm | readback_on | 70 | 100.0% (45) | 100.0% (20) | 100.0% (5) | **0** (0.0%) | 0.0% | 0.0% | 0.0% | 0.38 / 0.51 |
| | readback_off | 70 | 100.0% (45) | 100.0% (20) | 0.0% (5) | **5** (7.1%) | 0.0% | 0.0% | 0.0% | 0.37 / 0.47 |
| stale_read | readback_on | 70 | 100.0% (45) | 100.0% (20) | 100.0% (5) | **0** (0.0%) | 0.0% | 0.0% | 0.0% | 0.38 / 0.51 |
| | readback_off | 70 | 100.0% (45) | 100.0% (20) | 0.0% (5) | **5** (7.1%) | 0.0% | 0.0% | 0.0% | 0.37 / 0.47 |
| **silent_write_drop** | readback_on | 70 | 0.0% (45) | 100.0% (20) | 100.0% (5) | **0** (0.0%) | 0.0% | 0.0% | 0.0% | 0.49 / 0.63 |
| | readback_off | 70 | 0.0% (45) | 100.0% (20) | 0.0% (5) | **50** (71.4%) | 0.0% | 0.0% | 0.0% | 0.37 / 0.51 |
| **silent_partial_write** | readback_on | 70 | 0.0% (45) | 100.0% (20) | 100.0% (5) | **0** (0.0%) | 0.0% | 0.0% | 0.0% | 0.48 / 0.57 |
| | readback_off | 70 | 0.0% (45) | 100.0% (20) | 0.0% (5) | **50** (71.4%) | 0.0% | 0.0% | 0.0% | 0.37 / 0.49 |
| **divergent_write** | readback_on | 70 | 0.0% (45) | 100.0% (20) | 100.0% (5) | **0** (0.0%) | 0.0% | 0.0% | 0.0% | 0.48 / 0.61 |
| | readback_off | 70 | 0.0% (45) | 100.0% (20) | 0.0% (5) | **50** (71.4%) | 0.0% | 0.0% | 0.0% | 0.37 / 0.49 |
| **ALL** | **readback_on** | **560** | **62.5% (360)** | **100.0% (160)** | **100.0% (40)** | **0 (0.0%)** | **0.0%** | **0.0%** | **0.0%** | 0.42 / 0.57 |
| | **readback_off** | **560** | **37.5% (360)** | **100.0% (160)** | **0.0% (40)** | **165 (29.5%)** | **16.1%** | **0.0%** | **1.8%** | 0.37 / 0.51 |

Each rate uses its own denominator (brackets), so a correct refusal is not a failed task.
`refusal_correctness` also requires the **right rule** to fire.

## Silent failures by scenario and profile (readback_off)

| scenario | silent_write_drop | silent_partial_write | divergent_write | none | rate_limit_storm | stale_read | total |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| S01 refund_happy_path | 5 | 5 | 5 | – | – | – | 15 |
| S02 reprice_happy_path | 5 | 5 | 5 | – | – | – | 15 |
| S04 refund_error_after_write | 5 | 5 | 5 | – | – | – | 15 |
| S05 refund_timeout_after_commit | 5 | 5 | 5 | – | – | – | 15 |
| S06 refund_rate_limit_storm | 5 | 5 | 5 | – | – | – | 15 |
| S07 refund_stale_read | 5 | 5 | 5 | – | – | – | 15 |
| S08 reprice_error_after_write | 5 | 5 | 5 | – | – | – | 15 |
| S09 reprice_stale_read | 5 | 5 | 5 | – | – | – | 15 |
| S10 reprice_verify_failure | 5 | 5 | 5 | 5 | 5 | 5 | 30 |
| S11 crash_midrun_then_retry | 5 | 5 | 5 | – | – | – | 15 |
| **total** | **50** | **50** | **50** | **5** | **5** | **5** | **165** |

`readback_on` is **0** in every cell above.

## Reproducing

```bash
python -m readback.evals.run --repeats 5
```

Run twice back to back, **both invocations produced identical results** across all 1120
runs — every outcome, oracle verdict and metric matched exactly (wall-clock latencies
aside). Any cell replays with `--scenario N --profile P --mode M --seed S`.

The judge is independent: `evals/oracle.py` imports no runner, no adapter `verify()` and no
cross-check, and never sees the receipt. It reads provider state directly and compares it
to each scenario's declared truth. Without that, a `verify()` hardcoded to `True` scores
100%.

## Limitations

- **Fakes are not providers.** Real Stripe has an async search index, body-bound
  idempotency keys, and replays returning stale objects — all of which broke the live
  adapters in ways this matrix cannot produce.
- **The live subset is 3 scenarios**, once each (`--live`). All 1120 here are fakes.
- **Recovery time is sub-microsecond** because rollback is dict deletion — not a production
  latency claim.
- **Silent profiles are synthetic.** The 71.4% rate reflects injection frequency, not field
  data.
- **62.5% success_correctness** is bounded by scenario mix, identically for both modes.
