#!/data/data/com.termux/files/usr/bin/bash
set -Eeuo pipefail

REPO_URL="${TPS_REPO_URL:-https://github.com/husein2014-well/termux-public-server.git}"
INSTALL_DIR="${TPS_HOME:-$HOME/.termux-public-server}"
BIN_DIR="$PREFIX/bin"

if [[ "${PREFIX:-}" != *com.termux* ]]; then
  echo "Error: script ini harus dijalankan di Termux." >&2
  exit 1
fi

pkg update -y
pkg install -y git curl python tmux

if [[ -d "$INSTALL_DIR/.git" ]]; then
  git -C "$INSTALL_DIR" pull --ff-only
else
  rm -rf "$INSTALL_DIR"
  git clone "$REPO_URL" "$INSTALL_DIR"
fi

mkdir -p "$INSTALL_DIR/www" "$INSTALL_DIR/logs" "$INSTALL_DIR/run"
if [[ ! -f "$INSTALL_DIR/www/index.html" && -f "$INSTALL_DIR/server/www/index.html" ]]; then
  cp "$INSTALL_DIR/server/www/index.html" "$INSTALL_DIR/www/index.html"
fi
cp "$INSTALL_DIR/bin/tps" "$BIN_DIR/tps"
cp "$INSTALL_DIR/bin/tps-public" "$BIN_DIR/tps-public"
cp "$INSTALL_DIR/bin/tps-admin" "$BIN_DIR/tps-admin"
chmod 755 "$BIN_DIR/tps" "$BIN_DIR/tps-public" "$BIN_DIR/tps-admin"
printf 'export TPS_HOME=%q\n' "$INSTALL_DIR" > "$INSTALL_DIR/env"
printf '\nInstalasi selesai. Jalankan:\n  source %q\n  tps start --public\n' "$INSTALL_DIR/env"
