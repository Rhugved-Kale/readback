"""Restore demo starting state so a demo take can be repeated.

    python -m readback.reset

WHY THIS EXISTS
===============
The demo needs three identical takes, and a refund is irreversible. Once take 1
refunds order 4417, that PaymentIntent is spent: Stripe offers no un-refund, so
take 2 cannot use it. Every other demo effect is reversible in place (a price
goes back, a Notion cell goes back, a Slack message deletes), but the refund has
to be REPLACED -- a fresh PaymentIntent carrying the same order_id metadata, so
the request text in the script still reads "refund order 4417".

That asymmetry is the whole reason this file is separate from seed.py. Seeding
builds a world; resetting rewinds one that has already been used.

Safe to run repeatedly. Every step is a converge-to-target operation, not a
delta: it reads current state, compares it to the intended starting state, and
only writes where they differ. Running it twice in a row makes no second change.

Touches ONLY demo state. The 9001-9020 test range is left alone -- those are
meant to be burned, and replenishing them is `seed.py --orders 9001-9020`.
"""

from __future__ import annotations

import argparse
import os
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv

from .adapters.stripe_adapter import find_payment_intents_by_order, find_product_by_key, _meta
from .seed import DEMO_ORDERS, ORDER_AMOUNTS, data_source_id

#: The state every take must start from: product_key -> (display, cents).
#: Team is here because the live suite reprices it and the notion_drift
#: injection demo leaves it at the wrong number in BOTH Stripe and Notion.
RESET_PRODUCTS: list[tuple[str, str, int]] = [
    ("pro", "Pro", 9900),
    ("team", "Team", 24900),
]

PRO_KEY = "pro"
PRO_DISPLAY = "Pro"
PRO_AMOUNT_CENTS = 9900

#: How far back to sweep the bot's own Slack messages.
SLACK_LOOKBACK = timedelta(hours=2)

CATALOG_NAME = "Name"
CATALOG_PRICE = "Price"
CATALOG_PRICE_ID = "Stripe Price ID"
AUDIT_RUN_ID = "Run ID"


@dataclass
class ResetReport:
    """Before/after for every surface this touches."""

    stripe_prices: list[dict] = field(default_factory=list)
    stray_prices: list[dict] = field(default_factory=list)
    catalog: list[dict] = field(default_factory=list)
    audit_rows: list[dict] = field(default_factory=list)
    slack: list[dict] = field(default_factory=list)
    orders: list[dict] = field(default_factory=list)


# ---------------------------------------------------------------------------
# 1. Stripe: Pro back to $99/month
# ---------------------------------------------------------------------------


def reset_product_price(
    stripe, product_key: str, amount_cents: int, report: ResetReport
) -> str:
    """Point a product at its baseline monthly USD price and archive the strays.

    Order matters: the target price must be active and promoted to default
    BEFORE any stray is archived, because Stripe refuses to archive a price
    that is still a product default.
    """
    product = find_product_by_key(stripe, product_key, expand=["default_price"])
    if product is None:
        raise SystemExit(
            f"No Stripe product with metadata product_key={product_key!r}. "
            f"Run `python -m readback.seed` first."
        )

    current = getattr(product, "default_price", None)
    before_id = current if isinstance(current, str) else (current.id if current else None)
    before_amount = None if isinstance(current, (str, type(None))) else current.unit_amount

    # Every price on the product, archived ones included -- the $99 price we
    # want back may well be one a previous take archived.
    all_prices = list(stripe.Price.list(product=product.id, limit=100).auto_paging_iter())

    target = next(
        (
            p for p in all_prices
            if p.unit_amount == amount_cents
            and p.currency == "usd"
            and p.recurring
            and p.recurring.interval == "month"
        ),
        None,
    )

    if target is None:
        target = stripe.Price.create(
            product=product.id,
            currency="usd",
            unit_amount=amount_cents,
            recurring={"interval": "month"},
            metadata={"product_key": product_key},
        )
        action = "created"
    elif not target.active:
        stripe.Price.modify(target.id, active=True)
        action = "unarchived"
    else:
        action = "reused"

    # Metadata can drift if a run created the price without it.
    if _meta(target).get("product_key") != product_key:
        stripe.Price.modify(target.id, metadata={"product_key": product_key})

    if before_id != target.id:
        stripe.Product.modify(product.id, default_price=target.id)
        promoted = "promoted to default"
    else:
        promoted = "already default"

    # Now safe to archive strays: anything on this product that is not the
    # baseline price.
    for price in all_prices:
        if price.id == target.id or not price.active:
            continue
        stripe.Price.modify(price.id, active=False)
        report.stray_prices.append(
            {"product": product_key, "price_id": price.id,
             "amount": f"${price.unit_amount / 100:,.2f}", "status": "archived"}
        )

    report.stripe_prices.append({
        "product": product_key,
        "product_id": product.id,
        "before_price_id": before_id or "-",
        "before_amount": f"${before_amount / 100:,.2f}" if before_amount else "-",
        "after_price_id": target.id,
        "after_amount": f"${amount_cents / 100:,.2f}",
        "status": f"{action}, {promoted}",
    })
    return target.id


