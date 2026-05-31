---
title: Plugins
order: 3
---

# Plugins

Plugins are where all the real work happens. pyssg ships two tiers of built-in
plugins plus a way to write your own.

- [Built-in plugins](/en/plugins/built-in/) - the tier-1 and tier-2 plugins that
  come with pyssg.
- [Writing plugins](/en/plugins/writing-plugins/) - the `apply` method, tapping
  hooks, and conventions to follow.
- [Presets](/en/plugins/presets/) - ready-made plugin stacks for docs, blogs and
  company sites.

## Two tiers

**Tier 1** turns Markdown into HTML, one-to-one:

`ReadFile` -> `Frontmatter` -> `Markdown` -> `Template` -> `WriteFile`

**Tier 2** adds flexible structure - URLs, groupings, list pages and
navigation - so the source tree and the output tree need not match:

`Permalink`, `Collections`, `Listing`, `Navigation`

All tier-2 plugins share one [content model](/en/architecture/lifecycle/), so a
template only ever learns `site`, `page`, `collections` and `menus`.
