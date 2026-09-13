"""Notion adapter against the live API.

    notion.append_audit_row(run_id, action, details, amount, result)
    notion.update_catalog_price(product_name, new_price, stripe_price_id)

Uses `data_sources.query` throughout. `databases.query` does not exist in
Notion API version 2025-09-03 -- a database now holds one or more data sources
and rows belong to the data source. Reintroducing the old call is how the first
seed run died.

IDEMPOTENCY LIMITATION: Notion has no idempotency-key header. A retried
pages.create WILL create a second row. The defences, in order:
  1. the WAL's already_committed() check, which stops the retry before it
     reaches this adapter at all;
  2. a pre-write query for a row already carrying this run_id (below);
  3. verify(), which asserts EXACTLY ONE row matches the run, so a double write
     fails read-back and triggers compensation rather than passing silently.
Defence 2 is a query-then-write with a real race window. It narrows the gap; it
does not close it. Defence 3 is what actually makes a duplicate non-silent.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Callable

from notion_client import Client as NotionClient

from ..core import retry
from ..seed import data_source_id
from ..types import Effect, EffectResult, IrreversibleEffect
from .base import Adapter
from .live_base import LiveAdapter

#: Audit Log columns. Amount and Timestamp were added via the API so that
#: verify() can assert a typed number instead of grepping inside Details.
AUDIT_NAME = "Name"
AUDIT_ACTION = "Action"
AUDIT_DETAILS = "Details"
AUDIT_AMOUNT = "Amount"
AUDIT_RESULT = "Result"
AUDIT_RUN_ID = "Run ID"
AUDIT_TIMESTAMP = "Timestamp"

#: Imported by value to keep this module free of a circular import.
_INJECT_NOTION_DRIFT = "notion_drift"
_INJECT_DRIFT_DOLLARS = 10

#: Catalog columns.
CATALOG_NAME = "Name"
CATALOG_PRICE = "Price"
CATALOG_PRICE_ID = "Stripe Price ID"


class NotionAdapter(LiveAdapter, Adapter):
    name = "notion"

    ACTIONS = {
        "append_audit_row": "audit",
        "update_catalog_price": "catalog",
    }

    def __init__(
        self,
        client=None,
        run_id: str = "",
        catalog_db: str | None = None,
        audit_db: str | None = None,
        stripe_price_lookup: Callable[[str], dict | None] | None = None,
        injection: str | None = None,
    ) -> None:
        self.client = client or NotionClient(auth=os.environ.get("NOTION_TOKEN", ""))
        self.run_id = run_id
        self.catalog_db = catalog_db or os.environ.get("NOTION_CATALOG_DB", "")
        self.audit_db = audit_db or os.environ.get("NOTION_AUDIT_DB", "")
        #: Injected rather than imported: the catalog row has to record the
        #: Stripe price id, and an adapter that reached into Stripe itself would
        #: make the cross-check circular. The live factory wires this to the
        #: Stripe adapter's public live read.
        self.stripe_price_lookup = stripe_price_lookup
        #: Deliberate fault for live demonstration. See readback/injection.py;
        #: refused unless READBACK_ALLOW_INJECTION=1 and the adapters are live.
        self.injection = injection
        self._source_cache: dict[str, str] = {}

    # -- plan --------------------------------------------------------------

    def plan(self, request) -> list[Effect]:
        """Notion's share of a request. Pure: no writes, no reads."""
        return [
            e for e in (getattr(request, "effects", request) or [])
            if isinstance(e, Effect) and e.app == self.name
        ]

    # -- apply -------------------------------------------------------------

    def apply(self, effect: Effect) -> EffectResult:
        action = self.canonical(effect.action)
        if action == "append_audit_row":
            return self._apply_audit(effect)
        if action == "update_catalog_price":
            return self._apply_catalog(effect)
        return self._skipped(effect, f"notion adapter does not handle {effect.action!r}")

    def _apply_audit(self, effect: Effect) -> EffectResult:
        source = self._source(self.audit_db)
        run_id = self._run_id(effect)

        # Defence 2: a row for this run already exists, so don't write another.
        existing = self._rows_for_run(source, run_id)
        if existing:
            effect.reversible = True
            effect.prior_state = {"created_page_id": existing[0]["id"], "pre_existing": True}
            return self._skipped(
                effect,
                f"audit row for run {run_id} already exists; not writing a duplicate",
                {"page_id": existing[0]["id"]},
            )

        # Pre-write state: the audit row is an INSERT, so the prior state is
        # "no row existed". compensate() archives what we create, restoring it.
        effect.reversible = True
        effect.prior_state = {"existed_before": False, "created_page_id": None}

        amount = self._amount_dollars(effect)
        properties = {
            AUDIT_NAME: {"title": [{"text": {"content": self._title(effect)}}]},
            AUDIT_ACTION: self._rich(str(effect.params.get("kind") or effect.params.get("action") or effect.action)),
            AUDIT_DETAILS: self._rich(str(effect.params.get("details") or effect.params.get("reason") or "")),
            AUDIT_RESULT: self._rich(str(effect.params.get("result") or "applied")),
            AUDIT_RUN_ID: self._rich(run_id),
            AUDIT_TIMESTAMP: {"date": {"start": datetime.now(timezone.utc).isoformat()}},
        }
        if amount is not None:
            properties[AUDIT_AMOUNT] = {"number": amount}

        outcome = retry.call(
            lambda: self.client.pages.create(
                parent={"type": "data_source_id", "data_source_id": source},
                properties=properties,
            ),
            op="pages.create",
        )
        if not outcome.ok:
            return self._failed(effect, outcome, "pages.create(audit row)")

        page = outcome.value
        effect.prior_state["created_page_id"] = page["id"]
        return self._ok(effect, outcome, {"page_id": page["id"], "amount": amount})

    def _apply_catalog(self, effect: Effect) -> EffectResult:
        source = self._source(self.catalog_db)
        product_name = str(
            effect.params.get("product_name") or effect.params.get("name") or ""
        )
        new_price = self._price_number(effect)

        found = retry.call(lambda: self._row_by_name(source, product_name), op="catalog.query")
        if not found.ok:
            return self._failed(effect, found, "catalog query")
        row = found.value
        if row is None:
            return self._failed(
                effect, found, f"no catalog row with Name={product_name!r}"
            )

        # PRE-WRITE CAPTURE of both columns this effect overwrites.
        prior_price = self._number_of(row, CATALOG_PRICE)
        prior_price_id = self._text_of(row, CATALOG_PRICE_ID)
        effect.reversible = True
        effect.prior_state = {
            "page_id": row["id"],
            "prior_price": prior_price,
            "prior_stripe_price_id": prior_price_id,
        }

        # DELIBERATE FAULT INJECTION. Write a price that disagrees with the one
        # Stripe is being given. Notion still returns success, and the row will
        # read back exactly what we wrote, so Notion is internally consistent --
        # which is the whole point. Only a check that reads STRIPE can see it.
        if self.injection == _INJECT_NOTION_DRIFT:
            new_price = float(new_price) + _INJECT_DRIFT_DOLLARS
            effect.prior_state["injected_price"] = new_price
            effect.prior_state["injection"] = self.injection

        price_id = self._resolve_price_id(effect)
        properties: dict[str, Any] = {CATALOG_PRICE: {"number": new_price}}
        if price_id:
            properties[CATALOG_PRICE_ID] = self._rich(price_id)

        outcome = retry.call(
            lambda: self.client.pages.update(page_id=row["id"], properties=properties),
            op="pages.update",
        )
        if not outcome.ok:
            return self._failed(effect, outcome, "pages.update(catalog row)")

        return self._ok(effect, outcome, {
            "page_id": row["id"],
            "price": new_price,
            "stripe_price_id": price_id,
            "was": {"price": prior_price, "stripe_price_id": prior_price_id},
        })

    # -- verify ------------------------------------------------------------

    def verify(self, effect: Effect) -> tuple[bool, str]:
        """Re-read live Notion state.

        HARD RULE: every branch issues a NEW query or retrieve. None of this
        inspects apply()'s EffectResult, the page object apply() received, or
        any cached property. Page ids come from a fresh query keyed on the
        Effect's own data, so a restarted process reaches the same verdict.
        """
        action = self.canonical(effect.action)
        if action == "append_audit_row":
            return self._verify_audit(effect)
        if action == "update_catalog_price":
            return self._verify_catalog(effect)
        return False, f"notion adapter cannot verify {effect.action!r}"

    def _verify_audit(self, effect: Effect) -> tuple[bool, str]:
        run_id = self._run_id(effect)
        expected_amount = self._amount_dollars(effect)

        def check(attempt: int) -> tuple[bool, str]:
            source = self._source(self.audit_db)
            # FRESH query filtered on Run ID. Also the duplicate detector: two
            # rows here means a retried write landed twice.
            rows = self._rows_for_run(source, run_id)
            if not rows:
                return False, (
                    f"notion.append_audit_row: no audit row with Run ID={run_id!r} "
                    f"(read attempt {attempt})"
                )
            if len(rows) > 1:
                ids = ", ".join(r["id"] for r in rows)
                return False, (
                    f"notion.append_audit_row: expected exactly 1 audit row for run "
                    f"{run_id!r}, live Notion returned {len(rows)} ({ids}) -- a duplicate "
                    f"write landed (read attempt {attempt})"
                )
            row = rows[0]
            actual = self._number_of(row, AUDIT_AMOUNT)
            if expected_amount is not None:
                # TYPED comparison against the number column, not a substring
                # search inside Details. This is why Amount was added.
                if actual is None:
                    return False, (
                        f"notion.append_audit_row: Amount is empty, expected the number "
                        f"{expected_amount} (read attempt {attempt})"
                    )
                if abs(float(actual) - float(expected_amount)) > 1e-9:
                    return False, (
                        f"notion.append_audit_row: expected Amount={expected_amount} "
                        f"(number), live Notion reports {actual} (read attempt {attempt})"
                    )
            return True, (
                f"notion.append_audit_row: live query confirms exactly 1 row for run "
                f"{run_id!r} (page {row['id']}) with Amount={actual} as a typed number "
                f"(read attempt {attempt})"
            )

        return self._reread(check)

    def _verify_catalog(self, effect: Effect) -> tuple[bool, str]:
        # Under injection, Notion is asserted against what NOTION was made to
        # write, not against what the operator asked for. That is deliberate and
        # is what makes the demonstration honest: each app is internally
        # consistent on its own terms, and the incoherence only exists between
        # them. If this asserted the operator's number instead, per-effect
        # verify would catch it and the cross-app check would never run --
        # proving the wrong thing.
        expected_price = float(
            (effect.prior_state or {}).get("injected_price", self._price_number(effect))
        )
        expected_price_id = self._resolve_price_id(effect)
        page_id = (effect.prior_state or {}).get("page_id")
        product_name = str(
            effect.params.get("product_name") or effect.params.get("name") or ""
        )

        def check(attempt: int) -> tuple[bool, str]:
            # FRESH retrieve. Falls back to a fresh query by Name when the WAL
            # record has no page id, so verify works from a bare replay.
            if page_id:
                row = self.client.pages.retrieve(page_id=page_id)
            else:
                row = self._row_by_name(self._source(self.catalog_db), product_name)
            if row is None:
                return False, (
                    f"notion.update_catalog_price: no catalog row for {product_name!r} "
                    f"(read attempt {attempt})"
                )

            actual_price = self._number_of(row, CATALOG_PRICE)
            if actual_price is None or abs(float(actual_price) - float(expected_price)) > 1e-9:
                return False, (
                    f"notion.update_catalog_price: expected Price={expected_price} (number), "
                    f"live Notion reports {actual_price} (read attempt {attempt})"
                )

            if expected_price_id:
                actual_id = self._text_of(row, CATALOG_PRICE_ID)
                if actual_id != expected_price_id:
                    return False, (
                        f"notion.update_catalog_price: expected Stripe Price ID="
                        f"{expected_price_id!r}, live Notion reports {actual_id!r} "
                        f"(read attempt {attempt})"
                    )

            return True, (
                f"notion.update_catalog_price: live read of page {row['id']} confirms "
                f"Price={actual_price} (number) and Stripe Price ID="
                f"{self._text_of(row, CATALOG_PRICE_ID)!r} (read attempt {attempt})"
            )

        return self._reread(check)

    # -- compensate --------------------------------------------------------

    def compensate(self, effect: Effect) -> EffectResult:
        action = self.canonical(effect.action)
        if action == "append_audit_row":
            return self._compensate_audit(effect)
        if action == "update_catalog_price":
            return self._compensate_catalog(effect)
        return self._skipped(effect, f"nothing to compensate for {effect.action!r}")

    def _compensate_audit(self, effect: Effect) -> EffectResult:
        """Archive the audit row this effect created.

        Idempotent: an already-archived page reports 'skipped'. A row that
        pre-existed this run is left alone -- we only undo what we wrote.
        """
        prior = effect.prior_state or {}
        if prior.get("pre_existing"):
            return self._skipped(effect, "audit row pre-dated this run; left untouched")

        page_id = prior.get("created_page_id")
        if not page_id:
            # Nothing was captured, so fall back to a fresh lookup by run id
            # rather than leaving an orphan row behind.
            rows = self._rows_for_run(self._source(self.audit_db), self._run_id(effect))
            page_id = rows[0]["id"] if rows else None
        if not page_id:
            return self._skipped(effect, "no audit row found to archive")

        live = self.client.pages.retrieve(page_id=page_id)
        if live.get("archived") or live.get("in_trash"):
            return self._skipped(effect, "audit row already archived", {"page_id": page_id})

        outcome = retry.call(
            lambda: self.client.pages.update(page_id=page_id, archived=True),
            op="pages.archive",
        )
        if not outcome.ok:
            return self._failed(effect, outcome, "pages.update(archive audit row)")
        return self._ok(effect, outcome, {
            "archived_page_id": page_id,
            "note": "audit row archived; Notion has no hard delete via the API",
        })

    def _compensate_catalog(self, effect: Effect) -> EffectResult:
        """Write the captured prior Price and Stripe Price ID back."""
        prior = effect.prior_state or {}
        page_id = prior.get("page_id")
        if not page_id:
            raise IrreversibleEffect(
                f"Notion catalog row for {effect.params.get('name')!r} cannot be reversed: "
                f"no prior state was captured before the write.",
                app=self.name,
                object_id=str(page_id or ""),
            )

        properties: dict[str, Any] = {CATALOG_PRICE: {"number": prior.get("prior_price")}}
        properties[CATALOG_PRICE_ID] = self._rich(prior.get("prior_stripe_price_id") or "")

        live = self.client.pages.retrieve(page_id=page_id)
        if (
            self._number_of(live, CATALOG_PRICE) == prior.get("prior_price")
            and self._text_of(live, CATALOG_PRICE_ID) == (prior.get("prior_stripe_price_id") or "")
        ):
            return self._skipped(effect, "catalog row already holds its prior values")

        outcome = retry.call(
            lambda: self.client.pages.update(page_id=page_id, properties=properties),
            op="pages.restore",
        )
        if not outcome.ok:
            return self._failed(effect, outcome, "pages.update(restore catalog row)")
        return self._ok(effect, outcome, {
            "page_id": page_id,
            "restored_price": prior.get("prior_price"),
            "restored_stripe_price_id": prior.get("prior_stripe_price_id"),
        })

    # -- live reads used by cross-checks -----------------------------------

    def live_catalog_row(self, product_name: str) -> dict[str, Any] | None:
        """Fresh read of one catalog row. Used by crosscheck.py."""
        row = self._row_by_name(self._source(self.catalog_db), product_name)
        if row is None:
            return None
        return {
            "page_id": row["id"],
            "price": self._number_of(row, CATALOG_PRICE),
            "stripe_price_id": self._text_of(row, CATALOG_PRICE_ID),
        }

    def live_audit_row(self, run_id: str) -> dict[str, Any] | None:
        """Fresh read of this run's audit row. Used by crosscheck.py."""
        rows = self._rows_for_run(self._source(self.audit_db), run_id)
        if len(rows) != 1:
            return None
        row = rows[0]
        return {
            "page_id": row["id"],
            "amount": self._number_of(row, AUDIT_AMOUNT),
            "action": self._text_of(row, AUDIT_ACTION),
        }

    # -- internals ---------------------------------------------------------

    def _source(self, database_id: str) -> str:
        """database_id -> data_source_id, memoized.

        Safe to cache: it is workspace structure, not the row state under test.
        Nothing verify() asserts on is cached.
        """
        if database_id not in self._source_cache:
            self._source_cache[database_id] = data_source_id(self.client, database_id)
        return self._source_cache[database_id]

    def _rows_for_run(self, source: str, run_id: str) -> list[dict]:
        return self.client.data_sources.query(
            data_source_id=source,
            filter={"property": AUDIT_RUN_ID, "rich_text": {"equals": run_id}},
        ).get("results", [])

    def _row_by_name(self, source: str, name: str) -> dict | None:
        rows = self.client.data_sources.query(
            data_source_id=source,
            filter={"property": CATALOG_NAME, "title": {"equals": name}},
        ).get("results", [])
        return rows[0] if len(rows) == 1 else (rows[0] if rows else None)

    def _run_id(self, effect: Effect) -> str:
        return str(effect.params.get("run_id") or self.run_id or "")

    def _title(self, effect: Effect) -> str:
        kind = effect.params.get("kind") or effect.action
        target = effect.params.get("order_id") or effect.params.get("name") or ""
        return f"{kind} {target}".strip()

    def _amount_dollars(self, effect: Effect) -> float | None:
        if "amount" in effect.params and effect.params["amount"] is not None:
            return float(effect.params["amount"])
        cents = effect.params.get("amount_cents")
        return None if cents is None else round(int(cents) / 100.0, 2)

    def _price_number(self, effect: Effect) -> float:
        value = effect.params.get("new_price", effect.params.get("price"))
        return float(value)

    def _resolve_price_id(self, effect: Effect) -> str:
        """The Stripe price id this row should carry.

        Taken from the effect when the planner supplied one, otherwise from the
        injected live Stripe read. Never from another adapter's apply() result.
        """
        explicit = effect.params.get("stripe_price_id")
        if explicit:
            return str(explicit)
        if self.stripe_price_lookup is None:
            return ""
        key = str(
            effect.params.get("product_key")
            or effect.params.get("name", "")
        ).strip().lower()
        live = self.stripe_price_lookup(key)
        return str(live["price_id"]) if live else ""

    @staticmethod
    def _rich(text: str) -> dict:
        return {"rich_text": [{"text": {"content": text[:2000]}}]}

    @staticmethod
    def _text_of(page: dict, column: str) -> str:
        prop = page.get("properties", {}).get(column)
        if not prop:
            return ""
        kind = prop.get("type")
        parts = prop.get(kind) or []
        if kind in ("rich_text", "title"):
            return "".join(p.get("plain_text", "") for p in parts)
        return ""

    @staticmethod
    def _number_of(page: dict, column: str) -> float | None:
        prop = page.get("properties", {}).get(column)
        if not prop or prop.get("type") != "number":
            return None
        return prop.get("number")
