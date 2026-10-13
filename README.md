# O Carteiro

Ferramenta de terminal que pesquisa notícias em português e cria um jornal HTML novo por busca. Exibe títulos, resumos disponíveis, fonte e links para matérias originais; não copia o conteúdo completo dos sites. Requer Python 3.10+ e internet para buscar notícias.

## Instalação rápida

Os instaladores baixam o projeto deste repositório, criam um ambiente isolado e instalam o comando `carteiro`.

### Bash

```bash
curl -fLO https://raw.githubusercontent.com/7deo/carteiro/main/install.sh
less install.sh
bash install.sh
```

Requer `curl` e `tar`. O comando instala em `~/.local/share/carteiro`; se necessário, adicione `~/.local/bin` ao PATH.

### PowerShell

```powershell
Invoke-WebRequest https://raw.githubusercontent.com/7deo/carteiro/main/install.ps1 -OutFile install.ps1
Get-Content .\install.ps1
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

Instala em `%LOCALAPPDATA%\Carteiro` e adiciona o comando ao PATH do usuário. Abra um novo terminal depois.

## Uso

```text
carteiro "assunto da busca" [--limite N] [--saida PASTA]
```

Exemplo: `carteiro "tecnologia no Brasil" --limite 5`. O limite aceita de 1 a 20 notícias (padrão 8); as edições únicas são salvas em `edicoes/` por padrão. Cada arquivo é responsivo, imprimível e traz o mascote Pombo Carteiro.

Para instalar manualmente a partir do código: `python -m pip install .`. Testes: `python3 -m unittest discover -s tests -v`.
