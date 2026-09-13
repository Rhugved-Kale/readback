# Runs where the oracle disagreed with the reported outcome

Every entry is reproducible from its seed with the command shown.

## S01 refund_happy_path — false alarm

- mode: `readback_off`
- fault: `error_after_write` @ `notion`
- seed: `2100`  (repeat 0)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: notion.append_audit_row -> 500 internal_server_error (write may have landed). No read-back was performed, so whether the writes landed is un
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 1 --profile error_after_write --mode readback_off --seed 2100
```

## S01 refund_happy_path — false alarm

- mode: `readback_off`
- fault: `error_after_write` @ `slack`
- seed: `2101`  (repeat 1)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: slack.post_message -> 500 internal_server_error (write may have landed). No read-back was performed, so whether the writes landed is unknown
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 1 --profile error_after_write --mode readback_off --seed 2101
```

## S01 refund_happy_path — false alarm

- mode: `readback_off`
- fault: `error_after_write` @ `notion`
- seed: `2102`  (repeat 2)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: notion.append_audit_row -> 500 internal_server_error (write may have landed). No read-back was performed, so whether the writes landed is un
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 1 --profile error_after_write --mode readback_off --seed 2102
```

## S01 refund_happy_path — false alarm

- mode: `readback_off`
- fault: `error_after_write` @ `stripe`
- seed: `2103`  (repeat 3)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: stripe.refund_payment -> 500 internal_server_error (write may have landed). No read-back was performed, so whether the writes landed is unkn
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 1 --profile error_after_write --mode readback_off --seed 2103
```

## S01 refund_happy_path — false alarm

- mode: `readback_off`
- fault: `error_after_write` @ `stripe`
- seed: `2104`  (repeat 4)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: stripe.refund_payment -> 500 internal_server_error (write may have landed). No read-back was performed, so whether the writes landed is unkn
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 1 --profile error_after_write --mode readback_off --seed 2104
```

## S01 refund_happy_path — false alarm

- mode: `readback_off`
- fault: `timeout_after_commit` @ `notion`
- seed: `2200`  (repeat 0)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: notion.append_audit_row -> read timeout after commit (write may have landed). No read-back was performed, so whether the writes landed is un
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 1 --profile timeout_after_commit --mode readback_off --seed 2200
```

## S01 refund_happy_path — false alarm

- mode: `readback_off`
- fault: `timeout_after_commit` @ `stripe`
- seed: `2201`  (repeat 1)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: stripe.refund_payment -> read timeout after commit (write may have landed). No read-back was performed, so whether the writes landed is unkn
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 1 --profile timeout_after_commit --mode readback_off --seed 2201
```

## S01 refund_happy_path — false alarm

- mode: `readback_off`
- fault: `timeout_after_commit` @ `stripe`
- seed: `2202`  (repeat 2)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: stripe.refund_payment -> read timeout after commit (write may have landed). No read-back was performed, so whether the writes landed is unkn
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 1 --profile timeout_after_commit --mode readback_off --seed 2202
```

## S01 refund_happy_path — false alarm

- mode: `readback_off`
- fault: `timeout_after_commit` @ `slack`
- seed: `2203`  (repeat 3)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: slack.post_message -> read timeout after commit (write may have landed). No read-back was performed, so whether the writes landed is unknown
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 1 --profile timeout_after_commit --mode readback_off --seed 2203
```

## S01 refund_happy_path — false alarm

- mode: `readback_off`
- fault: `timeout_after_commit` @ `stripe`
- seed: `2204`  (repeat 4)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: stripe.refund_payment -> read timeout after commit (write may have landed). No read-back was performed, so whether the writes landed is unkn
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 1 --profile timeout_after_commit --mode readback_off --seed 2204
```

## S01 refund_happy_path — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_write_drop` @ `stripe`
- seed: `2500`  (repeat 0)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — MISSING stripe: stripe:refund:order-4417

```bash
python -m readback.evals.run --scenario 1 --profile silent_write_drop --mode readback_off --seed 2500
```

## S01 refund_happy_path — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_write_drop` @ `stripe`
- seed: `2501`  (repeat 1)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — MISSING stripe: stripe:refund:order-4417

```bash
python -m readback.evals.run --scenario 1 --profile silent_write_drop --mode readback_off --seed 2501
```

## S01 refund_happy_path — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_write_drop` @ `stripe`
- seed: `2502`  (repeat 2)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — MISSING stripe: stripe:refund:order-4417

```bash
python -m readback.evals.run --scenario 1 --profile silent_write_drop --mode readback_off --seed 2502
```

## S01 refund_happy_path — forbidden effect

- mode: `readback_on`
- fault: `silent_write_drop` @ `notion`
- seed: `2503`  (repeat 3)
- reported: `failure` — Read-back failed on notion.append_audit_row: notion.append_audit_row: expected a record for 'notion:audit:refund-order-4417', live read found none (1 of 3 assertion(s) failed). All committed effects w
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4417; slack: slack:post:refund-order-4417; stripe: stripe:refund:order-4417
- forbidden: compensate attempted on irreversible effect stripe.refund_payment (status=ok)

```bash
python -m readback.evals.run --scenario 1 --profile silent_write_drop --mode readback_on --seed 2503
```

## S01 refund_happy_path — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_write_drop` @ `notion`
- seed: `2503`  (repeat 3)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4417

```bash
python -m readback.evals.run --scenario 1 --profile silent_write_drop --mode readback_off --seed 2503
```

## S01 refund_happy_path — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_write_drop` @ `stripe`
- seed: `2504`  (repeat 4)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — MISSING stripe: stripe:refund:order-4417

```bash
python -m readback.evals.run --scenario 1 --profile silent_write_drop --mode readback_off --seed 2504
```

## S01 refund_happy_path — forbidden effect

- mode: `readback_on`
- fault: `silent_partial_write` @ `slack`
- seed: `2600`  (repeat 0)
- reported: `failure` — Read-back failed on slack.post_message: slack.post_message: text: expected 'Refunded order 4417 ($99.00). Reason: logged at operator request.', live value 'Refunded order 4417 ($99.00). Reason: logged
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4417; slack: slack:post:refund-order-4417; stripe: stripe:refund:order-4417
- forbidden: compensate attempted on irreversible effect stripe.refund_payment (status=ok)

```bash
python -m readback.evals.run --scenario 1 --profile silent_partial_write --mode readback_on --seed 2600
```

## S01 refund_happy_path — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_partial_write` @ `slack`
- seed: `2600`  (repeat 0)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES slack: slack:post:refund-order-4417: text: expected 'Refunded order 4417 ($99.00). Reason: logged at operator request.', found 'Refunded order 4417 ($99.00). Reason: logged at operator request. [unverified]'

```bash
python -m readback.evals.run --scenario 1 --profile silent_partial_write --mode readback_off --seed 2600
```

## S01 refund_happy_path — forbidden effect

- mode: `readback_on`
- fault: `silent_partial_write` @ `slack`
- seed: `2601`  (repeat 1)
- reported: `failure` — Read-back failed on slack.post_message: slack.post_message: text: expected 'Refunded order 4417 ($99.00). Reason: logged at operator request.', live value 'Refunded order 4417 ($99.00). Reason: logged
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4417; slack: slack:post:refund-order-4417; stripe: stripe:refund:order-4417
- forbidden: compensate attempted on irreversible effect stripe.refund_payment (status=ok)

```bash
python -m readback.evals.run --scenario 1 --profile silent_partial_write --mode readback_on --seed 2601
```

## S01 refund_happy_path — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_partial_write` @ `slack`
- seed: `2601`  (repeat 1)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES slack: slack:post:refund-order-4417: text: expected 'Refunded order 4417 ($99.00). Reason: logged at operator request.', found 'Refunded order 4417 ($99.00). Reason: logged at operator request. [unverified]'

```bash
python -m readback.evals.run --scenario 1 --profile silent_partial_write --mode readback_off --seed 2601
```

## S01 refund_happy_path — forbidden effect

- mode: `readback_on`
- fault: `silent_partial_write` @ `stripe`
- seed: `2602`  (repeat 2)
- reported: `failure` — Read-back failed on stripe.refund_payment: stripe.refund_payment: amount_cents: expected 9900, live value 99000 (1 of 3 assertion(s) failed). All committed effects were compensated.
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4417; slack: slack:post:refund-order-4417; stripe: stripe:refund:order-4417
- forbidden: compensate attempted on irreversible effect stripe.refund_payment (status=ok)

```bash
python -m readback.evals.run --scenario 1 --profile silent_partial_write --mode readback_on --seed 2602
```

## S01 refund_happy_path — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_partial_write` @ `stripe`
- seed: `2602`  (repeat 2)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES stripe: stripe:refund:order-4417: amount_cents: expected 9900, found 99000

```bash
python -m readback.evals.run --scenario 1 --profile silent_partial_write --mode readback_off --seed 2602
```

## S01 refund_happy_path — forbidden effect

- mode: `readback_on`
- fault: `silent_partial_write` @ `notion`
- seed: `2603`  (repeat 3)
- reported: `failure` — Read-back failed on notion.append_audit_row: notion.append_audit_row: amount_cents: expected 9900, live value 99000 (1 of 3 assertion(s) failed). All committed effects were compensated.
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4417; slack: slack:post:refund-order-4417; stripe: stripe:refund:order-4417
- forbidden: compensate attempted on irreversible effect stripe.refund_payment (status=ok)

```bash
python -m readback.evals.run --scenario 1 --profile silent_partial_write --mode readback_on --seed 2603
```

## S01 refund_happy_path — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_partial_write` @ `notion`
- seed: `2603`  (repeat 3)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES notion: notion:audit:refund-order-4417: amount_cents: expected 9900, found 99000

```bash
python -m readback.evals.run --scenario 1 --profile silent_partial_write --mode readback_off --seed 2603
```

## S01 refund_happy_path — forbidden effect

- mode: `readback_on`
- fault: `silent_partial_write` @ `stripe`
- seed: `2604`  (repeat 4)
- reported: `failure` — Read-back failed on stripe.refund_payment: stripe.refund_payment: amount_cents: expected 9900, live value 99000 (1 of 3 assertion(s) failed). All committed effects were compensated.
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4417; slack: slack:post:refund-order-4417; stripe: stripe:refund:order-4417
- forbidden: compensate attempted on irreversible effect stripe.refund_payment (status=ok)

```bash
python -m readback.evals.run --scenario 1 --profile silent_partial_write --mode readback_on --seed 2604
```

## S01 refund_happy_path — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_partial_write` @ `stripe`
- seed: `2604`  (repeat 4)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES stripe: stripe:refund:order-4417: amount_cents: expected 9900, found 99000

```bash
python -m readback.evals.run --scenario 1 --profile silent_partial_write --mode readback_off --seed 2604
```

## S01 refund_happy_path — forbidden effect

- mode: `readback_on`
- fault: `divergent_write` @ `stripe`
- seed: `2700`  (repeat 0)
- reported: `failure` — Read-back failed on stripe.refund_payment: stripe.refund_payment: amount_cents: expected 9900, live value 10500 (1 of 3 assertion(s) failed). All committed effects were compensated.
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4417; slack: slack:post:refund-order-4417; stripe: stripe:refund:order-4417
- forbidden: compensate attempted on irreversible effect stripe.refund_payment (status=ok)

```bash
python -m readback.evals.run --scenario 1 --profile divergent_write --mode readback_on --seed 2700
```

## S01 refund_happy_path — SILENT FAILURE

- mode: `readback_off`
- fault: `divergent_write` @ `stripe`
- seed: `2700`  (repeat 0)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES stripe: stripe:refund:order-4417: amount_cents: expected 9900, found 10500

```bash
python -m readback.evals.run --scenario 1 --profile divergent_write --mode readback_off --seed 2700
```

## S01 refund_happy_path — forbidden effect

- mode: `readback_on`
- fault: `divergent_write` @ `notion`
- seed: `2701`  (repeat 1)
- reported: `failure` — Read-back failed on notion.append_audit_row: notion.append_audit_row: amount_cents: expected 9900, live value 10600 (1 of 3 assertion(s) failed). All committed effects were compensated.
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4417; slack: slack:post:refund-order-4417; stripe: stripe:refund:order-4417
- forbidden: compensate attempted on irreversible effect stripe.refund_payment (status=ok)

```bash
python -m readback.evals.run --scenario 1 --profile divergent_write --mode readback_on --seed 2701
```

## S01 refund_happy_path — SILENT FAILURE

- mode: `readback_off`
- fault: `divergent_write` @ `notion`
- seed: `2701`  (repeat 1)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES notion: notion:audit:refund-order-4417: amount_cents: expected 9900, found 10600

```bash
python -m readback.evals.run --scenario 1 --profile divergent_write --mode readback_off --seed 2701
```

## S01 refund_happy_path — forbidden effect

- mode: `readback_on`
- fault: `divergent_write` @ `stripe`
- seed: `2702`  (repeat 2)
- reported: `failure` — Read-back failed on stripe.refund_payment: stripe.refund_payment: amount_cents: expected 9900, live value 10000 (1 of 3 assertion(s) failed). All committed effects were compensated.
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4417; slack: slack:post:refund-order-4417; stripe: stripe:refund:order-4417
- forbidden: compensate attempted on irreversible effect stripe.refund_payment (status=ok)

```bash
python -m readback.evals.run --scenario 1 --profile divergent_write --mode readback_on --seed 2702
```

## S01 refund_happy_path — SILENT FAILURE

- mode: `readback_off`
- fault: `divergent_write` @ `stripe`
- seed: `2702`  (repeat 2)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES stripe: stripe:refund:order-4417: amount_cents: expected 9900, found 10000

```bash
python -m readback.evals.run --scenario 1 --profile divergent_write --mode readback_off --seed 2702
```

## S01 refund_happy_path — forbidden effect

- mode: `readback_on`
- fault: `divergent_write` @ `notion`
- seed: `2703`  (repeat 3)
- reported: `failure` — Read-back failed on notion.append_audit_row: notion.append_audit_row: amount_cents: expected 9900, live value 10100 (1 of 3 assertion(s) failed). All committed effects were compensated.
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4417; slack: slack:post:refund-order-4417; stripe: stripe:refund:order-4417
- forbidden: compensate attempted on irreversible effect stripe.refund_payment (status=ok)

```bash
python -m readback.evals.run --scenario 1 --profile divergent_write --mode readback_on --seed 2703
```

## S01 refund_happy_path — SILENT FAILURE

- mode: `readback_off`
- fault: `divergent_write` @ `notion`
- seed: `2703`  (repeat 3)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES notion: notion:audit:refund-order-4417: amount_cents: expected 9900, found 10100

```bash
python -m readback.evals.run --scenario 1 --profile divergent_write --mode readback_off --seed 2703
```

## S01 refund_happy_path — forbidden effect

- mode: `readback_on`
- fault: `divergent_write` @ `slack`
- seed: `2704`  (repeat 4)
- reported: `failure` — Read-back failed on slack.post_message: slack.post_message: text: expected 'Refunded order 4417 ($99.00). Reason: logged at operator request.', live value 'Refunded order 4417 ($99.00). Reason: logged
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4417; slack: slack:post:refund-order-4417; stripe: stripe:refund:order-4417
- forbidden: compensate attempted on irreversible effect stripe.refund_payment (status=ok)

```bash
python -m readback.evals.run --scenario 1 --profile divergent_write --mode readback_on --seed 2704
```

## S01 refund_happy_path — SILENT FAILURE

- mode: `readback_off`
- fault: `divergent_write` @ `slack`
- seed: `2704`  (repeat 4)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES slack: slack:post:refund-order-4417: text: expected 'Refunded order 4417 ($99.00). Reason: logged at operator request.', found 'Refunded order 4417 ($99.00). Reason: logged at operator request. [unverified]'

```bash
python -m readback.evals.run --scenario 1 --profile divergent_write --mode readback_off --seed 2704
```

## S02 reprice_happy_path — false alarm

- mode: `readback_off`
- fault: `error_after_write` @ `notion`
- seed: `3100`  (repeat 0)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: notion.update_catalog_row -> 500 internal_server_error (write may have landed). No read-back was performed, so whether the writes landed is 
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 2 --profile error_after_write --mode readback_off --seed 3100
```

## S02 reprice_happy_path — false alarm

- mode: `readback_off`
- fault: `error_after_write` @ `notion`
- seed: `3101`  (repeat 1)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: notion.update_catalog_row -> 500 internal_server_error (write may have landed). No read-back was performed, so whether the writes landed is 
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 2 --profile error_after_write --mode readback_off --seed 3101
```

## S02 reprice_happy_path — false alarm

- mode: `readback_off`
- fault: `error_after_write` @ `notion`
- seed: `3102`  (repeat 2)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: notion.update_catalog_row -> 500 internal_server_error (write may have landed). No read-back was performed, so whether the writes landed is 
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 2 --profile error_after_write --mode readback_off --seed 3102
```

## S02 reprice_happy_path — false alarm

- mode: `readback_off`
- fault: `error_after_write` @ `notion`
- seed: `3103`  (repeat 3)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: notion.update_catalog_row -> 500 internal_server_error (write may have landed). No read-back was performed, so whether the writes landed is 
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 2 --profile error_after_write --mode readback_off --seed 3103
```

## S02 reprice_happy_path — false alarm

