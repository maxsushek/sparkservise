#!/usr/bin/env python3
# inject_analytics.py — вставляет <script defer src=".../analytics.js"> в <head> всех
# страниц (RU+UA) с правильным относительным путём по глубине. Идемпотентно (маркеры).
# Запускать ПОСЛЕ make_ua.py. analytics.js (в корне) — единственное место с ID конверсий.
import os, re, glob
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M0, M1 = '<!--spark-analytics-->', '<!--/spark-analytics-->'

def block(prefix):
    return M0 + '<script defer src="' + prefix + 'analytics.js"></script>' + M1

def process(f):
    rel = os.path.relpath(f, REPO).replace(os.sep, '/')
    prefix = '../' * rel.count('/')          # глубина до корня
    t = open(f, encoding='utf-8').read()
    b = block(prefix)
    if M0 in t:
        t2 = re.sub(re.escape(M0) + '.*?' + re.escape(M1), lambda m: b, t, flags=re.S)
    elif '</head>' in t:
        t2 = t.replace('</head>', b + '\n</head>', 1)
    else:
        return False
    if t2 != t:
        open(f, 'w', encoding='utf-8').write(t2)
        return True
    return False

def main():
    n = tot = 0
    for f in glob.glob(os.path.join(REPO, '**', 'index.html'), recursive=True):
        if '_build' in f:
            continue
        tot += 1
        if process(f):
            n += 1
    print("analytics injected/updated: %d из %d страниц" % (n, tot))

if __name__ == '__main__':
    main()
