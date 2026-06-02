# pyssg theme gallery

This directory is a **gallery of standalone themes** for pyssg. Unlike the
built-in themes under `pyssg/themes/` (which ship inside the `pyssg` wheel),
themes here are **source-only**: they are not packaged or installed with pyssg.
They are meant to be adopted into a site by vendoring (copy the theme directory
into your project) and pointing `Config.layout` at it.

```python
# pyssg.config.py -- after copying themes/blog-technical into your site as ./theme
from pyssg.presets import blog

config = blog(site={"title": "My Blog"}, layout="theme")
```

`Config.layout` accepts a `str` path (resolved relative to the site directory)
or an absolute `Path`, so a vendored theme is referenced the same way as any
local layout package.

## Theme layout

Each theme is a layout package:

```
<theme>/
  layout.toml          # manifest: name, version, default_template, [options]
  templates/           # Jinja2 templates (*.html.j2)
  assets/              # css/js/fonts copied to /assets/ in the output
  i18n/                # UI string tables (en.toml, ...); a site can override them
  THEME-LICENSE        # upstream license when the theme is adapted from another
```

## Configuration

Themes expose configurable options through the **theme configuration API**. A
theme declares its option defaults in the `layout.toml` `[options]` table; a site
overrides any of them via `Config.theme`. Resolution is `theme defaults <-
Config.theme`, and the result is available to templates as `theme.*`.

```toml
# layout.toml
[options]
default_theme = "auto"   # color scheme: "auto" | "light" | "dark"
accent = "#0b66c3"
show_toc = true
```

```python
config.theme = {"default_theme": "dark", "accent": "#e25555"}
```

The mechanism is standardized; the **option vocabulary is per-theme**, so read
each theme's own option list. Keys a theme does not declare are still passed
through to templates but trigger a non-fatal warning (typo guard). For
cross-theme consistency, theme authors are encouraged -- not required -- to reuse
conventional names where they apply, currently:

| Convention | Meaning |
| --- | --- |
| `default_theme` | Initial color scheme: `"auto"`, `"light"`, or `"dark"`. |
| `accent` | Primary accent color. |

## Themes

| Theme | Adapted from | Notes |
| --- | --- | --- |
| `blog-minimal` | [hugo-coder](https://github.com/luizdepra/hugo-coder) (MIT) | Minimal blog: clean typography, post list + post page, light/dark toggle. |
| `blog-technical` | [hugo-PaperMod](https://github.com/adityatelange/hugo-PaperMod) (MIT) | Technical blog: TOC, tags, reading time, code copy, light/dark toggle. |
| `docs-technical` | [docsy](https://github.com/google/docsy) (layout reference; CSS original) | Technical docs: navbar, left nav sidebar, "on this page" TOC, breadcrumbs, prev/next. |

Themes whose stylesheet is compiled offline from upstream SCSS document the exact
source commit and reproduction command in their `STYLE.md` (the pyssg build never
compiles SCSS; only the static CSS is shipped).
