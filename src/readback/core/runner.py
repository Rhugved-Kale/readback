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
from ..types import STATUS_OK, Effect, EffectResult, RunContext
from . import riskgate
from .receipt import (
    OUTCOME_FAILURE,
    OUTCOME_HELD,
    OUTCOME_REFUSED,
    OUTCOME_SUCCESS,
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
) -> Receipt:
    """Execute one request end to end and return its receipt.

    Passing an existing `run_id` resumes that run: its WAL is replayed and any
    effect already COMMITTED is skipped rather than re-applied.
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

    # -- apply -----------------------------------------------------------
    for effect in plan.effects:
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
    failures: list[Verification] = []
    for effect in plan.effects:
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

    if not failures:
        receipt.outcome = OUTCOME_SUCCESS
        receipt.reason = (
            f"All {len(receipt.verifications)} read-back assertion(s) passed "
            f"against live state."
        )
        receipt.state_diff = _diff(adapters, before)
        return _finish(receipt, root, write_receipt)

    # -- compensate ------------------------------------------------------
    for record in reversed(wal.committed_effects()):
        effect = Effect(
            app=record["app"],
            action=record["action"],
            params=record["params"],
            idempotency_key=record["idempotency_key"],
            id=record["effect_id"],
        )
        adapter = _adapter_for(adapters, effect)
        result = adapter.compensate(effect)
        receipt.calls.append(_call("compensate", effect, result))
        wal.compensated(effect, result)

    first = failures[0]
    receipt.outcome = OUTCOME_FAILURE
    receipt.reason = (
        f"Read-back failed on {first.app}.{first.action}: {first.detail} "
        f"({len(failures)} of {len(receipt.verifications)} assertion(s) failed). "
        f"All committed effects were compensated."
    )
    receipt.state_diff = _diff(adapters, before)
    return _finish(receipt, root, write_receipt)


# -- helpers ---------------------------------------------------------------


def _adapter_for(adapters: Mapping[str, Any], effect: Effect):
    try:
        return adapters[effect.app]
    except KeyError:
        raise KeyError(
            f"No adapter registered for app {effect.app!r}; "
            f"have {sorted(adapters)}"
        ) from None


def _call(phase: str, effect: Effect, result: EffectResult) -> ProviderCall:
    return ProviderCall(
        phase=phase,
        app=effect.app,
        action=effect.action,
        effect_id=effect.id,
        idempotency_key=effect.idempotency_key,
        status=result.status,
        latency_ms=result.latency_ms,
        error=result.error,
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
