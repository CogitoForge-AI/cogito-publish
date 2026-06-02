"""Build test for the gallery ``blog-minimal`` theme (ported from hugo-coder).

Mirrors the ``blog-technical`` test: the fixture drives the theme through the
``blog`` preset with two ``Config.theme`` overrides, so this covers the coder
page structure, the theme configuration API (#53) layering, and byte-for-byte
determinism across two builds. Assertion-based rather than a byte snapshot --
the theme's compiled stylesheet is already version-controlled in the theme
directory, so a golden tree would only add brittle duplication.
"""

from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "blog_minimal"
# The theme lives in the repo-root `themes/` gallery (source-only, not shipped in
# the pyssg wheel), so it is referenced by path rather than via `theme_path`.
THEME = Path(__file__).resolve().parents[2] / "themes" / "blog-minimal"


def _files_under(root: Path) -> dict[str, str]:
    return {
        p.relative_to(root).as_posix(): p.read_text(encoding="utf-8")
        for p in sorted(root.rglob("*"))
        if p.is_file()
    }


def _build_into(tmp_path: Path) -> Path:
    from pyssg.cli import build_site

    site = tmp_path / "site"
    shutil.copytree(FIXTURE, site)
    # Vendor the gallery theme into the site under `theme/`, matching the
    # relative `layout="theme"` the fixture config points at.
    shutil.copytree(THEME, site / "theme")
    build_site(site)
    return site / "dist"


class BlogMinimalThemeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_path = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.dist = _build_into(self.tmp_path)

    def _read(self, rel: str) -> str:
        return (self.dist / rel).read_text(encoding="utf-8")

    def test_post_page_has_coder_structure(self) -> None:
        post = self._read("posts/first-post/index.html")
        for marker in (
            'class="navigation"',
            'class="container post"',
            'class="post-title"',
            'class="post-meta"',
            'class="post-content"',
        ):
            self.assertIn(marker, post)

    def test_list_page_lists_posts_and_paginates(self) -> None:
        index = self._read("index.html")
        self.assertIn('class="container list"', index)
        self.assertIn('<a class="title"', index)
        # posts_per_page=2 over three posts paginates, so a second page exists.
        self.assertIn('class="pagination"', index)
        self.assertTrue((self.dist / "page" / "2" / "index.html").is_file())

    def test_tags_index_uses_taxonomy_markup(self) -> None:
        tags = self._read("tags/index.html")
        self.assertIn('class="container taxonomy"', tags)
        self.assertIn('class="taxonomy-element"', tags)

    def test_theme_option_overrides_propagate(self) -> None:
        # Fixture sets Config.theme = {default_theme: dark, show_toc: True}.
        post = self._read("posts/first-post/index.html")
        self.assertIn("colorscheme-dark", post)
        self.assertIn('class="toc"', post)

    def test_theme_option_defaults_apply(self) -> None:
        # show_reading_time defaults to true in layout.toml and is not overridden.
        post = self._read("posts/first-post/index.html")
        self.assertIn("min read", post)

    def test_assets_are_copied(self) -> None:
        self.assertTrue((self.dist / "assets" / "style.css").is_file())
        self.assertTrue((self.dist / "assets" / "js" / "theme.js").is_file())

    def test_build_is_deterministic(self) -> None:
        first = _files_under(_build_into(self.tmp_path / "a"))
        second = _files_under(_build_into(self.tmp_path / "b"))
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
