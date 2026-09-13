"""Seed the real Stripe / Notion / Slack accounts for development.

Run manually, never from a test, never from the runner:

    python -m readback.seed
    python -m readback.seed --orders 4417 4418 4419

This script talks to LIVE APIs. Use Stripe test-mode keys.

It is idempotent by construction: every create is preceded by a search, and an
existing object is reused rather than duplicated. Running it twice is safe and
produces the same table.

What it does:
  1. Stripe   create four products with monthly USD recurring prices
  2. Notion   write each new Stripe price ID into the existing Catalog rows
  3. Stripe   create three refundable test payments, one per order ID
  4. Slack    post a completion message (the Slack smoke test)
  5. print a table of everything touched
"""

from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass, field

from dotenv import load_dotenv

#: product_key -> (display name, unit amount in cents)
PRODUCTS: list[tuple[str, str, int]] = [
    ("starter", "Starter", 2900),
    ("pro", "Pro", 9900),
    ("team", "Team", 24900),
    ("enterprise", "Enterprise", 99900),
]

#: order_id -> amount in cents, for the refundable test payments.
ORDER_AMOUNTS: dict[str, int] = {"4417": 9900, "4418": 2900, "4419": 24900}

DEFAULT_ORDERS: list[str] = ["4417", "4418", "4419"]

#: Notion Catalog column that receives the Stripe price ID.
PRICE_ID_COLUMN = "Stripe Price ID"
NAME_COLUMN = "Name"


@dataclass
class SeedReport:
    """Everything the run touched, for the summary table."""

    products: list[dict] = field(default_factory=list)
    notion_rows: list[dict] = field(default_factory=list)
    orders: list[dict] = field(default_factory=list)
    slack_ts: str | None = None


# ---------------------------------------------------------------------------
# 1. Stripe products + prices
# ---------------------------------------------------------------------------


def seed_products(stripe, report: SeedReport) -> dict[str, dict]:
    """Create the four products and their monthly prices, skipping any that exist.

    Existing products are found by searching `metadata['product_key']`, which is
    what makes a second run a no-op.
    """
    resolved: dict[str, dict] = {}

    for product_key, display, cents in PRODUCTS:
        found = stripe.Product.search(
            query=f"metadata['product_key']:'{product_key}'", limit=1
        )
        if found.data:
            product = found.data[0]
            action = "exists"
        else:
            product = stripe.Product.create(
                name=display,
                metadata={"product_key": product_key},
                idempotency_key=f"seed:product:{product_key}",
            )
            action = "created"

        # Reuse a matching active price if one is already on the product.
        price = None
        for candidate in stripe.Price.list(product=product.id, active=True, limit=100).data:
            if (
                candidate.unit_amount == cents
                and candidate.currency == "usd"
                and candidate.recurring
                and candidate.recurring.interval == "month"
            ):
                price = candidate
                break

        if price is None:
            price = stripe.Price.create(
                product=product.id,
                currency="usd",
                unit_amount=cents,
                recurring={"interval": "month"},
                metadata={"product_key": product_key},
                idempotency_key=f"seed:price:{product_key}:{cents}",
            )
            price_action = "created"
        else:
            price_action = "exists"

        resolved[product_key] = {"product": product, "price": price, "display": display}
        report.products.append(
            {
                "product_key": product_key,
                "name": display,
                "product_id": product.id,
                "price_id": price.id,
                "amount": f"${cents / 100:,.2f}/mo",
                "status": f"product {action}, price {price_action}",
            }
        )

    return resolved


# ---------------------------------------------------------------------------
# 2. Notion catalog rows
# ---------------------------------------------------------------------------


def seed_notion(notion, catalog_db: str, resolved: dict[str, dict], report: SeedReport) -> None:
    """Write each Stripe price ID into the matching existing Catalog row.

    Matches on the Name title. Never creates a row: the four rows (Starter 29,
    Pro 99, Team 249, Enterprise 999) already exist, and creating a fifth would
    be a silent data bug rather than a seed.
    """
    for product_key, info in resolved.items():
        display = info["display"]
        price_id = info["price"].id

        results = notion.databases.query(
            database_id=catalog_db,
            filter={"property": NAME_COLUMN, "title": {"equals": display}},
        ).get("results", [])

        if not results:
            report.notion_rows.append(
                {"name": display, "page_id": "-", "price_id": price_id,
                 "status": "SKIPPED: no row with that Name"}
            )
            continue
        if len(results) > 1:
            report.notion_rows.append(
                {"name": display, "page_id": "-", "price_id": price_id,
                 "status": f"SKIPPED: {len(results)} rows match that Name"}
            )
            continue

        page = results[0]
        current = _plain_text(page["properties"].get(PRICE_ID_COLUMN))
        if current == price_id:
            status = "already set"
        else:
            notion.pages.update(
                page_id=page["id"],
                properties={
                    PRICE_ID_COLUMN: {"rich_text": [{"text": {"content": price_id}}]}
                },
            )
            status = "updated" if current else "set"

        report.notion_rows.append(
            {"name": display, "page_id": page["id"], "price_id": price_id, "status": status}
        )


def _plain_text(prop: dict | None) -> str:
    """Flatten a Notion rich_text property to a plain string."""
    if not prop:
        return ""
    return "".join(part.get("plain_text", "") for part in prop.get("rich_text", []))


