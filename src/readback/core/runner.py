"""The Readback loop.

    plan
      -> risk gate
      -> per effect: wal.intend, skip if already committed, apply, wal.commit
      -> AFTER every effect: read back by verifying each one against live state
      -> all pass  : success receipt
      -> any fail  : walk the WAL backwards, compensate every COMMITTED effect,
                     then emit a failure receipt naming the failed assertion

Two design points carry most of the weight:

1. **Read-back happens after all writes, not interleaved.** Verifying effect N
   before effect N+1 lands would miss the interactions that actually break ops
   work — a Notion row that a later write clobbers, a Slack post that describes
   a state that changed after it was sent.

2. **A failed apply() is still verified.** Providers report 500s and time out
   on writes that committed. If read-back finds the write, the effect is
   promoted from FAILED to COMMITTED and the run can still succeed.
"""

from __future__ import annotations

from typing import Any, Mapping

from ..planner import plan_request
from ..types import STATUS_OK, Effect, EffectResult, IrreversibleEffect, RunContext
from . import crosscheck, riskgate
from .receipt import (
    OUTCOME_FAILURE,
    OUTCOME_HELD,
    OUTCOME_PARTIAL,
    OUTCOME_REFUSED,
    OUTCOME_SUCCESS,
    CrossCheckResult,
    ManualRemediation,
    ProviderCall,
    Receipt,
    Verification,
    diff_snapshots,
)
from .wal import WAL


