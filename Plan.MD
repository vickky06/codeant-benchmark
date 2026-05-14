# Benchmark plan — CodeAnt on Rexec

Living checklist for the **vickky06/Rexec** PR benchmark and **codeant-benchmark** artifacts. Update this file as steps finish.

---

## Completed

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

## Go corpus arm (2026-05-14, branch `docs/go-corpus-2026-05-14`)

### Completed

- [x] **Go corpus design** — `docs/Go-Corpus-Design.md`: rationale for three Go arms covering different defect surfaces (HTTP/auth, domain logic, concurrency).
- [x] **Uber-Eats arm** — `vickky06/Uber-Eats` PR #1 (`feat/payments-and-restaurant-registry`): six seeded defects (U1 hardcoded Stripe key, U2 PII log, U3 Quantity narrow, U4 silent overwrite, U5 action error swallow, U6 authz gap). Answer key, Round 1 score (40 % recall, 0 FP), snapshots in `uber-eats-pr1/` and `uber-eats-pr1-round2/` (R2 did not fire — suspected 403).
- [x] **Rate-Limiter arm** — `vickky06/Rate-Limiter` PR #1 (`feat/observability-and-policy-rotation`): six seeded defects (RL1 admin key, RL2 header leak, RL3 wire-break, RL4 goroutine leak, RL5 off-by-one, RL6 error swallow). Answer key, Round 1 score (75 % recall, 0 FP, 1 unseeded `NewTicker` panic catch), snapshot in `rate-limiter-pr1/` (R2 did not fire — suspected 403).
- [x] **Ride-Sharing arm** — `vickky06/Ride-Sharing-Trip-Manager` PR #1 (`feat/dispatch-dashboard-and-autopilot`): four seeded concurrency defects (C1 race, C2 leak, C3 deadlock, C4 RLock-write). Answer key, Round 1 score (100 % recall, 0 FP), snapshots in `ride-sharing-pr1/` and `ride-sharing-pr1-round2/`.
- [x] **Generalized fetch script** — `fetch_pr.sh <owner/repo> <pr#> [outdir]`. Uses `gh` CLI auth; no `GH_TOKEN` env required.
- [x] **Go fix loop** — Fixes applied to all three PRs (commits `658710d`, `b3c4dc0`, `e81a2ad`). All 8 CodeAnt-flagged findings addressed; `go build / vet / test / test -race` clean. Methodology: Claude assistant, not Fix-in-Cursor. See `fix_loop_results_go_addendum.md`.
- [x] **Round 2 measurement (Ride-Sharing only)** — 5 min 37 s incremental. **3 of 3 new comments on the post-fix commit are false positives** re-flagging the fixed `GetAllStates`. `go test -race` confirms code is correct. New Sequence Diagram feature observed. Documented in `RideSharing_PR_Score.md` Round 2 section.

### Remaining (Go arm)

- [ ] **Open codeant-benchmark PR** for `docs/go-corpus-2026-05-14` — mirrors the 2026-05-13 branch pattern.
- [ ] **Round 2 for Uber-Eats / Rate-Limiter** — re-trigger via `@codeant-ai: review` once quota resets, or document permanent quota-failure if it doesn't fire on push.
- [ ] **UI-driven Fix-in-Cursor pass on one Go PR** — Rate-Limiter recommended (3 threads: RL5 easy, RL2 medium, RL4 hard). Records per-thread wall-clock + accept-as-is fraction to fill the developer-experience gap in `fix_loop_results_go_addendum.md`.
- [ ] **NetApp recommendation writeup** — sufficient body of evidence now exists. Headline: Round 1 recall is class-dependent (strong on concurrency / secrets, weak on silent-overwrite / contract narrowing / wire-breaks). **Manual-gate model fails on the post-fix Round 2 UX** — no auto-resolve, count grows on fix, R2 can re-flag fixed code as false positive.

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
| `docs/NEXT-STEPS.md` | Short operational next steps (merge gating, Bitbucket). |
| `fix_loop_results.md` | Fix-me outcomes (append UI-driven run when complete). |
| `PR1_CodeAnt_Score.md` / `PR2_CodeAnt_Score.md` | Scored results. |
| `README.md` | Entry point and tables. |
