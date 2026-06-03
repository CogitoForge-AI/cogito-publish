"""Unit tests for the redirects plugin."""

from __future__ import annotations

import unittest

from pyssg.config import Config
from pyssg.core.build import Build
from pyssg.core.builder import Builder
from pyssg.core.node import Document, Page
from pyssg.core.types import NodeKind
from pyssg.plugins.redirects import (
    _PAGE_PREFIX,
    RedirectsPlugin,
    build_redirects,
    render_redirect_html,
)


def _build(base_url: str = "https://example.com") -> Build:
    builder = Builder(config=Config(base_url=base_url))
    return builder.create_build()


def _add_real_page(build: Build, doc_id: str, url: str) -> None:
    build.graph.add_node(Document(id=doc_id, kind=NodeKind.MARKDOWN, meta={"title": doc_id}))
    build.graph.add_node(
        Page(id=f"page:{doc_id}", kind=NodeKind.PAGE, url=url, generated_from=[doc_id])
    )


def _redirect(build: Build, source: str) -> Page:
    page = build.graph.get(f"{_PAGE_PREFIX}{source}")
    assert isinstance(page, Page)
    return page


class RenderRedirectHtmlTest(unittest.TestCase):
    def test_basic_shape(self) -> None:
        html = render_redirect_html(target="/new/", canonical="https://example.com/new/")
        self.assertIn('<meta http-equiv="refresh" content="0; url=/new/">', html)
        self.assertIn('<link rel="canonical" href="https://example.com/new/">', html)
        self.assertIn('<meta name="robots" content="noindex">', html)
        self.assertIn('<a href="/new/">/new/</a>', html)

    def test_escapes_special_characters(self) -> None:
        html = render_redirect_html(
            target="/s/?a=1&b=2", canonical="https://example.com/s/?a=1&b=2"
        )
        # Ampersands are escaped in both the attribute and the text node.
        self.assertIn("url=/s/?a=1&amp;b=2", html)
        self.assertNotIn("&b=2", html.replace("&amp;b=2", ""))


class BuildRedirectsTest(unittest.TestCase):
    def test_emits_template_none_page_per_rule(self) -> None:
        build = _build()
        build_redirects(build, {"/posts/": "/", "/old/": "/new/"})

        for source, target in (("/posts/", "/"), ("/old/", "/new/")):
            page = _redirect(build, source)
            self.assertEqual(page.url, source)
            self.assertIsNone(page.template)
            html = str(page.meta["content_html"])
            self.assertIn(f'content="0; url={target}"', html)

    def test_relative_target_canonical_uses_base_url(self) -> None:
        build = _build(base_url="https://example.com")
        build_redirects(build, {"/old/": "/new/"})

        html = str(_redirect(build, "/old/").meta["content_html"])
        self.assertIn('<link rel="canonical" href="https://example.com/new/">', html)

    def test_external_target_used_verbatim(self) -> None:
        build = _build()
        build_redirects(build, {"/about/": "https://cv.example.com"})

        html = str(_redirect(build, "/about/").meta["content_html"])
        self.assertIn('content="0; url=https://cv.example.com"', html)
        # An external target is canonical as-is, not joined onto base_url.
        self.assertIn('<link rel="canonical" href="https://cv.example.com">', html)

    def test_skips_rule_colliding_with_real_page(self) -> None:
        build = _build()
        _add_real_page(build, "posts", "/posts/")  # a live /posts/ page
        build_redirects(build, {"/posts/": "/", "/old/": "/new/"})

        # The live page wins; only the non-colliding redirect is emitted.
        self.assertIsNone(build.graph.get(f"{_PAGE_PREFIX}/posts/"))
        self.assertIsInstance(build.graph.get(f"{_PAGE_PREFIX}/old/"), Page)

    def test_skips_empty_source_or_target(self) -> None:
        build = _build()
        build_redirects(build, {"": "/new/", "/old/": ""})

        self.assertIsNone(build.graph.get(f"{_PAGE_PREFIX}"))
        self.assertIsNone(build.graph.get(f"{_PAGE_PREFIX}/old/"))

    def test_drops_stale_redirect_on_rebuild(self) -> None:
        build = _build()
        build_redirects(build, {"/a/": "/x/", "/b/": "/y/"})
        self.assertIsInstance(build.graph.get(f"{_PAGE_PREFIX}/b/"), Page)

        # Rebuild with /b/ removed: its page (and so its output) must vanish.
        build_redirects(build, {"/a/": "/x/"})
        self.assertIsInstance(build.graph.get(f"{_PAGE_PREFIX}/a/"), Page)
        self.assertIsNone(build.graph.get(f"{_PAGE_PREFIX}/b/"))

    def test_rebuild_updates_target_in_place(self) -> None:
        build = _build()
        build_redirects(build, {"/a/": "/x/"})
        build_redirects(build, {"/a/": "/z/"})

        html = str(_redirect(build, "/a/").meta["content_html"])
        self.assertIn('content="0; url=/z/"', html)
        self.assertNotIn("url=/x/", html)


class RedirectsCacheVersionTest(unittest.TestCase):
    def test_empty_rules_keep_base_version(self) -> None:
        self.assertEqual(RedirectsPlugin().cache_version, "1.0.0")

    def test_rules_are_folded_into_cache_version(self) -> None:
        a = RedirectsPlugin(rules={"/a/": "/x/"}).cache_version
        b = RedirectsPlugin(rules={"/a/": "/y/"}).cache_version
        self.assertNotEqual(a, "1.0.0")
        self.assertNotEqual(a, b)

    def test_cache_version_is_order_independent(self) -> None:
        a = RedirectsPlugin(rules={"/a/": "/x/", "/b/": "/y/"}).cache_version
        b = RedirectsPlugin(rules={"/b/": "/y/", "/a/": "/x/"}).cache_version
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
