# Go fix-me loop — results (2026-05-14)

Append into `fix_loop_results.md`.

## Methodology note (important)

The runbook in `docs/Go-Fix-Loop-Runbook.md` prescribed the **UI-driven Fix-in-Cursor** workflow — click the inline-comment button, accept/edit CodeAnt's IDE diff, record per-thread wall-clock. **This was not the workflow used.** The actual fixes were drafted with a Claude assistant outside the CodeAnt product surface, then committed as one bundled commit per PR.

What this gives us:
- **Fix-correctness data** — does each CodeAnt finding translate into an actionable, correct fix? (Yes, measured below.)

What this does **not** give us:
- **CodeAnt's "Fix in Cursor" suggestion quality** — never exercised.
- **Per-thread UI-driven wall-clock** — no apples-to-apples comparison against the adoption-band thresholds (<60 s preferred, >5 min kills) in the runbook.
- **The "accepted CodeAnt fix as-is vs edited" fraction** — not applicable when Claude generated the diffs.

A separate pass using Cursor's "Fix in Cursor" button on the seeded PRs is still required before the NetApp writeup can make any claim about developer-experience cost.

## Fix coverage table

For each CodeAnt Round-1 finding (8 total CAUGHT across both PRs), did the fix commit actually address it, and is the fix correct?

