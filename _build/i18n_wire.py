#!/usr/bin/env python3
# i18n_wire.py — детерминированная SEO-обвязка двуязычности SPARK (RU в корне + UK в /ua/).
# Запускать ПОСЛЕ создания/перевода любых /ua/ страниц (агенты делают только перевод текста+JSON-LD+lang=uk).
# Скрипт проставляет: пути к общим ассетам, canonical, og:url, reciprocal hreflang,
# языковой переключатель, JS-редирект, и для UA-страниц — внутренние ссылки (prefer-UA-else-RU).
import os, re, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "https://sparkservice.od.ua"
ASSETS = ("styles.css", "main.js", "logo.png", "logo-footer.png")
IMG_EXT = (".webp", ".jpg", ".jpeg", ".png", ".avif")
SKIP = ("http://", "https://", "mailto:", "tel:", "javascript:", "data:", "#")
HDR = '<header class="site" id="hdr">'
MARK = '<!--lang-redirect-->'
REDIR = MARK + "<script>(function(){try{var c=document.documentElement.lang==='uk'?'uk':'ru';var w=localStorage.getItem('spark_lang');if(!w){w=((navigator.language||navigator.userLanguage||'')+'').toLowerCase().indexOf('uk')===0?'uk':'ru';}var L=document.querySelectorAll('.lang a');for(var i=0;i<L.length;i++){(function(a){a.addEventListener('click',function(){try{localStorage.setItem('spark_lang',(a.textContent||'').trim().toUpperCase()==='UA'?'uk':'ru');}catch(e){}});})(L[i]);}if(w===c)return;if(sessionStorage.getItem('spark_rd'))return;var t=null;for(var j=0;j<L.length;j++){var x=(L[j].textContent||'').trim().toUpperCase();var h=L[j].getAttribute('href');if(h&&h!=='#'&&((w==='uk'&&x==='UA')||(w==='ru'&&x==='RU')))t=h;}if(t){sessionStorage.setItem('spark_rd','1');location.replace(t);}}catch(e){}})();</script>"
lang_re = re.compile(r'<span class="lang">.*?</a></span>', re.S)
MNAV_LANG = '<div class="mnav-lang"><span class="lang"><a href="#">UA</a><span>/</span><a href="#">RU</a></span></div>'

def segs(p):
    return [x for x in p.strip('/').split('/') if x]

def reldir(dest, frm):
    r = os.path.relpath(dest if dest else '.', frm if frm else '.')
    return './' if r == '.' else r.replace(os.sep, '/') + '/'

def url_ru(P):
    return BASE + '/' + (P + '/' if P else '')

def url_ua(P):
    return BASE + '/ua/' + (P + '/' if P else '')

def ua_sitepaths():
    s = set()
    for f in glob.glob(os.path.join(ROOT, 'ua', '**', 'index.html'), recursive=True):
        rel = os.path.relpath(os.path.dirname(f), os.path.join(ROOT, 'ua')).replace(os.sep, '/')
        s.add('' if rel == '.' else rel)
    return s

def ru_pages():
    out = []
    for f in glob.glob(os.path.join(ROOT, '**', 'index.html'), recursive=True):
        rel = os.path.relpath(f, ROOT).replace(os.sep, '/')
        if rel.startswith('ua/') or '_build' in rel:
            continue
        d = os.path.dirname(rel)
        out.append((rel, d))  # d = sitepath ('' for home)
    return out

def set_canonical(t, url):
    return re.sub(r'<link rel="canonical"[^>]*>', lambda m: '<link rel="canonical" href="%s">' % url, t, count=1)

def set_og_url(t, url):
    return re.sub(r'(<meta property="og:url" content=")[^"]*(">)', lambda m: m.group(1) + url + m.group(2), t, count=1)

def set_hreflang(t, P):
    block = ('<link rel="alternate" hreflang="ru-UA" href="%s">\n'
             '<link rel="alternate" hreflang="uk-UA" href="%s">\n'
             '<link rel="alternate" hreflang="x-default" href="%s">') % (url_ru(P), url_ua(P), url_ru(P))
    t = re.sub(r'[ \t]*<link rel="alternate" hreflang="[^"]*"[^>]*>\n?', '', t)
    return re.sub(r'(<link rel="canonical"[^>]*>)', lambda m: m.group(1) + '\n' + block, t, count=1)

