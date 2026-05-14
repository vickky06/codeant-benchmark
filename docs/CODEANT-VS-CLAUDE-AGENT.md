# CodeAnt (benchmarked) vs a Claude-based agent — comparison note

This document situates **CodeAnt as measured in this repository** next to a **Claude-based agent** tasked with similar work (PR review, defect finding, optional fix guidance). It is **not** a head-to-head benchmark unless you run the same PRs, answer keys, and rubric against a **frozen** Claude configuration.

**Related:** `docs/BENCHMARK-SUMMARY.md`, `docs/CALCULATION-VERIFICATION.md`, per-PR `*_PR_Score.md`.

---

## What this repo actually measured (CodeAnt)

The corpus scores **CodeAnt-as-shipped on GitHub**: inline review, PR-body summary, incremental re-review where captured, optional “Fix in Cursor” / IDE handoff, and **templated** agent prompts. API exports show reviews remain **`COMMENTED`** with empty `body` — no machine-readable **`APPROVED` / `CHANGES_REQUESTED`** signal from that surface alone (see `docs/CALCULATION-VERIFICATION.md`).

A **Claude-based agent** might instead be: Cursor Composer with Claude, a `claude` CLI workflow, a CI job calling **Claude API** on `git diff`, or an internal bot. Each choice changes **context**, **tools**, **latency**, **cost**, and **whether a PR summary even exists**.

So “how does CodeAnt rate vs Claude?” depends on **which Claude agent** and **what contract** (diff-only vs full files, required tests, merge checks).

---

## Where CodeAnt (this study) looks strong vs a typical ad-hoc Claude reviewer

- **Structured, diff-anchored feedback** — Severity, repro-style steps, and file/line anchors appear consistently on high-signal threads (e.g. Ride-Sharing concurrency, Rate-Limiter boundary reasoning in `RateLimiter_PR_Score.md`).
- **Round 1 inline false positives** — As scored across the four weighted PRs, **0** inline FPs in round 1 on the threads you graded (`PR1_CodeAnt_Score.md`, `UberEats_PR_Score.md`, `RateLimiter_PR_Score.md`, `RideSharing_PR_Score.md`). Ungated LLM chat reviews often pick up **style noise** or **speculative** issues unless prompts and rubrics are tight.
- **Product integration** — Findings land on the PR where reviewers already work; that is a real adoption advantage over “paste the diff into chat.”

---

## Where a well-built Claude agent can beat what you observed — *if you design for it*

- **Summary vs inline split** — This benchmark documents a **systematic** risk: PR-body summaries can **✅-endorse** changes while inline threads flag **Critical** issues (all four scored PRs; detail in score files). A pipeline you own can **forbid** marketing-style summaries, or require **“summary may only restate inline severities.”**
- **Round 2 grounding / false positives** — Ride-Sharing round 2 re-flagged fixed code (`RideSharing_PR_Score.md`). A custom agent can require **post-fix full-file read**, **diff against base**, or **tool proof** (`go test -race`, `cargo test`) and **suppress** claims contradicted by tests.
- **Merge gating** — Neither stack “fixes” GitHub by itself. A Claude-based workflow can still emit a **commit Check** from your automation if you control the CI — independent of whether the LLM is Claude or a vendor bot.

---

## Where a Claude agent is often weaker or riskier unless engineered

- **Repeatability** — Vendor product behavior shifts on their release cycle; Claude models and routing also change. Any comparison should **pin model id + prompt version + temperature + tools**.
- **Operations** — You own **prompt injection** (malicious PR body), **PII in logs**, **token cost**, **rate limits**, and **audit** when you run your own agent.
- **Same blind spots without extra context** — Misses on **unchanged hunks**, **silent overwrite**, **narrowing / contract** issues often come from **diff-only** context. A Claude reviewer given only the patch can miss the same classes unless you explicitly widen context (full files, `go vet`/linters as tools, policy rules).

---

## Fair one-line summary for stakeholders

**CodeAnt (as measured)** delivers a **mature GitHub-native review surface** with **strong peak reasoning** on several defect classes, but shows **product-level gaps** (summary regression, round-2 grounding/FPI risk in at least one track, no approval signal from reviews JSON). A **Claude-based agent** is not automatically better; it is **more flexible** and can **target those gaps** — at the cost of **building and maintaining** workflow, verification, and governance yourself.

---

## How to produce an actual head-to-head score

1. **Freeze** the Claude stack: model, system prompt, tools (`go test`, `rg`, file reads), max tokens, temperature.  
2. Re-run on the **same four PRs** (or frozen SHAs + exported JSON diffs).  
3. Apply the **same answer keys** and **weighted recall / FP / noise / latency** rubric used here.  
4. Record **merge-gating** behavior separately (Checks vs comments-only).

Until that exists, treat this file as **qualitative** guidance, not a numeric ranking.

---

## Maintenance

When the corpus or scoring changes, update the pointers at the top; do not assert Claude outcomes here without measured runs.
