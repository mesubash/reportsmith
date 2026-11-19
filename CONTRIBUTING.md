# Contributing

Most contributions are small markdown files. No build step.

## Layout

```
skills/reportsmith/
  SKILL.md              workflow and writing rules (keep it short)
  sources.md            how each source is read
  publishing.md         how reports are published
  config.example.yml    every config key with its default
  templates/<kind>.md   report templates
  destinations/<server>.md   publishing recipes per MCP server
  scripts/sessions.py   agent-session reader (Python 3 stdlib only)
tests/                  self-checks, not shipped with the skill
```

## Add a template

1. Add `skills/reportsmith/templates/<kind>.md`.
2. Start with an HTML comment saying who reads it and what to leave out. Use `{{date}}`, `{{period}}`, `{{scope}}`, `{{version}}` or `{{title}}` where needed.
3. If the kind needs a default period other than "current week", add it to the defaults line in `SKILL.md`.

## Add a destination recipe

Add `skills/reportsmith/destinations/<server>.md` for an MCP server. Base it on the server's real tool schema, not on guesses, and say which version you checked. Cover which tool and action to use, field mapping, body format, how to avoid duplicates, and any limits (message length, rate limits). Keep it under about 25 lines. `_generic.md` already handles servers without a recipe, so only add one when the generic mapping gets something wrong.

## Add a session reader

Add a `read_<agent>(path, lo, hi)` function and a `READERS` entry in `scripts/sessions.py`, plus a case in `tests/test_sessions.py` built from a small, anonymised sample of the agent's real log format. Rules:

- Standard library only.
- Return the same session dict as the other readers.
- Never print raw transcript text; everything goes through `render()` and `redact()`.

## Writing

Docs, templates and recipes follow the writing rules in `SKILL.md`: plain words, no em dashes, no filler.

## Checks

```sh
python3 tests/test_sessions.py
claude plugin validate .    # if you have Claude Code
```

CI runs the same checks on Linux and macOS.

Changes to `SKILL.md`, `sources.md` or the templates should also pass the end-to-end evals in `evals/` (they call the model, so they are not in CI). See `evals/README.md`. A new behaviour is best covered by a new case: a fixture in `scaffold.sh` and graders in `case.yaml`.

## Commits and PRs

One change per commit, imperative subject, and a body that says why. Reference the issue (`Closes #12`).
