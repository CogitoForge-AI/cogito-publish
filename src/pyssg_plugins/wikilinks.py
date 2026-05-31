"""WikiLink plugin: resolve Obsidian-style ``[[wikilinks]]`` to page URLs.

Taps ``transform`` at a stage after Markdown (stage 0), post-processing the
rendered HTML. python-markdown leaves ``[[Note]]`` untouched as literal text, so
the same HTML-pass strategy the LinkResolver uses applies: ``[[...]]`` inside a
code span or fence stays inside ``<code>``/``<pre>`` and is skipped, so authored
examples are never rewritten.

A ``[[Note Title]]`` target is resolved against a name index built from
``build.sources``: a page is addressable by its file stem (``Note Title.md`` ->
``[[Note Title]]``) or by a path without the suffix (``[[folder/Note]]``), both
matched case-insensitively. Two variants are supported on top of the base form:

- ``[[Note|custom text]]`` -- an explicit display alias.
- ``[[Note#Heading]]`` -- a link to a slugified heading id on the target page;
  ``[[#Heading]]`` (empty name) anchors within the current page.

The link text defaults to the target as written (``Note``, ``Note > Heading``,
or the heading alone) unless an alias overrides it; it is always HTML-escaped.

Unresolved targets render as a clearly-marked broken ``<span>`` and are recorded
in ``build.meta["broken_links"]`` so the BrokenLinks plugin can report them.

Embeds/transclusion (``![[Note]]``, ``![[Note#Heading]]``) inline another note's
rendered body (or a single section). Because every source is transformed before
any is rendered, the embed pass runs in ``render`` (before the Template tap, so
it operates on the rendered body, not the wrapped page) over a one-time snapshot
of all bodies. Embeds are expanded recursively with a guard that breaks cycles.

The plugin uses the standard library only.
"""

from __future__ import annotations

import html
import re
from dataclasses import dataclass

from pyssg.build import Build
from pyssg.builder import Builder
from pyssg.content import URL
from pyssg.models import Source
from pyssg_plugins.link_resolver import BrokenLink, broken_links
from pyssg_plugins.permalink import slugify

# Run after Markdown's transform (stage 0); the literal ``[[...]]`` text exists by
# then. Resolved links carry final URLs, so the LinkResolver (stage 50) ignores
# them.
_TRANSFORM_STAGE = 40

# Run embeds early in ``render``, before the Template tap (stage 0) wraps the body
# in a layout, so they inline the rendered body rather than a full page.
_EMBED_STAGE = -100

# Protect rendered code so ``[[...]]`` inside it is never rewritten. ``<pre>``
# (fenced blocks) is matched before ``<code>`` (inline code).
_CODE_RE = re.compile(r"<pre\b.*?</pre>|<code\b.*?</code>", re.DOTALL | re.IGNORECASE)

# A wikilink: ``[[target]]`` not preceded by ``!`` (which marks an embed).
# The target is any run of non-bracket characters, surrounding space trimmed.
_WIKILINK_RE = re.compile(r"(?<!!)\[\[\s*([^\[\]]+?)\s*\]\]")

# An embed: ``![[target]]``.
_EMBED_RE = re.compile(r"!\[\[\s*([^\[\]]+?)\s*\]\]")

# A rendered heading element, capturing its level and inner HTML.
_HEADING_RE = re.compile(r"<h([1-6])\b[^>]*>(.*?)</h\1>", re.DOTALL | re.IGNORECASE)

_INDEX_KEY = "_wikilink_index"
_EMBED_KEY = "_wikilink_embed_index"


class WikiLink:
    def __init__(
        self,
        *,
        link_class: str = "wikilink",
        broken_class: str = "wikilink-broken",
        embed_class: str = "wikilink-embed",
    ) -> None:
        self._link_class = link_class
        self._broken_class = broken_class
        self._embed_class = embed_class

    def apply(self, builder: Builder) -> None:
        builder.hooks.transform.tap("WikiLink", self._transform, stage=_TRANSFORM_STAGE)
        builder.hooks.render.tap("WikiLink", self._embed, stage=_EMBED_STAGE)

    def _transform(self, source: Source, build: Build) -> Source:
        if not source.content or "[[" not in source.content:
            return source
        index = _index(build)
        protected, guarded = _protect(source.content)
        guarded = _WIKILINK_RE.sub(
            lambda m: self._render(m.group(1), source, build, index), guarded
        )
        source.content = _restore(guarded, protected)
        return source

    def _embed(self, source: Source, build: Build) -> None:
        if not source.content:
            return
        # Built on the first non-empty source, before any body is mutated, so the
        # snapshot holds every note's rendered (but not yet embedded) body.
        index = _embed_index(build)
        if "![[" not in source.content:
            return
        rel = source.relpath.as_posix()
        source.content = self._expand(
            source.content, rel, frozenset({rel}), index, build
        )

    def _expand(
        self,
        content: str,
        current: str,
        stack: frozenset[str],
        index: _EmbedIndex,
        build: Build,
    ) -> str:
        protected, guarded = _protect(content)
        guarded = _EMBED_RE.sub(
            lambda m: self._embed_one(m.group(1), current, stack, index, build), guarded
        )
        return _restore(guarded, protected)

    def _embed_one(
        self,
        raw: str,
        current: str,
        stack: frozenset[str],
        index: _EmbedIndex,
        build: Build,
    ) -> str:
        name, heading, _alias = _parse(raw)
        rel = index.names.get(name.casefold()) if name else None
        marker = f"![[{html.escape(raw)}]]"
        if rel is None:
            broken_links(build).append(BrokenLink(current, f"![[{raw}]]"))
            return f'<span class="{self._broken_class}">{marker}</span>'
        if rel in stack:
            # A note (transitively) embedding itself; stop to break the cycle.
            return f'<span class="{self._broken_class}">{marker} (recursive)</span>'

        body = index.bodies[rel]
        if heading:
            section = _extract_section(body, heading)
            if section is None:
                broken_links(build).append(BrokenLink(current, f"![[{raw}]]"))
                return f'<span class="{self._broken_class}">{marker}</span>'
            body = section

        expanded = self._expand(body, rel, stack | {rel}, index, build)
        return f'<div class="{self._embed_class}">{expanded}</div>'

    def _render(
        self, raw: str, source: Source, build: Build, index: dict[str, str]
    ) -> str:
        name, heading, alias = _parse(raw)
        if not name and not heading:
            return f"[[{raw}]]"

        if name:
            url = index.get(name.casefold())
        else:
            # ``[[#Heading]]`` anchors within the current page.
            current = source.meta.get(URL)
            url = current if isinstance(current, str) else None

        text = html.escape(alias or _default_text(name, heading))
        if url is None:
            _record_broken(build, source, raw)
            return f'<span class="{self._broken_class}">{text}</span>'

        href = f"{url}#{slugify(heading)}" if heading else url
        return f'<a class="{self._link_class}" href="{href}">{text}</a>'


