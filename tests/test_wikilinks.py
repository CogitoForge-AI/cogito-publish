"""Unit tests for the WikiLink plugin."""

from __future__ import annotations

import unittest
from pathlib import Path

from pyssg.build import Build
from pyssg.config import Config
from pyssg.content import URL
from pyssg.models import Source
from pyssg_plugins.link_resolver import BROKEN_LINKS, BrokenLink
from pyssg_plugins.wikilinks import WikiLink


def make_build(pages: dict[str, str]) -> Build:
    build = Build(config=Config(src=Path("content"), out=Path("public")))
    for relpath, url in pages.items():
        source = Source(path=Path(relpath), relpath=Path(relpath))
        source.meta[URL] = url
        build.sources.append(source)
    return build


def transform(build: Build, content: str, relpath: str = "a.md") -> str:
    source = Source(path=Path(relpath), relpath=Path(relpath), content=content)
    source.meta[URL] = "/" + relpath.removesuffix(".md") + "/"
    build.sources.append(source)
    return WikiLink()._transform(source, build).content


class ResolveTest(unittest.TestCase):
    def test_stem_match_renders_anchor(self) -> None:
        build = make_build({"notes/Note Title.md": "/notes/note-title/"})
        out = transform(build, "<p>see [[Note Title]] now</p>")
        self.assertIn(
            '<a class="wikilink" href="/notes/note-title/">Note Title</a>', out
        )

    def test_match_is_case_insensitive(self) -> None:
        build = make_build({"Foo.md": "/foo/"})
        out = transform(build, "<p>[[foo]]</p>")
        self.assertIn('href="/foo/"', out)

    def test_path_form_is_resolved(self) -> None:
        build = make_build({"posts/Deep.md": "/posts/deep/"})
        out = transform(build, "<p>[[posts/Deep]]</p>")
        self.assertIn('href="/posts/deep/"', out)
        self.assertIn(">posts/Deep</a>", out)

    def test_surrounding_whitespace_is_trimmed(self) -> None:
        build = make_build({"Foo.md": "/foo/"})
        out = transform(build, "<p>[[  Foo  ]]</p>")
        self.assertIn('href="/foo/"', out)

    def test_first_source_wins_on_stem_collision(self) -> None:
        build = make_build({"a/Dup.md": "/a/dup/", "b/Dup.md": "/b/dup/"})
        out = transform(build, "<p>[[Dup]]</p>")
        self.assertIn('href="/a/dup/"', out)

    def test_multiple_wikilinks_in_one_document(self) -> None:
        build = make_build({"X.md": "/x/", "Y.md": "/y/"})
        out = transform(build, "<p>[[X]] and [[Y]]</p>")
        self.assertIn('href="/x/"', out)
        self.assertIn('href="/y/"', out)

    def test_link_text_is_html_escaped(self) -> None:
        build = make_build({"A&B.md": "/ab/"})
        out = transform(build, "<p>[[A&B]]</p>")
        self.assertIn(">A&amp;B</a>", out)


class AliasAnchorTest(unittest.TestCase):
    def test_alias_overrides_display_text(self) -> None:
        build = make_build({"Note.md": "/note/"})
        out = transform(build, "<p>[[Note|click here]]</p>")
        self.assertIn('<a class="wikilink" href="/note/">click here</a>', out)

    def test_heading_anchor_is_slugified(self) -> None:
        build = make_build({"Note.md": "/note/"})
        out = transform(build, "<p>[[Note#My Heading]]</p>")
        self.assertIn('href="/note/#my-heading"', out)
        self.assertIn(">Note &gt; My Heading</a>", out)

    def test_heading_and_alias_combined(self) -> None:
        build = make_build({"Note.md": "/note/"})
        out = transform(build, "<p>[[Note#Sec|see section]]</p>")
        self.assertIn('href="/note/#sec"', out)
        self.assertIn(">see section</a>", out)

    def test_same_page_heading_anchor(self) -> None:
        build = make_build({})
        out = transform(build, "<p>[[#Local Section]]</p>", relpath="page.md")
        self.assertIn('href="/page/#local-section"', out)
        self.assertIn(">Local Section</a>", out)

    def test_empty_alias_falls_back_to_default_text(self) -> None:
        build = make_build({"Note.md": "/note/"})
        out = transform(build, "<p>[[Note|]]</p>")
        self.assertIn(">Note</a>", out)

    def test_first_pipe_splits_alias(self) -> None:
        build = make_build({"Note.md": "/note/"})
        out = transform(build, "<p>[[Note|a|b]]</p>")
        self.assertIn(">a|b</a>", out)

    def test_empty_target_is_left_literal(self) -> None:
        build = make_build({})
        out = transform(build, "<p>[[ ]]</p>")
        self.assertIn("[[ ]]", out)
        self.assertNotIn("<a", out)


