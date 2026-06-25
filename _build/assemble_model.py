#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
assemble_model.py — генератор spoke-страниц моделей iPhone (remont-iphone/<slug>/).

Цены берутся НАПРЯМУЮ из var TIERS в remont-iphone/index.html (единый источник).
Спеки моделей (порт, ProMotion, матрица, биометрия, True Tone, влагозащита) — в SPEC.
Прайс/карточки/FAQ генерируются по фактическим услугам модели (у старых моделей —
кнопка Home/Touch ID вместо Face ID, у 7/SE — без замены заднего стекла, и т.д.).

Перелинковка КЛАСТЕРНАЯ (не «все-со-всеми»): каждая модель → свой модельный ряд +
топ-модели + хаб. Хаб линкует все модели.

Как добавить модель: добавь спеку в SPEC (id совпадает с TIERS) → python3 _build/assemble_model.py.
iPhone 17 Pro Max НЕ генерируется (ручная страница с реальным фото).
Если в папке есть <slug>.webp — он покажется как фото; иначе SVG-макет.
"""
import os, re, json

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "https://sparkservice.od.ua"
OG_IMAGE = BASE + "/og/spark.jpg"

# ---- Спеки моделей. id == id в TIERS. (slug, port, promotion, display, biometric, truetone, water)
# biometric: 'faceid' (X и новее) | 'touchid' (8 и старше + SE)
SPEC = {
 "17p":   ("iPhone 17 Pro",      "iphone-17-pro",      "USB-C",     True,  "OLED", "faceid", True, True),
 "17air": ("iPhone 17 Air",      "iphone-17-air",      "USB-C",     True,  "OLED", "faceid", True, True),
 "17":    ("iPhone 17",          "iphone-17",          "USB-C",     True,  "OLED", "faceid", True, True),
 "16pm":  ("iPhone 16 Pro Max",  "iphone-16-pro-max",  "USB-C",     True,  "OLED", "faceid", True, True),
 "16p":   ("iPhone 16 Pro",      "iphone-16-pro",      "USB-C",     True,  "OLED", "faceid", True, True),
 "16pl":  ("iPhone 16 Plus",     "iphone-16-plus",     "USB-C",     False, "OLED", "faceid", True, True),
 "16":    ("iPhone 16",          "iphone-16",          "USB-C",     False, "OLED", "faceid", True, True),
 "15pm":  ("iPhone 15 Pro Max",  "iphone-15-pro-max",  "USB-C",     True,  "OLED", "faceid", True, True),
 "15p":   ("iPhone 15 Pro",      "iphone-15-pro",      "USB-C",     True,  "OLED", "faceid", True, True),
 "15pl":  ("iPhone 15 Plus",     "iphone-15-plus",     "USB-C",     False, "OLED", "faceid", True, True),
 "15":    ("iPhone 15",          "iphone-15",          "USB-C",     False, "OLED", "faceid", True, True),
 "14pm":  ("iPhone 14 Pro Max",  "iphone-14-pro-max",  "Lightning", True,  "OLED", "faceid", True, True),
 "14p":   ("iPhone 14 Pro",      "iphone-14-pro",      "Lightning", True,  "OLED", "faceid", True, True),
 "14pl":  ("iPhone 14 Plus",     "iphone-14-plus",     "Lightning", False, "OLED", "faceid", True, True),
 "14":    ("iPhone 14",          "iphone-14",          "Lightning", False, "OLED", "faceid", True, True),
 "13pm":  ("iPhone 13 Pro Max",  "iphone-13-pro-max",  "Lightning", True,  "OLED", "faceid", True, True),
 "13p":   ("iPhone 13 Pro",      "iphone-13-pro",      "Lightning", True,  "OLED", "faceid", True, True),
 "13":    ("iPhone 13",          "iphone-13",          "Lightning", False, "OLED", "faceid", True, True),
 "13m":   ("iPhone 13 mini",     "iphone-13-mini",     "Lightning", False, "OLED", "faceid", True, True),
 "12pm":  ("iPhone 12 Pro Max",  "iphone-12-pro-max",  "Lightning", False, "OLED", "faceid", True, True),
 "12p":   ("iPhone 12 Pro",      "iphone-12-pro",      "Lightning", False, "OLED", "faceid", True, True),
 "12":    ("iPhone 12",          "iphone-12",          "Lightning", False, "OLED", "faceid", True, True),
 "12m":   ("iPhone 12 mini",     "iphone-12-mini",     "Lightning", False, "OLED", "faceid", True, True),
 "11pm":  ("iPhone 11 Pro Max",  "iphone-11-pro-max",  "Lightning", False, "OLED", "faceid", True, True),
 "11p":   ("iPhone 11 Pro",      "iphone-11-pro",      "Lightning", False, "OLED", "faceid", True, True),
 "11":    ("iPhone 11",          "iphone-11",          "Lightning", False, "LCD",  "faceid", True, True),
 "xs-max":("iPhone XS Max",      "iphone-xs-max",      "Lightning", False, "OLED", "faceid", True, True),
 "xs":    ("iPhone XS",          "iphone-xs",          "Lightning", False, "OLED", "faceid", True, True),
 "xr":    ("iPhone XR",          "iphone-xr",          "Lightning", False, "LCD",  "faceid", True, True),
 "x":     ("iPhone X",           "iphone-x",           "Lightning", False, "OLED", "faceid", True, True),
 "8p":    ("iPhone 8 Plus",      "iphone-8-plus",      "Lightning", False, "LCD",  "touchid", True, True),
 "8":     ("iPhone 8",           "iphone-8",           "Lightning", False, "LCD",  "touchid", True, True),
 "7p":    ("iPhone 7 Plus",      "iphone-7-plus",      "Lightning", False, "LCD",  "touchid", False, True),
 "7":     ("iPhone 7",           "iphone-7",           "Lightning", False, "LCD",  "touchid", False, True),
 "se3":   ("iPhone SE 3 (2022)", "iphone-se-2022",     "Lightning", False, "LCD",  "touchid", True, True),
 "se2":   ("iPhone SE 2 (2020)", "iphone-se-2020",     "Lightning", False, "LCD",  "touchid", True, True),
 "se1":   ("iPhone SE (2016)",   "iphone-se-2016",     "Lightning", False, "LCD",  "touchid", False, False),
}

# Кластеры для перелинковки (модельные ряды)
SERIES = [
 ["17pm","17p","17air","17"], ["16pm","16p","16pl","16"], ["15pm","15p","15pl","15"],
 ["14pm","14p","14pl","14"], ["13pm","13p","13","13m"], ["12pm","12p","12","12m"],
 ["11pm","11p","11"], ["xs-max","xs","xr","x"], ["8p","8","7p","7","se3","se2","se1"],
]
ANCHORS = ["11","13","14","16","15","15pm","16pm"]  # топ-спрос + флагманы

# Прайс: порядок услуг + время. Услуга включается, только если есть в ценах модели.
SVC_META = [
 ("Замена экрана (дисплея)", "Замена экрана (дисплея)", "30-60 мин"),
 ("Замена аккумулятора", "Замена аккумулятора", "30-40 мин"),
 ("Замена заднего стекла", "Замена заднего стекла", "1-2 часа"),
 ("Не заряжается (разъём)", "Не заряжается (__PORT__ разъём)", "30-50 мин"),
 ("После воды", "После воды", "от 2 часов"),
 ("Замена камеры", "Замена камеры", "40-60 мин"),
 ("Динамик / микрофон", "Динамик / микрофон", "30-50 мин"),
 ("Face ID", "Face ID", "1-3 часа"),
 ("Кнопка Home / Touch ID", "Кнопка Home / Touch ID", "40-60 мин"),
 ("Ремонт платы", "Ремонт платы", "1-3 дня"),
]

# Иконки + тексты карточек «виды ремонта» по ключу услуги
ICONS = {
 "Замена экрана (дисплея)": '<rect x="5" y="2" width="14" height="20" rx="3"/><line x1="12" y1="18" x2="12" y2="18.01"/>',
 "Замена аккумулятора": '<rect x="6" y="7" width="12" height="10" rx="1"/><line x1="10" y1="17" x2="10" y2="21"/><line x1="14" y1="17" x2="14" y2="21"/><line x1="8" y1="21" x2="16" y2="21"/><path d="M7 7V5a5 5 0 0110 0v2"/>',
 "Замена заднего стекла": '<rect x="2" y="7" width="20" height="14" rx="2" ry="2"/><path d="M16 3h-8l-2 4h12z"/>',
 "Не заряжается (разъём)": '<path d="M5 4h4l1.5 5-2 1.2a12 12 0 005.3 5.3l1.2-2 5 1.5v4a2 2 0 01-2 2A16 16 0 013 6a2 2 0 012-2z"/>',
 "После воды": '<path d="M12 3s6 7 6 11a6 6 0 11-12 0c0-4 6-11 6-11z"/>',
 "Замена камеры": '<path d="M23 19a2 2 0 01-2 2H3a2 2 0 01-2-2V8a2 2 0 012-2h4l2-3h6l2 3h4a2 2 0 012 2z"/><circle cx="12" cy="13" r="4"/>',
 "Динамик / микрофон": '<polygon points="11 5 6 9 2 9 2 15 6 15 11 19"/><path d="M19.07 4.93a10 10 0 010 14.14M15.54 8.46a5 5 0 010 7.08"/>',
 "Face ID": '<circle cx="12" cy="12" r="3"/><path d="M12 2v2m0 16v2M4.93 4.93l1.41 1.41m11.32 11.32l1.41 1.41M2 12h2m16 0h2M4.93 19.07l1.41-1.41m11.32-11.32l1.41-1.41"/>',
 "Кнопка Home / Touch ID": '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="3"/>',
 "Ремонт платы": '<path d="M14.7 6.3a1 1 0 000 1.4l1.6 1.6a1 1 0 001.4 0l3.77-3.77a6 6 0 01-7.94 7.94l-6.91 6.91a2.12 2.12 0 01-3-3l6.91-6.91a6 6 0 017.94-7.94l-3.76 3.76z"/>',
}

# Уникальный per-model абзац (типичные поломки поколения). Факты выверены.
NOTES = {
 "iphone-17-pro": "iPhone 17 Pro (2025) — титановый Pro с USB-C, дисплеем ProMotion 120 Гц и продвинутой системой камер. В ремонт чаще всего попадает с разбитым OLED-дисплеем, износом аккумулятора и проблемами телеобъектива. Восстанавливаем 120 Гц, Dynamic Island и Face ID.",
 "iphone-17-air": "iPhone 17 Air (2025) — ультратонкий корпус и одна основная камера. Из-за тонкости чаще встречаются деформации корпуса и трещины OLED-дисплея; также меняем аккумулятор и ремонтируем разъём USB-C. Сохраняем ProMotion и Face ID.",
 "iphone-17": "iPhone 17 (2025) — базовая модель, впервые с дисплеем ProMotion 120 Гц и разъёмом USB-C. Типичный ремонт: замена OLED-дисплея и аккумулятора, ремонт USB-C, восстановление после попадания воды.",
 "iphone-16-pro-max": "iPhone 16 Pro Max (2024) — флагман с крупнейшим экраном ProMotion 120 Гц и продвинутой системой камер. В ремонт идёт с разбитым OLED-дисплеем, износом батареи и неисправностями камер, включая 5× телефото. Восстанавливаем ProMotion, Dynamic Island и Camera Control.",
 "iphone-16-pro": "iPhone 16 Pro (2024) — титановый корпус, кнопка «Действие» и сенсорная Camera Control. Чаще всего меняем дорогой OLED ProMotion-дисплей, аккумулятор и ремонтируем камеры; восстанавливаем кнопку Camera Control и разъём USB-C.",
 "iphone-16-plus": "iPhone 16 Plus (2024) — большой 6,7″ OLED-экран (60 Гц), ёмкая батарея, USB-C и кнопка Camera Control. В ремонт идёт с трещинами дисплея, износом аккумулятора и неисправным USB-C.",
 "iphone-16": "iPhone 16 (2024) получил кнопку «Действие» и сенсорную Camera Control. Частые случаи: замена OLED-дисплея, аккумулятора, ремонт разъёма USB-C и восстановление новой кнопки Camera Control. Меняем заднее стекло без замены всего корпуса.",
 "iphone-15-pro-max": "iPhone 15 Pro Max (2023) — единственный в линейке с перископической камерой 5× и титановым корпусом. Чаще всего меняем дорогой OLED-дисплей ProMotion, аккумулятор и ремонтируем телеобъектив 5× (сложный оптический узел), а также разъём USB-C и заднее стекло.",
 "iphone-15-pro": "iPhone 15 Pro (2023) — титановый корпус, разъём USB-C и настраиваемая кнопка «Действие». В ремонт попадает с разбитым дисплеем ProMotion 120 Гц, износом аккумулятора и неисправным USB-C. Сохраняем 120 Гц, True Tone и Face ID.",
 "iphone-15-plus": "iPhone 15 Plus (2023) — большой экран и аккумулятор, разъём USB-C и Dynamic Island. Частые случаи: замена OLED-дисплея, батареи и ремонт нового порта USB-C после попадания пыли или влаги.",
 "iphone-15": "iPhone 15 (2023) — первый базовый iPhone с разъёмом USB-C и Dynamic Island. Типичные обращения: замена дисплея и аккумулятора, ремонт нового порта USB-C, замена заднего стекла с цветным напылением.",
 "iphone-14-pro-max": "iPhone 14 Pro Max (2022) — крупнейший экран и батарея линейки 14. В ремонт идёт с трещинами большого OLED-дисплея, деградацией аккумулятора (Always-On ускоряет износ) и проблемами 48-Мп камеры и телеобъектива. Восстанавливаем ProMotion 120 Гц и Dynamic Island.",
 "iphone-14-pro": "iPhone 14 Pro (2022) — первый iPhone с «островом» Dynamic Island и постоянно включённым экраном Always-On. Частые поломки: разбитый дисплей ProMotion 120 Гц, ускоренный износ батареи, выход из строя основной 48-Мп камеры. Меняем дисплей с сохранением Dynamic Island и True Tone.",
 "iphone-14-plus": "iPhone 14 Plus (2022) — крупный 6,7″ OLED-экран при доступной цене, разъём Lightning. Типичный ремонт — замена дисплея, аккумулятора и основной камеры, восстановление после воды.",
 "iphone-14": "iPhone 14 (2022) внешне близок к 13-му, но с улучшенным охлаждением и экстренным вызовом SOS. Типичный ремонт — замена аккумулятора, OLED-дисплея и основной камеры, восстановление после влаги.",
 "iphone-13-pro-max": "iPhone 13 Pro Max (2021) — флагман с дисплеем ProMotion 120 Гц и самой ёмкой батареей своего поколения. Чаще всего попадает к нам с разбитым дорогим OLED-дисплеем, просадкой автономности и неисправностями телеобъектива (3× оптический зум). Восстанавливаем ProMotion и систему из трёх камер.",
 "iphone-13-pro": "iPhone 13 Pro (2021) — компактный флагман с ProMotion 120 Гц и тройной камерой. В ремонт попадает с разбитым OLED-дисплеем, просадкой автономности и неисправностями телеобъектива (3× зум). Восстанавливаем 120 Гц и Face ID.",
 "iphone-13": "iPhone 13 (2021) получил увеличенный аккумулятор, но к 2026 многие устройства уже просят его замены. Частые случаи — замена разбитого OLED-дисплея, ремонт после попадания воды, замена основной и сверхширокоугольной камер. Сохраняем заводскую влагозащиту IP68.",
 "iphone-13-mini": "iPhone 13 mini (2021) — компактный 5,4″ OLED. Из-за малого размера батарея изнашивается быстрее, поэтому замена аккумулятора — одна из самых частых услуг, наряду с заменой дисплея и ремонтом после воды.",
 "iphone-12-pro-max": "iPhone 12 Pro Max (2020) — крупнейший экран линейки 12 с большой OLED-матрицей, MagSafe и сканером LiDAR. Чаще всего меняем дорогой дисплей, аккумулятор и ремонтируем камеры; восстанавливаем заднее стекло с магнитами MagSafe.",
 "iphone-12-pro": "iPhone 12 Pro (2020) — OLED Super Retina XDR, MagSafe и тройная камера с LiDAR. В ремонт идёт с разбитым дисплеем, износом батареи и проблемами камер. Восстанавливаем Face ID и влагозащиту.",
 "iphone-12": "iPhone 12 (2020) — первый iPhone с плоскими гранями, MagSafe и защитой Ceramic Shield. Типичные неисправности к 2026: износ аккумулятора, трещины OLED-дисплея при ударах по углам, пропадание сети после падений. Восстанавливаем Face ID и меняем заднее стекло с сохранением магнитов MagSafe.",
 "iphone-12-mini": "iPhone 12 mini (2020) — компактный 5,4″ OLED с MagSafe. Маленький аккумулятор изнашивается быстрее обычного, поэтому замена батареи в топе обращений вместе с заменой дисплея и ремонтом разъёма Lightning.",
 "iphone-11-pro-max": "iPhone 11 Pro Max (2019) — флагман с OLED-дисплеем и рекордной для своего времени автономностью. К 2026 чаще всего просит замены аккумулятора и дисплея; также меняем тройную камеру и ремонтируем плату.",
 "iphone-11-pro": "iPhone 11 Pro (2019) — компактный OLED-флагман с тройной камерой. Типичные обращения к 2026: износ аккумулятора, замена дорогого OLED-дисплея, ремонт после воды. В отличие от обычного iPhone 11, здесь OLED-матрица.",
 "iphone-11": "iPhone 11 (2019 год) — одна из самых частых моделей в нашем сервисе: к 2026 году аккумулятор у большинства устройств деградировал, ёмкость опускается ниже 80% и телефон выключается на холоде. Чаще всего меняем батарею и дисплей — у iPhone 11 ЖК-матрица (LCD), её замена заметно дешевле, чем OLED у Pro-версий. Также популярны замена основной камеры и чистка разъёма Lightning.",
 "iphone-xs-max": "iPhone XS Max (2018) — большой OLED-экран и Face ID. Популярная модель в ремонте: к 2026 батарея сильно деградировала, частая замена аккумулятора и разбитого OLED-дисплея, ремонт разъёма Lightning и после воды.",
 "iphone-xs": "iPhone XS (2018) — OLED Super Retina, Face ID, защита IP68. Чаще всего меняем аккумулятор (деградация за годы), разбитый дисплей и заднее стекло, восстанавливаем после попадания воды.",
 "iphone-xr": "iPhone XR (2018) — самый популярный iPhone 2018 года с ЖК-экраном (LCD) Liquid Retina и Face ID. ЖК-дисплей дешевле в замене, чем OLED; частые услуги — замена батареи, дисплея и ремонт после воды.",
 "iphone-x": "iPhone X (2017) — первый iPhone с Face ID и OLED-экраном, без кнопки Home. К 2026 почти всем нужна замена аккумулятора; часто меняем дорогой OLED-дисплей и ремонтируем систему Face ID (сложная микропайка).",
 "iphone-8-plus": "iPhone 8 Plus (2017) — последний крупный iPhone с кнопкой Home и Touch ID, ЖК-экран и стеклянная задняя крышка. Частые услуги: замена аккумулятора, дисплея, заднего стекла и ремонт кнопки Home / Touch ID.",
 "iphone-8": "iPhone 8 (2017) — кнопка Home с Touch ID, ЖК-дисплей и стеклянная спинка с поддержкой беспроводной зарядки. Чаще всего меняем аккумулятор и дисплей, ремонтируем кнопку Home и заднее стекло.",
 "iphone-7-plus": "iPhone 7 Plus (2016) — двойная камера, кнопка Home с Touch ID, алюминиевый корпус без стеклянной крышки. Типичные ремонты: замена аккумулятора и ЖК-дисплея, ремонт кнопки Home и разъёма Lightning, восстановление после воды.",
 "iphone-7": "iPhone 7 (2016) — сенсорная кнопка Home с Touch ID и ЖК-экран, влагозащита IP67. Самые частые услуги к 2026 — замена изношенного аккумулятора и дисплея, ремонт кнопки Home и нижнего шлейфа зарядки.",
 "iphone-se-2022": "iPhone SE 3 (2022) — современная начинка A15 в классическом корпусе с кнопкой Home и Touch ID, ЖК-дисплей. Частые обращения: замена аккумулятора, ЖК-дисплея и ремонт кнопки Home / Touch ID.",
 "iphone-se-2020": "iPhone SE 2 (2020) — кнопка Home с Touch ID и ЖК-экран 4,7″. Популярная бюджетная модель; чаще всего меняем аккумулятор и дисплей, ремонтируем разъём Lightning и кнопку Home.",
 "iphone-se-2016": "iPhone SE (2016) — компактный 4″ корпус, кнопка Home с Touch ID, ЖК-экран. Старая, но живучая модель: к 2026 почти всем нужна замена аккумулятора; также меняем дисплей и ремонтируем разъём зарядки.",
}

def money(n): return f"{n:,}".replace(",", " ")
def rng(p): return f"{money(p[0])} — {money(p[1])} ₴"
def esc_attr(s): return s.replace('"', "&quot;")
def jstr(s): return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'

def translit(name):
    return (name.replace("iPhone", "айфон").replace("Pro Max", "про макс").replace("Pro", "про")
                .replace("Plus", "плюс").replace("mini", "мини").replace("Air", "эйр")
                .replace("SE", "эс и").replace("XS Max", "икс эс макс").replace("XS", "икс эс")
                .replace("XR", "икс эр"))

def parse_tiers():
    s = open(os.path.join(REPO, "remont-iphone", "index.html"), encoding="utf-8").read()
    body = re.search(r'var TIERS=\[(.*?)\];', s, re.S).group(1)
    rows = re.findall(r"\{id:'([^']+)',label:'([^']+)',prices:\{([^}]*)\},time:'([^']+)'\}", body)
    out = {}
    for tid, label, pr, time in rows:
        out[tid] = json.loads('{' + pr.replace("'", '"') + '}')
    return out

PRICES_ALL = parse_tiers()

def render(tid):
    name, slug, port, promo, disp, bio, truetone, water = SPEC[tid]
    pr = PRICES_ALL[tid]
    canon = f"{BASE}/remont-iphone/{slug}/"
    batt_low = pr["Замена аккумулятора"][0]
    has_back = "Замена заднего стекла" in pr
    bio_label = "Face ID" if bio == "faceid" else "Кнопка Home / Touch ID"
    bio_human = "Face ID" if bio == "faceid" else "кнопку Home и сканер Touch ID"
    bio_short = "Face ID" if bio == "faceid" else "Touch ID"

    # Что сохраняем при замене экрана
    feats = []
    if promo: feats.append("ProMotion 120 Гц")
    if truetone: feats.append("True Tone")
    save_screen = "True Tone, ProMotion 120 Гц" if (promo and truetone) else (", ".join(feats) if feats else "")
    if water:
        screen_feat = (save_screen + " и заводскую влагозащиту") if save_screen else "заводскую влагозащиту"
    else:
        screen_feat = (save_screen + " и качество изображения") if save_screen else "заводское качество изображения"
    disp_human = "OLED-дисплей" if disp == "OLED" else "ЖК-дисплей (LCD)"

    # Прайс
    rows = ['<tr><td class="svc-name free">Диагностика</td><td class="pr free">Бесплатно</td><td class="time">при вас</td></tr>']
    for key, label_t, t in SVC_META:
        if key not in pr: continue
        label = label_t.replace("__PORT__", port)
        rows.append(f'<tr><td class="svc-name">{label}</td><td class="pr">{rng(pr[key])}</td><td class="time">{t}</td></tr>')
    price_rows = "\n            ".join(rows)

    # Карточки «виды ремонта»
    card_desc = {
        "Замена экрана (дисплея)": f"Разбит дисплей {name} или не реагирует на касания. Сохраняем {screen_feat}.",
        "Замена аккумулятора": f"{name} быстро разряжается или выключается на холоде. Ставим новую батарею с ёмкостью 100%.",
        "Замена заднего стекла": f"Треснула задняя крышка {name}. Восстанавливаем заводской вид без замены всего корпуса.",
        "Не заряжается (разъём)": f"{name} не заряжается или заряд идёт через раз. Чистим или меняем {port} порт.",
        "После воды": f"{name} попал в воду и не включается. Ультразвуковая чистка платы — чем раньше, тем больше шансов.",
        "Замена камеры": f"Основная, телеобъектив или фронтальная камера {name}. Решаем проблему с фокусом и тряской.",
        "Динамик / микрофон": f"Собеседник вас не слышит или тихий звук в {name}. Меняем разговорный/полифонический динамик и микрофон.",
        "Face ID": f"Восстановление Face ID и фронтальной камеры {name}. Сложный ремонт с микропайкой.",
        "Кнопка Home / Touch ID": f"Не работает кнопка Home или отпечаток Touch ID на {name}. Ремонтируем шлейф и восстанавливаем функцию.",
        "Ремонт платы": f"Микропайка BGA, восстановление цепей питания, замена контроллеров {name}. Сложный ремонт — наша специализация.",
    }
    card_title = {"Не заряжается (разъём)": f"{port} разъём", "Face ID": "Face ID",
                  "Кнопка Home / Touch ID": "Кнопка Home / Touch ID"}
    card_order = ["Замена экрана (дисплея)", "Замена аккумулятора", "Не заряжается (разъём)", bio_label,
                  "Замена камеры", "Замена заднего стекла", "Динамик / микрофон", "После воды", "Ремонт платы"]
    card_meta = {"Замена экрана (дисплея)":["30-60 мин","Гарантия 12 мес"], "Замена аккумулятора":["30-40 мин","Гарантия 12 мес"],
                 "Не заряжается (разъём)":["30-50 мин","Гарантия 12 мес"], "Face ID":["1-3 часа","Гарантия 12 мес"],
                 "Кнопка Home / Touch ID":["40-60 мин","Гарантия 12 мес"], "Замена камеры":["40-60 мин","Гарантия 12 мес"],
                 "Замена заднего стекла":["1-2 часа","Гарантия 12 мес"], "Динамик / микрофон":["30-50 мин","Гарантия 12 мес"],
                 "После воды":["от 2 часов","Диагностика 0 ₴"], "Ремонт платы":["1-3 дня","Диагностика 0 ₴"]}
    cards = []
    for key in card_order:
        if key not in pr: continue
        title = card_title.get(key, key)
        m0, m1 = card_meta[key]
        green = ' class="green"' if "Диагностика" in m1 or "Гарантия" in m1 else ""
        cards.append(
            '<div class="rtype reveal">\n'
            '          <h3><span class="ri"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">%s</svg></span> %s</h3>\n'
            '          <p>%s</p>\n'
            '          <div class="meta"><span>%s</span><span class="green">%s</span></div>\n'
            '        </div>' % (ICONS[key], title, card_desc[key], m0, m1))
    repair_cards = "\n        ".join(cards)

    # FAQ
    if promo:
        dq = f"Сохранится ли True Tone и ProMotion 120 Гц после замены экрана {name}?"
        da = "Да. Мы переносим данные дисплея — True Tone и частота обновления ProMotion 120 Гц сохраняются как на оригинальных, так и на качественных совместимых экранах."
    elif bio == "touchid":
        dq = f"Ремонтируете ли вы кнопку Home и Touch ID {name}?"
        da = f"Да. Восстанавливаем кнопку Home и сканер отпечатка Touch ID {name}, меняем шлейф. Важно: при повреждении самого датчика Touch ID функция отпечатка может быть недоступна — мастер проверит и скажет точно на бесплатной диагностике."
    elif truetone:
        dq = f"Сохранится ли True Tone после замены экрана {name}?"
        da = f"Да. Мы переносим данные дисплея — функция True Tone сохраняется как на оригинальных, так и на качественных совместимых экранах {name}."
    else:
        dq = f"Какие экраны вы ставите на {name}?"
        da = f"Оригинальные или качественные совместимые {disp_human.lower()} на ваш выбор. Разницу в цене и качестве мастер показывает до начала ремонта."
    faq = [
        (f"Сколько стоит замена экрана {name}?",
         f"От {money(pr['Замена экрана (дисплея)'][0])} до {money(pr['Замена экрана (дисплея)'][1])} ₴ в зависимости от типа запчасти (оригинал или качественный совместимый дисплей). Точную цену мастер назовёт после бесплатной диагностики."),
        ("Сколько времени занимает ремонт?",
         f"Замена экрана и аккумулятора {name} — 30-60 минут при вас. Ремонт после воды и микропайка платы — от нескольких часов до 1-3 дней."),
        (dq, da),
        (f"Ремонтируете ли вы {port} разъём {name}?",
         f"Да. Если {name} не заряжается или заряд идёт через раз — чистим или меняем {port} разъём. Стоимость от {money(pr['Не заряжается (разъём)'][0])} ₴, ремонт 30-50 минут."),
        (f"Можно ли починить {name} после воды?",
         "В 70-80% случаев — да. Важно не пытаться заряжать и не сушить феном, а сразу привезти к нам. Чем раньше — тем выше шанс на успешный ремонт."),
        ("Какая гарантия на ремонт?",
         "До 12 месяцев на запчасти и работы. Срок указан в чеке для каждой услуги."),
    ]
    faq_json = ",\n    ".join('{"@type":"Question","name":%s,"acceptedAnswer":{"@type":"Answer","text":%s}}' % (jstr(q), jstr(a)) for q, a in faq)
    faq_html = "\n        ".join(f'<details{" open" if i==0 else ""}><summary>{q}</summary><div class="a">{a}</div></details>' for i, (q, a) in enumerate(faq))

    # Перелинковка: кластер (свой ряд) + якоря, без self, до 9
    my_series = next((s for s in SERIES if tid in s), [])
    related, seen = [], set()
    for cand in my_series + ANCHORS:
        if cand == tid or cand in seen or cand not in SPEC: continue
        seen.add(cand); related.append(cand)
        if len(related) >= 9: break
    other_links = "\n          ".join(f'<a href="../{SPEC[c][1]}/">{SPEC[c][0]}</a>' for c in related)
    other_links += '\n          <a href="../">Все модели iPhone →</a>'

    # SEO-текст: биометрия + порт + заднее стекло
    bio_seo = "восстанавливаем Face ID и фронтальную камеру" if bio == "faceid" else "ремонтируем кнопку Home и сканер Touch ID"
    back_seo = "заднее стекло, " if has_back else ""
    if water:
        save_line = f"При замене экрана {name} ({disp_human}) сохраняем {('True Tone и ProMotion 120 Гц' if (promo and truetone) else (save_screen if save_screen else 'качество изображения'))}, при ремонте — восстанавливаем заводскую влагозащиту."
    else:
        save_line = f"При замене экрана {name} ({disp_human}) используем качественные дисплейные модули; разницу между оригиналом и совместимым мастер показывает до ремонта."

    # Опции форм
    opts = "\n              ".join("<option>%s</option>" % o for o in [
        f"{name} — разбит экран", f"{name} — не держит батарея", f"{name} — не заряжается",
        f"{name} — после воды / не включается",
        (f"{name} — Face ID не работает" if bio == "faceid" else f"{name} — не работает кнопка Home"),
        f"{name} — проблема с камерой", f"{name} — другое"])

    # Hero-арт
    out_dir = os.path.join(REPO, "remont-iphone", slug)
    has_photo = os.path.exists(os.path.join(out_dir, slug + ".webp"))
    svg = (
        '<svg class="phone" viewBox="0 0 300 600" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="%s">\n'
        '              <defs>\n'
        '                <linearGradient id="frm" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#3a3d45"/><stop offset=".5" stop-color="#15171c"/><stop offset="1" stop-color="#2b2e36"/></linearGradient>\n'
        '                <linearGradient id="scr" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1c1f27"/><stop offset="1" stop-color="#0f1117"/></linearGradient>\n'
        '              </defs>\n'
        '              <rect x="284" y="150" width="5" height="58" rx="2.5" fill="#2c2f38"/>\n'
        '              <rect x="11" y="150" width="5" height="34" rx="2.5" fill="#2c2f38"/>\n'
        '              <rect x="11" y="196" width="5" height="34" rx="2.5" fill="#2c2f38"/>\n'
        '              <rect x="16" y="6" width="268" height="588" rx="48" fill="url(#frm)"/>\n'
        '              <rect x="22" y="12" width="256" height="576" rx="43" fill="#0a0b0e"/>\n'
        '              <rect x="28" y="18" width="244" height="564" rx="38" fill="url(#scr)"/>\n'
        '              <rect x="120" y="30" width="60" height="20" rx="10" fill="#000"/>\n'
        '              <text x="50" y="44" fill="#aeb3bf" font-family="-apple-system,Arial" font-size="14" font-weight="600">9:41</text>\n'
        '              <rect x="231" y="34" width="22" height="11" rx="3" fill="none" stroke="#aeb3bf" stroke-width="1.3"/>\n'
        '              <rect x="233" y="36" width="15" height="7" rx="1.5" fill="#aeb3bf"/>\n'
        '              <text x="150" y="290" text-anchor="middle" fill="#fff" font-family="-apple-system,Arial" font-size="22" font-weight="700">%s</text>\n'
        '              <text x="150" y="318" text-anchor="middle" fill="#878d99" font-family="-apple-system,Arial" font-size="13">Ремонт · SPARK · Одесса</text>\n'
        '            </svg>' % (esc_attr(name), name))
    if has_photo:
        hero_art = ('<div class="model-photo-wrap">\n'
            '          <img class="model-photo" src="%s.webp" alt="Ремонт %s в Одессе — сервисный центр SPARK" width="500" height="500" fetchpriority="high" onload="var f=document.getElementById(\'photoFallback\');if(f)f.remove()" onerror="this.remove()">\n'
            '          <div id="photoFallback" class="photo-fallback">\n            %s\n          </div>\n        </div>' % (slug, esc_attr(name), svg))
    else:
        hero_art = ('<div class="model-photo-wrap">\n          <div class="photo-fallback">\n            %s\n          </div>\n        </div>' % svg)

    repl = {
        "@@NAME@@": name, "@@TRANSLIT@@": translit(name), "@@CANON@@": canon, "@@OG_IMAGE@@": OG_IMAGE,
        "@@OFFER_PRICE@@": str(batt_low), "@@OFFER_BATT@@": money(batt_low), "@@FROM_PRICE@@": money(batt_low),
        "@@PORT@@": port, "@@BIO_HUMAN@@": bio_human, "@@BIO_SEO@@": bio_seo, "@@BACK_SEO@@": back_seo,
        "@@SCREEN_FEAT@@": screen_feat, "@@SAVE_LINE@@": save_line, "@@DISP_HUMAN@@": disp_human,
        "@@FAQ_JSON@@": faq_json, "@@FAQ_HTML@@": faq_html, "@@PRICE_ROWS@@": price_rows,
        "@@REPAIR_CARDS@@": repair_cards, "@@OTHER_MODELS@@": other_links, "@@BOOK_OPTIONS@@": opts,
        "@@HERO_ART@@": hero_art, "@@MODEL_NOTES@@": NOTES.get(slug, f"Сервисный центр SPARK ремонтирует {name} в Одессе — экран, аккумулятор, разъём, камеры, плата."),
    }
    html = TEMPLATE
    for k, v in repl.items():
        html = html.replace(k, v)
    return html, out_dir


TEMPLATE = r'''<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Ремонт @@NAME@@ в Одессе — замена экрана, батареи, @@BIO_HUMAN@@ | SPARK</title>
<meta name="description" content="Ремонт @@NAME@@ в Одессе: замена экрана, аккумулятора, @@BIO_HUMAN@@, @@PORT@@ разъёма, после воды. Бесплатная диагностика, оригинальные запчасти, гарантия 12 мес, ремонт за 30-60 мин. ☎ +38 (096) 075-54-52">
<meta name="keywords" content="ремонт @@NAME@@, ремонт @@TRANSLIT@@ Одесса, замена экрана @@NAME@@, замена дисплея @@NAME@@, замена батареи @@NAME@@, замена аккумулятора @@NAME@@, @@NAME@@ Одесса, замена стекла @@NAME@@, сервисный центр Apple Одесса">
<meta name="robots" content="index, follow">
<link rel="canonical" href="@@CANON@@">
<meta name="theme-color" content="#ffffff">
<meta property="og:type" content="website">
<meta property="og:title" content="Ремонт @@NAME@@ в Одессе | SPARK">
<meta property="og:description" content="Замена экрана, батареи, @@BIO_HUMAN@@, @@PORT@@. Бесплатная диагностика, гарантия 12 мес. ул. Академика Королёва, 23, Одесса.">
<meta property="og:url" content="@@CANON@@">
<meta property="og:locale" content="ru_RU">
<meta property="og:image" content="@@OG_IMAGE@@">

<script type="application/ld+json">
{
  "@context":"https://schema.org","@type":"Service","@id":"@@CANON@@#service",
  "name":"Ремонт @@NAME@@ в Одессе","description":"Профессиональный ремонт @@NAME@@: замена экрана, аккумулятора, @@BIO_HUMAN@@, @@PORT@@ разъёма, ремонт после воды и микропайка платы. Гарантия до 12 месяцев.",
  "provider":{"@type":"Organization","name":"SPARK","url":"https://sparkservice.od.ua/","telephone":"+380960755452","address":{"@type":"PostalAddress","streetAddress":"ул. Академика Королёва, 23","addressLocality":"Одесса","addressCountry":"UA"}},
  "areaServed":{"@type":"City","name":"Одесса"},
  "serviceType":"Ремонт @@NAME@@",
  "offers":{"@type":"Offer","priceCurrency":"UAH","price":"@@OFFER_PRICE@@","description":"Замена аккумулятора @@NAME@@ от @@OFFER_BATT@@ ₴"}
}
</script>
<script type="application/ld+json">
{
  "@context":"https://schema.org","@type":"BreadcrumbList",
  "itemListElement":[
    {"@type":"ListItem","position":1,"name":"Главная","item":"https://sparkservice.od.ua/"},
    {"@type":"ListItem","position":2,"name":"Ремонт iPhone","item":"https://sparkservice.od.ua/remont-iphone/"},
    {"@type":"ListItem","position":3,"name":"@@NAME@@","item":"@@CANON@@"}
  ]
}
</script>
<script type="application/ld+json">
{
  "@context":"https://schema.org","@type":"FAQPage","mainEntity":[
    @@FAQ_JSON@@
  ]
}
</script>

<link rel="stylesheet" href="../../styles.css">
<style>
  .bc{padding:14px 0;font-size:.86rem;color:var(--muted)}
  .bc a{color:var(--muted);font-weight:500}.bc a:hover{color:var(--spark)}
  .bc span{margin:0 7px;opacity:.5}
  .page-hero{padding:48px 0 56px;background:linear-gradient(180deg,#fff 0%,var(--bg) 100%)}
  .page-hero .wrap{display:grid;grid-template-columns:1fr;gap:30px;align-items:center}
  .page-hero h1{font-size:clamp(1.7rem,4vw,2.6rem);line-height:1.12;font-weight:750;letter-spacing:-.025em;color:var(--ink);margin:18px 0 16px}
  .page-hero p.sub{font-size:1.05rem;line-height:1.6;color:#41454f;max-width:52ch;margin-bottom:24px}
  .page-hero .hero-cta{display:flex;flex-wrap:wrap;gap:12px}
  .page-hero .quick{display:flex;flex-wrap:wrap;gap:8px 18px;margin-top:22px;font-size:.9rem;color:var(--muted)}
  .page-hero .quick b{color:var(--text);font-weight:600}
  @media(min-width:920px){.page-hero .wrap{grid-template-columns:1.15fr .85fr;gap:48px;padding-top:20px}}
  .model-photo-wrap{display:flex;justify-content:center;align-items:center}
  .model-photo{width:100%;max-width:360px;height:auto;display:block;filter:drop-shadow(0 22px 38px rgba(16,18,26,.20))}
  @media(min-width:920px){.model-photo{max-width:430px}}
  .photo-fallback{position:relative;width:100%;max-width:340px}
  .repair-types{display:grid;grid-template-columns:1fr;gap:14px;margin-top:24px}
  .rtype{background:#fff;border:1px solid var(--line);border-radius:var(--r);padding:22px;transition:transform .3s,box-shadow .3s,border-color .3s}
  .rtype:hover{transform:translateY(-3px);box-shadow:0 18px 40px -20px rgba(16,18,26,.25);border-color:#dbe0e8}
  .rtype h3{font-size:1.08rem;font-weight:650;margin-bottom:6px;display:flex;align-items:center;gap:10px}
  .rtype h3 .ri{width:36px;height:36px;border-radius:9px;background:var(--spark-soft);color:var(--spark);display:grid;place-items:center;flex-shrink:0}
  .rtype h3 .ri svg{width:20px;height:20px}
  .rtype p{color:var(--muted);font-size:.93rem;margin-bottom:10px}
  .rtype .meta{display:flex;flex-wrap:wrap;gap:8px}
  .rtype .meta span{font-size:.8rem;font-weight:600;background:var(--bg);border:1px solid var(--line);border-radius:999px;padding:4px 11px;color:var(--ink)}
  .rtype .meta .green{color:var(--ok)}
  @media(min-width:680px){.repair-types{grid-template-columns:repeat(2,1fr)}}
  @media(min-width:920px){.repair-types{grid-template-columns:repeat(3,1fr)}}
  .other-models{display:flex;flex-wrap:wrap;gap:8px;margin-top:8px}
  .other-models a{display:inline-flex;padding:7px 13px;border:1px solid var(--line);border-radius:999px;font-size:.88rem;font-weight:500;color:var(--text);background:#fff;transition:.15s}
  .other-models a:hover{border-color:var(--spark);color:var(--spark);transform:translateY(-1px)}
</style>
</head>
<body>
<a class="skip" href="#main">Перейти к содержимому</a>

<div class="topbar">
  <div class="wrap">
    <span class="tb-item tb-hide"><span class="dot"></span> Сегодня работаем · 10:00-19:00</span>
    <span class="right">
      <span class="lang"><a href="https://sparkservice.od.ua/">UA</a><span>/</span><a class="on" href="#">RU</a></span>
    </span>
  </div>
</div>

<header class="site" id="hdr">
  <div class="wrap nav">
    <a class="brand" href="../../" aria-label="SPARK - сервисный центр Apple в Одессе"><img src="../../logo.png" alt="SPARK - ремонт и сервис техники Apple в Одессе" width="160" height="82" style="height:36px;width:auto"></a>
    <nav class="nav-links" aria-label="Основная навигация">
      <span class="has-drop">
        <a href="../../remont-iphone/" role="button" aria-haspopup="true">Ремонт</a>
        <span class="drop" role="menu">
          <a href="../../remont-iphone/"><svg class="di" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><rect x="7" y="2" width="10" height="20" rx="2.5"/></svg> Ремонт iPhone</a>
          <a href="../../remont-macbook/"><svg class="di" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><rect x="4" y="4" width="16" height="11" rx="1.5"/><path d="M2 19h20l-1.5-2H3.5z"/></svg> Ремонт MacBook</a>
          <a href="../../remont-imac/"><svg class="di" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><rect x="3" y="3" width="18" height="13" rx="1.5"/><path d="M9 20h6"/></svg> Ремонт iMac</a>
          <a href="../../remont-ipad/"><svg class="di" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><rect x="5" y="3" width="14" height="18" rx="2"/></svg> Ремонт iPad</a>
          <a href="../../remont-apple-watch/"><svg class="di" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><rect x="7" y="6" width="10" height="12" rx="3"/></svg> Ремонт Apple Watch</a>
          <a href="../../remont-airpods/"><svg class="di" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M8 3v10M16 3v10"/></svg> Ремонт AirPods</a>
        </span>
      </span>
      <span class="has-drop">
        <a href="../../razblokirovka-icloud/" role="button" aria-haspopup="true">Услуги</a>
        <span class="drop" role="menu">
          <a href="../../razblokirovka-icloud/">Разблокировка iCloud</a>
          <a href="../../razblokirovka-iphone/">Разблокировка iPhone</a>
          <a href="../../diagnostika/">Диагностика</a>
          <a href="../../vosstanovlenie-dannyh/">Восстановление данных</a>
        </span>
      </span>
      <a href="../../#prices">Цены</a>
      <a href="../../blog/">Блог</a>
      <a href="../../kontakty/">Контакты</a>
    </nav>
    <div class="nav-right">
      <span class="hphone"><a href="tel:+380960755452">+38 (096) 075-54-52</a><small>Пн-Сб 10:00-19:00</small></span>
      <a class="btn btn-spark hcta" href="#book">Записаться</a>
      <button class="burger" id="burger" aria-label="Меню" aria-expanded="false"><span></span></button>
    </div>
  </div>
</header>
<nav class="mnav" id="mnav" aria-label="Мобильное меню">
  <p class="grp">Ремонт устройств</p>
  <a href="../../remont-iphone/"><span class="mi"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><rect x="7" y="2" width="10" height="20" rx="2.5"/><line x1="11" y1="18.5" x2="13" y2="18.5"/></svg></span> iPhone</a>
  <a href="../../remont-macbook/"><span class="mi"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><rect x="4" y="4" width="16" height="11" rx="1.5"/><path d="M2 19h20l-1.5-2H3.5z"/></svg></span> MacBook</a>
  <a href="../../remont-imac/"><span class="mi"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><rect x="3" y="3" width="18" height="13" rx="1.5"/><path d="M9 20h6"/></svg></span> iMac</a>
  <a href="../../remont-ipad/"><span class="mi"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><rect x="5" y="3" width="14" height="18" rx="2"/></svg></span> iPad</a>
  <a href="../../remont-apple-watch/"><span class="mi"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><rect x="7" y="6" width="10" height="12" rx="3"/><path d="M9 6l1-3h4l1 3"/></svg></span> Apple Watch</a>
  <a href="../../remont-airpods/"><span class="mi"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M8 3v10M8 13a3 3 0 11-3 3M16 3v10M16 13a3 3 0 103 3"/></svg></span> AirPods</a>
  <p class="grp">Услуги</p>
  <a href="../../razblokirovka-icloud/"><span class="mi"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M7 18a4 4 0 010-8 5 5 0 019.6-1.3A3.5 3.5 0 0117.5 18z"/></svg></span> Разблокировка iCloud</a>
  <a href="../../razblokirovka-iphone/"><span class="mi"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><rect x="5" y="11" width="14" height="9" rx="2"/><path d="M8 11V8a4 4 0 018 0v3"/></svg></span> Разблокировка iPhone</a>
  <a href="../../diagnostika/"><span class="mi"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.5" y2="16.5"/></svg></span> Диагностика</a>
  <a href="../../vosstanovlenie-dannyh/"><span class="mi"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><ellipse cx="12" cy="6" rx="8" ry="3"/><path d="M4 6v12c0 1.7 3.6 3 8 3s8-1.3 8-3V6"/></svg></span> Восстановление данных</a>
  <p class="grp">Информация</p>
  <a href="../../#prices"><span class="mi"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M3 7v5l9 9 5-5-9-9H3z"/><circle cx="7" cy="11" r="1.3"/></svg></span> Цены и сроки</a>
  <a href="../../blog/"><span class="mi"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M6 3h9l3 3v15H6z"/><line x1="9" y1="10" x2="15" y2="10"/><line x1="9" y1="14" x2="15" y2="14"/></svg></span> Блог</a>
  <a href="../../kontakty/"><span class="mi"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M12 3s6 7 6 11a6 6 0 11-12 0c0-4 6-11 6-11z"/><circle cx="12" cy="11" r="2"/></svg></span> Контакты</a>
  <a class="cta" href="#book">Записаться</a>
</nav>

<main id="main">
  <div class="wrap">
    <div class="bc" aria-label="Хлебные крошки">
      <a href="../../">Главная</a><span>›</span><a href="../../remont-iphone/">Ремонт iPhone</a><span>›</span><span>@@NAME@@</span>
    </div>
  </div>

  <section class="page-hero">
    <div class="wrap">
      <div class="page-hero-copy">
        <span class="eyebrow">Ремонт @@NAME@@ в Одессе</span>
        <h1>Ремонт @@NAME@@</h1>
        <p class="sub">Замена экрана и аккумулятора, ремонт @@BIO_HUMAN@@, @@PORT@@ разъёма, задней крышки и платы. Сохраняем @@SCREEN_FEAT@@. Бесплатная диагностика, оригинальные запчасти и гарантия до 12 месяцев. Чаще всего — за 30-60 минут при вас.</p>
        <div class="hero-cta">
          <a class="btn btn-spark" href="#book">Записаться</a>
          <a class="btn btn-line" href="tel:+380960755452">☎ Позвонить</a>
        </div>
        <p class="cta-note">⏱ <b>Перезвоним за 15 минут</b> · без предоплаты</p>
        <div class="trustbar"><span class="tb-star">★ 4.9</span> <b>Google</b><span class="sep">·</span>127 отзывов<span class="sep">·</span><b>32 000</b> ремонтов<span class="sep">·</span>9 лет</div>
        <div class="quick">
          <span>📍 <b>ул. Академика Королёва, 23</b></span>
          <span>🕐 <b>Пн-Сб 10:00-19:00</b></span>
          <span>🛠 <b>от @@FROM_PRICE@@ ₴</b></span>
        </div>
      </div>
      <div class="hero-art">
        @@HERO_ART@@
      </div>
    </div>
  </section>

  <section class="sec sec-bg" id="prices">
    <div class="wrap">
      <div class="sec-head reveal">
        <span class="sec-tag">Цены на ремонт @@NAME@@</span>
        <h2>Прайс на ремонт @@NAME@@</h2>
        <p class="lead-p">Цены ориентировочные и зависят от типа запчасти (оригинал или совместимый). Точную стоимость мастер назовёт после бесплатной диагностики.</p>
      </div>
      <div class="ptable-wrap reveal">
        <table class="price-table">
          <thead>
            <tr><th>Услуга</th><th>Цена</th><th>Срок</th></tr>
          </thead>
          <tbody>
            @@PRICE_ROWS@@
          </tbody>
        </table>
      </div>
      <p class="lead-p" style="margin-top:18px;font-size:.88rem">Цены указаны в гривнах. Диагностика @@NAME@@ бесплатная.</p>
    </div>
  </section>

  <section class="sec" id="repair-types">
    <div class="wrap">
      <div class="sec-head reveal">
        <span class="sec-tag">Виды ремонта</span>
        <h2>Что ремонтируем в @@NAME@@</h2>
        <p class="lead-p">Беремся за любые неисправности @@NAME@@ — от замены стекла до микропайки платы. Точную цену и срок назовём после бесплатной диагностики.</p>
      </div>
      <div class="repair-types">
        @@REPAIR_CARDS@@
      </div>
    </div>
  </section>

  <section class="sec sec-ink" id="process">
    <div class="wrap">
      <div class="sec-head reveal">
        <span class="sec-tag">Как мы работаем</span>
        <h2 style="color:#fff">Ремонт @@NAME@@ за 4 шага</h2>
      </div>
      <div class="steps">
        <div class="step reveal"><h3>Приём устройства</h3><p>Привезите @@NAME@@ или оставьте заявку — зафиксируем состояние и выдадим квитанцию.</p></div>
        <div class="step reveal"><h3>Бесплатная диагностика</h3><p>Находим причину поломки и называем точную цену. Начинаем только с вашего согласия.</p><span class="badge">Бесплатно</span></div>
        <div class="step reveal"><h3>Ремонт и тестирование</h3><p>Меняем запчасть или паяем плату, проверяем по чек-листу из 15+ пунктов.</p></div>
        <div class="step reveal"><h3>Выдача с гарантией</h3><p>Отдаём @@NAME@@ с чеком и гарантийным талоном.</p><span class="badge w">До 12 месяцев</span></div>
      </div>
    </div>
  </section>

  <section class="sec" id="why">
    <div class="wrap">
      <div class="sec-head reveal">
        <span class="sec-tag">Почему выбирают нас</span>
        <h2>Преимущества ремонта @@NAME@@ в SPARK</h2>
      </div>
      <div class="why-grid">
        <div class="why reveal"><div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.5" y2="16.5"/></svg></div><h3>Бесплатная диагностика</h3><p>Найдём причину бесплатно — даже если откажетесь от ремонта.</p></div>
        <div class="why reveal"><div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 3l7 3v5c0 4.5-3 8-7 10-4-2-7-5.5-7-10V6z"/><path d="M9 12l2 2 4-4"/></svg></div><h3>Гарантия до 12 месяцев</h3><p>На запчасти и работу. Срок фиксируется в чеке.</p></div>
        <div class="why reveal"><div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2l3 6 6 .5-4.5 4 1.5 6-6-3.5L6 18.5 7.5 12.5 3 8.5 9 8z"/></svg></div><h3>Оригинальные запчасти</h3><p>Оригинал или качественный аналог — выбор за вами, разницу объясним.</p></div>
        <div class="why reveal"><div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg></div><h3>Ремонт за 30-60 минут</h3><p>Большинство ремонтов @@NAME@@ выполняется при вас за полчаса-час.</p></div>
      </div>
    </div>
  </section>

  <section class="sec" id="seo-text">
    <div class="wrap">
      <div class="reveal" style="max-width:80ch">
        <h2 style="font-size:1.3rem;margin-bottom:14px">Ремонт @@NAME@@ в Одессе — сервисный центр SPARK</h2>
        <p style="color:var(--text);font-size:.97rem;line-height:1.7;margin-bottom:14px;padding-left:14px;border-left:3px solid var(--spark)">
          @@MODEL_NOTES@@
        </p>
        <p style="color:var(--muted);font-size:.95rem;line-height:1.7;margin-bottom:14px">
          Сервисный центр SPARK выполняет ремонт @@NAME@@ в Одессе любой сложности. Меняем разбитый экран (дисплей), вздувшийся или быстро разряжающийся аккумулятор, @@BIO_SEO@@, ремонтируем @@PORT@@ разъём зарядки, @@BACK_SEO@@основную и фронтальную камеру, разговорный и полифонический динамики, микрофон. Делаем микропайку материнской платы и восстановление после попадания воды.
        </p>
        <p style="color:var(--muted);font-size:.95rem;line-height:1.7;margin-bottom:14px">
          @@SAVE_LINE@@ Используем оригинальные или качественные совместимые запчасти на ваш выбор — разницу мастер объясняет и показывает до начала ремонта. На все работы и детали — гарантия до 12 месяцев, указанная в чеке.
        </p>
        <p style="color:var(--muted);font-size:.95rem;line-height:1.7">
          Бесплатная диагностика, ремонт чаще всего за 30-60 минут при вас. Находимся по адресу: ул. Академика Королёва, 23, Одесса. Работаем Пн-Сб с 10:00 до 19:00. Звоните: +38 (096) 075-54-52.
        </p>
        <p style="margin-top:18px;font-weight:600;color:var(--ink)">Ремонт других моделей iPhone:</p>
        <div class="other-models">
          @@OTHER_MODELS@@
        </div>
      </div>
    </div>
  </section>

  <section class="sec sec-bg" id="faq">
    <div class="wrap">
      <div class="sec-head reveal">
        <span class="sec-tag">Частые вопросы</span>
        <h2>Вопросы о ремонте @@NAME@@</h2>
      </div>
      <div class="faq reveal">
        @@FAQ_HTML@@
      </div>
    </div>
  </section>

  <section class="sec" id="blog-related">
    <div class="wrap">
      <div class="sec-head reveal"><span class="sec-tag">Полезные статьи</span><h2>Из нашего блога</h2></div>
      <div style="display:flex;flex-wrap:wrap;gap:9px;margin-top:14px">
        <a href="../../blog/original-ili-kopiya-displeya-iphone/" style="display:inline-flex;padding:9px 15px;border:1px solid var(--line);border-radius:999px;font-size:.9rem;font-weight:500;color:var(--text);background:#fff">Оригинал или копия дисплея iPhone</a>
        <a href="../../blog/iphone-upal-v-vodu-chto-delat/" style="display:inline-flex;padding:9px 15px;border:1px solid var(--line);border-radius:999px;font-size:.9rem;font-weight:500;color:var(--text);background:#fff">iPhone упал в воду — что делать</a>
        <a href="../../blog/pochemu-bystro-saditsya-batareya/" style="display:inline-flex;padding:9px 15px;border:1px solid var(--line);border-radius:999px;font-size:.9rem;font-weight:500;color:var(--text);background:#fff">Почему быстро садится батарея</a>
      </div>
    </div>
  </section>

  <section class="sec sec-ink" id="book">
    <div class="wrap">
      <div class="book">
        <div class="copy reveal">
          <span class="sec-tag">Запись на ремонт @@NAME@@</span>
          <h2>Опишите поломку — перезвоним за 15 минут</h2>
          <p>Подскажем предварительную цену и срок, забронируем время. Или просто позвоните — мастер на связи.</p>
        </div>
        <div class="form sf reveal" id="bookFormInline">
          <div class="sf-body">
            <div class="mf-progress"><div class="mf-progress-row"><span>Заполнение заявки</span><b class="js-pct">0%</b></div><div class="mf-progress-track"><i class="js-bar"></i></div></div>
            <h3 class="sf-title">Заявка на ремонт @@NAME@@</h3>
            <div class="mf-field"><label>Ваше имя</label><div class="mf-input"><input class="js-name" type="text" autocomplete="name" placeholder="Как к вам обращаться"><span class="mf-ok">✓</span></div></div>
            <div class="mf-field"><label>Телефон</label>
              <div class="mf-input"><span class="mf-pre">+38</span><input class="js-phone" type="tel" inputmode="tel" autocomplete="tel" placeholder="(0__) ___-__-__"><span class="mf-ok">✓</span></div>
              <div class="mf-dots js-dots" aria-hidden="true"><span><i></i><i></i><i></i></span><span><i></i><i></i><i></i></span><span><i></i><i></i></span><span><i></i><i></i></span></div>
              <div class="mf-hint js-hint">Введите номер мобильного оператора Украины</div>
            </div>
            <div class="mf-field"><label>Что случилось</label><div class="mf-input"><select class="js-device" aria-label="Что случилось">
              @@BOOK_OPTIONS@@
            </select></div></div>
            <button class="btn btn-spark mf-submit js-submit" type="button" disabled>Отправить заявку</button>
            <p class="mf-note">Нажимая кнопку, вы соглашаетесь на обработку данных.</p>
            <div class="mf-trust"><span><b>✓</b> Бесплатная диагностика</span><span><b>✓</b> Гарантия 12 месяцев</span><span><b>✓</b> Без предоплаты</span></div>
          </div>
          <div class="sf-success">
            <div class="ms-check"><svg viewBox="0 0 52 52" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="26" cy="26" r="25" fill="rgba(31,174,90,.10)"/><path d="M15 27l7 7 15-16" stroke="#1FAE5A" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/></svg></div>
            <h3>Заявка принята!</h3>
            <p>Перезвоним в течение 15 минут в рабочее время.</p>
            <div class="ms-sum js-summary"></div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <section class="sec sec-bg" id="contacts">
    <div class="wrap">
      <div class="sec-head reveal">
        <span class="sec-tag">Контакты</span>
        <h2>Как нас найти</h2>
        <p class="lead-p">Мы в центре Одессы, рядом с Киевским рынком. Бесплатная диагностика — приходите или вызовите курьера.</p>
      </div>
      <div class="loc-grid reveal">
        <div class="loc-card">
          <div class="loc-row"><span class="lr-ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M12 3s6 7 6 11a6 6 0 11-12 0c0-4 6-11 6-11z"/><circle cx="12" cy="11" r="2"/></svg></span><div><b>Адрес</b><span>ул. Академика Королёва, 23, Одесса</span></div></div>
          <div class="loc-row"><span class="lr-ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg></span><div><b>Часы работы</b><span>Пн-Сб: 10:00-19:00 · Вс: выходной</span></div></div>
          <div class="loc-row"><span class="lr-ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M5 4h4l1.5 5-2 1.2a12 12 0 005.3 5.3l1.2-2 5 1.5v4a2 2 0 01-2 2A16 16 0 013 6a2 2 0 012-2z"/></svg></span><div><b>Телефон</b><a href="tel:+380960755452">+38 (096) 075-54-52</a></div></div>
          <a class="btn btn-spark" href="https://www.google.com/maps/dir/?api=1&destination=46.4035605,30.7226524" target="_blank" rel="noopener">Проложить маршрут</a>
        </div>
        <div class="loc-map">
          <iframe loading="lazy" title="SPARK на карте Одессы" src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d2751.2871721068323!2d30.720994715589114!3d46.40336147912331!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x40c6335e75e1ea93%3A0x24bdf429024f4684!2z0YPQuy4g0JDQutCw0LTQtdC80LjQutCwINCa0L7RgNC-0LvRkdCy0LAsIDIzLA!5e0!3m2!1sru!2sua!4v1667565183335!5m2!1sru!2sua"></iframe>
        </div>
      </div>
    </div>
  </section>
</main>

<footer class="site" id="footer">
  <div class="wrap">
    <div class="foot-grid">
      <div class="foot reveal">
        <a class="brand" href="../../"><img src="../../logo-footer.png" alt="SPARK - сервисный центр Apple в Одессе" width="160" height="82" style="height:40px;width:auto"></a>
        <p>Сервисный центр по ремонту техники Apple в Одессе. Ремонтируем Apple с любовью.</p>
        <div class="soc">
          <a href="https://www.instagram.com/spark__odessa/" rel="nofollow noopener" target="_blank" aria-label="Instagram"><svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2.16c3.2 0 3.58.01 4.85.07 1.17.05 1.8.25 2.23.41.56.22.96.48 1.38.9.42.42.68.82.9 1.38.16.42.36 1.06.41 2.23.06 1.27.07 1.65.07 4.85s-.01 3.58-.07 4.85c-.05 1.17-.25 1.8-.41 2.23-.22.56-.48.96-.9 1.38-.42.42-.82.68-1.38.9-.42.16-1.06.36-2.23.41-1.27.06-1.65.07-4.85.07s-3.58-.01-4.85-.07c-1.17-.05-1.8-.25-2.23-.41-.56-.22-.96-.48-1.38-.9-.42-.42-.68-.82-.9-1.38-.16-.42-.36-1.06-.41-2.23-.06-1.27-.07-1.65-.07-4.85s.01-3.58.07-4.85c.05-1.17.25-1.8.41-2.23.22-.56.48-.96.9-1.38.42-.42.82-.68 1.38-.9.42-.16 1.06-.36 2.23-.41 1.27-.06 1.65-.07 4.85-.07M12 0C8.74 0 8.33.01 7.05.07 5.78.13 4.9.33 4.14.63c-.79.31-1.46.72-2.13 1.38C1.35 2.68.94 3.35.63 4.14.33 4.9.13 5.78.07 7.05.01 8.33 0 8.74 0 12s.01 3.67.07 4.95c.06 1.27.26 2.15.56 2.91.31.79.72 1.46 1.38 2.13.67.66 1.34 1.07 2.13 1.38.76.3 1.64.5 2.91.56C8.33 23.99 8.74 24 12 24s3.67-.01 4.95-.07c1.27-.06 2.15-.26 2.91-.56.79-.31 1.46-.72 2.13-1.38.66-.67 1.07-1.34 1.38-2.13.3-.76.5-1.64.56-2.91.06-1.28.07-1.69.07-4.95s-.01-3.67-.07-4.95c-.06-1.27-.26-2.15-.56-2.91-.31-.79-.72-1.46-1.38-2.13C21.32 1.35 20.65.94 19.86.63 19.1.33 18.22.13 16.95.07 15.67.01 15.26 0 12 0z"/><path d="M12 5.84A6.16 6.16 0 1 0 18.16 12 6.16 6.16 0 0 0 12 5.84M12 16a4 4 0 1 1 4-4 4 4 0 0 1-4 4z"/><circle cx="18.41" cy="5.59" r="1.44"/></svg></a>
          <a href="https://t.me/sparks3m" rel="nofollow noopener" target="_blank" aria-label="Telegram"><svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M21.9 4.3l-3.3 15.5c-.2 1.1-.9 1.3-1.8.8l-4.9-3.6-2.4 2.3c-.3.3-.5.5-1 .5l.3-5 9.1-8.2c.4-.4-.1-.6-.6-.2L6.3 13.1l-4.8-1.5c-1-.3-1-1 .2-1.5L20.6 2.9c.9-.3 1.6.2 1.3 1.4z"/></svg></a>
          <a href="https://wa.me/380960755452" rel="nofollow noopener" target="_blank" aria-label="WhatsApp"><svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2a10 10 0 00-8.5 15.2L2 22l4.9-1.3A10 10 0 1012 2zm5.3 14.1c-.2.6-1.3 1.2-1.8 1.2-.5.1-1 .1-1.7-.1-.4-.1-.9-.3-1.6-.6-2.8-1.2-4.6-4-4.7-4.2-.1-.2-1.1-1.5-1.1-2.8s.7-2 .9-2.2c.2-.3.5-.3.7-.3h.5c.2 0 .4 0 .6.5l.8 1.9c.1.2.1.4 0 .5l-.4.6c-.1.2-.3.3-.1.6.1.2.6 1 1.3 1.6.9.8 1.6 1 1.9 1.2.2.1.4.1.5-.1l.6-.8c.2-.2.4-.2.6-.1l1.8.9c.2.1.4.2.5.3.1.3.1.7-.1 1.3z"/></svg></a>
        </div>
      </div>
      <div class="foot reveal">
        <h3>Ремонт</h3>
        <ul>
          <li><a href="../../remont-iphone/">Ремонт iPhone</a></li>
          <li><a href="../../remont-macbook/">Ремонт MacBook</a></li>
          <li><a href="../../remont-imac/">Ремонт iMac</a></li>
          <li><a href="../../remont-apple-watch/">Ремонт Apple Watch</a></li>
          <li><a href="../../remont-ipad/">Ремонт iPad</a></li>
          <li><a href="../../remont-airpods/">Ремонт AirPods</a></li>
        </ul>
      </div>
      <div class="foot reveal">
        <h3>Услуги</h3>
        <ul>
          <li><a href="../../razblokirovka-icloud/">Разблокировка iCloud</a></li>
          <li><a href="../../razblokirovka-iphone/">Разблокировка iPhone</a></li>
          <li><a href="../../diagnostika/">Диагностика</a></li>
          <li><a href="../../vosstanovlenie-dannyh/">Восстановление данных</a></li>
          <li><a href="../../blog/">Блог</a></li>
          <li><a href="../../o-kompanii/">О компании</a></li>
        </ul>
      </div>
      <div class="foot reveal">
        <h3>Контакты</h3>
        <p>ул. Академика Королёва, 23, Одесса<br>Пн-Сб: 10:00-19:00 · Вс: выходной</p>
        <p><a href="../../kontakty/">Как нас найти →</a></p>
      </div>
    </div>
    <div class="copyr">
      <span>© 2026 SPARK · Сервисный центр Apple в Одессе</span>
      <span>Прототип нового сайта</span>
    </div>
  </div>
</footer>

<div class="callbar">
  <a class="btn btn-line" href="tel:+380960755452">☎ Позвонить</a>
  <a class="btn btn-spark" href="#book">Записаться</a>
</div>

<div class="fab" aria-label="Связаться в мессенджере">
  <a class="tg" href="https://t.me/sparks3m" target="_blank" rel="noopener" aria-label="Telegram"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M21.9 4.3l-3.3 15.5c-.2 1.1-.9 1.3-1.8.8l-4.9-3.6-2.4 2.3c-.3.3-.5.5-1 .5l.3-5 9.1-8.2c.4-.4-.1-.6-.6-.2L6.3 13.1l-4.8-1.5c-1-.3-1-1 .2-1.5L20.6 2.9c.9-.3 1.6.2 1.3 1.4z"/></svg></a>
  <a class="wa" href="https://wa.me/380960755452" target="_blank" rel="noopener" aria-label="WhatsApp"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2a10 10 0 00-8.5 15.2L2 22l4.9-1.3A10 10 0 1012 2zm5.3 14.1c-.2.6-1.3 1.2-1.8 1.2-.5.1-1 .1-1.7-.1-.4-.1-.9-.3-1.6-.6-2.8-1.2-4.6-4-4.7-4.2-.1-.2-1.1-1.5-1.1-2.8s.7-2 .9-2.2c.2-.3.5-.3.7-.3h.5c.2 0 .4 0 .6.5l.8 1.9c.1.2.1.4 0 .5l-.4.6c-.1.2-.3.3-.1.6.1.2.6 1 1.3 1.6.9.8 1.6 1 1.9 1.2.2.1.4.1.5-.1l.6-.8c.2-.2.4-.2.6-.1l1.8.9c.2.1.4.2.5.3.1.3.1.7-.1 1.3z"/></svg></a>
</div>

<div class="modal" id="bookModal" aria-hidden="true">
  <div class="modal-overlay" data-close></div>
  <div class="modal-card" role="dialog" aria-modal="true" aria-labelledby="bookTitle">
    <button class="modal-x" type="button" aria-label="Закрыть" data-close>&times;</button>
    <div class="modal-body">
      <div class="mf-progress"><div class="mf-progress-row"><span>Заполнение заявки</span><b id="mPct">0%</b></div><div class="mf-progress-track"><i id="mpBar"></i></div></div>
      <div class="mf-head">
        <span class="eyebrow">Ремонт @@NAME@@</span>
        <h3 id="bookTitle">Оставьте заявку</h3>
        <p>Перезвоним за 15 минут, подскажем цену и срок. Диагностика бесплатная.</p>
      </div>
      <div class="mf-field">
        <label for="mName">Ваше имя</label>
        <div class="mf-input"><input id="mName" type="text" autocomplete="name" placeholder="Как к вам обращаться"><span class="mf-ok">✓</span></div>
      </div>
      <div class="mf-field">
        <label for="mPhone">Телефон</label>
        <div class="mf-input"><span class="mf-pre">+38</span><input id="mPhone" type="tel" inputmode="tel" autocomplete="tel" placeholder="(0__) ___-__-__"><span class="mf-ok">✓</span></div>
        <div class="mf-dots" id="mPhoneDots" aria-hidden="true"><span><i></i><i></i><i></i></span><span><i></i><i></i><i></i></span><span><i></i><i></i></span><span><i></i><i></i></span></div>
        <div class="mf-hint" id="mPhoneHint">Введите номер мобильного оператора Украины</div>
      </div>
      <div class="mf-field">
        <label for="mDevice">Что случилось</label>
        <div class="mf-input"><select id="mDevice" aria-label="Что случилось">
          @@BOOK_OPTIONS@@
        </select></div>
      </div>
      <button class="btn btn-spark mf-submit" id="mSubmit" type="button" disabled>Отправить заявку</button>
      <p class="mf-note">Нажимая кнопку, вы соглашаетесь на обработку данных. Мы не передаём их третьим лицам.</p>
      <div class="mf-trust">
        <span><b>✓</b> Бесплатная диагностика</span>
        <span><b>✓</b> Гарантия 12 месяцев</span>
        <span><b>✓</b> Без предоплаты</span>
      </div>
    </div>
    <div class="modal-success">
      <div class="ms-check"><svg viewBox="0 0 52 52" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="26" cy="26" r="25" fill="rgba(31,174,90,.10)"/><path d="M15 27l7 7 15-16" stroke="#1FAE5A" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/></svg></div>
      <h3>Заявка принята!</h3>
      <p>Перезвоним в течение 15 минут в рабочее время.</p>
      <div class="ms-sum" id="msSummary"></div>
      <button class="btn btn-line" type="button" data-close>Готово</button>
    </div>
  </div>
</div>

<script>
  var hdr=document.getElementById('hdr');
  addEventListener('scroll',function(){hdr.style.boxShadow=scrollY>6?'0 6px 20px -14px rgba(0,0,0,.25)':'none'},{passive:true});
  var b=document.getElementById('burger'),m=document.getElementById('mnav');
  b.addEventListener('click',function(){var o=m.classList.toggle('open');b.setAttribute('aria-expanded',o)});
  m.querySelectorAll('a').forEach(function(a){a.addEventListener('click',function(){m.classList.remove('open');b.setAttribute('aria-expanded',false)})});
  var rm=matchMedia('(prefers-reduced-motion: reduce)').matches;
  if(!rm && 'IntersectionObserver' in window){
    var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target)}})},{threshold:.1});
    document.querySelectorAll('.reveal').forEach(function(el){io.observe(el)});
  } else { document.querySelectorAll('.reveal').forEach(function(el){el.classList.add('in')}); }

  /* ---- Booking forms ---- */
  (function(){
    var OPS=[
      {n:'Kyivstar',c:['67','68','96','97','98','77']},
      {n:'Vodafone',c:['50','66','95','99']},
      {n:'lifecell',c:['63','73','93']},
      {n:'оператор',c:['91','92','94']}
    ];
    function detect(code){for(var i=0;i<OPS.length;i++){if(OPS[i].c.indexOf(code)>-1)return OPS[i].n;}return null;}
    function rawDigits(v){var d=v.replace(/\D/g,'');if(d.indexOf('38')===0)d=d.slice(2);if(d.length&&d[0]!=='0')d='0'+d;return d.slice(0,10);}
    function fmt(d){var o='';if(d.length>0)o='('+d.slice(0,3);if(d.length>=3)o+=') ';if(d.length>3)o+=d.slice(3,6);if(d.length>6)o+='-'+d.slice(6,8);if(d.length>8)o+='-'+d.slice(8,10);return o;}
    function esc(s){return String(s).replace(/[<>&"]/g,function(c){return {'<':'&lt;','>':'&gt;','&':'&amp;','"':'&quot;'}[c];});}

    function wireForm(o){
      if(!o.name||!o.phone||!o.submit) return;
      var dots=o.dotsWrap?o.dotsWrap.querySelectorAll('i'):[];
      var phoneValid=false;
      function checkPhone(){
        var d=rawDigits(o.phone.value); o.phone.value=fmt(d);
        var box=o.phone.closest('.mf-input'); phoneValid=false;
        if(d.length===0){o.hint.textContent='Введите номер мобильного оператора Украины';o.hint.className='mf-hint js-hint';box.classList.remove('valid','invalid');}
        else if(d.length<10){o.hint.textContent='Введите номер полностью';o.hint.className='mf-hint js-hint';box.classList.remove('valid','invalid');}
        else{var op=detect(d.slice(1,3));
          if(op){phoneValid=true;o.hint.innerHTML='<span class="mf-op">✓ '+op+'</span> номер распознан';o.hint.className='mf-hint js-hint ok';box.classList.add('valid');box.classList.remove('invalid');}
          else{o.hint.textContent='Проверьте код оператора — такого в Украине нет';o.hint.className='mf-hint js-hint err';box.classList.add('invalid');box.classList.remove('valid');}
        }
        for(var i=0;i<dots.length;i++){ if(i<d.length) dots[i].classList.add('on'); else dots[i].classList.remove('on'); }
        if(o.dotsWrap){o.dotsWrap.classList.remove('valid','invalid'); if(d.length===10) o.dotsWrap.classList.add(phoneValid?'valid':'invalid');}
        return d;
      }
      function checkName(){var ok=o.name.value.trim().length>=2;o.name.closest('.mf-input').classList.toggle('valid',ok);return ok;}
      function update(){
        var nameOk=checkName(); var d=checkPhone();
        var p=Math.round(((nameOk?1:0)+Math.min(d.length/10,1))/2*100);
        if(o.bar)o.bar.style.width=p+'%'; if(o.pct)o.pct.textContent=p+'%';
        o.submit.disabled=!(nameOk&&phoneValid);
      }
      o.name.addEventListener('input',update);
      o.phone.addEventListener('input',update);
      o.submit.addEventListener('click',function(){
        if(o.submit.disabled)return;
        if(o.summary)o.summary.innerHTML=
          '<div><span>Имя</span><b>'+esc(o.name.value.trim())+'</b></div>'+
          '<div><span>Телефон</span><b>+38 '+esc(o.phone.value)+'</b></div>'+
          '<div><span>Запрос</span><b>'+esc(o.dev?o.dev.value:'')+'</b></div>';
        if(o.bar)o.bar.style.width='100%';
        o.root.classList.add('done');
      });
      update();
    }

    var modal=document.getElementById('bookModal');
    if(modal){
      var card=modal.querySelector('.modal-card'), nameEl=document.getElementById('mName');
      wireForm({root:card,name:nameEl,phone:document.getElementById('mPhone'),dev:document.getElementById('mDevice'),hint:document.getElementById('mPhoneHint'),bar:document.getElementById('mpBar'),pct:document.getElementById('mPct'),submit:document.getElementById('mSubmit'),dotsWrap:document.getElementById('mPhoneDots'),summary:document.getElementById('msSummary')});
      var lastFocus=null;
      function openM(){lastFocus=document.activeElement;modal.classList.add('open');modal.setAttribute('aria-hidden','false');document.body.classList.add('modal-open');requestAnimationFrame(function(){modal.classList.add('show');});setTimeout(function(){if(nameEl)nameEl.focus();},360);}
      function closeM(){modal.classList.remove('show');modal.setAttribute('aria-hidden','true');document.body.classList.remove('modal-open');setTimeout(function(){modal.classList.remove('open');card.classList.remove('done');},300);if(lastFocus&&lastFocus.focus)lastFocus.focus();}
      document.addEventListener('click',function(e){
        var op=e.target.closest('a[href="#book"],[data-book]');
        if(op){e.preventDefault();openM();return;}
        if(e.target.closest('[data-close]'))closeM();
      });
      document.addEventListener('keydown',function(e){if(e.key==='Escape'&&modal.classList.contains('open'))closeM();});
    }

    var inlineRoot=document.getElementById('bookFormInline');
    if(inlineRoot){
      wireForm({root:inlineRoot,name:inlineRoot.querySelector('.js-name'),phone:inlineRoot.querySelector('.js-phone'),dev:inlineRoot.querySelector('.js-device'),hint:inlineRoot.querySelector('.js-hint'),bar:inlineRoot.querySelector('.js-bar'),pct:inlineRoot.querySelector('.js-pct'),submit:inlineRoot.querySelector('.js-submit'),dotsWrap:inlineRoot.querySelector('.js-dots'),summary:inlineRoot.querySelector('.js-summary')});
    }
  })();

  (function(){
    var bar=document.querySelector('.callbar');
    if(!bar) return;
    var hero=document.querySelector('.page-hero');
    var threshold=200, ticking=false;
    function measure(){ threshold = hero ? Math.max(hero.offsetHeight-100, 200) : window.innerHeight*0.8; }
    function check(){ bar.classList.toggle('show', window.scrollY > threshold); ticking=false; }
    function onScroll(){ if(!ticking){ ticking=true; requestAnimationFrame(check); } }
    window.addEventListener('scroll', onScroll, {passive:true});
    window.addEventListener('resize', function(){ measure(); check(); }, {passive:true});
    window.addEventListener('load', measure, {passive:true});
    measure(); check();
  })();
</script>
</body>
</html>
'''


def main():
    written = []
    for tid in SPEC:
        html, out_dir = render(tid)
        os.makedirs(out_dir, exist_ok=True)
        with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(html)
        written.append((SPEC[tid][1], len(html)))
    print("=== WRITTEN ===")
    for slug, n in written:
        print("  ✓ remont-iphone/%s (%d симв.)" % (slug, n))
    print("Итого: %d страниц моделей (iPhone 17 Pro Max — ручная, не трогаем)" % len(written))


if __name__ == "__main__":
    main()
