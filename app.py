#!/usr/bin/env python3
import argparse
import hashlib
import hmac
import http.server
import secrets
import shutil
import socketserver
from pathlib import Path
from urllib.parse import parse_qs, urlparse

HOME = Path(__file__).resolve().parent
WWW = HOME / "www"
KEY_FILE = HOME / "run" / "access.key"
COOKIE_NAME = "tps_auth"


def ensure_key():
    KEY_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not KEY_FILE.exists() or not KEY_FILE.read_text().strip():
        KEY_FILE.write_text(secrets.token_urlsafe(24) + "\n")
        KEY_FILE.chmod(0o600)
    return KEY_FILE.read_text().strip()


def new_key():
    KEY_FILE.parent.mkdir(parents=True, exist_ok=True)
    key = secrets.token_urlsafe(24)
    KEY_FILE.write_text(key + "\n")
    KEY_FILE.chmod(0o600)
    return key


def token(key):
    return hmac.new(key.encode(), b"termux-public-server-auth", hashlib.sha256).hexdigest()


def page(title, body):
    return f"""<!doctype html><html lang=\"id\"><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"><title>{title}</title><style>body{{font:16px system-ui,sans-serif;max-width:680px;margin:3rem auto;padding:0 1rem;color:#17202a}}input,button{{font:inherit;padding:.65rem;margin:.25rem 0}}input{{width:min(100%,28rem)}}button{{cursor:pointer}}.card{{background:#f2f5f7;padding:1rem;border-radius:.5rem}}</style>{body}</html>"""


class Server(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


class Handler(http.server.BaseHTTPRequestHandler):
    server_version = "TermuxPublicServer/1.0"

    def send_html(self, html, status=200, headers=None):
        data = html.encode()
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        for key, value in (headers or {}).items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(data)

    def form(self):
        length = int(self.headers.get("Content-Length", "0"))
        return parse_qs(self.rfile.read(length).decode("utf-8", "replace"))

    def public(self):
        key = ensure_key()
        parsed = urlparse(self.path)
        if parsed.path == "/logout":
            self.send_html(page("Keluar", "<p>Sesi dihapus.</p><a href=\"/\">Masuk lagi</a>"), headers={"Set-Cookie": f"{COOKIE_NAME}=; Max-Age=0; HttpOnly; SameSite=Lax", "Refresh": "1; url=/"})
            return
        authenticated = hmac.compare_digest(self.headers.get("Cookie", "").split(f"{COOKIE_NAME}=", 1)[-1].split(";", 1)[0], token(key))
        if parsed.path == "/login" and self.command == "POST":
            supplied = self.form().get("key", [""])[0].strip()
            if hmac.compare_digest(supplied, key):
                self.send_html(page("Berhasil", "<p>Login berhasil.</p><a href=\"/\">Lanjut</a>"), headers={"Set-Cookie": f"{COOKIE_NAME}={token(key)}; Max-Age=86400; HttpOnly; SameSite=Lax", "Refresh": "1; url=/"})
            else:
                self.send_html(page("Key salah", "<h1>Key salah</h1><a href=\"/\">Coba lagi</a>"), 401)
            return
        if not authenticated:
            self.send_html(page("Masukkan key", "<h1>Server terkunci</h1><p>Masukkan access key untuk melanjutkan.</p><form method=post action=/login><input name=key type=password placeholder=\"Access key\" required autofocus><br><button>Masuk</button></form>"), 401)
            return
        if parsed.path == "/" or parsed.path == "":
            target = WWW / "index.html"
        else:
            target = (WWW / parsed.path.lstrip("/")).resolve()
            if WWW.resolve() not in target.parents:
                self.send_error(403)
                return
        if target.is_file():
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8" if target.suffix == ".html" else "application/octet-stream")
            self.send_header("Content-Length", str(target.stat().st_size))
            self.end_headers()
            self.wfile.write(target.read_bytes())
        else:
            self.send_error(404)

    def admin(self):
        if self.client_address[0] not in ("127.0.0.1", "::1"):
            self.send_error(403, "Admin hanya tersedia di perangkat ini")
            return
        if self.path == "/generate" and self.command == "POST":
            key = new_key()
            self.send_html(page("Key baru", f"<h1>Key baru dibuat</h1><p>Simpan key ini. Key lama sudah tidak berlaku.</p><p><input readonly value=\"{key}\" onclick=\"this.select()\"></p><a href=\"/\">Kembali</a>"))
            return
        current = ensure_key()
        masked = current[:4] + "..." + current[-4:]
        self.send_html(page("Admin key", f"<h1>Kelola access key</h1><div class=card><p>Key aktif: <code>{masked}</code></p><form method=post action=/generate><button>Buat key baru</button></form></div><p>Halaman ini hanya listen di <code>127.0.0.1</code> dan tidak melewati tunnel publik.</p>"))

    def do_GET(self):
        (self.admin if self.server.mode == "admin" else self.public)()

    def do_POST(self):
        (self.admin if self.server.mode == "admin" else self.public)()

    def log_message(self, fmt, *args):
        print(fmt % args, flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--public", action="store_true")
    parser.add_argument("--admin", action="store_true")
    parser.add_argument("--bind", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--generate-key", action="store_true")
    args = parser.parse_args()
    if args.generate_key:
        print(new_key())
        return
    ensure_key()
    mode = "admin" if args.admin else "public"
    server = Server((args.bind, args.port), Handler)
    server.mode = mode
    print(f"{mode} server listening on {args.bind}:{args.port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
