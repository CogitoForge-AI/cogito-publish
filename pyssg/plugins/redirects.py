"""Redirects plugin.

Emits a tiny ``meta refresh`` HTML page for every ``old URL -> new URL`` rule a
site declares, so links to retired paths keep resolving after a migration
(``/posts/`` -> ``/``, a renamed slug -> its new permalink, ``/about/`` -> an
external CV). Each rule materializes a virtual :class:`~pyssg.core.node.Page`
with ``template=None``, whose body is the redirect HTML emitted verbatim by the
render plugin (no layout) -- the same "summarizer page" mechanism the
sitemap/rss plugins use.

The rules are *literal*: the source is the exact old URL (``/posts/`` ->
``posts/index.html``) and the target is used as-is, so an absolute path
(``/new/``) or a full external URL (``https://cv.example.com``) both work. This
plugin is therefore locale-agnostic by design -- a localized site lists the old
localized URLs explicitly rather than having the engine partition them.

A rule is skipped when its source URL already belongs to a real page (a redirect
must never overwrite live content); the remaining set is materialized
deterministically (sorted by source, body derived purely from the rule and
``base_url``), so two builds are byte-identical and an incremental rebuild reuses
cached output whenever the rules are unchanged. Rules dropped between builds have
their stale page -- and thus their output -- removed.

The algorithm lives in :class:`RedirectsPlugin` methods so a site can subclass it
to change the redirect markup (e.g. add a delay or a styled body) or the page-id
scheme without forking the plugin (see ``AGENTS.md`` on plugin design).
"""

from __future__ import annotations

import hashlib
import json
from typing import TYPE_CHECKING
from xml.sax.saxutils import escape, quoteattr

from pyssg.core.node import Page
from pyssg.core.types import NodeKind

if TYPE_CHECKING:
    from collections.abc import Mapping

    from pyssg.core.build import Build
    from pyssg.core.builder import Builder

#: Node-id prefix for every redirect page; the source URL is appended so each
#: rule owns a stable, unique node across rebuilds.
_PAGE_PREFIX = "page:redirect:"
_BASE_CACHE_VERSION = "1.0.0"


def _is_external(target: str) -> bool:
    """True when ``target`` is an absolute URL (has a scheme or is protocol-relative).

    Such a target is used verbatim for both the refresh and the canonical link;
    a site-relative target (``/new/``) is instead joined onto ``base_url`` to form
    an absolute canonical URL.
    """
    return target.startswith(("http://", "https://", "//"))


def render_redirect_html(*, target: str, canonical: str) -> str:
    """Build the ``meta refresh`` redirect document pointing at ``target``.

    ``target`` is the value used for the instant ``<meta http-equiv="refresh">``
    and the visible fallback link; ``canonical`` is the absolute URL advertised to
    crawlers via ``<link rel="canonical">``. The page is marked ``noindex`` so the
    stub itself never competes with the destination in search results. Both URLs
    are attribute- and text-escaped, so an ampersand in a query string is safe.
    """
    href = quoteattr(target)
    return (
        "<!DOCTYPE html>\n"
        '<html lang="en">\n'
        "<head>\n"
        '<meta charset="utf-8">\n'
        "<title>Redirecting</title>\n"
        f'<link rel="canonical" href={quoteattr(canonical)}>\n'
        '<meta name="robots" content="noindex">\n'
        f'<meta http-equiv="refresh" content={quoteattr(f"0; url={target}")}>\n'
        "</head>\n"
        "<body>\n"
        f"<p>This page has moved to <a href={href}>{escape(target)}</a>.</p>\n"
        "</body>\n"
        "</html>\n"
    )


