---
name: reportsmith
description: Write work reports (standup, daily, weekly, monthly, changelog, release notes, or a custom kind) for any period and any folder scope, from git, local coding-agent sessions (Claude Code, Codex), agent memory, PRs, tickets and notes, then optionally publish them through MCP, a webhook or a command. Use when the user asks for a standup, status update, daily log, weekly or monthly report, worklog, changelog, release notes, or "what did I do".
---

# reportsmith

Report maker. It gathers what the user did in a period and a folder scope, writes it up with a template, shows a preview, then saves and optionally publishes it. It runs only when asked and stores nothing between runs.

Files in this skill's folder, read when the step needs them:
- `sources.md`: how to read each source
- `publishing.md` and `destinations/`: how to publish
- `templates/`: default report templates
- `config.example.yml`: every config key with its default
- `scripts/sessions.py`: agent-session reader (Python 3 stdlib)

## 1. Load config

Read whichever exist; later ones override earlier ones key by key:

1. Defaults (`config.example.yml` in this folder)
2. `~/.reportsmith/config.yml`
3. `.reportsmith.yml` in the current repo root

No config is fine. Ignore unknown keys, and mention them once.

## 2. Work out the request

From the user's words first, then `reports.<kind>` in config, then these defaults:

| Field | Default |
|---|---|
| kind | `standup` |
| period | see below |
| scope | config `scope`, else the current repo |
| audience | `team` (`manager`, `team`, `public`, `self`) |
| format | `markdown` (`slack`, `email`, `plain`) |
| length | `medium` (`short` ≈ 5 items, `medium` ≈ 15, `long` no cap) |

Default period per kind: standup = last working day and today · daily = today · weekly = current week · monthly = current month · changelog and release-notes = last tag to HEAD.

### Period

Resolve the user's words to an inclusive `from`/`to` date range in `prefs.timezone`:

| User says | Range |
|---|---|
| `yesterday`, `today`, `2026-11-03`, `Nov 3`, `last Friday` | that day |
| `this week`, `last week`, `week 45`, `week of Nov 3` | that week (`prefs.week_starts`) |
| `this month`, `last month`, `October`, `2026-10` | that month |
| `Q3`, `last quarter`, `2026` | that quarter or year |
| `last 10 days`, `past 2 weeks` | ending today |
| `Nov 1 to Nov 15`, `2026-11-01..2026-11-15`, `since Nov 1` | that range (`since` ends today) |

- For a standup, if "yesterday" was a weekend day with no activity, use the last working day and say so.
- A future range, or `from` after `to`: ask.
- Put the resolved range and the scope in the report header.

**Threshold.** A range longer than `limits.max_days` (default 92): say how long it is and ask to confirm or narrow it. More than `limits.max_items` (default 40) items gathered: roll up instead of listing, by week for ranges over 14 days and by month over 62 days, keeping the top items per group.

### Scope

Which work counts, decided by folder: "for ~/work", "only ~/work/api", or config:

```yaml
scope:
  include: [~/work]
  exclude: [~/work/archive]
```

Only repos and agent sessions under `include`, and not under `exclude`, count. This keeps work, side projects and clients in separate reports.

## 3. Gather

Read every available source for the period and scope; `sources.md` says how. Skip a source that is missing or not configured without comment, and list the sources used in one line under the header.

| Source | Gives |
|---|---|
| git | commits in every repo under the scope |
| agent sessions | work done with Claude Code or Codex, including work with no commit |
| agent memory | memory MCP such as claude-mem, if connected |
| PRs and reviews | via `gh`, if installed and signed in |
| tickets | issue-tracker MCP (Jira, Linear, Plane, GitHub Issues), if connected |
| notes | `sources.notes` file: the user's own lines for work no tool saw |
| conversation | what the user said in this session |

**Redact before drafting.** Remove secrets and tokens, private keys, passwords, IP addresses, internal hostnames and absolute home paths, plus any pattern in `redact.patterns`. Never put raw transcript text in a report.

## 4. Draft

