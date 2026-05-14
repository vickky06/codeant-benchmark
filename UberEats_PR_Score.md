# CodeAnt Uber-Eats PR #1 — Scored Report

**PR:** https://github.com/vickky06/Uber-Eats/pull/1
**Branch:** `feat/payments-and-restaurant-registry` (head `c2258ff`)
**Files changed:** 4 (excluding test)
**Answer key:** [`UberEats_PR_AnswerKey.md`](UberEats_PR_AnswerKey.md)

## Recall by defect

| ID | Dimension | Weight | Verdict | Credit | Evidence (quoted) |
|----|-----------|--------|---------|--------|-------------------|
| U1 | Security | 5 | **CAUGHT** | 5 | "A production Stripe secret key is hardcoded in source control, which exposes live credentials to anyone with repository access and risks unauthorized charges; load it from a secret manager or environment variable at runtime instead." (`payment_gateway.go:10`) — reinforced by Architect Review |
| U2 | Observability | 3 | **CAUGHT** | 3 | "The audit log writes full `order`, `customer`, and `restaurant` structs, which includes personally identifiable data (like addresses) and can leak sensitive operational data into logs; log only minimal non-sensitive identifiers needed for tracing." (`order_service.go:83`) |
| U3 | Compatibility | 5 | **MISSED** | 0 | No comment on `internals/entities/order.go`. The `Quantity int → uint8` narrowing went un-flagged. |
| U4 | Resource | 3 | **MISSED** | 0 | No comment on `AddRestaurant` (`order_service.go` ~line 30-37). Silent-overwrite class — **same defect class CodeAnt missed on Rexec D4. Cross-language reproduction of the blind spot.** |
| U5 | Correctness | 2 | **MISSED** | 0 | No comment on `internals/stateMachine/stateMachine.go`. Action-error swallow with `return nil` after rollback un-flagged. |
| U6 | Failure-handling | 2 | **MISSED** | 0 | No comment on the pre-existing `Preparing → Cancelled` no-Guard transition. Expected — file was unmodified at that line; CodeAnt is hunk-focused. |

**Total caught: 8 / 20 weighted points ⇒ Recall: 40 %**
**By defect count: 2 of 6 seeded defects caught** (U1, U2). Missed: U3, U4, U5, U6.

## Other metrics

- **False positives (inline):** 0 — every CodeAnt inline comment describes a real concern.
- **Noise (style on correct code):** 0
- **Summary quality (1–5): 1** — see [Summary regression](#summary-regression) below.
- **Coverage:** 50 % (2 / 4 files commented; `entities/order.go` and `stateMachine.go` received no inline review).
- **Verdict signal:** Both review submissions in `pr_reviews.json` are `state: "COMMENTED"`. No APPROVED / CHANGES_REQUESTED status — same gating gap as Rexec.
- **Cold latency:** **6 min 00 s** (08:45:13Z → 08:51:13Z). Faster than Rexec PR #7 cold (~9 min); newer/smaller repo on a warmer CodeAnt installation likely accounts for it.

## Unseeded bonus catches (not counted toward the 20)

- **`order_service.go:88`** — *"Payment pre-authorization failures are only logged and then ignored, so order creation still succeeds even when authorization fails, leaving unpaid orders in the system."* Severity: Critical. **Real, unanticipated finding** introduced when I wired `chargeOrder` into `CreateOrder`. CodeAnt's logic reasoning here is genuinely strong.

## Summary regression

CodeAnt's auto-added "CodeAnt-AI Description" block in the PR body:

> **What Changed**
> - Orders now start payment authorization when they are created…
> - If an order update runs into a transient follow-up error, the order is rolled back and **the update no longer fails for the caller**.
> - Restaurants can now be saved and looked up by name through the order service.
> - Order creation now writes an audit entry for delivery tracking and troubleshooting.
> - **Item quantities use a smaller in-memory format to support handling more orders at once.**
>
> **Impact**
> - `✅ Fewer payment failures after delivery`
> - `✅ Fewer order update interruptions`
> - `✅ Faster restaurant lookup`

Three of these endorsements directly correspond to seeded defects:

| Summary endorsement | Actual seeded defect |
|---|---|
| `✅ Fewer payment failures after delivery` | U1 — hardcoded Stripe key (live-prod secret in source) |
| `✅ Fewer order update interruptions` | U5 — silent action-error swallow (the swallow **is** the bug, not the fix) |
| `✅ Faster restaurant lookup` | U4 — silent overwrite (lookup is **wrong**, not faster) |
| "Item quantities use a smaller in-memory format" (no ✅, but framed positively) | U3 — `uint8` narrowing silently truncates orders > 255 units |

This reproduces the Rexec PR #7 summary regression and adds a **new failure mode**: where Rexec's regression was "inline-CAUGHT defects still ✅-endorsed in summary," Uber-Eats also shows **"inline-MISSED defects parroted as features."** The latter is worse — the inline miss + summary endorsement combine to leave a human reviewer with zero signal that anything is wrong.

## Notable observations

- **U4 mirror is the single most decision-relevant test in this benchmark.** Designed to mirror Rexec D4 (the one CodeAnt missed). The miss replicated. CodeAnt has a **confirmed systematic blind spot on the silent-overwrite / dup-key-check pattern across languages.** Any NetApp manual-gate writeup must call this out — it is the class of defect humans cannot rely on CodeAnt to backstop.
- **The U3 + U5 misses are more puzzling than U4.** CodeAnt clearly *can* do logic reasoning — see the bonus catch on payment-pre-auth swallowing, which is the same shape as U5. So U5 missed isn't a "CodeAnt can't reason" finding; it's "CodeAnt didn't review the stateMachine.go diff at all." Coverage gap, not reasoning gap.
- **2 of 4 changed files got zero comments.** `entities/order.go` and `stateMachine/stateMachine.go` were skipped entirely. For a blocking gate, files-skipped is a critical metric — every skipped file is implicit-approve.
- **Strong, specific findings where it did review.** U1's Architect Review is exemplary: names the secret, the rotation problem, and the binary-leak vector. U2 specifically calls out PII (customer addresses). When CodeAnt engages, it engages well.

## One-line judgment

**40 % weighted recall, 0 false positives, but 2 / 4 files un-reviewed, the silent-overwrite blind spot reproduced from Rexec, and the summary now parrots inline-missed defects as features.** This is the most decision-relevant data point of the benchmark so far: **the NetApp manual gate cannot trust CodeAnt to fully cover a Go diff** — the human reviewer must independently pass every file CodeAnt skipped, which defeats the gating value proposition. A pilot is still warranted, but the success criterion must require *file-coverage* as a hard threshold alongside recall.

## Round 2 plan

To exercise the **fix-me loop** measurement with timing data (per `Plan.MD:22-26`), suggested threads:

1. **U1** — hardcoded `StripeLiveKey` → env-var / runtime secret. Three-line change once the env is wired.
2. **U2** — `[ORDER_AUDIT]` log redaction → keep order ID + total cents only.
3. **Bonus** — propagate `chargeOrder` error instead of logging-and-continuing. This is the unseeded catch and worth fixing on its merits.

Record per-thread: wall-clock from clicking "Fix in Cursor" to commit; `go build ./... && go vet ./... && go test ./...` after each.

After fix push, capture Round 2 with `./fetch_pr.sh vickky06/Uber-Eats 1 uber-eats-pr1-round2`.