class BrokenTest(unittest.TestCase):
    def test_unresolved_renders_broken_span(self) -> None:
        build = make_build({})
        out = transform(build, "<p>[[Ghost]]</p>")
        self.assertIn('<span class="wikilink-broken">Ghost</span>', out)

    def test_unresolved_is_recorded(self) -> None:
        build = make_build({})
        transform(build, "<p>[[Ghost]]</p>", relpath="notes/a.md")
        recorded = build.meta.get(BROKEN_LINKS)
        assert isinstance(recorded, list)
        self.assertEqual(recorded, [BrokenLink("notes/a.md", "[[Ghost]]")])

    def test_unresolved_records_raw_with_anchor_and_alias(self) -> None:
        build = make_build({})
        transform(build, "<p>[[Ghost#X|t]]</p>", relpath="a.md")
        recorded = build.meta.get(BROKEN_LINKS)
        assert isinstance(recorded, list)
        self.assertEqual(recorded[0], BrokenLink("a.md", "[[Ghost#X|t]]"))


class CodeProtectionTest(unittest.TestCase):
    def test_fenced_block_is_untouched(self) -> None:
        build = make_build({"Note.md": "/note/"})
        original = "<pre><code>[[Note]]\n</code></pre>"
        self.assertEqual(transform(build, original), original)

    def test_inline_code_is_untouched(self) -> None:
        build = make_build({"Note.md": "/note/"})
        original = "<p>literal <code>[[Note]]</code> here</p>"
        self.assertEqual(transform(build, original), original)

    def test_link_outside_code_still_resolved(self) -> None:
        build = make_build({"Note.md": "/note/"})
        out = transform(build, "<p>[[Note]] <code>[[Note]]</code></p>")
        self.assertIn('href="/note/"', out)
        self.assertIn("<code>[[Note]]</code>", out)


class IgnoreTest(unittest.TestCase):
    def test_embed_syntax_is_left_untouched(self) -> None:
        # ![[note]] is an embed (issue #21), not a link.
        build = make_build({"Note.md": "/note/"})
        out = transform(build, "<p>![[Note]]</p>")
        self.assertIn("![[Note]]", out)
        self.assertNotIn("<a", out)

    def test_content_without_wikilinks_is_unchanged(self) -> None:
        build = make_build({"Note.md": "/note/"})
        original = "<p>plain text, no links</p>"
        self.assertEqual(transform(build, original), original)

    def test_empty_content_is_noop(self) -> None:
        build = make_build({})
        source = Source(path=Path("a.md"), relpath=Path("a.md"), content="")
        self.assertEqual(WikiLink()._transform(source, build).content, "")

    def test_custom_classes(self) -> None:
        build = make_build({"Note.md": "/note/"})
        source = Source(
            path=Path("a.md"), relpath=Path("a.md"), content="<p>[[Note]] [[X]]</p>"
        )
        source.meta[URL] = "/a/"
        build.sources.append(source)
        out = (
            WikiLink(link_class="wl", broken_class="wl-x")
            ._transform(source, build)
            .content
        )
        self.assertIn('<a class="wl" href="/note/">Note</a>', out)
        self.assertIn('<span class="wl-x">X</span>', out)