def run(
    request_text: str,
    adapters: Mapping[str, Any],
    run_id: str | None = None,
    root: str = "runs",
    write_receipt: bool = True,
    readback: bool = True,
) -> Receipt:
    """Execute one request end to end and return its receipt.

    Passing an existing `run_id` resumes that run: its WAL is replayed and any
    effect already COMMITTED is skipped rather than re-applied.

    `readback=False` is the NAIVE-AGENT BASELINE the eval harness measures
    against. It skips per-effect verify and the cross-app checks, and reports
    success when every apply() returned ok -- i.e. it believes the provider's
    response. Compensation never fires, because nothing ever detects a reason
    to roll back.

    It is a flag on this function rather than a second implementation on
    purpose: planning, the risk gate, WAL bookkeeping and effect ordering are
    shared verbatim, so any measured difference between the two modes is
    attributable to read-back itself and not to two copies of the loop drifting
    apart.
    """
    ctx = RunContext(request_text=request_text) if run_id is None else RunContext(
        request_text=request_text, run_id=run_id
    )
    receipt = Receipt.for_run(ctx)
    wal = WAL(ctx.run_id, root=root)

    before = _snapshots(adapters)

    # -- plan ------------------------------------------------------------
    plan = plan_request(request_text)
    receipt.planned = [effect.to_dict() for effect in plan.effects]

    # -- risk gate -------------------------------------------------------
    decision = riskgate.evaluate(request_text, plan.effects)
    receipt.gate = decision.to_dict()

    if decision.held:
        # Zero provider calls. Nothing to compensate, nothing to verify.
        receipt.outcome = OUTCOME_HELD
        receipt.reason = f"Held for human approval. {decision.reason}"
        return _finish(receipt, root, write_receipt)

    if plan.refused:
        receipt.outcome = OUTCOME_REFUSED
        receipt.reason = plan.refusal or "Planner refused the request."
        return _finish(receipt, root, write_receipt)

    if not plan.effects:
        receipt.outcome = OUTCOME_REFUSED
        receipt.reason = "Planner produced no effects for this request."
        return _finish(receipt, root, write_receipt)

    # -- order -----------------------------------------------------------
    # Irreversible effects run LAST.
    #
    # Rollback is only total while every committed effect still has an inverse.
    # If the refund runs first and the Notion write then fails read-back, the
    # money is already gone and the best available outcome is PARTIAL. Running
    # every reversible effect first means a plan that is going to fail has the
    # maximum chance of failing while it is still completely undoable -- the
    # refund is not attempted until everything cheap to reverse has already
    # proven it can land.
    #
    # Stable sort: within each group the planner's ordering is preserved, so
    # this reorders only across the reversible/irreversible boundary.
    effects = sorted(plan.effects, key=lambda e: not e.reversible)
    if [e.id for e in effects] != [e.id for e in plan.effects]:
        receipt.planned = [effect.to_dict() for effect in effects]

    # -- apply -----------------------------------------------------------
    for effect in effects:
        adapter = _adapter_for(adapters, effect)
        wal.intend(effect)

        if wal.already_committed(effect.idempotency_key):
            # A previous attempt of this run already landed this write.
            receipt.calls.append(
                ProviderCall(
                    phase="apply",
                    app=effect.app,
                    action=effect.action,
                    effect_id=effect.id,
                    idempotency_key=effect.idempotency_key,
                    status="skipped",
                    latency_ms=0.0,
                    error=None,
                )
            )
            continue

        result = adapter.apply(effect)
        receipt.calls.append(_call("apply", effect, result))

        if result.status == STATUS_OK:
            wal.commit(effect, result)
        else:
            # NOT a verdict that the write is absent. Read-back decides.
            wal.fail(effect, result)

    # -- read back -------------------------------------------------------
    if not readback:
        # Baseline: trust the provider. No fresh reads, no cross-checks, no
        # compensation. Success is "every apply returned ok", which is exactly
        # the belief this project exists to disprove.
        applied = [c for c in receipt.calls if c.phase == "apply"]
        bad = [c for c in applied if c.status not in (STATUS_OK, "skipped")]
        if bad:
            receipt.outcome = OUTCOME_FAILURE
            receipt.reason = (
                f"[readback disabled] {len(bad)} of {len(applied)} apply call(s) "
                f"reported an error: {bad[0].app}.{bad[0].action} -> {bad[0].error}. "
                f"No read-back was performed, so whether the writes landed is unknown."
            )
        else:
            receipt.outcome = OUTCOME_SUCCESS
            receipt.reason = (
                f"[readback disabled] All {len(applied)} apply call(s) returned ok. "
                f"No live state was re-read; this is the provider's word, not evidence."
            )
        receipt.state_diff = _diff(adapters, before)
        return _finish(receipt, root, write_receipt)

    failures: list[Verification] = []
    for effect in effects:
        adapter = _adapter_for(adapters, effect)
        passed, detail = adapter.verify(effect)
        receipt.verifications.append(
            Verification(
                app=effect.app,
                action=effect.action,
                effect_id=effect.id,
                passed=passed,
                detail=detail,
            )
        )
        if passed:
            if not wal.already_committed(effect.idempotency_key):
                # The write landed even though the provider said otherwise.
                wal.commit(effect)
        else:
            failures.append(receipt.verifications[-1])

    # -- cross-app checks --------------------------------------------------
    # Only after every per-effect verify has passed. Each assertion reads a
    # fact from a DIFFERENT app than the one that wrote it, which is the only
    # way to catch the failure where every individual write landed but the
    # apps no longer agree with each other.
    cross_failures: list[CrossCheckResult] = []
    if not failures:
        for check in crosscheck.build(adapters, effects, ctx.run_id):
            passed, detail = check.evaluate()
            result = CrossCheckResult(
                name=check.name,
                reads_from=check.reads_from,
                written_by=check.written_by,
                description=check.description,
                passed=passed,
                detail=detail,
            )
            receipt.crosschecks.append(result)
            if not passed:
                cross_failures.append(result)

    if not failures and not cross_failures:
        receipt.outcome = OUTCOME_SUCCESS
        receipt.reason = (
            f"All {len(receipt.verifications)} read-back assertion(s) and "
            f"{len(receipt.crosschecks)} cross-app check(s) passed against live state."
        )
        receipt.state_diff = _diff(adapters, before)
        return _finish(receipt, root, write_receipt)

    # -- compensate ------------------------------------------------------
    # Reverse order, so later writes are undone before the writes they depended
    # on. An effect with no inverse does not stop the walk: everything else is
    # still reversed, and the un-reversible one is collected for the receipt.
    #
    # Candidates are COMMITTED *and* FAILED. A failed apply() is not evidence
    # that the write is absent -- a provider that times out after committing
    # leaves the row in place and the WAL saying FAILED. Compensating only the
    # COMMITTED ones orphans it. compensate() is contractually idempotent and
    # reports 'skipped' when there is nothing there, so the cost of asking is a
    # no-op and the cost of not asking is permanent.
    for record in reversed(wal.reversal_candidates()):
        # Rebuilt from the WAL, not from memory, so this path behaves the same
        # in a restarted process as it does here. prior_state rides along.
        effect = Effect.from_record(record)
        adapter = _adapter_for(adapters, effect)
        try:
            result = adapter.compensate(effect)
        except IrreversibleEffect as exc:
            receipt.manual_remediation.append(
                ManualRemediation(
                    app=exc.app or effect.app,
                    action=effect.action,
                    effect_id=effect.id,
                    object_id=exc.object_id,
                    what=str(exc),
                )
            )
            receipt.calls.append(
                ProviderCall(
                    phase="compensate",
                    app=effect.app,
                    action=effect.action,
                    effect_id=effect.id,
                    idempotency_key=effect.idempotency_key,
                    status="irreversible",
                    latency_ms=0.0,
                    error=str(exc),
                )
            )
            continue
        receipt.calls.append(_call("compensate", effect, result))
        wal.compensated(effect, result)

    reason_head = _failure_head(failures, cross_failures, receipt)

    if receipt.manual_remediation:
        # NEVER success, and never plain failure either: the system is in a
        # state no automated step can finish cleaning up.
        receipt.outcome = OUTCOME_PARTIAL
        objects = "; ".join(
            f"{m.app}.{m.action} -> {m.object_id}" for m in receipt.manual_remediation
        )
        receipt.reason = (
            f"{reason_head} Every reversible effect was compensated, but "
            f"{len(receipt.manual_remediation)} committed effect(s) have no provider "
            f"inverse and need a human: {objects}."
        )
        _notify_manual_remediation(adapters, receipt)
    else:
        receipt.outcome = OUTCOME_FAILURE
        receipt.reason = f"{reason_head} All committed effects were compensated."

    receipt.state_diff = _diff(adapters, before)
    return _finish(receipt, root, write_receipt)