# ---------------------------------------------------------------------------
# 3. Stripe refundable test payments
# ---------------------------------------------------------------------------


def seed_payments(stripe, orders: list[str], report: SeedReport) -> None:
    """Create one confirmed, refundable PaymentIntent per order ID.

    Skips an order that already has a PaymentIntent which has not been refunded,
    so a second run does not pile up charges. An order whose payment HAS been
    refunded (by a demo run) gets a fresh one, which is what makes the demos
    repeatable.
    """
    for order_id in orders:
        amount = ORDER_AMOUNTS.get(order_id)
        if amount is None:
            report.orders.append(
                {"order_id": order_id, "payment_intent": "-", "amount": "-",
                 "status": "SKIPPED: no amount configured for this order"}
            )
            continue

        existing = stripe.PaymentIntent.search(
            query=f"metadata['order_id']:'{order_id}'", limit=100
        ).data
        reusable = next(
            (
                pi
                for pi in existing
                if pi.status == "succeeded" and not getattr(pi, "amount_refunded", 0)
            ),
            None,
        )
        if reusable is not None:
            report.orders.append(
                {"order_id": order_id, "payment_intent": reusable.id,
                 "amount": f"${reusable.amount / 100:,.2f}", "status": "exists, refundable"}
            )
            continue

        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency="usd",
            payment_method="pm_card_visa",
            confirm=True,
            automatic_payment_methods={"enabled": True, "allow_redirects": "never"},
            metadata={"order_id": order_id},
            idempotency_key=f"seed:pi:{order_id}:{amount}:{len(existing)}",
        )
        report.orders.append(
            {"order_id": order_id, "payment_intent": intent.id,
             "amount": f"${amount / 100:,.2f}", "status": f"created ({intent.status})"}
        )


# ---------------------------------------------------------------------------
# 4. Slack smoke test
# ---------------------------------------------------------------------------


def seed_slack(slack, channel_id: str, report: SeedReport) -> None:
    """Post one completion message. If this fails, the Slack wiring is wrong."""
    counts = (
        f"{len(report.products)} product(s), "
        f"{len(report.notion_rows)} catalog row(s), "
        f"{len(report.orders)} order(s)"
    )
    response = slack.chat_postMessage(
        channel=channel_id,
        text=f"Readback seed completed: {counts}.",
    )
    report.slack_ts = response["ts"]


# ---------------------------------------------------------------------------
# 5. Summary table
# ---------------------------------------------------------------------------


def print_report(report: SeedReport) -> None:
    def table(title: str, columns: list[str], rows: list[dict]) -> None:
        print(f"\n{title}")
        if not rows:
            print("  (nothing)")
            return
        widths = [
            max(len(col), *(len(str(row.get(col, ""))) for row in rows))
            for col in columns
        ]
        print("  " + "  ".join(col.ljust(w) for col, w in zip(columns, widths)))
        print("  " + "  ".join("-" * w for w in widths))
        for row in rows:
            print("  " + "  ".join(str(row.get(c, "")).ljust(w) for c, w in zip(columns, widths)))

    print("\n" + "=" * 72)
    print("READBACK SEED")
    print("=" * 72)
    table("STRIPE PRODUCTS", ["product_key", "name", "product_id", "price_id", "amount", "status"], report.products)
    table("NOTION CATALOG ROWS", ["name", "page_id", "price_id", "status"], report.notion_rows)
    table("STRIPE ORDERS", ["order_id", "payment_intent", "amount", "status"], report.orders)
    print(f"\nSLACK  message ts: {report.slack_ts or '(not posted)'}")
    print("=" * 72 + "\n")


# ---------------------------------------------------------------------------


def _require_env(*names: str) -> dict[str, str]:
    values = {name: os.environ.get(name, "") for name in names}
    missing = [name for name, value in values.items() if not value]
    if missing:
        print(
            f"Missing required environment variable(s): {', '.join(missing)}.\n"
            f"Copy .env.example to .env and fill them in.",
            file=sys.stderr,
        )
        raise SystemExit(2)
    return values


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="readback.seed",
        description="Seed live Stripe/Notion/Slack state for Readback development.",
    )
    parser.add_argument(
        "--orders",
        nargs="+",
        default=DEFAULT_ORDERS,
        metavar="ORDER_ID",
        help=f"order IDs to create payments for (default: {' '.join(DEFAULT_ORDERS)})",
    )
    args = parser.parse_args(argv)

    load_dotenv()
    env = _require_env(
        "STRIPE_SECRET_KEY", "NOTION_TOKEN", "NOTION_CATALOG_DB",
        "SLACK_BOT_TOKEN", "SLACK_CHANNEL_ID",
    )

    import stripe as stripe_sdk
    from notion_client import Client as NotionClient
    from slack_sdk import WebClient

    stripe_sdk.api_key = env["STRIPE_SECRET_KEY"]
    notion = NotionClient(auth=env["NOTION_TOKEN"])
    slack = WebClient(token=env["SLACK_BOT_TOKEN"])

    report = SeedReport()
    resolved = seed_products(stripe_sdk, report)
    seed_notion(notion, env["NOTION_CATALOG_DB"], resolved, report)
    seed_payments(stripe_sdk, list(args.orders), report)
    seed_slack(slack, env["SLACK_CHANNEL_ID"], report)
    print_report(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