- mode: `readback_off`
- fault: `error_after_write` @ `stripe`
- seed: `3104`  (repeat 4)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: stripe.create_price -> 500 internal_server_error (write may have landed). No read-back was performed, so whether the writes landed is unknow
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 2 --profile error_after_write --mode readback_off --seed 3104
```

## S02 reprice_happy_path — false alarm

- mode: `readback_off`
- fault: `timeout_after_commit` @ `slack`
- seed: `3200`  (repeat 0)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: slack.post_message -> read timeout after commit (write may have landed). No read-back was performed, so whether the writes landed is unknown
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 2 --profile timeout_after_commit --mode readback_off --seed 3200
```

## S02 reprice_happy_path — false alarm

- mode: `readback_off`
- fault: `timeout_after_commit` @ `slack`
- seed: `3201`  (repeat 1)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: slack.post_message -> read timeout after commit (write may have landed). No read-back was performed, so whether the writes landed is unknown
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 2 --profile timeout_after_commit --mode readback_off --seed 3201
```

## S02 reprice_happy_path — false alarm

- mode: `readback_off`
- fault: `timeout_after_commit` @ `notion`
- seed: `3202`  (repeat 2)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: notion.update_catalog_row -> read timeout after commit (write may have landed). No read-back was performed, so whether the writes landed is 
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 2 --profile timeout_after_commit --mode readback_off --seed 3202
```

## S02 reprice_happy_path — false alarm

- mode: `readback_off`
- fault: `timeout_after_commit` @ `slack`
- seed: `3203`  (repeat 3)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: slack.post_message -> read timeout after commit (write may have landed). No read-back was performed, so whether the writes landed is unknown
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 2 --profile timeout_after_commit --mode readback_off --seed 3203
```

## S02 reprice_happy_path — false alarm

- mode: `readback_off`
- fault: `timeout_after_commit` @ `stripe`
- seed: `3204`  (repeat 4)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: stripe.create_price -> read timeout after commit (write may have landed). No read-back was performed, so whether the writes landed is unknow
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 2 --profile timeout_after_commit --mode readback_off --seed 3204
```

## S02 reprice_happy_path — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_write_drop` @ `notion`
- seed: `3500`  (repeat 0)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — MISSING notion: notion:catalog:pro-7900

```bash
python -m readback.evals.run --scenario 2 --profile silent_write_drop --mode readback_off --seed 3500
```

## S02 reprice_happy_path — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_write_drop` @ `stripe`
- seed: `3501`  (repeat 1)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — MISSING stripe: stripe:price:pro-7900

```bash
python -m readback.evals.run --scenario 2 --profile silent_write_drop --mode readback_off --seed 3501
```

## S02 reprice_happy_path — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_write_drop` @ `notion`
- seed: `3502`  (repeat 2)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — MISSING notion: notion:catalog:pro-7900

```bash
python -m readback.evals.run --scenario 2 --profile silent_write_drop --mode readback_off --seed 3502
```

## S02 reprice_happy_path — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_write_drop` @ `notion`
- seed: `3503`  (repeat 3)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — MISSING notion: notion:catalog:pro-7900

```bash
python -m readback.evals.run --scenario 2 --profile silent_write_drop --mode readback_off --seed 3503
```

## S02 reprice_happy_path — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_write_drop` @ `slack`
- seed: `3504`  (repeat 4)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — MISSING slack: slack:post:price-pro-7900

```bash
python -m readback.evals.run --scenario 2 --profile silent_write_drop --mode readback_off --seed 3504
```

## S02 reprice_happy_path — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_partial_write` @ `stripe`
- seed: `3600`  (repeat 0)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES stripe: stripe:price:pro-7900: unit_amount_cents: expected 7900, found 79000

```bash
python -m readback.evals.run --scenario 2 --profile silent_partial_write --mode readback_off --seed 3600
```

## S02 reprice_happy_path — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_partial_write` @ `stripe`
- seed: `3601`  (repeat 1)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES stripe: stripe:price:pro-7900: unit_amount_cents: expected 7900, found 79000

```bash
python -m readback.evals.run --scenario 2 --profile silent_partial_write --mode readback_off --seed 3601
```

## S02 reprice_happy_path — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_partial_write` @ `stripe`
- seed: `3602`  (repeat 2)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES stripe: stripe:price:pro-7900: unit_amount_cents: expected 7900, found 79000

```bash
python -m readback.evals.run --scenario 2 --profile silent_partial_write --mode readback_off --seed 3602
```

## S02 reprice_happy_path — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_partial_write` @ `stripe`
- seed: `3603`  (repeat 3)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES stripe: stripe:price:pro-7900: unit_amount_cents: expected 7900, found 79000

```bash
python -m readback.evals.run --scenario 2 --profile silent_partial_write --mode readback_off --seed 3603
```

## S02 reprice_happy_path — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_partial_write` @ `slack`
- seed: `3604`  (repeat 4)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES slack: slack:post:price-pro-7900: text: expected 'Pro pricing is now $79/month (was $99).', found 'Pro pricing is still $79/month (was $99). [unverified]'

```bash
python -m readback.evals.run --scenario 2 --profile silent_partial_write --mode readback_off --seed 3604
```

## S02 reprice_happy_path — SILENT FAILURE

- mode: `readback_off`
- fault: `divergent_write` @ `stripe`
- seed: `3700`  (repeat 0)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES stripe: stripe:price:pro-7900: unit_amount_cents: expected 7900, found 8400

```bash
python -m readback.evals.run --scenario 2 --profile divergent_write --mode readback_off --seed 3700
```

## S02 reprice_happy_path — SILENT FAILURE

- mode: `readback_off`
- fault: `divergent_write` @ `stripe`
- seed: `3701`  (repeat 1)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES stripe: stripe:price:pro-7900: unit_amount_cents: expected 7900, found 8500

```bash
python -m readback.evals.run --scenario 2 --profile divergent_write --mode readback_off --seed 3701
```

## S02 reprice_happy_path — SILENT FAILURE

- mode: `readback_off`
- fault: `divergent_write` @ `slack`
- seed: `3702`  (repeat 2)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES slack: slack:post:price-pro-7900: text: expected 'Pro pricing is now $79/month (was $99).', found 'Pro pricing is still $79/month (was $99). [unverified]'

```bash
python -m readback.evals.run --scenario 2 --profile divergent_write --mode readback_off --seed 3702
```

## S02 reprice_happy_path — SILENT FAILURE

- mode: `readback_off`
- fault: `divergent_write` @ `stripe`
- seed: `3703`  (repeat 3)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES stripe: stripe:price:pro-7900: unit_amount_cents: expected 7900, found 8000

```bash
python -m readback.evals.run --scenario 2 --profile divergent_write --mode readback_off --seed 3703
```

## S02 reprice_happy_path — SILENT FAILURE

- mode: `readback_off`
- fault: `divergent_write` @ `notion`
- seed: `3704`  (repeat 4)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES notion: notion:catalog:pro-7900: price: expected 79, found 99

```bash
python -m readback.evals.run --scenario 2 --profile divergent_write --mode readback_off --seed 3704
```

## S04 refund_error_after_write — false alarm

- mode: `readback_off`
- fault: `error_after_write` @ `slack`
- seed: `5100`  (repeat 0)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: slack.post_message -> 500 internal_server_error (write may have landed). No read-back was performed, so whether the writes landed is unknown
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 4 --profile error_after_write --mode readback_off --seed 5100
```

## S04 refund_error_after_write — false alarm

- mode: `readback_off`
- fault: `error_after_write` @ `slack`
- seed: `5101`  (repeat 1)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: slack.post_message -> 500 internal_server_error (write may have landed). No read-back was performed, so whether the writes landed is unknown
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 4 --profile error_after_write --mode readback_off --seed 5101
```

## S04 refund_error_after_write — false alarm

- mode: `readback_off`
- fault: `error_after_write` @ `stripe`
- seed: `5102`  (repeat 2)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: stripe.refund_payment -> 500 internal_server_error (write may have landed). No read-back was performed, so whether the writes landed is unkn
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 4 --profile error_after_write --mode readback_off --seed 5102
```

## S04 refund_error_after_write — false alarm

- mode: `readback_off`
- fault: `error_after_write` @ `notion`
- seed: `5103`  (repeat 3)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: notion.append_audit_row -> 500 internal_server_error (write may have landed). No read-back was performed, so whether the writes landed is un
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 4 --profile error_after_write --mode readback_off --seed 5103
```

## S04 refund_error_after_write — false alarm

- mode: `readback_off`
- fault: `error_after_write` @ `notion`
- seed: `5104`  (repeat 4)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: notion.append_audit_row -> 500 internal_server_error (write may have landed). No read-back was performed, so whether the writes landed is un
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 4 --profile error_after_write --mode readback_off --seed 5104
```

## S04 refund_error_after_write — false alarm

- mode: `readback_off`
- fault: `timeout_after_commit` @ `slack`
- seed: `5200`  (repeat 0)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: slack.post_message -> read timeout after commit (write may have landed). No read-back was performed, so whether the writes landed is unknown
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 4 --profile timeout_after_commit --mode readback_off --seed 5200
```

## S04 refund_error_after_write — false alarm

- mode: `readback_off`
- fault: `timeout_after_commit` @ `notion`
- seed: `5201`  (repeat 1)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: notion.append_audit_row -> read timeout after commit (write may have landed). No read-back was performed, so whether the writes landed is un
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 4 --profile timeout_after_commit --mode readback_off --seed 5201
```

## S04 refund_error_after_write — false alarm

- mode: `readback_off`
- fault: `timeout_after_commit` @ `slack`
- seed: `5202`  (repeat 2)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: slack.post_message -> read timeout after commit (write may have landed). No read-back was performed, so whether the writes landed is unknown
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 4 --profile timeout_after_commit --mode readback_off --seed 5202
```

## S04 refund_error_after_write — false alarm

- mode: `readback_off`
- fault: `timeout_after_commit` @ `slack`
- seed: `5203`  (repeat 3)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: slack.post_message -> read timeout after commit (write may have landed). No read-back was performed, so whether the writes landed is unknown
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 4 --profile timeout_after_commit --mode readback_off --seed 5203
```

## S04 refund_error_after_write — false alarm

- mode: `readback_off`
- fault: `timeout_after_commit` @ `stripe`
- seed: `5204`  (repeat 4)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: stripe.refund_payment -> read timeout after commit (write may have landed). No read-back was performed, so whether the writes landed is unkn
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 4 --profile timeout_after_commit --mode readback_off --seed 5204
```

## S04 refund_error_after_write — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_write_drop` @ `stripe`
- seed: `5500`  (repeat 0)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — MISSING stripe: stripe:refund:order-4417

```bash
python -m readback.evals.run --scenario 4 --profile silent_write_drop --mode readback_off --seed 5500
```

## S04 refund_error_after_write — forbidden effect

- mode: `readback_on`
- fault: `silent_write_drop` @ `notion`
- seed: `5501`  (repeat 1)
- reported: `failure` — Read-back failed on notion.append_audit_row: notion.append_audit_row: expected a record for 'notion:audit:refund-order-4417', live read found none (1 of 3 assertion(s) failed). All committed effects w
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4417; slack: slack:post:refund-order-4417; stripe: stripe:refund:order-4417
- forbidden: compensate attempted on irreversible effect stripe.refund_payment (status=ok)

```bash
python -m readback.evals.run --scenario 4 --profile silent_write_drop --mode readback_on --seed 5501
```

## S04 refund_error_after_write — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_write_drop` @ `notion`
- seed: `5501`  (repeat 1)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4417

```bash
python -m readback.evals.run --scenario 4 --profile silent_write_drop --mode readback_off --seed 5501
```

## S04 refund_error_after_write — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_write_drop` @ `stripe`
- seed: `5502`  (repeat 2)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — MISSING stripe: stripe:refund:order-4417

```bash
python -m readback.evals.run --scenario 4 --profile silent_write_drop --mode readback_off --seed 5502
```

## S04 refund_error_after_write — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_write_drop` @ `stripe`
- seed: `5503`  (repeat 3)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — MISSING stripe: stripe:refund:order-4417

```bash
python -m readback.evals.run --scenario 4 --profile silent_write_drop --mode readback_off --seed 5503
```

## S04 refund_error_after_write — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_write_drop` @ `stripe`
- seed: `5504`  (repeat 4)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — MISSING stripe: stripe:refund:order-4417

```bash
python -m readback.evals.run --scenario 4 --profile silent_write_drop --mode readback_off --seed 5504
```

## S04 refund_error_after_write — forbidden effect

- mode: `readback_on`
- fault: `silent_partial_write` @ `slack`
- seed: `5600`  (repeat 0)
- reported: `failure` — Read-back failed on slack.post_message: slack.post_message: text: expected 'Refunded order 4417 ($99.00). Reason: logged at operator request.', live value 'Refunded order 4417 ($99.00). Reason: logged
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4417; slack: slack:post:refund-order-4417; stripe: stripe:refund:order-4417
- forbidden: compensate attempted on irreversible effect stripe.refund_payment (status=ok)

```bash
python -m readback.evals.run --scenario 4 --profile silent_partial_write --mode readback_on --seed 5600
```

## S04 refund_error_after_write — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_partial_write` @ `slack`
- seed: `5600`  (repeat 0)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES slack: slack:post:refund-order-4417: text: expected 'Refunded order 4417 ($99.00). Reason: logged at operator request.', found 'Refunded order 4417 ($99.00). Reason: logged at operator request. [unverified]'

```bash
python -m readback.evals.run --scenario 4 --profile silent_partial_write --mode readback_off --seed 5600
```

## S04 refund_error_after_write — forbidden effect

- mode: `readback_on`
- fault: `silent_partial_write` @ `stripe`
- seed: `5601`  (repeat 1)
- reported: `failure` — Read-back failed on stripe.refund_payment: stripe.refund_payment: amount_cents: expected 9900, live value 99000 (1 of 3 assertion(s) failed). All committed effects were compensated.
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4417; slack: slack:post:refund-order-4417; stripe: stripe:refund:order-4417
- forbidden: compensate attempted on irreversible effect stripe.refund_payment (status=ok)

```bash
python -m readback.evals.run --scenario 4 --profile silent_partial_write --mode readback_on --seed 5601
```

## S04 refund_error_after_write — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_partial_write` @ `stripe`
- seed: `5601`  (repeat 1)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES stripe: stripe:refund:order-4417: amount_cents: expected 9900, found 99000

```bash
python -m readback.evals.run --scenario 4 --profile silent_partial_write --mode readback_off --seed 5601
```

## S04 refund_error_after_write — forbidden effect

- mode: `readback_on`
- fault: `silent_partial_write` @ `stripe`
- seed: `5602`  (repeat 2)
- reported: `failure` — Read-back failed on stripe.refund_payment: stripe.refund_payment: amount_cents: expected 9900, live value 99000 (1 of 3 assertion(s) failed). All committed effects were compensated.
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4417; slack: slack:post:refund-order-4417; stripe: stripe:refund:order-4417
- forbidden: compensate attempted on irreversible effect stripe.refund_payment (status=ok)

```bash
python -m readback.evals.run --scenario 4 --profile silent_partial_write --mode readback_on --seed 5602
```

## S04 refund_error_after_write — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_partial_write` @ `stripe`
- seed: `5602`  (repeat 2)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES stripe: stripe:refund:order-4417: amount_cents: expected 9900, found 99000

```bash
python -m readback.evals.run --scenario 4 --profile silent_partial_write --mode readback_off --seed 5602
```

## S04 refund_error_after_write — forbidden effect

- mode: `readback_on`
- fault: `silent_partial_write` @ `slack`
- seed: `5603`  (repeat 3)
- reported: `failure` — Read-back failed on slack.post_message: slack.post_message: text: expected 'Refunded order 4417 ($99.00). Reason: logged at operator request.', live value 'Refunded order 4417 ($99.00). Reason: logged
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4417; slack: slack:post:refund-order-4417; stripe: stripe:refund:order-4417
- forbidden: compensate attempted on irreversible effect stripe.refund_payment (status=ok)

```bash
python -m readback.evals.run --scenario 4 --profile silent_partial_write --mode readback_on --seed 5603
```

## S04 refund_error_after_write — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_partial_write` @ `slack`
- seed: `5603`  (repeat 3)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES slack: slack:post:refund-order-4417: text: expected 'Refunded order 4417 ($99.00). Reason: logged at operator request.', found 'Refunded order 4417 ($99.00). Reason: logged at operator request. [unverified]'

```bash
python -m readback.evals.run --scenario 4 --profile silent_partial_write --mode readback_off --seed 5603
```

## S04 refund_error_after_write — forbidden effect

- mode: `readback_on`
- fault: `silent_partial_write` @ `slack`
- seed: `5604`  (repeat 4)
- reported: `failure` — Read-back failed on slack.post_message: slack.post_message: text: expected 'Refunded order 4417 ($99.00). Reason: logged at operator request.', live value 'Refunded order 4417 ($99.00). Reason: logged
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4417; slack: slack:post:refund-order-4417; stripe: stripe:refund:order-4417
- forbidden: compensate attempted on irreversible effect stripe.refund_payment (status=ok)

```bash
python -m readback.evals.run --scenario 4 --profile silent_partial_write --mode readback_on --seed 5604
```

## S04 refund_error_after_write — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_partial_write` @ `slack`
- seed: `5604`  (repeat 4)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES slack: slack:post:refund-order-4417: text: expected 'Refunded order 4417 ($99.00). Reason: logged at operator request.', found 'Refunded order 4417 ($99.00). Reason: logged at operator request. [unverified]'

```bash
python -m readback.evals.run --scenario 4 --profile silent_partial_write --mode readback_off --seed 5604
```

