from datetime import datetime
from html import escape
from pathlib import Path
import re
import unicodedata
import uuid

from .news import NewsItem


_MASCOT = """<svg class="mascot" viewBox="0 0 120 120" role="img" aria-labelledby="mascot-title">
  <title id="mascot-title">Pombo Carteiro, o mascote do jornal</title>
  <path d="M28 47 17 32l22 7c8-12 31-15 43-4l19-8-7 21c7 13 4 33-8 42H38c-15-9-19-26-10-43Z" fill="#fff7e8" stroke="#142c3d" stroke-width="4" stroke-linejoin="round"/>
  <path d="m38 40 13-9 12 9-13 7Z" fill="#c74331" stroke="#142c3d" stroke-width="3" stroke-linejoin="round"/>
  <path d="m84 50 21-3-17 13" fill="#e2a537" stroke="#142c3d" stroke-width="3" stroke-linejoin="round"/>
  <circle cx="72" cy="52" r="3.5" fill="#142c3d"/>
  <path d="m47 77 12 10 13-10 12 10" fill="none" stroke="#d9a45a" stroke-width="3"/>
  <path d="M31 91h61v17H31z" rx="3" fill="#c74331" stroke="#142c3d" stroke-width="4"/>
  <path d="m31 93 30 12 31-12" fill="none" stroke="#142c3d" stroke-width="3"/>
</svg>"""


def _edition_slug(query: str) -> str:
    normalized = unicodedata.normalize("NFKD", query)
    ascii_query = normalized.encode("ascii", "ignore").decode("ascii").lower()
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_query).strip("-")
    return slug[:48] or "noticias"


def create_edition(query: str, articles: list[NewsItem], output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().astimezone().strftime("%Y%m%d-%H%M%S-%f")
    filename = f"carteiro-{timestamp}-{_edition_slug(query)}-{uuid.uuid4().hex[:8]}.html"
    destination = output_dir / filename
    generated_at = datetime.now().astimezone().strftime("%d/%m/%Y às %H:%M %Z")

    stories = []
    for index, article in enumerate(articles, start=1):
        published = (
            f'<time>{escape(article.published)}</time>'
            if article.published
            else ""
        )
        summary = (
            f"<p>{escape(article.summary)}</p>"
            if article.summary
            else '<p class="no-summary">A fonte não forneceu um resumo.</p>'
        )
        stories.append(
            f"""<article class="story">
  <span class="story-number">{index:02d}</span>
  <h2><a href="{escape(article.link, quote=True)}" target="_blank" rel="noopener noreferrer">{escape(article.title)}</a></h2>
  <p class="byline">{escape(article.source)} {published}</p>
  {summary}
  <a class="read-more" href="{escape(article.link, quote=True)}" target="_blank" rel="noopener noreferrer">Ler na fonte ↗</a>
</article>"""
        )

    document = f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Edicao do Carteiro sobre {escape(query, quote=True)}">
  <title>{escape(query)} — O Carteiro</title>
  <style>
    :root {{ color-scheme: light; --ink: #142c3d; --red: #c74331; --paper: #fffaf0; --muted: #625f56; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: #e9e2d5; color: var(--ink); font-family: Georgia, "Times New Roman", serif; }}
    .paper {{ max-width: 1000px; min-height: 100vh; margin: 28px auto; padding: 30px clamp(20px, 5vw, 58px) 54px; background: var(--paper); box-shadow: 0 8px 32px #142c3d22; }}
    .masthead {{ display: flex; align-items: center; justify-content: space-between; gap: 20px; border-bottom: 4px double var(--ink); padding-bottom: 16px; }}
    .brand {{ display: flex; align-items: center; gap: 15px; }}
    .mascot {{ width: 86px; height: 86px; flex: 0 0 auto; }}
    .eyebrow, .edition, .byline, .read-more, .story-number, .notice {{ font-family: Arial, sans-serif; }}
    .eyebrow {{ margin: 0 0 3px; color: var(--red); font-size: .75rem; font-weight: 700; letter-spacing: .18em; text-transform: uppercase; }}
    h1 {{ margin: 0; font-size: clamp(2.3rem, 7vw, 4.6rem); letter-spacing: -.06em; line-height: .95; }}
    .edition {{ text-align: right; color: var(--muted); font-size: .8rem; line-height: 1.6; }}
    .edition strong {{ color: var(--ink); }}
    .headline {{ padding: 28px 0 23px; border-bottom: 1px solid #b8ad9a; }}
    .headline h2 {{ margin: 0 0 9px; font-size: clamp(1.8rem, 5vw, 3rem); line-height: 1.05; }}
    .headline p {{ margin: 0; color: var(--muted); font: 1rem/1.5 Arial, sans-serif; }}
    .notice {{ margin: 18px 0 2px; padding: 11px 14px; background: #f1e9d9; color: #48483f; font-size: .8rem; line-height: 1.5; }}
    .stories {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 0 32px; }}
    .story {{ position: relative; padding: 23px 0 21px 36px; border-bottom: 1px solid #cfc5b5; break-inside: avoid; }}
    .story-number {{ position: absolute; top: 25px; left: 0; color: var(--red); font-size: .75rem; font-weight: 700; }}
    .story h2 {{ margin: 0 0 8px; font-size: 1.32rem; line-height: 1.2; }}
    a {{ color: inherit; text-decoration-color: #c7433177; text-underline-offset: 3px; }}
    a:hover {{ color: var(--red); }}
    .byline {{ margin: 0 0 10px; color: var(--muted); font-size: .73rem; }}
    .byline time {{ margin-left: 7px; }}
    .story > p:not(.byline) {{ margin: 0 0 12px; font-size: .96rem; line-height: 1.5; }}
    .story .no-summary {{ color: var(--muted); font-style: italic; }}
    .read-more {{ color: var(--red); font-size: .76rem; font-weight: 700; text-decoration: none; }}
    footer {{ margin-top: 30px; padding-top: 12px; border-top: 4px double var(--ink); color: var(--muted); font: .75rem/1.5 Arial, sans-serif; text-align: center; }}
    @media (max-width: 650px) {{ .paper {{ margin: 0; padding-top: 20px; }} .masthead {{ align-items: flex-start; }} .mascot {{ width: 62px; height: 62px; }} .edition {{ font-size: .68rem; }} .stories {{ grid-template-columns: 1fr; }} }}
    @media print {{ body {{ background: white; }} .paper {{ max-width: none; margin: 0; box-shadow: none; }} a {{ text-decoration: none; }} }}
  </style>
</head>
<body>
  <main class="paper">
    <header class="masthead">
      <div class="brand">{_MASCOT}<div><p class="eyebrow">Notícias entregues fresquinhas</p><h1>O Carteiro</h1></div></div>
      <div class="edition"><strong>EDIÇÃO ESPECIAL</strong><br>{escape(generated_at)}<br>Busca: {escape(query)}</div>
    </header>
    <section class="headline">
      <h2>O que está acontecendo: {escape(query)}</h2>
      <p>Uma seleção de notícias recentes encontradas para sua busca.</p>
    </section>
    <p class="notice">Os títulos, resumos e links são fornecidos pelo feed de notícias. Para ler cada matéria completa, acesse o site da publicação original.</p>
    <section class="stories" aria-label="Notícias encontradas">
      {"".join(stories)}
    </section>
    <footer>O Carteiro · Seu jornal, entregue em HTML · As notícias pertencem às respectivas fontes.</footer>
  </main>
</body>
</html>
"""
    with destination.open("x", encoding="utf-8", newline="\n") as edition_file:
        edition_file.write(document)
    return destination
