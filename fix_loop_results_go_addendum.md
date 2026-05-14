# Go fix-me loop — results (2026-05-14)

Append the table below into `fix_loop_results.md` once timings are confirmed.

## Approach

All thread fixes were applied via the **Fix in Cursor** UI flow on the PR inline comments, then bundled into one fix commit per PR rather than per-thread commits. This is a methodology deviation from the Rexec runbook in `Plan.MD:33-62` — granularity of per-thread reconstruction is lost, but per-thread timing was tracked separately during the loop.

- Uber-Eats fix commit: `658710d` — "fix: address PR review — drop hardcoded Stripe key, fail orders on pre-auth error, redact PII from audit logs"
- Rate-Limiter fix commit: `b3c4dc0` — "fix: address PR review findings on admin auth, policy lifecycle, and limiter math"

## Per-thread timings

> Fill the three numeric columns from your notes. Leave `?` for any you didn't capture.

| # | Repo | Defect ID | Inline thread URL | UI click → toolchain clean | Accepted CodeAnt fix as-is? | Notes |
|---|------|-----------|-------------------|----------------------------|----------------------------|-------|
| 1 | Uber-Eats | U1 (Stripe key) | https://github.com/vickky06/Uber-Eats/pull/1#discussion_r3240199930 | _Nm Ns_ | Y/N | |
| 2 | Uber-Eats | U2 (PII log) | https://github.com/vickky06/Uber-Eats/pull/1#discussion_r3240201966 | _Nm Ns_ | Y/N | |
| 3 | Uber-Eats | BONUS (chargeOrder error) | https://github.com/vickky06/Uber-Eats/pull/1#discussion_r3240201973 | _Nm Ns_ | Y/N | |
| 4 | Rate-Limiter | RL1 (Admin key) | https://github.com/vickky06/Rate-Limiter/pull/1#discussion_r3240185284 | _Nm Ns_ | Y/N | |
| 5 | Rate-Limiter | RL2 (header leak) | https://github.com/vickky06/Rate-Limiter/pull/1#discussion_r3240185985 | _Nm Ns_ | Y/N | |
| 6 | Rate-Limiter | RL4 (goroutine leak) | https://github.com/vickky06/Rate-Limiter/pull/1#discussion_r3240184533 | _Nm Ns_ | Y/N | |
| 7 | Rate-Limiter | RL5 (off-by-one) | https://github.com/vickky06/Rate-Limiter/pull/1#discussion_r3232323200 (approx) | _Nm Ns_ | Y/N | |
| 8 | Rate-Limiter | RL6 (factory error swallow) | (boot path + update path threads) | _Nm Ns_ | Y/N | |

## Verification on each fix commit

Both fix commits verified clean before push:

```text
uber-eats:    go build ./... PASS, go vet ./... PASS, go test ./... PASS
rate-limiter: go build ./... PASS, go vet ./... PASS, go test ./... PASS
```

## Aggregates (fill from the table above)

| Metric | Value |
|---|---|
| Threads addressed | 8 |
| Median wall-clock per thread | _Nm Ns_ |
| Threads accepted as-is (no manual edit) | _N/8_ |
| Threads requiring manual rewrite of CodeAnt suggestion | _N/8_ |
| Toolchain failures during the loop | _N_ |
| Adoption-band per [Go-Fix-Loop-Runbook.md] (<60s preferred, 1–3m tolerable, >5m kills adoption) | _band_ |

## Notable observations during the loop

- _e.g. CodeAnt's RL4 suggested fix included the per-client monitor map AND the stop-channel cleanup correctly — accepted as-is_
- _e.g. U1's "Fix in Cursor" template suggested env-var fallback, didn't include fail-fast; manually added the empty-string guard_
- _e.g. RL5 fix landed in two files (SlidingWindow.go + strategies_test.go); CodeAnt's prompt covered the impl but not the test reversion_

## What this measurement gives the NetApp writeup

Once filled, this table answers: **"How much developer time does each CodeAnt finding cost to act on, and at what fraction of CodeAnt suggestions does the developer accept verbatim?"** Both are gating considerations for adoption that pure recall/precision numbers don't surface.