Template lookup, first found wins: `<templates_dir>/<kind>.md` · `~/.reportsmith/templates/<kind>.md` · `templates/<kind>.md` here. A kind with no template: use the `weekly.md` structure and say the user can add one. Placeholders are `{{date}}`, `{{period}}`, `{{scope}}`, `{{version}}` and `{{title}}`. Prose instructions and `<!-- comments -->` in a template are for you; don't copy them into the output.

Rules:

- **Never invent.** Every line traces to a gathered source. Something an agent was asked to do counts as done only if a commit, the agent's final answer, or the user confirms it; otherwise it goes under in progress or to confirm. Unsure: leave it out or ask.
- **Outcomes over activity.** "Fixed login timeout for mobile users", not "changed auth.ts".
- **One item per piece of work.** A session, its commits, its PR and its ticket are one item. Cite the ticket ID and commit once.
- **Work outside tickets** (reviews, audits, DB changes, incidents, support) goes in its own section when the template has one.
- **Audience.** `manager`: outcomes, risks, decisions needed; no code or file names. `team`: plus useful technical detail. `public`: user-facing wording, no internal names. `self`: everything.
- Drop empty sections. Convert to the requested format last.

### Writing style

People read these reports, and wording that sounds machine-written makes them trust the content less. Write the way a busy engineer writes a status update.

**The user's own style comes first.** If `style.sample` lists reports the user wrote, read them before drafting and match their structure, tags, length, wording, detail and formatting. If `style.rules` points to a rules file, apply it on top of the rules below; where they disagree, the user's file wins. Precedence: never invent > `style.sample` > `style.rules` > the rules below.

**Voice** (`style.voice`, default `terse`): `terse` = "Fixed double charge on card payments." · `first-person` = "I fixed…" · `team` = "We fixed…". Past tense for done work, present tense for ongoing work.

**Plain words.** Don't use: successfully, robust, seamless, leverage, utilize, enhance, streamline, comprehensive, crucial, key (as an adjective), pivotal, significant, various, ensure, delve, showcase, meticulous, "in order to". Write "is" or "has", not "serves as", "represents" or "features".

**No inflation.** Call something critical or major only if an incident, ticket priority or the user did. Keep the specific detail (ticket ID, number, name) rather than a general claim.

**No templates.** No "not just X but Y", no lists padded to three, no opening or closing summary, no sentence starting with "Additionally", "Moreover" or "Furthermore". End a sentence at the fact, without a trailing ", ensuring…" or ", improving…". No stacked hedges. Use the same term for the same thing throughout.

**Results, not process.** "Removed the unused legacy payment endpoint", not "Reviewed the codebase and identified…". Leave out how the agent worked.

**Formatting.** Bold only for item labels at the start of a bullet, if at all. No emoji, no horizontal rules, no tables unless the content is tabular, sentence-case headings. No em dashes: use commas, colons, parentheses or full stops. No `A → B → C` chains in place of a sentence.

**No assistant residue.** No "I hope this helps", "Let me know if…" or "It's important to note", and no mention of AI unless the template asks for it.

**Final check.** Reread the draft against the gathered sources. Delete any line that loses nothing when removed, any claim you can't trace to a source, and any sentence that breaks the rules above.

## 5. Preview

Show the report and, if it will be published, where to ("Will post to: team-chat (#standup), wiki"). Ask whether to change anything. Apply edits and show it again until the user approves.

## 6. Save

Write to `reports.<kind>.output` if set, otherwise `<output.dir>/<kind>-<from>[_<to>].md` (default `~/.reportsmith/out`). Create missing folders, and ask before overwriting. Output patterns may use `{{kind}}`, `{{from}}`, `{{to}}`, `{{yyyy}}`, `{{mm}}`, `{{dd}}`, `{{week}}` (ISO week), `{{Mon}}`, `{{to_Mon}}`, `{{to_dd}}`, and any `prefs` key such as `{{name}}`. Print the path.

## 7. Publish

Only if the kind has `reports.<kind>.publish` destinations or the user names one. Follow `publishing.md`. With "dry run", show the exact calls and make none.

## Unattended runs

When run non-interactively (cron, CI, a scheduled agent) with `publish.confirm: false`:
- skip the preview
- never ask; where you would ask, stop and say why
- publish, and print one line per destination with its link or error

If the scope, the range or a required MCP server is missing, exit with a clear message rather than guessing.
