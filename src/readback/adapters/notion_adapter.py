"""Notion adapter. Interface only — no implementation yet."""

from __future__ import annotations

from ..types import Effect, EffectResult
from .base import Adapter


class NotionAdapter(Adapter):
    name = "notion"

    def __init__(self, client=None, catalog_db: str | None = None,
                 audit_db: str | None = None, **kwargs) -> None:
        # TODO: accept a notion_client.Client; read NOTION_TOKEN,
        #       NOTION_CATALOG_DB and NOTION_AUDIT_DB from the environment.
        self.client = client
        self.catalog_db = catalog_db
        self.audit_db = audit_db

    def plan(self, request) -> list[Effect]:
        # TODO: no write. Resolve the target row up front with
        #       client.databases.query(database_id=self.catalog_db,
        #           filter={"property": "Name", "title": {"equals": "Pro"}})
        #       so the effect carries a concrete page_id. If the query returns
        #       zero or more than one row, plan nothing — that is the ambiguous
        #       product-name case (scenario 14) and belongs to the risk gate.
        raise NotImplementedError

    def apply(self, effect: Effect) -> EffectResult:
        # TODO: update_catalog_row -> client.pages.update(page_id=...,
        #           properties={"Price": {"number": 79},
        #                       "Stripe Price ID": {"rich_text": [...]}})
        # TODO: append_audit_row   -> client.pages.create(
        #           parent={"database_id": self.audit_db}, properties={...})
        #       Notion has no idempotency-key header, so write
        #       effect.idempotency_key into a dedicated "Idempotency Key" text
        #       property and query it before creating.
        raise NotImplementedError

    def verify(self, effect: Effect) -> tuple[bool, str]:
        # TODO: update_catalog_row -> client.pages.retrieve(page_id) as a FRESH
        #       call; assert the Price number and Stripe Price ID text match.
        # TODO: append_audit_row   -> client.databases.query(audit_db,
        #           filter={"property": "Idempotency Key",
        #                   "rich_text": {"equals": effect.idempotency_key}})
        #       and assert results length is EXACTLY 1 — zero means the write
        #       never landed, more than one means a retry duplicated it.
        raise NotImplementedError

    def compensate(self, effect: Effect) -> EffectResult:
        # TODO: update_catalog_row -> client.pages.update(page_id, properties=...)
        #       restoring the prior values captured in effect.params["previous"].
        # TODO: append_audit_row   -> client.pages.update(page_id, archived=True)
        #       (Notion's soft delete; the API has no hard delete for pages).
        raise NotImplementedError
