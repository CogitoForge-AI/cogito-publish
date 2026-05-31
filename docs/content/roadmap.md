---
title: Roadmap
order: 6
---

# Roadmap

Where pyssg is heading. This is a living document - items move and priorities
shift as the project grows. For the full picture of what already works, browse
the rest of these docs.

Want to help with something here, or suggest an item? Open an issue or pull
request on [GitHub](https://github.com/magiskboy/pyssg).

## Available now

- Zero-dependency kernel with a webpack-style plugin and lifecycle-hook design.
- `pyssg build` and `pyssg serve` (watch + live reload).
- The `docs()`, `blog()` and `site()` presets.
- Templating with a Hugo-style lookup cascade and `partial()`.
- `pyssg new` scaffolding with offline and GitHub-hosted themes.
- Syntax highlighting, asset fingerprinting, SEO / Open Graph tags,
  `robots.txt` and redirects.
- Sitemaps, RSS, and raw Markdown output alongside HTML.

## Next

Targeted for the 1.0 release.

- **Data files** - load `data/*.toml|json|yaml` into your templates.
- **Two polished themes** - an OSS docs theme and a personal blog theme, with
  no Node or build step required.
- **Client-side search** - a generated index plus a small search widget.

## Later

- **Shortcodes & admonitions** - callouts, embeds, and tab groups.
- **Per-page table of contents**, reading time, and word count.
- **Internal link resolution** with broken-link reporting.
- **Obsidian-style wikilinks** (`[[...]]`) and backlinks.
- **Markdown linting** to catch issues at build time.
- **Extended feeds** - JSON Feed and Atom, plus per-tag feeds.
- **Third-party plugins** distributed as plain Python packages.
- **Incremental builds** for faster rebuilds on large sites.
