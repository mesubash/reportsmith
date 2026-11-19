"""Self-check for sessions.py: python3 tests/test_sessions.py"""
import json
import os
import sys
import tempfile
from datetime import datetime, time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "skills", "reportsmith", "scripts"))
import sessions as S

tmp = tempfile.mkdtemp()
work, other = os.path.join(tmp, "work"), os.path.join(tmp, "work-other")
os.makedirs(work); os.makedirs(other)
tz = datetime.now().astimezone().tzinfo
lo = datetime.combine(datetime(2026, 11, 19).date(), time.min, tz)
hi = datetime.combine(datetime(2026, 11, 19).date(), time.max, tz)
day = datetime(2026, 11, 19, 10, 0, tzinfo=tz).isoformat()
old = datetime(2026, 11, 1, 10, 0, tzinfo=tz).isoformat()


def write(name, rows):
    p = os.path.join(tmp, name)
    with open(p, "w") as f:
        f.write("\n".join(json.dumps(r) for r in rows))
    return p


claude = write("c.jsonl", [
    {"type": "ai-title", "aiTitle": "Fix payments"},
    {"type": "user", "timestamp": old, "cwd": work, "message": {"content": "old prompt"}},
    {"type": "user", "timestamp": day, "cwd": work, "message": {"content": "fix double charge, token=abc123 on 10.0.0.5"}},
    {"type": "user", "timestamp": day, "cwd": work, "message": {"content": "<system-reminder>noise</system-reminder>"}},
    {"type": "assistant", "timestamp": day, "cwd": work, "message": {"content": [
        {"type": "tool_use", "name": "Edit", "input": {"file_path": os.path.join(work, "pay.py")}},
        {"type": "text", "text": "Fixed and tested."}]}},
])
s = S.read_claude(claude, lo, hi)
assert s["title"] == "Fix payments"
assert len(s["prompts"]) == 1, s["prompts"]          # old + noise dropped
assert s["files"] == {os.path.join(work, "pay.py")}
assert s["answer"] == "Fixed and tested."
out = S.render([dict(s, cwd=work)], [work])
assert "abc123" not in out and "10.0.0.5" not in out, out   # redacted
assert "pay.py" in out

codex = write("rollout-2026-11-19T10-00-00-01a1d364-a1a4-7c33-86d3-726fb31efd45.jsonl", [
    {"type": "session_meta", "timestamp": day, "payload": {"cwd": work}},
    {"type": "response_item", "timestamp": day, "payload": {"type": "message", "role": "user", "content": [
        {"type": "input_text", "text": "<environment_context>x</environment_context>"},
        {"type": "input_text", "text": "add retry"}]}},
    {"type": "response_item", "timestamp": day, "payload": {"type": "custom_tool_call", "input": "*** Update File: src/a.py\n"}},
    {"type": "event_msg", "timestamp": day, "payload": {"type": "task_complete", "last_agent_message": "Retry added."}},
])
c = S.read_codex(codex, lo, hi)
assert c["prompts"] == ["add retry"] and c["files"] == {"src/a.py"} and c["answer"] == "Retry added."

# Scope: sibling folder with shared prefix must not match; exclude wins.
assert S.in_scope(os.path.join(work, "x"), [work], [])
assert not S.in_scope(other, [work], [])
assert not S.in_scope(os.path.join(work, "x"), [work], [os.path.join(work, "x")])
print("ok")

# Paths: inside → relative, agent-internal → dropped, elsewhere → flagged.
assert S.show_path(os.path.join(work, "src", "a.py"), [work]) == os.path.join("src", "a.py")
assert S.show_path(os.path.join(work, "a", "b", "c", "d.py"), [work]) == os.path.join("a", "…", "d.py")
assert S.show_path(os.path.expanduser("~/.claude/x/memory/m.md"), [work]) is None
assert S.show_path("/opt/elsewhere/proj/f.py", [work]).startswith("outside:")
print("ok paths")

# Extra redaction patterns from config.
S.REDACT.append((S.re.compile(r"acme-internal-\w+"), "[redacted]"))
assert S.redact("deployed to acme-internal-db7") == "deployed to [redacted]"
print("ok redact")
