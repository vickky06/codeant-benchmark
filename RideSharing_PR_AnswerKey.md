# CodeAnt Benchmarking — Ride-Sharing Answer Key

**PR URL:** https://github.com/vickky06/Ride-Sharing-Trip-Manager/pull/1
**Repo:** `vickky06/Ride-Sharing-Trip-Manager`
**Branch:** `feat/dispatch-dashboard-and-autopilot`
**Baseline:** Go 1.24, `go test ./...` passes on PR head. `go test -race ./...` should fail (expected — exercises C1/C4).
**Total weighted defect points available:** 20

Concurrency-focused third arm. The first two Go PRs (`UberEats`, `RateLimiter`) seeded one resource-class concurrency defect (RL4 goroutine leak — caught) but no true data races, deadlocks, or lock-contract violations — gaps explicitly documented in `docs/Go-Corpus-Design.md`. This corpus closes that gap.

## Seeded defects

| ID | File | Defect | Dimension | Severity (weight) | Bot must mention |
|----|------|--------|-----------|--------------------|-------------------|
| C1 | `internal/orchestrator/trip_service.go` (new `GetAllStates`) | Reads `s.trips` map and each `t.State` field **without any lock** (neither `s.mu.RLock()` nor `t.Lock()`); concurrent `Transition` / `RequestRide` mutate both. `go test -race` will catch. | Race | Critical (6) | data race / concurrent map iteration / read without lock / `-race` |
| C2 | `internal/orchestrator/trip_service.go` (modified `AssignDriver`) | Per-call goroutine `go func() { for { time.Sleep(15s); log.Printf("[ETA] …") } }()` — no stop channel, no `context.Context`, no shutdown signal. Closure pinned by infinite loop, no GC reclamation. | Goroutine leak | Critical (5) | goroutine leak / never terminates / no shutdown / context.Context / stop channel |
| C3 | `internal/statemachine/statemachine.go` (Accepted→InProgress Action) + `internal/orchestrator/trip_service.go` (`NewTripService` wiring) | Action runs **while outer `Apply` still holds `t.mu`**; for `t.DriverID == "AUTOPILOT"` it calls `sm.svc.Transition(t.ID, Completed)` which re-enters `Apply` → tries `t.Lock()` again → **deadlock**. | Deadlock / reentrant lock | Critical (5) | reentrant / recursive lock / deadlock / callback under lock / re-entry |
| C4 | `internal/orchestrator/trip_service.go` (new `Cancel`) | `delete(s.trips, tripID)` executes while holding `s.mu.RLock()` — **mutation under read lock**; concurrent `getTrip` / `GetAllStates` see an inconsistent map. | Mutex misuse / race | High (4) | RLock / write under read lock / mutation under read lock / map race |

## Bonus unseeded defects (not counted toward the 20 points)

These exist on main and remain through this PR. Track separately as unseeded recall.

| Bonus | File:Line | Defect |
|---|---|---|
| B1 | `internal/orchestrator/trip_service.go:88` (renumbered after edits) | `from := t.State` read **outside** the trip lock — `Apply` later takes `t.Lock()`, but `from` was already captured. Concurrent `Transition` can mutate `t.State` between the read and the `Publish` → stale `TripEvent.From`. Real lock-contract violation. |
| B2 | `internal/eventbus/eventbus.go:25-31` | `Publish` spawns `len(observers)` goroutines per event, **no backpressure**, no panic recovery, no bounded queue. DoS surface as observer set or publish rate grows. |

## Bonus *deterministic*-tool baseline

These defects should be partly caught by **`go test -race`** and **`go vet`** without any AI:

| Defect | `-race` catches? | `go vet` flags? | Notes |
|---|---|---|---|
| C1 (lockless read) | **Yes** (under concurrent test load) | No | Static analysis won't see it; runtime detector will |
| C2 (goroutine leak) | No | No | Standard tools don't track lifetime |
| C3 (deadlock) | No | No | Triggered only by AUTOPILOT path; even `-race` won't unless test exercises it |
| C4 (write under RLock) | **Yes** (race detector) | No | Race detector sees the concurrent read + delete |

This means **C2 and C3 are CodeAnt's two clearest opportunities to demonstrate value beyond the baseline.** Score these specifically when comparing CodeAnt's marginal recall over `go test -race`.

## Scoring rules

Same as `UberEats_PR_AnswerKey.md`: CAUGHT (full weight if comment identifies the issue), PARTIAL (½ if region only), MISSED (0).

Recall = caught_weight / 20 × 100.

Track separately: false positives, noise, summary quality (1–5), verdict signal, latency, coverage, **unseeded recall** (B1, B2).

## Adversarial framing in the PR

Cover story positions each defect as a plausible feature:

| PR body bullet | Defect framed as feature |
|---|---|
| "GetAllStates: snapshot of every trip's state for the dispatch dashboard…" | C1 — lockless reads |
| "ETA streamer: spawn a per-trip goroutine on AssignDriver…" | C2 — leak |
| "Autopilot auto-complete: when an AUTOPILOT trip enters InProgress, the state machine drives it straight to Completed via the new Service callback" | C3 — reentrant lock |
| "Cancel(): fast cancel-then-cleanup path; reads the trip under RLock so multiple cancels for different trips can run in parallel" | C4 — write under RLock |

Use this table when scoring summary quality. If the bot's auto-summary endorses any of the left-column phrasing with `✅` while inline (or not even inline) flags the right-column concern, that's another summary-regression data point.

## Manual-gate operational rule (proposed)

For the NetApp manual blocking gate, treat **C1 and C4** (both data races detectable by `go test -race`) as **must-flag-or-baseline-tool-must-catch**. If CodeAnt misses *and* `go test -race` is not part of NetApp's pre-merge CI, the gate has zero coverage on concurrency hazards.

C2 and C3 are the higher-value tests for "AI reviewer beats deterministic tools": no standard Go tool catches them statically. A miss on C2/C3 is the strongest argument that CodeAnt does not yet replace a careful human reviewer for Go concurrency-critical code.

## Round 1 capture (after CodeAnt finishes)

```bash
./fetch_pr.sh vickky06/Ride-Sharing-Trip-Manager 1 ride-sharing-pr1
```

Score the resulting `ride-sharing-pr1/pr_inline_comments.json` against the C1–C4 table; aggregate into `RideSharing_PR_Score.md` mirroring `UberEats_PR_Score.md` / `RateLimiter_PR_Score.md`.

## Fix-me loop targets (highest signal for adoption-cost data)

After Round 1 scoring, pick the top 3 by severity that CodeAnt **caught**. Most likely candidates if recall is high:

1. **C1** — add `s.mu.RLock()` around the map iteration and `t.Lock()`/`t.Unlock()` around each `t.State` read (or refactor to a per-trip lock-and-snapshot helper).
2. **C2** — add a `stop chan struct{}` to TripService, close it on shutdown, `select` against `<-stop` in the ETA goroutine.
3. **C3** — defer the auto-complete to *after* the outer `Apply` returns (e.g., via a deferred channel or by returning a "next state" from Action instead of recursing).

Record per-thread wall-clock + `go build ./... && go vet ./... && go test ./... && go test -race ./...` after each.
