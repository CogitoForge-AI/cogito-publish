"""Navigation plugin.

Builds site-wide navigation data during ``evaluate_collections`` and stashes it
on ``build.site_data`` for templates (via the render context): a section-grouped
``menu`` (sidebar), a ``url_titles`` map (breadcrumbs), and an ``ordered_pages``
list (prev/next).

This is the "fan-out" feature: nav appears on every page. Correctness under
incremental builds is guaranteed by the engine's render sweep -- a structural
change (add/move/delete a doc) changes the menu, so every page's rendered HTML
differs and is re-emitted; a body-only edit leaves the menu identical, so other
pages hit the render cache and are not re-emitted.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pyssg.core.node import Document, Page

if TYPE_CHECKING:
    from pyssg.core.build import Build
    from pyssg.core.builder import Builder

_NO_ORDER = 10**9  # pages without a frontmatter `order` sort last, then by url


def _order_of(meta: dict[str, object]) -> int:
    value = meta.get("order")
    if isinstance(value, bool):  # bool is an int subclass; treat as unset
        return _NO_ORDER
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.lstrip("-").isdigit():
        return int(value)
    return _NO_ORDER


def _doc_page_entries(build: Build) -> list[dict[str, object]]:
    """One entry per document page: url, title, order, section, locale.

    ``locale`` is the document's i18n locale (``meta["lang"]``, empty when i18n is
    not in use). ``section`` is the first URL segment *after* any ``/<locale>/``
    prefix, so a localised page such as ``/vi/guide/intro/`` groups under
    ``guide`` rather than ``vi`` -- giving each locale a correctly grouped sidebar.
    """
    entries: list[dict[str, object]] = []
    for node in build.graph.nodes():
        if not (isinstance(node, Page) and node.generated_from):
            continue
        doc = build.graph.get(node.generated_from[0])
        if not isinstance(doc, Document):
            continue
        title = doc.meta.get("nav_title") or doc.meta.get("title") or node.url
        lang = doc.meta.get("lang")
        locale = lang if isinstance(lang, str) else ""
        path = node.url
        prefix = f"/{locale}/"
        if locale and path.startswith(prefix):
            path = "/" + path[len(prefix) :]
        segments = [s for s in path.split("/") if s]
        entries.append(
            {
                "url": node.url,
                "title": str(title),
                "order": _order_of(doc.meta),
                "section": segments[0] if segments else "",
                "locale": locale,
            }
        )
    return entries


def _sort_key(entry: dict[str, object]) -> tuple[int, str]:
    order = entry["order"]
    url = entry["url"]
    return (order if isinstance(order, int) else _NO_ORDER, str(url))


def _locale_sort_key(entry: dict[str, object]) -> tuple[str, int, str]:
    """Order pages within a locale: locale, then frontmatter order, then url."""
    order = entry["order"]
    return (
        str(entry["locale"]),
        order if isinstance(order, int) else _NO_ORDER,
        str(entry["url"]),
    )


def build_navigation(build: Build) -> None:
    """Populate ``build.site_data`` with menu / url_titles / ordered_pages.

    Navigation is grouped per locale: each menu section carries a ``locale`` tag
    and is keyed by ``(locale, section)``, and ``ordered_pages`` keeps every
    locale's pages contiguous so prev/next never crosses languages. A single-locale
    (or no-i18n) site has every locale equal to ``""``, which reduces to the plain
    alphabetical-by-section menu and a flat ordered list.
    """
    entries = sorted(_doc_page_entries(build), key=_sort_key)

    url_titles: dict[str, str] = {str(e["url"]): str(e["title"]) for e in entries}

    ordered = sorted(entries, key=_locale_sort_key)
    ordered_pages = [{"url": e["url"], "title": e["title"], "locale": e["locale"]} for e in ordered]

    sections: dict[tuple[str, str], list[dict[str, object]]] = {}
    for entry in entries:
        key = (str(entry["locale"]), str(entry["section"]))
        sections.setdefault(key, []).append({"url": entry["url"], "title": entry["title"]})
    menu = [
        {"locale": locale, "section": section, "items": items}
        for (locale, section), items in sorted(sections.items())
    ]

    build.site_data["url_titles"] = url_titles
    build.site_data["ordered_pages"] = ordered_pages
    build.site_data["menu"] = menu


class NavigationPlugin:
    """Computes navigation data each build."""

    name = "nav"
    cache_version = "1.0.0"

    def apply(self, builder: Builder) -> None:
        @builder.hooks.this_compilation.tap(self.name)
        def _wire(build: Build) -> None:
            @build.hooks.evaluate_collections.tap(self.name)
            def _eval(b: Build) -> None:
                build_navigation(b)


def nav() -> NavigationPlugin:
    """Factory used in ``pyssg.config.py``."""
    return NavigationPlugin()