# ---------------------------------------------------------------------------
# 2. Notion catalog: Pro row back to 99 + the live price id
# ---------------------------------------------------------------------------


def reset_catalog(
    notion, catalog_db: str, display: str, amount_cents: int, price_id: str,
    report: ResetReport,
) -> None:
    source = data_source_id(notion, catalog_db)
    rows = notion.data_sources.query(
        data_source_id=source,
        filter={"property": CATALOG_NAME, "title": {"equals": display}},
    ).get("results", [])

    if not rows:
        report.catalog.append({"name": display, "status": "SKIPPED: no such row"})
        return

    row = rows[0]
    before_price = _number(row, CATALOG_PRICE)
    before_id = _text(row, CATALOG_PRICE_ID)

    if before_price == amount_cents / 100 and before_id == price_id:
        status = "already correct"
    else:
        notion.pages.update(
            page_id=row["id"],
            properties={
                CATALOG_PRICE: {"number": amount_cents / 100},
                CATALOG_PRICE_ID: {"rich_text": [{"text": {"content": price_id}}]},
            },
        )
        status = "restored"

    report.catalog.append({
        "name": display,
        "before_price": before_price,
        "before_price_id": before_id or "(empty)",
        "after_price": amount_cents / 100,
        "after_price_id": price_id,
        "status": status,
    })


# ---------------------------------------------------------------------------
# 3. Notion audit log: archive everything a run wrote
# ---------------------------------------------------------------------------


def reset_audit(notion, audit_db: str, report: ResetReport) -> None:
    """Archive every audit row carrying a Run ID.

    A non-empty Run ID means a Readback run wrote it. Rows without one were put
    there by a human and are left alone.
    """
    source = data_source_id(notion, audit_db)
    rows = notion.data_sources.query(
        data_source_id=source,
        filter={"property": AUDIT_RUN_ID, "rich_text": {"is_not_empty": True}},
    ).get("results", [])

    for row in rows:
        if row.get("archived") or row.get("in_trash"):
            continue
        notion.pages.update(page_id=row["id"], archived=True)
        report.audit_rows.append(
            {"page_id": row["id"], "run_id": _text(row, AUDIT_RUN_ID), "status": "archived"}
        )


# ---------------------------------------------------------------------------
# 4. Slack: remove this bot's recent messages
# ---------------------------------------------------------------------------


def reset_slack(slack, channel_id: str, report: ResetReport) -> None:
    """Delete messages this bot posted in the last 2 hours.

    Scoped to THIS bot's own user id: a reset must never delete a human's
    message, and the channel is shared.
    """
    me = slack.auth_test()
    bot_user_id = me.get("user_id")
    cutoff = (datetime.now(timezone.utc) - SLACK_LOOKBACK).timestamp()

    history = slack.conversations_history(channel=channel_id, limit=200).get("messages", [])
    for message in history:
        ts = message.get("ts", "0")
        if float(ts) < cutoff:
            continue
        # Exactly one rule: the message's author must be THIS bot's user id.
        # Not "has a bot_id" (that matches every other integration in the
        # channel) and not "looks like ours" -- deleting someone else's message
        # is unrecoverable and this runs unattended between takes.
        if message.get("user") != bot_user_id:
            continue
        try:
            slack.chat_delete(channel=channel_id, ts=ts)
            status = "deleted"
        except Exception as exc:  # noqa: BLE001 - reported, not fatal
            status = f"FAILED: {exc}"
        report.slack.append({
            "ts": ts,
            "text": (message.get("text") or "").splitlines()[0][:58],
            "status": status,
        })


# ---------------------------------------------------------------------------
# 5. Demo orders: replace any that a take already refunded
# ---------------------------------------------------------------------------


def reset_orders(stripe, report: ResetReport) -> None:
    """Ensure every demo order has a fresh, unrefunded, refundable payment.

    A refunded PaymentIntent cannot be reused, so the replacement carries the
    SAME order_id metadata. The demo script keeps saying "refund order 4417"
    and keeps being right, take after take.
    """
    for order_id in sorted(DEMO_ORDERS):
        amount = ORDER_AMOUNTS.get(order_id, PRO_AMOUNT_CENTS)
        intents = find_payment_intents_by_order(stripe, order_id)

        refundable = None
        refunded_ids = []
        for intent in intents:
            if intent.status != "succeeded":
                continue
            if _refunded_cents(stripe, intent.id) > 0:
                refunded_ids.append(intent.id)
            else:
                refundable = refundable or intent

        if refundable is not None:
            report.orders.append({
                "order_id": order_id,
                "before": refunded_ids[0] if refunded_ids else refundable.id,
                "after": refundable.id,
                "amount": f"${refundable.amount / 100:,.2f}",
                "status": "usable, left as is",
            })
            continue

        replacement = stripe.PaymentIntent.create(
            amount=amount,
            currency="usd",
            payment_method="pm_card_visa",
            confirm=True,
            automatic_payment_methods={"enabled": True, "allow_redirects": "never"},
            metadata={"order_id": order_id},
        )
        report.orders.append({
            "order_id": order_id,
            "before": refunded_ids[0] if refunded_ids else "(none)",
            "after": replacement.id,
            "amount": f"${amount / 100:,.2f}",
            "status": "REPLACED (previous was refunded)",
        })


