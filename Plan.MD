# Benchmark plan — CodeAnt (Rexec + Go corpus)

Living checklist for **[vickky06/codeant-benchmark](https://github.com/vickky06/codeant-benchmark)**. Primary sources of truth: **`docs/BENCHMARK-SUMMARY.md`**, **`docs/CALCULATION-VERIFICATION.md`**, and per-PR `*_PR_Score.md` files.

**Status:** Benchmark corpus and scores **complete on `main`**. Optional / owner items below.

---

## Completed

### Rust (Rexec)

- [x] **PR #7 (defect-rich)** — [Rexec PR #7](https://github.com/vickky06/Rexec/pull/7): `Rexec_PR1_AnswerKey.md`, `PR1_CodeAnt_Score.md`, `pr1_*.json`.
- [x] **PR #8 (clean control)** — [Rexec PR #8](https://github.com/vickky06/Rexec/pull/8): `PR2_CodeAnt_Score.md`, `pr8/`.
- [x] **PR #7 round 2** — `pr7-round2/`, `PR1_CodeAnt_Score.md`, `fix_loop_results.md`, `docs/PR7-ROUND2-EXECUTION-LOG.md`.
- [x] **`fetch_rexec_pr.sh`**

### Go corpus

- [x] **Uber-Eats PR #1** — `UberEats_PR_*`, `uber-eats-pr1/`, `uber-eats-pr1-round2/`.
- [x] **Rate-Limiter PR #1** — `RateLimiter_PR_*`, `rate-limiter-pr1/`.
- [x] **Ride-Sharing PR #1** — `RideSharing_PR_*`, `ride-sharing-pr1/`, `ride-sharing-pr1-round2/`.
- [x] **Go fix-me write-up** — `fix_loop_results_go_addendum.md`.
- [x] **`fetch_pr.sh`**

### Repo / rigor

- [x] **Merged to `main`**
- [x] **`docs/BENCHMARK-SUMMARY.md`**
- [x] **Weighted recall arithmetic + merge-gating JSON audit** — `docs/CALCULATION-VERIFICATION.md`

### Stakeholder

- [x] **`NETAPP_RECOMMENDATION.md`**, **`docs/Go-Corpus-Design.md`**

---

## Optional / owner (not required to close benchmark)

- [ ] **UI “Fix in Cursor” measurement** — If you want product-level timing: `docs/Go-Fix-Loop-Runbook.md` + Rexec notes in `fix_loop_results.md` (fixes already landed; purely optional).
- [ ] **PAT hygiene** — Revoke benchmark tokens when study is fully closed (operational, not a repo deliverable).
- [ ] **Live Checks tab** — Org-specific: confirm CodeAnt app publishes a **required check** if you rely on branch protection (beyond JSON `COMMENTED` reviews — see `docs/CALCULATION-VERIFICATION.md`).

**Roadmap (outside this repo’s closure):** Bitbucket pilot, second vendor — **`docs/NEXT-STEPS.md`** §4–5.

---

## Fix-me reference (Rexec PR #7)

Optional **Fix in Cursor** workflow: GitHub PR #7 inline comments → Cursor → `cargo check` / `clippy` / `test` → record in `fix_loop_results.md`.

---

## Related docs

| Doc | Purpose |
|-----|---------|
| **`docs/BENCHMARK-SUMMARY.md`** | One-page summary (all arms). |
| **`docs/CALCULATION-VERIFICATION.md`** | Recall arithmetic + Ride-Sharing R2 FP counts + merge-gating JSON note. |
| `docs/Go-Corpus-Design.md` | Corpus rationale. |
| `docs/Go-Fix-Loop-Runbook.md` | Go UI fix-me. |
| `docs/NEXT-STEPS.md` | Merge gating narrative, Bitbucket, vendor A/B. |
| `docs/CODEANT-VS-CLAUDE-AGENT.md` | CodeAnt vs a Claude-based reviewer (qualitative; head-to-head needs same rubric). |
| `PR1_CodeAnt_Score.md` / `PR2_CodeAnt_Score.md` | Rexec. |
| `UberEats_PR_Score.md` / `RateLimiter_PR_Score.md` / `RideSharing_PR_Score.md` | Go. |
| `NETAPP_RECOMMENDATION.md` | Gate write-up. |
| `README.md` | Entry tables. |