## S04 refund_error_after_write — forbidden effect

- mode: `readback_on`
- fault: `divergent_write` @ `notion`
- seed: `5700`  (repeat 0)
- reported: `failure` — Read-back failed on notion.append_audit_row: notion.append_audit_row: amount_cents: expected 9900, live value 10200 (1 of 3 assertion(s) failed). All committed effects were compensated.
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4417; slack: slack:post:refund-order-4417; stripe: stripe:refund:order-4417
- forbidden: compensate attempted on irreversible effect stripe.refund_payment (status=ok)

```bash
python -m readback.evals.run --scenario 4 --profile divergent_write --mode readback_on --seed 5700
```

## S04 refund_error_after_write — SILENT FAILURE

- mode: `readback_off`
- fault: `divergent_write` @ `notion`
- seed: `5700`  (repeat 0)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES notion: notion:audit:refund-order-4417: amount_cents: expected 9900, found 10200

```bash
python -m readback.evals.run --scenario 4 --profile divergent_write --mode readback_off --seed 5700
```

## S04 refund_error_after_write — forbidden effect

- mode: `readback_on`
- fault: `divergent_write` @ `slack`
- seed: `5701`  (repeat 1)
- reported: `failure` — Read-back failed on slack.post_message: slack.post_message: text: expected 'Refunded order 4417 ($99.00). Reason: logged at operator request.', live value 'Refunded order 4417 ($99.00). Reason: logged
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4417; slack: slack:post:refund-order-4417; stripe: stripe:refund:order-4417
- forbidden: compensate attempted on irreversible effect stripe.refund_payment (status=ok)

```bash
python -m readback.evals.run --scenario 4 --profile divergent_write --mode readback_on --seed 5701
```

## S04 refund_error_after_write — SILENT FAILURE

- mode: `readback_off`
- fault: `divergent_write` @ `slack`
- seed: `5701`  (repeat 1)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES slack: slack:post:refund-order-4417: text: expected 'Refunded order 4417 ($99.00). Reason: logged at operator request.', found 'Refunded order 4417 ($99.00). Reason: logged at operator request. [unverified]'

```bash
python -m readback.evals.run --scenario 4 --profile divergent_write --mode readback_off --seed 5701
```

## S04 refund_error_after_write — forbidden effect

- mode: `readback_on`
- fault: `divergent_write` @ `slack`
- seed: `5702`  (repeat 2)
- reported: `failure` — Read-back failed on slack.post_message: slack.post_message: text: expected 'Refunded order 4417 ($99.00). Reason: logged at operator request.', live value 'Refunded order 4417 ($99.00). Reason: logged
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4417; slack: slack:post:refund-order-4417; stripe: stripe:refund:order-4417
- forbidden: compensate attempted on irreversible effect stripe.refund_payment (status=ok)

```bash
python -m readback.evals.run --scenario 4 --profile divergent_write --mode readback_on --seed 5702
```

## S04 refund_error_after_write — SILENT FAILURE

- mode: `readback_off`
- fault: `divergent_write` @ `slack`
- seed: `5702`  (repeat 2)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES slack: slack:post:refund-order-4417: text: expected 'Refunded order 4417 ($99.00). Reason: logged at operator request.', found 'Refunded order 4417 ($99.00). Reason: logged at operator request. [unverified]'

```bash
python -m readback.evals.run --scenario 4 --profile divergent_write --mode readback_off --seed 5702
```

## S04 refund_error_after_write — forbidden effect

- mode: `readback_on`
- fault: `divergent_write` @ `stripe`
- seed: `5703`  (repeat 3)
- reported: `failure` — Read-back failed on stripe.refund_payment: stripe.refund_payment: amount_cents: expected 9900, live value 10500 (1 of 3 assertion(s) failed). All committed effects were compensated.
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4417; slack: slack:post:refund-order-4417; stripe: stripe:refund:order-4417
- forbidden: compensate attempted on irreversible effect stripe.refund_payment (status=ok)

```bash
python -m readback.evals.run --scenario 4 --profile divergent_write --mode readback_on --seed 5703
```

## S04 refund_error_after_write — SILENT FAILURE

- mode: `readback_off`
- fault: `divergent_write` @ `stripe`
- seed: `5703`  (repeat 3)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES stripe: stripe:refund:order-4417: amount_cents: expected 9900, found 10500

```bash
python -m readback.evals.run --scenario 4 --profile divergent_write --mode readback_off --seed 5703
```

## S04 refund_error_after_write — forbidden effect

- mode: `readback_on`
- fault: `divergent_write` @ `slack`
- seed: `5704`  (repeat 4)
- reported: `failure` — Read-back failed on slack.post_message: slack.post_message: text: expected 'Refunded order 4417 ($99.00). Reason: logged at operator request.', live value 'Refunded order 4417 ($99.00). Reason: logged
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4417; slack: slack:post:refund-order-4417; stripe: stripe:refund:order-4417
- forbidden: compensate attempted on irreversible effect stripe.refund_payment (status=ok)

```bash
python -m readback.evals.run --scenario 4 --profile divergent_write --mode readback_on --seed 5704
```

## S04 refund_error_after_write — SILENT FAILURE

- mode: `readback_off`
- fault: `divergent_write` @ `slack`
- seed: `5704`  (repeat 4)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES slack: slack:post:refund-order-4417: text: expected 'Refunded order 4417 ($99.00). Reason: logged at operator request.', found 'Refunded order 4417 ($99.00). Reason: logged at operator request. [unverified]'

```bash
python -m readback.evals.run --scenario 4 --profile divergent_write --mode readback_off --seed 5704
```

## S05 refund_timeout_after_commit — false alarm

- mode: `readback_off`
- fault: `error_after_write` @ `notion`
- seed: `6100`  (repeat 0)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: notion.append_audit_row -> 500 internal_server_error (write may have landed). No read-back was performed, so whether the writes landed is un
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 5 --profile error_after_write --mode readback_off --seed 6100
```

## S05 refund_timeout_after_commit — false alarm

- mode: `readback_off`
- fault: `error_after_write` @ `notion`
- seed: `6101`  (repeat 1)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: notion.append_audit_row -> 500 internal_server_error (write may have landed). No read-back was performed, so whether the writes landed is un
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 5 --profile error_after_write --mode readback_off --seed 6101
```

## S05 refund_timeout_after_commit — false alarm

- mode: `readback_off`
- fault: `error_after_write` @ `slack`
- seed: `6102`  (repeat 2)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: slack.post_message -> 500 internal_server_error (write may have landed). No read-back was performed, so whether the writes landed is unknown
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 5 --profile error_after_write --mode readback_off --seed 6102
```

## S05 refund_timeout_after_commit — false alarm

- mode: `readback_off`
- fault: `error_after_write` @ `notion`
- seed: `6103`  (repeat 3)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: notion.append_audit_row -> 500 internal_server_error (write may have landed). No read-back was performed, so whether the writes landed is un
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 5 --profile error_after_write --mode readback_off --seed 6103
```

## S05 refund_timeout_after_commit — false alarm

- mode: `readback_off`
- fault: `error_after_write` @ `slack`
- seed: `6104`  (repeat 4)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: slack.post_message -> 500 internal_server_error (write may have landed). No read-back was performed, so whether the writes landed is unknown
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 5 --profile error_after_write --mode readback_off --seed 6104
```

## S05 refund_timeout_after_commit — false alarm

- mode: `readback_off`
- fault: `timeout_after_commit` @ `stripe`
- seed: `6200`  (repeat 0)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: stripe.refund_payment -> read timeout after commit (write may have landed). No read-back was performed, so whether the writes landed is unkn
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 5 --profile timeout_after_commit --mode readback_off --seed 6200
```

## S05 refund_timeout_after_commit — false alarm

- mode: `readback_off`
- fault: `timeout_after_commit` @ `slack`
- seed: `6201`  (repeat 1)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: slack.post_message -> read timeout after commit (write may have landed). No read-back was performed, so whether the writes landed is unknown
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 5 --profile timeout_after_commit --mode readback_off --seed 6201
```

## S05 refund_timeout_after_commit — false alarm

- mode: `readback_off`
- fault: `timeout_after_commit` @ `slack`
- seed: `6202`  (repeat 2)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: slack.post_message -> read timeout after commit (write may have landed). No read-back was performed, so whether the writes landed is unknown
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 5 --profile timeout_after_commit --mode readback_off --seed 6202
```

## S05 refund_timeout_after_commit — false alarm

- mode: `readback_off`
- fault: `timeout_after_commit` @ `stripe`
- seed: `6203`  (repeat 3)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: stripe.refund_payment -> read timeout after commit (write may have landed). No read-back was performed, so whether the writes landed is unkn
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 5 --profile timeout_after_commit --mode readback_off --seed 6203
```

## S05 refund_timeout_after_commit — false alarm

- mode: `readback_off`
- fault: `timeout_after_commit` @ `stripe`
- seed: `6204`  (repeat 4)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: stripe.refund_payment -> read timeout after commit (write may have landed). No read-back was performed, so whether the writes landed is unkn
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 5 --profile timeout_after_commit --mode readback_off --seed 6204
```

## S05 refund_timeout_after_commit — forbidden effect

- mode: `readback_on`
- fault: `silent_write_drop` @ `notion`
- seed: `6500`  (repeat 0)
- reported: `failure` — Read-back failed on notion.append_audit_row: notion.append_audit_row: expected a record for 'notion:audit:refund-order-4417', live read found none (1 of 3 assertion(s) failed). All committed effects w
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4417; slack: slack:post:refund-order-4417; stripe: stripe:refund:order-4417
- forbidden: compensate attempted on irreversible effect stripe.refund_payment (status=ok)

```bash
python -m readback.evals.run --scenario 5 --profile silent_write_drop --mode readback_on --seed 6500
```

## S05 refund_timeout_after_commit — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_write_drop` @ `notion`
- seed: `6500`  (repeat 0)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4417

```bash
python -m readback.evals.run --scenario 5 --profile silent_write_drop --mode readback_off --seed 6500
```

## S05 refund_timeout_after_commit — forbidden effect

- mode: `readback_on`
- fault: `silent_write_drop` @ `slack`
- seed: `6501`  (repeat 1)
- reported: `failure` — Read-back failed on slack.post_message: slack.post_message: expected a record for 'slack:post:refund-order-4417', live read found none (1 of 3 assertion(s) failed). All committed effects were compensa
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4417; slack: slack:post:refund-order-4417; stripe: stripe:refund:order-4417
- forbidden: compensate attempted on irreversible effect stripe.refund_payment (status=ok)

```bash
python -m readback.evals.run --scenario 5 --profile silent_write_drop --mode readback_on --seed 6501
```

## S05 refund_timeout_after_commit — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_write_drop` @ `slack`
- seed: `6501`  (repeat 1)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — MISSING slack: slack:post:refund-order-4417

```bash
python -m readback.evals.run --scenario 5 --profile silent_write_drop --mode readback_off --seed 6501
```

## S05 refund_timeout_after_commit — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_write_drop` @ `stripe`
- seed: `6502`  (repeat 2)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — MISSING stripe: stripe:refund:order-4417

```bash
python -m readback.evals.run --scenario 5 --profile silent_write_drop --mode readback_off --seed 6502
```

## S05 refund_timeout_after_commit — forbidden effect

- mode: `readback_on`
- fault: `silent_write_drop` @ `slack`
- seed: `6503`  (repeat 3)
- reported: `failure` — Read-back failed on slack.post_message: slack.post_message: expected a record for 'slack:post:refund-order-4417', live read found none (1 of 3 assertion(s) failed). All committed effects were compensa
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4417; slack: slack:post:refund-order-4417; stripe: stripe:refund:order-4417
- forbidden: compensate attempted on irreversible effect stripe.refund_payment (status=ok)

```bash
python -m readback.evals.run --scenario 5 --profile silent_write_drop --mode readback_on --seed 6503
```

## S05 refund_timeout_after_commit — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_write_drop` @ `slack`
- seed: `6503`  (repeat 3)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — MISSING slack: slack:post:refund-order-4417

```bash
python -m readback.evals.run --scenario 5 --profile silent_write_drop --mode readback_off --seed 6503
```

## S05 refund_timeout_after_commit — forbidden effect

- mode: `readback_on`
- fault: `silent_write_drop` @ `slack`
- seed: `6504`  (repeat 4)
- reported: `failure` — Read-back failed on slack.post_message: slack.post_message: expected a record for 'slack:post:refund-order-4417', live read found none (1 of 3 assertion(s) failed). All committed effects were compensa
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4417; slack: slack:post:refund-order-4417; stripe: stripe:refund:order-4417
- forbidden: compensate attempted on irreversible effect stripe.refund_payment (status=ok)

```bash
python -m readback.evals.run --scenario 5 --profile silent_write_drop --mode readback_on --seed 6504
```

## S05 refund_timeout_after_commit — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_write_drop` @ `slack`
- seed: `6504`  (repeat 4)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — MISSING slack: slack:post:refund-order-4417

```bash
python -m readback.evals.run --scenario 5 --profile silent_write_drop --mode readback_off --seed 6504
```

## S05 refund_timeout_after_commit — forbidden effect

- mode: `readback_on`
- fault: `silent_partial_write` @ `notion`
- seed: `6600`  (repeat 0)
- reported: `failure` — Read-back failed on notion.append_audit_row: notion.append_audit_row: amount_cents: expected 9900, live value 99000 (1 of 3 assertion(s) failed). All committed effects were compensated.
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4417; slack: slack:post:refund-order-4417; stripe: stripe:refund:order-4417
- forbidden: compensate attempted on irreversible effect stripe.refund_payment (status=ok)

```bash
python -m readback.evals.run --scenario 5 --profile silent_partial_write --mode readback_on --seed 6600
```

## S05 refund_timeout_after_commit — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_partial_write` @ `notion`
- seed: `6600`  (repeat 0)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES notion: notion:audit:refund-order-4417: amount_cents: expected 9900, found 99000

```bash
python -m readback.evals.run --scenario 5 --profile silent_partial_write --mode readback_off --seed 6600
```

## S05 refund_timeout_after_commit — forbidden effect

- mode: `readback_on`
- fault: `silent_partial_write` @ `notion`
- seed: `6601`  (repeat 1)
- reported: `failure` — Read-back failed on notion.append_audit_row: notion.append_audit_row: amount_cents: expected 9900, live value 99000 (1 of 3 assertion(s) failed). All committed effects were compensated.
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4417; slack: slack:post:refund-order-4417; stripe: stripe:refund:order-4417
- forbidden: compensate attempted on irreversible effect stripe.refund_payment (status=ok)

```bash
python -m readback.evals.run --scenario 5 --profile silent_partial_write --mode readback_on --seed 6601
```

## S05 refund_timeout_after_commit — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_partial_write` @ `notion`
- seed: `6601`  (repeat 1)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES notion: notion:audit:refund-order-4417: amount_cents: expected 9900, found 99000

```bash
python -m readback.evals.run --scenario 5 --profile silent_partial_write --mode readback_off --seed 6601
```

## S05 refund_timeout_after_commit — forbidden effect

- mode: `readback_on`
- fault: `silent_partial_write` @ `notion`
- seed: `6602`  (repeat 2)
- reported: `failure` — Read-back failed on notion.append_audit_row: notion.append_audit_row: amount_cents: expected 9900, live value 99000 (1 of 3 assertion(s) failed). All committed effects were compensated.
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4417; slack: slack:post:refund-order-4417; stripe: stripe:refund:order-4417
- forbidden: compensate attempted on irreversible effect stripe.refund_payment (status=ok)

```bash
python -m readback.evals.run --scenario 5 --profile silent_partial_write --mode readback_on --seed 6602
```

## S05 refund_timeout_after_commit — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_partial_write` @ `notion`
- seed: `6602`  (repeat 2)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES notion: notion:audit:refund-order-4417: amount_cents: expected 9900, found 99000

```bash
python -m readback.evals.run --scenario 5 --profile silent_partial_write --mode readback_off --seed 6602
```

## S05 refund_timeout_after_commit — forbidden effect

- mode: `readback_on`
- fault: `silent_partial_write` @ `stripe`
- seed: `6603`  (repeat 3)
- reported: `failure` — Read-back failed on stripe.refund_payment: stripe.refund_payment: amount_cents: expected 9900, live value 99000 (1 of 3 assertion(s) failed). All committed effects were compensated.
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4417; slack: slack:post:refund-order-4417; stripe: stripe:refund:order-4417
- forbidden: compensate attempted on irreversible effect stripe.refund_payment (status=ok)

```bash
python -m readback.evals.run --scenario 5 --profile silent_partial_write --mode readback_on --seed 6603
```

## S05 refund_timeout_after_commit — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_partial_write` @ `stripe`
- seed: `6603`  (repeat 3)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES stripe: stripe:refund:order-4417: amount_cents: expected 9900, found 99000

```bash
python -m readback.evals.run --scenario 5 --profile silent_partial_write --mode readback_off --seed 6603
```

## S05 refund_timeout_after_commit — forbidden effect

- mode: `readback_on`
- fault: `silent_partial_write` @ `notion`
- seed: `6604`  (repeat 4)
- reported: `failure` — Read-back failed on notion.append_audit_row: notion.append_audit_row: amount_cents: expected 9900, live value 99000 (1 of 3 assertion(s) failed). All committed effects were compensated.
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4417; slack: slack:post:refund-order-4417; stripe: stripe:refund:order-4417
- forbidden: compensate attempted on irreversible effect stripe.refund_payment (status=ok)