class IndexTest(unittest.TestCase):
    def test_index_is_cached_and_reused_across_sources(self) -> None:
        build = make_build({"Note.md": "/note/"})
        transform(build, "<p>[[Note]]</p>", relpath="a.md")
        self.assertIn("_wikilink_index", build.meta)
        # A second source reuses the cached index (the cache-hit path).
        out = transform(build, "<p>[[Note]] again</p>", relpath="b.md")
        self.assertIn('href="/note/"', out)

    def test_source_without_url_is_skipped(self) -> None:
        build = make_build({"Note.md": "/note/"})
        # A URL-less source (e.g. not yet assigned) must not enter the index.
        build.sources.append(Source(path=Path("draft.md"), relpath=Path("draft.md")))
        out = transform(build, "<p>[[Note]] and [[draft]]</p>")
        self.assertIn('href="/note/"', out)
        self.assertIn('<span class="wikilink-broken">draft</span>', out)


def build_with_content(pages: dict[str, str]) -> Build:
    """A build whose sources carry rendered content (for embed tests)."""

    build = Build(config=Config(src=Path("content"), out=Path("public")))
    for relpath, content in pages.items():
        source = Source(path=Path(relpath), relpath=Path(relpath), content=content)
        source.meta[URL] = "/" + relpath.removesuffix(".md") + "/"
        build.sources.append(source)
    return build


def embed(build: Build, relpath: str) -> str:
    source = next(s for s in build.sources if s.relpath == Path(relpath))
    WikiLink()._embed(source, build)
    return source.content


