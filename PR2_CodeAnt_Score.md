# CodeAnt PR 2 (clean control) — Scored Report

**PR:** https://github.com/vickky06/Rexec/pull/8  
**Title:** feat: add max code length validation to prevent oversized payloads  
**Design:** No seeded defects — measures **false positives**, **noise**, **summary quality**, and **warm-path latency** vs PR [#7](https://github.com/vickky06/Rexec/pull/7).

## Timeline (UTC)

| Milestone | Time |
|-----------|------|
| PR opened | `2026-05-13T10:02:00Z` |
| CodeAnt review submitted | `2026-05-13T10:06:08Z` |
| “Finished reviewing” issue comment | `2026-05-13T10:06:13Z` |

**Warm latency (open → finished): ~4 min 13 s** — materially faster than PR 1’s **~9 min** cold start on the same repo.

## Verdict signal

`pr_reviews.json`: single CodeAnt review with `state: "COMMENTED"`, empty `body` — same pattern as PR 1. Treat merge-gating as **unconfirmed** until you verify **Checks** on the PR.

## Inline comments (CodeAnt)

**Count:** 2 (both substantive; neither asserts a fake bug.)

| File | gist |
|------|------|
| `src/models/config_models.rs` | New `max_code_length` is required in TOML with no default — older `config.toml` will fail at startup (backward-compat / rollout risk). |
| `src/services/validation_services/request_validation/validation_service.rs` | Extra `get_global_config(...).await` + full clone inside hot path; suggests reusing earlier config access. |

### False positives

**0** — both comments describe real design/ops concerns for this change.

### Noise (style-only)

**0**

## Coverage

- **Files changed:** 4 (`pr_meta.json` `changed_files`)
- **Files with CodeAnt inline comments:** 2 (`config_models.rs`, `validation_service.rs`)
- **Coverage:** **2 / 4 = 50%** (`config.toml` and `validation_models.rs` had no inline comments)

## Summary quality (CodeAnt-AI block in PR body)

**4 / 5** — Accurately describes rejection of oversized code, error shape, and configurable limit; tone is proportional (unlike PR 1 where the summary endorsed harmful changes). Minor: still template-ish “Impact” bullets.

## One-line judgment

PR 2 shows **low noise, zero false positives, faster warm review**, and **reasonable** summary alignment — a good control for comparing against PR 1’s defect-rich behavior.
