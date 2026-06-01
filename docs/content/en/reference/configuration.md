---
title: Configuration reference
nav_title: Configuration
order: 3
---

# Configuration reference

A site is configured by a `pyssg.config.py` file at the site root. It must define a
module-level variable named `config` bound to a `pyssg.config.Config` instance.
Loading is deterministic and side-effect free: the file is imported fresh on each
call and the `config` variable is read back.

## The `Config` object

```python
from pyssg.config import Config
```

| Field | Type | Default | Description |
|---|---|---|---|
| `content_dir` | `str` | `"content"` | Source content directory, relative to the site. |
| `output_dir` | `str` | `"dist"` | Build output directory, relative to the site. |
| `layout` | `str \| Path \| None` | `None` | Theme. A `str` is a path relative to the site; an absolute `Path` is used as-is (built-in themes resolve to absolute paths via `pyssg.themes.theme_path`). |
| `base_url` | `str` | `""` | Absolute site base URL, used for the sitemap, RSS, and `hreflang`. |
| `plugins` | `list[Plugin]` | `[]` | Plugin instances in **apply order**. |
| `site` | `dict[str, object]` | `{}` | Arbitrary template variables (`title`, `description`, ...). |

Directory fields are joined against the site root when the engine runs. The
`plugins` list order is the order in which plugins apply.

## Presets

A **preset** is a pure factory that returns a fully populated `Config`, bundling
the right built-in plugins in the right apply order plus a default theme. The basic
user writes a one-line config and never has to know which plugins exist or how they
must be ordered.

### `docs`

```python
from pyssg.presets import docs
```

A documentation site: directory-based navigation, taxonomy, wikilinks /
transclusion, RSS, and sitemap. Default theme: the built-in `docs` theme.

```python
config = docs(
    site={"title": "My Docs"},
    base_url="https://example.com",
)
```

Keyword arguments:

| Argument | Default | Description |
|---|---|---|
| `site` | `None` | Template variables. |
| `base_url` | `""` | Absolute site base URL. |
| `content_dir` | `"content"` | Content directory. |
| `output_dir` | `"dist"` | Output directory. |
| `layout` | `None` | Override the default `docs` theme with a site-local layout. |
| `highlight_style` | `"default"` | Pygments style for code highlighting. |
| `rss_title` | `None` | RSS feed title (defaults to the site title). |
| `extra_plugins` | `None` | Plugins appended after the defaults (so they run last). |

### `blog`

```python
from pyssg.presets import blog
```

A blog: posts under `content/posts/`, newest-first listing with pagination and
RSS. Default theme: the built-in `blog` theme.

```python
config = blog(
    site={"title": "My Blog"},
    base_url="https://example.com",
)
```

## Composing your own

Because a preset just returns a `Config`, you can:

- **Extend** a preset with `extra_plugins` (the common case - see the
  [i18n](../how-to/internationalization.md) and
  [API reference](../how-to/api-reference.md) guides), or
- **Build a `Config` by hand**, choosing and ordering plugins yourself, when you
  need full control.

The [plugins and hooks reference](plugins.md) lists every built-in plugin you can
assemble.
