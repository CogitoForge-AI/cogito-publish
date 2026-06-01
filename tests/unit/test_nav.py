"""Unit tests for the ``nav`` plugin's locale-aware navigation building."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from pyssg.config import Config
from pyssg.core.build import Build
from pyssg.core.builder import Builder
from pyssg.core.node import Document, Page
from pyssg.core.types import NodeKind
from pyssg.plugins.nav import build_navigation, nav


def _build(tmp_path: Path) -> Build:
    builder = Builder(config=Config(output_dir="dist"), site_dir=tmp_path)
    return builder.create_build()


def _add_page(
    build: Build,
    *,
    doc_id: str,
    url: str,
    title: str,
    lang: str | None = None,
    order: int | None = None,
) -> None:
    doc = Document(id=doc_id, kind=NodeKind.MARKDOWN, source_path=doc_id)
    doc.meta["title"] = title
    if lang is not None:
        doc.meta["lang"] = lang
    if order is not None:
        doc.meta["order"] = order
    page = Page(id=f"page:{doc_id}", kind=NodeKind.PAGE, url=url, generated_from=[doc.id])
    build.graph.add_node(doc)
    build.graph.add_node(page)


def _dicts(value: object) -> list[dict[str, object]]:
    """Narrow a ``site_data`` list of dicts for type-checked indexing in tests."""
    assert isinstance(value, list)
    return [item for item in value if isinstance(item, dict)]


def _menu(build: Build) -> list[dict[str, object]]:
    return _dicts(build.site_data["menu"])


def _ordered(build: Build) -> list[dict[str, object]]:
    return _dicts(build.site_data["ordered_pages"])


class NavNoI18nTest(unittest.TestCase):
    """Without i18n every entry has locale "" and grouping is plain by section."""

    def setUp(self) -> None:
        self.tmp = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.build = _build(self.tmp)

    def test_sections_grouped_alphabetically_with_empty_locale(self) -> None:
        _add_page(self.build, doc_id="guide/a.md", url="/guide/a/", title="A", order=1)
        _add_page(self.build, doc_id="guide/b.md", url="/guide/b/", title="B", order=2)
        _add_page(self.build, doc_id="about.md", url="/about/", title="About")
        build_navigation(self.build)
        menu = _menu(self.build)
        self.assertEqual([s["section"] for s in menu], ["about", "guide"])
        self.assertTrue(all(s["locale"] == "" for s in menu))
        guide = next(s for s in menu if s["section"] == "guide")
        self.assertEqual([i["title"] for i in _dicts(guide["items"])], ["A", "B"])

    def test_ordered_pages_carry_locale_key(self) -> None:
        _add_page(self.build, doc_id="x.md", url="/x/", title="X", order=1)
        build_navigation(self.build)
        self.assertEqual(_ordered(self.build)[0]["locale"], "")


class NavI18nTest(unittest.TestCase):
    """With i18n, sections group per locale and the locale prefix is stripped."""

    def setUp(self) -> None:
        self.tmp = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.build = _build(self.tmp)
        # Default locale (en) served at root; vi served under /vi/.
        _add_page(
            self.build, doc_id="en/guide/intro.md", url="/guide/intro/", title="Intro", lang="en"
        )
        _add_page(
            self.build, doc_id="en/guide/next.md", url="/guide/next/", title="Next", lang="en"
        )
        _add_page(
            self.build,
            doc_id="vi/guide/intro.md",
            url="/vi/guide/intro/",
            title="Gioi thieu",
            lang="vi",
        )
        build_navigation(self.build)

    def test_vi_page_groups_under_real_section_not_locale(self) -> None:
        # The /vi/ prefix is stripped, so the section is "guide", not "vi".
        vi = [(s["locale"], s["section"]) for s in _menu(self.build) if s["locale"] == "vi"]
        self.assertEqual(vi, [("vi", "guide")])

    def test_each_locale_has_its_own_section(self) -> None:
        menu = _menu(self.build)
        keys = [(s["locale"], s["section"]) for s in menu]
        self.assertIn(("en", "guide"), keys)
        self.assertIn(("vi", "guide"), keys)
        en_guide = next(s for s in menu if s["locale"] == "en" and s["section"] == "guide")
        self.assertEqual([i["title"] for i in _dicts(en_guide["items"])], ["Intro", "Next"])
        vi_guide = next(s for s in menu if s["locale"] == "vi" and s["section"] == "guide")
        self.assertEqual([i["url"] for i in _dicts(vi_guide["items"])], ["/vi/guide/intro/"])

    def test_ordered_pages_keep_locales_contiguous(self) -> None:
        locales = [str(item["locale"]) for item in _ordered(self.build)]
        # All en entries come before all vi entries (sorted by locale): no interleave.
        self.assertEqual(locales, sorted(locales))
        en_urls = [i["url"] for i in _ordered(self.build) if i["locale"] == "en"]
        self.assertEqual(en_urls, ["/guide/intro/", "/guide/next/"])


class NavPluginTest(unittest.TestCase):
    def test_factory_and_name(self) -> None:
        self.assertEqual(nav().name, "nav")
