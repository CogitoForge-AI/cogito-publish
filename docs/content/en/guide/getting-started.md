---
title: Getting started
order: 1
---

# Getting started

This guide takes you from an empty folder to a built site.

## Requirements

- Python 3.13 or newer
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

## Install

pyssg installs directly from GitHub - it is not published on PyPI. The kernel has
no dependencies; the built-in `Markdown`, `Template` and `Highlight` plugins need
third party libraries, bundled in the `plugins` extra:

```bash
# uv (recommended)
uv add "pyssg[plugins] @ git+https://github.com/magiskboy/pyssg.git"
# pip
pip install "pyssg[plugins] @ git+https://github.com/magiskboy/pyssg.git"
```

Pin to a released tag by appending `@v0.1.0` to the URL.

## Project layout

A typical project looks like this:

```text
my-site/
  content/            # your Markdown sources
    index.md
    guide/
      intro.md
  layouts/            # Jinja2 templates
    default.html
    list.html
  pyssg.config.py     # configuration
  public/             # build output (generated)
```

The `layouts/` folder sits next to `content/`. The `Template` plugin looks for
templates in `<src>/../layouts` by default.

## Write some content

```text
---
title: Hello
---
# Hello world

This is **Markdown**.
```

The block between `---` fences is the *frontmatter*: per-page metadata your
templates and plugins can read.

## Add a layout

```html
<!-- layouts/default.html -->
<!doctype html>
<title>{{ page.title }}</title>
<main>{{ content }}</main>
```

`content` is the rendered HTML body; `page` exposes the frontmatter.

## Configure

```python
# pyssg.config.py
from pyssg.config import Config
from pyssg_cli.presets import docs


def config() -> Config:
    return Config(src="content", out="public", plugins=docs())
```

## Build

```bash
pyssg build
```

Your site is now in `public/`. To use a config file in a different location:

```bash
pyssg build -c path/to/pyssg.config.py
```

Next: learn the [configuration](/en/guide/configuration/) options in detail.