class EmbedTest(unittest.TestCase):
    def test_full_body_is_inlined(self) -> None:
        build = build_with_content(
            {"Note.md": "<p>note body</p>", "page.md": "<p>x ![[Note]]</p>"}
        )
        out = embed(build, "page.md")
        self.assertIn('<div class="wikilink-embed"><p>note body</p></div>', out)

    def test_section_embed_extracts_one_section(self) -> None:
        note = "<h2>Intro</h2>\n<p>a</p>\n<h2>Details</h2>\n<p>b</p>"
        build = build_with_content({"Note.md": note, "page.md": "![[Note#Details]]"})
        out = embed(build, "page.md")
        self.assertIn("<h2>Details</h2>", out)
        self.assertIn("<p>b</p>", out)
        self.assertNotIn("Intro", out)

    def test_section_stops_at_same_level_heading(self) -> None:
        note = "<h2>Intro</h2>\n<p>a</p>\n<h2>Details</h2>\n<p>b</p>"
        build = build_with_content({"Note.md": note, "page.md": "![[Note#Intro]]"})
        out = embed(build, "page.md")
        self.assertIn("<p>a</p>", out)
        self.assertNotIn("Details", out)

    def test_section_includes_deeper_subheadings(self) -> None:
        note = "<h2>Intro</h2>\n<h3>Sub</h3>\n<p>x</p>\n<h2>Next</h2>\n<p>y</p>"
        build = build_with_content({"Note.md": note, "page.md": "![[Note#Intro]]"})
        out = embed(build, "page.md")
        self.assertIn("<h3>Sub</h3>", out)
        self.assertIn("<p>x</p>", out)
        self.assertNotIn("Next", out)

    def test_missing_section_is_broken(self) -> None:
        build = build_with_content(
            {"Note.md": "<h2>Intro</h2>", "page.md": "![[Note#Nope]]"}
        )
        out = embed(build, "page.md")
        self.assertIn('<span class="wikilink-broken">![[Note#Nope]]</span>', out)
        recorded = build.meta.get(BROKEN_LINKS)
        assert isinstance(recorded, list)
        self.assertEqual(recorded[0], BrokenLink("page.md", "![[Note#Nope]]"))

    def test_unknown_target_is_broken_and_recorded(self) -> None:
        build = build_with_content({"page.md": "![[Ghost]]"})
        out = embed(build, "page.md")
        self.assertIn('<span class="wikilink-broken">![[Ghost]]</span>', out)
        recorded = build.meta.get(BROKEN_LINKS)
        assert isinstance(recorded, list)
        self.assertEqual(recorded[0], BrokenLink("page.md", "![[Ghost]]"))

    def test_nested_embed_is_expanded(self) -> None:
        build = build_with_content(
            {
                "Inner.md": "<p>inner</p>",
                "Outer.md": "<p>outer ![[Inner]]</p>",
                "page.md": "![[Outer]]",
            }
        )
        out = embed(build, "page.md")
        self.assertIn("inner", out)
        self.assertIn("outer", out)

    def test_recursive_cycle_is_broken(self) -> None:
        build = build_with_content(
            {"A.md": "<p>a ![[B]]</p>", "B.md": "<p>b ![[A]]</p>"}
        )
        out = embed(build, "A.md")
        self.assertIn("(recursive)", out)
        self.assertIn(">a ", out)
        self.assertIn("b ", out)

    def test_self_embed_is_broken(self) -> None:
        build = build_with_content({"A.md": "<p>a ![[A]]</p>"})
        out = embed(build, "A.md")
        self.assertIn("(recursive)", out)

    def test_embed_inside_code_is_untouched(self) -> None:
        build = build_with_content(
            {"Note.md": "<p>n</p>", "page.md": "<pre><code>![[Note]]</code></pre>"}
        )
        out = embed(build, "page.md")
        self.assertEqual(out, "<pre><code>![[Note]]</code></pre>")

    def test_no_embeds_is_unchanged(self) -> None:
        build = build_with_content({"page.md": "<p>plain</p>"})
        self.assertEqual(embed(build, "page.md"), "<p>plain</p>")

    def test_empty_content_is_noop(self) -> None:
        build = Build(config=Config(src=Path("c"), out=Path("o")))
        source = Source(path=Path("a.md"), relpath=Path("a.md"), content="")
        WikiLink()._embed(source, build)
        self.assertEqual(source.content, "")

    def test_embed_index_skips_url_less_sources(self) -> None:
        build = build_with_content({"page.md": "![[Note]]"})
        build.sources.insert(
            0, Source(path=Path("draft.md"), relpath=Path("draft.md"), content="d")
        )
        out = embed(build, "page.md")
        # No "Note" page exists, so the embed is broken (the URL-less draft is
        # not indexed and cannot satisfy it either).
        self.assertIn('<span class="wikilink-broken">![[Note]]</span>', out)

    def test_embed_index_is_cached_across_sources(self) -> None:
        build = build_with_content(
            {"Note.md": "<p>n</p>", "p1.md": "![[Note]]", "p2.md": "![[Note]]"}
        )
        embed(build, "p1.md")
        self.assertIn("_wikilink_embed_index", build.meta)
        # A second source reuses the cached snapshot (the cache-hit path).
        out = embed(build, "p2.md")
        self.assertIn('<div class="wikilink-embed"><p>n</p></div>', out)

    def test_custom_embed_class(self) -> None:
        build = build_with_content({"Note.md": "<p>n</p>", "page.md": "![[Note]]"})
        source = next(s for s in build.sources if s.relpath == Path("page.md"))
        WikiLink(embed_class="emb")._embed(source, build)
        self.assertIn('<div class="emb"><p>n</p></div>', source.content)


class HookTest(unittest.TestCase):
    def test_apply_taps_transform(self) -> None:
        from pyssg.builder import Builder

        builder = Builder(Config(src=Path("c"), out=Path("o"), plugins=[WikiLink()]))
        build = make_build({"Note.md": "/note/"})
        source = Source(
            path=Path("a.md"), relpath=Path("a.md"), content="<p>[[Note]]</p>"
        )
        source.meta[URL] = "/a/"
        build.sources.append(source)
        result = builder.hooks.transform.call(source, build)
        self.assertIn('href="/note/"', result.content)

    def test_apply_taps_render_for_embeds(self) -> None:
        from pyssg.builder import Builder

        builder = Builder(Config(src=Path("c"), out=Path("o"), plugins=[WikiLink()]))
        build = build_with_content({"Note.md": "<p>n</p>", "page.md": "![[Note]]"})
        source = next(s for s in build.sources if s.relpath == Path("page.md"))
        builder.hooks.render.call(source, build)
        self.assertIn('<div class="wikilink-embed"><p>n</p></div>', source.content)


if __name__ == "__main__":
    unittest.main()
