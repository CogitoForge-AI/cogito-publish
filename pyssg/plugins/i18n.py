"""Internationalisation (i18n) plugin: directory-based, route-driven locales.

The locale of a document is its top-level content directory: ``content/en/...``
and ``content/vi/...`` are the English and Vietnamese variants of the same site.
The *default* locale is served at the site root (its directory segment is
stripped from the URL); every other locale keeps its segment as a URL prefix::

    content/en/guide/intro.md  ->  /guide/intro/      (en = default)
    content/vi/guide/intro.md  ->  /vi/guide/intro/

When i18n is enabled the only content the engine emits is content that lives
under a recognised locale directory. A file or folder whose first path segment
is not a configured locale (``content/about.md``, ``content/blog/...``) produces
no page: the ``route`` tap returns ``""`` and the permalink generator skips it.
There is deliberately no way to override a document's locale from frontmatter --
the directory is the single source of truth, which keeps the feature free of
edge cases.

Pure: the locale, the translation key and the routed URL are all functions of
the source path plus the static config, never of a clock or randomness, so two
builds of the same tree are byte-identical. The locale config is folded into
``cache_version`` so changing ``locales`` / ``default_locale`` busts the cache.

This is a built-in plugin and uses the standard library only.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

from pyssg.core.errors import ConfigError
from pyssg.core.node import Document, Page
from pyssg.core.types import NodeKind

if TYPE_CHECKING:
    from pyssg.core.build import Build
    from pyssg.core.builder import Builder
    from pyssg.core.node import Node

# One translation variant as exposed to templates: the locale code, its URL and
# the page title in that locale.
type Variant = dict[str, str]

# Parse-stage for tagging ``meta["lang"]``: after frontmatter (100), before the
# markdown body render (200). The exact value is not load-bearing -- the lang is
# derived purely from the path -- but keeping it early documents intent.
_PARSE_STAGE = 150

# Route-stage: run late so i18n has the final say on the locale prefix, after any
# other plugin has contributed to the URL.
_ROUTE_STAGE = 500


def locale_of(source_path: str, locales: frozenset[str]) -> str | None:
    """Locale of a document, or ``None`` if it is not under a locale directory.

    The locale is the first path segment when that segment is a configured
    locale; otherwise the document lives outside the i18n tree and is dropped.
    """
    first = source_path.split("/", 1)[0]
    return first if first in locales else None


def translation_key(source_path: str, locales: frozenset[str]) -> str:
    """Path identifying a document across locales (the part after the locale dir).

    ``en/guide/intro.md`` and ``vi/guide/intro.md`` share the key
    ``guide/intro.md``. A path outside any locale directory is returned verbatim.
    """
    first, _, rest = source_path.partition("/")
    return rest if first in locales else source_path


def route_url(url: str, source_path: str, locales: frozenset[str], default: str) -> str:
    """Apply the locale routing rule to a computed URL.

    Returns ``""`` when the document is not under a locale directory (the page is
    then suppressed). For the default locale the leading ``/{default}/`` segment
    is stripped (so it is served at the root); other locales keep their segment.
    """
    if locale_of(source_path, locales) is None:
        return ""  # outside any locale directory -> no page
    prefix = f"/{default}/"
    if url == prefix:
        return "/"
    if url.startswith(prefix):
        return "/" + url[len(prefix) :]
    return url


def build_i18n_data(build: Build, default_locale: str, locales: frozenset[str]) -> None:
    """Group pages by translation key and stash the result on ``site_data``.

    Runs at ``evaluate_collections`` (once every page has its final routed URL).
    Pages sharing a translation key (same path under different locale dirs) are
    cross-linked. The shape written is::

        site_data["i18n"] = {
            "default_locale": "en",
            "languages": ["en", "vi"],            # all configured, sorted
            "by_url": {
                "/guide/intro/": {                # the English (default) page
                    "lang": "en",
                    "translations": [{"lang": "vi", "url": "/vi/guide/intro/", "title": ...}],
                },
                ...
            },
        }

    ``translations`` lists only the *other* locales that actually have the page,
    so a language switcher links to real translations and never to a 404
    (untranslated pages are simply absent).
    """
    # translation key -> locale -> variant. Sorted node iteration keeps the
    # output deterministic if two docs ever collide on the same (key, locale).
    groups: dict[str, dict[str, Variant]] = {}
    page_locale: dict[str, tuple[str, str]] = {}  # page url -> (locale, key)
    for node in sorted(build.graph.nodes(), key=lambda n: n.id):
        if not (isinstance(node, Page) and node.generated_from):
            continue
        doc = build.graph.get(node.generated_from[0])
        if not (isinstance(doc, Document) and doc.source_path is not None):
            continue
        locale = locale_of(doc.source_path, locales)
        if locale is None:
            continue
        key = translation_key(doc.source_path, locales)
        title = str(doc.meta.get("title") or node.url)
        groups.setdefault(key, {})[locale] = {"lang": locale, "url": node.url, "title": title}
        page_locale[node.url] = (locale, key)

    by_url: dict[str, object] = {}
    for url, (locale, key) in page_locale.items():
        variants = groups.get(key, {})
        translations = [variant for loc, variant in sorted(variants.items()) if loc != locale]
        by_url[url] = {"lang": locale, "translations": translations}

    build.site_data["i18n"] = {
        "default_locale": default_locale,
        "languages": sorted(locales),
        "by_url": by_url,
    }


class I18nPlugin:
    """Routes documents by their top-level locale directory."""

    name = "i18n"

    def __init__(self, default_locale: str, locales: Sequence[str]) -> None:
        locale_set = frozenset(locales)
        if default_locale not in locale_set:
            raise ConfigError(
                f"i18n default_locale {default_locale!r} is not in locales {sorted(locale_set)}"
            )
        self._default = default_locale
        self._locales = locale_set
        # Sorted tuple for a deterministic, config-sensitive cache key: changing
        # the locale set or default must bust cached routes/renders.
        ordered = ",".join(sorted(locale_set))
        self.cache_version = f"1.0.0:{default_locale}:{ordered}"

    def apply(self, builder: Builder) -> None:
        @builder.hooks.this_compilation.tap(self.name)
        def _wire(build: Build) -> None:
            @build.hooks.parse.tap(self.name, stage=_PARSE_STAGE)
            def _parse(node: Node) -> None:
                if node.kind is not NodeKind.MARKDOWN:
                    return
                locale = locale_of(node.source_path or "", self._locales)
                if locale is not None:
                    node.meta["lang"] = locale

            @build.hooks.route.tap(self.name, stage=_ROUTE_STAGE)
            def _route(url: str, node: Node) -> str:
                return route_url(url, node.source_path or "", self._locales, self._default)

            @build.hooks.evaluate_collections.tap(self.name)
            def _collect(b: Build) -> None:
                build_i18n_data(b, self._default, self._locales)


def i18n(default_locale: str, locales: Sequence[str]) -> I18nPlugin:
    """Factory used in ``pyssg.config.py``."""
    return I18nPlugin(default_locale=default_locale, locales=locales)
