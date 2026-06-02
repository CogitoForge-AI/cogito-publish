from __future__ import annotations

from pyssg.presets import docs

# Drive the gallery `docs-technical` theme (docsy-style) through the docs preset.
# The theme lives in the repo-root `themes/` gallery (source-only, not packaged),
# so the test vendors it into this site under `theme/` and points `layout` at
# that relative path. `theme=` overrides exercise the theme config API (#53).
config = docs(
    site={"title": "My Docs"},
    base_url="https://example.com",
    layout="theme",
)
config.theme = {"default_theme": "dark", "accent": "#b5179e"}
