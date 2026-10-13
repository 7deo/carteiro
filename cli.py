import argparse
from pathlib import Path
import sys

from . import __version__
from .news import NewsSearchError, search_news
from .newspaper import create_edition


_MASCOT = r'''
       .-""""-.
      /  .--.  \
     |  /    \  |     O CARTEIRO
     | |  ()  | |     Noticia boa
      \ \____/ /      chega em casa!
       '------'
      /|      |\
     /_|______|_\
'''


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="carteiro",
        description="Pesquisa noticias e entrega uma edicao de jornal em HTML.",
        epilog='Exemplo: carteiro "meio ambiente no Brasil"',
    )
    parser.add_argument("busca", help="assunto ou palavras-chave para pesquisar")
    parser.add_argument(
        "--limite",
        type=int,
        default=8,
        metavar="N",
        help="numero maximo de noticias (padrao: 8; faixa: 1 a 20)",
    )
    parser.add_argument(
        "--saida",
        type=Path,
        default=Path("edicoes"),
        metavar="PASTA",
        help="pasta onde salvar as edicoes (padrao: ./edicoes)",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    query = args.busca.strip()
    if not query:
        parser.error("a busca nao pode estar vazia")
    if not 1 <= args.limite <= 20:
        parser.error("--limite deve estar entre 1 e 20")

    print(_MASCOT)
    print(f'Pesquisando noticias sobre "{query}"...')
    try:
        articles = search_news(query, args.limite)
        edition_path = create_edition(query, articles, args.saida)
    except NewsSearchError as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"Nao foi possivel salvar a edicao: {exc}", file=sys.stderr)
        return 1

    print(f"{len(articles)} noticia(s) entregues.")
    print(f"Jornal salvo em: {edition_path.resolve()}")
    return 0
