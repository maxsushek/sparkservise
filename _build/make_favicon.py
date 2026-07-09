#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генерит favicon-набор из ЛОГОТИПА SPARK (wordmark на белой плитке).
Источник — logo.png; берём верхнюю строку «SPARK» (с фирменной красной молнией-A),
мелкую подпись «РЕМОНТ·СЕРВИС» отбрасываем — в иконке она нечитаема.
Пишет в корень: favicon.svg (embed-raster), favicon.ico (16/32/48), apple-touch-icon.png (180),
web-app-manifest-192/512 (maskable), site.webmanifest. Супер-сэмпл ×8 → LANCZOS."""
import os, json, base64, io
from PIL import Image, ImageDraw

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SS = 8
LOGO = Image.open(os.path.join(REPO, "logo.png")).convert("RGBA")
W, H = LOGO.size
WORDMARK = LOGO.crop((0, 2, W, 44))   # верхняя строка «SPARK», без яблочка/подписи
WHITE = (255, 255, 255, 255)

def tile(size, full_bleed=False, pad_frac=0.16, radius_frac=0.18):
    S = size * SS
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if full_bleed:
        d.rectangle([0, 0, S, S], fill=WHITE)
    else:
        d.rounded_rectangle([0, 0, S - 1, S - 1], radius=int(S * radius_frac), fill=WHITE)
    avail = int(S * (1 - 2 * pad_frac))
    sw, sh = WORDMARK.size
    sc = min(avail / sw, avail / sh)
    nw, nh = int(sw * sc), int(sh * sc)
    r = WORDMARK.resize((nw, nh), Image.LANCZOS)
    img.alpha_composite(r, ((S - nw) // 2, (S - nh) // 2))
    return img.resize((size, size), Image.LANCZOS)

def p(name): return os.path.join(REPO, name)

# favicon.ico — многоразмерный (таб + фавикон в Google-выдаче), плитка со скруглением
tile(48).save(p("favicon.ico"), sizes=[(16, 16), (32, 32), (48, 48)])
# apple-touch — 180 full-bleed белый (iOS сам скругляет)
tile(180, full_bleed=True).convert("RGB").save(p("apple-touch-icon.png"))
# PWA maskable — белая плитка до краёв, wordmark в safe-зоне центра
tile(192, full_bleed=True).save(p("web-app-manifest-192x192.png"))
tile(512, full_bleed=True).save(p("web-app-manifest-512x512.png"))

# favicon.svg — вектор-обёртка с встроенным растром логотипа (источник растровый, чистого вектора нет)
buf = io.BytesIO(); tile(256).save(buf, "PNG")
b64 = base64.b64encode(buf.getvalue()).decode()
svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="100" height="100">'
       '<image href="data:image/png;base64,' + b64 + '" x="0" y="0" width="100" height="100"/></svg>\n')
open(p("favicon.svg"), "w", encoding="utf-8").write(svg)

manifest = {
    "name": "SPARK — сервисный центр Apple в Одессе",
    "short_name": "SPARK",
    "icons": [
        {"src": "/web-app-manifest-192x192.png", "sizes": "192x192", "type": "image/png", "purpose": "maskable"},
        {"src": "/web-app-manifest-512x512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
        {"src": "/favicon.svg", "type": "image/svg+xml", "sizes": "any"},
    ],
    "theme_color": "#ffffff", "background_color": "#ffffff",
    "display": "standalone", "lang": "ru", "start_url": "/",
}
open(p("site.webmanifest"), "w", encoding="utf-8").write(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
print("favicon (из логотипа): svg, ico, apple-touch, 192, 512, manifest -> корень")
