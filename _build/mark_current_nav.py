#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Помечает пункт меню/футера, ТОЧНО совпадающий с текущей страницей, как «вы здесь»:
убирает href (это self-link — вести уже некуда, как логотип на главной) и добавляет
aria-current="page" (CSS даёт подчёркивание вместо hover-плашки).
Подстраницы (модели, статьи блога) НЕ трогает — там пункт меню ведёт на ДРУГУЮ
страницу (хаб), это осмысленная навигация. Идемпотентно. Область: <header>, <nav
class="mnav">, <footer> — не трогает {{L:}}-ссылки в теле статей/страниц.
Запускать ПОСЛЕ i18n_wire.py (нужны финальные относительные пути)."""
import os, re, glob

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLOCK_RE = re.compile(
    r'(<header class="site".*?</header>|<nav class="mnav".*?</nav>|<footer class="site".*?</footer>)',
    re.S)
A_RE = re.compile(r'<a\s+([^>]*?)href="([^"]+)"([^>]*)>')

def norm(p):
    return os.path.normpath(p).replace(os.sep, "/")

def own_dir(filepath):
    d = os.path.dirname(filepath).replace(os.sep, "/")
    return d  # '' для главной

def resolve(base_dir, href):
    if href.startswith(("#", "http", "tel:", "mailto:", "javascript:")):
        return None
    if not href.endswith("/"):
        return None
    target = norm(os.path.join(base_dir, href))
    return "" if target == "." else target

def process_file(rel):
    path = os.path.join(REPO, rel)
    text = open(path, encoding="utf-8").read()
    mydir = own_dir(rel)

    def block_repl(bm):
        block = bm.group(0)
        def a_repl(am):
            pre, href, post = am.groups()
            tgt = resolve(mydir, href)
            if tgt is None or tgt != mydir:
                return am.group(0)
            if 'aria-current="page"' in pre + post:
                return am.group(0)  # уже помечено
            attrs = (pre + " " + post).strip()
            attrs = re.sub(r"\s+", " ", attrs)
            return ('<a %s aria-current="page">' % attrs) if attrs else '<a aria-current="page">'
        return A_RE.sub(a_repl, block)

    new_text = BLOCK_RE.sub(block_repl, text)
    changed = new_text != text
    if changed:
        open(path, "w", encoding="utf-8").write(new_text)
    return changed

def main():
    files = []
    for f in glob.glob(os.path.join(REPO, "**", "index.html"), recursive=True):
        rel = os.path.relpath(f, REPO).replace(os.sep, "/")
        if "_build" in rel:
            continue
        files.append(rel)
    changed = [f for f in files if process_file(f)]
    print("Помечено «вы здесь» на %d из %d страниц" % (len(changed), len(files)))
    for f in sorted(changed):
        print("  ", f)

if __name__ == "__main__":
    main()
