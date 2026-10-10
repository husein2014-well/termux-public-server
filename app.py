#!/usr/bin/env python3
import argparse
import hashlib
import hmac
import http.server
import json
import secrets
import socketserver
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlparse

HOME = Path(__file__).resolve().parent
WWW = HOME / "www"
RUN = HOME / "run"
KEY_FILE = RUN / "access.key"
STATE_FILE = RUN / "access.json"
COOKIE_NAME = "tps_auth"


def parse_duration(value):
    value = str(value or "").strip().lower()
    if value in ("never", "none", "0"):
        return None
    units = {"m": 60, "h": 3600, "d": 86400}
    if len(value) < 2 or value[-1] not in units or not value[:-1].isdigit():
        raise ValueError("Gunakan format seperti 1h, 24h, 7d, 30d, atau never")
    seconds = int(value[:-1]) * units[value[-1]]
    if seconds < 60 or seconds > 365 * 86400:
        raise ValueError("Masa aktif harus antara 1 menit dan 365 hari")
    return int(time.time()) + seconds


def iso_expiry(expires_at):
    if not expires_at:
        return "Tidak kedaluwarsa"
    return datetime.fromtimestamp(expires_at, timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M %Z")


def load_state():
    RUN.mkdir(parents=True, exist_ok=True)
    if STATE_FILE.exists():
        try:
            state = json.loads(STATE_FILE.read_text())
            if state.get("key"):
                return state
        except (ValueError, OSError):
            pass
    legacy = KEY_FILE.read_text().strip() if KEY_FILE.exists() else ""
    state = {"key": legacy or secrets.token_urlsafe(24), "expires_at": None}
    save_state(state)
    return state


def save_state(state):
    RUN.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2) + "\n")
    STATE_FILE.chmod(0o600)
    KEY_FILE.write_text(state["key"] + "\n")
    KEY_FILE.chmod(0o600)


def ensure_key():
    return load_state()["key"]


def new_key(duration=None):
    state = {"key": secrets.token_urlsafe(24), "expires_at": parse_duration(duration) if duration else None}
    save_state(state)
    return state


def set_expiry(duration):
    state = load_state()
    state["expires_at"] = parse_duration(duration)
    save_state(state)
    return state


def is_expired(state):
    return bool(state.get("expires_at") and time.time() >= state["expires_at"])


def token(key):
    return hmac.new(key.encode(), b"termux-public-server-auth", hashlib.sha256).hexdigest()


def page(title, body):
    return f"""<!doctype html><html lang=\"id\"><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"><title>{title}</title><style>body{{font:16px system-ui,sans-serif;max-width:680px;margin:3rem auto;padding:0 1rem;color:#17202a}}input,select,button{{font:inherit;padding:.65rem;margin:.25rem 0}}input{{width:min(100%,30rem)}}button{{cursor:pointer}}.card{{background:#f2f5f7;padding:1rem;border-radius:.5rem;margin:1rem 0}}code{{word-break:break-all}}</style>{body}</html>"""


