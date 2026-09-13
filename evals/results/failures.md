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
