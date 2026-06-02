"""Layout package loading and validation.

A layout is a directory bundle the basic user customizes (templates + assets).
Its ``layout.toml`` manifest declares the layout's name, version and default
template; ``templates/`` holds the Jinja2 templates and the optional ``assets/``
holds css/js/fonts that get copied and content-hashed.

This loader only locates and validates the bundle into an immutable
:class:`Layout` record. Reading the manifest is pure (stdlib ``tomllib``); the
record carries no mutable state so it is safe to share across builds.
"""

from __future__ import annotations

import tomllib
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from types import MappingProxyType

from pyssg.core.errors import LayoutError

# Manifest filename and subdirectory layout.
_MANIFEST_FILENAME = "layout.toml"
_TEMPLATES_DIRNAME = "templates"
_ASSETS_DIRNAME = "assets"
_OPTIONS_KEY = "options"

# Defaults applied when the manifest omits a key.
_DEFAULT_VERSION = "0.0.0"
_DEFAULT_TEMPLATE = "page.html.j2"


@dataclass(slots=True, frozen=True)
class Layout:
    """A validated layout package.

    ``root`` is the package directory; ``templates_dir`` and ``assets_dir`` are
    resolved against it. ``assets_dir`` is None when the package ships no assets.

    ``options`` is the theme's configurable-option defaults, read verbatim from
    the manifest ``[options]`` table (an empty mapping when the table is absent).
    The engine layers the site's :attr:`pyssg.config.Config.theme` over these
    defaults to produce the ``theme`` template variable; the layout itself only
    declares the defaults and never resolves them.
    """

    name: str
    version: str
    root: Path
    templates_dir: Path
    assets_dir: Path | None
    default_template: str
    # Defaults to an empty read-only mapping so a layout built without options
    # (and direct construction in tests) needs no boilerplate.
    options: Mapping[str, object] = field(default_factory=lambda: MappingProxyType({}))


def load_layout(path: Path) -> Layout:
    """Load and validate the layout package rooted at ``path``.

    Raises :class:`LayoutError` if the directory, manifest, ``templates/`` dir or
    the declared default template are missing.
    """
    if not path.is_dir():
        raise LayoutError(f"layout package directory does not exist: {path}")

    manifest_path = path / _MANIFEST_FILENAME
    if not manifest_path.is_file():
        raise LayoutError(f"layout package is missing {_MANIFEST_FILENAME}: {manifest_path}")

    with manifest_path.open("rb") as fp:
        manifest = tomllib.load(fp)

    # Be lenient with sensible defaults: name falls back to the directory name,
    # version/default_template to fixed defaults.
    name = _as_str(manifest, "name", default=path.name, manifest_path=manifest_path)
    version = _as_str(manifest, "version", default=_DEFAULT_VERSION, manifest_path=manifest_path)
    default_template = _as_str(
        manifest, "default_template", default=_DEFAULT_TEMPLATE, manifest_path=manifest_path
    )

    templates_dir = path / _TEMPLATES_DIRNAME
    if not templates_dir.is_dir():
        raise LayoutError(f"layout package is missing a {_TEMPLATES_DIRNAME}/ directory: {path}")

    # The default template must actually exist, otherwise every page that relies
    # on it would fail far later at render time with a less obvious error.
    default_template_path = templates_dir / default_template
    if not default_template_path.is_file():
        raise LayoutError(f"default template not found: {default_template_path}")

    assets_dir = path / _ASSETS_DIRNAME
    resolved_assets_dir = assets_dir if assets_dir.is_dir() else None

    options = _read_options(manifest, manifest_path)

    return Layout(
        name=name,
        version=version,
        root=path,
        templates_dir=templates_dir,
        assets_dir=resolved_assets_dir,
        default_template=default_template,
        options=options,
    )


def _read_options(manifest: dict[str, object], manifest_path: Path) -> Mapping[str, object]:
    """Read the manifest ``[options]`` table as the theme's option defaults.

    An absent table yields an empty mapping. A present-but-non-table value is a
    malformed manifest, so it raises rather than being silently dropped. The
    result is wrapped read-only so the immutable :class:`Layout` cannot be
    mutated through it after loading.
    """
    if _OPTIONS_KEY not in manifest:
        return MappingProxyType({})
    value = manifest[_OPTIONS_KEY]
    if not isinstance(value, dict):
        raise LayoutError(
            f"{_MANIFEST_FILENAME} key '{_OPTIONS_KEY}' must be a table, "
            f"got {type(value).__name__}: {manifest_path}"
        )
    # Copy so later mutation of the parsed manifest cannot leak into the record.
    return MappingProxyType(dict(value))


def _as_str(manifest: dict[str, object], key: str, *, default: str, manifest_path: Path) -> str:
    """Read a string manifest value, applying ``default`` when the key is absent.

    A present-but-wrong-typed value is a malformed manifest, so it raises rather
    than being silently coerced.
    """
    if key not in manifest:
        return default
    value = manifest[key]
    if not isinstance(value, str):
        raise LayoutError(
            f"{_MANIFEST_FILENAME} key '{key}' must be a string, "
            f"got {type(value).__name__}: {manifest_path}"
        )
    return value
