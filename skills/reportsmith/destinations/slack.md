# Slack

- **Tool:** a send/post message tool from the Slack server.
- **Config:** `channel` (name like `#standup` or an id). Resolve names with the server's channel list/search tool.
- **Body:** Slack mrkdwn: `*bold*`, `_italic_`, `•` bullets, `<url|text>` links. No markdown headings: turn `#` headings into a bold line. Title goes in the first line, bold.
- **Long reports:** Slack truncates very long messages. Over ~3,000 characters, post the highlights and attach or link the full report.
- **Updates:** if the server has an update-message tool and the same report was posted today, update that message instead of posting again.
