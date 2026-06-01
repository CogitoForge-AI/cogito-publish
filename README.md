# pyssg

A fast, incremental static site generator for Markdown, with a Webpack-inspired
plugin architecture. Built for **documentation sites**, **blogs**, and large
**wikis / knowledge bases**.

The core (`pyssg.core`) is pure standard library; every third-party dependency
lives in a peripheral plugin. Builds are deterministic — building twice produces
byte-identical output.

## Features

- **Incremental builds** — on each save, only the pages that actually changed are
  re-rendered; everything else is served from cache. Incremental output is
  guaranteed byte-identical to a full rebuild.
- **Plugin pipeline** — content flows through a chain of hooks (load → parse →
  link → render), each owned by a small, composable plugin. Add your own by
  tapping into a hook.
- **Obsidian-style linking** — `[[wikilinks]]`, `![[transclusion]]`, automatic
  **backlinks**, and broken-link detection out of the box.
- **Zero-config taxonomy** — just add `tags:` or `category:` in frontmatter and
  the `/tags/` and `/categories/` index pages appear automatically.
- **Rich Markdown** — code highlighting (Pygments), Mermaid diagrams, internal
  link rewriting, table of contents, reading time, and excerpts.
- **Batteries included** — sidebar navigation, breadcrumbs, prev/next, RSS feed,
  and sitemap generated for you.
- **Live-reload dev server** — `serve` watches your files, rebuilds incrementally,
  and refreshes the browser.

## Requirements

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) (package and environment manager)

## Installation

pyssg is installed directly from GitHub (it is not published to PyPI).

To add it as a dependency in your own project:

```bash
uv add git+https://github.com/magiskboy/pyssg
```

Or clone the repository to develop against it:

```bash
git clone https://github.com/magiskboy/pyssg && cd pyssg
uv sync
```

## Quick start

The fastest way to begin is with a **preset** — a ready-made configuration that
bundles the right plugins and a default theme.

```bash
# Scaffold a new site (use --preset blog for a blog)
uv run python -m pyssg --site my-site init --preset docs

# Build to my-site/dist
uv run python -m pyssg --site my-site build

# Watch + incremental rebuild + live-reload at http://127.0.0.1:8000
uv run python -m pyssg --site my-site serve
```

`init` writes a one-line config plus some sample content. The whole config file
is just:

```python
from __future__ import annotations
from pyssg.presets import docs        # or: from pyssg.presets import blog

config = docs(site={"title": "My Docs"}, base_url="https://example.com")
```

Two presets ship today:

- **`docs`** — documentation site: directory-based navigation, taxonomy,
  wikilinks/transclusion, RSS, and sitemap.
- **`blog`** — blog: posts under `content/posts/`, newest-first listing with
  pagination and RSS.

Edit any file under `content/` and the page rebuilds and reloads automatically.

## CLI

| Command | Description |
|---|---|
| `init --preset docs\|blog` | Scaffold a new site for a preset. |
| `build` | Full build to `output_dir`. |
| `serve` | Watch + incremental rebuild + dev server with live-reload. |
| `clean` | Remove `output_dir` and cache. |
| `eject-layout --theme docs\|blog --to DIR` | Copy a built-in theme into your site to customize templates/CSS. |

Pass `--site PATH` to select the site directory (defaults to the current one).
Run any command with `--help` for its options.

## Examples

```bash
uv run python -m pyssg --site examples/docs serve   # bilingual docs site
uv run python -m pyssg --site examples/wiki serve   # ~117-note knowledge base
```

## Documentation

- Design history: [`docs/content/technical-spec-v0.1.0.md`](docs/content/technical-spec-v0.1.0.md)
- Contributing conventions: [`CLAUDE.md`](CLAUDE.md)

## License

[MIT](LICENSE)
