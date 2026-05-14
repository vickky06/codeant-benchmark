#!/usr/bin/env bash
# Fetch GitHub PR JSON artifacts (CodeAnt / manual scoring) for any repo.
# Uses the authenticated `gh` CLI — no GH_TOKEN env var needed.
#
# Usage:
#   ./fetch_pr.sh <owner/repo> <PR_NUMBER> [OUTPUT_DIR]
# Examples:
#   ./fetch_pr.sh vickky06/Rexec 7                  # -> pr7/
#   ./fetch_pr.sh vickky06/Uber-Eats 1 uber-eats-pr1
#   ./fetch_pr.sh vickky06/Rate-Limiter 1 rate-limiter-pr1
set -euo pipefail

REPO="${1:?Usage: $0 <owner/repo> <PR_NUMBER> [OUTPUT_DIR]}"
PR="${2:?Usage: $0 <owner/repo> <PR_NUMBER> [OUTPUT_DIR]}"
OUT_NAME="${3:-pr${PR}}"
DIR="$(cd "$(dirname "$0")" && pwd)"
OUT="${DIR}/${OUT_NAME}"
mkdir -p "$OUT"

if ! command -v gh >/dev/null 2>&1; then
  echo "ERROR: gh CLI not on PATH" >&2
  exit 1
fi

fetch() {
  local path=$1 out=$2
  gh api "repos/$REPO/$path" --paginate > "$out"
  echo "  -> $out ($(wc -c < "$out") bytes)"
}

echo "Fetching $REPO PR #$PR into $OUT/ ..."
fetch "pulls/$PR"                        "$OUT/pr_meta.json"
fetch "pulls/$PR/comments?per_page=100"  "$OUT/pr_inline_comments.json"
fetch "pulls/$PR/reviews?per_page=100"   "$OUT/pr_reviews.json"
fetch "issues/$PR/comments?per_page=100" "$OUT/pr_issue_comments.json"

# Sanity: any of these contain an API error envelope?
for f in "$OUT"/*.json; do
  if jq -e '.message? | strings' "$f" >/dev/null 2>&1; then
    echo "ERROR in $f:" >&2; cat "$f" >&2; exit 1
  fi
done

echo "Done. Open $OUT/ to score against the matching answer key."