def _refunded_cents(stripe, payment_intent_id: str) -> int:
    refunds = stripe.Refund.list(payment_intent=payment_intent_id, limit=100).data
    return sum(int(r.amount) for r in refunds if r.status == "succeeded")


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------


def _text(page: dict, column: str) -> str:
    prop = page.get("properties", {}).get(column)
    if not prop:
        return ""
    kind = prop.get("type")
    return "".join(p.get("plain_text", "") for p in (prop.get(kind) or []))


def _number(page: dict, column: str):
    prop = page.get("properties", {}).get(column)
    if not prop or prop.get("type") != "number":
        return None
    return prop.get("number")


def print_report(report: ResetReport) -> None:
    def table(title: str, columns: list[str], rows: list[dict]) -> None:
        print(f"\n{title}")
        if not rows:
            print("  (nothing to change)")
            return
        widths = {c: max(len(c), *(len(str(r.get(c, ""))) for r in rows)) for c in columns}
        print("  " + "  ".join(c.ljust(widths[c]) for c in columns))
        print("  " + "  ".join("-" * widths[c] for c in columns))
        for row in rows:
            print("  " + "  ".join(str(row.get(c, "")).ljust(widths[c]) for c in columns))

    print("=" * 72)
    print("READBACK RESET   demo starting state")
    print("=" * 72)

    table("STRIPE  default prices",
          ["product", "product_id", "before_price_id", "before_amount",
           "after_price_id", "after_amount", "status"],
          report.stripe_prices)
    table("STRIPE  stray prices archived", ["product", "price_id", "amount", "status"],
          report.stray_prices)
    table("NOTION  catalog rows",
          ["name", "before_price", "before_price_id", "after_price", "after_price_id", "status"],
          report.catalog)
    table("NOTION  audit rows archived", ["page_id", "run_id", "status"], report.audit_rows)
    table("SLACK   messages deleted", ["ts", "text", "status"], report.slack)
    table("STRIPE  demo orders", ["order_id", "before", "after", "amount", "status"],
          report.orders)

    replaced = [o for o in report.orders if o["status"].startswith("REPLACED")]
    print("\n" + "-" * 72)
    if replaced:
        print(f"Replaced {len(replaced)} spent demo order(s): "
              f"{', '.join(o['order_id'] for o in replaced)}")
    else:
        print("No demo orders needed replacing.")
    print("Demo starting state restored.")
    print("=" * 72)


def _require_env(*keys: str) -> dict[str, str]:
    values, missing = {}, []
    for key in keys:
        value = os.environ.get(key, "")
        if not value:
            missing.append(key)
        values[key] = value
    if missing:
        raise SystemExit(f"Missing environment variable(s): {', '.join(missing)}")
    return values


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="readback.reset",
        description="Restore demo starting state. Safe to run repeatedly.",
    )
    parser.add_argument(
        "--skip-slack", action="store_true",
        help="leave Slack messages alone (useful when re-running mid-take)",
    )
    args = parser.parse_args(argv)

    load_dotenv()
    env = _require_env(
        "STRIPE_SECRET_KEY", "NOTION_TOKEN", "NOTION_CATALOG_DB",
        "NOTION_AUDIT_DB", "SLACK_BOT_TOKEN", "SLACK_CHANNEL_ID",
    )

    import stripe as stripe_sdk
    from notion_client import Client as NotionClient
    from slack_sdk import WebClient

    stripe_sdk.api_key = env["STRIPE_SECRET_KEY"]
    notion = NotionClient(auth=env["NOTION_TOKEN"])
    slack = WebClient(token=env["SLACK_BOT_TOKEN"])

    report = ResetReport()
    for product_key, display, amount_cents in RESET_PRODUCTS:
        price_id = reset_product_price(stripe_sdk, product_key, amount_cents, report)
        reset_catalog(
            notion, env["NOTION_CATALOG_DB"], display, amount_cents, price_id, report
        )
    reset_audit(notion, env["NOTION_AUDIT_DB"], report)
    if not args.skip_slack:
        reset_slack(slack, env["SLACK_CHANNEL_ID"], report)
    reset_orders(stripe_sdk, report)
    print_report(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
