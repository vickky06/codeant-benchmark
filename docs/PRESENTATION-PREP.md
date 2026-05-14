# Presentation prep — CodeAnt benchmark walkthrough

Meeting-delivery companion to **`docs/BENCHMARK-SUMMARY.md`** (the findings) and **`NETAPP_RECOMMENDATION.md`** (the verdict). This document is about *how to present*, not what to present.

For raw findings → `docs/BENCHMARK-SUMMARY.md`.
For arithmetic / audit → `docs/CALCULATION-VERIFICATION.md`.
For verdict + 8 operational rules → `NETAPP_RECOMMENDATION.md`.

---

## 30-second opener

> "NetApp asked whether we could use CodeAnt AI as a first-pass reviewer — human reviews only after CodeAnt approves. I ran a controlled benchmark with four seeded-defect PRs across Rust and Go, scored against pre-written answer keys. Round-1 recall was 75 % overall with zero false positives — strong on concurrency and secrets. But the post-fix Round-2 review introduced 100 % false positives on already-fixed code, and the bot's PR summary endorsed every seeded defect as a ✅ improvement. **Recommendation: do not adopt as a gate; adopt in advisory mode with eight written operational rules.**"

---

## 1. The question being answered

NetApp engineering asked: **can CodeAnt AI serve as a first-pass code reviewer, where the human reviewer only reviews after CodeAnt has approved the PR?**

Two implicit assumptions worth testing:
- **Recall** is good enough that "CodeAnt clean" approximates "no obvious defects"
- **The bot produces a machine-readable approval signal** after fixes land

Both turned out to be wrong in instructive ways — covered in §5 below.

## 2. Design rationale (why we did what we did)

| Choice | Why |
|---|---|
| **Personal repos, not NetApp code** | Security/egress — couldn't send NetApp source to an external SaaS without sign-off. Personal Rust + Go repos are realistic in shape but expendable. Methodology is repeatable on NetApp code once egress is approved. |
| **Seeded defects (planted bugs)** | Without ground truth you cannot measure recall. Real bugs in production code don't come with a clean answer key. Pre-writing answer keys forces honest scoring. |
| **4 PRs across 2 languages** | Rust (Rexec) was the existing baseline; 3 Go arms because NetApp control plane is Go. Each Go arm tests a different defect surface (domain logic / HTTP middleware / concurrency). |
| **6 seeded defect classes per PR** | Mirrors the Rexec D1–D6 taxonomy: security / observability / compatibility / resource / correctness / failure-handling. Gives cross-language comparability. |
| **Cover-story PR descriptions** | Each PR title and body describes the defects as legitimate features ("payment gateway integration", "admin auth", "autopilot auto-complete"). Tests whether CodeAnt's summary layer falls for author framing — it does. |
| **Round 1 + Fix Loop + Round 2** | Round 1 measures recall. Fix loop tests whether findings are actionable. Round 2 tests whether the bot recognizes fixes — which is the load-bearing question for "human reviews only after approval." |
| **Independent answer keys, scored against** | Each PR has a pre-written `*_AnswerKey.md` listing expected catches with required keywords. Scoring is "did the inline comment match those keywords." Reduces bias. |

## 3. The four arms in one paragraph each

- **Rexec (Rust)** — pre-existing arm. Six seeded defects across telemetry, audit logging, proto wire format. Round 1 caught 5/6 (the missed one was D4 silent overwrite). Baseline cross-language reference.
- **Uber-Eats (Go)** — domain model, state machine, money in cents. Seeded U1–U6. Round 1 caught only U1 and U2 (40 %). Misses included U4 silent overwrite (same class as Rust D4) and U3 integer narrowing.
- **Rate-Limiter (Go)** — HTTP middleware, admin endpoint, rate-limit math. Seeded RL1–RL6. Round 1 caught 5/6 (75 %). Miss was RL3, a wire-breaking header rename. One bonus catch (NewTicker panic on non-positive duration).
- **Ride-Sharing (Go)** — concurrency surface. Seeded C1–C4. Round 1 caught **all 4** (100 %) with mechanism-level reasoning. Round 2 then posted **3 false positives** on the fixed code — the single most important finding.

## 4. Methodology in 5 steps

1. **Seed defects** in a feature branch with a plausible cover story
2. **Open the PR** on GitHub — CodeAnt's GitHub App reviews automatically
3. **Capture Round 1 artifacts** via `fetch_pr.sh` (custom script): inline comments, reviews, issue comments, PR meta — all as JSON snapshots committed to this repo
4. **Score** each inline comment against the answer key: CAUGHT (full weight), PARTIAL (half), MISSED (zero)
5. **Apply fixes**, push, capture Round 2 artifacts, score the delta

Every claim is traceable. The recommendation has a provenance table at the bottom mapping each finding to the source artifact.

## 5. The five findings to walk through (in this order)

### 5.1 Recall is class-dependent — show the matrix

