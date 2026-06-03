"""Asset-copy plugin.

Mirrors static file trees into the build output. By default it copies the active
layout's ``assets/`` directory to ``/assets/...`` (the theme owns those bytes);
beyond that, a site declares its own ``mounts`` -- a many-to-many list of
``(source, dest)`` pairs -- to publish site-local files such as ``static/`` at
the output root (so ``/style.css``, ``/images/...``, ``/robots.txt`` resolve
exactly where posts reference them).

Each mount's ``source`` is a directory: a relative string is resolved against the
site root, an absolute path is used as-is. Each ``dest`` is a site-absolute URL
path (``"/"`` for the output root, ``"/assets/vendor/"`` for a subtree). A missing
source directory is skipped rather than erroring, so an optional mount is
harmless.

A file is (re)written only when it is missing from the output or its bytes differ
from the source, so rebuilds stay cheap and the output is byte-identical to a
full rebuild. The copy is keyed on ``evaluate_collections`` (once per finalize)
and is a deterministic function of the source bytes -- no clock, no globals -- so
two builds are byte-identical. It never deletes files it did not place, so a
file removed from a source stays in the output until ``pyssg clean`` (a
deliberate, documented limitation).

Before writing anything the plugin checks for output-path collisions: if a mount
file would land on the same output file as a generated page (including the
virtual sitemap/rss/term pages) or as another mount file, it raises
:class:`~pyssg.core.errors.OutputConflictError` and aborts the build, leaving the
conflict for the user to resolve. The tap therefore runs *after* the page-
emitting summarizer plugins so every page URL is known when the check runs.
"""

from __future__ import annotations

import hashlib
import shutil
from pathlib import Path
from typing import TYPE_CHECKING

from pyssg.core.errors import OutputConflictError
from pyssg.core.node import Page
from pyssg.core.phases import output_path_for

if TYPE_CHECKING:
    from collections.abc import Iterator, Sequence

    from pyssg.core.build import Build
    from pyssg.core.builder import Builder

#: A ``(source, dest)`` mount: ``source`` is a directory (relative to the site
#: root, or absolute) and ``dest`` is a site-absolute URL path under the output.
type Mount = tuple[str, str]

_LAYOUT_ASSETS_DEST = "/assets/"
# Summarizer plugins that emit virtual pages during ``evaluate_collections``; we
# must run after them so every page URL is visible to the collision check.
_AFTER = ("nav", "taxonomy", "collections", "sitemap", "rss")


class _ResolvedMount:
    """A mount with both endpoints resolved to absolute filesystem roots."""

    __slots__ = ("dst_root", "label", "src_root")

    def __init__(self, *, src_root: Path, dst_root: Path, label: str) -> None:
        self.src_root = src_root
        self.dst_root = dst_root
        #: Human-readable origin used in conflict messages (the source, as given).
        self.label = label

    def files(self) -> Iterator[tuple[Path, Path]]:
        """Yield ``(src, dst)`` for every file in the tree, in a stable order.

        The walk is sorted so copying order is deterministic; order has no
        observable effect on output but keeps behaviour easy to reason about.
        """
        for src in sorted(p for p in self.src_root.rglob("*") if p.is_file()):
            yield src, self.dst_root / src.relative_to(self.src_root)


def _needs_copy(src: Path, dst: Path) -> bool:
    """True when ``dst`` is absent or its bytes differ from ``src``.

    Comparing bytes (rather than mtime/size) keeps the result independent of the
    filesystem clock, so an unchanged asset is never rewritten on rebuild.
    """
    if not dst.exists():
        return True
    return src.read_bytes() != dst.read_bytes()


