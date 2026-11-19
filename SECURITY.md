# Security and privacy

reportsmith reads sensitive material: your git history and your coding agents' session logs. This page says what it reads, what it can send, and where the limits are.

## What it reads

Only when you ask for a report, and only inside the folder scope and period you choose:

- git history of repos under the scope
- agent session logs on your machine, read-only: `~/.claude/projects`, `~/.codex/sessions`, `~/.local/share/opencode/opencode.db`
- if available: `gh` (your PRs and reviews), connected MCP servers (tickets, agent memory), your notes file, and your config, templates and style samples

The session reader (`scripts/sessions.py`) prints a short digest: titles, the first and last prompts, file names, and the last answer, each cut to a few hundred characters. The agent is told to use only this digest and never open raw transcripts.

## What leaves your machine

Nothing, unless you publish. Publishing sends the finished report to the destinations you configured or named, after you approve the preview. Unattended runs (`publish.confirm: false`) skip that approval, so use them only with destinations you trust.

Separately, your coding agent sends what it reads to its model provider, as it does for any task. That includes the session digest and git output. If that is a problem for a scope, exclude it.

reportsmith has no server and no telemetry.

## Redaction limits

Before drafting, reportsmith removes common secret formats (API keys and tokens, private keys, `password=` style values, bearer tokens), IP addresses, and any patterns you add in `redact.patterns`. This is pattern matching, not a guarantee: an unusual secret format can get through. Read the preview before you publish, and add patterns for anything specific to your work.

Destination credentials never go in the config. Webhook URLs come from environment variables; MCP servers use their own sign-in.

## Reporting a vulnerability

Use GitHub's private vulnerability reporting on this repository (Security tab, "Report a vulnerability"). Please don't open a public issue for security problems.
