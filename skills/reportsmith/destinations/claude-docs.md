# Claude Docs

Checked against the claude.ai Docs connector (Nov 2026), with a real publish of the v0.2.0 release notes.

- **Load first:** if the agent lists a `docs` skill, load it before any Docs call (the connector requires it).
- **Tool:** `batch` with `container: {kind: "project", create: {name: <title>, doc: {markdown: <body>}}}` and `batch: []`. One call creates the whole doc.
- **Body:** markdown as is. Headings, bullet lists and inline code keep their structure; no conversion needed.
- **Result:** the response has the doc link at `frame.url`. Report that link.
- **Private by default:** the doc is visible only to the user until they share it.
- **Reruns:** the connector creates a new doc each time. To change an existing report, use the connector's `update` tool on that doc rather than creating another.
