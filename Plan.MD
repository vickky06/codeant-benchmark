# Benchmark plan — CodeAnt (Rexec + extensions)

Living checklist for **vickky06/Rexec** (Rust) and **additional assessments** in this repo. Update as steps finish.

---

## Go assessments (add your two projects)

**Convention:** one folder per project under **`assessments/go/<slug>/`** — see **`assessments/go/README.md`**.

- [ ] **Go assessment 1** — `assessments/go/<slug>/` with `README.md`, `SCORE.md`, `artifacts/*.json` (and `ANSWER_KEY.md` if defect-seeded).
- [ ] **Go assessment 2** — same layout for second repo/PR set.
- [ ] **Summary** — extend **`docs/BENCHMARK-SUMMARY.md`** with a short “Go” subsection (links + headline metrics) once scores exist.

---

## Completed (Rexec / Rust)

- [x] **PR 1 (defect-rich)** — [Rexec PR #7](https://github.com/vickky06/Rexec/pull/7): six seeded defects, answer key (`Rexec_PR1_AnswerKey.md`), weighted scoring.
- [x] **PR 1 scoring doc** — `PR1_CodeAnt_Score.md` (recall, FPs, coverage, cold latency ~9 min, D4 miss noted).
- [x] **PR 1 artifacts** — Inline/reviews/issue/meta JSON at repo root (`pr1_*.json` / template flow).
- [x] **PR 2 spec** — `docs/PR2-clean-control-spec.md` (clean control design).
- [x] **PR 2 (clean control)** — [Rexec PR #8](https://github.com/vickky06/Rexec/pull/8) executed; artifacts under `pr8/`.
- [x] **PR 2 scoring doc** — `PR2_CodeAnt_Score.md` (FP0, noise, warm latency ~4m13s, coverage).
- [x] **Fetch script** — `fetch_rexec_pr.sh` for reproducible GitHub API exports (`pr<N>/`).
- [x] **Findings branch** — Pushed to [codeant-benchmark](https://github.com/vickky06/codeant-benchmark) on `docs/benchmark-findings-2026-05-13` (merge via open PR as needed).
- [x] **Exploratory fix pass (manual)** — Documented in `fix_loop_results.md`: local branch `throwaway/fix-me-codeant` with D1/D2/D3/D5/D6-aligned edits and `cargo check` PASS. **Not** the canonical fix-me procedure (see below).
- [x] **PR #7 round 2 (incremental) archived** — `pr7-round2/*.json`, narrative in `fix_loop_results.md` + `PR1_CodeAnt_Score.md`, runbook **`docs/PR7-ROUND2-EXECUTION-LOG.md`**. *Optional:* stricter UI-per-thread timing still in **Remaining** below.

---

## Remaining

- [ ] **Rotate credentials** — If any PAT was exposed, revoke it in GitHub and use a new token only via local `export GH_TOKEN=…` (never chat/commits).
- [ ] **Merge benchmark PR** — Land `docs/benchmark-findings-2026-05-13` (or equivalent) so `main` contains scores + `pr8/` + `pr7-round2/`.
- [ ] **Fix-me loop (UI-driven, measured)** — Optional rigor: re-run on PR #7 using **Fix in Cursor** per thread; record per-thread time and `cargo check` / `cargo clippy` / `cargo test` in `fix_loop_results.md` (fixes already landed on PR head for this bench).
- [ ] **Merge gating** — Confirm whether CodeAnt (or GitHub App) exposes a **required check / commit status** suitable for branch protection; document gap if reviews stay `COMMENTED`-only.
- [ ] **Bitbucket pilot** — Two-week pilot on a real service repo after security/egress sign-off (production is Bitbucket, not GitHub).
- [ ] **Optional second vendor** — Same PR design vs CodeRabbit (or internal tool) for A/B comparison.

---

## Fix-me loop — use the PR web UI (required)

**Goal:** Measure the product path where review comments drive fixes, not only hand-edited diffs.

1. **Checkout the PR head** locally (example):

   ```bash
   git fetch origin pull/7/head:pr7
   git checkout -b throwaway/fix-me-ui pr7
   ```

2. **For each high-signal inline thread** (D1 bearer, D3 proto tag, D5 error swallow, D2 audit payload, D6 telemetry/remove — order as you prefer):

   - Open [Rexec PR #7](https://github.com/vickky06/Rexec/pull/7) in the browser.
   - On the **inline review comment**, use the vendor control that opens Cursor with context for that fix (documented in CodeAnt/GitHub as **“Fix in Cursor”** or the current equivalent **fix / apply** control on the comment).
   - Apply the suggested change in the IDE, **review the diff**, adjust if the bot was wrong, then commit with a message that references the thread (e.g. `fix: restore proto code field tag 2 (CodeAnt D3)`).

3. **Verify after each batch or at the end:**

   ```bash
   cargo check
   cargo clippy --all-targets --no-deps
   cargo test
   ```

4. **Record** in `fix_loop_results.md`: which threads used **UI-initiated** fixes vs manual follow-up, wall-clock per thread, and command results.

5. **Cleanup:** Prefer **not** merging the throwaway branch into PR #7 unless you intend to ship; delete local branch when done or cherry-pick to a real feature branch.

**Why UI-first:** The earlier `fix_loop_results.md` pass validated *what* to change; the **benchmark** should stress the **comment → fix button → Cursor** workflow so latency and edit quality reflect real adoption.

---

## Related docs

| Doc | Purpose |
|-----|---------|
| **`docs/BENCHMARK-SUMMARY.md`** | **Canonical one-page summary** (Rexec; extend for Go when ready). |
| **`assessments/go/README.md`** | **Go** assessment layout and slots. |
| `docs/NEXT-STEPS.md` | Short operational next steps (merge gating, Bitbucket). |
| `fix_loop_results.md` | Fix-me outcomes (append UI-driven run when complete). |
| `PR1_CodeAnt_Score.md` / `PR2_CodeAnt_Score.md` | Rexec scored results. |
| `README.md` | Entry point and tables. |
