# CodeAnt Benchmarking — Rate-Limiter Answer Key

**PR URL:** _<fill in after PR is opened>_
**Opened at (ISO-8601 UTC):** _<fill in after PR is opened>_
**Repo:** `vickky06/Rate-Limiter`
**Branch:** `feat/observability-and-policy-rotation`
**Baseline:** Go 1.24, `go test ./...` passes on PR head.
**Total weighted defect points available:** 20

Companion arm to [`UberEats_PR_AnswerKey.md`](UberEats_PR_AnswerKey.md). Same defect-class taxonomy, exercised against the HTTP / middleware / authn surface that uber-eats lacks.

## Seeded defects

| ID | File | Defect | Dimension | Severity (weight) | Bot must mention |
|----|------|--------|-----------|--------------------|-------------------|
| RL1 | `internal/middleware/admin_auth.go` | `AdminAPIKey` hardcoded shared admin secret used as `X-Admin-Key` gate on `/admin/*` | Security | Critical (5) | hardcoded credential / secret in source / rotation requires code change |
| RL2 | `internal/middleware/ratelimiter.go` (RateLimit) | `log.Printf("[REQ] %s %s headers=%+v", …)` dumps the full request headers including `X-Client-ID` (and any `Authorization` / `Cookie` headers callers send) | Observability | High (3) | sensitive headers in logs / auth header leak / no redaction |
| RL3 | `internal/middleware/ratelimiter.go` | `ClientIDHeader` renamed `"X-API-Key"` → `"X-Client-ID"` — wire-breaking for every existing client without a compatibility shim | Compatibility | Critical (5) | wire-breaking header change / API contract / backward compat / dual-read shim |
| RL4 | `internal/store/client_store.go` (UpdateLimiter) | Per call, `go func(){ for range t.C { … } }(cfg.ClientID)` is launched and never stopped — a fresh goroutine + ticker leaks on every admin update | Resource | High (3) | goroutine leak / unbounded growth / no shutdown channel |
| RL5 | `internal/rateLimitingStrategy/SlidingWindow.go` | `<=` flipped to `<` in `int64(weight)+1 < sw.maxRequests` — request landing exactly at limit now blocks (off-by-one); test updated to mask the change | Correctness | Medium (2) | off-by-one / boundary semantics / rate-limit math |
| RL6 | `internal/store/client_store.go` (UpdateLimiter, NewClientStore) | Factory errors are logged and swallowed; `UpdateLimiter` returns `nil`, `NewClientStore` continues. Admin caller sees success; invalid policy silently ignored | Failure-handling | Medium (2) | error swallowed / silent failure / config rejection lost |

## Bonus unseeded defects (not counted toward the 20 points)

These exist on `main` and remain through this PR. Track separately as unseeded recall.

| Bonus | File:Line | Defect |
|---|---|---|
| B1 | `internal/middleware/ratelimiter.go:17` | `if r.URL.Path == "/health"` — exact-match bypass. `/health/`, `/HEALTH`, `/health?x=1` all skip rate-limit. Real bypass class. |
| B2 | `internal/middleware/admin.go` (pre-seeding state) | The admin endpoint had **zero** authentication. RL1 introduces auth via hardcoded key, partially closing the gap — track whether CodeAnt notes that the auth itself is hardcoded **and** that the pre-existing endpoint was unauthenticated. |
| B3 | `internal/store/client_store.go` (UpdateLimiter, post-seeding) | A request that fetched the old limiter via `GetLimiter` then calls `Allow()` on the stale limiter after admin swaps it — in-flight handover race. Likely benign in this codebase; document as a class. |

## Scoring rules

Same as `UberEats_PR_AnswerKey.md`: CAUGHT (full), PARTIAL (½), MISSED (0). Recall = caught_weight / 20 × 100. False-positives, noise, summary quality, verdict signal, latency, coverage, unseeded recall tracked separately.

## Adversarial framing in the PR

This PR's body is written as a plausible feature/observability/cleanup batch — mirroring Rexec PR #7's cover-story behavior. Each bullet doubles as a defect:

| PR body bullet | Defect framed as feature |
|---|---|
| "Gate `/admin/*` behind a shared admin key" | RL1 — hardcoded secret |
| "Per-request log line for SRE observability" | RL2 — header leak |
| "Standardize client identification header" | RL3 — wire break |
| "Tighten SlidingWindow boundary semantics" | RL5 — off-by-one |
| "Per-policy window-monitor goroutine" | RL4 — goroutine leak |
| "Best-effort UpdateLimiter / NewClientStore" | RL6 — error swallow |

Use this table when scoring **summary quality**: if CodeAnt's summary repeats any of the left-column phrasing without raising the right-column concern, that is a regression of the Rexec PR1 pattern (`PR1_CodeAnt_Score.md:22, 33`).

## Manual-gate operational rule (proposed)

For the NetApp manual gate, treat **RL1** (hardcoded admin secret) and **RL3** (wire-breaking header rename) as **must-flag-or-block**. RL3 in particular is the kind of defect where a missing CodeAnt callout sets up a production incident: every X-API-Key client breaks at deploy time.

## Fix-me loop targets

Highest-signal threads for the "Fix in Cursor" measurement pass:

1. **RL1** — hardcoded `AdminAPIKey` → env var / secret manager + constant-time compare.
2. **RL3** — restore `X-API-Key` (or add a dual-read shim for one release).
3. **RL4** — add a `stop chan struct{}` to `ClientStore`, close it on shutdown, and `select` against it in the monitor goroutine.

Verification after each batch: `go build ./... && go vet ./... && go test ./...` must pass.
