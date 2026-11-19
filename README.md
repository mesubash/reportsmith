# reportsmith

An agent skill that writes your work reports (standups, daily logs, weekly and monthly updates, changelogs, release notes) from everything you did in a folder: git commits **and the sessions of every coding agent you used there**. Then it publishes them wherever your agent can reach through MCP.

Works with any agent that supports the open `SKILL.md` skill format (Claude Code, Codex, and others). No server, no database, no tracking: it runs when you ask, makes a report, and stops.

> **Status:** v0.1 (private). Publishing through MCP is next.

## Why

Tickets show only part of the work. Code reviews, audits, database fixes, incidents and helping teammates rarely land in a ticket, so they disappear from status updates. Your agent can already see your repos, your PRs and (through MCP) your tracker, chat and wiki. reportsmith turns that into the report you need, in the format your team wants.

## What it does

```
scope: ~/work, any period
sources                         render                     publish
───────                         ──────                     ───────
git (every repo in scope)  ─┐                          ┌─► file (default)
agent sessions in scope    ─┤                          ├─► any MCP tool: Slack, Notion,
  (Claude Code, Codex)      ├─► template + config  ─►  │    Confluence, Jira, Linear, Plane, …
agent memory (claude-mem)  ─┤    preview / confirm     ├─► webhook
PRs, tickets, notes        ─┘                          └─► shell command (e.g. gh release)
```

Most real work never reaches a commit: triage, incident handling, server fixes, reviews, investigations. It does happen in agent sessions. reportsmith reads the session logs your agents already keep on disk, filtered to the folder you choose, so one report covers work done in Claude Code, Codex, or both.

- **Any scope:** `~/work/` for your job, `~/side-project/` for yourself, one folder per client. Repos under it are found automatically.
- **Any period:** a day, week, month, quarter, `last 10 days`, or `Nov 1..Nov 15`, with a threshold that switches long ranges to weekly or monthly roll-ups.
- **Report kinds:** standup, daily, weekly, monthly, changelog, release notes, or your own.
- **Honest:** never invents items; something an agent was asked to do counts as done only if a commit or the agent's answer confirms it.
- **Customizable through files only:** templates are markdown, config is YAML, per repo or global.
- **Works with any destination:** publishing goes through whatever MCP servers you have connected. Adding a destination means adding config, not code.
- **Private by default:** redaction before preview, nothing published without confirmation unless you turn that off.

## Install

reportsmith is a folder with a `SKILL.md`. Put it where your agent looks for skills:

```sh
git clone git@github.com:mesubash/reportsmith.git
```

| Agent | Location |
|---|---|
| Claude Code | `~/.claude/skills/reportsmith/` (all projects) or `.claude/skills/reportsmith/` (one repo) |
| Codex | `~/.codex/skills/reportsmith/` |
| Other agents with Agent Skills support | Their skills directory (see the agent's docs) |
| Agents without skill support | Keep the folder anywhere and add to `AGENTS.md`: *"For standups, status reports or changelogs, follow `<path>/reportsmith/SKILL.md`."* |

Example, Claude Code:

```sh
git clone git@github.com:mesubash/reportsmith.git ~/.claude/skills/reportsmith
```

Then ask your agent: *"standup"*, *"weekly report for my manager"*, *"changelog since v1.2"*.

Optional: copy `config.example.yml` to `~/.reportsmith/config.yml` and edit it. Put your own templates in `~/.reportsmith/templates/<kind>.md`.

## Non-goals

- Activity tracking, time tracking, productivity metrics.
- Storing a history of your work between runs.
- A hosted service.

## Roadmap

Tracked as [milestones](../../milestones):

| Version | Scope |
|---|---|
| v0.1 | Core skill, config loading, standup/weekly/changelog templates, git source, preview, file output, install docs |
| v0.2 | Publishing: generic MCP publisher, webhook, command; Slack/Notion/GitHub recipes |
| v0.3 | More sources (PRs/reviews, ticket MCP, notes file) and redaction |
| v0.4 | Unattended runs: cron, CI and GitHub Action examples |
| v0.5 | More templates and destination recipes, evals |
| v1.0 | Stable config schema, docs, public release and directory listings |

## License

MIT
