from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from carteiro.news import NewsItem, NewsSearchError, search_news
from carteiro.newspaper import create_edition


class NewsSearchTests(unittest.TestCase):
    def test_parses_rss_and_uses_requested_limit(self) -> None:
        feed = b'''<?xml version="1.0"?>
        <rss><channel>
          <item>
            <title>Clima &amp; cidades</title>
            <link>https://example.com/noticia</link>
            <source>Jornal Exemplo</source>
            <pubDate>Mon, 12 Oct 2026 10:00:00 GMT</pubDate>
            <description>&lt;p&gt;Resumo &amp;amp; contexto&lt;/p&gt;</description>
          </item>
          <item>
            <title>Segunda noticia</title>
            <link>https://example.com/segunda</link>
          </item>
        </channel></rss>'''

        class Response:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                return None

            def read(self):
                return feed

        with patch("carteiro.news.urlopen", return_value=Response()):
            items = search_news("clima", limit=1)

        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].title, "Clima & cidades")
        self.assertEqual(items[0].source, "Jornal Exemplo")
        self.assertEqual(items[0].summary, "Resumo & contexto")

    def test_rejects_items_with_non_web_links(self) -> None:
        feed = b'''<rss><channel><item>
        <title>Noticia</title><link>javascript:alert(1)</link>
        </item></channel></rss>'''

        class Response:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                return None

            def read(self):
                return feed

        with patch("carteiro.news.urlopen", return_value=Response()):
            with self.assertRaisesRegex(NewsSearchError, "Nenhuma noticia"):
                search_news("assunto")


class EditionTests(unittest.TestCase):
    def test_creates_distinct_safe_html_editions(self) -> None:
        article = NewsItem(
            title='<Alerta> "especial"',
            link="https://example.com/noticia?a=1&b=2",
            source="Fonte & Jornal",
            published="",
            summary="<script>alert('x')</script>Resumo & detalhes",
        )
        with tempfile.TemporaryDirectory() as temporary_dir:
            output_dir = Path(temporary_dir) / "edicoes"
            first = create_edition('<tema> & teste', [article], output_dir)
            second = create_edition('<tema> & teste', [article], output_dir)

            self.assertNotEqual(first, second)
            self.assertTrue(first.is_file())
            self.assertTrue(second.is_file())
            document = first.read_text(encoding="utf-8")

        self.assertIn('lang="pt-BR"', document)
        self.assertIn("Pombo Carteiro", document)
        self.assertIn('&lt;Alerta&gt; &quot;especial&quot;', document)
        self.assertIn("Fonte &amp; Jornal", document)
        self.assertIn('&lt;script&gt;alert(&#x27;x&#x27;)&lt;/script&gt;', document)
        self.assertIn('rel="noopener noreferrer"', document)
        self.assertNotIn("<script>alert", document)


if __name__ == "__main__":
    unittest.main()
