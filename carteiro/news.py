from dataclasses import dataclass
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen
import html
import xml.etree.ElementTree as ET


class NewsSearchError(Exception):
    """Falha ao consultar ou interpretar o feed de noticias."""


@dataclass(frozen=True)
class NewsItem:
    title: str
    link: str
    source: str
    published: str
    summary: str


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)


def _text_content(value: str) -> str:
    parser = _TextExtractor()
    parser.feed(html.unescape(value))
    return " ".join(" ".join(parser.parts).split())


def _child_text(element: ET.Element, name: str) -> str:
    for child in element:
        if child.tag.rsplit("}", 1)[-1] == name:
            return "".join(child.itertext()).strip()
    return ""


def _valid_article_url(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def search_news(query: str, limit: int = 8, timeout: float = 15) -> list[NewsItem]:
    params = urlencode(
        {"q": query, "hl": "pt-BR", "gl": "BR", "ceid": "BR:pt-419"}
    )
    request = Request(
        f"https://news.google.com/rss/search?{params}",
        headers={"User-Agent": "Carteiro/1.0 (+https://news.google.com/)"},
    )

    try:
        with urlopen(request, timeout=timeout) as response:
            feed = response.read()
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        raise NewsSearchError(f"Nao foi possivel consultar o feed de noticias: {exc}") from exc

    try:
        root = ET.fromstring(feed)
    except ET.ParseError as exc:
        raise NewsSearchError("O feed de noticias retornou um XML invalido.") from exc

    items: list[NewsItem] = []
    for entry in root.iter():
        if entry.tag.rsplit("}", 1)[-1] != "item":
            continue

        title = _text_content(_child_text(entry, "title"))
        link = _child_text(entry, "link")
        if not title or not _valid_article_url(link):
            continue

        source = _child_text(entry, "source") or "Fonte nao informada"
        items.append(
            NewsItem(
                title=title,
                link=link,
                source=source,
                published=_child_text(entry, "pubDate"),
                summary=_text_content(_child_text(entry, "description")),
            )
        )
        if len(items) >= limit:
            break

    if not items:
        raise NewsSearchError(
            "Nenhuma noticia foi encontrada para essa busca. Tente outros termos."
        )
    return items
