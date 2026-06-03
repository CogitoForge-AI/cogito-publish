"""Taxonomy plugin: tags + categories, zero-config.

A taxonomy is a named classification dimension; ``tag`` and ``category`` are two
built-in instances of one mechanism, so adding another dimension is
configuration, not engine code. During ``evaluate_collections`` it reads the
relevant frontmatter keys from every document, builds each term's member list,
and materializes virtual pages: a term page per term (``/tags/<term>/``,
``/categories/<a>/<b>/``) and an index page per taxonomy (``/tags/``). Categories
are hierarchical: ``category: a/b`` makes the document a member of both ``a`` and
``a/b``.

When the i18n plugin is loaded, taxonomies are partitioned per locale: the
default locale's pages stay at ``/tags/...`` while every other locale is prefixed
(``/<locale>/tags/...``), so a term page never mixes languages. The split is read
from each document's ``meta["lang"]`` and the page URLs; ``all_<plural>`` is
published per locale (``all_tags`` for the default/root locale, ``all_tags:<locale>``
otherwise). A site without i18n is unchanged.

Terms are grouped by their *slug*, not their raw text, so ``Python`` and
``python`` resolve to one term page (sharing the slug ``python``) with merged
members instead of one silently overwriting the other.

Incremental: term pages are recomputed deterministically each finalize, so
adding/removing a term adds/removes the right page (the engine's page-set diff
cleans vanished outputs) and a term page re-emits only when its membership
actually changes (render cache + emit cutoff).

The algorithm lives in :class:`TaxonomyPlugin` methods so a site can subclass it
to change the URL scheme or per-page metadata without forking (see ``AGENTS.md``
on plugin design).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from pyssg.core.node import Document, Page
from pyssg.core.types import NodeKind
from pyssg.plugins._context import doc_locale, locale_root, page_url_of
from pyssg.plugins.content_meta import slugify

if TYPE_CHECKING:
    from pyssg.core.build import Build
    from pyssg.core.builder import Builder

type Link = dict[str, str]


@dataclass(frozen=True, slots=True)
class Taxonomy:
    """One classification dimension."""

    name: str  # "tag"
    plural: str  # "tags"
    route: str  # "/tags/"
    frontmatter_keys: tuple[str, ...]
    hierarchical: bool = False


def tag() -> Taxonomy:
    return Taxonomy("tag", "tags", "/tags/", ("tags",))


def category() -> Taxonomy:
    return Taxonomy("category", "categories", "/categories/", ("category", "categories"), True)


def _term_slug(term: str, taxo: Taxonomy) -> str:
    if taxo.hierarchical:
        return "/".join(slugify(seg) for seg in term.split("/") if seg)
    return slugify(term)


def _expand(term: str, taxo: Taxonomy) -> list[str]:
    """A hierarchical term yields itself and its ancestors: a/b -> [a, a/b]."""
    if not taxo.hierarchical:
        return [term]
    parts = [p for p in term.split("/") if p]
    return ["/".join(parts[: i + 1]) for i in range(len(parts))]


def _doc_terms(meta: dict[str, object], taxo: Taxonomy) -> set[str]:
    raw: set[str] = set()
    for key in taxo.frontmatter_keys:
        value = meta.get(key)
        if isinstance(value, str):
            raw.add(value)
        elif isinstance(value, list):
            raw.update(str(v) for v in value)
    terms: set[str] = set()
    for term in raw:
        terms.update(_expand(term, taxo))
    return terms


@dataclass(slots=True)
class _TermBucket:
    """One term within one locale: its slug, a canonical display label and members.

    Members are keyed by URL so the same page contributing two raw terms that
    share a slug (``Python``/``python``) is counted once. ``label`` is the
    smallest raw term by sort order, chosen deterministically when variants merge.
    """

    slug: str
    label: str
    members: dict[str, Link] = field(default_factory=dict)

    def merge(self, term: str, member: Link) -> None:
        if term < self.label:
            self.label = term
        self.members.setdefault(member["url"], member)

    def sorted_members(self) -> list[Link]:
        return sorted(self.members.values(), key=lambda m: m["url"])


def _set_page(build: Build, pid: str, url: str, template: str, meta: dict[str, object]) -> None:
    existing = build.graph.get(pid)
    if isinstance(existing, Page):
        existing.url = url
        existing.template = template
        existing.meta = meta
    else:
        build.graph.add_node(
            Page(id=pid, kind=NodeKind.PAGE, url=url, template=template, meta=meta)
        )


@dataclass(slots=True)
class TaxonomyPlugin:
    """Built-in taxonomies; defaults to tag + category."""

    name: str = "taxonomy"
    cache_version: str = "1.2.0"  # bumped: per-locale split + slug-grouped terms
    taxonomies: list[Taxonomy] = field(default_factory=lambda: [tag(), category()])

    def apply(self, builder: Builder) -> None:
        @builder.hooks.this_compilation.tap(self.name)
        def _wire(build: Build) -> None:
            @build.hooks.evaluate_collections.tap(self.name, after=("nav",))
            def _eval(b: Build) -> None:
                self.build(b)

    def build(self, build: Build) -> None:
        """Materialize every taxonomy and drop term/index pages no longer wanted."""
        desired: set[str] = set()
        for taxo in self.taxonomies:
            desired |= self.build_taxonomy(build, taxo)
        for node in list(build.graph.nodes()):
            if (
                node.id.startswith("page:term:") or node.id.startswith("page:taxindex:")
            ) and node.id not in desired:
                build.graph.remove(node.id)

    def build_taxonomy(self, build: Build, taxo: Taxonomy) -> set[str]:
        """Materialize one taxonomy across all locales; return the ids it owns."""
        # locale -> slug -> bucket; plus the URL root chosen for each locale.
        per_locale: dict[str, dict[str, _TermBucket]] = {}
        roots: dict[str, str] = {}
        for node in build.graph.nodes():
            if not (isinstance(node, Document) and node.kind is NodeKind.MARKDOWN):
                continue
            url = page_url_of(build, node.id)
            if url is None:
                continue  # document produced no page (draft, or suppressed by i18n)
            locale = doc_locale(node)
            roots.setdefault(locale, locale_root(locale, url))
            title = str(node.meta.get("title") or node.id)
            member: Link = {"title": title, "url": url}
            buckets = per_locale.setdefault(locale, {})
            for term in _doc_terms(node.meta, taxo):
                slug = _term_slug(term, taxo)
                bucket = buckets.get(slug)
                if bucket is None:
                    bucket = _TermBucket(slug=slug, label=term)
                    buckets[slug] = bucket
                bucket.merge(term, member)

        owned: set[str] = set()
        for locale, buckets in per_locale.items():
            owned |= self._emit_locale(build, taxo, locale, roots[locale], buckets)
        return owned

    def _emit_locale(
        self,
        build: Build,
        taxo: Taxonomy,
        locale: str,
        root: str,
        buckets: dict[str, _TermBucket],
    ) -> set[str]:
        id_loc = "" if root == "/" else f"{locale}:"
        all_terms = sorted(
            (
                {
                    "term": b.label,
                    "count": len(b.members),
                    "url": self.term_url(taxo, b.slug, root),
                }
                for b in buckets.values()
            ),
            key=lambda t: str(t["term"]),
        )
        data_key = f"all_{taxo.plural}" if root == "/" else f"all_{taxo.plural}:{locale}"
        build.site_data[data_key] = all_terms

        index_id = f"page:taxindex:{taxo.name}:{id_loc}".rstrip(":")
        owned = {index_id}
        for bucket in buckets.values():
            pid = f"page:term:{taxo.name}:{id_loc}{bucket.slug}"
            owned.add(pid)
            _set_page(
                build,
                pid,
                self.term_url(taxo, bucket.slug, root),
                "term.html.j2",
                self.term_meta(taxo, locale, bucket),
            )
        _set_page(
            build,
            index_id,
            self.index_url(taxo, root),
            "terms.html.j2",
            self.index_meta(taxo, locale, all_terms),
        )
        return owned

    def term_url(self, taxo: Taxonomy, slug: str, root: str) -> str:
        """URL of a single term page under a locale ``root`` (see :func:`locale_root`)."""
        return f"{root}{taxo.plural}/{slug}/"

    def index_url(self, taxo: Taxonomy, root: str) -> str:
        """URL of a taxonomy's index page under a locale ``root``."""
        return f"{root}{taxo.plural}/"

    def term_meta(self, taxo: Taxonomy, locale: str, bucket: _TermBucket) -> dict[str, object]:
        """Template metadata for one term page."""
        return {
            "title": f"{taxo.name.title()}: {bucket.label}",
            "term": bucket.label,
            "taxonomy": taxo.name,
            "count": len(bucket.members),
            "members": bucket.sorted_members(),
            "kind": "term",
            "lang": locale,
        }

    def index_meta(
        self, taxo: Taxonomy, locale: str, all_terms: list[dict[str, object]]
    ) -> dict[str, object]:
        """Template metadata for a taxonomy's index page."""
        return {
            "title": taxo.plural.title(),
            "terms": all_terms,
            "kind": "term-index",
            "lang": locale,
        }


def build_taxonomies(build: Build, taxonomies: list[Taxonomy]) -> None:
    """Materialize the given taxonomies. Thin wrapper around :meth:`TaxonomyPlugin.build`."""
    TaxonomyPlugin(taxonomies=taxonomies).build(build)


def taxonomy(*taxonomies: Taxonomy) -> TaxonomyPlugin:
    """Factory. No args -> tag + category zero-config."""
    if taxonomies:
        return TaxonomyPlugin(taxonomies=list(taxonomies))
    return TaxonomyPlugin()
