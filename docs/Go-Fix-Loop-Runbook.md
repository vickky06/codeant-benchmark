# Go fix-me loop — execution runbook

UI-driven Fix-in-Cursor pass on the two Go PRs, mirroring the Rexec runbook in `Plan.MD:33-62`. Captures per-thread wall-clock, manual-edit fraction, and toolchain pass/fail.

## Selected threads (top 3 per PR by severity)

### Uber-Eats PR #1 — `vickky06/Uber-Eats` head `c2258ff`

| # | ID | File:Line | Class | Expected fix | Inline URL |
|---|----|-----------|-------|--------------|------------|
| 1 | U1 | `internals/service/payment_gateway.go:10` | Security | Replace hardcoded `StripeLiveKey` with `os.Getenv("STRIPE_LIVE_KEY")` loaded once; fail-fast if empty | https://github.com/vickky06/Uber-Eats/pull/1#discussion_r3240199930 |
| 2 | U2 | `internals/service/order_service.go:83` | Observability | Redact PII in `[ORDER_AUDIT]`: keep `order.Id`, `order.TotalPrice`, `customer.Id`, `restaurant.Id` (or name only) — drop addresses, full order body | https://github.com/vickky06/Uber-Eats/pull/1#discussion_r3240201966 |
| 3 | BONUS | `internals/service/order_service.go:88` | Correctness | Propagate `chargeOrder` error from `CreateOrder` (or mark order as failed) — do not log-and-continue | https://github.com/vickky06/Uber-Eats/pull/1#discussion_r3240201973 |

### Rate-Limiter PR #1 — `vickky06/Rate-Limiter` head `b001bc3`

| # | ID | File:Line | Class | Expected fix | Inline URL |
|---|----|-----------|-------|--------------|------------|
| 4 | RL1 | `internal/middleware/admin_auth.go:6` | Security | Replace `AdminAPIKey` constant with runtime config; use `subtle.ConstantTimeCompare` instead of `!=` | https://github.com/vickky06/Rate-Limiter/pull/1#discussion_r3240185284 |
| 5 | RL2 | `internal/middleware/ratelimiter.go:23` | Observability | Drop `r.Header` from log; keep `r.Method`, `r.URL.Path`, optional client-id (only if non-secret) | https://github.com/vickky06/Rate-Limiter/pull/1#discussion_r3240185985 |
| 6 | RL4 | `internal/store/client_store.go:63` | Resource | Track per-client monitor via `map[string]chan struct{}`; close existing on update; clean up on remove/shutdown | https://github.com/vickky06/Rate-Limiter/pull/1#discussion_r3240184533 |

## Per-thread procedure

For each of the 6 threads:

1. **Note clock-in time** (`date -Iseconds`) — the moment you click **Fix in Cursor** on the GitHub inline comment.
2. **Apply** in Cursor. **Read the suggested diff** before accepting. Note whether you accepted as-is or edited.
3. **Commit** with a message referencing the thread id and CodeAnt comment id, e.g.:
   ```
   fix: U2 redact PII from ORDER_AUDIT (CodeAnt r3240201966)
   ```
4. **Verify** — these must all pass:
   ```bash
   go build ./...
   go vet ./...
   go test ./...
   ```
   For uber-eats: `cd /Users/viveksingh/Repositories/GO/Rest-Projects/uber-eats`
   For rate-limiter: `cd /Users/viveksingh/Repositories/GO/Rest-Projects/rate-limiter`
5. **Note clock-out time** — moment the toolchain commands all return 0.
6. **Record** the row in `fix_loop_results.md` (template below).

## Branch strategy

Do **not** push fixes to the open PR branches yet (`feat/payments-and-restaurant-registry` / `feat/observability-and-policy-rotation`). Push triggers CodeAnt's incremental review — capture Round 1 first, run the fix loop on a **throwaway local branch** off each PR head, then optionally push to trigger Round 2.

```bash
# Uber-Eats
cd /Users/viveksingh/Repositories/GO/Rest-Projects/uber-eats
git fetch origin
git checkout -b throwaway/fix-me-ui-uber-eats origin/feat/payments-and-restaurant-registry

# Rate-Limiter
cd /Users/viveksingh/Repositories/GO/Rest-Projects/rate-limiter
git fetch origin
git checkout -b throwaway/fix-me-ui-rate-limiter origin/feat/observability-and-policy-rotation
```

After all 3 fixes per repo land + verify, optionally push to the PR branch to trigger Round 2:

```bash
# only if you want a Round 2 incremental review for benchmark data
git push origin throwaway/fix-me-ui-uber-eats:feat/payments-and-restaurant-registry
```

## What to record (template — paste into `fix_loop_results.md`)

```markdown
## Go fix-me loop — UI-driven (2026-05-14)

| # | ID | UI-clicked | Toolchain-clean | Wall-clock | Accepted as-is | Notes |
|---|----|-----------|------------------|------------|----------------|-------|
| 1 | U1  | YYYY-MM-DDTHH:MM:SSZ | YYYY-MM-DDTHH:MM:SSZ | _Nm Ns_ | Y/N | |
| 2 | U2  | …                    | …                    | …        | Y/N | |
| 3 | BON | …                    | …                    | …        | Y/N | |
| 4 | RL1 | …                    | …                    | …        | Y/N | |
| 5 | RL2 | …                    | …                    | …        | Y/N | |
| 6 | RL4 | …                    | …                    | …        | Y/N | |

### Aggregates
- Median wall-clock per thread: _N min_
- P95 wall-clock per thread: _N min_
- Fraction accepted as-is (no manual edit): _N/6_
- Toolchain-failed (any of build/vet/test) on first try: _N/6_

### Notable observations
- _e.g. RL4's suggested fix did/didn't include cleanup of the map on Remove_
- _e.g. U2's redaction kept more fields than minimal — manually trimmed_
- _e.g. The Fix-in-Cursor prompt template is identical across threads (see PR1_CodeAnt_Score.md addendum)_
```

## After all 6 threads

1. Optionally push throwaway branches to PR heads to capture Round 2 incremental reviews:
   ```bash
   ./fetch_pr.sh vickky06/Uber-Eats 1 uber-eats-pr1-round2
   ./fetch_pr.sh vickky06/Rate-Limiter 1 rate-limiter-pr1-round2
   ```
2. Append the filled-in table to `fix_loop_results.md`.
3. Update `Plan.MD:26` from `[ ]` to `[x]` (the UI-driven loop checkbox).
4. Cross-link the score docs:
   - `UberEats_PR_Score.md` — add a "Round 2 / Fix loop" section like `PR1_CodeAnt_Score.md`.
   - `RateLimiter_PR_Score.md` — same.

## What this measurement gives the NetApp writeup

The numbers from the table answer the question your manual gate writeup cannot answer otherwise: **"How much developer time does a CodeAnt finding cost to act on?"** Without this data, you can claim recall and precision but not developer-experience cost — which is the gating consideration for adoption.

Per-thread wall-clock targets (anecdotal, from internal sources on similar tools):
- **<60 s/thread**: developers actively prefer the workflow.
- **1–3 min/thread**: tolerable, like a slow CI check.
- **>5 min/thread**: workflow dies politically inside one sprint.

If median wall-clock comes out >3 min on this small sample, that is a stronger argument against the gate than any recall number.
