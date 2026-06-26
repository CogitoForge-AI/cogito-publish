"""Command-line interface.

The CLI is a Typer (Click) command tree. This package is the thin assembler: it
imports :mod:`pyssg.cli.commands` (whose import registers every subcommand on the
root app) and re-exports :func:`main` and the shared builder helpers.

- ``cogito-publish build`` runs a full build (``--no-cache``, ``--profile``, ``--json``).
- ``cogito-publish serve`` watches + incrementally rebuilds + serves with live reload.
- ``cogito-publish clean`` removes the output dir and cache (with confirmation).
- ``cogito-publish new`` scaffolds a ``site`` / ``post`` / ``theme`` / ``plugin``.
- ``cogito-publish deploy`` pushes the built site to a hosting provider; see
  :mod:`pyssg.cli.commands.deploy` for the subcommand surface.
"""

from __future__ import annotations

# Importing the commands package registers every subcommand on the root app as a
# side effect; it must run before ``main`` is used so the command tree is built.
from pyssg.cli import commands as commands
from pyssg.cli.app import app, main
from pyssg.cli.common import build_site, make_builder

__all__ = ["app", "build_site", "main", "make_builder"]