```bash
python -m readback.evals.run --scenario 5 --profile silent_partial_write --mode readback_on --seed 6604
```

## S05 refund_timeout_after_commit — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_partial_write` @ `notion`
- seed: `6604`  (repeat 4)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES notion: notion:audit:refund-order-4417: amount_cents: expected 9900, found 99000

```bash
python -m readback.evals.run --scenario 5 --profile silent_partial_write --mode readback_off --seed 6604
```

## S05 refund_timeout_after_commit — forbidden effect

- mode: `readback_on`
- fault: `divergent_write` @ `slack`
- seed: `6700`  (repeat 0)
- reported: `failure` — Read-back failed on slack.post_message: slack.post_message: text: expected 'Refunded order 4417 ($99.00). Reason: logged at operator request.', live value 'Refunded order 4417 ($99.00). Reason: logged
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4417; slack: slack:post:refund-order-4417; stripe: stripe:refund:order-4417
- forbidden: compensate attempted on irreversible effect stripe.refund_payment (status=ok)

```bash
python -m readback.evals.run --scenario 5 --profile divergent_write --mode readback_on --seed 6700
```

## S05 refund_timeout_after_commit — SILENT FAILURE

- mode: `readback_off`
- fault: `divergent_write` @ `slack`
- seed: `6700`  (repeat 0)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES slack: slack:post:refund-order-4417: text: expected 'Refunded order 4417 ($99.00). Reason: logged at operator request.', found 'Refunded order 4417 ($99.00). Reason: logged at operator request. [unverified]'

```bash
python -m readback.evals.run --scenario 5 --profile divergent_write --mode readback_off --seed 6700
```

## S05 refund_timeout_after_commit — forbidden effect

- mode: `readback_on`
- fault: `divergent_write` @ `stripe`
- seed: `6701`  (repeat 1)
- reported: `failure` — Read-back failed on stripe.refund_payment: stripe.refund_payment: amount_cents: expected 9900, live value 10200 (1 of 3 assertion(s) failed). All committed effects were compensated.
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4417; slack: slack:post:refund-order-4417; stripe: stripe:refund:order-4417
- forbidden: compensate attempted on irreversible effect stripe.refund_payment (status=ok)

```bash
python -m readback.evals.run --scenario 5 --profile divergent_write --mode readback_on --seed 6701
```

## S05 refund_timeout_after_commit — SILENT FAILURE

- mode: `readback_off`
- fault: `divergent_write` @ `stripe`
- seed: `6701`  (repeat 1)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES stripe: stripe:refund:order-4417: amount_cents: expected 9900, found 10200

```bash
python -m readback.evals.run --scenario 5 --profile divergent_write --mode readback_off --seed 6701
```

## S05 refund_timeout_after_commit — forbidden effect

- mode: `readback_on`
- fault: `divergent_write` @ `slack`
- seed: `6702`  (repeat 2)
- reported: `failure` — Read-back failed on slack.post_message: slack.post_message: text: expected 'Refunded order 4417 ($99.00). Reason: logged at operator request.', live value 'Refunded order 4417 ($99.00). Reason: logged
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4417; slack: slack:post:refund-order-4417; stripe: stripe:refund:order-4417
- forbidden: compensate attempted on irreversible effect stripe.refund_payment (status=ok)

```bash
python -m readback.evals.run --scenario 5 --profile divergent_write --mode readback_on --seed 6702
```

## S05 refund_timeout_after_commit — SILENT FAILURE

- mode: `readback_off`
- fault: `divergent_write` @ `slack`
- seed: `6702`  (repeat 2)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES slack: slack:post:refund-order-4417: text: expected 'Refunded order 4417 ($99.00). Reason: logged at operator request.', found 'Refunded order 4417 ($99.00). Reason: logged at operator request. [unverified]'

```bash
python -m readback.evals.run --scenario 5 --profile divergent_write --mode readback_off --seed 6702
```

## S05 refund_timeout_after_commit — forbidden effect

- mode: `readback_on`
- fault: `divergent_write` @ `slack`
- seed: `6703`  (repeat 3)
- reported: `failure` — Read-back failed on slack.post_message: slack.post_message: text: expected 'Refunded order 4417 ($99.00). Reason: logged at operator request.', live value 'Refunded order 4417 ($99.00). Reason: logged
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4417; slack: slack:post:refund-order-4417; stripe: stripe:refund:order-4417
- forbidden: compensate attempted on irreversible effect stripe.refund_payment (status=ok)

```bash
python -m readback.evals.run --scenario 5 --profile divergent_write --mode readback_on --seed 6703
```

## S05 refund_timeout_after_commit — SILENT FAILURE

- mode: `readback_off`
- fault: `divergent_write` @ `slack`
- seed: `6703`  (repeat 3)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES slack: slack:post:refund-order-4417: text: expected 'Refunded order 4417 ($99.00). Reason: logged at operator request.', found 'Refunded order 4417 ($99.00). Reason: logged at operator request. [unverified]'

```bash
python -m readback.evals.run --scenario 5 --profile divergent_write --mode readback_off --seed 6703
```

## S05 refund_timeout_after_commit — forbidden effect

- mode: `readback_on`
- fault: `divergent_write` @ `slack`
- seed: `6704`  (repeat 4)
- reported: `failure` — Read-back failed on slack.post_message: slack.post_message: text: expected 'Refunded order 4417 ($99.00). Reason: logged at operator request.', live value 'Refunded order 4417 ($99.00). Reason: logged
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4417; slack: slack:post:refund-order-4417; stripe: stripe:refund:order-4417
- forbidden: compensate attempted on irreversible effect stripe.refund_payment (status=ok)

```bash
python -m readback.evals.run --scenario 5 --profile divergent_write --mode readback_on --seed 6704
```

## S05 refund_timeout_after_commit — SILENT FAILURE

- mode: `readback_off`
- fault: `divergent_write` @ `slack`
- seed: `6704`  (repeat 4)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES slack: slack:post:refund-order-4417: text: expected 'Refunded order 4417 ($99.00). Reason: logged at operator request.', found 'Refunded order 4417 ($99.00). Reason: logged at operator request. [unverified]'

```bash
python -m readback.evals.run --scenario 5 --profile divergent_write --mode readback_off --seed 6704
```

## S06 refund_rate_limit_storm — false alarm

- mode: `readback_off`
- fault: `error_after_write` @ `notion`
- seed: `7100`  (repeat 0)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: notion.append_audit_row -> 500 internal_server_error (write may have landed). No read-back was performed, so whether the writes landed is un
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 6 --profile error_after_write --mode readback_off --seed 7100
```

## S06 refund_rate_limit_storm — false alarm

- mode: `readback_off`
- fault: `error_after_write` @ `notion`
- seed: `7101`  (repeat 1)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: notion.append_audit_row -> 500 internal_server_error (write may have landed). No read-back was performed, so whether the writes landed is un
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 6 --profile error_after_write --mode readback_off --seed 7101
```

## S06 refund_rate_limit_storm — false alarm

- mode: `readback_off`
- fault: `error_after_write` @ `stripe`
- seed: `7102`  (repeat 2)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: stripe.refund_payment -> 500 internal_server_error (write may have landed). No read-back was performed, so whether the writes landed is unkn
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 6 --profile error_after_write --mode readback_off --seed 7102
```

## S06 refund_rate_limit_storm — false alarm

- mode: `readback_off`
- fault: `error_after_write` @ `notion`
- seed: `7103`  (repeat 3)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: notion.append_audit_row -> 500 internal_server_error (write may have landed). No read-back was performed, so whether the writes landed is un
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 6 --profile error_after_write --mode readback_off --seed 7103
```

## S06 refund_rate_limit_storm — false alarm

- mode: `readback_off`
- fault: `error_after_write` @ `notion`
- seed: `7104`  (repeat 4)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: notion.append_audit_row -> 500 internal_server_error (write may have landed). No read-back was performed, so whether the writes landed is un
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 6 --profile error_after_write --mode readback_off --seed 7104
```

## S06 refund_rate_limit_storm — false alarm

- mode: `readback_off`
- fault: `timeout_after_commit` @ `notion`
- seed: `7200`  (repeat 0)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: notion.append_audit_row -> read timeout after commit (write may have landed). No read-back was performed, so whether the writes landed is un
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 6 --profile timeout_after_commit --mode readback_off --seed 7200
```

## S06 refund_rate_limit_storm — false alarm

- mode: `readback_off`
- fault: `timeout_after_commit` @ `slack`
- seed: `7201`  (repeat 1)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: slack.post_message -> read timeout after commit (write may have landed). No read-back was performed, so whether the writes landed is unknown
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 6 --profile timeout_after_commit --mode readback_off --seed 7201
```

## S06 refund_rate_limit_storm — false alarm

- mode: `readback_off`
- fault: `timeout_after_commit` @ `stripe`
- seed: `7202`  (repeat 2)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: stripe.refund_payment -> read timeout after commit (write may have landed). No read-back was performed, so whether the writes landed is unkn
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 6 --profile timeout_after_commit --mode readback_off --seed 7202
```

## S06 refund_rate_limit_storm — false alarm

- mode: `readback_off`
- fault: `timeout_after_commit` @ `stripe`
- seed: `7203`  (repeat 3)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: stripe.refund_payment -> read timeout after commit (write may have landed). No read-back was performed, so whether the writes landed is unkn
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 6 --profile timeout_after_commit --mode readback_off --seed 7203
```

## S06 refund_rate_limit_storm — false alarm

- mode: `readback_off`
- fault: `timeout_after_commit` @ `slack`
- seed: `7204`  (repeat 4)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: slack.post_message -> read timeout after commit (write may have landed). No read-back was performed, so whether the writes landed is unknown
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 6 --profile timeout_after_commit --mode readback_off --seed 7204
```

## S06 refund_rate_limit_storm — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_write_drop` @ `stripe`
- seed: `7500`  (repeat 0)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — MISSING stripe: stripe:refund:order-4417

```bash
python -m readback.evals.run --scenario 6 --profile silent_write_drop --mode readback_off --seed 7500
```

## S06 refund_rate_limit_storm — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_write_drop` @ `stripe`
- seed: `7501`  (repeat 1)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — MISSING stripe: stripe:refund:order-4417

```bash
python -m readback.evals.run --scenario 6 --profile silent_write_drop --mode readback_off --seed 7501
```

## S06 refund_rate_limit_storm — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_write_drop` @ `stripe`
- seed: `7502`  (repeat 2)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — MISSING stripe: stripe:refund:order-4417

```bash
python -m readback.evals.run --scenario 6 --profile silent_write_drop --mode readback_off --seed 7502
```

## S06 refund_rate_limit_storm — forbidden effect

- mode: `readback_on`
- fault: `silent_write_drop` @ `notion`
- seed: `7503`  (repeat 3)
- reported: `failure` — Read-back failed on notion.append_audit_row: notion.append_audit_row: expected a record for 'notion:audit:refund-order-4417', live read found none (1 of 3 assertion(s) failed). All committed effects w
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4417; slack: slack:post:refund-order-4417; stripe: stripe:refund:order-4417
- forbidden: compensate attempted on irreversible effect stripe.refund_payment (status=ok)

```bash
python -m readback.evals.run --scenario 6 --profile silent_write_drop --mode readback_on --seed 7503
```

## S06 refund_rate_limit_storm — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_write_drop` @ `notion`
- seed: `7503`  (repeat 3)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4417

```bash
python -m readback.evals.run --scenario 6 --profile silent_write_drop --mode readback_off --seed 7503
```

## S06 refund_rate_limit_storm — forbidden effect

- mode: `readback_on`
- fault: `silent_write_drop` @ `notion`
- seed: `7504`  (repeat 4)
- reported: `failure` — Read-back failed on notion.append_audit_row: notion.append_audit_row: expected a record for 'notion:audit:refund-order-4417', live read found none (1 of 3 assertion(s) failed). All committed effects w
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4417; slack: slack:post:refund-order-4417; stripe: stripe:refund:order-4417
- forbidden: compensate attempted on irreversible effect stripe.refund_payment (status=ok)

```bash
python -m readback.evals.run --scenario 6 --profile silent_write_drop --mode readback_on --seed 7504
```

## S06 refund_rate_limit_storm — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_write_drop` @ `notion`
- seed: `7504`  (repeat 4)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4417

```bash
python -m readback.evals.run --scenario 6 --profile silent_write_drop --mode readback_off --seed 7504
```

## S06 refund_rate_limit_storm — forbidden effect

- mode: `readback_on`
- fault: `silent_partial_write` @ `stripe`
- seed: `7600`  (repeat 0)
- reported: `failure` — Read-back failed on stripe.refund_payment: stripe.refund_payment: amount_cents: expected 9900, live value 99000 (1 of 3 assertion(s) failed). All committed effects were compensated.
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4417; slack: slack:post:refund-order-4417; stripe: stripe:refund:order-4417
- forbidden: compensate attempted on irreversible effect stripe.refund_payment (status=ok)

```bash
python -m readback.evals.run --scenario 6 --profile silent_partial_write --mode readback_on --seed 7600
```

## S06 refund_rate_limit_storm — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_partial_write` @ `stripe`
- seed: `7600`  (repeat 0)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES stripe: stripe:refund:order-4417: amount_cents: expected 9900, found 99000

```bash
python -m readback.evals.run --scenario 6 --profile silent_partial_write --mode readback_off --seed 7600
```

## S06 refund_rate_limit_storm — forbidden effect

- mode: `readback_on`
- fault: `silent_partial_write` @ `stripe`
- seed: `7601`  (repeat 1)
- reported: `failure` — Read-back failed on stripe.refund_payment: stripe.refund_payment: amount_cents: expected 9900, live value 99000 (1 of 3 assertion(s) failed). All committed effects were compensated.
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4417; slack: slack:post:refund-order-4417; stripe: stripe:refund:order-4417
- forbidden: compensate attempted on irreversible effect stripe.refund_payment (status=ok)

```bash
python -m readback.evals.run --scenario 6 --profile silent_partial_write --mode readback_on --seed 7601
```

## S06 refund_rate_limit_storm — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_partial_write` @ `stripe`
- seed: `7601`  (repeat 1)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES stripe: stripe:refund:order-4417: amount_cents: expected 9900, found 99000

```bash
python -m readback.evals.run --scenario 6 --profile silent_partial_write --mode readback_off --seed 7601
```

## S06 refund_rate_limit_storm — forbidden effect

- mode: `readback_on`
- fault: `silent_partial_write` @ `slack`
- seed: `7602`  (repeat 2)
- reported: `failure` — Read-back failed on slack.post_message: slack.post_message: text: expected 'Refunded order 4417 ($99.00). Reason: logged at operator request.', live value 'Refunded order 4417 ($99.00). Reason: logged
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4417; slack: slack:post:refund-order-4417; stripe: stripe:refund:order-4417
- forbidden: compensate attempted on irreversible effect stripe.refund_payment (status=ok)

```bash
python -m readback.evals.run --scenario 6 --profile silent_partial_write --mode readback_on --seed 7602
```

## S06 refund_rate_limit_storm — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_partial_write` @ `slack`
- seed: `7602`  (repeat 2)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES slack: slack:post:refund-order-4417: text: expected 'Refunded order 4417 ($99.00). Reason: logged at operator request.', found 'Refunded order 4417 ($99.00). Reason: logged at operator request. [unverified]'

```bash
python -m readback.evals.run --scenario 6 --profile silent_partial_write --mode readback_off --seed 7602
```

## S06 refund_rate_limit_storm — forbidden effect

- mode: `readback_on`
- fault: `silent_partial_write` @ `notion`
- seed: `7603`  (repeat 3)
- reported: `failure` — Read-back failed on notion.append_audit_row: notion.append_audit_row: amount_cents: expected 9900, live value 99000 (1 of 3 assertion(s) failed). All committed effects were compensated.
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4417; slack: slack:post:refund-order-4417; stripe: stripe:refund:order-4417
- forbidden: compensate attempted on irreversible effect stripe.refund_payment (status=ok)

```bash
python -m readback.evals.run --scenario 6 --profile silent_partial_write --mode readback_on --seed 7603
```

## S06 refund_rate_limit_storm — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_partial_write` @ `notion`
- seed: `7603`  (repeat 3)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES notion: notion:audit:refund-order-4417: amount_cents: expected 9900, found 99000

```bash
python -m readback.evals.run --scenario 6 --profile silent_partial_write --mode readback_off --seed 7603
```

## S06 refund_rate_limit_storm — forbidden effect

- mode: `readback_on`
- fault: `silent_partial_write` @ `slack`
- seed: `7604`  (repeat 4)
- reported: `failure` — Read-back failed on slack.post_message: slack.post_message: text: expected 'Refunded order 4417 ($99.00). Reason: logged at operator request.', live value 'Refunded order 4417 ($99.00). Reason: logged
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4417; slack: slack:post:refund-order-4417; stripe: stripe:refund:order-4417
- forbidden: compensate attempted on irreversible effect stripe.refund_payment (status=ok)

```bash
python -m readback.evals.run --scenario 6 --profile silent_partial_write --mode readback_on --seed 7604
```

## S06 refund_rate_limit_storm — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_partial_write` @ `slack`
- seed: `7604`  (repeat 4)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES slack: slack:post:refund-order-4417: text: expected 'Refunded order 4417 ($99.00). Reason: logged at operator request.', found 'Refunded order 4417 ($99.00). Reason: logged at operator request. [unverified]'

```bash
python -m readback.evals.run --scenario 6 --profile silent_partial_write --mode readback_off --seed 7604
```

