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
