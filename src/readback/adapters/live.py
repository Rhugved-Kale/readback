"""Factory that wires the three live adapters together for one run.

Exists mainly for one dependency that is not obvious: the Notion catalog row
has to record the Stripe price id, but a Notion adapter that imported Stripe
directly would make the cross-check circular -- Notion would be copying the
same value the cross-check later "independently" compares it to. So the Stripe
lookup is injected as a callable, and the cross-check reads Stripe again itself.
"""

from __future__ import annotations

import os

from .notion_adapter import NotionAdapter
from .slack_adapter import SlackAdapter
from .stripe_adapter import StripeAdapter

REQUIRED_ENV = (
    "STRIPE_SECRET_KEY",
    "NOTION_TOKEN",
    "NOTION_CATALOG_DB",
    "NOTION_AUDIT_DB",
    "SLACK_BOT_TOKEN",
    "SLACK_CHANNEL_ID",
)


def missing_env() -> list[str]:
    return [key for key in REQUIRED_ENV if not os.environ.get(key)]


def build_live_adapters(run_id: str, injection: str | None = None) -> dict[str, object]:
    """One live adapter per provider, all sharing this run's id.

    `run_id` is threaded in at construction rather than read from the runner,
    because Notion stamps it into the audit row's Run ID column and Slack into
    its message marker -- and both of those are what verify() and the dedupe
    checks key on.
    """
    gaps = missing_env()
    if gaps:
        raise RuntimeError(
            f"Missing required environment variable(s): {', '.join(gaps)}. "
            f"Copy .env.example to .env and fill it in."
        )

    stripe = StripeAdapter(run_id=run_id)
    notion = NotionAdapter(
        run_id=run_id,
        stripe_price_lookup=stripe.live_default_price,
        injection=injection,
    )
    slack = SlackAdapter(run_id=run_id)
    return {"stripe": stripe, "notion": notion, "slack": slack}
