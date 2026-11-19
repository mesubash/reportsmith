# Plane

Plane's server exposes one tool per object with an `action` parameter.

- **Report as a page** → tool `page`, `action: create`:
  - `name` ← title, `description_html` ← body as HTML
  - `project_id` for a project page (omit for workspace page); `parent_id` to nest under an existing page (resolve with `page list`)
  - `external_source: "reportsmith"`, `external_id: "<scope>:<kind>:<period>"` so reruns are recognizable
  - Rerun: `page list`, find the page with that `external_id` or name, then `action: update` (body replaces whole page).
- **Item on a ticket** → tool `workitem_comment`, `action: create`, `comment_html` ← that item's lines as HTML. Resolve the ticket from its identifier (e.g. `PROJ-123`) with the workitem tool first.
- **Time** → tool `work_log`, `action: create`, `duration` in minutes, `description`. Only when the user gives durations; never estimate time from session lengths.
