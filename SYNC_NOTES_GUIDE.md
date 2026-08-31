# Quartz Sync Notes Script Guide

Context for agents working on `sync-notes.py`.

> **IMPORTANT — standing instruction:** never read, scan, glob, or explore `D:\ajabhinai` (the source vault). It contains personal notes. The script reads it programmatically; agents must never open it directly. Work only on files inside this quartz repo.

## What the script does

1. Finds all `.md` files under `SOURCE_DIR` (`D:\ajabhinai`) and skips folders in `SKIP_DIRS` (currently `Archives`).
2. Checks the **first body line** (after frontmatter) for the `#published` tag; notes without it are skipped. The tag anywhere else in the body does NOT publish a note.
3. Copies each published note to `content/Notes` (updates if already exists). All notes are flattened into this one folder.

## Image / asset embeds

- `![[image.png]]`, `![[image.png|300]]` (size), `![[Folder/image.png]]` (folder path), `![alt](image.png)`, and `![alt](./folder/image.png)` (relative paths) are all recognized.
- Aliases and size suffixes (`|...`) are stripped and dropped.
- The asset is copied into `content/Notes/assets` and the link rewritten to `./assets/<filename>`.
- Folder paths and `.md` extensions are stripped before matching asset names.

## Note embeds (`![[Note]]`, `![[Note#Heading]]`, `![[Note#^blockid]]`)

- Target names are normalized before matching: alias (`|...`) stripped, folder path stripped, `.md` stripped, case-insensitive comparison.
- Published target:
  - Block ref (`#^blockid`) — the block's text is extracted from the source and inlined into the note. If extraction fails, falls back to a `[[Note#^blockid]]` link.
  - Heading or plain embed — becomes a `[[Note#...]]` link.
- Unpublished target — the embed is removed entirely (output is empty), so private content never leaks.

## Links

- Same-note links (including `[[#Heading]]` and `[[#^blockid]]`) are kept as-is.
- Links to published notes are kept and normalized to the flattened destination (folders and `.md` stripped).
- Bare block links like `[[Note^abc123]]` are normalized to `[[Note#^abc123]]` so Quartz resolves them.
- Links to unpublished notes become plain text (alias text is used if provided).

## Body and frontmatter rules

- `#published` is removed from the first body line only (a literal "#published" written later in a note is kept as text).
- Tags on the first line are moved into frontmatter `tags:` (inline tags elsewhere in the body are preserved).
- Frontmatter:
  - Existing frontmatter is preserved; missing frontmatter is generated (`title`, `permalink`, `date`, `publish: true`).
  - `publish: true` is normalized on both new copies and updates.
  - `last-modified` is added on first copy and updated only when content actually changes.
- If the processed body is identical to the existing destination file, the file is left untouched (no timestamp change).

## Known limitations (not yet fixed)

- Two published notes (or assets) with the same filename in different source folders collide — the later one silently overwrites the earlier.
- Frontmatter parsing splits on the first `---` after position 3 — a `---` inside a frontmatter value or a `----` file start can break it.
- First-line tag extraction runs after `#published` removal, so the "first line" can shift; text like `#fff` can be mistaken for a tag.
- A `#published` inside a code fence on the first body line would still count as a publish tag.
- Multi-paragraph block embeds only inline the single line above the `^blockid`.
- PDF embeds become markdown image syntax pointing at the PDF (won't render in browsers).
- Wikilinks/markdown links inside code blocks get rewritten as if they were real links.
- Performance: each embed triggers a full vault scan to find the asset (`find_asset_in_source`); large vaults are slow.

## Planned improvements

1. Build a one-time index of vault files (name → path) to speed up asset and block lookups.
2. Detect same-name collisions and warn (or disambiguate) instead of silently overwriting.
3. Harden frontmatter parsing (require the closing `---` on its own line).
4. Only detect `#published` outside code blocks.
