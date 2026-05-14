# Go — CodeAnt assessments

Add **two** (or more) Go-based benchmark tracks here. Keep each project **self-contained** so Rust (`Rexec`) artifacts at repo root stay unchanged.

## Layout (per project)

Create a directory named after the repo or feature slug:

```text
assessments/go/<slug>/
  README.md              # PR links, dates, one-paragraph goal
  ANSWER_KEY.md          # optional but recommended for defect-seeded PRs
  SCORE.md               # recall / FP / noise / latency / summary quality
  artifacts/             # GitHub API JSON (pr_meta, pr_inline_comments, …)
  FIX_LOOP.md            # optional: fix-me / round-2 notes
```

**Artifacts:** mirror the Rexec pattern (`artifacts/pr_meta.json`, `artifacts/pr_inline_comments.json`, `artifacts/pr_reviews.json`, `artifacts/pr_issue_comments.json`). You can copy `fetch_rexec_pr.sh` to a small wrapper that sets `REPO=owner/name` and `OUT=assessments/go/<slug>/artifacts`, or curl the same four endpoints manually.

## Slots for your two assessments

| Slot | Directory | Status |
|------|-----------|--------|
| 1 | `assessments/go/<add-slug>/` | Add when ready |
| 2 | `assessments/go/<add-slug>/` | Add when ready |

After both exist, update **`docs/BENCHMARK-SUMMARY.md`** (multi-language section) and **`Plan.MD`** checkboxes.

## Cross-language notes

- Reuse the same **scoring dimensions** where possible (recall vs answer key, FP, noise, coverage, latency, summary vs inline) so leadership can compare **Rust vs Go** fairly.
- Call out **language-specific** risks (e.g. `go test`, race detector, `staticcheck`) in each project’s `README.md`.