class AssetCopyPlugin:
    """Built-in copier for the layout's assets plus any site-declared mounts.

    Customise by subclassing: override :meth:`resolve_mounts` to change which
    trees are copied (e.g. drop the implicit layout-assets mount), while reusing
    the byte-compare copy and the collision check.
    """

    name = "asset_copy"
    # Bumped from 1.0.0: now supports arbitrary ``(source, dest)`` mounts.
    cache_version = "1.1.0"

    def __init__(self, *, mounts: Sequence[Mount] | None = None) -> None:
        # Copy so a caller mutating their list after construction cannot change
        # what this plugin copies mid-build.
        self._mounts: tuple[Mount, ...] = tuple(mounts or ())
        self.cache_version = self._compute_cache_version()

    def _compute_cache_version(self) -> str:
        """Fold the mount list into the cache key so a changed set busts caches."""
        if not self._mounts:
            return "1.1.0"
        payload = "|".join(f"{src}=>{dst}" for src, dst in self._mounts)
        digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12]
        return f"1.1.0:{digest}"

    def apply(self, builder: Builder) -> None:
        @builder.hooks.this_compilation.tap(self.name)
        def _wire(build: Build) -> None:
            @build.hooks.evaluate_collections.tap(self.name, after=_AFTER)
            def _eval(b: Build) -> None:
                self.run(b)

    def resolve_mounts(self, build: Build) -> list[_ResolvedMount]:
        """Resolve every mount (implicit layout assets + site mounts) to roots.

        The layout's ``assets/`` directory is always copied to ``/assets/`` (the
        existing default); each configured ``(source, dest)`` is added on top. A
        mount whose source directory is absent is dropped.
        """
        config = build.builder.config
        if config is None:
            return []
        site_dir = build.builder.site_dir
        out_root = site_dir / config.output_dir

        resolved: list[_ResolvedMount] = []
        layout = build.builder.layout
        if layout is not None and layout.assets_dir is not None:
            resolved.append(
                _ResolvedMount(
                    src_root=layout.assets_dir,
                    dst_root=self._dest_root(out_root, _LAYOUT_ASSETS_DEST),
                    label="<layout assets>",
                )
            )
        for source, dest in self._mounts:
            src_root = Path(source)
            if not src_root.is_absolute():
                src_root = site_dir / src_root
            if not src_root.is_dir():
                continue  # an optional/absent source mount is a no-op
            resolved.append(
                _ResolvedMount(
                    src_root=src_root,
                    dst_root=self._dest_root(out_root, dest),
                    label=source,
                )
            )
        return resolved

    def _dest_root(self, out_root: Path, dest: str) -> Path:
        """Map a site-absolute ``dest`` URL path to an output directory."""
        rel = dest.strip("/")
        return out_root if rel == "" else out_root / rel

    def run(self, build: Build) -> None:
        """Plan the copy, fail fast on any collision, then mirror each tree.

        Nothing is written until the whole copy plan is collision-free, so an
        aborted build never leaves a half-applied output.
        """
        mounts = self.resolve_mounts(build)
        if not mounts:
            return
        out_root = self._out_root(build)
        if out_root is None:
            return
        plan = self._plan(build, mounts, out_root)
        for src, dst in plan:
            if _needs_copy(src, dst):
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(src, dst)

    def _out_root(self, build: Build) -> Path | None:
        config = build.builder.config
        if config is None:
            return None
        return build.builder.site_dir / config.output_dir

    def _plan(
        self, build: Build, mounts: list[_ResolvedMount], out_root: Path
    ) -> list[tuple[Path, Path]]:
        """Build the ``(src, dst)`` copy list, raising on the first collision.

        ``claims`` maps an output-relative path to the artifact that owns it. Page
        outputs are seeded first (their paths are predicted from each page URL);
        adding a mount file that lands on an already-claimed path -- a page or an
        earlier mount file -- is an :class:`OutputConflictError`.
        """
        claims = self._page_claims(build, out_root)
        plan: list[tuple[Path, Path]] = []
        for mount in mounts:
            for src, dst in mount.files():
                rel = dst.relative_to(out_root).as_posix()
                existing = claims.get(rel)
                if existing is not None:
                    raise OutputConflictError(
                        f"output path {rel!r} is claimed by both {existing} and "
                        f"asset {src} (from mount {mount.label}); "
                        "resolve the collision (rename or move one) and rebuild"
                    )
                claims[rel] = f"asset {src} (from mount {mount.label})"
                plan.append((src, dst))
        return plan

    def _page_claims(self, build: Build, out_root: Path) -> dict[str, str]:
        """Output-relative paths each generated page will write, keyed for lookup.

        Page-vs-page duplicates are the engine's concern, not ours, so a repeated
        path simply keeps the last writer here; we only ever *check* mount files
        against this set.
        """
        claims: dict[str, str] = {}
        for node in build.graph.nodes():
            if not isinstance(node, Page):
                continue
            rel = output_path_for(out_root, node.url).relative_to(out_root).as_posix()
            claims[rel] = f"page {node.url}"
        return claims


def copy_assets(build: Build) -> None:
    """Mirror the layout ``assets/`` tree into the output. Thin default wrapper."""
    AssetCopyPlugin().run(build)


def asset_copy(mounts: Sequence[Mount] | None = None) -> AssetCopyPlugin:
    """Factory used in ``pyssg.config.py``.

    ``mounts`` is an optional list of ``(source, dest)`` pairs publishing extra
    static trees; see :class:`AssetCopyPlugin`. Omitting it keeps the default
    behavior (copy the layout's ``assets/`` to ``/assets/``).
    """
    return AssetCopyPlugin(mounts=mounts)
