"""Aggregate RunRecords into the reported metrics.

Definitions, stated precisely because the headline number depends on them:

  task_success_rate     reported success AND the oracle says the world is right
  silent_failure_rate   reported success BUT the oracle says the world is wrong.
                        The headline. For readback_on it must be 0: claiming a
                        job is done when it is not is the failure mode this
                        whole system exists to eliminate, and it is strictly
                        worse than failing loudly.
  false_alarm_rate      reported failure BUT the world was actually correct --
                        the cost of paranoia. A refusal is NOT a false alarm:
                        declining to act is a decision, not a mistaken verdict
                        about work already done.
  forbidden_effect_rate any run with >=1 violation of an invariant that no
                        outcome justifies (held-but-executed, double write,
                        success alongside a failed cross-check, compensation
                        attempted on an irreversible effect)
  partial_state_rate    ended in failure/partial AND left writes un-reversed
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Iterable, Sequence

from .runner import RunRecord


def percentile(values: Sequence[float], pct: float) -> float:
    """Linear-interpolated percentile. 0.0 for an empty sample."""
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return float(ordered[0])
    rank = (len(ordered) - 1) * pct
    low = math.floor(rank)
    high = math.ceil(rank)
    if low == high:
        return float(ordered[int(rank)])
    return float(ordered[low] + (ordered[high] - ordered[low]) * (rank - low))


@dataclass
class Metrics:
    """One aggregation bucket: a mode, a profile, or everything."""

    label: str
    total: int = 0
    task_success: int = 0
    success_n: int = 0
    success_ok: int = 0
    refusal_n: int = 0
    refusal_ok: int = 0
    compensation_n: int = 0
    compensation_ok: int = 0
    silent_failures: int = 0
    false_alarms: int = 0
    forbidden: int = 0
    partial_state: int = 0
    crashed: int = 0
    run_latency_p50: float = 0.0
    run_latency_p95: float = 0.0
    recovery_p50: float = 0.0
    recovery_p95: float = 0.0
    recovery_samples: int = 0
    forbidden_examples: list[str] = field(default_factory=list)

    def _rate(self, count: int) -> float:
        return 0.0 if not self.total else count / self.total

    @property
    def task_success_rate(self) -> float:
        return self._rate(self.task_success)

    @property
    def silent_failure_rate(self) -> float:
        return self._rate(self.silent_failures)

    @property
    def false_alarm_rate(self) -> float:
        return self._rate(self.false_alarms)

    @property
    def forbidden_effect_rate(self) -> float:
        return self._rate(self.forbidden)

    @property
    def partial_state_rate(self) -> float:
        return self._rate(self.partial_state)

    # -- the three honest correctness rates, each over its own denominator --

    @property
    def success_correctness(self) -> float | None:
        return None if not self.success_n else self.success_ok / self.success_n

    @property
    def refusal_correctness(self) -> float | None:
        return None if not self.refusal_n else self.refusal_ok / self.refusal_n

    @property
    def compensation_correctness(self) -> float | None:
        return None if not self.compensation_n else self.compensation_ok / self.compensation_n

    def to_dict(self) -> dict[str, Any]:
        return {
            "label": self.label,
            "total": self.total,
            "task_success_rate": round(self.task_success_rate, 4),
            "success_correctness": (
                None if self.success_correctness is None else round(self.success_correctness, 4)
            ),
            "success_denominator": self.success_n,
            "refusal_correctness": (
                None if self.refusal_correctness is None else round(self.refusal_correctness, 4)
            ),
            "refusal_denominator": self.refusal_n,
            "compensation_correctness": (
                None if self.compensation_correctness is None
                else round(self.compensation_correctness, 4)
            ),
            "compensation_denominator": self.compensation_n,
            "silent_failure_rate": round(self.silent_failure_rate, 4),
            "false_alarm_rate": round(self.false_alarm_rate, 4),
            "forbidden_effect_rate": round(self.forbidden_effect_rate, 4),
            "partial_state_rate": round(self.partial_state_rate, 4),
            "silent_failures": self.silent_failures,
            "false_alarms": self.false_alarms,
            "forbidden": self.forbidden,
            "partial_state": self.partial_state,
            "crashed": self.crashed,
            "run_latency_ms_p50": round(self.run_latency_p50, 3),
            "run_latency_ms_p95": round(self.run_latency_p95, 3),
            "recovery_time_ms_p50": round(self.recovery_p50, 3),
            "recovery_time_ms_p95": round(self.recovery_p95, 3),
            "recovery_samples": self.recovery_samples,
            "forbidden_examples": self.forbidden_examples[:5],
        }


def aggregate(label: str, records: Iterable[RunRecord]) -> Metrics:
    records = list(records)
    metrics = Metrics(label=label, total=len(records))

    latencies: list[float] = []
    recoveries: list[float] = []
    for record in records:
        if record.task_success:
            metrics.task_success += 1

        if record.success_correct is not None:
            metrics.success_n += 1
            metrics.success_ok += int(record.success_correct)
        if record.refusal_correct is not None:
            metrics.refusal_n += 1
            metrics.refusal_ok += int(record.refusal_correct)
        if record.compensation_correct is not None:
            metrics.compensation_n += 1
            metrics.compensation_ok += int(record.compensation_correct)
        if record.silent_failure:
            metrics.silent_failures += 1
        if record.false_alarm:
            metrics.false_alarms += 1
        if record.forbidden:
            metrics.forbidden += 1
            for violation in record.forbidden:
                entry = f"S{record.scenario_id:02d}/{record.mode}/{record.profile}: {violation}"
                if entry not in metrics.forbidden_examples:
                    metrics.forbidden_examples.append(entry)
        if record.partial_state:
            metrics.partial_state += 1
        if record.error:
            metrics.crashed += 1
        latencies.append(record.run_latency_ms)
        if record.recovery_time_ms is not None:
            recoveries.append(record.recovery_time_ms)

    metrics.run_latency_p50 = percentile(latencies, 0.50)
    metrics.run_latency_p95 = percentile(latencies, 0.95)
    metrics.recovery_p50 = percentile(recoveries, 0.50)
    metrics.recovery_p95 = percentile(recoveries, 0.95)
    metrics.recovery_samples = len(recoveries)
    return metrics


def by_mode_and_profile(
    records: Sequence[RunRecord], modes: Sequence[str], profiles: Sequence[str]
) -> dict[str, dict[str, Metrics]]:
    """metrics[mode][profile], plus metrics[mode]["ALL"]."""
    out: dict[str, dict[str, Metrics]] = {}
    for mode in modes:
        mode_records = [r for r in records if r.mode == mode]
        out[mode] = {
            profile: aggregate(
                f"{mode}/{profile}", [r for r in mode_records if r.profile == profile]
            )
            for profile in profiles
        }
        out[mode]["ALL"] = aggregate(f"{mode}/ALL", mode_records)
    return out
