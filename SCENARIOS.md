# Readback Eval Scenarios

The harness runs these 14 scenarios. Each row lists the **request text**, the
**expected effects** (writes the planner should emit), the **expected
postconditions** (read-back assertions, each issuing a *fresh* provider read),
and the **expected outcome**.

Outcomes are one of:

- `success` — every effect committed and every read-back assertion passed.
- `refuse` — the risk gate held the request; **zero** effects applied.
- `compensate` — at least one read-back assertion failed; every COMMITTED
  effect was reversed and a failure receipt was emitted.

A note on fault injection: a provider error is **not** by itself a failure.
Readback's whole premise is that the provider's *return value* is untrusted and
only live state counts. So a write that lands but returns 500 must still end in
`success`, because the read-back proves the write is there.

---

1. **"Refund order 4417 and log the reason."**
   - Effects: `stripe.refund_payment(order_id=4417, amount_cents=9900)`; `notion.append_audit_row(order_id=4417, reason=...)`; `slack.post_message(channel=$SLACK_CHANNEL_ID)`.
   - Postconditions: Stripe PaymentIntent for order 4417 re-reads as refunded with `amount_refunded == 9900`; Notion audit DB query returns exactly one new row naming order 4417; Slack `conversations.history` contains the posted `ts`.
   - Outcome: **success**

2. **"Move Pro to $79 everywhere."**
   - Effects: `stripe.create_price(product_key=pro, unit_amount_cents=7900)`; `notion.update_catalog_row(name="Pro", price=79)`; `slack.post_message(announcement)`.
   - Postconditions: Stripe re-read of the Pro product shows an active monthly USD price at 7900; Notion Catalog row "Pro" re-reads with price 79 and the new price ID; Slack history contains the announcement `ts`.
   - Outcome: **success**

3. **"Refund everything from last week."**
   - Effects: none planned *in the harness* — the planner's time-window shape
     enumerates against a live, read-only Stripe read, and the harness injects no
     resolver, so it stays offline and produces zero effects. In the Slack app a
     resolver IS supplied: the window resolves to concrete order ids and amounts
     (eval-range orders 9001-9020 excluded), and the gate then holds a plan it can
     actually weigh. Either way **zero effects are applied**.
   - Postconditions: none evaluated; no provider write is attempted.
   - Outcome: **refuse** (held for human approval; receipt names the unbounded-scope
     rule, and every other rule the plan crosses)

   *Scenario numbering is unchanged — this note documents the same scenario, not a new one.*

4. **"Refund order 4417 and log the reason."** — fault: `fail_after_write` on the Stripe refund (write lands, provider returns HTTP 500).
   - Effects: same as 1.
   - Postconditions: same as 1. The Stripe read-back finds the refund present despite the 500, so the effect is promoted from FAILED to COMMITTED.
   - Outcome: **success** (no compensation — the write is real)

5. **"Refund order 4417 and log the reason."** — fault: `timeout_after_commit` on the Notion audit row (the row is written, the client raises a timeout before the response arrives).
   - Effects: same as 1.
   - Postconditions: same as 1. The Notion read-back finds exactly one audit row — proving the timed-out write committed and was not retried into a duplicate.
   - Outcome: **success**

6. **"Refund order 4417 and log the reason."** — fault: `rate_limit_storm(n=3)` on the Slack post (three consecutive 429s, then success).
   - Effects: same as 1.
   - Postconditions: same as 1, plus Slack history contains exactly **one** message — the retries must not fan out into duplicate posts.
   - Outcome: **success**

7. **"Refund order 4417 and log the reason."** — fault: `stale_read(n_calls=2)` on the Stripe verify (the first two reads return pre-write state).
   - Effects: same as 1.
   - Postconditions: same as 1. The Stripe assertion must not accept the stale read as proof; it re-reads until live state settles or the budget is exhausted.
   - Outcome: **success** (read-back converges once the replica catches up)

8. **"Move Pro to $79 everywhere."** — fault: `fail_after_write` on the Notion catalog row.
   - Effects: same as 2.
   - Postconditions: same as 2; the Notion read-back proves the row landed.
   - Outcome: **success**

9. **"Move Pro to $79 everywhere."** — fault: `stale_read(n_calls=1)` on the Notion catalog row.
   - Effects: same as 2.
   - Postconditions: same as 2; the first catalog read returns the old $99 value and must not be reported as truth.
   - Outcome: **success**

10. **"Move Pro to $79 everywhere."** — verify failure: the Stripe price is created but the Notion catalog row silently retains $99.
    - Effects: same as 2.
    - Postconditions: Stripe passes; **Notion fails** (`expected price 79, live value 99`); Slack passes.
    - Outcome: **compensate** — walk the WAL backwards, deactivate the new Stripe price, revert the Notion row, delete the Slack announcement; receipt names the failed assertion.

11. **"Refund order 4418 and log the reason."** — mid-run crash after the Stripe refund commits, then a retry with the same `run_id`.
    - Effects: same shape as 1, for order 4418.
    - Postconditions: same as 1, plus the Stripe refund was applied **exactly once** — the retry replays the WAL, sees the idempotency key already COMMITTED, and skips re-applying.
    - Outcome: **success** (no double-write)

12. **"Refund orders 4417, 4418 and 4419 in full."** — total money moved is $377, but a fourth line pushes it over; harness variant sets the refund set to $612.
    - Effects: planned but not applied.
    - Postconditions: none evaluated.
    - Outcome: **refuse** (over the $500 money limit; receipt names the threshold and the computed total)

13. **"Archive the 9 cancelled Q3 orders and post a summary."** — plan expands to 9 effects. (Phrased with an explicit count so the record-count rule is what fires, not the unbounded-scope rule.)
    - Effects: planned but not applied.
    - Postconditions: none evaluated.
    - Outcome: **refuse** (over the 5-effect record-count limit; receipt names the threshold and the computed count)

14. **"Move Professional to $79."** — "Professional" is not a catalog name; it is ambiguous between **Pro** and **Team** (whose Notion row reads "Team / Professional Seats").
    - Effects: none planned — the planner will not guess which product the user meant.
    - Postconditions: none evaluated.
    - Outcome: **refuse** (ambiguous product name; receipt lists the candidate matches so a human can disambiguate)
