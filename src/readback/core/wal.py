"""Append-only write-ahead log at runs/{run_id}/wal.jsonl.

The WAL is the only durable record of what Readback intended and what it
believes it committed. It is written *before* each provider call and updated
*after*, and every append is fsynced, because the failure mode that matters is
the process dying between the write landing and us learning about it.

On retry the WAL is replayed: any effect whose idempotency key is already
COMMITTED is skipped, which is what makes a mid-run crash safe to resume.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ..types import Effect, EffectResult

# WAL record states.
INTENDED = "INTENDED"
COMMITTED = "COMMITTED"
FAILED = "FAILED"
COMPENSATED = "COMPENSATED"

DEFAULT_ROOT = Path("runs")


class WAL:
    """Append-only log for one run."""

    def __init__(self, run_id: str, root: Path | str = DEFAULT_ROOT) -> None:
        self.run_id = run_id
        self.root = Path(root)
        self.dir = self.root / run_id
        self.dir.mkdir(parents=True, exist_ok=True)
        self.path = self.dir / "wal.jsonl"
        # Load anything a previous attempt left behind so replay and
        # already_committed() see the full history, not just this process.
        self.records: list[dict[str, Any]] = self._load()
        self._seq = self.records[-1]["seq"] if self.records else 0

    # -- append API --------------------------------------------------------

    def intend(self, effect: Effect) -> dict[str, Any]:
        """Log the intent to write, before the provider is called."""
        return self._append(effect, INTENDED)

    def commit(self, effect: Effect, result: EffectResult | None = None) -> dict[str, Any]:
        """Log that the write is believed durable.

        Written both after a clean apply() and after read-back proves a write
        landed despite the provider reporting an error.
        """
        return self._append(effect, COMMITTED, result)

    def fail(self, effect: Effect, result: EffectResult | None = None) -> dict[str, Any]:
        """Log that the provider reported an error.

        This does NOT assert the write is absent — only read-back can decide
        that. A FAILED record may later be superseded by a COMMITTED one.
        """
        return self._append(effect, FAILED, result)

    def compensated(self, effect: Effect, result: EffectResult | None = None) -> dict[str, Any]:
        """Log that a previously COMMITTED effect has been reversed."""
        return self._append(effect, COMPENSATED, result)

    # -- queries -----------------------------------------------------------

    def already_committed(self, idempotency_key: str) -> bool:
        """True if this key is COMMITTED and has not since been COMPENSATED.

        The guard that prevents a retry from double-writing.

        Note that INTENDED is ignored here. A retry logs its intent *before*
        consulting this method, so a fresh INTENDED record always sits on top of
        the history; treating it as the current state would mask the earlier
        COMMITTED one and re-apply the write — exactly the bug the WAL exists to
        prevent. Only the terminal states carry the verdict.
        """
        return self._terminal_state(idempotency_key) == COMMITTED

    def committed_effects(self) -> list[dict[str, Any]]:
        """The COMMITTED record for every key whose terminal state is COMMITTED.

        Ordered by commit sequence. Rollback walks this list backwards.
        """
        return [
            record
            for record in self._terminal_records()
            if record["state"] == COMMITTED
        ]

    def _terminal_records(self) -> list[dict[str, Any]]:
        """Latest non-INTENDED record per key, in the order those records were written."""
        latest: dict[str, dict[str, Any]] = {}
        for record in self.records:
            if record["state"] == INTENDED:
                continue
            latest[record["idempotency_key"]] = record
        return [r for r in self.records if latest.get(r["idempotency_key"]) is r]

    def _terminal_state(self, idempotency_key: str) -> str | None:
        state: str | None = None
        for record in self.records:
            if record["idempotency_key"] == idempotency_key and record["state"] != INTENDED:
                state = record["state"]
        return state

    @staticmethod
    def replay(run_id: str, root: Path | str = DEFAULT_ROOT) -> list[dict[str, Any]]:
        """Read a run's WAL off disk without opening it for appending."""
        path = Path(root) / run_id / "wal.jsonl"
        if not path.exists():
            return []
        with path.open("r", encoding="utf-8") as handle:
            return [json.loads(line) for line in handle if line.strip()]

    # -- internals ---------------------------------------------------------

    def _load(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        with self.path.open("r", encoding="utf-8") as handle:
            return [json.loads(line) for line in handle if line.strip()]

    def _append(
        self, effect: Effect, state: str, result: EffectResult | None = None
    ) -> dict[str, Any]:
        self._seq += 1
        record = {
            "seq": self._seq,
            "ts": datetime.now(timezone.utc).isoformat(),
            "run_id": self.run_id,
            "effect_id": effect.id,
            "idempotency_key": effect.idempotency_key,
            "app": effect.app,
            "action": effect.action,
            "params": effect.params,
            "state": state,
        }
        if result is not None:
            record["result"] = result.to_dict()

        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record) + "\n")
            handle.flush()
            os.fsync(handle.fileno())

        self.records.append(record)
        return record
