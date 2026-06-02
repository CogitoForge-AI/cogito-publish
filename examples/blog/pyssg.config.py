from __future__ import annotations

from pyssg.presets import blog

# A complete blog built from the bundled ``blog`` preset and the default
# ``blog`` theme. Posts live under ``content/posts/`` and are paginated on the
# home page, newest-first, by their ``date`` frontmatter.
config = blog(
    site={
        "title": "The Rendered Web",
        "description": "Notes on static sites, build pipelines, and the craft of publishing.",
    },
    base_url="https://blog.example.com",
    posts_per_page=3,
)