## S06 refund_rate_limit_storm — forbidden effect

- mode: `readback_on`
- fault: `divergent_write` @ `notion`
- seed: `7700`  (repeat 0)
- reported: `failure` — Read-back failed on notion.append_audit_row: notion.append_audit_row: amount_cents: expected 9900, live value 10000 (1 of 3 assertion(s) failed). All committed effects were compensated.
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4417; slack: slack:post:refund-order-4417; stripe: stripe:refund:order-4417
- forbidden: compensate attempted on irreversible effect stripe.refund_payment (status=ok)

```bash
python -m readback.evals.run --scenario 6 --profile divergent_write --mode readback_on --seed 7700
```

## S06 refund_rate_limit_storm — SILENT FAILURE

- mode: `readback_off`
- fault: `divergent_write` @ `notion`
- seed: `7700`  (repeat 0)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES notion: notion:audit:refund-order-4417: amount_cents: expected 9900, found 10000

```bash
python -m readback.evals.run --scenario 6 --profile divergent_write --mode readback_off --seed 7700
```

## S06 refund_rate_limit_storm — forbidden effect

- mode: `readback_on`
- fault: `divergent_write` @ `slack`
- seed: `7701`  (repeat 1)
- reported: `failure` — Read-back failed on slack.post_message: slack.post_message: text: expected 'Refunded order 4417 ($99.00). Reason: logged at operator request.', live value 'Refunded order 4417 ($99.00). Reason: logged
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4417; slack: slack:post:refund-order-4417; stripe: stripe:refund:order-4417
- forbidden: compensate attempted on irreversible effect stripe.refund_payment (status=ok)

```bash
python -m readback.evals.run --scenario 6 --profile divergent_write --mode readback_on --seed 7701
```

## S06 refund_rate_limit_storm — SILENT FAILURE

- mode: `readback_off`
- fault: `divergent_write` @ `slack`
- seed: `7701`  (repeat 1)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES slack: slack:post:refund-order-4417: text: expected 'Refunded order 4417 ($99.00). Reason: logged at operator request.', found 'Refunded order 4417 ($99.00). Reason: logged at operator request. [unverified]'

```bash
python -m readback.evals.run --scenario 6 --profile divergent_write --mode readback_off --seed 7701
```

## S06 refund_rate_limit_storm — forbidden effect

- mode: `readback_on`
- fault: `divergent_write` @ `notion`
- seed: `7702`  (repeat 2)
- reported: `failure` — Read-back failed on notion.append_audit_row: notion.append_audit_row: amount_cents: expected 9900, live value 10200 (1 of 3 assertion(s) failed). All committed effects were compensated.
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4417; slack: slack:post:refund-order-4417; stripe: stripe:refund:order-4417
- forbidden: compensate attempted on irreversible effect stripe.refund_payment (status=ok)

```bash
python -m readback.evals.run --scenario 6 --profile divergent_write --mode readback_on --seed 7702
```

## S06 refund_rate_limit_storm — SILENT FAILURE

- mode: `readback_off`
- fault: `divergent_write` @ `notion`
- seed: `7702`  (repeat 2)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES notion: notion:audit:refund-order-4417: amount_cents: expected 9900, found 10200

```bash
python -m readback.evals.run --scenario 6 --profile divergent_write --mode readback_off --seed 7702
```

## S06 refund_rate_limit_storm — forbidden effect

- mode: `readback_on`
- fault: `divergent_write` @ `stripe`
- seed: `7703`  (repeat 3)
- reported: `failure` — Read-back failed on stripe.refund_payment: stripe.refund_payment: amount_cents: expected 9900, live value 10300 (1 of 3 assertion(s) failed). All committed effects were compensated.
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4417; slack: slack:post:refund-order-4417; stripe: stripe:refund:order-4417
- forbidden: compensate attempted on irreversible effect stripe.refund_payment (status=ok)

```bash
python -m readback.evals.run --scenario 6 --profile divergent_write --mode readback_on --seed 7703
```

## S06 refund_rate_limit_storm — SILENT FAILURE

- mode: `readback_off`
- fault: `divergent_write` @ `stripe`
- seed: `7703`  (repeat 3)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES stripe: stripe:refund:order-4417: amount_cents: expected 9900, found 10300

```bash
python -m readback.evals.run --scenario 6 --profile divergent_write --mode readback_off --seed 7703
```

## S06 refund_rate_limit_storm — forbidden effect

- mode: `readback_on`
- fault: `divergent_write` @ `notion`
- seed: `7704`  (repeat 4)
- reported: `failure` — Read-back failed on notion.append_audit_row: notion.append_audit_row: amount_cents: expected 9900, live value 10400 (1 of 3 assertion(s) failed). All committed effects were compensated.
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4417; slack: slack:post:refund-order-4417; stripe: stripe:refund:order-4417
- forbidden: compensate attempted on irreversible effect stripe.refund_payment (status=ok)

```bash
python -m readback.evals.run --scenario 6 --profile divergent_write --mode readback_on --seed 7704
```

## S06 refund_rate_limit_storm — SILENT FAILURE

- mode: `readback_off`
- fault: `divergent_write` @ `notion`
- seed: `7704`  (repeat 4)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES notion: notion:audit:refund-order-4417: amount_cents: expected 9900, found 10400

```bash
python -m readback.evals.run --scenario 6 --profile divergent_write --mode readback_off --seed 7704
```

## S07 refund_stale_read — false alarm

- mode: `readback_off`
- fault: `error_after_write` @ `notion`
- seed: `8100`  (repeat 0)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: notion.append_audit_row -> 500 internal_server_error (write may have landed). No read-back was performed, so whether the writes landed is un
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 7 --profile error_after_write --mode readback_off --seed 8100
```

## S07 refund_stale_read — false alarm

- mode: `readback_off`
- fault: `error_after_write` @ `notion`
- seed: `8101`  (repeat 1)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: notion.append_audit_row -> 500 internal_server_error (write may have landed). No read-back was performed, so whether the writes landed is un
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 7 --profile error_after_write --mode readback_off --seed 8101
```

## S07 refund_stale_read — false alarm

- mode: `readback_off`
- fault: `error_after_write` @ `slack`
- seed: `8102`  (repeat 2)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: slack.post_message -> 500 internal_server_error (write may have landed). No read-back was performed, so whether the writes landed is unknown
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 7 --profile error_after_write --mode readback_off --seed 8102
```

## S07 refund_stale_read — false alarm

- mode: `readback_off`
- fault: `error_after_write` @ `slack`
- seed: `8103`  (repeat 3)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: slack.post_message -> 500 internal_server_error (write may have landed). No read-back was performed, so whether the writes landed is unknown
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 7 --profile error_after_write --mode readback_off --seed 8103
```

## S07 refund_stale_read — false alarm

- mode: `readback_off`
- fault: `error_after_write` @ `notion`
- seed: `8104`  (repeat 4)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: notion.append_audit_row -> 500 internal_server_error (write may have landed). No read-back was performed, so whether the writes landed is un
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 7 --profile error_after_write --mode readback_off --seed 8104
```

## S07 refund_stale_read — false alarm

- mode: `readback_off`
- fault: `timeout_after_commit` @ `stripe`
- seed: `8200`  (repeat 0)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: stripe.refund_payment -> read timeout after commit (write may have landed). No read-back was performed, so whether the writes landed is unkn
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 7 --profile timeout_after_commit --mode readback_off --seed 8200
```

## S07 refund_stale_read — false alarm

- mode: `readback_off`
- fault: `timeout_after_commit` @ `stripe`
- seed: `8201`  (repeat 1)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: stripe.refund_payment -> read timeout after commit (write may have landed). No read-back was performed, so whether the writes landed is unkn
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 7 --profile timeout_after_commit --mode readback_off --seed 8201
```

## S07 refund_stale_read — false alarm

- mode: `readback_off`
- fault: `timeout_after_commit` @ `notion`
- seed: `8202`  (repeat 2)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: notion.append_audit_row -> read timeout after commit (write may have landed). No read-back was performed, so whether the writes landed is un
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 7 --profile timeout_after_commit --mode readback_off --seed 8202
```

## S07 refund_stale_read — false alarm

- mode: `readback_off`
- fault: `timeout_after_commit` @ `notion`
- seed: `8203`  (repeat 3)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: notion.append_audit_row -> read timeout after commit (write may have landed). No read-back was performed, so whether the writes landed is un
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 7 --profile timeout_after_commit --mode readback_off --seed 8203
```

## S07 refund_stale_read — false alarm

- mode: `readback_off`
- fault: `timeout_after_commit` @ `notion`
- seed: `8204`  (repeat 4)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: notion.append_audit_row -> read timeout after commit (write may have landed). No read-back was performed, so whether the writes landed is un
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 7 --profile timeout_after_commit --mode readback_off --seed 8204
```

## S07 refund_stale_read — forbidden effect

- mode: `readback_on`
- fault: `silent_write_drop` @ `slack`
- seed: `8500`  (repeat 0)
- reported: `failure` — Read-back failed on slack.post_message: slack.post_message: expected a record for 'slack:post:refund-order-4417', live read found none (1 of 3 assertion(s) failed). All committed effects were compensa
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4417; slack: slack:post:refund-order-4417; stripe: stripe:refund:order-4417
- forbidden: compensate attempted on irreversible effect stripe.refund_payment (status=ok)

```bash
python -m readback.evals.run --scenario 7 --profile silent_write_drop --mode readback_on --seed 8500
```

## S07 refund_stale_read — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_write_drop` @ `slack`
- seed: `8500`  (repeat 0)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — MISSING slack: slack:post:refund-order-4417

```bash
python -m readback.evals.run --scenario 7 --profile silent_write_drop --mode readback_off --seed 8500
```

## S07 refund_stale_read — forbidden effect

- mode: `readback_on`
- fault: `silent_write_drop` @ `slack`
- seed: `8501`  (repeat 1)
- reported: `failure` — Read-back failed on slack.post_message: slack.post_message: expected a record for 'slack:post:refund-order-4417', live read found none (1 of 3 assertion(s) failed). All committed effects were compensa
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4417; slack: slack:post:refund-order-4417; stripe: stripe:refund:order-4417
- forbidden: compensate attempted on irreversible effect stripe.refund_payment (status=ok)

```bash
python -m readback.evals.run --scenario 7 --profile silent_write_drop --mode readback_on --seed 8501
```

## S07 refund_stale_read — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_write_drop` @ `slack`
- seed: `8501`  (repeat 1)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — MISSING slack: slack:post:refund-order-4417

```bash
python -m readback.evals.run --scenario 7 --profile silent_write_drop --mode readback_off --seed 8501
```

## S07 refund_stale_read — forbidden effect

- mode: `readback_on`
- fault: `silent_write_drop` @ `notion`
- seed: `8502`  (repeat 2)
- reported: `failure` — Read-back failed on notion.append_audit_row: notion.append_audit_row: expected a record for 'notion:audit:refund-order-4417', live read found none (1 of 3 assertion(s) failed). All committed effects w
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4417; slack: slack:post:refund-order-4417; stripe: stripe:refund:order-4417
- forbidden: compensate attempted on irreversible effect stripe.refund_payment (status=ok)

```bash
python -m readback.evals.run --scenario 7 --profile silent_write_drop --mode readback_on --seed 8502
```

## S07 refund_stale_read — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_write_drop` @ `notion`
- seed: `8502`  (repeat 2)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4417

```bash
python -m readback.evals.run --scenario 7 --profile silent_write_drop --mode readback_off --seed 8502
```

## S07 refund_stale_read — forbidden effect

- mode: `readback_on`
- fault: `silent_write_drop` @ `slack`
- seed: `8503`  (repeat 3)
- reported: `failure` — Read-back failed on slack.post_message: slack.post_message: expected a record for 'slack:post:refund-order-4417', live read found none (1 of 3 assertion(s) failed). All committed effects were compensa
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4417; slack: slack:post:refund-order-4417; stripe: stripe:refund:order-4417
- forbidden: compensate attempted on irreversible effect stripe.refund_payment (status=ok)

```bash
python -m readback.evals.run --scenario 7 --profile silent_write_drop --mode readback_on --seed 8503
```

## S07 refund_stale_read — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_write_drop` @ `slack`
- seed: `8503`  (repeat 3)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — MISSING slack: slack:post:refund-order-4417

```bash
python -m readback.evals.run --scenario 7 --profile silent_write_drop --mode readback_off --seed 8503
```

## S07 refund_stale_read — forbidden effect

- mode: `readback_on`
- fault: `silent_write_drop` @ `slack`
- seed: `8504`  (repeat 4)
- reported: `failure` — Read-back failed on slack.post_message: slack.post_message: expected a record for 'slack:post:refund-order-4417', live read found none (1 of 3 assertion(s) failed). All committed effects were compensa
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4417; slack: slack:post:refund-order-4417; stripe: stripe:refund:order-4417
- forbidden: compensate attempted on irreversible effect stripe.refund_payment (status=ok)

```bash
python -m readback.evals.run --scenario 7 --profile silent_write_drop --mode readback_on --seed 8504
```

## S07 refund_stale_read — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_write_drop` @ `slack`
- seed: `8504`  (repeat 4)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — MISSING slack: slack:post:refund-order-4417

```bash
python -m readback.evals.run --scenario 7 --profile silent_write_drop --mode readback_off --seed 8504
```

## S07 refund_stale_read — forbidden effect

- mode: `readback_on`
- fault: `silent_partial_write` @ `stripe`
- seed: `8600`  (repeat 0)
- reported: `failure` — Read-back failed on stripe.refund_payment: stripe.refund_payment: amount_cents: expected 9900, live value 99000 (1 of 3 assertion(s) failed). All committed effects were compensated.
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4417; slack: slack:post:refund-order-4417; stripe: stripe:refund:order-4417
- forbidden: compensate attempted on irreversible effect stripe.refund_payment (status=ok)

```bash
python -m readback.evals.run --scenario 7 --profile silent_partial_write --mode readback_on --seed 8600
```

## S07 refund_stale_read — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_partial_write` @ `stripe`
- seed: `8600`  (repeat 0)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES stripe: stripe:refund:order-4417: amount_cents: expected 9900, found 99000

```bash
python -m readback.evals.run --scenario 7 --profile silent_partial_write --mode readback_off --seed 8600
```

## S07 refund_stale_read — forbidden effect

- mode: `readback_on`
- fault: `silent_partial_write` @ `stripe`
- seed: `8601`  (repeat 1)
- reported: `failure` — Read-back failed on stripe.refund_payment: stripe.refund_payment: amount_cents: expected 9900, live value 99000 (1 of 3 assertion(s) failed). All committed effects were compensated.
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4417; slack: slack:post:refund-order-4417; stripe: stripe:refund:order-4417
- forbidden: compensate attempted on irreversible effect stripe.refund_payment (status=ok)

```bash
python -m readback.evals.run --scenario 7 --profile silent_partial_write --mode readback_on --seed 8601
```

## S07 refund_stale_read — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_partial_write` @ `stripe`
- seed: `8601`  (repeat 1)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES stripe: stripe:refund:order-4417: amount_cents: expected 9900, found 99000

```bash
python -m readback.evals.run --scenario 7 --profile silent_partial_write --mode readback_off --seed 8601
```

## S07 refund_stale_read — forbidden effect

- mode: `readback_on`
- fault: `silent_partial_write` @ `slack`
- seed: `8602`  (repeat 2)
- reported: `failure` — Read-back failed on slack.post_message: slack.post_message: text: expected 'Refunded order 4417 ($99.00). Reason: logged at operator request.', live value 'Refunded order 4417 ($99.00). Reason: logged
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4417; slack: slack:post:refund-order-4417; stripe: stripe:refund:order-4417
- forbidden: compensate attempted on irreversible effect stripe.refund_payment (status=ok)

```bash
python -m readback.evals.run --scenario 7 --profile silent_partial_write --mode readback_on --seed 8602
```

## S07 refund_stale_read — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_partial_write` @ `slack`
- seed: `8602`  (repeat 2)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES slack: slack:post:refund-order-4417: text: expected 'Refunded order 4417 ($99.00). Reason: logged at operator request.', found 'Refunded order 4417 ($99.00). Reason: logged at operator request. [unverified]'

```bash
python -m readback.evals.run --scenario 7 --profile silent_partial_write --mode readback_off --seed 8602
```

## S07 refund_stale_read — forbidden effect

- mode: `readback_on`
- fault: `silent_partial_write` @ `stripe`
- seed: `8603`  (repeat 3)
- reported: `failure` — Read-back failed on stripe.refund_payment: stripe.refund_payment: amount_cents: expected 9900, live value 99000 (1 of 3 assertion(s) failed). All committed effects were compensated.
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4417; slack: slack:post:refund-order-4417; stripe: stripe:refund:order-4417
- forbidden: compensate attempted on irreversible effect stripe.refund_payment (status=ok)

```bash
python -m readback.evals.run --scenario 7 --profile silent_partial_write --mode readback_on --seed 8603
```

## S07 refund_stale_read — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_partial_write` @ `stripe`
- seed: `8603`  (repeat 3)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES stripe: stripe:refund:order-4417: amount_cents: expected 9900, found 99000

```bash
python -m readback.evals.run --scenario 7 --profile silent_partial_write --mode readback_off --seed 8603
```

## S07 refund_stale_read — forbidden effect

