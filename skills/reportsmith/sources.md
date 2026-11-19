# Sources

Read each source for the resolved `from`/`to` range and scope. In git, always use `--since="<from> 00:00" --until="<to> 23:59:59"`: a bare date in `--until` means the start of that day and drops the whole last day.

## git

**Repos:** `sources.git.repos` if set (globs and `~` allowed); otherwise every repo under `scope.include`:

```sh
find <include> -maxdepth 3 -name .git -prune 2>/dev/null
```

Skip excluded paths. Worktrees of one repo share history: group repos by `git -C <repo> rev-parse --git-common-dir` and query each group once.

```sh
git -C <repo> log --all --no-merges --author="<author>" \
  --since="<from> 00:00" --until="<to> 23:59:59" \
  --date=short --pretty='%h|%at|%ad|%s'
```

- `<author>`: `sources.git.author`, or `git config user.email` when `auto`. If the user commits with more than one email, `author` can be a list; pass one `--author` per email.
- **Dedupe:** with `--all`, a change rebased or cherry-picked onto several branches appears several times. Same subject and same author time (`%at`) = one item. `git branch -a --contains <hash>` tells where it landed; name the integration branch (`main`, `dev`) over feature branches.
- Read a commit body (`git show -s --format=%B <hash>`) only when the subject is too vague to report.
- Ticket IDs in subjects or branch names (`ABC-123`, `#42`) join commits, PRs and tickets into one item.

**changelog / release-notes:** all authors, by range instead of date:

```sh
git -C <repo> log --no-merges --pretty='%h|%s' <last-tag>..HEAD
```

`<last-tag>` = `git describe --tags --abbrev=0`; no tags: ask for a range. Leave out chore, CI, docs-only and merge commits unless asked. Release notes use `public` audience: what changed for users, not how.

## Agent sessions

Every coding agent keeps session logs on disk. The bundled reader filters them by scope and period and prints a redacted digest:

```sh
python3 <skill-dir>/scripts/sessions.py --from <from> --to <to> \
  --include <path> [--include <path> ...] [--exclude <path> ...] \
  [--redact <regex> ...]
```

Pass one `--redact` per entry in `redact.patterns`.

Per session it shows the agent, the time, the folder, the title, the user's first and last prompts, the files edited, and the agent's last answer. Use only this digest; never open raw transcript files.

- Supported: Claude Code (`~/.claude/projects`), Codex (`~/.codex/sessions`).
- A prompt shows what was asked. The last answer, the files edited and the commits show what happened. Report something as done only with that evidence.
- `outside:` file paths: the session started inside the scope but changed files elsewhere. Leave that work out, or put it under its own heading if the user wants it.
- Merge a session with the commits it produced into one item.

## Agent memory

If a memory MCP server is connected (for example claude-mem), search it for the period. Use observations and session summaries, not raw prompts. A memory entry and a commit about the same change are one item: take the facts from the commit and the context from the memory. Memory that records a start but no result means started, not done.

## PRs and reviews

If `gh` is installed and signed in (`gh auth status` succeeds):

```sh
gh search prs --author=@me    --updated="<from>..<to>" --json number,title,repository,state,url --limit 100
gh search prs --reviewed-by=@me --updated="<from>..<to>" --json number,title,repository,state,url --limit 100
```

Keep PRs whose repository is one of the scoped repos (match on the `origin` remote). Reviews of other people's PRs go under work outside tickets. For GitLab, use `glab mr list` equivalents if `glab` is installed.

## Tickets

If an issue-tracker MCP server is connected (Jira, Linear, Plane, GitHub Issues, …), list items assigned to the user that changed state in the period. Use the server's own filter or query language. Keep the ticket ID, title and state change. Never change a ticket while gathering.

## Notes

`sources.notes` (default `~/.reportsmith/notes.md`), if it exists. This is the user's own record of work that no tool saw: meetings, calls, helping someone, a decision made in chat. One line per item, ideally starting with a date:

```
2026-11-19 Walked ops through the double-charge incident
2026-11-19 Agreed with the PM to defer typed partner contracts
```

Keep lines dated inside the period. Undated lines count only if the period includes today.
