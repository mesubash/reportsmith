---
name: reportsmith
description: Write work reports (standup, weekly, changelog, or a custom kind) from the user's git history and what they say in the conversation. Use when the user asks for a standup, status update, weekly report, worklog, changelog, or "what did I do".
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

For each path in `sources.git.repos` (expand globs and `~`; skip anything that is not a git repo; default: current repo):

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

## 5. Output

After the user approves the preview:

- Write the report to `<output.dir>/<kind>-<period>.md` (default dir `~/.reportsmith/out`; create it if missing). Ask before overwriting an existing file.
- Print the path and the report so the user can copy it.
