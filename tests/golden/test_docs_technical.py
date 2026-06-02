"""Build test for the gallery ``docs-technical`` theme (docsy-style).

Mirrors the other gallery-theme tests: the fixture drives the theme through the
``docs`` preset with two ``Config.theme`` overrides, so this covers the docsy-like
three-column structure, the theme configuration API (#53) layering -- including
the runtime ``accent`` color fed into a CSS custom property -- and byte-for-byte
determinism across two builds.
"""

from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "docs_technical"
# The theme lives in the repo-root `themes/` gallery (source-only, not shipped in
# the pyssg wheel), so it is referenced by path rather than via `theme_path`.
THEME = Path(__file__).resolve().parents[2] / "themes" / "docs-technical"


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


class DocsTechnicalThemeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_path = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.dist = _build_into(self.tmp_path)

    def _read(self, rel: str) -> str:
        return (self.dist / rel).read_text(encoding="utf-8")

    def test_page_has_docsy_three_column_structure(self) -> None:
        page = self._read("guide/getting-started/index.html")
        for marker in (
            'class="td-navbar"',
            'class="td-main"',
            'class="td-sidebar"',
            'class="td-content"',
            'class="td-sidebar-toc"',
            'class="td-breadcrumb"',
        ):
            self.assertIn(marker, page)

    def test_sidebar_marks_current_page_active(self) -> None:
        page = self._read("guide/getting-started/index.html")
        self.assertIn('href="/guide/getting-started/" class="active"', page)

    def test_on_this_page_toc_renders(self) -> None:
        page = self._read("guide/getting-started/index.html")
        self.assertIn('class="td-toc"', page)

    def test_tags_index_uses_tag_cloud(self) -> None:
        tags = self._read("tags/index.html")
        self.assertIn('class="td-tag-cloud"', tags)

    def test_theme_option_overrides_propagate(self) -> None:
        # Fixture sets Config.theme = {default_theme: dark, accent: #b5179e}.
        page = self._read("guide/getting-started/index.html")
        self.assertIn('data-theme="dark"', page)
        # The accent option is a real runtime value, fed into --td-accent.
        self.assertIn("--td-accent: #b5179e", page)

    def test_theme_option_defaults_apply(self) -> None:
        # sidebar_title defaults to "Documentation" in layout.toml (not overridden).
        page = self._read("index.html")
        self.assertIn("Documentation", page)

    def test_assets_are_copied(self) -> None:
        self.assertTrue((self.dist / "assets" / "style.css").is_file())
        self.assertTrue((self.dist / "assets" / "js" / "theme.js").is_file())

    def test_build_is_deterministic(self) -> None:
        first = _files_under(_build_into(self.tmp_path / "a"))
        second = _files_under(_build_into(self.tmp_path / "b"))
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
