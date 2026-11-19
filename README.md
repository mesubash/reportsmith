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
- **Reads like you wrote it:** plain wording rules built in, and an optional `style.sample` of your own past reports to copy your voice.
- **Customizable through files only:** templates are markdown, config is YAML, per repo or global.
- **Works with any destination:** publishing goes through whatever MCP servers you have connected. Adding a destination means adding config, not code.
- **Private by default:** redaction before preview, nothing published without confirmation unless you turn that off.

## Install

The skill is the folder `skills/reportsmith/`. Install it whichever way your agent supports.

**Claude Code (plugin):**

```
/plugin install reportsmith --marketplace mesubash/reportsmith
```

Older Claude Code versions: `/plugin marketplace add mesubash/reportsmith`, then `/plugin install reportsmith@reportsmith`.

**Any agent with Agent Skills support (Claude Code, Codex, and others):** copy or link the skill folder into the agent's skills directory.

```sh
git clone https://github.com/mesubash/reportsmith.git
ln -s "$PWD/reportsmith/skills/reportsmith" ~/.claude/skills/reportsmith   # Claude Code
ln -s "$PWD/reportsmith/skills/reportsmith" ~/.codex/skills/reportsmith    # Codex
```

Other agents: use their skills directory (see the agent's docs).

**Agents without skill support:** keep the folder anywhere and add one line to `AGENTS.md`: *"For standups, status reports, changelogs or release notes, follow `<path>/skills/reportsmith/SKILL.md`."*

Requirements: `git`, and `python3` (3.8+, standard library only) for reading agent sessions. `gh` is used for PRs and reviews if installed.

## Use

Ask in plain words:

- *"standup"*
- *"what did I do yesterday in ~/work/api"*
- *"weekly report for my manager, last week, short"*
- *"monthly report for October, scope ~/clients/acme"*
- *"changelog since v1.2"*, *"release notes for v2.0"*
- *"daily log, then post it to #eng"* (needs a Slack MCP server and a destination in config)

## Configure

Everything is optional. Copy [`config.example.yml`](skills/reportsmith/config.example.yml) to `~/.reportsmith/config.yml` (global) or `.reportsmith.yml` (one repo) and keep only what you change.

| You want | Set |
|---|---|
| Only count work in some folders | `scope.include`, `scope.exclude` |
| Reports to sound like you | `style.sample` (your past reports), `style.voice`, `style.rules` |
| Your own report format | `templates_dir`, or files in `~/.reportsmith/templates/<kind>.md` |
| Reports saved in your own layout | `reports.<kind>.output` with `{{yyyy}}/{{mm}}/{{dd}}`-style patterns |
| Reports posted somewhere | `destinations` plus `reports.<kind>.publish` |
| A new kind of report | Add `templates/<kind>.md`, then ask for it by name |

## Run on a schedule

Any agent with a non-interactive mode can run reportsmith from cron or CI. Set `publish.confirm: false` in that run's config, and allow the tools it needs: Bash (for `git` and `python3`) and the MCP tools of your destinations.

```sh
# Claude Code, every Friday at 17:00
0 17 * * 5  cd ~/work && claude -p "weekly report for this week, publish" \
  --allowedTools "Bash(git:*)" "Bash(python3:*)" "Bash(gh:*)" "mcp__slack"

# Codex
0 17 * * 5  codex exec -C ~/work "weekly report for this week, publish"
```

Release notes on a tag can run the same way in CI, with the skill checked out and `gh` signed in. In unattended runs reportsmith never asks: if something is missing (scope, range, an MCP server), it stops and says why.

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

## Credits

Writing rules adapted from [Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing).

## License

MIT
