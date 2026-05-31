"""WikiLink plugin: resolve Obsidian-style ``[[wikilinks]]`` to page URLs.

Taps ``transform`` at a stage after Markdown (stage 0), post-processing the
rendered HTML. python-markdown leaves ``[[Note]]`` untouched as literal text, so
the same HTML-pass strategy the LinkResolver uses applies: ``[[...]]`` inside a
code span or fence stays inside ``<code>``/``<pre>`` and is skipped, so authored
examples are never rewritten.

A ``[[Note Title]]`` target is resolved against a name index built from
``build.sources``: a page is addressable by its file stem (``Note Title.md`` ->
``[[Note Title]]``) or by a path without the suffix (``[[folder/Note]]``), both
matched case-insensitively. The link text is the note title as written.

Unresolved targets render as a clearly-marked broken ``<span>`` and are recorded
in ``build.meta["broken_links"]`` so the BrokenLinks plugin can report them.

Aliases/anchors (``[[note|alias]]``, ``[[note#heading]]``) and embeds
(``![[note]]``) are tracked separately (issues #20, #21); embeds are explicitly
left untouched here. The plugin uses the standard library only.
"""

from __future__ import annotations

import html
import re

from pyssg.build import Build
from pyssg.builder import Builder
from pyssg.content import URL
from pyssg.models import Source
from pyssg_plugins.link_resolver import BrokenLink, broken_links

# Run after Markdown's transform (stage 0); the literal ``[[...]]`` text exists by
# then. Resolved links carry final URLs, so the LinkResolver (stage 50) ignores
# them.
_TRANSFORM_STAGE = 40

# Protect rendered code so ``[[...]]`` inside it is never rewritten. ``<pre>``
# (fenced blocks) is matched before ``<code>`` (inline code).
_CODE_RE = re.compile(r"<pre\b.*?</pre>|<code\b.*?</code>", re.DOTALL | re.IGNORECASE)

# A wikilink: ``[[target]]`` not preceded by ``!`` (which marks an embed, #21).
# The target is any run of non-bracket characters, surrounding space trimmed.
_WIKILINK_RE = re.compile(r"(?<!!)\[\[\s*([^\[\]]+?)\s*\]\]")

_INDEX_KEY = "_wikilink_index"


class WikiLink:
    def __init__(
        self, *, link_class: str = "wikilink", broken_class: str = "wikilink-broken"
    ) -> None:
        self._link_class = link_class
        self._broken_class = broken_class

    def apply(self, builder: Builder) -> None:
        builder.hooks.transform.tap("WikiLink", self._transform, stage=_TRANSFORM_STAGE)

    def _transform(self, source: Source, build: Build) -> Source:
        if not source.content or "[[" not in source.content:
            return source
        index = _index(build)

        protected: list[str] = []

        def stash(match: re.Match[str]) -> str:
            protected.append(match.group(0))
            return f"\x00{len(protected) - 1}\x00"

        guarded = _CODE_RE.sub(stash, source.content)
        guarded = _WIKILINK_RE.sub(
            lambda m: self._render(m.group(1), source, build, index), guarded
        )
        source.content = re.sub(
            r"\x00(\d+)\x00", lambda m: protected[int(m.group(1))], guarded
        )
        return source

    def _render(
        self, name: str, source: Source, build: Build, index: dict[str, str]
    ) -> str:
        url = index.get(name.casefold())
        text = html.escape(name)
        if url is None:
            _record_broken(build, source, name)
            return f'<span class="{self._broken_class}">{text}</span>'
        return f'<a class="{self._link_class}" href="{url}">{text}</a>'


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


def _record_broken(build: Build, source: Source, name: str) -> None:
    broken_links(build).append(BrokenLink(source.relpath.as_posix(), f"[[{name}]]"))
