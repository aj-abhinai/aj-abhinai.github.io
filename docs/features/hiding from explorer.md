---
title: Hiding Notes from Explorer
tags:
  - feature/explorer
---

You can publish notes (and link to them) while keeping them *out* of the Explorer sidebar.

## Frontmatter Flag

Add the following frontmatter key to any note you want hidden (the value may be `true`, `"true"`, `1`, `"1"`, `yes`, or `on`):

```md
---
title: My Hidden Note
hideInExplorer: true
---
```

The page will still be generated and is accessible through direct links, backlinks, search, graph view, etc. It just won't appear in the left-hand Explorer tree.

## Hiding Entire Folders

If you place an `index.md` (or `_index.md`) inside a folder and give that index file `hideInExplorer: true` (any truthy value works), the entire folder (and all of its children) will be hidden from the Explorer. This lets you:

1. Keep the on-disk folder structure for your own organization (e.g. `content/Course Notes/Module 1/...`).
2. Publish and link to the contained notes from other pages (like a master course index) without cluttering the sidebar.

Example structure:

```
content/
  Course Notes/
    index.md                <- public, shows links to modules
    Module 1/
      index.md              <- has hideInExplorer: true
      lesson-a.md
      lesson-b.md
    Module 2/
      index.md              <- has hideInExplorer: true
      lesson-a.md
```

`Module 1` and `Module 2` (and their lessons) won't appear in Explorer, but `lesson-a.md` is still reachable via any link you create.

## Linking Hidden Notes

Just link to them normally:

```md
See [[Course Notes/Module 1/lesson-a]] for more detail.
```

## Search & Graph

Hidden notes are still indexed for search and graph visualization. Only the Explorer tree view filters them out.

## Customizing Further

The default filter now excludes any file whose frontmatter contains `hideInExplorer: true`. If you override `Component.Explorer({ filterFn })` in `quartz.layout.ts`, remember to preserve that behavior if you still want it:

```ts
Component.Explorer({
  filterFn: (node) => node.slugSegment !== "tags" && node.data?.hideInExplorer !== true
})
```

---
Added in: custom enhancement for selective Explorer visibility.