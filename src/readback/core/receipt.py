"""The artifact a human actually reads.

A receipt is written for every run, including held and failed ones. It is
deliberately verbose: the point of Readback is that you can audit the claim
"this worked" without logging into three consoles, so the receipt records every
provider call, every read-back assertion with its detail string, and the state
diff — not just the verdict.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ..types import RunContext

OUTCOME_SUCCESS = "success"
OUTCOME_FAILURE = "failure"
OUTCOME_HELD = "held"
OUTCOME_REFUSED = "refused"

#: Rollback ran but could not be total: at least one committed effect had no
#: provider inverse. Never reported as success, and deliberately distinct from
#: plain failure -- "we undid everything" and "we undid everything except a
#: $99 refund that already left the account" are different facts for the human
#: reading this.
OUTCOME_PARTIAL = "partial_manual_remediation"

DEFAULT_ROOT = Path("runs")

_RULE = "=" * 72
_THIN = "-" * 72


@dataclass
class ProviderCall:
    """One round trip to a provider during apply or compensate."""

    phase: str          # apply | compensate
    app: str
    action: str
    effect_id: str
    idempotency_key: str
    status: str
    latency_ms: float
    error: str | None = None
    #: Per-attempt history from the retry helper. Empty for adapters that do
    #: not retry (the fakes), populated for every live call.
    attempts: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class Verification:
    """One read-back assertion."""

    app: str
    action: str
    effect_id: str
    passed: bool
    detail: str


@dataclass
class CrossCheckResult:
    """One cross-app assertion: a fact read from a different app than wrote it."""

    name: str
    reads_from: str
    written_by: str
    description: str
    passed: bool
    detail: str


@dataclass
class ManualRemediation:
    """One committed effect that could not be reversed.

    Carries the exact provider object id a human needs to finish by hand. This
    is the payload of a PARTIAL_MANUAL_REMEDIATION receipt.
    """

    app: str
    action: str
    effect_id: str
    object_id: str
    what: str


@dataclass
class Receipt:
    run_id: str
    requested: str
    started_at: str
    outcome: str = OUTCOME_SUCCESS
    reason: str = ""
    gate: dict[str, str] = field(default_factory=dict)
    planned: list[dict[str, Any]] = field(default_factory=list)
    calls: list[ProviderCall] = field(default_factory=list)
    verifications: list[Verification] = field(default_factory=list)
    crosschecks: list[CrossCheckResult] = field(default_factory=list)
    manual_remediation: list[ManualRemediation] = field(default_factory=list)
    state_diff: dict[str, Any] = field(default_factory=dict)
    finished_at: str = ""

    @classmethod
    def for_run(cls, ctx: RunContext) -> "Receipt":
        return cls(
            run_id=ctx.run_id,
            requested=ctx.request_text,
            started_at=ctx.started_at.isoformat(),
        )

    # -- serialisation -----------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "requested": self.requested,
            "started_at": self.started_at,
            "finished_at": self.finished_at or datetime.now(timezone.utc).isoformat(),
            "outcome": self.outcome,
            "reason": self.reason,
            "gate": self.gate,
            "planned": self.planned,
            "calls": [asdict(c) for c in self.calls],
            "verifications": [asdict(v) for v in self.verifications],
            "crosschecks": [asdict(c) for c in self.crosschecks],
            "manual_remediation": [asdict(m) for m in self.manual_remediation],
            "state_diff": self.state_diff,
        }

    def write(self, root: Path | str = DEFAULT_ROOT) -> tuple[Path, Path]:
        """Write receipt.json and receipt.txt. Returns both paths."""
        self.finished_at = self.finished_at or datetime.now(timezone.utc).isoformat()
        directory = Path(root) / self.run_id
        directory.mkdir(parents=True, exist_ok=True)

        json_path = directory / "receipt.json"
        json_path.write_text(json.dumps(self.to_dict(), indent=2, default=str), encoding="utf-8")

        text_path = directory / "receipt.txt"
        text_path.write_text(self.to_text(), encoding="utf-8")
        return json_path, text_path

    # -- human-readable ----------------------------------------------------

    def to_text(self) -> str:
        lines: list[str] = [
            _RULE,
            f"READBACK RECEIPT   run {self.run_id}",
            _RULE,
            "",
            "REQUESTED",
            f"  {self.requested}",
            "",
            "RISK GATE",
            f"  {self.gate.get('verdict', 'n/a')}: {self.gate.get('reason', '')}",
            "",
            f"PLANNED ({len(self.planned)} effect(s))",
        ]
        if not self.planned:
            lines.append("  (none)")
        for index, effect in enumerate(self.planned, 1):
            lines.append(f"  {index}. {effect['app']}.{effect['action']}  key={effect['idempotency_key']}")
            for key, value in effect.get("params", {}).items():
                lines.append(f"       {key}: {value}")
        lines.append("")

        lines.append(f"PROVIDER CALLS ({len(self.calls)})")
        if not self.calls:
            lines.append("  (none — nothing was applied)")
        for call in self.calls:
            flag = "ok " if call.status == "ok" else ("-- " if call.status == "skipped" else "ERR")
            lines.append(
                f"  [{flag}] {call.phase:<10} {call.app}.{call.action:<20} "
                f"{call.latency_ms:7.2f}ms  {call.status}"
            )
            for attempt in _attempts_of(call):
                lines.append(
                    f"           attempt {attempt.get('attempt')}: "
                    f"{attempt.get('status'):<8} {attempt.get('latency_ms', 0):7.2f}ms"
                    + (f"  http={attempt['http_status']}" if attempt.get("http_status") else "")
                    + (f"  slept {attempt['slept_ms']:.0f}ms" if attempt.get("slept_ms") else "")
                    + (f"  {attempt['error']}" if attempt.get("error") else "")
                )
            if call.error:
                lines.append(f"         error: {call.error}")
        lines.append("")

        lines.append(f"READ-BACK VERIFICATIONS ({len(self.verifications)})")
        if not self.verifications:
            lines.append("  (none — nothing was applied)")
        for check in self.verifications:
            flag = "PASS" if check.passed else "FAIL"
            lines.append(f"  [{flag}] {check.app}.{check.action}")
            lines.append(f"         {check.detail}")
        lines.append("")

        lines.append(f"CROSS-APP CHECKS ({len(self.crosschecks)})")
        if not self.crosschecks:
            lines.append("  (none — cross-checks require live adapters)")
        for cross in self.crosschecks:
            flag = "PASS" if cross.passed else "FAIL"
            lines.append(f"  [{flag}] {cross.name}  (reads {cross.reads_from})")
            lines.append(f"         {cross.description}")
            lines.append(f"         {cross.detail}")
        lines.append("")

        if self.manual_remediation:
            lines.append("!! MANUAL REMEDIATION REQUIRED")
            lines.append("   Rollback could not be completed. These committed effects have")
            lines.append("   no provider inverse and need a human:")
            for item in self.manual_remediation:
                lines.append(f"   - {item.app}.{item.action}  object: {item.object_id}")
                lines.append(f"     {item.what}")
            lines.append("")

        lines.append("STATE DIFF")
        if not self.state_diff:
            lines.append("  (no observable change)")
        for app, diff in sorted(self.state_diff.items()):
            added = diff.get("added", {})
            removed = diff.get("removed", {})
            changed = diff.get("changed", {})
            if not (added or removed or changed):
                lines.append(f"  {app}: no change")
                continue
            lines.append(f"  {app}:")
            for key, value in added.items():
                lines.append(f"    + {key}: {value}")
            for key, value in removed.items():
                lines.append(f"    - {key}: {value}")
            for key, (before, after) in changed.items():
                lines.append(f"    ~ {key}: {before} -> {after}")
        lines.append("")

        lines.append(_THIN)
        lines.append(f"OUTCOME: {self.outcome.upper()}")
        if self.reason:
            lines.append(f"  {self.reason}")
        lines.append(_RULE)
        return "\n".join(lines) + "\n"


def _attempts_of(call: "ProviderCall") -> list[dict[str, Any]]:
    """Per-attempt history a live adapter attached to the call, if any.

    Only rendered when there is more than one attempt: a clean single-try call
    is already fully described by its own line.
    """
    body = getattr(call, "attempts", None) or []
    return body if len(body) > 1 else []


def diff_snapshots(
    before: dict[str, dict[str, Any]], after: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    """Compare two adapter snapshots keyed by idempotency key."""
    added = {k: v for k, v in after.items() if k not in before}
    removed = {k: v for k, v in before.items() if k not in after}
    changed = {
        k: (before[k], after[k])
        for k in before.keys() & after.keys()
        if before[k] != after[k]
    }
    return {"added": added, "removed": removed, "changed": changed}
