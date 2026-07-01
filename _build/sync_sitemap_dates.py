#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Синхронизирует <lastmod> в sitemap.xml с реальной датой последнего git-коммита файла.
Честный сигнал для краулера (Google перестаёт доверять lastmod, если он не коррелирует
с реальными изменениями). Запускать ПОСЛЕ коммита правок (git log должен видеть коммит) —
обычно отдельным финальным коммитом после основной правки."""
import os, re, subprocess

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITEMAP = os.path.join(REPO, "sitemap.xml")
BASE = "https://sparkservice.od.ua/"

def git_date(relpath):
    r = subprocess.run(["git", "log", "-1", "--format=%ad", "--date=short", "--", relpath],
                        capture_output=True, text=True, cwd=REPO)
    d = r.stdout.strip()
    return d or None

def main():
    t = open(SITEMAP, encoding="utf-8").read()
    changed = 0
    def repl(m):
        nonlocal changed
        url, old_date = m.group(1), m.group(2)
        path = url[len(BASE):]
        fpath = (path.rstrip("/") + "/index.html") if path else "index.html"
        new_date = git_date(fpath) or old_date
        if new_date != old_date:
            changed += 1
        return '<url><loc>%s</loc><lastmod>%s</lastmod>' % (url, new_date)
    t = re.sub(r'<url><loc>(https://sparkservice\.od\.ua/[^<]*)</loc><lastmod>([^<]*)</lastmod>', repl, t)
    open(SITEMAP, "w", encoding="utf-8").write(t)
    print("sitemap lastmod обновлён: %d из %d URL" % (changed, t.count("<url>")))

if __name__ == "__main__":
    main()
