from __future__ import annotations

from pyssg.presets import docs

# A complete documentation site built from the bundled ``docs`` preset and the
# default ``docs`` theme. Every Markdown file under ``content/`` becomes a page;
# directories become sidebar sections, and ``[[wikilinks]]`` cross-reference
# pages by title.
config = docs(
    site={
        "title": "Widgetizer",
        "description": "Documentation for the Widgetizer toolkit.",
    },
    base_url="https://docs.example.com",
)
