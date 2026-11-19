#!/usr/bin/env bash
# Fixture for folder scope over a week (Mon 2026-03-09 to Sun 2026-03-15):
#   work/api      in scope: two commits this week, one the week before
#   work/web      in scope: one commit this week
#   work/archive  excluded: one commit this week
#   side/blog     outside scope: one commit this week, plus a Claude Code session
#   a Codex session in work/web whose result is not in git
set -eu
repo() {  # repo <path> then "date|message" lines on stdin
  mkdir -p "$1" && ( cd "$1" && git init -q -b main && git config user.email dev@example.com && git config user.name Dev
    while IFS='|' read -r d m; do GIT_AUTHOR_DATE="$d" GIT_COMMITTER_DATE="$d" git commit -q --allow-empty -m "$m"; done )
}
repo work/api <<'X'
2026-03-04T10:00:00|feat(api): add rate limit headers (API-1)
2026-03-09T11:00:00|fix(api): return 404 instead of 500 for unknown invoices (API-4)
2026-03-12T15:00:00|feat(api): paginate the invoices endpoint (API-5)
X
repo work/web <<'X'
2026-03-10T09:00:00|feat(web): show invoice status badges (WEB-2)
X
repo work/archive <<'X'
2026-03-11T10:00:00|chore(archive): migrate legacy reports (OLD-9)
X
repo side/blog <<'X'
2026-03-13T20:00:00|post: write about sourdough starters
X
python3 - "$HOME" "$PWD" <<'PY'
import json, os, sys
home, root = sys.argv[1], sys.argv[2]
def jsonl(path, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w").write("\n".join(json.dumps(r) for r in rows))
blog = os.path.join(root, "side/blog")
jsonl(os.path.join(home, ".claude/projects", blog.replace("/", "-").replace(".", "-"), "s1.jsonl"), [
  {"type": "ai-title", "aiTitle": "Blog theme"},
  {"type": "user", "timestamp": "2026-03-13T19:00:00Z", "cwd": blog, "message": {"content": "change the blog theme to dark"}},
  {"type": "assistant", "timestamp": "2026-03-13T19:30:00Z", "cwd": blog, "message": {"content": [{"type": "text", "text": "Switched the blog to the dark theme."}]}},
])
web = os.path.join(root, "work/web")
jsonl(os.path.join(home, ".codex/sessions/2026/03/11/rollout-2026-03-11T10-00-00-0000aaaa-bbbb-cccc-dddd-eeeeffff0000.jsonl"), [
  {"type": "session_meta", "timestamp": "2026-03-11T04:00:00Z", "payload": {"cwd": web}},
  {"type": "response_item", "timestamp": "2026-03-11T04:00:05Z", "payload": {"type": "message", "role": "user", "content": [{"type": "input_text", "text": "users report the dashboard is slow, find out why"}]}},
  {"type": "event_msg", "timestamp": "2026-03-11T04:40:00Z", "payload": {"type": "task_complete", "last_agent_message": "Found it: the dashboard loads all invoices at once. Added an index on invoices.customer_id in staging; the page now loads in 0.4s instead of 6s."}},
])
PY
