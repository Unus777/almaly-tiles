#!/bin/bash
# Пересобрать сайт и выложить на GitHub Pages
set -e
cd "$(dirname "$0")"
python3 build.py
git add -A
git commit -m "Обновление каталога $(date +%Y-%m-%d)" || echo "нет изменений"
git push
echo "Готово: $(python3 -c 'import json;print(json.load(open("config.json"))["base_url"])')"
