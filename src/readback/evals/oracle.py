"""An INDEPENDENT judge of final world state.

THIS EXISTS SO A BUG IN verify() CANNOT ALSO MARK ITS OWN RUN AS PASSING.

If the harness asked the runner whether the run went well, a verify() that
returns True unconditionally would score 100%: the thing under test would be
grading its own exam. So this module imports none of it. It does not import the
runner, any adapter's verify(), crosscheck, or the receipt. It never sees the
reported outcome.

It reads the fake providers' final in-memory state directly and compares it to
the scenario's declared `expected_final_state`. That is the only input. A run
"succeeded" here if and only if the world ended up the way the scenario says a
correct run leaves it.

The comparison is exhaustive per app: exactly the declared keys, no more and no
fewer. Missing keys mean a dropped write; extra keys mean a double write, an
un-reversed effect, or a held request that executed anyway.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from .scenarios import Scenario


@dataclass
class Verdict:
    """The oracle's judgement. `state_correct` is the only headline field."""

    state_correct: bool
    detail: str
    #: Records present that the scenario says should not be there. Used for
    #: partial_state_rate: writes a failed run left behind un-reversed.
    residual: dict[str, list[str]] = field(default_factory=dict)
    #: Records the scenario requires that are absent.
    missing: dict[str, list[str]] = field(default_factory=dict)
    #: Records present with the wrong field values.
    mismatched: dict[str, list[str]] = field(default_factory=dict)

    @property
    def has_residue(self) -> bool:
        return any(keys for keys in self.residual.values())

    def to_dict(self) -> dict[str, Any]:
        return {
            "state_correct": self.state_correct,
            "detail": self.detail,
            "residual": self.residual,
            "missing": self.missing,
            "mismatched": self.mismatched,
        }


def read_final_state(adapters: Mapping[str, Any]) -> dict[str, dict[str, dict]]:
    """Read live state straight out of the fake providers.

    Uses `.store` directly rather than any adapter method, so no code path under
    test participates in producing the evidence.
    """
    return {
        name: {key: dict(record) for key, record in adapter.store.items()}
        for name, adapter in adapters.items()
    }


def judge(scenario: Scenario, final_state: Mapping[str, Mapping[str, Mapping]]) -> Verdict:
    """Decide whether the world ended up the way the scenario says it must."""
    expected = scenario.expected_final_state
    residual: dict[str, list[str]] = {}
    missing: dict[str, list[str]] = {}
    mismatched: dict[str, list[str]] = {}

    apps = set(expected) | set(final_state)
    for app in sorted(apps):
        want = dict(expected.get(app, {}))
        have = dict(final_state.get(app, {}))

        extra_keys = [k for k in have if k not in want]
        if extra_keys:
            residual[app] = sorted(extra_keys)

        absent_keys = [k for k in want if k not in have]
        if absent_keys:
            missing[app] = sorted(absent_keys)

        for key, want_fields in want.items():
            if key not in have:
                continue
            record = have[key]
            bad = [
                f"{field}: expected {value!r}, found {record.get(field)!r}"
                for field, value in want_fields.items()
                if record.get(field) != value
            ]
            if bad:
                mismatched.setdefault(app, []).append(f"{key}: " + "; ".join(bad))

    state_correct = not (residual or missing or mismatched)

    if state_correct:
        declared = sum(len(v) for v in expected.values())
        detail = (
            f"state matches the scenario's declared truth exactly "
            f"({declared} record(s) across {len(expected)} app(s))"
            if declared
            else "state is empty, as a refused/fully-compensated run requires"
        )
    else:
        parts = []
        if missing:
            parts.append(
                "MISSING " + "; ".join(f"{a}: {', '.join(k)}" for a, k in sorted(missing.items()))
            )
        if residual:
            parts.append(
                "UNEXPECTED " + "; ".join(f"{a}: {', '.join(k)}" for a, k in sorted(residual.items()))
            )
        if mismatched:
            parts.append(
                "WRONG VALUES " + "; ".join(f"{a}: {' | '.join(k)}" for a, k in sorted(mismatched.items()))
            )
        detail = " || ".join(parts)

    return Verdict(
        state_correct=state_correct,
        detail=detail,
        residual=residual,
        missing=missing,
        mismatched=mismatched,
    )
