#!/bin/bash
# ============================================================
# sync-upstream.sh — Safe openclawd upstream sync for clawd/MIST
# Upstream: https://github.com/ComposioHQ/secure-openclaw
# Protected files (listed in workspace/protected-files.txt)
# are NEVER overwritten by upstream changes.
# ============================================================

set -e

REPO_ROOT=$(git rev-parse --show-toplevel)
PROTECTED="$REPO_ROOT/workspace/protected-files.txt"

echo "[sync-upstream] Adding upstream remote (if not exists)..."
git remote get-url upstream 2>/dev/null || \
  git remote add upstream https://github.com/ComposioHQ/secure-openclaw.git

echo "[sync-upstream] Fetching upstream..."
git fetch upstream

echo "[sync-upstream] Switching to upstream-sync branch..."
git checkout upstream-sync 2>/dev/null || git checkout -b upstream-sync

echo "[sync-upstream] Merging upstream/master (no auto-commit)..."
git merge upstream/master --no-commit --no-ff || true

echo "[sync-upstream] Restoring protected files from main..."
while IFS= read -r file || [ -n "$file" ]; do
  # Skip blank lines and comments
  [[ -z "$file" || "$file" == \#* ]] && continue
  # Handle directory entries (trailing /)
  if [[ "$file" == */ ]]; then
    git checkout main -- "${file%/}/" 2>/dev/null || true
  else
    git checkout main -- "$file" 2>/dev/null || true
  fi
  echo "  [protected] restored: $file"
done < "$PROTECTED"

echo ""
echo "[sync-upstream] Done. Protected files restored."
echo "Review the diff below, then commit and merge to main:"
echo "  git diff --cached"
echo "  git commit -m \"chore: sync upstream openclawd [ST]\""
echo "  git checkout main && git merge upstream-sync"
