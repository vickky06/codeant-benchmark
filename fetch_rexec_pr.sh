#!/usr/bin/env bash
# Fetch GitHub PR JSON artifacts for vickky06/Rexec (CodeAnt / manual scoring).
# Usage: export GH_TOKEN=ghp_xxx && ./fetch_rexec_pr.sh 8
#        export GH_TOKEN=ghp_xxx && ./fetch_rexec_pr.sh 7 pr7-round2   # custom folder (e.g. second review)
set -euo pipefail

PR="${1:?Usage: $0 <PR_NUMBER> [OUTPUT_DIR]}"
OUT_NAME="${2:-pr${PR}}"
REPO="vickky06/Rexec"
DIR="$(cd "$(dirname "$0")" && pwd)"
OUT="${DIR}/${OUT_NAME}"
mkdir -p "$OUT"

if [[ -z "${GH_TOKEN:-}" ]]; then
  echo "ERROR: export GH_TOKEN first" >&2
  exit 1
fi

fetch() {
  local path=$1 out=$2
  curl -sS \
    -H "Accept: application/vnd.github+json" \
    -H "Authorization: Bearer $GH_TOKEN" \
    "https://api.github.com/repos/$REPO/$path" \
    -o "$out"
  echo "  -> $out ($(wc -c < "$out") bytes)"
}

echo "Fetching Rexec PR #$PR into $OUT/ ..."
fetch "pulls/$PR"                        "$OUT/pr_meta.json"
fetch "pulls/$PR/comments?per_page=100"  "$OUT/pr_inline_comments.json"
fetch "pulls/$PR/reviews?per_page=100"   "$OUT/pr_reviews.json"
fetch "issues/$PR/comments?per_page=100" "$OUT/pr_issue_comments.json"

for f in "$OUT"/*.json; do
  if jq -e '.message? | strings' "$f" >/dev/null 2>&1; then
    echo "ERROR in $f:" >&2; cat "$f" >&2; exit 1
  fi
done

echo "Done. Open $OUT/ — PR8 scoring: docs/PR2-clean-control-spec.md — PR7 round-2 log: docs/PR7-ROUND2-EXECUTION-LOG.md"
