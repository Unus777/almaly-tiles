#!/usr/bin/env python3
"""Обновляет data/*.csv из Google-таблицы."""
import urllib.request
from pathlib import Path

SHEET = "1dqYgo6PI2ttiQgbF8QhLzOI19VSFSEdthK_xDX5Mk04"
TABS = {"60x60": "0", "60x120": "725867454"}

DATA = Path(__file__).parent / "data"
DATA.mkdir(exist_ok=True)

for name, gid in TABS.items():
    url = f"https://docs.google.com/spreadsheets/d/{SHEET}/export?format=csv&gid={gid}"
    data = urllib.request.urlopen(url, timeout=30).read()
    assert data.lstrip().startswith("Артикулы".encode()), f"{name}: таблица недоступна"
    (DATA / f"{name}.csv").write_bytes(data)
    print(f"{name}: {len(data.splitlines()) - 1} строк")