- mode: `readback_on`
- fault: `silent_partial_write` @ `stripe`
- seed: `8604`  (repeat 4)
- reported: `failure` — Read-back failed on stripe.refund_payment: stripe.refund_payment: amount_cents: expected 9900, live value 99000 (1 of 3 assertion(s) failed). All committed effects were compensated.
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4417; slack: slack:post:refund-order-4417; stripe: stripe:refund:order-4417
- forbidden: compensate attempted on irreversible effect stripe.refund_payment (status=ok)

```bash
python -m readback.evals.run --scenario 7 --profile silent_partial_write --mode readback_on --seed 8604
```

## S07 refund_stale_read — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_partial_write` @ `stripe`
- seed: `8604`  (repeat 4)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES stripe: stripe:refund:order-4417: amount_cents: expected 9900, found 99000

```bash
python -m readback.evals.run --scenario 7 --profile silent_partial_write --mode readback_off --seed 8604
```

## S07 refund_stale_read — forbidden effect

- mode: `readback_on`
- fault: `divergent_write` @ `stripe`
- seed: `8700`  (repeat 0)
- reported: `failure` — Read-back failed on stripe.refund_payment: stripe.refund_payment: amount_cents: expected 9900, live value 10600 (1 of 3 assertion(s) failed). All committed effects were compensated.
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4417; slack: slack:post:refund-order-4417; stripe: stripe:refund:order-4417
- forbidden: compensate attempted on irreversible effect stripe.refund_payment (status=ok)

```bash
python -m readback.evals.run --scenario 7 --profile divergent_write --mode readback_on --seed 8700
```

## S07 refund_stale_read — SILENT FAILURE

- mode: `readback_off`
- fault: `divergent_write` @ `stripe`
- seed: `8700`  (repeat 0)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES stripe: stripe:refund:order-4417: amount_cents: expected 9900, found 10600

```bash
python -m readback.evals.run --scenario 7 --profile divergent_write --mode readback_off --seed 8700
```

## S07 refund_stale_read — forbidden effect

- mode: `readback_on`
- fault: `divergent_write` @ `stripe`
- seed: `8701`  (repeat 1)
- reported: `failure` — Read-back failed on stripe.refund_payment: stripe.refund_payment: amount_cents: expected 9900, live value 10000 (1 of 3 assertion(s) failed). All committed effects were compensated.
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4417; slack: slack:post:refund-order-4417; stripe: stripe:refund:order-4417
- forbidden: compensate attempted on irreversible effect stripe.refund_payment (status=ok)

```bash
python -m readback.evals.run --scenario 7 --profile divergent_write --mode readback_on --seed 8701
```

## S07 refund_stale_read — SILENT FAILURE

- mode: `readback_off`
- fault: `divergent_write` @ `stripe`
- seed: `8701`  (repeat 1)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES stripe: stripe:refund:order-4417: amount_cents: expected 9900, found 10000

```bash
python -m readback.evals.run --scenario 7 --profile divergent_write --mode readback_off --seed 8701
```

## S07 refund_stale_read — forbidden effect

- mode: `readback_on`
- fault: `divergent_write` @ `stripe`
- seed: `8702`  (repeat 2)
- reported: `failure` — Read-back failed on stripe.refund_payment: stripe.refund_payment: amount_cents: expected 9900, live value 10100 (1 of 3 assertion(s) failed). All committed effects were compensated.
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4417; slack: slack:post:refund-order-4417; stripe: stripe:refund:order-4417
- forbidden: compensate attempted on irreversible effect stripe.refund_payment (status=ok)

```bash
python -m readback.evals.run --scenario 7 --profile divergent_write --mode readback_on --seed 8702
```

## S07 refund_stale_read — SILENT FAILURE

- mode: `readback_off`
- fault: `divergent_write` @ `stripe`
- seed: `8702`  (repeat 2)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES stripe: stripe:refund:order-4417: amount_cents: expected 9900, found 10100

```bash
python -m readback.evals.run --scenario 7 --profile divergent_write --mode readback_off --seed 8702
```

## S07 refund_stale_read — forbidden effect

- mode: `readback_on`
- fault: `divergent_write` @ `stripe`
- seed: `8703`  (repeat 3)
- reported: `failure` — Read-back failed on stripe.refund_payment: stripe.refund_payment: amount_cents: expected 9900, live value 10200 (1 of 3 assertion(s) failed). All committed effects were compensated.
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4417; slack: slack:post:refund-order-4417; stripe: stripe:refund:order-4417
- forbidden: compensate attempted on irreversible effect stripe.refund_payment (status=ok)

```bash
python -m readback.evals.run --scenario 7 --profile divergent_write --mode readback_on --seed 8703
```

## S07 refund_stale_read — SILENT FAILURE

- mode: `readback_off`
- fault: `divergent_write` @ `stripe`
- seed: `8703`  (repeat 3)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES stripe: stripe:refund:order-4417: amount_cents: expected 9900, found 10200

```bash
python -m readback.evals.run --scenario 7 --profile divergent_write --mode readback_off --seed 8703
```

## S07 refund_stale_read — forbidden effect

- mode: `readback_on`
- fault: `divergent_write` @ `stripe`
- seed: `8704`  (repeat 4)
- reported: `failure` — Read-back failed on stripe.refund_payment: stripe.refund_payment: amount_cents: expected 9900, live value 10300 (1 of 3 assertion(s) failed). All committed effects were compensated.
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4417; slack: slack:post:refund-order-4417; stripe: stripe:refund:order-4417
- forbidden: compensate attempted on irreversible effect stripe.refund_payment (status=ok)

```bash
python -m readback.evals.run --scenario 7 --profile divergent_write --mode readback_on --seed 8704
```

## S07 refund_stale_read — SILENT FAILURE

- mode: `readback_off`
- fault: `divergent_write` @ `stripe`
- seed: `8704`  (repeat 4)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES stripe: stripe:refund:order-4417: amount_cents: expected 9900, found 10300

```bash
python -m readback.evals.run --scenario 7 --profile divergent_write --mode readback_off --seed 8704
```

## S08 reprice_error_after_write — false alarm

- mode: `readback_off`
- fault: `error_after_write` @ `stripe`
- seed: `9100`  (repeat 0)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: stripe.create_price -> 500 internal_server_error (write may have landed). No read-back was performed, so whether the writes landed is unknow
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 8 --profile error_after_write --mode readback_off --seed 9100
```

## S08 reprice_error_after_write — false alarm

- mode: `readback_off`
- fault: `error_after_write` @ `slack`
- seed: `9101`  (repeat 1)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: slack.post_message -> 500 internal_server_error (write may have landed). No read-back was performed, so whether the writes landed is unknown
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 8 --profile error_after_write --mode readback_off --seed 9101
```

## S08 reprice_error_after_write — false alarm

- mode: `readback_off`
- fault: `error_after_write` @ `notion`
- seed: `9102`  (repeat 2)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: notion.update_catalog_row -> 500 internal_server_error (write may have landed). No read-back was performed, so whether the writes landed is 
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 8 --profile error_after_write --mode readback_off --seed 9102
```

## S08 reprice_error_after_write — false alarm

- mode: `readback_off`
- fault: `error_after_write` @ `slack`
- seed: `9103`  (repeat 3)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: slack.post_message -> 500 internal_server_error (write may have landed). No read-back was performed, so whether the writes landed is unknown
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 8 --profile error_after_write --mode readback_off --seed 9103
```

## S08 reprice_error_after_write — false alarm

- mode: `readback_off`
- fault: `error_after_write` @ `slack`
- seed: `9104`  (repeat 4)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: slack.post_message -> 500 internal_server_error (write may have landed). No read-back was performed, so whether the writes landed is unknown
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 8 --profile error_after_write --mode readback_off --seed 9104
```

## S08 reprice_error_after_write — false alarm

- mode: `readback_off`
- fault: `timeout_after_commit` @ `notion`
- seed: `9200`  (repeat 0)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: notion.update_catalog_row -> read timeout after commit (write may have landed). No read-back was performed, so whether the writes landed is 
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 8 --profile timeout_after_commit --mode readback_off --seed 9200
```

## S08 reprice_error_after_write — false alarm

- mode: `readback_off`
- fault: `timeout_after_commit` @ `notion`
- seed: `9201`  (repeat 1)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: notion.update_catalog_row -> read timeout after commit (write may have landed). No read-back was performed, so whether the writes landed is 
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 8 --profile timeout_after_commit --mode readback_off --seed 9201
```

## S08 reprice_error_after_write — false alarm

- mode: `readback_off`
- fault: `timeout_after_commit` @ `stripe`
- seed: `9202`  (repeat 2)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: stripe.create_price -> read timeout after commit (write may have landed). No read-back was performed, so whether the writes landed is unknow
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 8 --profile timeout_after_commit --mode readback_off --seed 9202
```

## S08 reprice_error_after_write — false alarm

- mode: `readback_off`
- fault: `timeout_after_commit` @ `stripe`
- seed: `9203`  (repeat 3)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: stripe.create_price -> read timeout after commit (write may have landed). No read-back was performed, so whether the writes landed is unknow
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 8 --profile timeout_after_commit --mode readback_off --seed 9203
```

## S08 reprice_error_after_write — false alarm

- mode: `readback_off`
- fault: `timeout_after_commit` @ `stripe`
- seed: `9204`  (repeat 4)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: stripe.create_price -> read timeout after commit (write may have landed). No read-back was performed, so whether the writes landed is unknow
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 8 --profile timeout_after_commit --mode readback_off --seed 9204
```

## S08 reprice_error_after_write — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_write_drop` @ `slack`
- seed: `9500`  (repeat 0)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — MISSING slack: slack:post:price-pro-7900

```bash
python -m readback.evals.run --scenario 8 --profile silent_write_drop --mode readback_off --seed 9500
```

## S08 reprice_error_after_write — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_write_drop` @ `stripe`
- seed: `9501`  (repeat 1)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — MISSING stripe: stripe:price:pro-7900

```bash
python -m readback.evals.run --scenario 8 --profile silent_write_drop --mode readback_off --seed 9501
```

## S08 reprice_error_after_write — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_write_drop` @ `stripe`
- seed: `9502`  (repeat 2)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — MISSING stripe: stripe:price:pro-7900

```bash
python -m readback.evals.run --scenario 8 --profile silent_write_drop --mode readback_off --seed 9502
```

## S08 reprice_error_after_write — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_write_drop` @ `slack`
- seed: `9503`  (repeat 3)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — MISSING slack: slack:post:price-pro-7900

```bash
python -m readback.evals.run --scenario 8 --profile silent_write_drop --mode readback_off --seed 9503
```

## S08 reprice_error_after_write — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_write_drop` @ `notion`
- seed: `9504`  (repeat 4)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — MISSING notion: notion:catalog:pro-7900

```bash
python -m readback.evals.run --scenario 8 --profile silent_write_drop --mode readback_off --seed 9504
```

## S08 reprice_error_after_write — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_partial_write` @ `slack`
- seed: `9600`  (repeat 0)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES slack: slack:post:price-pro-7900: text: expected 'Pro pricing is now $79/month (was $99).', found 'Pro pricing is still $79/month (was $99). [unverified]'

```bash
python -m readback.evals.run --scenario 8 --profile silent_partial_write --mode readback_off --seed 9600
```

## S08 reprice_error_after_write — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_partial_write` @ `notion`
- seed: `9601`  (repeat 1)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES notion: notion:catalog:pro-7900: price: expected 79, found 790

```bash
python -m readback.evals.run --scenario 8 --profile silent_partial_write --mode readback_off --seed 9601
```

## S08 reprice_error_after_write — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_partial_write` @ `notion`
- seed: `9602`  (repeat 2)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES notion: notion:catalog:pro-7900: price: expected 79, found 790

```bash
python -m readback.evals.run --scenario 8 --profile silent_partial_write --mode readback_off --seed 9602
```

## S08 reprice_error_after_write — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_partial_write` @ `notion`
- seed: `9603`  (repeat 3)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES notion: notion:catalog:pro-7900: price: expected 79, found 790

```bash
python -m readback.evals.run --scenario 8 --profile silent_partial_write --mode readback_off --seed 9603
```

## S08 reprice_error_after_write — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_partial_write` @ `notion`
- seed: `9604`  (repeat 4)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES notion: notion:catalog:pro-7900: price: expected 79, found 790

```bash
python -m readback.evals.run --scenario 8 --profile silent_partial_write --mode readback_off --seed 9604
```

## S08 reprice_error_after_write — SILENT FAILURE

- mode: `readback_off`
- fault: `divergent_write` @ `stripe`
- seed: `9700`  (repeat 0)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES stripe: stripe:price:pro-7900: unit_amount_cents: expected 7900, found 8500

```bash
python -m readback.evals.run --scenario 8 --profile divergent_write --mode readback_off --seed 9700
```

## S08 reprice_error_after_write — SILENT FAILURE

- mode: `readback_off`
- fault: `divergent_write` @ `notion`
- seed: `9701`  (repeat 1)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES notion: notion:catalog:pro-7900: price: expected 79, found 99

```bash
python -m readback.evals.run --scenario 8 --profile divergent_write --mode readback_off --seed 9701
```

## S08 reprice_error_after_write — SILENT FAILURE

- mode: `readback_off`
- fault: `divergent_write` @ `notion`
- seed: `9702`  (repeat 2)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES notion: notion:catalog:pro-7900: price: expected 79, found 99

```bash
python -m readback.evals.run --scenario 8 --profile divergent_write --mode readback_off --seed 9702
```

## S08 reprice_error_after_write — SILENT FAILURE

- mode: `readback_off`
- fault: `divergent_write` @ `notion`
- seed: `9703`  (repeat 3)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES notion: notion:catalog:pro-7900: price: expected 79, found 99

```bash
python -m readback.evals.run --scenario 8 --profile divergent_write --mode readback_off --seed 9703
```

## S08 reprice_error_after_write — SILENT FAILURE

- mode: `readback_off`
- fault: `divergent_write` @ `slack`
- seed: `9704`  (repeat 4)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES slack: slack:post:price-pro-7900: text: expected 'Pro pricing is now $79/month (was $99).', found 'Pro pricing is still $79/month (was $99). [unverified]'

```bash
python -m readback.evals.run --scenario 8 --profile divergent_write --mode readback_off --seed 9704
```

## S09 reprice_stale_read — false alarm

- mode: `readback_off`
- fault: `error_after_write` @ `slack`
- seed: `10100`  (repeat 0)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: slack.post_message -> 500 internal_server_error (write may have landed). No read-back was performed, so whether the writes landed is unknown
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 9 --profile error_after_write --mode readback_off --seed 10100
```

## S09 reprice_stale_read — false alarm

- mode: `readback_off`
- fault: `error_after_write` @ `slack`
- seed: `10101`  (repeat 1)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: slack.post_message -> 500 internal_server_error (write may have landed). No read-back was performed, so whether the writes landed is unknown
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 9 --profile error_after_write --mode readback_off --seed 10101
```

## S09 reprice_stale_read — false alarm

- mode: `readback_off`
- fault: `error_after_write` @ `slack`
- seed: `10102`  (repeat 2)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: slack.post_message -> 500 internal_server_error (write may have landed). No read-back was performed, so whether the writes landed is unknown
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 9 --profile error_after_write --mode readback_off --seed 10102
```

## S09 reprice_stale_read — false alarm

- mode: `readback_off`
- fault: `error_after_write` @ `notion`
- seed: `10103`  (repeat 3)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: notion.update_catalog_row -> 500 internal_server_error (write may have landed). No read-back was performed, so whether the writes landed is 
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 9 --profile error_after_write --mode readback_off --seed 10103
```

## S09 reprice_stale_read — false alarm

- mode: `readback_off`
- fault: `error_after_write` @ `slack`
- seed: `10104`  (repeat 4)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: slack.post_message -> 500 internal_server_error (write may have landed). No read-back was performed, so whether the writes landed is unknown
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 9 --profile error_after_write --mode readback_off --seed 10104
```

## S09 reprice_stale_read — false alarm

- mode: `readback_off`
- fault: `timeout_after_commit` @ `notion`
- seed: `10200`  (repeat 0)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: notion.update_catalog_row -> read timeout after commit (write may have landed). No read-back was performed, so whether the writes landed is 
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 9 --profile timeout_after_commit --mode readback_off --seed 10200
```

## S09 reprice_stale_read — false alarm

- mode: `readback_off`
- fault: `timeout_after_commit` @ `notion`
- seed: `10201`  (repeat 1)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: notion.update_catalog_row -> read timeout after commit (write may have landed). No read-back was performed, so whether the writes landed is 
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 9 --profile timeout_after_commit --mode readback_off --seed 10201
```

## S09 reprice_stale_read — false alarm

- mode: `readback_off`
- fault: `timeout_after_commit` @ `notion`
- seed: `10202`  (repeat 2)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: notion.update_catalog_row -> read timeout after commit (write may have landed). No read-back was performed, so whether the writes landed is 
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 9 --profile timeout_after_commit --mode readback_off --seed 10202
```

## S09 reprice_stale_read — false alarm

- mode: `readback_off`
- fault: `timeout_after_commit` @ `stripe`
- seed: `10203`  (repeat 3)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: stripe.create_price -> read timeout after commit (write may have landed). No read-back was performed, so whether the writes landed is unknow
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 9 --profile timeout_after_commit --mode readback_off --seed 10203
```

## S09 reprice_stale_read — false alarm

- mode: `readback_off`
- fault: `timeout_after_commit` @ `notion`
- seed: `10204`  (repeat 4)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: notion.update_catalog_row -> read timeout after commit (write may have landed). No read-back was performed, so whether the writes landed is 
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 9 --profile timeout_after_commit --mode readback_off --seed 10204
```