| Class | Recall | Verdict |
|---|---|---|
| Concurrency (race, deadlock, leak, RLock-write) | 5/5 | **Strong** — mechanism-level reasoning |
| Hardcoded secrets | 3/3 | Strong |
| PII in logs | 2/2 | Strong |
| Off-by-one boundaries | 1/1 | Strong (constructs worst-case counter-example) |
| Wire-breaking renames | 0/1 | **Weak** — RL3 missed |
| **Silent map overwrite / dup-key** | **0/2** | **Cross-language blind spot** — D4 + U4 |
| Integer narrowing | 0/1 | Weak |
| Action error swallow | 1/2 | Weak on Go (U5 missed) |

**What to say:** "CodeAnt is genuinely strong on the classes where it engages. It has identifiable blind spots that humans must independently check. The blind spots reproduced cross-language — D4 on Rust, U4 on Go, same defect pattern, both missed."

### 5.2 The PR-body summary endorses defects (n=4, both failure modes)

Every PR's auto-generated summary block contained `✅` bullets endorsing the seeded defects:
- *"✅ Safer policy changes"* — on a PR that introduced a hardcoded admin secret
- *"✅ Fewer boundary-limit bypasses"* — on an off-by-one defect that denies traffic at the limit
- *"✅ Faster trip cancellation"* — on a `delete()` under `RLock` that panics under load

**Two failure modes:**
- **Mode A** — inline review CAUGHT the defect, summary still endorsed it (4 of 4 PRs)
- **Mode B** — inline review MISSED the defect, summary parroted the cover story (Uber-Eats)

**What to say:** "The PR summary cannot be trusted as a heuristic for 'is this PR safe-looking.' The reviewer must read inline severities directly, every time."

### 5.3 The Round-2 finding (the most important one — slow down here)

The Ride-Sharing arm caught **100 % of seeded concurrency defects** in Round 1. The fix commit applied CodeAnt's own Round-1 suggestions almost verbatim. `go test -race` confirms no race condition remains.

**Round 2 incremental review then posted 3 NEW Critical/Major comments on the fixed code, all false positives**, claiming the same locks weren't being held — when they demonstrably are.

The smoking gun: one of the false-positive comments cites *pre-fix line numbers (138-139)* in its Steps-of-Reproduction, while the comment itself is anchored at *post-fix lines (175-177)*. The reasoner used stale code state.

**What to say:** "Even on a PR where Round-1 recall was perfect, the post-fix experience collapses the manual-gate model. Three things happen simultaneously: (1) no machine-readable 'approved' signal exists — original findings stay visible; (2) comment count grew (4 → 12) after correct fixes landed; (3) Round 2 introduced 100 % false positives on the fixed commit."

**This is the single highest-impact slide.** If the audience only takes one thing away, this is it.

### 5.4 The wall-clock cost

Wall-clock proxy: time from Round-1-finish to fix-commit-pushed, across all three Go PRs:

| PR | Per-thread |
|---|---|
| Uber-Eats | 6 m 51 s |
| Rate-Limiter | 5 m 20 s |
| Ride-Sharing | 4 m 50 s |
| **Median** | **5 m 20 s/thread** |

Runbook adoption bands: `<60 s` preferred, `1–3 min` tolerated, `>5 min` kills adoption within one sprint.

**What to say:** "Even with LLM assistance during the fix loop, the per-thread cost lands in adoption-killing territory. Without LLM tailwind it gets worse. This is independent quantitative evidence that the workflow won't survive politically beyond one or two sprints."

### 5.5 Where CodeAnt clearly helps (the steel-man for adoption)

| Use case | Evidence |
|---|---|
| Concurrency review of Go services | 100 % recall, mechanism-level reasoning beyond `go test -race` |
| Secret rotation pattern | Architect Reviews name binary-leak vector, not just regex |
| PII / sensitive-header leak detection | Explicitly names the leak vector (e.g., `X-Admin-Key`) |
| Cross-file logic chain reasoning | Caught the unseeded `NewTicker` panic — chained consequence of two changes |
| Architecture diagrams (Sequence Diagram feature) | Useful review hand-off artifact |

**What to say:** "Where CodeAnt engages, it produces signal humans and standard tooling miss often. That's why the recommendation is advisory mode, not 'do not use'."

## 6. The recommendation on one slide

| Use case | Verdict |
|---|---|
| Manual gate (human reviews after CodeAnt approves) | **No** — §5.3 alone disqualifies |
| Branch-protection blocking gate | **No** — no required-check / commit-status mechanism |
| **Advisory first-pass alongside human review** | **Yes**, with 8 operational rules — see `NETAPP_RECOMMENDATION.md` §8 |
| PR summarizer / triage tool | **No** — summary regression n=4 |
| Fix-suggestion tool (Fix-in-Cursor product UX) | **Yes, with caveat** — Fix-in-Cursor was exercised in this benchmark and works (produced actionable diffs on multiple threads). Free-tier **403 quota** hit after multiple iterations; per-thread Fix-in-Cursor wall-clock not isolated before the cut-off. Enterprise rate-limit behavior unverified. |

## 7. Anticipated Q&A — and how to answer

