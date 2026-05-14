# Weighted recall — arithmetic verification

Independent check: defect **weights** come from each `*_PR_AnswerKey.md`; **caught credits** come from the verdict column in each `*_PR_Score.md`. **Recall %** = (sum of caught weights) / 20 × 100.

| Corpus | Defects (weight) | Caught (weight sum) | Recall | Check |
|--------|------------------|----------------------|--------|-------|
| **Rexec PR #7** | D1:5, D2:3, D3:5, D4:3, D5:2, D6:2 → **20** | 5+3+5+0+2+2 = **17** | **85%** | 17/20 = 0.85 ✓ |
| **Uber-Eats PR #1** | U1:5, U2:3, U3:5, U4:3, U5:2, U6:2 → **20** | 5+3+0+0+0+0 = **8** | **40%** | 8/20 = 0.40 ✓ |
| **Rate-Limiter PR #1** | RL1:5, RL2:3, RL3:5, RL4:3, RL5:2, RL6:2 → **20** | 5+3+0+3+2+2 = **15** | **75%** | 15/20 = 0.75 ✓ |
| **Ride-Sharing PR #1** | C1:6, C2:5, C3:5, C4:4 → **20** | 6+5+5+4 = **20** | **100%** | 20/20 = 1.00 ✓ |

**Ride-Sharing round 2 (false positives on fix head):** From `ride-sharing-pr1-round2/pr_inline_comments.json`, `codeant-ai[bot]` comments grouped by `commit_id`:

- `b02b7ee…` (seeded head): **9** threads  
- `e81a2ad…` (post-fix head): **3** threads — all three are the disputed **GetAllStates** re-flags described in `RideSharing_PR_Score.md` (treated as **FP** there). 3/3 on new head = **100%** of *new* inline threads on that commit are FPs ✓ (matches narrative).

---

## Merge gating — signal verified from committed JSON

For every **`pr_reviews.json`** in this repo that includes CodeAnt bot reviews, **`state`** is **`COMMENTED`** and review **`body`** is empty in the captured exports (Rexec `pr7`, `pr7-round2`, `pr8`; Uber-Eats; Rate-Limiter; Ride-Sharing round 1 & 2).

**Conclusion for this benchmark:** the GitHub **Reviews** API objects alone do **not** provide `APPROVED` / `CHANGES_REQUESTED` style gating. Production must use **Checks / commit statuses** (or an equivalent) if branch protection should depend on CodeAnt — same recommendation as `docs/NEXT-STEPS.md` §3.

**Not verified here:** live GitHub **Checks** tab per repo (requires browser / org settings).

---

## Latency strings (sanity)

Latencies in score docs are computed from **issue-comment** or **review** timestamps in the same JSON folders; rounding to “~Xm Ys” is intentional. Re-derive anytime with `jq` on `pr_issue_comments.json` / `pr_reviews.json`.

---

## Files checked

- `Rexec_PR1_AnswerKey.md`, `UberEats_PR_AnswerKey.md`, `RateLimiter_PR_AnswerKey.md`, `RideSharing_PR_AnswerKey.md`
- `PR1_CodeAnt_Score.md`, `UberEats_PR_Score.md`, `RateLimiter_PR_Score.md`, `RideSharing_PR_Score.md`
- `ride-sharing-pr1-round2/pr_inline_comments.json` (bot + `group_by(.commit_id)`)

Last verified in-repo: **2026-05-14** (assistant pass).
