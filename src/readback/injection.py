"""Deliberate fault injection, for demonstrating cross-app detection live.

This exists so a real cross-app mismatch can be shown end to end against real
providers, rather than asserted from a slide. It is dangerous in the obvious
way -- it makes the system write something wrong on purpose -- so every guard
here is a refusal, not a warning:

  * off unless READBACK_ALLOW_INJECTION=1 is set in the environment;
  * refused outright when the adapters are fakes, which is what keeps it out of
    the eval harness permanently;
  * labelled in every surface a human or a machine could read the result from
    (the Slack post, receipt.json, receipt.txt), so an injected run can never
    be mistaken for a genuine provider failure.

The last point is the one that matters. A demo that fakes a failure without
saying so is a lie; a demo that fakes a failure and says so in three places is
a test.
"""

from __future__ import annotations

import os
import re
from typing import Any, Mapping

#: The only supported injection today.
NOTION_DRIFT = "notion_drift"
KNOWN: frozenset[str] = frozenset({NOTION_DRIFT})

#: How far the injected Notion price diverges from the Stripe price, in dollars.
#: Fixed rather than random so the demo is reproducible and the receipt's two
#: numbers are predictable.
DRIFT_DOLLARS = 10

ENV_FLAG = "READBACK_ALLOW_INJECTION"

_SUFFIX_RE = re.compile(r"\s*--inject[ =]+(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*$")


class InjectionRefused(Exception):
    """Raised when an injection is requested but must not run."""


def parse(text: str) -> tuple[str, str | None]:
    """Split a trailing `--inject <name>` off a request.

    Returns (clean_request, injection_name). The clean request is what gets
    planned, so the parsed plan is byte-identical to the same request without
    the suffix -- the injection changes how a provider behaves, never what the
    operator asked for.
    """
    raw = (text or "").strip()
    match = _SUFFIX_RE.search(raw)
    if not match:
        return raw, None
    return raw[: match.start()].strip(), match.group("name").lower()


def enabled() -> bool:
    return os.environ.get(ENV_FLAG, "") == "1"


def refusal_reason(name: str) -> str | None:
    """Why this injection may not run, or None if it may."""
    if name not in KNOWN:
        return (
            f"Unknown injection {name!r}. Known: {', '.join(sorted(KNOWN))}."
        )
    if not enabled():
        return (
            f"Fault injection is disabled. Set {ENV_FLAG}=1 in the environment "
            f"to allow it. It is off by default so a deliberate fault can never "
            f"be triggered by accident."
        )
    return None


def adapters_are_live(adapters: Mapping[str, Any]) -> bool:
    """True only when every adapter talks to a real provider.

    Detected by capability rather than class name: the live adapters expose the
    `live_*` cross-read helpers, the fakes deliberately do not.
    """
    stripe = adapters.get("stripe")
    notion = adapters.get("notion")
    return bool(
        stripe is not None
        and notion is not None
        and hasattr(stripe, "live_default_price")
        and hasattr(notion, "live_catalog_row")
    )


def check(name: str, adapters: Mapping[str, Any]) -> None:
    """Raise InjectionRefused unless this injection is permitted right now."""
    reason = refusal_reason(name)
    if reason:
        raise InjectionRefused(reason)
    if not adapters_are_live(adapters):
        raise InjectionRefused(
            "Fault injection is refused against fake adapters. The eval harness "
            "runs on fakes, and an injected fault there would corrupt a measured "
            "number while looking exactly like a real finding. Injection is for "
            "live demonstration only."
        )


def banner(name: str) -> str:
    """The label that must appear on every surface reporting an injected run."""
    return (
        f"FAULT INJECTED: {name}. Deliberate. Not a real provider failure."
    )


def describe(name: str) -> str:
    if name == NOTION_DRIFT:
        return (
            f"The Notion catalog write commits a price ${DRIFT_DOLLARS} higher than "
            f"the Stripe price. Both providers return success and each is "
            f"internally consistent; only the cross-app check sees the disagreement."
        )
    return "Unknown injection."
