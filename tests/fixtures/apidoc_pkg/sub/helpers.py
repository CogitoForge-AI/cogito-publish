"""Helpers in a subpackage (Google style)."""

from __future__ import annotations


class Box:
    """A simple container."""

    def __init__(self, value: int) -> None:
        """Store ``value``.

        Args:
            value: The wrapped value.
        """
        self.value = value

    def _secret(self) -> int:
        """Private helper that must not appear by default."""
        return self.value
