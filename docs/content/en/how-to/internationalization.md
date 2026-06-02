---
title: Add internationalization (i18n)
nav_title: Internationalization
order: 2
---

# Add internationalization (i18n)

**Goal:** serve the same site in several languages, with a language switcher and
correct `hreflang` tags, without ever linking to a missing translation.

## 1. Add the plugin

The `i18n` plugin is built in. Append it to a preset with `extra_plugins`:

```python
from __future__ import annotations

from pyssg.presets import docs
from pyssg.plugins import i18n

config = docs(
    site={"title": "My Docs"},
    base_url="https://example.com",
    extra_plugins=[i18n(default_locale="en", locales=["en", "vi"])],
)
```

## 2. Lay content out one directory per locale

The locale is the **top-level directory** under `content/` - there is no
frontmatter override:

```
content/
  en/index.md          ->  /            (default locale, served at the root)
  en/guide/intro.md    ->  /guide/intro/
  vi/index.md          ->  /vi/
  vi/guide/intro.md    ->  /vi/guide/intro/
```

The rules are deliberately simple:

- The **default locale** is served at the site root (its prefix is stripped);
  every other locale keeps its `/<locale>/` prefix.
- Content **outside** any locale directory produces no page.
- A page is emitted only for locales that **actually have the file** - there is no
  content fallback, so a language switcher never links to a missing translation.

## 3. Use the template variables

The plugin gives every page three extra template variables:

- `lang` - the current page's locale.
- `translations` - the same page in other locales, each `{lang, url, title}`.
- `languages` - all configured locales.

The built-in `docs` and `blog` themes already use them to render `<html lang>`,
`hreflang` alternates, and a header switcher, so with the layout above you get a
working bilingual site out of the box.

## 4. Build and check

```bash
pyssg --site my-site build
```

English pages appear at the root and Vietnamese pages under `/vi/`. See
`examples/docs/` in the repository for a complete bilingual sample.
