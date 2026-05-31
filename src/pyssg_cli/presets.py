"""Presets: ready-made plugin stacks for the three target use cases.

A preset is just a function returning a list of plugin instances in the right
order, so beginners write one line while power users keep the freedom to
assemble plugins by hand:

    from pyssg_cli.presets import docs
    plugins = docs()

- ``docs()`` -- technical documentation: folder-based sidebar with prev/next.
- ``blog()`` -- personal blog: paginated index, tag pages, top menu, RSS.
- ``site()`` -- company/organisation site: flat top menu, standalone pages.
- ``i18n_blog()`` -- a multilingual blog: ``blog()`` partitioned per locale from
  a folder-per-locale source tree (``<locale>/<posts_dir>/...``).
- ``i18n_docs()`` -- multilingual documentation: ``docs()`` partitioned per
  locale, each with its own folder sidebar and prev/next.

All presets accept ``sitemap``, ``minify``, ``robots`` and ``markdown_pages``
flags to enable the matching tier-3 plugin, ``seo`` (on by default) for
SEO/social head tags and ``highlight`` to syntax-highlight fenced code blocks
with Pygments; ``blog()`` also generates an RSS feed by default.
"""

from __future__ import annotations

from collections.abc import Sequence

from pyssg.plugin import Plugin
from pyssg_plugins.collections import Collections
from pyssg_plugins.frontmatter import Frontmatter
from pyssg_plugins.highlight import Highlight
from pyssg_plugins.i18n import I18n
from pyssg_plugins.listing import Listing
from pyssg_plugins.markdown import Markdown
from pyssg_plugins.markdown_page import MarkdownPage
from pyssg_plugins.minify import Minify
from pyssg_plugins.navigation import Navigation
from pyssg_plugins.permalink import Permalink
from pyssg_plugins.read_file import ReadFile
from pyssg_plugins.redirects import Redirects
from pyssg_plugins.robots import Robots
from pyssg_plugins.rss import Rss
from pyssg_plugins.seo import Seo
from pyssg_plugins.sitemap import Sitemap
from pyssg_plugins.template import Template
from pyssg_plugins.write_file import WriteFile


def _head(markdown_extensions: Sequence[str], highlight: bool) -> list[Plugin]:
    head: list[Plugin] = [
        ReadFile(),
        Frontmatter(),
        Markdown(extensions=markdown_extensions),
    ]
    if highlight:
        head.append(Highlight(dark_style="github-dark"))
    return head


def _extras(
    *, sitemap: bool, minify: bool, robots: bool, markdown_pages: bool
) -> list[Plugin]:
    extras: list[Plugin] = []
    if sitemap:
        extras.append(Sitemap())
    if robots:
        extras.append(Robots())
    if markdown_pages:
        extras.append(MarkdownPage())
    if minify:
        extras.append(Minify())
    return extras


def _tail(template_dir: str, clean: bool) -> list[Plugin]:
    return [Template(directory=template_dir), WriteFile(clean=clean)]


def docs(
    *,
    markdown_extensions: Sequence[str] = (),
    template_dir: str = "layouts",
    clean: bool = True,
    sitemap: bool = False,
    minify: bool = False,
    robots: bool = False,
    markdown_pages: bool = False,
    seo: bool = True,
    highlight: bool = False,
) -> list[Plugin]:
    return [
        *_head(markdown_extensions, highlight),
        Permalink(),
        Collections(by_tag=False, by_folder=True),
        Navigation(mode="folder", sequential=True),
        *_extras(
            sitemap=sitemap,
            minify=minify,
            robots=robots,
            markdown_pages=markdown_pages,
        ),
        *([Seo(schema_type="Article")] if seo else []),
        *_tail(template_dir, clean),
    ]


def blog(
    *,
    page_size: int = 10,
    markdown_extensions: Sequence[str] = (),
    template_dir: str = "layouts",
    clean: bool = True,
    rss: bool = True,
    sitemap: bool = False,
    minify: bool = False,
    robots: bool = False,
    markdown_pages: bool = False,
    seo: bool = True,
    highlight: bool = False,
) -> list[Plugin]:
    plugins: list[Plugin] = [
        *_head(markdown_extensions, highlight),
        Permalink(),
        Collections(by_tag=True, by_folder=True),
        Listing(
            collection="blog", base_url="/blog/", title="Blog", page_size=page_size
        ),
        Listing(kind="tag", base_url="/tags/:name/", title=":name"),
        Navigation(mode="frontmatter"),
    ]
    if rss:
        plugins.append(Rss(collection="blog"))
    plugins.extend(
        _extras(
            sitemap=sitemap,
            minify=minify,
            robots=robots,
            markdown_pages=markdown_pages,
        )
    )
    if seo:
        plugins.append(Seo(schema_type="BlogPosting"))
    plugins.extend(_tail(template_dir, clean))
    return plugins


