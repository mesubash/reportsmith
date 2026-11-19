# Discord

No MCP needed: use a channel webhook (Server settings, Integrations, Webhooks).

```yaml
destinations:
  discord: { via: command, run: "python3 {{skill_dir}}/scripts/discord.py" }
```

Put the webhook URL in the `DISCORD_WEBHOOK` environment variable, not in config. The script handles the limits below.

Discord takes JSON `{"content": "..."}` with a 2,000-character limit, so the generic webhook payload does not fit. Send the report as `content` if it fits; otherwise post the title and highlights in `content` and put the full body in an embed description (`embeds: [{"title": ..., "description": ...}]`, 4,096 characters). Longer than that: post the highlights and say where the full report is saved.

Discord markdown supports `**bold**`, `- ` lists and `#`/`##` headings; tables do not render.
