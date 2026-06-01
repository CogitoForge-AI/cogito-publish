"""Sample package used to test the apidoc contrib plugin.

This top-level docstring should appear on the package's reference page.
"""

from __future__ import annotations


def greet(name: str, *, loud: bool = False) -> str:
    """Build a greeting.

    Args:
        name: Who to greet.
        loud: If True, shout it.

    Returns:
        str: The greeting line.

    Raises:
        ValueError: If name is empty.
    """
    raise NotImplementedError
