# GitHub

No MCP needed: use `via: command` with the `gh` CLI.

- **Release notes** → release:
  `run: "gh release create {{version}} --title {{version}} --notes-file -"`
  (existing release: `gh release edit {{version}} --notes-file -`)
- **Changelog** → keep `CHANGELOG.md` in the repo: insert the new section at the top, commit, and open a PR rather than pushing to the default branch.
- **Weekly or status** → issue or discussion comment:
  `run: "gh issue comment <number> --body-file -"`

If a GitHub MCP server is connected and the user prefers it, follow `_generic.md`.