def set_switcher(t, ua_active, other_href):
    if ua_active:
        sw = '<span class="lang"><a class="on" href="#">UA</a><span>/</span><a href="%s">RU</a></span>' % other_href
    else:
        sw = '<span class="lang"><a href="%s">UA</a><span>/</span><a class="on" href="#">RU</a></span>' % other_href
    return lang_re.sub(lambda m: sw, t, count=0)   # wire ALL .lang (topbar + mobile menu)

def add_redirect(t):
    if MARK in t:
        return t
    return t.replace(HDR, REDIR + '\n' + HDR, 1) if HDR in t else t

def add_mnav_lang(t):
    if 'mnav-lang' in t:
        return t
    return re.sub(r'(<nav class="mnav"[^>]*>)', lambda m: m.group(0) + '\n  ' + MNAV_LANG, t, count=1)

def wire_ua(t, ua_dir, UA):
    """ua_dir like 'ua' or 'ua/remont-iphone'; fix assets + internal page links (mask .lang)."""
    prefix = '../' * len(segs(ua_dir))
    spans = []
    t = lang_re.sub(lambda m: (spans.append(m.group(0)) or '@@L%d@@' % (len(spans) - 1)), t)
    def repl(m):
        attr, h = m.group(1), m.group(2)
        if h.startswith(SKIP):
            return m.group(0)
        frag = ''
        path = h
        if '#' in path:
            i = path.index('#'); frag = path[i:]; path = path[:i]
        base = path.split('/')[-1]
        if base in ASSETS:
            return '%s="%s%s"' % (attr, prefix, base)
        cleanp = path[2:] if path.startswith('./') else path
        if '/' not in cleanp and cleanp.lower().endswith(IMG_EXT):
            sp_ru = ua_dir[3:].strip('/') if ua_dir.startswith('ua/') else ''
            return '%s="%s%s%s"' % (attr, '../' * len(segs(ua_dir)), (sp_ru + '/' if sp_ru else ''), cleanp)
        if path.endswith('/'):
            tgt = os.path.normpath(os.path.join(ua_dir, path)).replace(os.sep, '/')
            parts = [x for x in tgt.split('/') if x and x != '.']
            if parts and parts[0] == 'ua':
                parts = parts[1:]
            sp = '/'.join(parts)
            dest = ('ua/' + sp).rstrip('/') if sp in UA else sp
            if sp in UA and not sp:
                dest = 'ua'
            return '%s="%s%s"' % (attr, reldir(dest, ua_dir), frag)
        return m.group(0)
    t = re.sub(r'(href|src)="([^"]+)"', repl, t)
    for i, s in enumerate(spans):
        t = t.replace('@@L%d@@' % i, s)
    return t

def main():
    UA = ua_sitepaths()
    n_ua = n_ru = 0
    # UA pages
    for sp in sorted(UA):
        f = os.path.join(ROOT, 'ua', sp, 'index.html') if sp else os.path.join(ROOT, 'ua', 'index.html')
        t = open(f, encoding='utf-8').read()
        t = t.replace('<html lang="ru">', '<html lang="uk">')
        ua_dir = ('ua/' + sp).rstrip('/')
        t = wire_ua(t, ua_dir, UA)
        t = set_canonical(t, url_ua(sp))
        t = set_og_url(t, url_ua(sp))
        t = set_hreflang(t, sp)
        t = add_mnav_lang(t)
        t = set_switcher(t, True, reldir(sp, ua_dir))   # RU counterpart (wires topbar + mnav .lang)
        t = add_redirect(t)
        open(f, 'w', encoding='utf-8').write(t)
        n_ua += 1
    # RU pages that have a UA counterpart
    for rel, P in ru_pages():
        if P not in UA:
            continue
        f = os.path.join(ROOT, rel)
        t = open(f, encoding='utf-8').read()
        t = set_canonical(t, url_ru(P))
        t = set_og_url(t, url_ru(P))
        t = set_hreflang(t, P)
        ua_dir = ('ua/' + P).rstrip('/')
        t = add_mnav_lang(t)
        t = set_switcher(t, False, reldir(ua_dir, P))   # UA counterpart (wires topbar + mnav .lang)
        t = add_redirect(t)
        open(f, 'w', encoding='utf-8').write(t)
        n_ru += 1
    print("i18n_wire: UA-страниц обвязано %d, RU-страниц обвязано %d (UA sitepaths: %d)" % (n_ua, n_ru, len(UA)))

if __name__ == '__main__':
    main()
