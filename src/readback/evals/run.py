"""Eval harness entry point.

    python -m readback.evals.run                 full fake matrix (default)
    python -m readback.evals.run --repeats 3
    python -m readback.evals.run --scenario 10 --profile none --mode readback_off
    python -m readback.evals.run --live          3 scenarios once each, real APIs

Writes evals/results/{summary.md,results.json,failures.md} and prints the
summary table, ending with the headline SILENT FAILURES line.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from . import faults as faults_mod
from .metrics import aggregate, by_mode_and_profile
from .runner import MODE_OFF, MODE_ON, MODES, RunRecord, run_matrix
from .scenarios import SCENARIOS, by_id

RESULTS_DIR = Path("evals/results")

#: Orders the live subset may touch. NEVER 4417-4419 -- those are the demo's,
#: and a refund cannot be undone.
LIVE_POOL_LOW, LIVE_POOL_HIGH = 9001, 9020
DEMO_ORDERS = frozenset({"4417", "4418", "4419"})

#: The live subset: one refund, one reprice, one compensating run.
LIVE_SCENARIO_IDS = (1, 2, 10)


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------


def _pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def summary_table(records: list[RunRecord], profiles: tuple[str, ...]) -> str:
    """readback_on beside readback_off, one row per fault profile."""
    grouped = by_mode_and_profile(records, MODES, profiles)
    lines: list[str] = []

    lines.append("| fault profile | mode | runs | task success | SILENT FAIL | false alarm | forbidden | partial state | run p50/p95 ms | recovery p50/p95 ms |")
    lines.append("| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")

    for profile in list(profiles) + ["ALL"]:
        for mode in MODES:
            m = grouped[mode][profile]
            if not m.total:
                continue
            name = profile if mode == MODE_ON else ""
            lines.append(
                f"| {name} | {mode} | {m.total} | {_pct(m.task_success_rate)} | "
                f"**{m.silent_failures}** ({_pct(m.silent_failure_rate)}) | "
                f"{_pct(m.false_alarm_rate)} | {_pct(m.forbidden_effect_rate)} | "
                f"{_pct(m.partial_state_rate)} | "
                f"{m.run_latency_p50:.2f} / {m.run_latency_p95:.2f} | "
                + (
                    f"{m.recovery_p50:.3f} / {m.recovery_p95:.3f} (n={m.recovery_samples}) |"
                    if m.recovery_samples
                    else "n/a (no rollback) |"
                )
            )
        if profile != "ALL":
            lines.append("| | | | | | | | | | |")
    return "\n".join(lines)


def per_scenario_table(records: list[RunRecord]) -> str:
    lines = ["| scenario | expected | mode | runs | task success | SILENT FAIL | forbidden |",
             "| --- | --- | --- | ---: | ---: | ---: | ---: |"]
    for scenario in SCENARIOS:
        for mode in MODES:
            subset = [r for r in records if r.scenario_id == scenario.id and r.mode == mode]
            if not subset:
                continue
            m = aggregate(f"S{scenario.id}", subset)
            label = f"S{scenario.id:02d} {scenario.name}" if mode == MODE_ON else ""
            expected = scenario.expected_outcome if mode == MODE_ON else ""
            lines.append(
                f"| {label} | {expected} | {mode} | {m.total} | {_pct(m.task_success_rate)} | "
                f"**{m.silent_failures}** | {m.forbidden} |"
            )
    return "\n".join(lines)


def write_reports(
    records: list[RunRecord], profiles: tuple[str, ...], out_dir: Path, live: bool
) -> tuple[str, str]:
    out_dir.mkdir(parents=True, exist_ok=True)

    on = [r for r in records if r.mode == MODE_ON]
    off = [r for r in records if r.mode == MODE_OFF]
    silent_on = sum(1 for r in on if r.silent_failure)
    silent_off = sum(1 for r in off if r.silent_failure)

    table = summary_table(records, profiles)
    headline = (
        f"SILENT FAILURES  readback_on: {silent_on}/{len(on)}   "
        f"readback_off: {silent_off}/{len(off)}"
    )

    # -- summary.md ---------------------------------------------------------
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    summary = [
        "# Readback eval results",
        "",
        f"Generated {stamp}  |  {'LIVE subset' if live else 'fake adapters'}  |  "
        f"{len(records)} runs",
        "",
        "`readback_off` is the naive-agent baseline: it skips every read-back "
        "assertion and every cross-app check, and reports success whenever the "
        "provider's own response said ok. Both modes share one code path; the "
        "only difference is the flag.",
        "",
        "The headline is **SILENT FAIL** — the run reported success while an "
        "independent oracle, which never sees the receipt, found the world in the "
        "wrong state. For `readback_on` it must be 0.",
        "",
        "Reading the other columns correctly:",
        "",
        "- **task success** is the literal definition: reported success AND correct "
        "state. The 4 refuse scenarios and the 1 compensate scenario can never "
        "score here — a correctly refused request did not do the task. Both modes "
        "carry the same 5/14 handicap, so the comparison stays like-for-like, but "
        "the absolute number is not \"how often it worked\".",
        "- **false alarm** excludes refusals and excludes the compensate scenario, "
        "where ending in failure is the designed outcome.",
        "- **partial state** is the one to read next to SILENT FAIL: it counts runs "
        "that ended badly AND left writes behind un-reversed.",
        "- **recovery** is sub-millisecond because the fake providers are in-memory "
        "dicts; it measures the compensation span, not real provider latency. "
        "`readback_off` has no samples at all — by construction it never rolls back.",
        "",
        "## By fault profile",
        "",
        table,
        "",
        "## By scenario",
        "",
        per_scenario_table(records),
        "",
        "## Headline",
        "",
        "```",
        headline,
        "```",
        "",
    ]
    (out_dir / "summary.md").write_text("\n".join(summary), encoding="utf-8")

    # -- results.json -------------------------------------------------------
    grouped = by_mode_and_profile(records, MODES, profiles)
    payload = {
        "generated_at": stamp,
        "live": live,
        "total_runs": len(records),
        "headline": headline,
        "metrics": {
            mode: {profile: m.to_dict() for profile, m in per_profile.items()}
            for mode, per_profile in grouped.items()
        },
        "runs": [r.to_dict() for r in records],
    }
    (out_dir / "results.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

    # -- failures.md --------------------------------------------------------
    disagreements = [
        r for r in records
        if r.silent_failure or r.false_alarm or r.forbidden or r.error
    ]
    failure_lines = [
        "# Runs where the oracle disagreed with the reported outcome",
        "",
        "Every entry is reproducible from its seed with the command shown.",
        "",
    ]
    if not disagreements:
        failure_lines.append("None. The reported outcome matched independent "
                             "state on every run, and no forbidden effect occurred.")
    for record in disagreements:
        kinds = []
        if record.silent_failure:
            kinds.append("SILENT FAILURE")
        if record.false_alarm:
            kinds.append("false alarm")
        if record.forbidden:
            kinds.append("forbidden effect")
        if record.error:
            kinds.append("harness error")
        failure_lines += [
            f"## S{record.scenario_id:02d} {record.scenario_name} — {', '.join(kinds)}",
            "",
            f"- mode: `{record.mode}`",
            f"- fault: `{record.profile}`" + (f" @ `{record.target_app}`" if record.target_app else ""),
            f"- seed: `{record.seed}`  (repeat {record.repeat})",
            f"- reported: `{record.reported_outcome}` — {record.reported_reason[:200]}",
            f"- oracle: `{'correct' if record.oracle_correct else 'WRONG'}` — {record.oracle_detail[:300]}",
        ]
        if record.forbidden:
            failure_lines.append("- forbidden: " + "; ".join(record.forbidden[:4]))
        if record.error:
            failure_lines.append(f"- error: `{record.error}`")
        failure_lines += ["", "```bash", record.repro(), "```", ""]
    (out_dir / "failures.md").write_text("\n".join(failure_lines), encoding="utf-8")

    return table, headline


# ---------------------------------------------------------------------------
# Live subset
# ---------------------------------------------------------------------------


def _live_pool() -> list[str]:
    """Unrefunded 9xxx orders. Never consults or touches the demo range."""
    import stripe as stripe_sdk
    from ..adapters.stripe_adapter import find_payment_intents_by_order

    stripe_sdk.api_key = os.environ["STRIPE_SECRET_KEY"]
    usable: list[str] = []
    for number in range(LIVE_POOL_LOW, LIVE_POOL_HIGH + 1):
        order_id = str(number)
        assert order_id not in DEMO_ORDERS, "pool must never include a demo order"
        for intent in find_payment_intents_by_order(stripe_sdk, order_id):
            if intent.status != "succeeded":
                continue
            refunded = sum(
                int(r.amount)
                for r in stripe_sdk.Refund.list(payment_intent=intent.id, limit=100).data
                if r.status == "succeeded"
            )
            if refunded == 0:
                usable.append(order_id)
                break
    return usable


def run_live(out_dir: Path) -> int:
    """Three scenarios, once each, against real providers.

    Fails loudly rather than falling back to demo data: burning a demo order
    costs a re-shoot, and no eval result is worth that.
    """
    from dotenv import load_dotenv

    from ..adapters.live import build_live_adapters, missing_env

    load_dotenv()
    gaps = missing_env()
    if gaps:
        print(f"ERROR: --live needs these env vars: {', '.join(gaps)}", file=sys.stderr)
        return 2

    pool = _live_pool()
    needed = 2  # scenario 1 and scenario 10 each consume one order
    if len(pool) < needed:
        print(
            f"ERROR: only {len(pool)} unrefunded order(s) in {LIVE_POOL_LOW}-{LIVE_POOL_HIGH}; "
            f"need {needed}. Run `python -m readback.seed --orders "
            f"{LIVE_POOL_LOW}-{LIVE_POOL_HIGH}` to replenish. "
            f"REFUSING to fall back to demo orders {sorted(DEMO_ORDERS)}.",
            file=sys.stderr,
        )
        return 2

    print(f"live pool: {len(pool)} unrefunded order(s) available; using {pool[:needed]}")
    print("NOTE: the live subset asserts reported outcomes only. The fake-adapter")
    print("      oracle cannot read real provider state, so silent-failure rate is")
    print("      measured on the fake matrix, which is where the baseline lives.\n")

    from ..core.runner import run as run_request

    results = []
    order_index = 0
    for scenario_id in LIVE_SCENARIO_IDS:
        scenario = by_id(scenario_id)
        request = scenario.request
        if "4417" in request:
            request = request.replace("4417", pool[order_index])
            order_index += 1
        run_id = f"eval_live_{scenario_id}_{os.urandom(3).hex()}"
        adapters = build_live_adapters(run_id)
        receipt = run_request(
            request, adapters=adapters, run_id=run_id,
            root=str(out_dir / "live_runs"), readback=True,
        )
        ok = receipt.outcome in ("success", "failure", "partial_manual_remediation")
        results.append((scenario, request, receipt))
        print(f"  S{scenario_id:02d} {scenario.name}: {receipt.outcome.upper()}")
        for check in receipt.crosschecks:
            print(f"       cross-check [{'PASS' if check.passed else 'FAIL'}] {check.name}")

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "live.md").write_text(
        "\n".join(
            ["# Live eval subset", ""]
            + [
                f"- **S{s.id:02d} {s.name}** — request `{req}` → `{r.outcome}`\n"
                f"  - {r.reason[:300]}"
                for s, req, r in results
            ]
        ),
        encoding="utf-8",
    )
    print(f"\nwrote {out_dir / 'live.md'}")
    return 0


# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="readback.evals.run",
        description="Run the Readback eval matrix.",
    )
    parser.add_argument("--repeats", type=int, default=5, help="repeats per cell (default 5)")
    parser.add_argument("--scenario", type=int, help="run a single scenario id")
    parser.add_argument("--profile", choices=faults_mod.PROFILES, help="run a single fault profile")
    parser.add_argument("--mode", choices=MODES, help="run a single mode")
    parser.add_argument("--seed", type=int, help="base seed (default 1000)")
    parser.add_argument("--out", default=str(RESULTS_DIR), help="results directory")
    parser.add_argument("--live", action="store_true", help="run the live subset instead")
    args = parser.parse_args(argv)

    out_dir = Path(args.out)

    if args.live:
        return run_live(out_dir)

    scenarios = [by_id(args.scenario)] if args.scenario else SCENARIOS
    profiles = (args.profile,) if args.profile else faults_mod.PROFILES
    modes = (args.mode,) if args.mode else MODES

    total = len(scenarios) * len(profiles) * len(modes) * args.repeats
    print(
        f"Running {total} cells: {len(scenarios)} scenario(s) x {len(profiles)} fault "
        f"profile(s) x {len(modes)} mode(s) x {args.repeats} repeat(s)\n"
    )

    records = run_matrix(
        repeats=args.repeats,
        scenarios=scenarios,
        profiles=profiles,
        modes=modes,
        base_seed=args.seed if args.seed is not None else 1000,
    )

    table, headline = write_reports(records, profiles, out_dir, live=False)

    print()
    print(table)
    print()
    print(f"wrote {out_dir/'summary.md'}, {out_dir/'results.json'}, {out_dir/'failures.md'}")
    print()
    print(headline)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
