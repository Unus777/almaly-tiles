#!/usr/bin/env python3
"""Одноразовый импорт: раскладывает исходные фото по папкам артикулов photos/<АРТИКУЛ>/.
Запускать повторно безопасно — уже скопированные файлы пропускаются."""
import csv, shutil, unicodedata
from pathlib import Path

SRC = Path("/Users/yunus_mac/Documents/Старс керамик (Плитки)/Фото для озон")
ROOT = Path(__file__).parent
DST = ROOT / "photos"

# папки, чьё имя не совпадает с названием из таблицы
ALIASES = {
    "ЛИАМ КРЕМ МАТОВЫЙ": "ЛИАМ КРЕМ",
    "ЛИАМ КРЕМ ГАЛЯНЦЕЫЙ": "ЛИАМ КРЕМ ПОЛИШ",
    "ДЖОЗЕФИНА": "ДЖОЗЕФИНА ПОЛИШ",
    "АЙССНОВ": "АЙССНОУ",
}

def norm(s):
    s = unicodedata.normalize("NFC", s)
    return " ".join(s.upper().replace("Ё", "Е").replace("*", "X").split())

def load_catalog():
    out = {}
    for f in (ROOT / "data").glob("*.csv"):
        for row in csv.DictReader(f.open(encoding="utf-8")):
            art, name, fmt = row["Артикулы"].strip(), row["НАЗВАНИЯ"].strip(), norm(row["ФОРМАТ"])
            if art and name:
                out[(norm(name), fmt)] = art
    return out

def main():
    cat = load_catalog()
    unmatched = []
    for fmt_dir in SRC.iterdir():
        if not fmt_dir.is_dir():
            continue
        fmt = norm(fmt_dir.name)
        for tile_dir in sorted(fmt_dir.iterdir()):
            if not tile_dir.is_dir():
                continue
            name = norm(tile_dir.name)
            name = ALIASES.get(name, name)
            art = cat.get((name, fmt))
            if not art:
                unmatched.append(f"{fmt_dir.name}/{tile_dir.name}")
                continue
            target = DST / art
            target.mkdir(parents=True, exist_ok=True)
            for i, src in enumerate(sorted(p for p in tile_dir.iterdir()
                                           if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp", ".heic"}), 1):
                dst = target / f"{i:02d}{src.suffix.lower()}"
                if not dst.exists():
                    shutil.copy2(src, dst)
            print(f"{art:12} {name:25} {len(list(target.iterdir()))} фото")
    if unmatched:
        print("\nНе нашёл в таблице (проверь названия):", *unmatched, sep="\n  ")

if __name__ == "__main__":
    main()