class Server(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


class Handler(http.server.BaseHTTPRequestHandler):
    server_version = "TermuxPublicServer/1.1"

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
        state = load_state()
        parsed = urlparse(self.path)
        if parsed.path == "/logout":
            self.send_html(page("Keluar", "<p>Sesi dihapus.</p><a href=\"/\">Masuk lagi</a>"), headers={"Set-Cookie": f"{COOKIE_NAME}=; Max-Age=0; HttpOnly; SameSite=Lax", "Refresh": "1; url=/"})
            return
        if parsed.path == "/login" and self.command == "POST":
            if is_expired(state):
                self.send_html(page("Key kedaluwarsa", "<h1>Key kedaluwarsa</h1><p>Minta access key baru kepada admin.</p>"), 403)
                return
            supplied = self.form().get("key", [""])[0].strip()
            if hmac.compare_digest(supplied, state["key"]):
                self.send_html(page("Berhasil", "<p>Login berhasil.</p><a href=\"/\">Lanjut</a>"), headers={"Set-Cookie": f"{COOKIE_NAME}={token(state['key'])}; Max-Age=86400; HttpOnly; SameSite=Lax", "Refresh": "1; url=/"})
            else:
                self.send_html(page("Key salah", "<h1>Key salah</h1><a href=\"/\">Coba lagi</a>"), 401)
            return
        authenticated = not is_expired(state) and hmac.compare_digest(self.headers.get("Cookie", "").split(f"{COOKIE_NAME}=", 1)[-1].split(";", 1)[0], token(state["key"]))
        if not authenticated:
            message = "Access key sudah kedaluwarsa." if is_expired(state) else "Masukkan access key untuk melanjutkan."
            self.send_html(page("Masukkan key", f"<h1>Server terkunci</h1><p>{message}</p><form method=post action=/login><input name=key type=password placeholder=\"Access key\" required autofocus><br><button>Masuk</button></form>"), 401)
            return
        target = WWW / "index.html" if parsed.path in ("", "/") else (WWW / parsed.path.lstrip("/")).resolve()
        if WWW.resolve() not in target.parents and target != WWW.resolve():
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
            form = self.form()
            duration = form.get("duration", ["never"])[0]
            try:
                state = new_key(duration)
                body = f"<h1>Key baru dibuat</h1><p>Key lama sudah tidak berlaku.</p><p>Masa aktif: <b>{iso_expiry(state['expires_at'])}</b></p><p><input readonly value=\"{state['key']}\" onclick=\"this.select()\"></p><a href=\"/\">Kembali</a>"
                self.send_html(page("Key baru", body))
            except ValueError as exc:
                self.send_html(page("Input salah", f"<h1>Input salah</h1><p>{exc}</p><a href=\"/\">Kembali</a>"), 400)
            return
        if self.path == "/settings" and self.command == "POST":
            form = self.form()
            try:
                state = set_expiry(form.get("duration", ["never"])[0])
                self.send_html(page("Masa aktif diperbarui", f"<h1>Masa aktif diperbarui</h1><p>Key tetap sama.</p><p>Berlaku sampai: <b>{iso_expiry(state['expires_at'])}</b></p><a href=\"/\">Kembali</a>"))
            except ValueError as exc:
                self.send_html(page("Input salah", f"<h1>Input salah</h1><p>{exc}</p><a href=\"/\">Kembali</a>"), 400)
            return
        state = load_state()
        body = f"<h1>Kelola access key</h1><div class=card><p>Key aktif:</p><p><input readonly value=\"{state['key']}\" onclick=\"this.select()\"></p><p>Berlaku sampai: <b>{iso_expiry(state['expires_at'])}</b></p></div><div class=card><h2>Atur masa aktif key saat ini</h2><form method=post action=/settings><select name=duration><option value=1h>1 jam</option><option value=24h>24 jam</option><option value=7d>7 hari</option><option value=30d>30 hari</option><option value=never>Tanpa kedaluwarsa</option></select><br><button>Simpan masa aktif</button></form></div><div class=card><h2>Buat key baru</h2><form method=post action=/generate><select name=duration><option value=1h>1 jam</option><option value=24h>24 jam</option><option value=7d>7 hari</option><option value=30d>30 hari</option><option value=never>Tanpa kedaluwarsa</option></select><br><button>Buat key baru</button></form></div><p>Admin hanya listen di <code>127.0.0.1</code> dan tidak melewati tunnel publik.</p>"
        self.send_html(page("Admin key", body))

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
    parser.add_argument("--generate-key", nargs="?", const="never")
    parser.add_argument("--show-key", action="store_true")
    parser.add_argument("--show-info", action="store_true")
    parser.add_argument("--set-expiry")
    args = parser.parse_args()
    if args.generate_key is not None:
        state = new_key(args.generate_key)
        print(f"{state['key']}\nBerlaku sampai: {iso_expiry(state['expires_at'])}")
        return
    if args.show_key:
        print(load_state()["key"])
        return
    if args.show_info:
        state = load_state()
        print(f"key: {state['key']}\nexpires: {iso_expiry(state['expires_at'])}\nexpired: {'yes' if is_expired(state) else 'no'}")
        return
    if args.set_expiry:
        state = set_expiry(args.set_expiry)
        print(f"Berlaku sampai: {iso_expiry(state['expires_at'])}")
        return
    load_state()
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
