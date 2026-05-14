# Go corpus design — dual-arm benchmark for NetApp manual gate

Companion to the Rust (Rexec) arm. Adds Go coverage because the NetApp blocking-gate use case is for **Go control-plane + Java web** code, neither of which the Rust arm exercises.

## Why dual

The two repos are deliberately complementary:

| Repo | Surface | Defect classes exercised |
|------|---------|---------------------------|
| `vickky06/Uber-Eats` | Order service, actor-aware state machine, money in `int64` cents, sync.RWMutex, domain model | Hardcoded secret, PII in logs, integer narrowing, silent overwrite (dup-key), action error swallow, **actor-authorization gap (unseeded)** |
| `vickky06/Rate-Limiter` | HTTP middleware, admin endpoint, JSON request body, three rate-limit strategies, time math, ticker-driven control | Hardcoded admin secret, header logging leak, wire-breaking header rename, **goroutine leak**, off-by-one boundary, error swallow on admin path |

Neither repo alone covers what the NetApp manual gate needs to catch. Together they exercise: secret handling, PII in logs, API/wire compatibility, resource leaks (goroutine + map), concurrency contracts, error-handling antipatterns, authorization gaps in state machines, and HTTP/middleware-layer auth.

## Scope decisions

- **Why not just rate-limiter:** no domain model, no state machine, no money math. Misses an entire class of NetApp-style logic-correctness defects.
- **Why not just uber-eats:** no HTTP, no auth header, no admin endpoint. Misses the entire middleware-layer attack surface.
- **Why not RideSharingApp:** overlaps with uber-eats on state machine; reserved for a potential third arm if "unbounded goroutine fan-out" needs its own test.
- **Why not Lru-Cache:** too small (324 LOC) for a 6-defect PR but **excellent for unseeded-recall measurement** — open a trivial doc PR and observe what CodeAnt surfaces against the 6 known existing defects (see Memory note). Use as a free third data point.

## Answer keys

- [`UberEats_PR_AnswerKey.md`](../UberEats_PR_AnswerKey.md) — U1–U6 (20 points) + bonus B1–B3 unseeded.
- [`RateLimiter_PR_AnswerKey.md`](../RateLimiter_PR_AnswerKey.md) — RL1–RL6 (20 points) + bonus B1–B3 unseeded.

Both mirror the Rexec D1–D6 taxonomy so cross-language behavior is comparable.

## What this benchmark proves vs what it doesn't

**Will prove** (with these two PRs):
- Recall on Go security/observability/compatibility/resource/correctness defects.
- Whether the **Rexec D4 miss** (silent overwrite) replicates on Go — U4 mirrors it exactly. **Most decision-relevant single test.**
- Whether CodeAnt's **summary regression** (Rexec PR1: ✅ on seeded defects) reproduces on Go cover-story PRs.
- Whether CodeAnt reviews **holistically vs hunk-only** — U6 lives in unchanged code.

**Will not prove** (deferred):
- Generalization to NetApp's actual codebase (sample size still small).
- Java behavior (not in scope here; would require a third corpus).
- Marginal recall over baseline tools (`golangci-lint`, `gosec`, `staticcheck`) — see "Next steps" below.
- Historical-replay recall on bugs that escaped human review (would require a Go repo with merged PRs + post-merge bugfixes).

## Next steps in priority order

1. **Open the two PRs.** Both branches are committed locally; push and open via `gh pr create`. Each will trigger one CodeAnt review.
2. **Score against the answer keys.** Reuse `score_pr1.py` with file paths swapped (rename to `prepare_score_template.py` per Rexec review notes).
3. **Run the baseline arm.** Same PR diffs through `golangci-lint run --enable-all` and `gosec ./...`. Subtract baseline catches from CodeAnt's recall to get **marginal** recall.
4. **Manual-gate operational definition.** Write one sentence: "human reviewer self-assigns only when CodeAnt's review contains zero `Critical` inline comments and ≤ N `Major`." Test the rule against U1/U3/RL1/RL3 — would the gate have blocked?
5. **Summary-regression check.** Score `summary quality (1–5)` explicitly on both PRs against the "PR body bullet → defect framed as feature" tables in each answer key.
6. **Bitbucket pilot prerequisite check.** Confirm in writing whether CodeAnt exposes a Bitbucket commit-status / required check that branch protection can require. Manual gate does not need this, but documenting the gap is decision-grade information.

## What is **not** in this corpus by design

- No tests for the seeded defects themselves — fix-me loop validates that fixes don't break the **baseline** tests on `main`. Adding tests for the seeded behaviors would over-engineer the harness.
- No CI on the new PRs initially — adding GitHub Actions would conflate CodeAnt's findings with linter findings. Run the baseline arm offline against the same diff to isolate signals.
- No CodeAnt "Fix in Cursor" yet — runs after the first review pass; per-thread timing is recorded in `fix_loop_results.md` per `Plan.MD:22-26`.
