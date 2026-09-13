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


@dataclass
class Verification:
    """One read-back assertion."""

    app: str
    action: str
    effect_id: str
    passed: bool
    detail: str


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