| # | Repo | Defect | CodeAnt's suggestion (paraphrased) | Fix in commit | Verdict |
|---|------|--------|------------------------------------|---------------|---------|
| 1 | Uber-Eats | U1 — hardcoded `StripeLiveKey` | Load from runtime secret manager/env | Removed const; `os.Getenv("STRIPE_SECRET_KEY")` + fail-fast on empty | **Addressed (+ defense-in-depth: fail-fast)** |
| 2 | Uber-Eats | U2 — PII in `[ORDER_AUDIT]` log | Log minimal non-sensitive identifiers | Format string changed from `%+v` (full structs) to `%s` for `order.Id`, `customer.Id`, `restaurant.Id` only | **Addressed (clean minimal)** |
| 3 | Uber-Eats | BONUS — `chargeOrder` error swallowed | Propagate / fail order on pre-auth failure | Moved `chargeOrder` **before** map insert; returns `fmt.Errorf("payment pre-authorization failed: %w", err)` on failure | **Addressed (+ improvement: prevents orphan map entry)** |
| 4 | Rate-Limiter | RL1 — hardcoded `AdminAPIKey` const | Load from secure runtime config | `const` → `var AdminAPIKey = os.Getenv("ADMIN_API_KEY")`. Plus `AdminAPIKey == ""` guard in `UpdateStrategy` | **Addressed (+ defense-in-depth: empty-key rejection)** |
| 5 | Rate-Limiter | RL2 — full request headers logged | Redact sensitive headers or allowlist | Added `sensitiveHeaders` set + `redactHeaders()` helper; logs go through `redactHeaders(r.Header)` | **Addressed (clean denylist with `[REDACTED]` token)** |
| 6 | Rate-Limiter | RL4 — UpdateLimiter ticker goroutine leak | Track per-client monitor; cancel previous on update | Added `monitors map[string]chan struct{}` field. Closes previous monitor before installing new one. Goroutine `select`s on done channel | **Addressed (mirrors CodeAnt's suggestion almost line-for-line)** |
| 7 | Rate-Limiter | RL5 — `<=` flipped to `<` (off-by-one) | Restore `<=` so limit is inclusive | Boundary check reverted to `int64(weight)+1 <= sw.maxRequests`. Test also reverted (3-of-3 expectation restored) | **Addressed** |
| 8 | Rate-Limiter | RL6 — factory errors swallowed in both `NewClientStore` and `UpdateLimiter` | Return the validation error; surface bad config to operator | Both paths now return `fmt.Errorf(...)`. Plus `WindowSize <= 0` validation added (addresses the unseeded `NewTicker`-panic bonus catch) | **Addressed (+ both seeded paths + the bonus)** |

## Aggregates

| Metric | Value |
|---|---|
| CodeAnt-flagged findings addressed by the fix commits | **8 / 8** (plus 4 on Ride-Sharing = 12 total across 3 PRs) |
| Fix-correctness (matches CodeAnt's recommendation, compiles, tests pass) | **12 / 12** |
| Fixes that exceed CodeAnt's suggestion with defense-in-depth | **4 / 12** (U1 fail-fast, U-BONUS map-insert ordering, RL1 empty-key guard, RL6 + NewTicker validation) |
| Toolchain failures during the loop | **0** — all 3 fix commits show `go build / go vet / go test / go test -race` clean |

## Wall-clock proxy: R1-finish → fix-commit pushed

Using the **PR commit timestamp as a proxy for fix-loop duration** (Round 1 review completion timestamp → fix commit push timestamp). This measures real-world developer cost end-to-end — drafting, reading, verifying, pushing — not pure code-edit time.

| PR | R1 finished | Fix commit | Wall-clock | Threads addressed | Per-thread avg |
|---|---|---|---|---|---|
| Uber-Eats #1 | 08:51:13Z | `658710d` 09:11:46Z | **20 m 33 s** | 3 (U1, U2, BONUS) | **6 m 51 s** |
| Rate-Limiter #1 | 08:47:54Z | `b3c4dc0` 09:14:34Z | **26 m 40 s** | 5 (RL1, RL2, RL4, RL5, RL6) | **5 m 20 s** |
| Ride-Sharing #1 | 09:22:19Z | `e81a2ad` 09:41:39Z | **19 m 20 s** | 4 (C1, C2, C3, C4) | **4 m 50 s** |
| **Aggregate** | | | **66 m 33 s** | **12 threads** | **median 5 m 20 s** |

### Adoption-band interpretation (per `docs/Go-Fix-Loop-Runbook.md` thresholds)

| Band | Threshold | This corpus |
|---|---|---|
| Adopted (developers prefer the workflow) | < 60 s / thread | **No PR landed here** |
| Tolerated (like a slow CI check) | 1–3 min / thread | **No PR landed here** |
| **Kills adoption within one sprint** | > 5 min / thread | **2 of 3 PRs land here (Uber-Eats 6m 51s, Rate-Limiter 5m 20s)** |

Ride-Sharing landed just below the 5-minute cutoff (4m 50s) — likely because all 4 findings were concurrency-class, where CodeAnt's mechanism-level reasoning ("re-entrant Lock on sync.Mutex", "concurrent map read and map write") translates more directly to a clear fix than the broader uber-eats / rate-limiter mix.

### Caveats on the proxy

The wall-clock proxy is **not** a clean measurement:

- **Upper-bound noise:** the interval includes context-switches, side-conversations (this benchmark was run alongside a Claude assistant), verification (`go build / vet / test / test -race`), and the push itself. Pure code-edit time is lower.
- **Lower-bound noise:** fixes were drafted with Claude assistance, not via CodeAnt's "Fix in Cursor" button. A developer without an LLM assistant or working purely in the CodeAnt product surface would likely take longer.
- **Bundled commit:** per-thread average divides total wall-clock by thread count. Some threads were trivial (RL5 one-character `<` → `<=`), others non-trivial (RL4 monitor-map + cancel-channel). Variance is not captured.

Despite these caveats, the band placement is unambiguous: **median fix-loop session lands above the runbook's adoption-killing threshold.** This is the best wall-clock data this benchmark produces without the deferred UI-driven Fix-in-Cursor pass.

## What remains un-fixed (and why)

Five seeded defects + 1 wire-break still live in code:

| ID | Repo | Why unfixed |
|----|------|-------------|
| U3 | Uber-Eats | `Quantity int → uint8` narrowing — CodeAnt did not flag it in Round 1 |
| U4 | Uber-Eats | `AddRestaurant` silent overwrite — CodeAnt did not flag (the cross-language D4 blind spot) |
| U5 | Uber-Eats | `stateMachine.Apply` action error swallow — CodeAnt did not flag |
| U6 | Uber-Eats | `Preparing → Cancelled` actor-guard gap — file was modified for U5 area but this hunk was unmodified; CodeAnt did not flag |
| RL3 | Rate-Limiter | `ClientIDHeader` X-API-Key → X-Client-ID rename — CodeAnt did not flag (the wire-break miss) |

This is the intended fix-loop behavior: only address what CodeAnt finds. The 5 unfixed defects **are** the proof points for the "human must independently check these classes" rule in the manual-gate writeup.

## What this measurement tells us — and what it doesn't

**Tells us:**
- **Every Critical/High CodeAnt finding in this benchmark was actionable.** No false positives, no findings too vague to fix, no findings requiring more context than the inline comment provided.
- **CodeAnt's textual suggestions are sufficient input for a correct fix** — at least when a strong assistant or experienced developer drafts the patch.
- **Defense-in-depth often comes naturally** — 4/8 fixes went beyond the minimal patch CodeAnt suggested.

**Does NOT tell us:**
- Whether Cursor's "Fix in Cursor" button generates equivalent diffs to what Claude produced.
- Per-thread time-to-fix in the actual CodeAnt product workflow.
- Whether developers without an LLM assistant or strong concurrency intuition would produce equivalent fixes.

## Recommended follow-up for the NetApp writeup

To produce decision-grade developer-experience data, **one more pass** on either Uber-Eats PR #1 or Rate-Limiter PR #1 using Cursor's "Fix in Cursor" button is needed. Suggested approach if quota is a constraint:

1. Pick **one PR** (Rate-Limiter is the better target — more findings, broader variety: secret, leak, off-by-one, error path).
2. Pick **3 threads** spanning easy/medium/hard fix complexity (e.g., RL5 easy off-by-one, RL2 medium denylist, RL4 hard goroutine lifecycle).
3. Run the UI workflow exactly per `docs/Go-Fix-Loop-Runbook.md`, recording wall-clock and accept-as-is Y/N.
4. Compare the Cursor-generated diff against the Claude-generated diff already in `b3c4dc0` — does CodeAnt's tooling produce a comparable fix without LLM assistance?

That single follow-up pass is the gap between "we have recall data" and "we have manual-gate adoption data."
