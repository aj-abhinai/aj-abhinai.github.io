# Quartz Sync Notes Script Guide

Simple, step-by-step summary of what `sync-notes.py` does:

1. Finds all `.md` files under `SOURCE_DIR` and skips folders in `SKIP_DIRS` (currently `Archives`).
2. Checks each note for the `#published` tag; notes without it are skipped.
3. Copies each published note to `temp-content/Notes` (updates if already exists).
4. Converts image embeds to local assets:
   - `![[image.png]]` and `![alt](image.png)` are copied into `temp-content/Notes/assets`.
   - Links are rewritten to `./assets/<filename>`.
5. Keeps same-note links (including `[[#Heading]]` and `[[#^blockid]]`) as links.
6. Keeps links to other published notes as links, and normalizes them to match the flattened destination (folders and `.md` are stripped).
7. Converts links to unpublished notes into plain text (uses alias text if provided).
8. Removes `#published` from the body.
9. Moves tags from the first line into frontmatter `tags:` (inline tags elsewhere in the body are preserved).
10. Frontmatter rules:
    - If frontmatter exists, it is preserved.
    - If missing, it is generated (`title`, `permalink`, `date`, `publish: true`).
    - `publish: true` is normalized.
    - `last-modified` is updated only when content actually changes.
11. If the processed body is identical to the existing destination file, the file is left untouched (no timestamp change).

Next task (planned):
1. Review and improve how embed links like `![[Note#^blockid]]` are handled. Right now embeds are left unchanged and may break if the target note is not published.
eg: ![[Hugo#^d58766]]
