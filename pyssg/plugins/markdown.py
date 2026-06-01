"""Markdown loader + parser plugin.

Loads ``.md`` files (``load_node``) and, in the parse phase, renders the body to
``content_html`` and records the heading tree (the ``toc`` extension's
``toc_tokens``) on ``node.ast`` for the content-meta plugin. Frontmatter splitting
runs in an earlier parse stage (see the frontmatter plugin), so this plugin reads
``__body__`` if present, falling back to the raw text.

Rendering uses `Python-Markdown <https://python-markdown.github.io/>`_ with a
fixed extension set: ``fenced_code`` (so ```` ``` ```` blocks become
``<pre><code class="language-...">``, which the mermaid/highlight plugins rewrite),
``tables`` (GFM-style pipe tables), ``sane_lists`` and ``toc``. The ``toc``
extension assigns heading ``id`` attributes using the project's :func:`slugify`,
so in-page anchors resolve and the same slug is shared with the link resolver's
fragment links.

The parser instance is reused across documents but ``reset()`` is called before
every parse, so no state leaks between documents and two builds are byte-identical.

Third-party (``markdown``) lives only in this peripheral plugin, never in
``pyssg.core``.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import markdown as md_lib
from markdown.extensions.toc import TocExtension

from pyssg.core.node import Document
from pyssg.core.types import NodeKind
from pyssg.plugins.content_meta import slugify

if TYPE_CHECKING:
    from pyssg.core.build import Build
    from pyssg.core.builder import Builder
    from pyssg.core.node import Node

# Parse-stage ordering: frontmatter (100) strips YAML before markdown (200) renders.
_PARSE_STAGE = 200


def _toc_slugify(value: str, separator: str) -> str:
    """Adapter so the ``toc`` extension uses the project's :func:`slugify`.

    Python-Markdown calls ``slugify(value, separator)``; our slugifier always uses
    a hyphen separator, so the second argument is intentionally ignored. Sharing
    one slugifier keeps heading ``id``s consistent with the link resolver's
    fragment slugs.
    """
    return slugify(value)


def _text(value: object) -> str:
    return value if isinstance(value, str) else ""


def _first_heading(toc_tokens: object) -> str | None:
    """Text of the first heading in the document, read from ``toc_tokens``."""
    if isinstance(toc_tokens, list) and toc_tokens:
        first = toc_tokens[0]
        if isinstance(first, dict):
            name = first.get("name")
            if isinstance(name, str) and name:
                return name
    return None


def _derive_title(node: Document, toc_tokens: object) -> str:
    """Title precedence: frontmatter ``title`` -> first heading -> file stem."""
    existing = node.meta.get("title")
    if isinstance(existing, str) and existing:
        return existing
    heading = _first_heading(toc_tokens)
    if heading:
        return heading
    return Path(node.source_path).stem if node.source_path else node.id


class MarkdownPlugin:
    """Parses Markdown documents to HTML via Python-Markdown."""

    name = "markdown"
    # Bumped when the rendering engine changed (markdown-it-py -> Python-Markdown)
    # so the persistent render cache is busted on the next build.
    cache_version = "2.0.0"

    def __init__(self) -> None:
        # One parser instance, configured deterministically; reset() per parse.
        self._md = md_lib.Markdown(
            extensions=[
                "fenced_code",
                "tables",
                "sane_lists",
                TocExtension(slugify=_toc_slugify),
            ],
            output_format="html",
        )

    def apply(self, builder: Builder) -> None:
        @builder.hooks.this_compilation.tap(self.name)
        def _wire(build: Build) -> None:
            @build.hooks.load_node.tap(self.name)
            def _load(path: str) -> Node | None:
                if not path.endswith(".md"):
                    return None
                node = Document(id=path, kind=NodeKind.MARKDOWN, source_path=path)
                node.meta["__raw__"] = Path(path).read_text(encoding="utf-8")
                return node

            @build.hooks.parse.tap(self.name, stage=_PARSE_STAGE)
            def _parse(node: Node) -> None:
                if node.kind is not NodeKind.MARKDOWN or not isinstance(node, Document):
                    return
                body = node.meta.get("__body__")
                text = _text(body) if body is not None else _text(node.meta.get("__raw__"))
                # reset() clears the per-document state (including toc_tokens) so
                # one reused parser stays pure across documents.
                self._md.reset()
                html = self._md.convert(text)
                # ``toc_tokens`` is set dynamically by the toc extension (not in the
                # Markdown stub). Copy it before the next reset reassigns it.
                raw_toc = getattr(self._md, "toc_tokens", [])
                toc_tokens: list[object] = list(raw_toc) if isinstance(raw_toc, list) else []
                node.ast = toc_tokens
                node.meta["content_html"] = html
                # Keep the pre-link-resolution HTML so link_resolver can rewrite
                # from a stable source on every finalize.
                node.meta["__content_html_raw__"] = html
                node.meta["title"] = _derive_title(node, toc_tokens)


def markdown() -> MarkdownPlugin:
    """Factory used in ``pyssg.config.py``."""
    return MarkdownPlugin()
