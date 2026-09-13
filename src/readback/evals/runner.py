"""Executes the eval matrix: 14 scenarios x 5 fault profiles x 2 modes x repeats.

Every cell gets a fresh WAL directory and a fresh set of fake adapters, so no
run can inherit state from another. Every cell records its seed; the seed plus
the scenario id and profile is enough to reproduce any single run exactly, which
is what makes a failure in a 700-run matrix actionable rather than folklore.
"""

from __future__ import annotations

import tempfile
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ..adapters.fake import FakeAdapter
from ..core.receipt import (
    OUTCOME_FAILURE,
    OUTCOME_HELD,
    OUTCOME_PARTIAL,
    OUTCOME_REFUSED,
    OUTCOME_SUCCESS,
)
from ..core.runner import run as run_request
from ..types import IRREVERSIBLE_ACTIONS
from . import faults as faults_mod
from . import oracle as oracle_mod
from .scenarios import SCENARIOS, Scenario

MODE_ON = "readback_on"
MODE_OFF = "readback_off"
MODES = (MODE_ON, MODE_OFF)

#: Reported outcomes that mean "the agent said the task is done".
REPORTED_SUCCESS = {OUTCOME_SUCCESS}
#: Reported outcomes that mean "the agent declined before writing anything".
REPORTED_REFUSE = {OUTCOME_HELD, OUTCOME_REFUSED}


@dataclass
class RunRecord:
    """One cell of the matrix."""

    scenario_id: int
    scenario_name: str
    expected_outcome: str
    mode: str
    profile: str
    target_app: str | None
    seed: int
    repeat: int
    run_id: str

    reported_outcome: str = ""
    reported_reason: str = ""
    oracle_correct: bool = False
    oracle_detail: str = ""
    oracle_residual: dict = field(default_factory=dict)

    run_latency_ms: float = 0.0
    recovery_time_ms: float | None = None

    forbidden: list[str] = field(default_factory=list)
    applied_effects: int = 0
    double_writes: dict[str, int] = field(default_factory=dict)
    error: str | None = None

    @property
    def reported_success(self) -> bool:
        return self.reported_outcome in REPORTED_SUCCESS

    @property
    def silent_failure(self) -> bool:
        """Reported success while the world is wrong. The headline metric."""
        return self.reported_success and not self.oracle_correct

    @property
    def false_alarm(self) -> bool:
        """Reported failure while the world was actually correct.

        Two exclusions, both because "reported failure" is the RIGHT answer
        there and calling it an alarm would be scoring correct behaviour as a
        defect:

        * a refusal is a decision made before any work, not a mistaken verdict
          about work already done;
        * a scenario whose expected outcome IS compensate ends in a correct
          state precisely BECAUSE it rolled back. Counting that as a false
          alarm would mean the better the rollback, the worse the score.
        """
        if self.reported_success:
            return False
        if self.reported_outcome in REPORTED_REFUSE:
            return False
        if self.expected_outcome == "compensate":
            return False
        return self.oracle_correct

    @property
    def task_success(self) -> bool:
        return self.reported_success and self.oracle_correct

    @property
    def partial_state(self) -> bool:
        """Ended badly AND left writes behind un-reversed."""
        ended_badly = self.reported_outcome in (OUTCOME_FAILURE, OUTCOME_PARTIAL)
        return ended_badly and bool(
            any(keys for keys in (self.oracle_residual or {}).values())
        )

    def repro(self) -> str:
        return (
            f"python -m readback.evals.run --scenario {self.scenario_id} "
            f"--profile {self.profile} --mode {self.mode} --seed {self.seed}"
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "scenario_id": self.scenario_id,
            "scenario_name": self.scenario_name,
            "expected_outcome": self.expected_outcome,
            "mode": self.mode,
            "profile": self.profile,
            "target_app": self.target_app,
            "seed": self.seed,
            "repeat": self.repeat,
            "run_id": self.run_id,
            "reported_outcome": self.reported_outcome,
            "reported_reason": self.reported_reason,
            "oracle_correct": self.oracle_correct,
            "oracle_detail": self.oracle_detail,
            "oracle_residual": self.oracle_residual,
            "run_latency_ms": round(self.run_latency_ms, 3),
            "recovery_time_ms": (
                None if self.recovery_time_ms is None else round(self.recovery_time_ms, 3)
            ),
            "forbidden": self.forbidden,
            "applied_effects": self.applied_effects,
            "double_writes": self.double_writes,
            "silent_failure": self.silent_failure,
            "false_alarm": self.false_alarm,
            "task_success": self.task_success,
            "partial_state": self.partial_state,
            "error": self.error,
            "repro": self.repro(),
        }


class _Crash(RuntimeError):
    """Raised inside an adapter to simulate the process dying mid-run."""


def build_adapters(plan: faults_mod.FaultPlan) -> dict[str, FakeAdapter]:
    configs = faults_mod.configs_for(plan)
    return {app: FakeAdapter(name=app, faults=configs[app]) for app in faults_mod.APPS}


def _detect_forbidden(receipt, adapters, scenario: Scenario) -> tuple[list[str], dict[str, int]]:
    """Effects that must never happen, regardless of outcome.

    Four kinds, per the spec:
      * a held request executed anyway
      * a double write for one idempotency key
      * success reported alongside a failed cross-check
      * compensate attempted on an effect marked irreversible
    """
    violations: list[str] = []

    applied = [c for c in receipt.calls if c.phase == "apply" and c.status != "skipped"]
    if receipt.outcome in REPORTED_REFUSE and applied:
        violations.append(
            f"held/refused request applied {len(applied)} effect(s): "
            + ", ".join(f"{c.app}.{c.action}" for c in applied)
        )

    doubles: dict[str, int] = {}
    for adapter in adapters.values():
        for key, count in adapter.write_count.items():
            if count > 1:
                doubles[key] = count
                violations.append(f"double write: {key} written {count} times")

    if receipt.outcome == OUTCOME_SUCCESS:
        failed_cross = [c for c in receipt.crosschecks if not c.passed]
        if failed_cross:
            violations.append(
                f"success reported with {len(failed_cross)} failed cross-check(s): "
                + ", ".join(c.name for c in failed_cross)
            )

    for call in receipt.calls:
        if call.phase != "compensate":
            continue
        if call.action in IRREVERSIBLE_ACTIONS and call.status not in ("irreversible", "skipped"):
            violations.append(
                f"compensate attempted on irreversible effect {call.app}.{call.action} "
                f"(status={call.status})"
            )

    return violations, doubles


