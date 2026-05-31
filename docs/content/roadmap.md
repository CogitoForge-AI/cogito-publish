---
title: Roadmap
order: 6
---

# Roadmap

This page tracks the work that takes pyssg from "it runs" to "it's usable for
real" by technical users. It mirrors the planning notes kept in the repository
and is updated as items change state.

Status legend: `[ ]` not started · `[~]` in progress · `[x]` done. Finished
items are removed from the lists and summarized in [What's done](#whats-done);
the decision details live in the code and git history.

## Framing

Technical users judge a static site generator on two axes:

1. **Time from zero to a deployable site** (onboarding / DX).
2. **Whether the output is production-grade** (fingerprinting, syntax
   highlighting, SEO, search, feeds, speed).

There is also an implicit axis for the ecosystem: **how third-party plugins and
themes are packaged and loaded**. Without that mechanism, an ecosystem cannot
exist in technical terms.

## What's done

### Core foundation

- Zero-dependency kernel plus three plugin tiers
  (read / parse / markdown / template / write, then
  permalink / collections / listing / navigation, then
  sitemap / rss / minify / static).
- `pyssg build` and `pyssg serve` (watch + live reload).
- `Statistics` plugin, the `docs()` / `blog()` / `site()` presets, and this
  documentation site built by pyssg itself.
- Templating: a Hugo-style lookup cascade plus `partial()`.

### Shipped (as of 2026-05-31)

- **A. Onboarding / DX** — `pyssg new` (scaffolding, embedded offline
  docs/blog themes, GitHub tarball fetch); friendly error messages and a build
  error overlay with `file:line`; early `Config` / frontmatter validation via a
  schema registry; deploy recipes for GitHub Pages, Netlify and Cloudflare
  Pages.
- **B. Authoring** — syntax highlighting (the `Highlight` plugin, Pygments at
  build time, inline CSS via the `highlight_css()` global, dark mode).
- **C. Output** — markdown page output (the raw `.md` for AI consumers); asset
  fingerprinting / cache-busting; SEO and meta tags (Open Graph, Twitter,
  canonical, JSON-LD); `robots.txt` and redirects.
- **D. Themes** — fetch & vendor tarballs with the standard library (no git
  required); `owner/repo[/path][@tag]` syntax plus offline-first embedded
  themes; a hybrid model; the `theme.toml` manifest; generating
  `pyssg.config.py` from a preset; an official `themes/` folder.

## B. Authoring power

- [ ] **Data files** — load `data/*.toml|json|yaml` into `build.meta` for
  templates. (1.0)
- [ ] **Shortcodes / admonitions** — callouts (note / warning / tip), embeds
  (YouTube / gist), tab groups.
- [ ] **Per-page TOC** plus reading time / word count.
- [ ] **Internal link resolution** — link by source path resolved to the
  permalink; report broken links.
- [ ] **Obsidian wikilinks / backlinks `[[...]]`** — a plugin that rewrites
  `[[...]]` into proper Markdown links *before* the Markdown-to-HTML plugins
  run. Standard library only (regex), opt-in. (1.1)
- [ ] **Markdown lint / validate** — a plugin that checks Markdown files against
  a set of rules and surfaces problems early at build time; the headline
  feature is catching broken internal links and wikilinks early. Shipped as a
  separate `pyssg_lint` package, not a built-in plugin. (1.1)

## C. Production output quality

- [ ] **Client-side search** — generate a JSON index plus a small widget (a
  minimal pagefind / lunr style). (1.0 or 1.1)
- [ ] **Extended feeds** — JSON Feed and Atom; per-tag feeds.
- [ ] **Incremental build** — deferred to 1.1+ (touches the phased-pass
  architecture and caching).

## D. Extensibility & ecosystem

The settled principle (2026-05-30): **plugins and themes are two different
distribution mechanisms.** A plugin is Python code (via a package / import); a
theme is a bundle of static files (via fetch & vendor). The theme mechanism
(fetch & vendor plus `theme.toml`) is done; the remaining work is on plugins.

- [ ] **Load a plugin by plain Python `import`** in `pyssg.config.py` (no entry
  points). Users `uv add` a package, then import it.
- [ ] **Official plugins to PyPI via CI** (versioned); third-party plugins from
  GitHub via `uv pip install "git+https://..."`.
- [ ] **Monorepo packaging** — `src/plugins/<plugin>`, one package per folder,
  built automatically by CI.
- [ ] **Clear split** between built-in plugins (shipped with the kernel, needed
  by presets) and add-on plugins (separate packages).

## Theme ecosystem by audience

Settled priority (2026-05-30): build the first two themes first — an OSS docs
theme and a personal blog theme.

| Audience | Theme | Priority | Theme features needed |
|---|---|---|---|
| OSS docs maintainer | `docs` | **1** | sidebar, search, syntax highlight, edit-on-GitHub, (versioning later) |
| Personal dev blog | `blog` | **1** | dark mode, RSS / JSON feed, tags, reading time, OG image |
| Team / knowledge base | `kb` | 2 | strong search, breadcrumbs, last-updated, internal links |
| Tool / startup landing | `landing` | 2 | section blocks, SEO / OG, CTA |

Every theme ships responsive CSS plus dark mode, good typography, and **no
Node / build step required from the user**. The prerequisite foundations
(fingerprinting, syntax-highlight CSS, SEO / OG) are done, so theme work can now
proceed.

## Proposed 1.0 scope

The 1.0 core foundation is done: scaffolding, the DX error overlay, syntax
highlighting, asset fingerprinting, SEO / OG, and the theme loading mechanism.
**Still missing for 1.0:** data files, and shipping two polished themes (docs +
blog).

Slated for 1.1: search, shortcodes, extended feeds, the link checker, Obsidian
wikilinks, and Markdown lint / validate. Incremental build comes last.

## Settled decisions

- 2026-05-30: The first two themes are **OSS docs** and **personal blog**.
- 2026-05-30: The next brainstorm / implementation session focuses on the
  **DX onboarding (A)** track.