def i18n_blog(
    *,
    locales: Sequence[str],
    default_locale: str,
    posts_dir: str = "posts",
    page_size: int = 10,
    markdown_extensions: Sequence[str] = (),
    template_dir: str = "layouts",
    clean: bool = True,
    rss: bool = True,
    sitemap: bool = False,
    minify: bool = False,
    robots: bool = False,
    markdown_pages: bool = False,
    seo: bool = True,
    highlight: bool = False,
    root_redirect: bool = True,
) -> list[Plugin]:
    """A multilingual blog: one ``blog()`` partitioned per locale.

    Sources live under ``<locale>/<posts_dir>/...``; the locale segment is kept
    in the URL (``/vi/posts/x/``). Each locale gets its own paginated index at
    ``/<locale>/`` and RSS feed; tag pages and the top menu are produced once and
    split by locale. With ``root_redirect`` the bare ``/`` redirects to the
    default locale's home.
    """

    if default_locale not in locales:
        raise ValueError(
            f"default_locale {default_locale!r} is not in locales {list(locales)}"
        )

    plugins: list[Plugin] = [
        *_head(markdown_extensions, highlight),
        I18n(locales=list(locales), default_locale=default_locale),
        Permalink(),
        Collections(by_tag=True, by_folder=True, group_by="locale"),
    ]
    # One paginated index per locale: /<locale>/ lists that locale's posts.
    plugins.extend(
        Listing(
            collection=f"{locale}/{posts_dir}",
            base_url=f"/{locale}/",
            title=locale,
            page_size=page_size,
        )
        for locale in locales
    )
    # A single tag listing covers every (locale, tag) pair via the :locale token.
    plugins.append(Listing(kind="tag", base_url="/:locale/tags/:name/", title=":name"))
    plugins.append(Navigation(mode="frontmatter", group_by="locale"))
    if rss:
        plugins.extend(
            Rss(collection=f"{locale}/{posts_dir}", path=f"{locale}/feed.xml")
            for locale in locales
        )
    plugins.extend(
        _extras(
            sitemap=sitemap,
            minify=minify,
            robots=robots,
            markdown_pages=markdown_pages,
        )
    )
    if seo:
        plugins.append(Seo(schema_type="BlogPosting"))
    if root_redirect:
        plugins.append(Redirects(rules={"/": f"/{default_locale}/"}))
    plugins.extend(_tail(template_dir, clean))
    return plugins


def i18n_docs(
    *,
    locales: Sequence[str],
    default_locale: str,
    markdown_extensions: Sequence[str] = (),
    template_dir: str = "layouts",
    clean: bool = True,
    sitemap: bool = False,
    minify: bool = False,
    robots: bool = False,
    markdown_pages: bool = False,
    seo: bool = True,
    highlight: bool = False,
    root_redirect: bool = True,
) -> list[Plugin]:
    """Multilingual technical documentation: ``docs()`` partitioned per locale.

    Sources live under ``<locale>/...``; the locale segment is kept in the URL
    (``/vi/guide/install/``). Each locale gets its own folder sidebar with
    prev/next, rooted at the locale's content (the locale segment is not shown as
    a node). With ``root_redirect`` the bare ``/`` redirects to the default
    locale's home.
    """

    if default_locale not in locales:
        raise ValueError(
            f"default_locale {default_locale!r} is not in locales {list(locales)}"
        )

    plugins: list[Plugin] = [
        *_head(markdown_extensions, highlight),
        I18n(locales=list(locales), default_locale=default_locale),
        Permalink(),
        Collections(by_tag=False, by_folder=True, group_by="locale"),
        Navigation(mode="folder", sequential=True, group_by="locale"),
        *_extras(
            sitemap=sitemap,
            minify=minify,
            robots=robots,
            markdown_pages=markdown_pages,
        ),
        *([Seo(schema_type="Article")] if seo else []),
        *([Redirects(rules={"/": f"/{default_locale}/"})] if root_redirect else []),
        *_tail(template_dir, clean),
    ]
    return plugins


def site(
    *,
    markdown_extensions: Sequence[str] = (),
    template_dir: str = "layouts",
    clean: bool = True,
    sitemap: bool = False,
    minify: bool = False,
    robots: bool = False,
    markdown_pages: bool = False,
    seo: bool = True,
    highlight: bool = False,
) -> list[Plugin]:
    return [
        *_head(markdown_extensions, highlight),
        Permalink(),
        Navigation(mode="frontmatter"),
        *_extras(
            sitemap=sitemap,
            minify=minify,
            robots=robots,
            markdown_pages=markdown_pages,
        ),
        *([Seo(schema_type="Article")] if seo else []),
        *_tail(template_dir, clean),
    ]
