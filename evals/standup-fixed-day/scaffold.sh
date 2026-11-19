#!/usr/bin/env bash
# Fixture: one repo, one fixed day (2026-03-10), a cherry-picked duplicate,
# a commit on the next day, a teammate's commit, and one Claude Code session
# whose only result is not in git.
set -eu
echo "scaffold pwd=$PWD HOME=$HOME" > scaffold-debug.txt
env | grep -E '^(EVAL|SCAFFOLD|WORK|CLAUDE)' | sed 's/=.*//' >> scaffold-debug.txt || true
git init -q -b main app && cd app
git config user.email dev@example.com && git config user.name Dev
c() { GIT_AUTHOR_DATE="$1" GIT_COMMITTER_DATE="$1" git commit -q --allow-empty -m "$2"; }
c "2026-03-09T16:00:00" "chore: set up project"
c "2026-03-10T09:30:00" "fix(payment): stop a second card charge while the first is unconfirmed (PAY-12)"
c "2026-03-10T14:10:00" "feat(export): add CSV export of invoices (INV-7)"
git checkout -q -b release
git cherry-pick -q --keep-redundant-commits main~1 2>/dev/null || true
git checkout -q main
GIT_AUTHOR_DATE="2026-03-10T11:00:00" GIT_COMMITTER_DATE="2026-03-10T11:00:00" \
  git -c user.email=teammate@example.com -c user.name=Mate commit -q --allow-empty -m "docs: rewrite onboarding guide"
c "2026-03-11T10:00:00" "fix(auth): refresh tokens before expiry (AUTH-3)"
cd ..
proj="$HOME/.claude/projects/$(echo "$PWD/app" | sed 's#[/.]#-#g')"
mkdir -p "$proj"
python3 - "$proj/fixture.jsonl" "$PWD/app" <<'PY'
import json, sys
path, cwd = sys.argv[1], sys.argv[2]
rows = [
  {"type": "ai-title", "aiTitle": "Restart stuck queue worker"},
  {"type": "user", "timestamp": "2026-03-10T12:00:00Z", "cwd": cwd,
   "message": {"content": "the invoice queue worker on staging is stuck, can you check and restart it"}},
  {"type": "assistant", "timestamp": "2026-03-10T12:20:00Z", "cwd": cwd,
   "message": {"content": [{"type": "text", "text": "Restarted the invoice queue worker on staging; 214 queued jobs drained and the queue is empty now."}]}},
  {"type": "user", "timestamp": "2026-03-10T12:25:00Z", "cwd": cwd,
   "message": {"content": "also look into why the nightly backup failed"}},
]
open(path, "w").write("\n".join(json.dumps(r) for r in rows))
PY
