#!/usr/bin/env bash
set -euo pipefail

REPOSITORY="7deo/carteiro"
BRANCH="${CARTEIRO_BRANCH:-main}"
INSTALL_ROOT="${CARTEIRO_HOME:-${XDG_DATA_HOME:-"$HOME/.local/share"}/carteiro}"
BIN_DIR="${CARTEIRO_BIN_DIR:-"$HOME/.local/bin"}"
ARCHIVE_URL="https://github.com/${REPOSITORY}/archive/refs/heads/${BRANCH}.tar.gz"

if ! command -v curl >/dev/null 2>&1 || ! command -v tar >/dev/null 2>&1; then
    printf '%s\n' "Erro: o instalador precisa de curl e tar." >&2
    exit 1
fi

PYTHON=""
for candidate in python3 python; do
    if command -v "$candidate" >/dev/null 2>&1 &&
        "$candidate" -c 'import sys; raise SystemExit(sys.version_info < (3, 10))'; then
        PYTHON="$(command -v "$candidate")"
        break
    fi
done

if [[ -z "$PYTHON" ]]; then
    printf '%s\n' "Erro: instale Python 3.10 ou superior e tente novamente." >&2
    exit 1
fi

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

printf 'Baixando O Carteiro de %s...\n' "$REPOSITORY"
curl --fail --silent --show-error --location "$ARCHIVE_URL" -o "$TMP_DIR/carteiro.tar.gz"
mkdir "$TMP_DIR/source"
tar -xzf "$TMP_DIR/carteiro.tar.gz" --strip-components=1 -C "$TMP_DIR/source"

mkdir -p "$INSTALL_ROOT" "$BIN_DIR"
"$PYTHON" -m venv "$INSTALL_ROOT/venv"
"$INSTALL_ROOT/venv/bin/python" -m pip install --disable-pip-version-check "$TMP_DIR/source"

cat > "$BIN_DIR/carteiro" <<EOF
#!/usr/bin/env bash
exec "$INSTALL_ROOT/venv/bin/python" -m carteiro "\$@"
EOF
chmod +x "$BIN_DIR/carteiro"

printf '\nInstalacao concluida. Execute: carteiro "noticias do Brasil"\n'
case ":${PATH}:" in
    *":${BIN_DIR}:"*) ;;
    *) printf 'Se o comando nao for encontrado, adicione %s ao PATH e abra um novo terminal.\n' "$BIN_DIR" ;;
esac
