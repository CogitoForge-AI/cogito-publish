"""I18n plugin: multilingual sites from a folder-per-locale source tree.

Folder-based only: the first path segment of a source decides its locale
(``vi/posts/x.md`` -> locale ``vi``). The locale segment is kept in the path on
purpose, so :class:`~pyssg_plugins.permalink.Permalink` derives the public URL
from it.

The default locale renders at the site root (``en/posts/x.md`` ->
``/posts/x/`` when ``en`` is the default); every other locale keeps its prefix
(``/vi/posts/x/``). I18n communicates this to Permalink via
``meta["locale_prefix"]`` -- ``""`` for the default locale, the segment
otherwise -- so the relpath itself is never rewritten (collection names and
navigation trees keep the locale segment).

It taps ``collect`` twice:

- early (before Permalink) it stamps each source with ``meta["locale"]`` and a
  ``meta["translation_key"]`` (the path *after* the locale segment, without the
  suffix), so pages that are translations of each other share a key;
- late (after Listing/Navigation) it builds a build-wide translation index
  ``build.meta["i18n"]`` and hangs ``meta["translations"]`` on every page -- the
  ordered list a layout renders as a language switcher and ``hreflang`` tags.

Pages without a known locale folder (e.g. a root ``index.md``) fall back to the
default locale. A page may override its pairing with frontmatter
``translation_key``.

Standard library only.
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from pyssg.build import Build
from pyssg.builder import Builder
from pyssg.content import (
    I18N,
    LOCALE,
    LOCALE_PREFIX,
    TRANSLATION_KEY,
    TRANSLATIONS,
    URL,
    is_draft,
    site,
)
from pyssg.models import Source

# Tag locales before Permalink (-200); build the index after Navigation (100),
# so generated listing pages (Listing at stage 0) are paired too.
_TAG_STAGE = -300
_INDEX_STAGE = 200


class I18n:
    def __init__(
        self,
        *,
        locales: Sequence[str],
        default_locale: str,
        translation_key_field: str = "translation_key",
    ) -> None:
        if not locales:
            raise ValueError("I18n needs at least one locale")
        if default_locale not in locales:
            raise ValueError(
                f"default_locale {default_locale!r} is not in locales {list(locales)}"
            )
        self._locales = list(locales)
        self._default = default_locale
        self._key_field = translation_key_field

    def apply(self, builder: Builder) -> None:
        builder.hooks.collect.tap("I18n", self._tag, stage=_TAG_STAGE)
        builder.hooks.collect.tap("I18n", self._index, stage=_INDEX_STAGE)

    def _tag(self, build: Build) -> None:
        for source in build.sources:
            parts = source.relpath.parts
            first = parts[0] if parts else ""
            if first in self._locales:
                locale = first
                rest = Path(*parts[1:]) if len(parts) > 1 else source.relpath
            else:
                locale = self._default
                rest = source.relpath
            source.meta[LOCALE] = locale
            # The default locale lives at the root (no prefix); others keep
            # their segment. Permalink reads this to strip the prefix.
            source.meta[LOCALE_PREFIX] = "" if locale == self._default else locale
            source.meta[TRANSLATION_KEY] = self._translation_key(source, rest)

    def _translation_key(self, source: Source, rest: Path) -> str:
        override = source.frontmatter.get(self._key_field)
        if isinstance(override, str) and override:
            return override
        return rest.with_suffix("").as_posix()

    def _index(self, build: Build) -> None:
        translations: dict[str, dict[str, str]] = {}
        for source in build.sources:
            if is_draft(source):
                continue
            locale = source.meta.get(LOCALE)
            key = source.meta.get(TRANSLATION_KEY)
            url = source.meta.get(URL)
            if not (isinstance(locale, str) and isinstance(key, str) and url):
                continue
            translations.setdefault(key, {}).setdefault(locale, str(url))

        build.meta[I18N] = {
            "locales": list(self._locales),
            "default_locale": self._default,
            "translations": translations,
        }
        seeded = site(build)
        seeded.setdefault("locales", list(self._locales))
        seeded.setdefault("default_locale", self._default)

        for source in build.sources:
            self._attach(source, translations)

    def _attach(self, source: Source, translations: dict[str, dict[str, str]]) -> None:
        key = source.meta.get(TRANSLATION_KEY)
        current = source.meta.get(LOCALE)
        by_locale = translations.get(key, {}) if isinstance(key, str) else {}
        # Order by configured locale order for deterministic output.
        source.meta[TRANSLATIONS] = [
            {"locale": locale, "url": by_locale[locale], "current": locale == current}
            for locale in self._locales
            if locale in by_locale
        ]
