# Benchmark plan — CodeAnt (Rexec + Go corpus)

Living checklist for **[vickky06/codeant-benchmark](https://github.com/vickky06/codeant-benchmark)**. Primary sources of truth: **`docs/BENCHMARK-SUMMARY.md`** (one page) and per-PR `*_PR_Score.md` files.

---

## Completed

### Rust (Rexec)

- [x] **PR #7 (defect-rich)** — [Rexec PR #7](https://github.com/vickky06/Rexec/pull/7): six seeded defects, `Rexec_PR1_AnswerKey.md`, `PR1_CodeAnt_Score.md`, `pr1_*.json`.
- [x] **PR #8 (clean control)** — [Rexec PR #8](https://github.com/vickky06/Rexec/pull/8): `PR2_CodeAnt_Score.md`, `pr8/`.
- [x] **PR #7 round 2** — `pr7-round2/`, narrative in `PR1_CodeAnt_Score.md`, `fix_loop_results.md`, `docs/PR7-ROUND2-EXECUTION-LOG.md`.
- [x] **`fetch_rexec_pr.sh`** — Rexec PR JSON export (`GH_TOKEN` + curl).

### Go corpus (design: `docs/Go-Corpus-Design.md`)

- [x] **Uber-Eats PR #1** — `UberEats_PR_Score.md`, `UberEats_PR_AnswerKey.md`, `uber-eats-pr1/`, `uber-eats-pr1-round2/`.
- [x] **Rate-Limiter PR #1** — `RateLimiter_PR_Score.md`, `RateLimiter_PR_AnswerKey.md`, `rate-limiter-pr1/`.
- [x] **Ride-Sharing PR #1** — `RideSharing_PR_Score.md`, `RideSharing_PR_AnswerKey.md`, `ride-sharing-pr1/`, `ride-sharing-pr1-round2/` (round 2 FP analysis in score doc).
- [x] **Go fix-me write-up** — `fix_loop_results_go_addendum.md` (incl. methodology note on non–Fix-in-Cursor workflow).
- [x] **`fetch_pr.sh`** — generic `gh api` export for any `owner/repo` + PR + output dir.

### Repo / publication

- [x] **Merged to `main`** — benchmark corpus and scores landed on default branch.
- [x] **Canonical summary** — `docs/BENCHMARK-SUMMARY.md` (exec + tables + validity + reproduce).

### Stakeholder deliverable

- [x] **NetApp / manual gate** — `NETAPP_RECOMMENDATION.md` (+ Go corpus rationale in `docs/Go-Corpus-Design.md`).

---

## Remaining (optional / operational)

- [ ] **Rotate credentials** — If any PAT was exposed, revoke and use `export GH_TOKEN=…` or `gh auth` only in your shell.
- [ ] **Fix-me loop (UI-driven)** — Optional: run **Fix in Cursor** per thread on a throwaway branch and record wall-clock (`Plan.MD` historically referenced Rexec PR #7; Go runbook: `docs/Go-Fix-Loop-Runbook.md`).
- [ ] **Merge gating** — Confirm whether CodeAnt publishes a **required check** vs comments-only `COMMENTED` reviews (each PR / org).
- [ ] **Bitbucket pilot** — Per `docs/NEXT-STEPS.md`.
- [ ] **Optional second vendor** — Same protocol (e.g. CodeRabbit) if leadership wants A/B.

---

## Fix-me loop — PR #7 (Rexec, reference)

**Goal:** Measure **comment → Fix in Cursor → commit** (not hand-authored diffs only). Procedure: open [Rexec PR #7](https://github.com/vickky06/Rexec/pull/7) → inline comment → **Fix in Cursor** → `cargo check` / `clippy` / `test` → record in `fix_loop_results.md`. Optional if fixes already merged.

---

## Related docs

| Doc | Purpose |
|-----|---------|
| **`docs/BENCHMARK-SUMMARY.md`** | Canonical one-page summary (all arms). |
| `docs/Go-Corpus-Design.md` | Why Uber-Eats + Rate-Limiter (+ Ride-Sharing). |
| `docs/Go-Fix-Loop-Runbook.md` | Go fix-me / UI workflow. |
| `docs/NEXT-STEPS.md` | Merge gating, Bitbucket, vendor. |
| `PR1_CodeAnt_Score.md` / `PR2_CodeAnt_Score.md` | Rexec scores. |
| `UberEats_PR_Score.md` / `RateLimiter_PR_Score.md` / `RideSharing_PR_Score.md` | Go scores. |
| `NETAPP_RECOMMENDATION.md` | Gate recommendation. |
| `README.md` | Entry tables. |