def _protect(content: str) -> tuple[list[str], str]:
    """Replace rendered code spans/fences with placeholders, returning both."""

    protected: list[str] = []

    def stash(match: re.Match[str]) -> str:
        protected.append(match.group(0))
        return f"\x00{len(protected) - 1}\x00"

    return protected, _CODE_RE.sub(stash, content)


def _restore(content: str, protected: list[str]) -> str:
    return re.sub(r"\x00(\d+)\x00", lambda m: protected[int(m.group(1))], content)


def _index(build: Build) -> dict[str, str]:
    """Build (once per run) the ``name -> url`` index, cached on ``build.meta``.

    Each page is addressable by its file stem and by its suffix-less path, both
    case-folded. On a stem collision the first source registered wins.
    """

    cached = build.meta.get(_INDEX_KEY)
    if isinstance(cached, dict):
        return cached
    index: dict[str, str] = {}
    for source in build.sources:
        url = source.meta.get(URL)
        if not isinstance(url, str):
            continue
        index.setdefault(source.relpath.stem.casefold(), url)
        index.setdefault(source.relpath.with_suffix("").as_posix().casefold(), url)
    build.meta[_INDEX_KEY] = index
    return index


@dataclass(frozen=True, slots=True)
class _EmbedIndex:
    """A snapshot for embeds: ``name -> relpath`` and ``relpath -> rendered body``."""

    names: dict[str, str]
    bodies: dict[str, str]


def _embed_index(build: Build) -> _EmbedIndex:
    """Snapshot every page's rendered body, keyed for embed resolution.

    Built once per run; the first non-empty source triggers it before any body is
    mutated, so the snapshot holds bodies as rendered but not yet embedded.
    """

    cached = build.meta.get(_EMBED_KEY)
    if isinstance(cached, _EmbedIndex):
        return cached
    names: dict[str, str] = {}
    bodies: dict[str, str] = {}
    for source in build.sources:
        if not isinstance(source.meta.get(URL), str):
            continue
        rel = source.relpath.as_posix()
        bodies[rel] = source.content
        names.setdefault(source.relpath.stem.casefold(), rel)
        names.setdefault(source.relpath.with_suffix("").as_posix().casefold(), rel)
    index = _EmbedIndex(names=names, bodies=bodies)
    build.meta[_EMBED_KEY] = index
    return index


def _extract_section(body: str, heading: str) -> str | None:
    """Return the section under the heading matching ``heading``, or ``None``.

    The match is by slugified heading text, so it does not depend on the renderer
    emitting ``id`` attributes. The section spans from the matched heading to the
    next heading of the same or higher level (or the end of the body).
    """

    target = slugify(heading)
    matches = list(_HEADING_RE.finditer(body))
    for position, match in enumerate(matches):
        text = re.sub(r"<[^>]+>", "", match.group(2))
        if slugify(text) != target:
            continue
        level = int(match.group(1))
        end = len(body)
        for following in matches[position + 1 :]:
            if int(following.group(1)) <= level:
                end = following.start()
                break
        return body[match.start() : end].strip()
    return None


def _parse(raw: str) -> tuple[str, str, str]:
    """Split a wikilink body into ``(name, heading, alias)``.

    ``Note#Heading|alias`` -> ``("Note", "Heading", "alias")``. The alias is the
    text after the first ``|``; the heading is the text after the first ``#`` in
    the part before that ``|``. Empty components come back as ``""``.
    """

    target, sep, alias = raw.partition("|")
    name, _, heading = target.partition("#")
    return name.strip(), heading.strip(), alias.strip() if sep else ""


def _default_text(name: str, heading: str) -> str:
    if name and heading:
        return f"{name} > {heading}"
    return name or heading


def _record_broken(build: Build, source: Source, raw: str) -> None:
    broken_links(build).append(BrokenLink(source.relpath.as_posix(), f"[[{raw}]]"))