# -- helpers ---------------------------------------------------------------


def _failure_head(
    failures: list[Verification],
    cross_failures: list[CrossCheckResult],
    receipt: Receipt,
) -> str:
    """Name the assertion that actually failed, verify or cross-check."""
    if failures:
        first = failures[0]
        return (
            f"Read-back failed on {first.app}.{first.action}: {first.detail} "
            f"({len(failures)} of {len(receipt.verifications)} assertion(s) failed)."
        )
    first_cross = cross_failures[0]
    return (
        f"Cross-app check failed: {first_cross.detail} "
        f"({len(cross_failures)} of {len(receipt.crosschecks)} cross-check(s) failed). "
        f"Every per-effect verification passed, so each write landed in its own app "
        f"but the apps disagree with each other."
    )


def _notify_manual_remediation(adapters: Mapping[str, Any], receipt: Receipt) -> None:
    """Post the remediation notice to Slack.

    Best effort by design: if Slack itself is the thing that is broken, the
    receipt on disk is still the durable record and must not be lost to an
    exception raised while trying to announce it.
    """
    slack = adapters.get("slack")
    notify = getattr(slack, "post_notice", None)
    if notify is None:
        return
    lines = [
        f":rotating_light: Readback run `{receipt.run_id}` could not fully roll back.",
        f"Request: {receipt.requested}",
        f"Reason: {receipt.reason}",
        "",
        "Needs a human:",
    ]
    for item in receipt.manual_remediation:
        lines.append(f"• `{item.app}.{item.action}` object `{item.object_id}` — {item.what}")
    try:
        notify("\n".join(lines))
    except BaseException:  # noqa: BLE001
        pass


def _adapter_for(adapters: Mapping[str, Any], effect: Effect):
    try:
        return adapters[effect.app]
    except KeyError:
        raise KeyError(
            f"No adapter registered for app {effect.app!r}; "
            f"have {sorted(adapters)}"
        ) from None


def _call(phase: str, effect: Effect, result: EffectResult) -> ProviderCall:
    body = result.provider_response if isinstance(result.provider_response, dict) else {}
    return ProviderCall(
        phase=phase,
        app=effect.app,
        action=effect.action,
        effect_id=effect.id,
        idempotency_key=effect.idempotency_key,
        status=result.status,
        latency_ms=result.latency_ms,
        error=result.error,
        attempts=body.get("attempts", []) or [],
    )


def _snapshots(adapters: Mapping[str, Any]) -> dict[str, dict]:
    """Capture pre-run state from any adapter that can produce one."""
    return {
        name: adapter.snapshot()
        for name, adapter in adapters.items()
        if hasattr(adapter, "snapshot")
    }


def _diff(adapters: Mapping[str, Any], before: dict[str, dict]) -> dict[str, Any]:
    return {
        name: diff_snapshots(before[name], adapter.snapshot())
        for name, adapter in adapters.items()
        if name in before and hasattr(adapter, "snapshot")
    }


def _finish(receipt: Receipt, root: str, write_receipt: bool) -> Receipt:
    if write_receipt:
        receipt.write(root=root)
    return receipt
