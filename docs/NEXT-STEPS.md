# Next steps after PR 1 scoring

Round 2 snapshot and checklist: **`docs/PR7-ROUND2-EXECUTION-LOG.md`**. Overall status: **`Plan.MD`**. **One-page summary:** **`docs/BENCHMARK-SUMMARY.md`**. **Recall / JSON audit:** **`docs/CALCULATION-VERIFICATION.md`**.

## 1. Fix-me loop (PR #7)

Goal: measure whether CodeAnt’s **“Fix in Cursor”** flow produces changes that pass your bar.

**Suggested threads (highest signal):**

1. **D1** — hardcoded bearer token → env / secret manager.
2. **D3** — protobuf field tag renumber → restore tag `2` or introduce a proper v2 message.
3. **D5** — `Ok(String::new())` on error → restore `Err(e)`.

**Procedure:**

1. `git fetch origin pull/7/head:pr7 && git checkout -b throwaway/fix-loop pr7`
2. For each fix: open **Fix in Cursor** from the GitHub comment → apply → run:
   - `cargo check && cargo clippy --all-targets --no-deps && cargo test`
3. Record: time to apply, manual edits required, pass/fail per command.
4. Prefer **not pushing** until round-1 metrics are archived, **or** push **one** fix for a controlled **round-2** re-review latency test.
5. `git checkout main && git branch -D throwaway/fix-loop`

## 2. PR 2 (clean control)

- **PR:** https://github.com/vickky06/Rexec/pull/8
- From repo root: `export GH_TOKEN=… && ./fetch_rexec_pr.sh 8` → saves under `pr8/`.
- After CodeAnt finishes: score **false positives**, **noise**, **summary quality**, and **warm latency** vs PR 1’s **cold** ~9 minutes (see `docs/PR2-clean-control-spec.md`).

## 3. Merge gating (“bot as shield”)

**Corpus check (JSON in this repo):** Every captured `pr_reviews.json` shows CodeAnt with `state: COMMENTED` and an empty review `body` — see **`docs/CALCULATION-VERIFICATION.md`**. That is **not** a merge-blocking approval signal by itself.

For production:

- Confirm in the GitHub **Checks** UI (per org/repo) whether CodeAnt publishes a **commit status / check** branch protection can require.
- If only comments exist, use a thin workflow (e.g. Bitbucket Pipeline + API) to map “review complete” → reviewer assignment.

## 4. Bitbucket pilot

PRs here are on **GitHub**; production target is **Bitbucket**. Run a **2-week pilot** on one service repo after security signs off on SaaS egress.

## 5. Optional: second vendor

If leadership wants an A/B: repeat the same seeded PR + clean PR against **CodeRabbit** (or fork internal ReviewBot) using the same answer key and weights.
