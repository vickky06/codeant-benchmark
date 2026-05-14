# CodeAnt Benchmarking — Uber-Eats Answer Key

**PR URL:** _<fill in after PR is opened>_
**Opened at (ISO-8601 UTC):** _<fill in after PR is opened>_
**Repo:** `vickky06/Uber-Eats`
**Branch:** `feat/payments-and-restaurant-registry`
**Baseline:** Go 1.24, `go test ./...` passes on PR head.
**Total weighted defect points available:** 20

This corpus is the Go counterpart to [`Rexec_PR1_AnswerKey.md`](Rexec_PR1_AnswerKey.md). Defect classes mirror Rexec D1–D6 so cross-language behavior can be compared.

## Seeded defects

| ID | File | Defect | Dimension | Severity (weight) | Bot must mention |
|----|------|--------|-----------|--------------------|-------------------|
| U1 | `internals/service/payment_gateway.go` | `StripeLiveKey` hardcoded production Stripe secret used as `Authorization: Bearer …` | Security | Critical (5) | hardcoded credential / secret in source / rotate exposed token |
| U2 | `internals/service/order_service.go` (CreateOrder) | `log.Printf("[ORDER_AUDIT] created order=%+v customer=%+v restaurant=%+v", …)` dumps PII (customer name+address) and full order body | Observability | High (3) | sensitive data in logs / PII / no redaction |
| U3 | `internals/entities/order.go` | `type Quantity uint8` narrowed from `int` — silently truncates / overflows orders with >255 units; API contract change | Compatibility | Critical (5) | integer narrowing / contract change / silent truncation / API stability |
| U4 | `internals/service/order_service.go` (AddRestaurant) | `s.restaurants[r.Name] = r` with no `if _, ok := s.restaurants[r.Name]; ok` guard — silently overwrites previous registration on duplicate name | Resource | High (3) | silent overwrite / dup-key check missing / orphan reference |
| U5 | `internals/stateMachine/stateMachine.go` (Apply) | After `Action` returns error, `o.SetStatus(from)` then `return nil` — callers think transition succeeded; the error is swallowed | Correctness | Medium (2) | error swallowed / silent failure / caller misled |
| U6 | `internals/stateMachine/stateMachine.go` (Preparing → Cancelled) | Transition has **no Guard** while every other Cancel path checks actor — any caller can cancel a Preparing order regardless of role | Failure-handling | Medium (2) | missing authorization / actor guard / inconsistent enforcement |

**U6 is unmodified existing code.** The seeded PR touches `stateMachine.go` (for U5) but does not change the `Preparing → Cancelled` transition. U6 therefore measures whether CodeAnt reviews holistically (full file context) or hunk-only.

## Bonus unseeded defects (not counted toward the 20 points)

These exist on `main` and through this PR. Track separately as **unseeded recall** — equivalent to Rexec's "extra finding" beyond the answer key.

| Bonus | File:Line | Defect |
|---|---|---|
| B1 | `internals/entities/order.go:57` | `DistanceBasedFee.CalculateDeliveryFee` uses `int64(distanceKm) * d.PerKmFeeInCents` — truncates fractional km silently (5.7 km billed as 5 km). Real money-loss bug. |
| B2 | `internals/entities/order.go:95-96` | `GetStatus` / `SetStatus` read/write `o.status` without holding `o.mu`. Lock contract relies on every caller already holding the mutex — fragile, unenforced. |
| B3 | `internals/service/order_service.go:67-69` (post-seeding) | `Transition` releases RLock before passing the order pointer to `sm.Apply`. If the entry is deleted between the read and the apply, we still operate on the freed pointer (Go GC keeps it alive, but the order is no longer in the service map). |

## Scoring rules

- **CAUGHT (full weight)**: CodeAnt's review explicitly identifies the problem (not "this file changed"). Quote must include the keywords in "Bot must mention" or a semantic equivalent.
- **PARTIAL (50%)**: Comment flags the right file/region but misses the specific issue.
- **MISSED (0)**: No relevant comment.
- **Recall %** = sum(weights of CAUGHT) / 20 × 100.

## Track separately (do **not** fold into recall)

- **False positives:** comments claiming defects that don't exist.
- **Noise:** stylistic/preferential suggestions on correct code.
- **Summary quality (1–5):** does the bot's PR summary match intent without inventing risks **or laundering the seeded defects as ✅ improvements** (Rexec PR1 regression — track explicitly).
- **Verdict signal:** did CodeAnt publish a machine-readable pass/fail status or only `state: COMMENTED`?
- **Time-to-verdict:** minutes from PR open → "finished reviewing".
- **Coverage:** distinct files commented / files changed.
- **Unseeded recall:** how many of B1–B3 did CodeAnt flag without being in the answer-key set.

## Manual-gate operational rule (proposed)

For the NetApp manual blocking gate, treat **U1, U3** (both Critical weight 5) as **must-flag-or-block** — if CodeAnt does not raise either as Critical inline, the human reviewer is not freed to skip their own pass. Document the rule before the pilot starts.

## Fix-me loop targets

When running the **UI-driven "Fix in Cursor"** loop (per `Plan.MD` Remaining), exercise these three threads first (highest signal):

1. **U1** — hardcoded Stripe key → env-var / secret manager.
2. **U3** — restore `Quantity int` (or document the contract narrowing if intentional).
3. **U5** — restore the `fmt.Errorf("action failed, rolled back: %w", err)` propagation.

After each fix: `go build ./... && go vet ./... && go test ./...` must still pass.
