# CodeAnt Benchmarking — PR 1 Answer Key

PR URL: <fill in after PR is opened>
Opened at (ISO-8601 UTC): <fill in after PR is opened>
Repo: vickky06/Rexec
Branch: feat/telemetry-and-lifecycle-improvements
Total weighted defect points available: 20

| ID | File | Defect | Dimension | Severity (weight) | Bot must mention |
|----|------|--------|-----------|--------------------|-------------------|
| D1 | src/services/helper_services/cleanup_service.rs | Hardcoded bearer token | Security | Critical (5) | hardcoded credential / secret in source |
| D2 | src/services/websocket/websocket_server.rs | Logging unredacted client payload | Observability | High (3) | sensitive data in logs / no redaction |
| D3 | src/proto/executor.proto | Field tag changed 2 -> 5 | Compatibility | Critical (5) | wire-breaking proto change / tag is contract |
| D4 | src/services/all_session_services/session_management_service.rs | Removed dup check -> silent overwrite | Resource | High (3) | container leak / orphaned session value |
| D5 | src/services/execution_services/executor_service.rs | Returns Ok(empty) on container error | Correctness | Medium (2) | error swallowed / caller misled |
| D6 | src/services/helper_services/cleanup_service.rs | force: true -> false | Failure-handling | Medium (2) | will fail on running containers / cleanup ineffective |

## Scoring rules

- For each defect, mark CAUGHT (full credit) if CodeAnt's review explicitly
  identifies the problem (not just "this file changed"). Award PARTIAL credit
  (50% of severity weight) if the comment flags the right file/region but
  misses the specific issue.
- Recall % = sum(severity weights of caught defects) / 20 * 100.

## Track separately (do not fold into recall)

- False positives: claims of defects that don't exist.
- Noise: stylistic or preferential suggestions on correct code.
- Summary quality: 1-5 (1 = restates diff; 5 = correct intent + risks + tests).
- Verdict signal: did the bot post a machine-readable pass/fail status?
- Time-to-verdict (minutes from PR open).
- Coverage: files commented / files changed.
- Fix actionability: for each accepted fix applied via Cursor, does
  `cargo check && cargo clippy --all-targets && cargo test` still pass?
