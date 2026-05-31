"""End-to-end integration tests running full presets through the Builder."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from pyssg.builder import Builder
from pyssg.config import Config
from pyssg_cli.presets import blog, docs, i18n_blog, i18n_docs


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class BlogIntegrationTest(unittest.TestCase):
    def test_blog_build_produces_posts_index_and_tags(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            content = root / "content"
            layouts = root / "layouts"
            out = root / "public"

            write(
                content / "about.md", "---\ntitle: About\nmenu: main\n---\nAbout us\n"
            )
            write(
                content / "blog" / "first.md",
                "---\ntitle: First\ndate: 2024-01-01\ntags: [python]\n---\nHello\n",
            )
            write(
                content / "blog" / "second.md",
                "---\ntitle: Second\ndate: 2024-02-01\n"
                "tags: [python, web]\n---\nWorld\n",
            )

            write(
                layouts / "default.html",
                "<article>{{ page.title }}|{{ content }}</article>",
            )
            write(
                layouts / "list.html",
                "<ul>{% for item in page.entries %}"
                "<li><a href='{{ item.url }}'>{{ item.title }}</a></li>"
                "{% endfor %}</ul>",
            )

            config = Config(src=content, out=out, plugins=blog())
            Builder(config).run()

            # Standalone page with pretty URL.
            self.assertTrue((out / "about" / "index.html").exists())
            # Individual posts.
            self.assertTrue((out / "blog" / "first" / "index.html").exists())
            # Blog index listing.
            blog_index = (out / "blog" / "index.html").read_text()
            self.assertIn("/blog/first/", blog_index)
            self.assertIn("/blog/second/", blog_index)
            # Tag pages, one per tag.
            self.assertTrue((out / "tags" / "python" / "index.html").exists())
            self.assertTrue((out / "tags" / "web" / "index.html").exists())
            python_page = (out / "tags" / "python" / "index.html").read_text()
            self.assertIn("/blog/first/", python_page)
            self.assertIn("/blog/second/", python_page)

    def test_blog_pagination(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            content = root / "content"
            layouts = root / "layouts"
            out = root / "public"

            for i in range(5):
                write(
                    content / "blog" / f"post{i}.md",
                    f"---\ntitle: Post {i}\ndate: 2024-01-0{i + 1}\n---\nBody {i}\n",
                )
            write(layouts / "default.html", "{{ content }}")
            write(
                layouts / "list.html",
                "p{{ page.paginator.number }}/{{ page.paginator.total_pages }}",
            )

            config = Config(src=content, out=out, plugins=blog(page_size=2))
            Builder(config).run()

            self.assertEqual((out / "blog" / "index.html").read_text(), "p1/3")
            self.assertEqual(
                (out / "blog" / "page" / "2" / "index.html").read_text(), "p2/3"
            )
            self.assertEqual(
                (out / "blog" / "page" / "3" / "index.html").read_text(), "p3/3"
            )


class I18nBlogIntegrationTest(unittest.TestCase):
    def test_multilingual_build(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            content = root / "content"
            layouts = root / "layouts"
            out = root / "public"

            post = "---\ntitle: {t}\ndate: 2024-01-01\ntags: [python]\n---\nBody\n"
            write(content / "vi" / "posts" / "oauth2.md", post.format(t="OAuth2 VI"))
            write(content / "en" / "posts" / "oauth2.md", post.format(t="OAuth2 EN"))
            write(
                content / "vi" / "about.md",
                "---\ntitle: Gioi thieu\nmenu: main\n---\nAbout\n",
            )

            # The post layout prints the locale and the language-switcher links.
            write(
                layouts / "default.html",
                "L:{{ page.locale }}|"
                "{% for t in page.translations %}"
                "{{ t.locale }}={{ t.url }}{% if t.current %}*{% endif %};"
                "{% endfor %}|{{ content }}",
            )
            write(
                layouts / "list.html",
                "MENU[{% for n in menus['main:' + page.locale] %}"
                "{{ n.url }}{% endfor %}]"
                "{% for item in page.entries %}{{ item.url }};{% endfor %}",
            )

            config = Config(
                src=content,
                out=out,
                plugins=i18n_blog(locales=["vi", "en"], default_locale="vi"),
            )
            Builder(config).run()

            # The default locale (vi) renders at the root; others are prefixed.
            self.assertTrue((out / "posts" / "oauth2" / "index.html").exists())
            self.assertTrue((out / "en" / "posts" / "oauth2" / "index.html").exists())

            # The post page carries its locale and a switcher to the other locale.
            vi_post = (out / "posts" / "oauth2" / "index.html").read_text()
            self.assertIn("L:vi|", vi_post)
            self.assertIn("vi=/posts/oauth2/*;", vi_post)
            self.assertIn("en=/en/posts/oauth2/;", vi_post)

            # The default locale's index is the site root; others at /<locale>/.
            vi_index = (out / "index.html").read_text()
            self.assertIn("/posts/oauth2/;", vi_index)
            self.assertNotIn("/en/posts/oauth2/;", vi_index)
            # The menu is the locale-specific one.
            self.assertIn("MENU[/about/]", vi_index)

            # Tag pages and feeds: default at root, others prefixed.
            self.assertTrue((out / "tags" / "python" / "index.html").exists())
            self.assertTrue((out / "en" / "tags" / "python" / "index.html").exists())
            self.assertTrue((out / "feed.xml").exists())
            self.assertTrue((out / "en" / "feed.xml").exists())

            # No root redirect: the bare root is the default locale's home.
            self.assertFalse((out / "vi" / "index.html").exists())


class I18nDocsIntegrationTest(unittest.TestCase):
    def test_per_locale_sidebar_is_rooted_at_locale(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            content = root / "content"
            layouts = root / "layouts"
            out = root / "public"

            for locale in ("en", "vi"):
                write(
                    content / locale / "index.md",
                    f"---\ntitle: Home {locale}\n---\nH\n",
                )
                write(
                    content / locale / "guide" / "index.md",
                    f"---\ntitle: Guide {locale}\norder: 1\n---\nG\n",
                )
                write(
                    content / locale / "guide" / "install.md",
                    f"---\ntitle: Install {locale}\norder: 1\n---\nI\n",
                )
                write(
                    content / locale / "guide" / "usage.md",
                    f"---\ntitle: Usage {locale}\norder: 2\n---\nU\n",
                )

            # Sidebar prints node urls; the locale segment must NOT appear as a
            # top-level node (no empty-url "En"/"Vi" wrapper).
            nav = (
                "NAV[{% for n in menus['main:' + page.locale] %}"
                "{{ n.title }}:{{ n.url }}>"
                "{% for c in n.children %}{{ c.title }}:{{ c.url }},{% endfor %}"
                "{% endfor %}]"
            )
            prevnext = (
                "{% if page.prev %}P:{{ page.prev.url }}{% endif %}"
                "{% if page.next %}N:{{ page.next.url }}{% endif %}"
            )
            write(layouts / "default.html", f"{nav}{prevnext}|{{{{ content }}}}")

            config = Config(
                src=content,
                out=out,
                plugins=i18n_docs(locales=["en", "vi"], default_locale="en"),
            )
            Builder(config).run()

            # The default locale (en) renders at the root.
            install = (out / "guide" / "install" / "index.html").read_text()
            # The sidebar is rooted at the "guide" folder, not a redundant "en".
            self.assertIn("Guide en:/guide/", install)
            self.assertIn("Install en:/guide/install/", install)
            self.assertNotIn("/guide/install/", install.split("NAV[")[0])
            # Sequential prev/next stays within the locale.
            usage = (out / "guide" / "usage" / "index.html").read_text()
            self.assertIn("P:/guide/install/", usage)
            # vi (non-default) pages exist and keep their prefix.
            self.assertTrue((out / "vi" / "guide" / "install" / "index.html").exists())
            # No root redirect: the default locale's home is the site root.
            self.assertTrue((out / "index.html").exists())
            self.assertFalse((out / "en" / "index.html").exists())


class DocsIntegrationTest(unittest.TestCase):
    def test_docs_build_with_sidebar_and_prev_next(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            content = root / "content"
            layouts = root / "layouts"
            out = root / "public"

            write(content / "index.md", "---\ntitle: Home\n---\nWelcome\n")
            write(
                content / "guide" / "index.md",
                "---\ntitle: Guide\norder: 1\n---\nGuide\n",
            )
            write(
                content / "guide" / "install.md",
                "---\ntitle: Install\norder: 1\n---\nInstall\n",
            )
            write(
                content / "guide" / "usage.md",
                "---\ntitle: Usage\norder: 2\n---\nUsage\n",
            )

            nav = (
                "{% for node in menus.main %}{{ node.title }}"
                "{% for c in node.children %}>{{ c.title }}{% endfor %}{% endfor %}"
            )
            prevnext = "{% if page.prev %}P:{{ page.prev.title }}{% endif %}"
            write(layouts / "default.html", f"NAV[{nav}]{prevnext}|{{{{ content }}}}")

            config = Config(src=content, out=out, plugins=docs())
            Builder(config).run()

            install = (out / "guide" / "install" / "index.html").read_text()
            # Sidebar shows the Guide section with its children.
            self.assertIn("Guide>Install>Usage", install)
            # Usage follows Install in sequential order.
            usage = (out / "guide" / "usage" / "index.html").read_text()
            self.assertIn("P:Install", usage)


if __name__ == "__main__":
    unittest.main()
