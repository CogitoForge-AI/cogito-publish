"""Core exception hierarchy (stdlib only).

Errors raised by the engine are explicit configuration / contract violations, so
plugin authors get a clear message instead of silent incorrectness.
"""

from __future__ import annotations


class PyssgError(Exception):
    """Base class for all pyssg errors."""


class HookOrderError(PyssgError):
    """A hook's tap ordering constraints (before/after) form a cycle."""


class ConfigError(PyssgError):
    """The site configuration is invalid or could not be loaded."""


class LayoutError(PyssgError):
    """A layout package is missing required pieces or is malformed."""


class OutputConflictError(PyssgError):
    """Two build artifacts claim the same output path.

    Raised before anything is written when a static asset would land on the same
    output file as a generated page (or another asset), so the collision is
    surfaced for the user to resolve instead of one artifact silently clobbering
    the other.
    """
