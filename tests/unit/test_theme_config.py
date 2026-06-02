"""Theme configuration API: option defaults overlaid by ``Config.theme``.

A theme declares its option defaults in ``layout.toml`` ``[options]``; the site
overrides individual keys via ``Config.theme``. The engine resolves the two into
a single ``theme`` mapping exposed to templates (``layout defaults <- site``).
These tests drive a real themed build and read the merged values back out of the
rendered HTML, covering the whole resolution path end to end.
"""

from __future__ import annotations

import tempfile
import unittest
import warnings
from pathlib import Path

# A throwaway layout whose template simply echoes the resolved theme options, so
# the rendered bytes reveal exactly what reached the template namespace. ``extra``
# is read with a fallback because the layout intentionally does not declare it
# (used to exercise the undeclared-key path).
_TEMPLATE = (
    "<!doctype html><html><body>"
    "accent={{ theme.accent }};show_toc={{ theme.show_toc }};"
    "extra={{ theme.get('extra', 'none') }}"
    "{{ content_html }}</body></html>"
)


def _write_layout(root: Path) -> None:
    (root / "templates").mkdir(parents=True)
    (root / "layout.toml").write_text(
        'name = "probe"\n'
        'default_template = "page.html.j2"\n'
        "[options]\n"
        'accent = "#000000"\n'
        "show_toc = true\n",
        encoding="utf-8",
    )
    (root / "templates" / "page.html.j2").write_text(_TEMPLATE, encoding="utf-8")


class ThemeConfigTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_path = Path(self.enterContext(tempfile.TemporaryDirectory()))

    def _build(self, theme_literal: str) -> str:
        """Build a one-page site whose config sets ``theme=<theme_literal>``."""
        from pyssg.cli import build_site

        site = self.tmp_path / "site"
        layout = self.tmp_path / "layout"
        _write_layout(layout)
        (site / "content").mkdir(parents=True)
        (site / "content" / "index.md").write_text("---\ntitle: Home\n---\nHi.\n", encoding="utf-8")
        (site / "pyssg.config.py").write_text(
            "from __future__ import annotations\n"
            "from pathlib import Path\n"
            "from pyssg.config import Config\n"
            "from pyssg.plugins.directory_loader import directory_loader\n"
            "from pyssg.plugins.frontmatter import frontmatter\n"
            "from pyssg.plugins.markdown import markdown\n"
            "from pyssg.plugins.permalink import permalink\n"
            "from pyssg.plugins.render import render\n"
            "config = Config(\n"
            f"    layout=Path({str(layout)!r}),\n"
            f"    theme={theme_literal},\n"
            "    plugins=[directory_loader(), frontmatter(), markdown(), "
            "permalink(), render()],\n"
            ")\n",
            encoding="utf-8",
        )
        build_site(site)
        return (site / "dist" / "index.html").read_text(encoding="utf-8")

    def test_defaults_apply_when_site_overrides_nothing(self) -> None:
        html = self._build("{}")
        self.assertIn("accent=#000000;show_toc=True;extra=none", html)

    def test_site_overrides_individual_keys(self) -> None:
        html = self._build("{'accent': '#0b66c3', 'show_toc': False}")
        # Overridden keys win; untouched ones keep the theme default.
        self.assertIn("accent=#0b66c3;show_toc=False;extra=none", html)

    def test_declared_overrides_do_not_warn(self) -> None:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            self._build("{'accent': '#0b66c3', 'show_toc': False}")
        self.assertEqual([str(w.message) for w in caught], [])

    def test_undeclared_key_passes_through_with_warning(self) -> None:
        # Hybrid contract: a key the theme does not declare is still forwarded to
        # templates, but the engine warns so a typo does not pass silently.
        with self.assertWarnsRegex(UserWarning, "extra"):
            html = self._build("{'extra': 'custom'}")
        self.assertIn("extra=custom", html)


if __name__ == "__main__":
    unittest.main()
