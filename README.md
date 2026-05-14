# CodeAnt benchmarks — Rexec (Rust) + Go corpus

This repository holds **reproducible artifacts** and **scored findings** for evaluating [CodeAnt AI](https://codeant.ai).

**Canonical summary (all arms):** **`docs/BENCHMARK-SUMMARY.md`** · **Weights / JSON audit:** **`docs/CALCULATION-VERIFICATION.md`** · **Go corpus design:** **`docs/Go-Corpus-Design.md`** · **NetApp gate:** **`NETAPP_RECOMMENDATION.md`** · **Meeting walkthrough:** **`docs/PRESENTATION-PREP.md`** · **vs Claude-based agents:** **`docs/CODEANT-VS-CLAUDE-AGENT.md`**

- **Rust (Rexec):** PRs [#7](https://github.com/vickky06/Rexec/pull/7) / [#8](https://github.com/vickky06/Rexec/pull/8) — below.  
- **Go:** [Uber-Eats PR #1](https://github.com/vickky06/Uber-Eats/pull/1), [Rate-Limiter PR #1](https://github.com/vickky06/Rate-Limiter/pull/1), [Ride-Sharing PR #1](https://github.com/vickky06/Ride-Sharing-Trip-Manager/pull/1) — scores `UberEats_PR_Score.md`, `RateLimiter_PR_Score.md`, `RideSharing_PR_Score.md`; artifacts under `uber-eats-pr1/`, `rate-limiter-pr1/`, `ride-sharing-pr1/` (+ `*-round2/` where applicable).

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

## Go corpus (headline)

| PR | Recall | FP (R1 inline) | Full report |
|----|--------|----------------|-------------|
| [Uber-Eats #1](https://github.com/vickky06/Uber-Eats/pull/1) | **40%** (8/20) | 0 | `UberEats_PR_Score.md` |
| [Rate-Limiter #1](https://github.com/vickky06/Rate-Limiter/pull/1) | **75%** (15/20) | 0 | `RateLimiter_PR_Score.md` |
| [Ride-Sharing #1](https://github.com/vickky06/Ride-Sharing-Trip-Manager/pull/1) | **100%** (20/20); **3 FP** post-fix R2 | 0 R1 | `RideSharing_PR_Score.md` |

Design + NetApp framing: **`docs/Go-Corpus-Design.md`**, **`NETAPP_RECOMMENDATION.md`**.

## Scripts

- **`fetch_rexec_pr.sh`** — `export GH_TOKEN=… && ./fetch_rexec_pr.sh <PR_NUMBER> [OUTPUT_DIR]` — Rexec only (`vickky06/Rexec`).
- **`fetch_pr.sh`** — `./fetch_pr.sh <owner/repo> <PR> [OUT_DIR]` — any repo (requires **`gh`** CLI auth).
- **`score_pr1.py`** — optional helper for scoring templates.

## Fix-me loop

- **Rexec:** **`fix_loop_results.md`** · **`pr7-round2/`** · **`docs/PR7-ROUND2-EXECUTION-LOG.md`**.  
- **Go:** **`fix_loop_results_go_addendum.md`** · **`docs/Go-Fix-Loop-Runbook.md`**.

## Security

**Never commit GitHub PATs** or paste them into chat. If a PAT was exposed, **revoke it** in GitHub → Settings → Developer settings → Personal access tokens, then create a new one.

## Clean control (PR 2)

- **PR:** [#8 — max code length validation](https://github.com/vickky06/Rexec/pull/8) (Rexec)
- **Spec:** **`docs/PR2-clean-control-spec.md`**
- **Artifacts:** `pr8/` (see `fetch_rexec_pr.sh`)

## What to do next

**`Plan.MD`** · **`docs/NEXT-STEPS.md`** · **`docs/CALCULATION-VERIFICATION.md`** · PR #8: **`docs/PR8-comments-inventory.md`**

## License / data

JSON files are API exports from public GitHub data. Do not commit live secrets; the “token” in the benchmark PR is **fake** by design.