class RedirectsPlugin:
    """Built-in ``meta refresh`` redirect generator, one page per rule.

    Customise by subclassing: override :meth:`render_html` for the redirect markup,
    :meth:`page_id` for the node-id scheme, or :meth:`canonical_url` for how a
    site-relative target is made absolute, while reusing the collision check and
    emit wiring. Pass the rules through the :func:`redirects` factory.
    """

    name = "redirects"
    #: Base cache version; a digest of the rules is folded in per instance so a
    #: changed rule set never reuses a page rendered under the old rules.
    cache_version = _BASE_CACHE_VERSION

    def __init__(self, *, rules: Mapping[str, str] | None = None) -> None:
        # Copy so a caller mutating their dict after construction cannot change
        # what this plugin emits mid-build.
        self._rules: dict[str, str] = dict(rules or {})
        self.cache_version = self._compute_cache_version()

    def _compute_cache_version(self) -> str:
        """Fold the rules into the cache key so a changed map invalidates output.

        The empty default keeps the bare base version (so an unchanged cache
        survives an upgrade); any rules append a short digest of the sorted map.
        """
        if not self._rules:
            return _BASE_CACHE_VERSION
        payload = json.dumps(self._rules, sort_keys=True)
        digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12]
        return f"{_BASE_CACHE_VERSION}:{digest}"

    def apply(self, builder: Builder) -> None:
        @builder.hooks.this_compilation.tap(self.name)
        def _wire(build: Build) -> None:
            # Run after the summarizer plugins so their virtual pages are present
            # when we check a source URL against the set of real page URLs.
            @build.hooks.evaluate_collections.tap(self.name, after=("nav", "taxonomy"))
            def _eval(b: Build) -> None:
                self.build(b)

    def page_id(self, source: str) -> str:
        """Stable node id for the redirect page serving ``source``."""
        return f"{_PAGE_PREFIX}{source}"

    def canonical_url(self, target: str, base_url: str) -> str:
        """Absolute URL advertised as canonical for a redirect to ``target``.

        An already-absolute target is returned unchanged; a site-relative target
        is joined onto ``base_url`` so crawlers see a fully-qualified destination.
        """
        if _is_external(target):
            return target
        return f"{base_url}{target}"

    def render_html(self, source: str, target: str, base_url: str) -> str:
        """Render the redirect document for one ``source -> target`` rule."""
        return render_redirect_html(target=target, canonical=self.canonical_url(target, base_url))

    def build(self, build: Build) -> None:
        """(Re)materialize one redirect page per rule and drop stale ones.

        Skips any rule whose source URL or target is empty, or whose source URL is
        already served by a real page (live content always wins). Iterates the
        rules sorted by source so the emitted set is order-independent.
        """
        config = build.builder.config
        base_url = config.base_url if config is not None else ""
        taken = self._live_page_urls(build)

        owned: set[str] = set()
        for source, target in sorted(self._rules.items()):
            if not source or not target or source in taken:
                continue
            pid = self.page_id(source)
            _set_redirect_page(build, pid, source, self.render_html(source, target, base_url))
            owned.add(pid)

        # Remove redirect pages from a previous evaluation (a rule that was
        # deleted) so the finalize page-set diff deletes their stale output.
        for node in list(build.graph.nodes()):
            if node.id.startswith(_PAGE_PREFIX) and node.id not in owned:
                build.graph.remove(node.id)

    def _live_page_urls(self, build: Build) -> set[str]:
        """URLs owned by non-redirect pages, so a redirect never shadows one."""
        return {
            node.url
            for node in build.graph.nodes()
            if isinstance(node, Page) and not node.id.startswith(_PAGE_PREFIX)
        }


def _set_redirect_page(build: Build, pid: str, url: str, html: str) -> None:
    """Create or update the redirect page at ``url`` carrying ``html`` verbatim."""
    meta: dict[str, object] = {"title": "Redirecting", "content_html": html}
    existing = build.graph.get(pid)
    if isinstance(existing, Page):
        existing.url = url
        existing.template = None
        existing.meta = meta
    else:
        build.graph.add_node(Page(id=pid, kind=NodeKind.PAGE, url=url, template=None, meta=meta))


def build_redirects(build: Build, rules: Mapping[str, str] | None = None) -> None:
    """Materialize the redirect pages. Thin wrapper around :meth:`RedirectsPlugin.build`."""
    RedirectsPlugin(rules=rules).build(build)


def redirects(rules: Mapping[str, str] | None = None) -> RedirectsPlugin:
    """Factory used in ``pyssg.config.py``.

    ``rules`` maps each old URL to its replacement; see :class:`RedirectsPlugin`.
    """
    return RedirectsPlugin(rules=rules)
