"""Unit tests for the I18n plugin and the locale-aware plugin generalizations."""

from __future__ import annotations

import unittest
from pathlib import Path

from pyssg.build import Build
from pyssg.config import Config
from pyssg.content import (
    I18N,
    LOCALE,
    LOCALE_PREFIX,
    TRANSLATION_KEY,
    TRANSLATIONS,
    collections,
    is_generated,
    menus,
)
from pyssg.models import Source
from pyssg_plugins.collections import Collections
from pyssg_plugins.i18n import I18n
from pyssg_plugins.listing import Listing
from pyssg_plugins.navigation import Navigation
from pyssg_plugins.permalink import Permalink


def src(rel: str, **frontmatter: object) -> Source:
    return Source(path=Path(rel), relpath=Path(rel), frontmatter=dict(frontmatter))


def build_with(sources: list[Source]) -> Build:
    build = Build(config=Config(src=Path("content"), out=Path("public")))
    build.sources = sources
    return build


class ConstructorTest(unittest.TestCase):
    def test_requires_locales(self) -> None:
        with self.assertRaises(ValueError):
            I18n(locales=[], default_locale="vi")

    def test_default_must_be_a_locale(self) -> None:
        with self.assertRaises(ValueError):
            I18n(locales=["vi", "en"], default_locale="fr")

    def test_apply_taps_collect_twice(self) -> None:
        from pyssg.builder import Builder

        builder = Builder(
            Config(
                src=Path("content"),
                out=Path("public"),
                plugins=[I18n(locales=["vi"], default_locale="vi")],
            )
        )
        self.assertTrue(builder.hooks.collect.has_taps)


class TagStageTest(unittest.TestCase):
    def setUp(self) -> None:
        self.plugin = I18n(locales=["vi", "en"], default_locale="vi")

    def test_locale_from_first_folder(self) -> None:
        build = build_with([src("en/posts/oauth2.md")])
        self.plugin._tag(build)
        source = build.sources[0]
        self.assertEqual(source.meta[LOCALE], "en")
        self.assertEqual(source.meta[TRANSLATION_KEY], "posts/oauth2")

    def test_non_default_locale_keeps_prefix(self) -> None:
        build = build_with([src("en/posts/oauth2.md")])
        self.plugin._tag(build)
        self.assertEqual(build.sources[0].meta[LOCALE_PREFIX], "en")

    def test_default_locale_renders_at_root(self) -> None:
        build = build_with([src("vi/posts/oauth2.md")])
        self.plugin._tag(build)
        self.assertEqual(build.sources[0].meta[LOCALE_PREFIX], "")

    def test_unknown_folder_falls_back_to_default(self) -> None:
        build = build_with([src("index.md")])
        self.plugin._tag(build)
        source = build.sources[0]
        self.assertEqual(source.meta[LOCALE], "vi")
        self.assertEqual(source.meta[LOCALE_PREFIX], "")
        self.assertEqual(source.meta[TRANSLATION_KEY], "index")

    def test_translation_key_override(self) -> None:
        build = build_with([src("vi/posts/a.md", translation_key="shared/a")])
        self.plugin._tag(build)
        self.assertEqual(build.sources[0].meta[TRANSLATION_KEY], "shared/a")


class IndexStageTest(unittest.TestCase):
    def setUp(self) -> None:
        self.plugin = I18n(locales=["vi", "en"], default_locale="vi")

    def _run(self, sources: list[Source]) -> Build:
        build = build_with(sources)
        self.plugin._tag(build)
        Permalink()._collect(build)
        self.plugin._index(build)
        return build

    def test_builds_translation_index(self) -> None:
        build = self._run([src("vi/posts/oauth2.md"), src("en/posts/oauth2.md")])
        index = build.meta[I18N]
        assert isinstance(index, dict)
        self.assertEqual(
            index["translations"]["posts/oauth2"],
            {"vi": "/posts/oauth2/", "en": "/en/posts/oauth2/"},
        )

    def test_per_source_translations_ordered_with_current_flag(self) -> None:
        build = self._run([src("en/posts/oauth2.md"), src("vi/posts/oauth2.md")])
        en = next(s for s in build.sources if s.meta[LOCALE] == "en")
        self.assertEqual(
            en.meta[TRANSLATIONS],
            [
                {"locale": "vi", "url": "/posts/oauth2/", "current": False},
                {"locale": "en", "url": "/en/posts/oauth2/", "current": True},
            ],
        )

    def test_unpaired_page_lists_only_itself(self) -> None:
        build = self._run([src("vi/posts/only.md")])
        source = build.sources[0]
        self.assertEqual(
            source.meta[TRANSLATIONS],
            [{"locale": "vi", "url": "/posts/only/", "current": True}],
        )

    def test_drafts_excluded_from_index(self) -> None:
        build = self._run([src("vi/posts/a.md"), src("en/posts/a.md", draft=True)])
        index = build.meta[I18N]
        assert isinstance(index, dict)
        self.assertEqual(index["translations"]["posts/a"], {"vi": "/posts/a/"})

    def test_sources_without_locale_are_skipped(self) -> None:
        # A page that never went through _tag (no locale/key) must not crash the
        # index pass and stays out of the translation map.
        build = build_with([src("assets/logo.md")])
        Permalink()._collect(build)
        self.plugin._index(build)
        index = build.meta[I18N]
        assert isinstance(index, dict)
        self.assertEqual(index["translations"], {})

    def test_seeds_site_locales(self) -> None:
        build = self._run([src("vi/posts/a.md")])
        site = build.meta["site"]
        assert isinstance(site, dict)
        self.assertEqual(site["locales"], ["vi", "en"])
        self.assertEqual(site["default_locale"], "vi")


