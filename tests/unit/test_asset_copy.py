"""Unit tests for the asset_copy plugin."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from pyssg.config import Config
from pyssg.core.build import Build
from pyssg.core.builder import Builder
from pyssg.core.errors import OutputConflictError
from pyssg.core.node import Page
from pyssg.core.types import NodeKind
from pyssg.layout import Layout
from pyssg.plugins.asset_copy import asset_copy, copy_assets


def _layout_with_assets(root: Path) -> Layout:
    """A minimal Layout record whose ``assets_dir`` is populated."""
    assets = root / "assets"
    templates = root / "templates"
    assets.mkdir(parents=True)
    templates.mkdir(parents=True)
    return Layout(
        name="test",
        version="0.0.0",
        root=root,
        templates_dir=templates,
        assets_dir=assets,
        default_template="page.html.j2",
    )


def _build(tmp_path: Path, layout: Layout | None) -> Build:
    builder = Builder(config=Config(output_dir="dist"), site_dir=tmp_path)
    builder.layout = layout
    return builder.create_build()


class CopyAssetsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_path = Path(self.enterContext(tempfile.TemporaryDirectory()))

    def test_copy_assets_mirrors_tree(self) -> None:
        layout = _layout_with_assets(self.tmp_path / "layout")
        assert layout.assets_dir is not None  # narrow Optional for type checker
        (layout.assets_dir / "css").mkdir()
        (layout.assets_dir / "css" / "site.css").write_text("body{}")
        (layout.assets_dir / "logo.svg").write_text("<svg/>")

        build = _build(self.tmp_path, layout)
        copy_assets(build)

        out = self.tmp_path / "dist" / "assets"
        self.assertEqual((out / "css" / "site.css").read_text(), "body{}")
        self.assertEqual((out / "logo.svg").read_text(), "<svg/>")

    def test_copy_assets_noop_without_layout(self) -> None:
        build = _build(self.tmp_path, None)
        copy_assets(build)
        self.assertFalse((self.tmp_path / "dist").exists())

    def test_copy_assets_skips_unchanged_files(self) -> None:
        layout = _layout_with_assets(self.tmp_path / "layout")
        assert layout.assets_dir is not None  # narrow Optional for type checker
        src = layout.assets_dir / "a.txt"
        src.write_text("v1")

        build = _build(self.tmp_path, layout)
        copy_assets(build)
        dst = self.tmp_path / "dist" / "assets" / "a.txt"
        mtime = dst.stat().st_mtime_ns

        # An unchanged source must not rewrite the destination file.
        copy_assets(build)
        self.assertEqual(dst.stat().st_mtime_ns, mtime)

    def test_copy_assets_updates_changed_files(self) -> None:
        layout = _layout_with_assets(self.tmp_path / "layout")
        assert layout.assets_dir is not None  # narrow Optional for type checker
        src = layout.assets_dir / "a.txt"
        src.write_text("v1")

        build = _build(self.tmp_path, layout)
        copy_assets(build)

        src.write_text("v2")
        copy_assets(build)
        self.assertEqual((self.tmp_path / "dist" / "assets" / "a.txt").read_text(), "v2")

    def test_copy_assets_leaves_unknown_output_files(self) -> None:
        layout = _layout_with_assets(self.tmp_path / "layout")
        assert layout.assets_dir is not None  # narrow Optional for type checker
        (layout.assets_dir / "a.txt").write_text("v1")

        out_assets = self.tmp_path / "dist" / "assets"
        out_assets.mkdir(parents=True)
        (out_assets / "keep.txt").write_text("user file")

        build = _build(self.tmp_path, layout)
        copy_assets(build)

        # The plugin never deletes files it did not place.
        self.assertEqual((out_assets / "keep.txt").read_text(), "user file")
        self.assertEqual((out_assets / "a.txt").read_text(), "v1")


def _add_page(build: Build, pid: str, url: str) -> None:
    build.graph.add_node(Page(id=pid, kind=NodeKind.PAGE, url=url))


class MountsTest(unittest.TestCase):
    """Site-declared ``(source, dest)`` mounts publish extra static trees."""

    def setUp(self) -> None:
        self.tmp_path = Path(self.enterContext(tempfile.TemporaryDirectory()))

    def _build(self) -> Build:
        builder = Builder(config=Config(output_dir="dist"), site_dir=self.tmp_path)
        return builder.create_build()

    def _static_dir(self, name: str = "static") -> Path:
        d = self.tmp_path / name
        d.mkdir(parents=True, exist_ok=True)
        return d

    def test_relative_source_copies_to_output_root(self) -> None:
        static = self._static_dir()
        static.joinpath("style.css").write_text("body{}")
        (static / "images").mkdir()
        (static / "images" / "a.png").write_bytes(b"PNG")

        asset_copy(mounts=[("static", "/")]).run(self._build())

        out = self.tmp_path / "dist"
        self.assertEqual((out / "style.css").read_text(), "body{}")
        self.assertEqual((out / "images" / "a.png").read_bytes(), b"PNG")

    def test_relative_source_to_subpath_dest(self) -> None:
        vendor = self._static_dir("vendor")
        vendor.joinpath("lib.js").write_text("x")

        asset_copy(mounts=[("vendor", "/assets/vendor/")]).run(self._build())

        self.assertEqual((self.tmp_path / "dist" / "assets" / "vendor" / "lib.js").read_text(), "x")

    def test_absolute_source_path(self) -> None:
        external = Path(self.enterContext(tempfile.TemporaryDirectory())) / "ext"
        external.mkdir()
        external.joinpath("robots.txt").write_text("User-agent: *")

        asset_copy(mounts=[(str(external), "/")]).run(self._build())

        self.assertEqual((self.tmp_path / "dist" / "robots.txt").read_text(), "User-agent: *")

    def test_absent_source_is_noop(self) -> None:
        asset_copy(mounts=[("does-not-exist", "/")]).run(self._build())
        self.assertFalse((self.tmp_path / "dist").exists())

    def test_skips_unchanged_files(self) -> None:
        static = self._static_dir()
        src = static / "a.txt"
        src.write_text("v1")
        plugin = asset_copy(mounts=[("static", "/")])

        build = self._build()
        plugin.run(build)
        dst = self.tmp_path / "dist" / "a.txt"
        mtime = dst.stat().st_mtime_ns

        plugin.run(build)  # unchanged source must not rewrite the destination
        self.assertEqual(dst.stat().st_mtime_ns, mtime)


class ConflictDetectionTest(unittest.TestCase):
    """A mount file colliding with a page or another mount aborts the build."""

    def setUp(self) -> None:
        self.tmp_path = Path(self.enterContext(tempfile.TemporaryDirectory()))

    def _build(self) -> Build:
        builder = Builder(config=Config(output_dir="dist"), site_dir=self.tmp_path)
        return builder.create_build()

    def test_static_collides_with_page_raises(self) -> None:
        static = self.tmp_path / "static"
        (static / "about").mkdir(parents=True)
        # A page at /about/ writes dist/about/index.html; the static file lands
        # on the same output path.
        (static / "about" / "index.html").write_text("static")

        build = self._build()
        _add_page(build, "page:about", "/about/")
        with self.assertRaises(OutputConflictError) as ctx:
            asset_copy(mounts=[("static", "/")]).run(build)
        self.assertIn("about/index.html", str(ctx.exception))

    def test_static_collides_with_extensioned_page_raises(self) -> None:
        static = self.tmp_path / "static"
        static.mkdir()
        (static / "feed.xml").write_text("static feed")

        build = self._build()
        _add_page(build, "page:rss", "/feed.xml")  # rss writes dist/feed.xml
        with self.assertRaises(OutputConflictError):
            asset_copy(mounts=[("static", "/")]).run(build)

    def test_two_mounts_colliding_raises(self) -> None:
        a = self.tmp_path / "a"
        b = self.tmp_path / "b"
        a.mkdir()
        b.mkdir()
        a.joinpath("x.txt").write_text("from a")
        b.joinpath("x.txt").write_text("from b")  # both map to dist/x.txt

        with self.assertRaises(OutputConflictError):
            asset_copy(mounts=[("a", "/"), ("b", "/")]).run(self._build())

    def test_no_collision_passes(self) -> None:
        static = self.tmp_path / "static"
        static.mkdir()
        static.joinpath("style.css").write_text("body{}")

        build = self._build()
        _add_page(build, "page:home", "/")  # dist/index.html, no overlap
        asset_copy(mounts=[("static", "/")]).run(build)
        self.assertEqual((self.tmp_path / "dist" / "style.css").read_text(), "body{}")

    def test_conflict_aborts_before_writing_anything(self) -> None:
        # An earlier, valid file must not be written when a later file conflicts:
        # the plan is checked in full before any copy happens.
        a = self.tmp_path / "a"
        a.mkdir()
        a.joinpath("ok.txt").write_text("ok")
        a.joinpath("about").mkdir()
        a.joinpath("about", "index.html").write_text("collides")

        build = self._build()
        _add_page(build, "page:about", "/about/")
        with self.assertRaises(OutputConflictError):
            asset_copy(mounts=[("a", "/")]).run(build)
        # Nothing was written -- not even the non-colliding ok.txt.
        self.assertFalse((self.tmp_path / "dist").exists())
