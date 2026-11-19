# Google Drive / Google Docs

Checked against the claude.ai Google Drive connector (Nov 2026).

- **Tool:** `create_file`. Fields: `title` ← report title; `textContent` ← body; `contentMimeType: "text/html"`; `parentId` ← folder id.
- **Body:** send HTML (headings, lists, links). Drive converts `text/html` to a Google Doc; plain text or markdown arrives unformatted. Add `disableConversionToGoogleType: true` only if the user wants the raw file.
- **Folder:** config `parent` is a folder name or id. Resolve a name with `search_files`: `title contains '<name>' and mimeType = 'application/vnd.google-apps.folder'`.
- **No in-place updates.** `update_file` changes metadata only (title, folder, lock), not content. Before creating, search the folder for the same title; if one exists, tell the user and create the new one with a ` (v2)` suffix rather than leaving two identical titles. Never trash the old one without being asked.