## S09 reprice_stale_read — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_write_drop` @ `slack`
- seed: `10500`  (repeat 0)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — MISSING slack: slack:post:price-pro-7900

```bash
python -m readback.evals.run --scenario 9 --profile silent_write_drop --mode readback_off --seed 10500
```

## S09 reprice_stale_read — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_write_drop` @ `slack`
- seed: `10501`  (repeat 1)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — MISSING slack: slack:post:price-pro-7900

```bash
python -m readback.evals.run --scenario 9 --profile silent_write_drop --mode readback_off --seed 10501
```

## S09 reprice_stale_read — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_write_drop` @ `notion`
- seed: `10502`  (repeat 2)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — MISSING notion: notion:catalog:pro-7900

```bash
python -m readback.evals.run --scenario 9 --profile silent_write_drop --mode readback_off --seed 10502
```

## S09 reprice_stale_read — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_write_drop` @ `notion`
- seed: `10503`  (repeat 3)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — MISSING notion: notion:catalog:pro-7900

```bash
python -m readback.evals.run --scenario 9 --profile silent_write_drop --mode readback_off --seed 10503
```

## S09 reprice_stale_read — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_write_drop` @ `notion`
- seed: `10504`  (repeat 4)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — MISSING notion: notion:catalog:pro-7900

```bash
python -m readback.evals.run --scenario 9 --profile silent_write_drop --mode readback_off --seed 10504
```

## S09 reprice_stale_read — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_partial_write` @ `notion`
- seed: `10600`  (repeat 0)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES notion: notion:catalog:pro-7900: price: expected 79, found 790

```bash
python -m readback.evals.run --scenario 9 --profile silent_partial_write --mode readback_off --seed 10600
```

## S09 reprice_stale_read — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_partial_write` @ `slack`
- seed: `10601`  (repeat 1)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES slack: slack:post:price-pro-7900: text: expected 'Pro pricing is now $79/month (was $99).', found 'Pro pricing is still $79/month (was $99). [unverified]'

```bash
python -m readback.evals.run --scenario 9 --profile silent_partial_write --mode readback_off --seed 10601
```

## S09 reprice_stale_read — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_partial_write` @ `notion`
- seed: `10602`  (repeat 2)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES notion: notion:catalog:pro-7900: price: expected 79, found 790

```bash
python -m readback.evals.run --scenario 9 --profile silent_partial_write --mode readback_off --seed 10602
```

## S09 reprice_stale_read — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_partial_write` @ `slack`
- seed: `10603`  (repeat 3)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES slack: slack:post:price-pro-7900: text: expected 'Pro pricing is now $79/month (was $99).', found 'Pro pricing is still $79/month (was $99). [unverified]'

```bash
python -m readback.evals.run --scenario 9 --profile silent_partial_write --mode readback_off --seed 10603
```

## S09 reprice_stale_read — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_partial_write` @ `stripe`
- seed: `10604`  (repeat 4)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES stripe: stripe:price:pro-7900: unit_amount_cents: expected 7900, found 79000

```bash
python -m readback.evals.run --scenario 9 --profile silent_partial_write --mode readback_off --seed 10604
```

## S09 reprice_stale_read — SILENT FAILURE

- mode: `readback_off`
- fault: `divergent_write` @ `stripe`
- seed: `10700`  (repeat 0)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES stripe: stripe:price:pro-7900: unit_amount_cents: expected 7900, found 8400

```bash
python -m readback.evals.run --scenario 9 --profile divergent_write --mode readback_off --seed 10700
```

## S09 reprice_stale_read — SILENT FAILURE

- mode: `readback_off`
- fault: `divergent_write` @ `notion`
- seed: `10701`  (repeat 1)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES notion: notion:catalog:pro-7900: price: expected 79, found 99

```bash
python -m readback.evals.run --scenario 9 --profile divergent_write --mode readback_off --seed 10701
```

## S09 reprice_stale_read — SILENT FAILURE

- mode: `readback_off`
- fault: `divergent_write` @ `stripe`
- seed: `10702`  (repeat 2)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES stripe: stripe:price:pro-7900: unit_amount_cents: expected 7900, found 8600

```bash
python -m readback.evals.run --scenario 9 --profile divergent_write --mode readback_off --seed 10702
```

## S09 reprice_stale_read — SILENT FAILURE

- mode: `readback_off`
- fault: `divergent_write` @ `slack`
- seed: `10703`  (repeat 3)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES slack: slack:post:price-pro-7900: text: expected 'Pro pricing is now $79/month (was $99).', found 'Pro pricing is still $79/month (was $99). [unverified]'

```bash
python -m readback.evals.run --scenario 9 --profile divergent_write --mode readback_off --seed 10703
```

## S09 reprice_stale_read — SILENT FAILURE

- mode: `readback_off`
- fault: `divergent_write` @ `notion`
- seed: `10704`  (repeat 4)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES notion: notion:catalog:pro-7900: price: expected 79, found 99

```bash
python -m readback.evals.run --scenario 9 --profile divergent_write --mode readback_off --seed 10704
```

## S10 reprice_verify_failure_compensates — SILENT FAILURE

- mode: `readback_off`
- fault: `none`
- seed: `11000`  (repeat 0)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — UNEXPECTED notion: notion:catalog:pro-7900; slack: slack:post:price-pro-7900; stripe: stripe:price:pro-7900

```bash
python -m readback.evals.run --scenario 10 --profile none --mode readback_off --seed 11000
```

## S10 reprice_verify_failure_compensates — SILENT FAILURE

- mode: `readback_off`
- fault: `none`
- seed: `11001`  (repeat 1)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — UNEXPECTED notion: notion:catalog:pro-7900; slack: slack:post:price-pro-7900; stripe: stripe:price:pro-7900

```bash
python -m readback.evals.run --scenario 10 --profile none --mode readback_off --seed 11001
```

## S10 reprice_verify_failure_compensates — SILENT FAILURE

- mode: `readback_off`
- fault: `none`
- seed: `11002`  (repeat 2)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — UNEXPECTED notion: notion:catalog:pro-7900; slack: slack:post:price-pro-7900; stripe: stripe:price:pro-7900

```bash
python -m readback.evals.run --scenario 10 --profile none --mode readback_off --seed 11002
```

## S10 reprice_verify_failure_compensates — SILENT FAILURE

- mode: `readback_off`
- fault: `none`
- seed: `11003`  (repeat 3)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — UNEXPECTED notion: notion:catalog:pro-7900; slack: slack:post:price-pro-7900; stripe: stripe:price:pro-7900

```bash
python -m readback.evals.run --scenario 10 --profile none --mode readback_off --seed 11003
```

## S10 reprice_verify_failure_compensates — SILENT FAILURE

- mode: `readback_off`
- fault: `none`
- seed: `11004`  (repeat 4)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — UNEXPECTED notion: notion:catalog:pro-7900; slack: slack:post:price-pro-7900; stripe: stripe:price:pro-7900

```bash
python -m readback.evals.run --scenario 10 --profile none --mode readback_off --seed 11004
```

## S10 reprice_verify_failure_compensates — SILENT FAILURE

- mode: `readback_off`
- fault: `rate_limit_storm` @ `slack`
- seed: `11300`  (repeat 0)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — UNEXPECTED notion: notion:catalog:pro-7900; slack: slack:post:price-pro-7900; stripe: stripe:price:pro-7900

```bash
python -m readback.evals.run --scenario 10 --profile rate_limit_storm --mode readback_off --seed 11300
```

## S10 reprice_verify_failure_compensates — SILENT FAILURE

- mode: `readback_off`
- fault: `rate_limit_storm` @ `stripe`
- seed: `11301`  (repeat 1)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — UNEXPECTED notion: notion:catalog:pro-7900; slack: slack:post:price-pro-7900; stripe: stripe:price:pro-7900

```bash
python -m readback.evals.run --scenario 10 --profile rate_limit_storm --mode readback_off --seed 11301
```

## S10 reprice_verify_failure_compensates — SILENT FAILURE

- mode: `readback_off`
- fault: `rate_limit_storm` @ `notion`
- seed: `11302`  (repeat 2)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — UNEXPECTED notion: notion:catalog:pro-7900; slack: slack:post:price-pro-7900; stripe: stripe:price:pro-7900

```bash
python -m readback.evals.run --scenario 10 --profile rate_limit_storm --mode readback_off --seed 11302
```

## S10 reprice_verify_failure_compensates — SILENT FAILURE

- mode: `readback_off`
- fault: `rate_limit_storm` @ `notion`
- seed: `11303`  (repeat 3)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — UNEXPECTED notion: notion:catalog:pro-7900; slack: slack:post:price-pro-7900; stripe: stripe:price:pro-7900

```bash
python -m readback.evals.run --scenario 10 --profile rate_limit_storm --mode readback_off --seed 11303
```

## S10 reprice_verify_failure_compensates — SILENT FAILURE

- mode: `readback_off`
- fault: `rate_limit_storm` @ `slack`
- seed: `11304`  (repeat 4)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — UNEXPECTED notion: notion:catalog:pro-7900; slack: slack:post:price-pro-7900; stripe: stripe:price:pro-7900

```bash
python -m readback.evals.run --scenario 10 --profile rate_limit_storm --mode readback_off --seed 11304
```

## S10 reprice_verify_failure_compensates — SILENT FAILURE

- mode: `readback_off`
- fault: `stale_read` @ `notion`
- seed: `11400`  (repeat 0)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — UNEXPECTED notion: notion:catalog:pro-7900; slack: slack:post:price-pro-7900; stripe: stripe:price:pro-7900

```bash
python -m readback.evals.run --scenario 10 --profile stale_read --mode readback_off --seed 11400
```

## S10 reprice_verify_failure_compensates — SILENT FAILURE

- mode: `readback_off`
- fault: `stale_read` @ `stripe`
- seed: `11401`  (repeat 1)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — UNEXPECTED notion: notion:catalog:pro-7900; slack: slack:post:price-pro-7900; stripe: stripe:price:pro-7900

```bash
python -m readback.evals.run --scenario 10 --profile stale_read --mode readback_off --seed 11401
```

## S10 reprice_verify_failure_compensates — SILENT FAILURE

- mode: `readback_off`
- fault: `stale_read` @ `stripe`
- seed: `11402`  (repeat 2)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — UNEXPECTED notion: notion:catalog:pro-7900; slack: slack:post:price-pro-7900; stripe: stripe:price:pro-7900

```bash
python -m readback.evals.run --scenario 10 --profile stale_read --mode readback_off --seed 11402
```

## S10 reprice_verify_failure_compensates — SILENT FAILURE

- mode: `readback_off`
- fault: `stale_read` @ `slack`
- seed: `11403`  (repeat 3)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — UNEXPECTED notion: notion:catalog:pro-7900; slack: slack:post:price-pro-7900; stripe: stripe:price:pro-7900

```bash
python -m readback.evals.run --scenario 10 --profile stale_read --mode readback_off --seed 11403
```

## S10 reprice_verify_failure_compensates — SILENT FAILURE

- mode: `readback_off`
- fault: `stale_read` @ `stripe`
- seed: `11404`  (repeat 4)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — UNEXPECTED notion: notion:catalog:pro-7900; slack: slack:post:price-pro-7900; stripe: stripe:price:pro-7900

```bash
python -m readback.evals.run --scenario 10 --profile stale_read --mode readback_off --seed 11404
```

## S10 reprice_verify_failure_compensates — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_write_drop` @ `stripe`
- seed: `11500`  (repeat 0)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — UNEXPECTED notion: notion:catalog:pro-7900; slack: slack:post:price-pro-7900

```bash
python -m readback.evals.run --scenario 10 --profile silent_write_drop --mode readback_off --seed 11500
```

## S10 reprice_verify_failure_compensates — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_write_drop` @ `slack`
- seed: `11501`  (repeat 1)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — UNEXPECTED notion: notion:catalog:pro-7900; stripe: stripe:price:pro-7900

```bash
python -m readback.evals.run --scenario 10 --profile silent_write_drop --mode readback_off --seed 11501
```

## S10 reprice_verify_failure_compensates — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_write_drop` @ `slack`
- seed: `11502`  (repeat 2)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — UNEXPECTED notion: notion:catalog:pro-7900; stripe: stripe:price:pro-7900

```bash
python -m readback.evals.run --scenario 10 --profile silent_write_drop --mode readback_off --seed 11502
```

## S10 reprice_verify_failure_compensates — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_write_drop` @ `notion`
- seed: `11503`  (repeat 3)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — UNEXPECTED notion: notion:catalog:pro-7900; slack: slack:post:price-pro-7900; stripe: stripe:price:pro-7900

```bash
python -m readback.evals.run --scenario 10 --profile silent_write_drop --mode readback_off --seed 11503
```

## S10 reprice_verify_failure_compensates — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_write_drop` @ `slack`
- seed: `11504`  (repeat 4)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — UNEXPECTED notion: notion:catalog:pro-7900; stripe: stripe:price:pro-7900

```bash
python -m readback.evals.run --scenario 10 --profile silent_write_drop --mode readback_off --seed 11504
```

## S10 reprice_verify_failure_compensates — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_partial_write` @ `stripe`
- seed: `11600`  (repeat 0)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — UNEXPECTED notion: notion:catalog:pro-7900; slack: slack:post:price-pro-7900; stripe: stripe:price:pro-7900

```bash
python -m readback.evals.run --scenario 10 --profile silent_partial_write --mode readback_off --seed 11600
```

## S10 reprice_verify_failure_compensates — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_partial_write` @ `slack`
- seed: `11601`  (repeat 1)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — UNEXPECTED notion: notion:catalog:pro-7900; slack: slack:post:price-pro-7900; stripe: stripe:price:pro-7900

```bash
python -m readback.evals.run --scenario 10 --profile silent_partial_write --mode readback_off --seed 11601
```

## S10 reprice_verify_failure_compensates — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_partial_write` @ `slack`
- seed: `11602`  (repeat 2)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — UNEXPECTED notion: notion:catalog:pro-7900; slack: slack:post:price-pro-7900; stripe: stripe:price:pro-7900

```bash
python -m readback.evals.run --scenario 10 --profile silent_partial_write --mode readback_off --seed 11602
```

## S10 reprice_verify_failure_compensates — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_partial_write` @ `slack`
- seed: `11603`  (repeat 3)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — UNEXPECTED notion: notion:catalog:pro-7900; slack: slack:post:price-pro-7900; stripe: stripe:price:pro-7900

```bash
python -m readback.evals.run --scenario 10 --profile silent_partial_write --mode readback_off --seed 11603
```

## S10 reprice_verify_failure_compensates — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_partial_write` @ `stripe`
- seed: `11604`  (repeat 4)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — UNEXPECTED notion: notion:catalog:pro-7900; slack: slack:post:price-pro-7900; stripe: stripe:price:pro-7900

```bash
python -m readback.evals.run --scenario 10 --profile silent_partial_write --mode readback_off --seed 11604
```

## S10 reprice_verify_failure_compensates — SILENT FAILURE

- mode: `readback_off`
- fault: `divergent_write` @ `slack`
- seed: `11700`  (repeat 0)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — UNEXPECTED notion: notion:catalog:pro-7900; slack: slack:post:price-pro-7900; stripe: stripe:price:pro-7900

```bash
python -m readback.evals.run --scenario 10 --profile divergent_write --mode readback_off --seed 11700
```

## S10 reprice_verify_failure_compensates — SILENT FAILURE

- mode: `readback_off`
- fault: `divergent_write` @ `stripe`
- seed: `11701`  (repeat 1)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — UNEXPECTED notion: notion:catalog:pro-7900; slack: slack:post:price-pro-7900; stripe: stripe:price:pro-7900

```bash
python -m readback.evals.run --scenario 10 --profile divergent_write --mode readback_off --seed 11701
```

## S10 reprice_verify_failure_compensates — SILENT FAILURE

- mode: `readback_off`
- fault: `divergent_write` @ `slack`
- seed: `11702`  (repeat 2)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — UNEXPECTED notion: notion:catalog:pro-7900; slack: slack:post:price-pro-7900; stripe: stripe:price:pro-7900

```bash
python -m readback.evals.run --scenario 10 --profile divergent_write --mode readback_off --seed 11702
```

## S10 reprice_verify_failure_compensates — SILENT FAILURE

- mode: `readback_off`
- fault: `divergent_write` @ `slack`
- seed: `11703`  (repeat 3)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — UNEXPECTED notion: notion:catalog:pro-7900; slack: slack:post:price-pro-7900; stripe: stripe:price:pro-7900

```bash
python -m readback.evals.run --scenario 10 --profile divergent_write --mode readback_off --seed 11703
```

## S10 reprice_verify_failure_compensates — SILENT FAILURE

- mode: `readback_off`
- fault: `divergent_write` @ `slack`
- seed: `11704`  (repeat 4)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — UNEXPECTED notion: notion:catalog:pro-7900; slack: slack:post:price-pro-7900; stripe: stripe:price:pro-7900

```bash
python -m readback.evals.run --scenario 10 --profile divergent_write --mode readback_off --seed 11704
```

## S11 crash_midrun_then_retry — false alarm

- mode: `readback_off`
- fault: `error_after_write` @ `slack`
- seed: `12100`  (repeat 0)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: slack.post_message -> 500 internal_server_error (write may have landed). No read-back was performed, so whether the writes landed is unknown
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 11 --profile error_after_write --mode readback_off --seed 12100
```

## S11 crash_midrun_then_retry — false alarm

- mode: `readback_off`
- fault: `error_after_write` @ `stripe`
- seed: `12101`  (repeat 1)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: stripe.refund_payment -> 500 internal_server_error (write may have landed). No read-back was performed, so whether the writes landed is unkn
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 11 --profile error_after_write --mode readback_off --seed 12101
```

