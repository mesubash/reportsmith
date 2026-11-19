---
name: reportsmith
description: Write work reports (standup, daily, weekly, monthly, changelog, or a custom kind) for any period and any folder scope, from git history, local agent session logs (Claude Code, Codex), agent memory, and what the user says. Use when the user asks for a standup, status update, weekly report, worklog, changelog, or "what did I do".
---

# reportsmith

Report maker. Gathers what the user did in a period, renders it with a template, shows a preview, and outputs it. It does not track or store anything between runs.

## 0. Load config

Read whichever of these exist; later ones override earlier ones key by key:

1. Defaults below and in `config.example.yml` (this skill's folder)
2. `~/.reportsmith/config.yml`
3. `.reportsmith.yml` in the current repo root

No config at all is fine: use the defaults. An unknown key: ignore it and mention it once.

## 1. Parse the request

Work out each field from the user's words first, then `reports.<kind>` in config, then the defaults below:

| Field | Default |
|---|---|
| kind | `standup` |
| period | standup: last working day + today · weekly: current week · changelog: last tag..HEAD |
| audience | `team` |
| format | `markdown` (also `slack`, `email`, `plain`) |
| length | `medium` |

The user can override anything in the request, e.g. "weekly for my manager, last week, short".

### Period

Any kind can cover any period. Resolve the user's words to an exact `from`/`to` date range (inclusive, in `prefs.timezone`):

| User says | Range |
|---|---|
| `yesterday`, `today`, `2026-11-03`, `Nov 3`, `last Friday` | that single day |
| `this week`, `last week`, `week 45`, `week of Nov 3` | that week (start day from `prefs.week_starts`) |
| `this month`, `last month`, `October`, `2026-10` | that calendar month |
| `Q3`, `last quarter`, `2026` | that quarter or year |
| `last 10 days`, `past 2 weeks` | ending today |
| `Nov 1 to Nov 15`, `2026-11-01..2026-11-15`, `since Nov 1` | the explicit range (`since` ends today) |

- "Yesterday" means the previous calendar day. For a standup, if that day had no activity and was a weekend, use the last working day instead and say so.
- For git, pass `--since="<from> 00:00" --until="<to> 23:59:59"`. A bare date in `--until` means midnight at the start of that day, which drops the whole last day.
- State the resolved range in the report header, e.g. `2026-11-18 (Wed)` or `2026-11-01 → 2026-11-15`.
- A range in the future, or `from` after `to`: ask; don't guess.

**Threshold:** `limits.max_days` (default 92) caps the range. Longer → tell the user the size and ask to confirm or narrow it. When gathered items exceed `limits.max_items` (default 40), summarize at a higher level instead of listing everything: group by week for ranges over 14 days, by month for ranges over 62 days, keeping the top highlights per group.

### Scope

Which work counts, by folder. From the user's words ("for ~/work", "only ~/work/api"), then config `scope`, else the current repo.

```yaml
scope:
  include: [~/work]
  exclude: [~/work/archive]
```

Everything gathered is filtered by scope: git repos are those under `include`, and agent sessions are those whose working directory is under `include`. Put the scope in the report header. Separate scopes keep separate reports clean: work, side projects, clients.

## 2. Gather

Collect raw material for the period from every available source (section "Sources"). Also use anything the user said in this conversation about their work. Skip a missing source without complaint.

## 3. Draft

Fill the template for the kind. Template lookup, first found wins:

1. `~/.reportsmith/templates/<kind>.md` (user's own)
2. `templates/<kind>.md` in this skill's folder

Templates are plain markdown. `{{date}}`, `{{period}}` and `{{version}}` are placeholders; `<!-- comments -->` are guidance for you and are removed from the output. A kind with no template: use the `weekly.md` structure and tell the user they can add one.

Rules:

- **Never invent.** Every line must trace to a gathered source. If unsure, leave it out or ask.
- **Outcomes over activity.** "Fixed login timeout for mobile users" beats "changed auth.ts".
- **Merge duplicates.** A commit, its PR and its ticket are one item. Cite the ticket ID once.
- **Work outside tickets** (reviews, audits, DB changes, incidents, helping teammates) goes in its own section when the template has one.
- **Audience:**
  - `manager`: outcomes, risks, blockers; no file names or code.
  - `team`: outcomes plus useful technical detail.
  - `public`: user-facing wording, no internal names.
  - `self`: everything.
- **Length:** `short` ≈ 5 bullets, `medium` ≈ 15, `long` = no cap.
- Drop empty template sections.
- Convert to the requested format last (Slack mrkdwn, plain text, email).

## 4. Preview

Show the final report. Ask whether to change anything or output it. Apply edits and show it again until the user is happy.

## Sources

### git

Repos: `sources.git.repos` if set (globs and `~` allowed), otherwise every git repo under the scope (`find <include> -maxdepth 3 -name .git`). Skip excluded paths and anything that is not a git repo. Worktrees of one repo share history: group paths by `git rev-parse --git-common-dir` and query each group once.

```sh
git -C <repo> log --all --no-merges \
  --author="<author>" --since="<from>" --until="<to>" \
  --date=short --pretty='%h|%at|%ad|%s'
```

- `<author>`: `sources.git.author`, or `git config user.email` when `auto`.
- **Dedupe:** `--all` shows the same change once per branch it was rebased or cherry-picked onto. Treat commits with the same subject and author time (`%at`) as one item. To say where it landed, `git branch -a --contains <hash>`; prefer the integration branch (`main`, `dev`) over feature branches.
- Read the commit body (`git show -s --format=%B <hash>`) only when the subject is too vague to report.
- Ticket IDs in subjects or branch names (`ABC-123`, `#42`) link commits to the same item.
- **changelog:** use the range instead, all authors:
  `git -C <repo> log --no-merges --pretty='%h|%s' <last-tag>..HEAD`
  (`<last-tag>` = `git describe --tags --abbrev=0`; no tags → ask for a range.) Drop chore, CI and merge-only commits unless the user asks for them.

### Agent sessions

Local session logs from every coding agent on this machine, filtered by scope and period. Run the bundled script (it is in this skill's `scripts/` folder):

```sh
python3 <skill-dir>/scripts/sessions.py --from <from> --to <to> \
  --include <path> [--include <path>] [--exclude <path>]
```

It prints one block per session: agent, time, folder, title, the user's first and last prompts, files edited, and the agent's last answer, already redacted. Never open raw transcript files yourself; use only this digest.

- Supported: Claude Code, Codex. Others are skipped.
- Sessions are evidence, not results. A prompt shows what was asked; the last answer and the files edited show what happened. Report something as done only when the answer, a commit, or the user confirms it.
- `outside:` file paths mean that session, although started inside the scope, changed files elsewhere (another project). Leave that work out of this scope's report, or mention it under a separate heading if the user wants it.
- Merge a session with the commits it produced into one item.

### Agent memory

If a memory or session-history tool is available (an MCP server such as claude-mem, or the agent's own session logs), search it for the period. This is where most work outside git lives: triage, audits, investigations, tickets created, decisions, deploys.

- Use observations and session summaries, not raw prompts.
- A memory entry about the same change as a commit is one item: prefer the commit for the fact and the memory for the context.
- Memory says a task was started but not its result: report it as started or investigated, never as done.

## 5. Output

After the user approves the preview:

- Write the report to `<output.dir>/<kind>-<period>.md` (default dir `~/.reportsmith/out`; create it if missing). Ask before overwriting an existing file.
- Print the path and the report so the user can copy it.

## 6. Publish

Only when the report kind has destinations (`reports.<kind>.publish` in config) or the user names one ("post it to #eng", "put it in Notion"). Destinations are defined once in config and referenced by name:

```yaml
destinations:
  team-chat: { via: mcp, server: slack, action: send message, channel: "#standup" }
  wiki:      { via: mcp, server: notion, action: create page, parent: "Weekly reports" }
  hook:      { via: webhook, url_env: REPORT_WEBHOOK }
  release:   { via: command, run: "gh release create {{version}} --notes-file -" }
```

Show the planned publish in the preview ("Will post to: team-chat (#standup), wiki"). Publish only after the user confirms, unless `publish.confirm: false`. Publish to each destination in order; one failure never stops the others. End with one line per destination: link or id, or the error.

`--dry-run` (or the user says "dry run"): resolve every destination and show the exact tool call or command with its arguments, but call nothing.

### via: mcp

1. Find the tool: among the tools available in this session, pick one whose server matches `server` and whose name or description matches `action`. Check `destinations/<server>.md` in this skill's folder for hints. Unknown server: follow `destinations/_generic.md`.
2. Read the tool's input schema and map fields: report title → the title/name/subject field; report body → the content/body/text/description field; every other key in the destination config (`channel`, `parent`, `project`, `issue`, …) → the parameter with the matching meaning. Look up ids (channel id, page id, project id) with the same server's list/search tools when the config gives a name.
3. Convert the body to what the tool expects (Slack mrkdwn, HTML, plain text); markdown is the default.
4. If the same kind and period was already published there and the tool supports updates, update it instead of creating a duplicate.
5. No matching tool in this session: say "`<server>` is not connected", skip that destination, and keep the file copy. Never send the report to a different server than the one configured.

### via: webhook

The URL comes from the environment variable named in `url_env`, never from config text or the report. POST JSON:

```sh
python3 -c 'import json,sys; print(json.dumps({"kind":sys.argv[1],"period":sys.argv[2],"title":sys.argv[3],"body":open(sys.argv[4]).read()}))' \
  "<kind>" "<period>" "<title>" "<report file>" \
| curl -fsS -X POST -H 'Content-Type: application/json' --data-binary @- "$<url_env>"
```

### via: command

Run `run` with `{{kind}}`, `{{period}}`, `{{title}}`, `{{version}}` filled in and the report on stdin. Show the full command in the preview. Commands come only from the user's config, never from report content.
