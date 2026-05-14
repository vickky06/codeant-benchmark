# CodeAnt benchmark — Rexec (Rust)

This repository holds **reproducible artifacts** and **scored findings** for evaluating [CodeAnt AI](https://codeant.ai) on a controlled pull request.

## Benchmark PR (defect-rich)

- **Application repo:** [vickky06/Rexec](https://github.com/vickky06/Rexec)
- **PR:** [#7 — feat: telemetry, audit logging, and lifecycle improvements](https://github.com/vickky06/Rexec/pull/7)
- **Design:** six **seeded defects** across security, observability, compatibility, resource, correctness, and failure-handling (20 weighted points). See `Rexec_PR1_AnswerKey.md`.

## Results (PR 1)

| Metric | Value |
|--------|--------|
| Weighted recall | **85%** (17 / 20) |
| Missed | **D4** — silent session overwrite / duplicate-key guard removed |
| False positives (inline) | **0** |
| Inline file coverage | **80%** (4 / 5 files) |
| Cold review latency | **~9 min** |

Full analysis: **`PR1_CodeAnt_Score.md`**

## Results (PR 2 — clean control)

| Metric | Value |
|--------|--------|
| False positives (inline) | **0** |
| Noise | **0** |
| Inline file coverage | **50%** (2 / 4 files) |
| Warm review latency | **~4 min 13 s** |

Full analysis: **`PR2_CodeAnt_Score.md`** · Artifacts: **`pr8/*.json`**

## Scripts

- **`fetch_rexec_pr.sh`** — `export GH_TOKEN=… && ./fetch_rexec_pr.sh <PR_NUMBER> [OUTPUT_DIR]` fetches Rexec PR JSON (default dir `pr<N>/`; e.g. `… 7 pr7-round2` for a second snapshot).
- **`score_pr1.py`** — optional helper to build a human scoring template from inline comments.

## Fix-me loop (PR 7)

**`fix_loop_results.md`** — local rehearsal + **Round 2** (post-push) notes. API snapshot: **`pr7-round2/`** · Runbook: **`docs/PR7-ROUND2-EXECUTION-LOG.md`**.

## Security

**Never commit GitHub PATs** or paste them into chat. If a PAT was exposed, **revoke it** in GitHub → Settings → Developer settings → Personal access tokens, then create a new one.

## Clean control (PR 2)

- **PR:** [#8 — max code length validation](https://github.com/vickky06/Rexec/pull/8) (Rexec)
- **Spec:** **`docs/PR2-clean-control-spec.md`**
- **Artifacts:** `pr8/` (see `fetch_rexec_pr.sh`)

## Go corpus (three-arm benchmark, 2026-05-14)

Adds Go coverage because the NetApp manual-gate use case is Go control-plane + Java web. Each arm is a defect-rich PR with a separate answer key and score doc; design rationale in **`docs/Go-Corpus-Design.md`**.

| Arm | Application repo | PR | Defect surface | Recall (R1) | False positives | Answer key | Score |
|---|---|---|---|---|---|---|---|
| Uber-Eats | [vickky06/Uber-Eats](https://github.com/vickky06/Uber-Eats) | [#1](https://github.com/vickky06/Uber-Eats/pull/1) | secret, PII log, type narrow, silent overwrite, error swallow, authz gap | **40 %** (8/20) | 0 | `UberEats_PR_AnswerKey.md` | `UberEats_PR_Score.md` |
| Rate-Limiter | [vickky06/Rate-Limiter](https://github.com/vickky06/Rate-Limiter) | [#1](https://github.com/vickky06/Rate-Limiter/pull/1) | admin secret, header leak, wire-break, goroutine leak, off-by-one, error swallow | **75 %** (15/20) | 0 | `RateLimiter_PR_AnswerKey.md` | `RateLimiter_PR_Score.md` |
| Ride-Sharing | [vickky06/Ride-Sharing-Trip-Manager](https://github.com/vickky06/Ride-Sharing-Trip-Manager) | [#1](https://github.com/vickky06/Ride-Sharing-Trip-Manager/pull/1) | concurrency: race, goroutine leak, deadlock, RLock-write | **100 %** (20/20) | 0 (R1); 3/3 false positives (R2) | `RideSharing_PR_AnswerKey.md` | `RideSharing_PR_Score.md` |

### Cross-language defect-class picture

| Class | CodeAnt recall |
|---|---|
| Concurrency (race, deadlock, leak, RLock-write) | **Strong** — 4/4 + RL4 |
| Hardcoded secrets | **Strong** — 3/3 |
| PII in logs | **Strong** — 2/2 |
| Off-by-one boundaries | **Strong** — 1/1 with worst-case counter-example |
| Wire-breaking renames | **Weak** — 0/1 (RL3 missed) |
| Silent map overwrite / dup-key | **Cross-language blind spot** — 0/2 (D4 + U4) |
| Integer narrowing / API contract | **Weak** — 0/1 (U3) |
| Action error swallow (Go) | **Weak** — 0/1 (U5) |

### Round 2 (post-fix) — major finding

- **Ride-Sharing R2 fired** (5m 37s incremental, vs Rexec 66s) — see `RideSharing_PR_Score.md` "Round 2" section.
- **3 of 3 new R2 comments are false positives** re-flagging the already-fixed `GetAllStates`. `go test -race` is clean on the post-fix commit; CodeAnt's R2 reasoner anchored on pre-fix line numbers while posting on post-fix lines.
- **Uber-Eats / Rate-Limiter R2 did not fire** — suspected free-tier quota 403. Documented in respective score docs Round-2 sections.
- **Decision-grade for the manual gate**: even with perfect R1 recall, R2 doesn't auto-resolve fixed findings, post-fix comment count grew (4 → 12 on Ride-Sharing), and R2 can introduce false positives. The "human reviews only after CodeAnt approves" model collapses for any PR that goes through a fix-and-re-review cycle.

### Fix-loop methodology note

The runbook **`docs/Go-Fix-Loop-Runbook.md`** prescribes the UI-driven Fix-in-Cursor flow with per-thread timing. The actual fix loop used **Claude assistant**, not Fix-in-Cursor (403 quota blocked the latter on rideSharingApp); results in **`fix_loop_results_go_addendum.md`**. UI-driven measurement of CodeAnt's product UX remains a follow-up.

## What to do next

**`Plan.MD`** (checklist) · **`docs/NEXT-STEPS.md`** (merge gating, Bitbucket pilot) · PR #8 threads: **`docs/PR8-comments-inventory.md`** · Go corpus: **`docs/Go-Corpus-Design.md`**.

## License / data

JSON files are API exports from public GitHub data. Do not commit live secrets; the “token” in the benchmark PR is **fake** by design.
