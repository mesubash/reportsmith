#!/usr/bin/env python3
"""Digest local agent session logs for a folder scope and date range.

Reads Claude Code and Codex session logs, keeps sessions whose working
directory is inside the scope and that have activity in the range, and
prints a short redacted markdown digest. Raw transcripts never leave this
script. Stdlib only.

Usage:
  sessions.py --from 2026-11-19 --to 2026-11-19 --include ~/work \
              [--exclude PATH ...] [--agents claude-code,codex]
"""
import argparse
import glob
import json
import os
import re
from datetime import datetime, time, timezone

MAX_PROMPTS = 12
PROMPT_CHARS = 240
ANSWER_CHARS = 500

REDACT = [
    (re.compile(r"\b(sk-[A-Za-z0-9_-]{16,}|gh[opsu]_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|xox[abp]-[A-Za-z0-9-]{10,})"), "[secret]"),
    (re.compile(r"(?i)\b(password|passwd|secret|token|api[_-]?key)\s*[:=]\s*\S+"), r"\1=[secret]"),
    (re.compile(r"(?i)bearer\s+[A-Za-z0-9._-]{12,}"), "Bearer [secret]"),
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----", re.S), "[private key]"),
    (re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"), "[ip]"),
]


def redact(text):
    for pattern, repl in REDACT:
        text = pattern.sub(repl, text)
    return text


def clip(text, n):
    text = " ".join(text.split())
    return text if len(text) <= n else text[: n - 1] + "…"


def parse_ts(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone()
    except ValueError:
        return None


def in_scope(cwd, include, exclude):
    if not cwd:
        return False
    cwd = os.path.realpath(cwd)

    def inside(root):
        root = os.path.realpath(root)
        return cwd == root or cwd.startswith(root + os.sep)

    return any(inside(r) for r in include) and not any(inside(r) for r in exclude)


def is_noise(text):
    # Harness-injected blocks (system reminders, env context, command wrappers).
    return not text.strip() or text.lstrip().startswith("<")


def new_session(agent, sid):
    return {"agent": agent, "id": sid, "cwd": None, "title": None, "start": None,
            "end": None, "prompts": [], "files": set(), "answer": None}


def touch(s, ts):
    s["start"] = ts if s["start"] is None or ts < s["start"] else s["start"]
    s["end"] = ts if s["end"] is None or ts > s["end"] else s["end"]


def read_claude(path, lo, hi):
    s = new_session("claude-code", os.path.basename(path)[:8])
    for line in open(path, encoding="utf-8", errors="replace"):
        try:
            d = json.loads(line)
        except ValueError:
            continue
        t = d.get("type")
        if t == "custom-title":
            s["title"] = d.get("customTitle")
        elif t == "ai-title" and not s["title"]:
            s["title"] = d.get("aiTitle")
        ts = parse_ts(d.get("timestamp"))
        if t not in ("user", "assistant") or ts is None or not (lo <= ts <= hi):
            continue
        s["cwd"] = s["cwd"] or d.get("cwd")
        touch(s, ts)
        content = d.get("message", {}).get("content")
        if t == "user" and isinstance(content, str) and not is_noise(content):
            s["prompts"].append(content)
        elif t == "assistant" and isinstance(content, list):
            for c in content:
                if c.get("type") == "text" and c.get("text", "").strip():
                    s["answer"] = c["text"]
                elif c.get("type") == "tool_use" and c.get("name") in ("Edit", "Write", "NotebookEdit"):
                    fp = c.get("input", {}).get("file_path") or c.get("input", {}).get("notebook_path")
                    if fp:
                        s["files"].add(fp)
    return s


PATCH_FILE = re.compile(r"\*\*\* (?:Update|Add|Delete) File: (\S+)")


def read_codex(path, lo, hi):
    s = new_session("codex", os.path.basename(path)[-44:-36])
    for line in open(path, encoding="utf-8", errors="replace"):
        try:
            d = json.loads(line)
        except ValueError:
            continue
        p = d.get("payload") or {}
        if d.get("type") in ("session_meta", "turn_context") and p.get("cwd"):
            s["cwd"] = p["cwd"]
        ts = parse_ts(d.get("timestamp"))
        if ts is None or not (lo <= ts <= hi):
            continue
        kind = p.get("type")
        if d.get("type") == "response_item" and kind == "message" and p.get("role") == "user":
            touch(s, ts)
            for c in p.get("content", []):
                text = c.get("text", "")
                if c.get("type") == "input_text" and not is_noise(text):
                    s["prompts"].append(text)
        elif d.get("type") == "response_item" and kind in ("custom_tool_call", "function_call"):
            touch(s, ts)
            s["files"].update(PATCH_FILE.findall(str(p.get("input") or p.get("arguments") or "")))
        elif d.get("type") == "event_msg" and kind == "task_complete" and p.get("last_agent_message"):
            touch(s, ts)
            s["answer"] = p["last_agent_message"]
    return s


def candidates(pattern, lo):
    cutoff = lo.timestamp()
    return [f for f in glob.glob(os.path.expanduser(pattern), recursive=True)
            if os.path.getmtime(f) >= cutoff]


READERS = {
    "claude-code": ("~/.claude/projects/*/*.jsonl", read_claude),
    "codex": ("~/.codex/sessions/**/*.jsonl", read_codex),
}


def collect(lo, hi, include, exclude, agents):
    out = []
    for agent in agents:
        pattern, reader = READERS[agent]
        for f in candidates(pattern, lo):
            s = reader(f, lo, hi)
            if s["start"] and in_scope(s["cwd"], include, exclude) and (s["prompts"] or s["answer"]):
                out.append(s)
    return sorted(out, key=lambda s: s["start"])


AGENT_DIRS = tuple(os.path.realpath(os.path.expanduser(d)) + os.sep
                   for d in ("~/.claude", "~/.codex", "~/.config/opencode"))


def short(parts):
    return os.sep.join(parts) if len(parts) <= 3 else os.sep.join([parts[0], "…", parts[-1]])


def show_path(path, roots):
    """Path relative to the scope root it is in; None for agent-internal files;
    'outside:' prefix when the session edited files outside the scope."""
    if not path.startswith("/"):
        return path
    real = os.path.realpath(path)
    if real.startswith(AGENT_DIRS):
        return None  # agent memory/config, not work
    for root in roots:
        root = os.path.realpath(root)
        if real.startswith(root + os.sep):
            return short(os.path.relpath(real, root).split(os.sep))
    return "outside:" + short(real.split(os.sep)[-3:])


def render(sessions, roots):
    if not sessions:
        return "_No agent sessions in scope for this period._\n"
    lines = []
    for s in sessions:
        head = f"### {s['agent']} · {s['start']:%Y-%m-%d %H:%M}–{s['end']:%H:%M} · {s['cwd']}"
        lines.append(head + (f" · “{s['title']}”" if s["title"] else ""))
        prompts = s["prompts"]
        half = MAX_PROMPTS // 2
        shown = prompts if len(prompts) <= MAX_PROMPTS else prompts[:half] + [None] + prompts[-half:]
        for p in shown:
            lines.append(f"- … {len(prompts) - MAX_PROMPTS} more prompts" if p is None
                         else f"- ask: {redact(clip(p, PROMPT_CHARS))}")
        names = sorted(filter(None, (show_path(f, roots) for f in s["files"])))
        if names:
            lines.append(f"- files edited ({len(names)}): {', '.join(names[:15])}")
        if s["answer"]:
            lines.append(f"- last answer: {redact(clip(s['answer'], ANSWER_CHARS))}")
        lines.append("")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="frm", required=True, help="YYYY-MM-DD, local time")
    ap.add_argument("--to", required=True, help="YYYY-MM-DD, inclusive")
    ap.add_argument("--include", action="append", required=True)
    ap.add_argument("--exclude", action="append", default=[])
    ap.add_argument("--agents", default=",".join(READERS))
    a = ap.parse_args()
    tz = datetime.now(timezone.utc).astimezone().tzinfo
    lo = datetime.combine(datetime.fromisoformat(a.frm).date(), time.min, tz)
    hi = datetime.combine(datetime.fromisoformat(a.to).date(), time.max, tz)
    norm = lambda ps: [os.path.realpath(os.path.expanduser(p)) for p in ps]
    agents = [x for x in a.agents.split(",") if x in READERS]
    include = norm(a.include)
    print(render(collect(lo, hi, include, norm(a.exclude), agents), include))


if __name__ == "__main__":
    main()
