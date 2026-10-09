#!/usr/bin/env bash
# Commit + push one finished step (session 3 rule: "commit and push to the same branch after every step").
# Serialised across all agents by a lock, so parallel agents never race on the git index.
#   pipeline/jawad_reels/tools/commit_step.sh "<one-line message>" <path> [<path> ...]
# Only the given paths are staged. Refuses files >= 95 MB (GitHub's hard limit is 100 MB; no LFS on this repo).
# workspace/ is git-ignored: copy anything worth keeping into brand_reels/ or reel/ first.
set -u
BRANCH=claude/beautiful-planck-mtdn0c
REPO=/home/user/100
[ $# -ge 2 ] || { echo "usage: $0 \"message\" path..." >&2; exit 2; }
msg="$1"; shift
mkdir -p "$REPO/workspace/jawad_reels/locks"
exec 9>"$REPO/workspace/jawad_reels/locks/git.lock"
flock 9
cd "$REPO" || exit 1
for p in "$@"; do
  if [ -e "$p" ]; then
    big=$(find "$p" -type f -size +95M 2>/dev/null | head -5)
    if [ -n "$big" ]; then echo "REFUSED: files >= 95 MB: $big" >&2; exit 3; fi
  fi
done
git add -A -- "$@" || exit 1
if git diff --cached --quiet; then echo "nothing to commit"; exit 0; fi
git commit -q -m "$msg

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01N8UkVXghpsVSJ8xNkDkkj9" || exit 1
for d in 0 2 4 8 16; do
  sleep $d
  if git push -u origin "$BRANCH" >/dev/null 2>&1; then git log --oneline -1; exit 0; fi
  git pull -q --no-rebase origin "$BRANCH" >/dev/null 2>&1 || true
done
echo "PUSH FAILED (commit kept locally)" >&2
exit 4
