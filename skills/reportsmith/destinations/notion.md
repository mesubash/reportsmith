# Notion

- **Tool:** a create-page tool from the Notion server; for updates, its update-page or append-blocks tool.
- **Config:** `parent` (page or database name or id). Resolve names with the server's search tool.
- **Mapping:** title → page title property; body → page content (markdown if the tool accepts it, otherwise blocks).
- **Database parent:** also fill a date property with the report period and a select/tag property with the kind if the database has them.
- **Updates:** search the parent for a page with the same title first; update it if found.
