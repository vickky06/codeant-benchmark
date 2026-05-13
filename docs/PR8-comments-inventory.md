# PR #8 — CodeAnt comments inventory (clean control)

Cross-reference for [Rexec PR #8](https://github.com/vickky06/Rexec/pull/8). Raw JSON lives in **`pr8/`** (re-fetch with `./fetch_rexec_pr.sh 8` or `./fetch_rexec_pr.sh 8 pr8-round2` after new pushes).

Scored narrative: **`PR2_CodeAnt_Score.md`**.

---

## Issue / timeline comments (`pr8/pr_issue_comments.json`)

| When (UTC) | Body |
|------------|------|
| `2026-05-13T10:02:04Z` | “CodeAnt AI is reviewing your PR.” |
| `2026-05-13T10:06:13Z` | “CodeAnt AI finished reviewing your PR.” |

**Warm path:** open `10:02:00Z` → finished comment `10:06:13Z` ≈ **4 min 13 s** (matches `PR2_CodeAnt_Score.md`).

---

## Pull request review (`pr8/pr_reviews.json`)

| `id` | `submitted_at` | `state` | `commit_id` |
|------|----------------|---------|---------------|
| 4280482212 | `2026-05-13T10:06:08Z` | COMMENTED | `0576b535964a97963b6920bfe43fbdde34038a66` |

Review `body` is empty (same merge-gating caveat as PR #7: rely on **Checks** if you need a blocking signal).

---

## Inline review threads (`pr8/pr_inline_comments.json`)

Both from **`codeant-ai[bot]`**, same review id **4280482212**, `created_at` **`2026-05-13T10:06:08Z`**.

### 1 — Config contract / rollout

| Field | Value |
|-------|--------|
| Comment id | [3233270422](https://github.com/vickky06/Rexec/pull/8#discussion_r3233270422) |
| Path | `src/models/config_models.rs` |
| Theme | `max_code_length` required in TOML with **no serde default** → older `config.toml` can **fail startup** at parse time. |
| Severity in comment | Critical (api mismatch) |
| FP? | **No** — legitimate backward-compat / rollout concern for the feature as written. |

### 2 — Hot-path performance

| Field | Value |
|-------|--------|
| Comment id | [3233270432](https://github.com/vickky06/Rexec/pull/8#discussion_r3233270432) |
| Path | `src/services/validation_services/request_validation/validation_service.rs` |
| Theme | Second **`get_global_config(...).await` + full `Config` clone** in the same validation path → extra mutex contention and cloning per request. |
| Severity in comment | Major (performance) |
| FP? | **No** — accurate read of duplicated global config access. |

---

## How this fits the benchmark

| Arm | What PR #8 comments measure |
|-----|-----------------------------|
| vs PR #7 | PR #8 has **no seeded defects**; these two threads are **design/ops** feedback on an otherwise intentional feature — used for **FP = 0**, **noise = 0**, **latency**, and **summary** scoring (`PR2_CodeAnt_Score.md`). |
| vs PR #7 round 2 | PR #8 is **unchanged** by your PR #7 fix push. No “second review” step is required for PR #8 **unless** you change PR #8’s branch again; then re-fetch into e.g. `pr8-round2/`. |

---

## Optional terminal check (same pattern as PR #7)

```bash
export GH_TOKEN='…'
./fetch_rexec_pr.sh 8 pr8-$(date +%Y%m%d)   # or ./fetch_rexec_pr.sh 8 to refresh pr8/
jq '[.[] | select(.user.login=="codeant-ai[bot]")] | length' pr8/pr_inline_comments.json
```

Expected **2** inline comments for commit `0576b53…` unless the PR head moves and CodeAnt posts a new review.