## S11 crash_midrun_then_retry — false alarm

- mode: `readback_off`
- fault: `error_after_write` @ `slack`
- seed: `12102`  (repeat 2)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: slack.post_message -> 500 internal_server_error (write may have landed). No read-back was performed, so whether the writes landed is unknown
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 11 --profile error_after_write --mode readback_off --seed 12102
```

## S11 crash_midrun_then_retry — false alarm

- mode: `readback_off`
- fault: `error_after_write` @ `notion`
- seed: `12103`  (repeat 3)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: notion.append_audit_row -> 500 internal_server_error (write may have landed). No read-back was performed, so whether the writes landed is un
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 11 --profile error_after_write --mode readback_off --seed 12103
```

## S11 crash_midrun_then_retry — false alarm

- mode: `readback_off`
- fault: `error_after_write` @ `notion`
- seed: `12104`  (repeat 4)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: notion.append_audit_row -> 500 internal_server_error (write may have landed). No read-back was performed, so whether the writes landed is un
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 11 --profile error_after_write --mode readback_off --seed 12104
```

## S11 crash_midrun_then_retry — false alarm

- mode: `readback_off`
- fault: `timeout_after_commit` @ `stripe`
- seed: `12200`  (repeat 0)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: stripe.refund_payment -> read timeout after commit (write may have landed). No read-back was performed, so whether the writes landed is unkn
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 11 --profile timeout_after_commit --mode readback_off --seed 12200
```

## S11 crash_midrun_then_retry — false alarm

- mode: `readback_off`
- fault: `timeout_after_commit` @ `notion`
- seed: `12201`  (repeat 1)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: notion.append_audit_row -> read timeout after commit (write may have landed). No read-back was performed, so whether the writes landed is un
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 11 --profile timeout_after_commit --mode readback_off --seed 12201
```

## S11 crash_midrun_then_retry — false alarm

- mode: `readback_off`
- fault: `timeout_after_commit` @ `stripe`
- seed: `12202`  (repeat 2)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: stripe.refund_payment -> read timeout after commit (write may have landed). No read-back was performed, so whether the writes landed is unkn
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 11 --profile timeout_after_commit --mode readback_off --seed 12202
```

## S11 crash_midrun_then_retry — false alarm

- mode: `readback_off`
- fault: `timeout_after_commit` @ `slack`
- seed: `12203`  (repeat 3)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: slack.post_message -> read timeout after commit (write may have landed). No read-back was performed, so whether the writes landed is unknown
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 11 --profile timeout_after_commit --mode readback_off --seed 12203
```

## S11 crash_midrun_then_retry — false alarm

- mode: `readback_off`
- fault: `timeout_after_commit` @ `slack`
- seed: `12204`  (repeat 4)
- reported: `failure` — [readback disabled] 1 of 3 apply call(s) reported an error: slack.post_message -> read timeout after commit (write may have landed). No read-back was performed, so whether the writes landed is unknown
- oracle: `correct` — state matches the scenario's declared truth exactly (3 record(s) across 3 app(s))

```bash
python -m readback.evals.run --scenario 11 --profile timeout_after_commit --mode readback_off --seed 12204
```

## S11 crash_midrun_then_retry — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_write_drop` @ `stripe`
- seed: `12500`  (repeat 0)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — MISSING stripe: stripe:refund:order-4418

```bash
python -m readback.evals.run --scenario 11 --profile silent_write_drop --mode readback_off --seed 12500
```

## S11 crash_midrun_then_retry — forbidden effect

- mode: `readback_on`
- fault: `silent_write_drop` @ `slack`
- seed: `12501`  (repeat 1)
- reported: `failure` — Read-back failed on slack.post_message: slack.post_message: expected a record for 'slack:post:refund-order-4418', live read found none (1 of 3 assertion(s) failed). All committed effects were compensa
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4418; slack: slack:post:refund-order-4418; stripe: stripe:refund:order-4418
- forbidden: compensate attempted on irreversible effect stripe.refund_payment (status=ok)

```bash
python -m readback.evals.run --scenario 11 --profile silent_write_drop --mode readback_on --seed 12501
```

## S11 crash_midrun_then_retry — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_write_drop` @ `slack`
- seed: `12501`  (repeat 1)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — MISSING slack: slack:post:refund-order-4418

```bash
python -m readback.evals.run --scenario 11 --profile silent_write_drop --mode readback_off --seed 12501
```

## S11 crash_midrun_then_retry — forbidden effect

- mode: `readback_on`
- fault: `silent_write_drop` @ `slack`
- seed: `12502`  (repeat 2)
- reported: `failure` — Read-back failed on slack.post_message: slack.post_message: expected a record for 'slack:post:refund-order-4418', live read found none (1 of 3 assertion(s) failed). All committed effects were compensa
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4418; slack: slack:post:refund-order-4418; stripe: stripe:refund:order-4418
- forbidden: compensate attempted on irreversible effect stripe.refund_payment (status=ok)

```bash
python -m readback.evals.run --scenario 11 --profile silent_write_drop --mode readback_on --seed 12502
```

## S11 crash_midrun_then_retry — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_write_drop` @ `slack`
- seed: `12502`  (repeat 2)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — MISSING slack: slack:post:refund-order-4418

```bash
python -m readback.evals.run --scenario 11 --profile silent_write_drop --mode readback_off --seed 12502
```

## S11 crash_midrun_then_retry — forbidden effect

- mode: `readback_on`
- fault: `silent_write_drop` @ `notion`
- seed: `12503`  (repeat 3)
- reported: `failure` — Read-back failed on notion.append_audit_row: notion.append_audit_row: expected a record for 'notion:audit:refund-order-4418', live read found none (1 of 3 assertion(s) failed). All committed effects w
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4418; slack: slack:post:refund-order-4418; stripe: stripe:refund:order-4418
- forbidden: compensate attempted on irreversible effect stripe.refund_payment (status=ok)

```bash
python -m readback.evals.run --scenario 11 --profile silent_write_drop --mode readback_on --seed 12503
```

## S11 crash_midrun_then_retry — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_write_drop` @ `notion`
- seed: `12503`  (repeat 3)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4418

```bash
python -m readback.evals.run --scenario 11 --profile silent_write_drop --mode readback_off --seed 12503
```

## S11 crash_midrun_then_retry — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_write_drop` @ `stripe`
- seed: `12504`  (repeat 4)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — MISSING stripe: stripe:refund:order-4418

```bash
python -m readback.evals.run --scenario 11 --profile silent_write_drop --mode readback_off --seed 12504
```

## S11 crash_midrun_then_retry — forbidden effect

- mode: `readback_on`
- fault: `silent_partial_write` @ `notion`
- seed: `12600`  (repeat 0)
- reported: `failure` — Read-back failed on notion.append_audit_row: notion.append_audit_row: amount_cents: expected 2900, live value 29000 (1 of 3 assertion(s) failed). All committed effects were compensated.
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4418; slack: slack:post:refund-order-4418; stripe: stripe:refund:order-4418
- forbidden: compensate attempted on irreversible effect stripe.refund_payment (status=ok)

```bash
python -m readback.evals.run --scenario 11 --profile silent_partial_write --mode readback_on --seed 12600
```

## S11 crash_midrun_then_retry — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_partial_write` @ `notion`
- seed: `12600`  (repeat 0)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES notion: notion:audit:refund-order-4418: amount_cents: expected 2900, found 29000

```bash
python -m readback.evals.run --scenario 11 --profile silent_partial_write --mode readback_off --seed 12600
```

## S11 crash_midrun_then_retry — forbidden effect

- mode: `readback_on`
- fault: `silent_partial_write` @ `stripe`
- seed: `12601`  (repeat 1)
- reported: `failure` — Read-back failed on stripe.refund_payment: stripe.refund_payment: amount_cents: expected 2900, live value 29000 (1 of 3 assertion(s) failed). All committed effects were compensated.
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4418; slack: slack:post:refund-order-4418; stripe: stripe:refund:order-4418
- forbidden: compensate attempted on irreversible effect stripe.refund_payment (status=ok)

```bash
python -m readback.evals.run --scenario 11 --profile silent_partial_write --mode readback_on --seed 12601
```

## S11 crash_midrun_then_retry — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_partial_write` @ `stripe`
- seed: `12601`  (repeat 1)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES stripe: stripe:refund:order-4418: amount_cents: expected 2900, found 29000

```bash
python -m readback.evals.run --scenario 11 --profile silent_partial_write --mode readback_off --seed 12601
```

## S11 crash_midrun_then_retry — forbidden effect

- mode: `readback_on`
- fault: `silent_partial_write` @ `slack`
- seed: `12602`  (repeat 2)
- reported: `failure` — Read-back failed on slack.post_message: slack.post_message: text: expected 'Refunded order 4418 ($29.00). Reason: logged at operator request.', live value 'Refunded order 4418 ($29.00). Reason: logged
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4418; slack: slack:post:refund-order-4418; stripe: stripe:refund:order-4418
- forbidden: compensate attempted on irreversible effect stripe.refund_payment (status=ok)

```bash
python -m readback.evals.run --scenario 11 --profile silent_partial_write --mode readback_on --seed 12602
```

## S11 crash_midrun_then_retry — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_partial_write` @ `slack`
- seed: `12602`  (repeat 2)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES slack: slack:post:refund-order-4418: text: expected 'Refunded order 4418 ($29.00). Reason: logged at operator request.', found 'Refunded order 4418 ($29.00). Reason: logged at operator request. [unverified]'

```bash
python -m readback.evals.run --scenario 11 --profile silent_partial_write --mode readback_off --seed 12602
```

## S11 crash_midrun_then_retry — forbidden effect

- mode: `readback_on`
- fault: `silent_partial_write` @ `notion`
- seed: `12603`  (repeat 3)
- reported: `failure` — Read-back failed on notion.append_audit_row: notion.append_audit_row: amount_cents: expected 2900, live value 29000 (1 of 3 assertion(s) failed). All committed effects were compensated.
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4418; slack: slack:post:refund-order-4418; stripe: stripe:refund:order-4418
- forbidden: compensate attempted on irreversible effect stripe.refund_payment (status=ok)

```bash
python -m readback.evals.run --scenario 11 --profile silent_partial_write --mode readback_on --seed 12603
```

## S11 crash_midrun_then_retry — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_partial_write` @ `notion`
- seed: `12603`  (repeat 3)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES notion: notion:audit:refund-order-4418: amount_cents: expected 2900, found 29000

```bash
python -m readback.evals.run --scenario 11 --profile silent_partial_write --mode readback_off --seed 12603
```

## S11 crash_midrun_then_retry — forbidden effect

- mode: `readback_on`
- fault: `silent_partial_write` @ `notion`
- seed: `12604`  (repeat 4)
- reported: `failure` — Read-back failed on notion.append_audit_row: notion.append_audit_row: amount_cents: expected 2900, live value 29000 (1 of 3 assertion(s) failed). All committed effects were compensated.
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4418; slack: slack:post:refund-order-4418; stripe: stripe:refund:order-4418
- forbidden: compensate attempted on irreversible effect stripe.refund_payment (status=ok)

```bash
python -m readback.evals.run --scenario 11 --profile silent_partial_write --mode readback_on --seed 12604
```

## S11 crash_midrun_then_retry — SILENT FAILURE

- mode: `readback_off`
- fault: `silent_partial_write` @ `notion`
- seed: `12604`  (repeat 4)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES notion: notion:audit:refund-order-4418: amount_cents: expected 2900, found 29000

```bash
python -m readback.evals.run --scenario 11 --profile silent_partial_write --mode readback_off --seed 12604
```

## S11 crash_midrun_then_retry — forbidden effect

- mode: `readback_on`
- fault: `divergent_write` @ `stripe`
- seed: `12700`  (repeat 0)
- reported: `failure` — Read-back failed on stripe.refund_payment: stripe.refund_payment: amount_cents: expected 2900, live value 3200 (1 of 3 assertion(s) failed). All committed effects were compensated.
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4418; slack: slack:post:refund-order-4418; stripe: stripe:refund:order-4418
- forbidden: compensate attempted on irreversible effect stripe.refund_payment (status=ok)

```bash
python -m readback.evals.run --scenario 11 --profile divergent_write --mode readback_on --seed 12700
```

## S11 crash_midrun_then_retry — SILENT FAILURE

- mode: `readback_off`
- fault: `divergent_write` @ `stripe`
- seed: `12700`  (repeat 0)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES stripe: stripe:refund:order-4418: amount_cents: expected 2900, found 3200

```bash
python -m readback.evals.run --scenario 11 --profile divergent_write --mode readback_off --seed 12700
```

## S11 crash_midrun_then_retry — forbidden effect

- mode: `readback_on`
- fault: `divergent_write` @ `notion`
- seed: `12701`  (repeat 1)
- reported: `failure` — Read-back failed on notion.append_audit_row: notion.append_audit_row: amount_cents: expected 2900, live value 3300 (1 of 3 assertion(s) failed). All committed effects were compensated.
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4418; slack: slack:post:refund-order-4418; stripe: stripe:refund:order-4418
- forbidden: compensate attempted on irreversible effect stripe.refund_payment (status=ok)

```bash
python -m readback.evals.run --scenario 11 --profile divergent_write --mode readback_on --seed 12701
```

## S11 crash_midrun_then_retry — SILENT FAILURE

- mode: `readback_off`
- fault: `divergent_write` @ `notion`
- seed: `12701`  (repeat 1)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES notion: notion:audit:refund-order-4418: amount_cents: expected 2900, found 3300

```bash
python -m readback.evals.run --scenario 11 --profile divergent_write --mode readback_off --seed 12701
```

## S11 crash_midrun_then_retry — forbidden effect

- mode: `readback_on`
- fault: `divergent_write` @ `slack`
- seed: `12702`  (repeat 2)
- reported: `failure` — Read-back failed on slack.post_message: slack.post_message: text: expected 'Refunded order 4418 ($29.00). Reason: logged at operator request.', live value 'Refunded order 4418 ($29.00). Reason: logged
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4418; slack: slack:post:refund-order-4418; stripe: stripe:refund:order-4418
- forbidden: compensate attempted on irreversible effect stripe.refund_payment (status=ok)

```bash
python -m readback.evals.run --scenario 11 --profile divergent_write --mode readback_on --seed 12702
```

## S11 crash_midrun_then_retry — SILENT FAILURE

- mode: `readback_off`
- fault: `divergent_write` @ `slack`
- seed: `12702`  (repeat 2)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES slack: slack:post:refund-order-4418: text: expected 'Refunded order 4418 ($29.00). Reason: logged at operator request.', found 'Refunded order 4418 ($29.00). Reason: logged at operator request. [unverified]'

```bash
python -m readback.evals.run --scenario 11 --profile divergent_write --mode readback_off --seed 12702
```

## S11 crash_midrun_then_retry — forbidden effect

- mode: `readback_on`
- fault: `divergent_write` @ `stripe`
- seed: `12703`  (repeat 3)
- reported: `failure` — Read-back failed on stripe.refund_payment: stripe.refund_payment: amount_cents: expected 2900, live value 3500 (1 of 3 assertion(s) failed). All committed effects were compensated.
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4418; slack: slack:post:refund-order-4418; stripe: stripe:refund:order-4418
- forbidden: compensate attempted on irreversible effect stripe.refund_payment (status=ok)

```bash
python -m readback.evals.run --scenario 11 --profile divergent_write --mode readback_on --seed 12703
```

## S11 crash_midrun_then_retry — SILENT FAILURE

- mode: `readback_off`
- fault: `divergent_write` @ `stripe`
- seed: `12703`  (repeat 3)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES stripe: stripe:refund:order-4418: amount_cents: expected 2900, found 3500

```bash
python -m readback.evals.run --scenario 11 --profile divergent_write --mode readback_off --seed 12703
```

## S11 crash_midrun_then_retry — forbidden effect

- mode: `readback_on`
- fault: `divergent_write` @ `slack`
- seed: `12704`  (repeat 4)
- reported: `failure` — Read-back failed on slack.post_message: slack.post_message: text: expected 'Refunded order 4418 ($29.00). Reason: logged at operator request.', live value 'Refunded order 4418 ($29.00). Reason: logged
- oracle: `WRONG` — MISSING notion: notion:audit:refund-order-4418; slack: slack:post:refund-order-4418; stripe: stripe:refund:order-4418
- forbidden: compensate attempted on irreversible effect stripe.refund_payment (status=ok)

```bash
python -m readback.evals.run --scenario 11 --profile divergent_write --mode readback_on --seed 12704
```

## S11 crash_midrun_then_retry — SILENT FAILURE

- mode: `readback_off`
- fault: `divergent_write` @ `slack`
- seed: `12704`  (repeat 4)
- reported: `success` — [readback disabled] All 3 apply call(s) returned ok. No live state was re-read; this is the provider's word, not evidence.
- oracle: `WRONG` — WRONG VALUES slack: slack:post:refund-order-4418: text: expected 'Refunded order 4418 ($29.00). Reason: logged at operator request.', found 'Refunded order 4418 ($29.00). Reason: logged at operator request. [unverified]'

```bash
python -m readback.evals.run --scenario 11 --profile divergent_write --mode readback_off --seed 12704
```
