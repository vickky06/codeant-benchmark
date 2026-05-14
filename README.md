# CodeAnt benchmarks — Rexec (Rust) + Go

This repository holds **reproducible artifacts** and **scored findings** for evaluating [CodeAnt AI](https://codeant.ai).

- **Rust (Rexec):** controlled PRs [#7](https://github.com/vickky06/Rexec/pull/7) / [#8](https://github.com/vickky06/Rexec/pull/8) — see below.  
- **Go:** add assessments under **`assessments/go/<project-slug>/`** — see **`assessments/go/README.md`**.

**One-page summary (Rexec):** **`docs/BENCHMARK-SUMMARY.md`** · **Multi-language index:** **`assessments/go/README.md`**

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

## What to do next

**`Plan.MD`** (checklist) · **`docs/NEXT-STEPS.md`** (merge gating, Bitbucket pilot) · PR #8 threads: **`docs/PR8-comments-inventory.md`** · **Go assessments:** **`assessments/go/README.md`**

## License / data

JSON files are API exports from public GitHub data. Do not commit live secrets; the “token” in the benchmark PR is **fake** by design.
