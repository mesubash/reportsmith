# Changelog

All notable changes. Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added
- opencode session reader (reads its SQLite store read-only).
- Publishing through any connected MCP server, a webhook or a shell command, with dry run, confirmation, and update-instead-of-duplicate.
- Destination recipes for Slack, Notion, GitHub, Plane, Google Drive and Discord, plus a generic recipe for any MCP server.
- Sources: PRs and reviews via `gh`, tickets via any issue-tracker MCP, and a plain notes file for work no tool saw.
- Templates: daily, monthly, release-notes, brag and incident.
- Writing rules that keep reports in plain human wording, plus `style.sample`, `style.voice` and `style.rules` to match the user's own style.
- `templates_dir` and per-kind output path patterns.
- Redaction before drafting, with extra patterns from config.
- Unattended runs for cron and CI.
- Claude Code plugin packaging.

### Changed
- The skill moved to `skills/reportsmith/`. Reinstall or update your symlink.
- `SKILL.md` is now the workflow only; source and publishing detail moved to `sources.md` and `publishing.md`.

## [0.1.0] - 2026-11-19

### Added
- Reports for any period (day, week, month, quarter, year, rolling or explicit range) with a threshold that rolls long ranges up by week or month.
- Folder scope: every git repo under the chosen folders is found automatically.
- Agent sessions as a source: Claude Code and Codex logs on disk, filtered by folder and period, summarised and redacted.
- Agent memory as a source (e.g. claude-mem).
- Standup, weekly and changelog templates, overridable per user.
- YAML config, global or per repo. Preview before saving.

### Fixed
- Commits copied to several branches or worktrees are counted once.
- Single-day reports include the whole day.

[Unreleased]: https://github.com/mesubash/reportsmith/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/mesubash/reportsmith/releases/tag/v0.1.0