def _recovery_time_ms(receipt) -> float | None:
    """From the first failed assertion to the last compensation completing.

    Approximated from the recorded call latencies: the compensation phase's
    total wall time plus the verify work that preceded it is not separately
    timestamped, so this measures the compensation span itself, which is the
    part a human waits on.
    """
    comps = [c for c in receipt.calls if c.phase == "compensate"]
    if not comps:
        return None
    return sum(c.latency_ms for c in comps)


def execute_cell(
    scenario: Scenario,
    mode: str,
    plan: faults_mod.FaultPlan,
    repeat: int,
    root: str,
) -> RunRecord:
    """Run one scenario once, under one fault plan, in one mode."""
    adapters = build_adapters(plan)
    run_id = f"eval_{scenario.id:02d}_{plan.profile}_{mode}_{repeat}_{uuid.uuid4().hex[:6]}"
    record = RunRecord(
        scenario_id=scenario.id,
        scenario_name=scenario.name,
        expected_outcome=scenario.expected_outcome,
        mode=mode,
        profile=plan.profile,
        target_app=plan.target_app,
        seed=plan.seed,
        repeat=repeat,
        run_id=run_id,
    )

    readback = mode == MODE_ON
    injection = scenario.injection

    # Structural injection: drift live state right after the write lands.
    if injection.drift_app:
        target = adapters[injection.drift_app]
        original_apply = target.apply

        def apply_then_drift(effect, _target=target, _orig=original_apply):
            result = _orig(effect)
            if effect.idempotency_key == injection.drift_key:
                _target.drift(injection.drift_key, **injection.drift_changes)
            return result

        target.apply = apply_then_drift

    started = time.perf_counter()
    try:
        if injection.crash_on_app:
            # First attempt dies inside the named app. Then the SAME run_id is
            # replayed, which is what exercises WAL recovery.
            crashing = adapters[injection.crash_on_app]
            crashing.apply = lambda effect: (_ for _ in ()).throw(_Crash("process died mid-run"))
            try:
                run_request(
                    scenario.request, adapters=adapters, run_id=run_id,
                    root=root, write_receipt=False, readback=readback,
                )
            except _Crash:
                pass
            del crashing.apply  # restore the real method for the retry

        receipt = run_request(
            scenario.request, adapters=adapters, run_id=run_id,
            root=root, write_receipt=False, readback=readback,
        )
    except BaseException as exc:  # noqa: BLE001 - recorded, never fatal to the matrix
        record.error = f"{type(exc).__name__}: {exc}"
        record.run_latency_ms = (time.perf_counter() - started) * 1000.0
        final_state = oracle_mod.read_final_state(adapters)
        verdict = oracle_mod.judge(scenario, final_state)
        record.oracle_correct = verdict.state_correct
        record.oracle_detail = verdict.detail
        record.oracle_residual = verdict.residual
        record.reported_outcome = "crashed"
        return record

    record.run_latency_ms = (time.perf_counter() - started) * 1000.0
    record.reported_outcome = receipt.outcome
    record.reported_reason = receipt.reason
    record.applied_effects = len(
        [c for c in receipt.calls if c.phase == "apply" and c.status != "skipped"]
    )
    record.recovery_time_ms = _recovery_time_ms(receipt)

    # The oracle reads the fakes directly. It never sees `receipt`.
    final_state = oracle_mod.read_final_state(adapters)
    verdict = oracle_mod.judge(scenario, final_state)
    record.oracle_correct = verdict.state_correct
    record.oracle_detail = verdict.detail
    record.oracle_residual = verdict.residual

    record.forbidden, record.double_writes = _detect_forbidden(receipt, adapters, scenario)
    return record


def run_matrix(
    repeats: int = 5,
    scenarios: list[Scenario] | None = None,
    profiles: tuple[str, ...] = faults_mod.PROFILES,
    modes: tuple[str, ...] = MODES,
    base_seed: int = 1000,
    progress: bool = True,
) -> list[RunRecord]:
    """Execute the full matrix and return one record per cell."""
    scenarios = scenarios or SCENARIOS
    records: list[RunRecord] = []
    total = len(scenarios) * len(profiles) * len(modes) * repeats
    done = 0

    with tempfile.TemporaryDirectory(prefix="readback_evals_") as tmp:
        for scenario in scenarios:
            for profile in profiles:
                for repeat in range(repeats):
                    # Seed depends on scenario/profile/repeat but NOT on mode,
                    # so both modes face the identical fault assignment and the
                    # comparison between them is like-for-like.
                    seed = base_seed + scenario.id * 1000 + profiles.index(profile) * 100 + repeat
                    plan = faults_mod.plan_faults(profile, seed=seed)
                    for mode in modes:
                        root = str(Path(tmp) / f"{scenario.id}_{profile}_{mode}_{repeat}")
                        records.append(execute_cell(scenario, mode, plan, repeat, root))
                        done += 1
                        if progress and done % 50 == 0:
                            print(f"  ... {done}/{total} runs", flush=True)

    return records
