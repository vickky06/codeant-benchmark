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

## Scripts

- **`score_pr1.sh`** — fetch PR JSON from GitHub (`export GH_TOKEN=…` required for private or rate-limited use).
- **`score_pr1.py`** — optional helper to build a human scoring template from inline comments.

## Clean control (PR 2)

- **PR:** [#8 — max code length validation](https://github.com/vickky06/Rexec/pull/8) (Rexec)
- **Spec / scoring:** **`docs/PR2-clean-control-spec.md`**
- **Artifacts:** run `export GH_TOKEN=… && ./fetch_rexec_pr.sh 8` — writes `pr8/*.json`

## What to do next

See **`docs/NEXT-STEPS.md`** (fix-me loop, PR 2, merge gating, Bitbucket pilot).

## License / data

JSON files are API exports from public GitHub data. Do not commit live secrets; the “token” in the benchmark PR is **fake** by design.
