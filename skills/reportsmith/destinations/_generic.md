# Any MCP server

Use when there is no recipe for the configured `server`.

1. **Find the tool.** List this session's tools from that server. Prefer names or descriptions containing the `action` words (e.g. `create page`, `send message`, `add comment`). Some servers expose one tool with an `action` parameter: pick that tool and set the action.
2. **Map fields from the schema**, by meaning, not exact name:
   - title → `title`, `name`, `subject`, `summary`
   - body → `content`, `body`, `text`, `description`, `markdown`, `*_html`
   - config extras (`channel`, `parent`, `project`, `space`, `issue`) → the matching parameter, resolving names to ids with the server's list/search tools
3. **Body format:** a field ending in `_html` gets HTML; Slack-like chat gets mrkdwn; otherwise markdown.
4. **Avoid duplicates:** if the tool has an external-id style field (`external_id`, `idempotency_key`, `client_id`), set it to `reportsmith:<scope>:<kind>:<period>`. Otherwise search for an existing item with the same title before creating, and update it if found.
5. **Unsure** about a required field: dry-run and ask; don't guess.