| Q | A |
|---|---|
| "Why personal repos and not NetApp code?" | Security/egress. The methodology is repeatable on NetApp code once egress is approved. Personal repos let me run the benchmark unblocked. |
| "Why only 4 PRs? Is the sample large enough?" | 4 PRs is small; that's why findings are **qualitative** (class-specific blind spots, summary regression mechanism, Round-2 false-positive mechanism). The cross-language D4/U4 blind spot was seen on **both** Rust and Go — that survives small sample sizes. |
| "Could results differ on the paid tier?" | Possibly — Round 2 incremental only fired on one of three PRs (suspected free-tier quota). Documented as `NETAPP_RECOMMENDATION.md` §9 gap; worth confirming with CodeAnt support before pilot. |
| "Did Claude really write the fixes?" | **Partially.** CodeAnt's Fix-in-Cursor was used on early iterations (confirmed working, produced actionable diffs). After a free-tier **403 quota** hit mid-session, the remainder of the loop completed with a Claude assistant. Per-thread Fix-in-Cursor wall-clocks were not isolated before the cut-off. Fix-correctness still holds (12/12 toolchain-clean, `go test -race` passes). Wall-clock proxy still shows median 5m 20s/thread under this mixed-assistance setup. |
| "What does CodeAnt say about these findings?" | Haven't asked. The recommendation is pre-vendor-engagement. If we pilot, the §8 rules become the conversation starters with the vendor. |
| "100 % recall on the concurrency arm — why isn't that the headline?" | Round 1 = 100 %. Round 2 on the same PR posted 3 false positives. The headline is the **delta** between R1 and R2, not R1 alone. The manual-gate question is "can human skip review after CodeAnt approves" — R1 doesn't answer that; R2 does. |
| "Does this generalize to Java?" | Zero Java tested. Documented gap. Class-based blind spots may differ for Java (Maven/Spring/annotations). Recommend a Java arm before extending beyond Go. |
| "How does this compare to CodeRabbit or others?" | Not measured. The harness (`fetch_pr.sh` + answer-key format + scoring methodology) is generalized — running the same 4 PRs through CodeRabbit would take ~1 day. Worth doing if leadership wants vendor comparison. |
| "What about CodeAnt as a learning / mentorship tool?" | Genuinely strong on classes it engages. The C3 deadlock review explained `sync.Mutex` non-reentrancy with a clarity exceeding most human review feedback. Advisory mode captures this — supplementary reviewer, not replacement. |
| "If we adopt advisory mode, what's the cost?" | Most of the 8 rules are zero-cost (e.g., "ignore the summary block", "human must check silent-overwrite classes"). Two have ongoing cost: running `golangci-lint + gosec` baseline alongside (essentially free), and confirming Bitbucket integration with the vendor (one email). |
| "Has anything changed since this benchmark?" | Run was 2026-05-14. Vendor behavior can shift; the §5.3 finding mechanism (stale-code reasoning in Round 2) would need to be re-tested before any go-live. Treat findings as a snapshot. |

## 8. What NOT to say in the meeting

| Don't say | Why |
|---|---|
| "CodeAnt is bad." | It isn't. It's strong on specific things. The verdict is about *use-case fit*. |
| "Static analysis can do all this." | It can't — `time.NewTicker` chain, C3 deadlock reasoning, the Sequence Diagram artifact. CodeAnt has clear value-add. |
| "We just need a better gate model." | The §5.3 evidence is about CodeAnt's current Round-2 product behavior, not gate models in general. Until the vendor's product changes, no gate model works. |
| "The summary regression is minor." | It is the single highest-impact finding for the manual-gate question. A human reviewer skimming `✅` before reading code is worse than no automated review at all. |
| "We measured everything we needed." | We didn't. Java, NetApp-scale, historical-replay, enterprise R2, Fix-in-Cursor product UX — all gaps. Be honest in `NETAPP_RECOMMENDATION.md` §9. |

## 9. Closing line

> "My recommendation is **don't gate, do advise**. The benchmark gives us 80 weighted points of evidence about where CodeAnt helps and where it doesn't. The full document is `NETAPP_RECOMMENDATION.md` with provenance to every artifact. Happy to walk through any specific finding in detail."

---

## Tabs to have open during the meeting

1. **`NETAPP_RECOMMENDATION.md`** — open to §5 (Round-2 finding) and §10 (recommendation table)
2. **`docs/BENCHMARK-SUMMARY.md`** — the canonical findings page
3. **One Round-2 false-positive comment** from Ride-Sharing PR #1 — useful as the "show, don't tell" moment if anyone challenges §5.3
4. The class-based recall table in §5.1 above — single most useful visual

## What to send in the calendar invite

- This document (`docs/PRESENTATION-PREP.md`) — the script
- `NETAPP_RECOMMENDATION.md` — the deliverable
- `docs/BENCHMARK-SUMMARY.md` — the canonical findings

If the meeting goes well: agree on whether to proceed with the advisory-mode pilot scope in `NETAPP_RECOMMENDATION.md` §10, and who owns the four follow-up actions (vendor email on quota/Bitbucket, security/egress sign-off, baseline-arm setup, success/exit-criteria sign-off).
