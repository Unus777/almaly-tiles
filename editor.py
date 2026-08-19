#!/usr/bin/env python3
"""Локальный редактор медиа: http://localhost:8787

Показывает все рабочие артикулы, даёт загружать/удалять фото, менять порядок
и обложку, и публиковать изменения на сайт. Правит файлы в photos/<АРТИКУЛ>/.
"""
import json, re, shutil, subprocess, urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import build

ROOT = Path(__file__).parent
PHOTOS = ROOT / "photos"
EXT = {".jpg", ".jpeg", ".png", ".webp"}
PORT = 8787


def photos_of(art):
    d = PHOTOS / art
    return sorted(p.name for p in d.iterdir() if p.suffix.lower() in EXT) if d.is_dir() else []


def renumber(art, order):
    """Переименовывает файлы в 01..NN по заданному порядку (через временные имена)."""
    d = PHOTOS / art
    order = [f for f in order if (d / f).exists()]
    order += [f for f in photos_of(art) if f not in order]
    tmp = []
    for i, name in enumerate(order, 1):
        t = d / f"tmp_{i:02d}{Path(name).suffix.lower()}"
        (d / name).rename(t)
        tmp.append(t)
    for t in tmp:
        t.rename(d / t.name[4:])


def safe_art(art):
    if not re.fullmatch(r"[A-Za-z0-9]+", art or ""):
        raise ValueError("плохой артикул")
    return art


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def send(self, code, body=b"", ctype="application/json"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def json(self, obj, code=200):
        self.send(code, json.dumps(obj, ensure_ascii=False).encode(), "application/json; charset=utf-8")

    def do_GET(self):
        url = urllib.parse.urlparse(self.path)
        q = urllib.parse.parse_qs(url.query)
        if url.path in ("/", "/index.html"):
            return self.send(200, (ROOT / "editor.html").read_bytes(), "text/html; charset=utf-8")
        if url.path == "/dnd.js":
            return self.send(200, (ROOT / "docs" / "dnd.js").read_bytes(), "application/javascript; charset=utf-8")
        if url.path == "/api/tiles":
            tiles = [{"art": t["art"], "name": t["name"], "format": t["format"],
                      "surface": t["surface"], "photos": photos_of(t["art"])}
                     for t in build.catalog()]
            return self.json({"tiles": tiles})
        if url.path == "/api/photo":
            art, f = safe_art(q.get("art", [""])[0]), Path(q.get("f", [""])[0]).name
            p = PHOTOS / art / f
            if p.is_file() and p.suffix.lower() in EXT:
                return self.send(200, p.read_bytes(), "image/" + p.suffix.lstrip(".").replace("jpg", "jpeg"))
            return self.send(404)
        self.send(404)

    def do_POST(self):
        url = urllib.parse.urlparse(self.path)
        q = urllib.parse.parse_qs(url.query)
        body = self.rfile.read(int(self.headers.get("Content-Length") or 0))
        try:
            if url.path == "/api/upload":                      # тело = сам файл
                art = safe_art(q["art"][0])
                ext = Path(q.get("name", ["x.jpg"])[0]).suffix.lower()
                if ext not in EXT:
                    return self.json({"error": f"формат {ext} не поддерживается"}, 400)
                d = PHOTOS / art
                d.mkdir(parents=True, exist_ok=True)
                n = len(photos_of(art)) + 1
                (d / f"{n:02d}{ext}").write_bytes(body)
                renumber(art, photos_of(art))
                return self.json({"photos": photos_of(art)})

            data = json.loads(body or b"{}")
            if url.path == "/api/delete":
                art = safe_art(data["art"])
                p = PHOTOS / art / Path(data["file"]).name
                if p.is_file():
                    p.unlink()
                renumber(art, photos_of(art))
                return self.json({"photos": photos_of(art)})

            if url.path == "/api/order":
                art = safe_art(data["art"])
                renumber(art, [Path(f).name for f in data["order"]])
                return self.json({"photos": photos_of(art)})

            if url.path == "/api/publish":
                r = subprocess.run(["./publish.sh"], cwd=ROOT, capture_output=True, text=True)
                return self.json({"ok": r.returncode == 0, "log": (r.stdout + r.stderr)[-4000:]})
        except Exception as e:                                   # ошибку показываем в интерфейсе
            return self.json({"error": str(e)}, 400)
        self.send(404)


if __name__ == "__main__":
    print(f"Редактор медиа: http://localhost:{PORT}  (Ctrl+C — выход)")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