class CollectionsGroupByTest(unittest.TestCase):
    def test_same_tag_splits_per_locale(self) -> None:
        build = build_with(
            [
                src("vi/posts/a.md", tags=["python"]),
                src("en/posts/a.md", tags=["python"]),
            ]
        )
        I18n(locales=["vi", "en"], default_locale="vi")._tag(build)
        Collections(by_tag=True, group_by="locale")._collect(build)
        reg = collections(build)
        self.assertIn("vi/python", reg)
        self.assertIn("en/python", reg)
        self.assertEqual(reg["vi/python"].name, "python")
        self.assertEqual(reg["vi/python"].meta["locale"], "vi")

    def test_folder_collection_stamps_locale(self) -> None:
        build = build_with([src("vi/posts/a.md")])
        I18n(locales=["vi", "en"], default_locale="vi")._tag(build)
        Collections(by_tag=False, by_folder=True, group_by="locale")._collect(build)
        self.assertEqual(collections(build)["vi/posts"].meta["locale"], "vi")


class ListingLocaleTokenTest(unittest.TestCase):
    def _tag_pages(self) -> Build:
        build = build_with(
            [
                src("vi/posts/a.md", tags=["python"]),
                src("en/posts/a.md", tags=["python"]),
            ]
        )
        I18n(locales=["vi", "en"], default_locale="vi")._tag(build)
        Permalink()._collect(build)
        Collections(by_tag=True, group_by="locale")._collect(build)
        return build

    def test_locale_token_in_url_and_translation_key(self) -> None:
        build = self._tag_pages()
        Listing(kind="tag", base_url="/:locale/tags/:name/", title=":name")._collect(
            build
        )
        generated = {s.meta["url"]: s for s in build.sources if is_generated(s)}
        # vi is the default locale, so its tag page renders at the root.
        self.assertIn("/tags/python/", generated)
        self.assertIn("/en/tags/python/", generated)
        vi_page = generated["/tags/python/"]
        self.assertEqual(vi_page.meta[LOCALE], "vi")
        # The locale-independent key is what pairs the two listings.
        self.assertEqual(vi_page.meta[TRANSLATION_KEY], "/tags/python/")
        self.assertEqual(
            generated["/en/tags/python/"].meta[TRANSLATION_KEY], "/tags/python/"
        )

    def test_listing_pages_are_paired_by_index(self) -> None:
        build = self._tag_pages()
        Listing(kind="tag", base_url="/:locale/tags/:name/")._collect(build)
        I18n(locales=["vi", "en"], default_locale="vi")._index(build)
        index = build.meta[I18N]
        assert isinstance(index, dict)
        self.assertEqual(
            index["translations"]["/tags/python/"],
            {"vi": "/tags/python/", "en": "/en/tags/python/"},
        )

    def test_per_locale_index_listings_are_paired(self) -> None:
        # The default locale's index ("/") and another locale's ("/en/") use
        # literal base URLs, yet must share a translation_key so the home page
        # gets a language switcher.
        build = build_with([src("vi/posts/a.md"), src("en/posts/a.md")])
        I18n(locales=["vi", "en"], default_locale="vi")._tag(build)
        Permalink()._collect(build)
        Collections(by_folder=True, by_tag=False, group_by="locale")._collect(build)
        Listing(collection="vi/posts", base_url="/", title="vi")._collect(build)
        Listing(collection="en/posts", base_url="/en/", title="en")._collect(build)
        I18n(locales=["vi", "en"], default_locale="vi")._index(build)
        index = build.meta[I18N]
        assert isinstance(index, dict)
        self.assertEqual(index["translations"]["/"], {"vi": "/", "en": "/en/"})

    def test_locale_token_dropped_without_locale(self) -> None:
        build = build_with([src("posts/a.md", tags=["python"])])
        Permalink()._collect(build)
        Collections(by_tag=True)._collect(build)
        Listing(kind="tag", base_url="/:locale/tags/:name/")._collect(build)
        urls = {s.meta["url"] for s in build.sources if is_generated(s)}
        self.assertEqual(urls, {"/tags/python/"})


class NavigationGroupByTest(unittest.TestCase):
    def test_one_menu_per_locale(self) -> None:
        build = build_with(
            [
                src("vi/about.md", menu="main"),
                src("en/about.md", menu="main"),
            ]
        )
        I18n(locales=["vi", "en"], default_locale="vi")._tag(build)
        Permalink()._collect(build)
        Navigation(mode="frontmatter", group_by="locale")._collect(build)
        registry = menus(build)
        self.assertIn("main:vi", registry)
        self.assertIn("main:en", registry)
        self.assertEqual(registry["main:vi"][0].url, "/about/")
        self.assertEqual(registry["main:en"][0].url, "/en/about/")


if __name__ == "__main__":
    unittest.main()
