# PR 2 — Clean control (no seeded defects)

**Purpose:** Measure **false positives** and **noise** on a small, legitimate change. PR 1 alone cannot show whether the bot is chatty or over-alarmist.

**Target repo:** [vickky06/Rexec](https://github.com/vickky06/Rexec)

**Opened PR:** https://github.com/vickky06/Rexec/pull/8

## Branch (local / to push)

- **Branch name:** `feat/max-code-length-validation`
- **Commit (local clone):** `0576b53` — *feat: add max code length validation to prevent oversized payloads*
- **Files:** `config.toml`, `src/models/config_models.rs`, `src/models/validation_models.rs`, `src/services/validation_services/request_validation/validation_service.rs` (4 files, +17 LOC).

## Behavior

- Adds `session_configs.max_code_length` (default `100_000`) in `config.toml` and `SessionConfigs`.
- Adds `ValidationError::CodeTooLarge { actual, max }`.
- After empty-code check, rejects when `code.len() > max_code_length`.

## PR title / body

Use the same title as the commit subject line, and a body that **does not** claim anything extraordinary — this PR should read as a normal hygiene improvement.

## Scoring (when CodeAnt has reviewed)

- **False positives:** count inline comments that assert a **non-existent** defect.
- **Noise:** stylistic / preference comments on correct code (separate from FP).
- **Summary quality (1–5):** does the bot’s PR summary match intent without inventing risks?
- **Latency:** time from PR open → “finished reviewing” (warm path vs PR 1 cold ~9 min).

## Validation

```bash
cargo check
cargo clippy --all-targets --no-deps   # may fail on pre-existing Rexec clippy; document if so
cargo test
```
