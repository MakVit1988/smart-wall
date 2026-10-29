#!/usr/bin/env python3
"""Собирает весь прототип (site/) в один HTML-файл: dist/smartwall-prototype.html.

Страницы, стили, скрипт и фотографии (сжатые) лежат внутри файла, переходы между
страницами идут через #-адреса, интернет нужен только для шрифта Onest.
Запуск: python3 tools/make_single.py
"""
import base64, io, json, mimetypes, os, re
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, 'site')
OUT = os.path.join(ROOT, 'dist', 'smartwall-prototype.html')
MAXSIDE, QUALITY = 1000, 62


def data_uri(path):
    ext = os.path.splitext(path)[1].lower()
    if ext in ('.jpg', '.jpeg'):
        im = Image.open(path).convert('RGB')
        im.thumbnail((MAXSIDE, MAXSIDE))
        buf = io.BytesIO()
        im.save(buf, 'JPEG', quality=QUALITY, optimize=True, progressive=True)
        raw, mime = buf.getvalue(), 'image/jpeg'
    else:
        raw = open(path, 'rb').read()
        mime = mimetypes.guess_type(path)[0] or ('image/svg+xml' if ext == '.svg' else 'application/octet-stream')
    return 'data:%s;base64,%s' % (mime, base64.b64encode(raw).decode())


def key_of(rel):
    rel = rel.replace(os.sep, '/')
    if rel.endswith('index.html'):
        return rel[:-len('index.html')]
    return rel  # 404.html


def main():
    pages, used = {}, set()
    for dp, _, fs in os.walk(SITE):
        for f in fs:
            if not f.endswith('.html'):
                continue
            p = os.path.join(dp, f)
            t = open(p, encoding='utf-8').read()
            title = re.search(r'<title>(.*?)</title>', t, re.S).group(1)
            body = re.search(r'<body[^>]*>(.*)</body>', t, re.S).group(1)
            body = re.sub(r'<script\b[^>]*></script>', '', body)
            # пути к картинкам -> ключи вида assets/photos/xxx.jpg
            def asset(m):
                used.add(m.group(1))
                return m.group(1)
            body = re.sub(r'(?:\.\./)*(assets/(?:photos|img)/[\w.\-]+)', asset, body)
            pages[key_of(os.path.relpath(p, SITE))] = {'t': title, 'b': body}
    css = open(os.path.join(SITE, 'assets/css/site.css'), encoding='utf-8').read()
    css = re.sub(r'(?:\.\./)*(assets/(?:photos|img)/[\w.\-]+)', lambda m: (used.add(m.group(1)), m.group(1))[1], css)
    js = open(os.path.join(SITE, 'assets/js/site.js'), encoding='utf-8').read()
    used.add('assets/img/logo-dark.svg')
    assets = {a: data_uri(os.path.join(SITE, a)) for a in sorted(used) if os.path.exists(os.path.join(SITE, a))}
    page0 = open(os.path.join(SITE, 'index.html'), encoding='utf-8').read()
    fonts = re.findall(r'<link[^>]+fonts\.(?:googleapis|gstatic)[^>]*>', page0)

    def j(o):
        return json.dumps(o, ensure_ascii=False).replace('</', '<\\/')

    html = '''<!DOCTYPE html>
<html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow"><title>SmartWall — прототип сайта</title>
%(fonts)s
<style>%(css)s</style></head>
<body>
<div id="app"></div>
<script id="pages" type="application/json">%(pages)s</script>
<script id="assets" type="application/json">%(assets)s</script>
<script>
(function () {
  var PAGES = JSON.parse(document.getElementById('pages').textContent);
  var ASSETS = JSON.parse(document.getElementById('assets').textContent);
  var blobs = {};
  function blobUrl(k) {
    if (blobs[k]) return blobs[k];
    var d = ASSETS[k]; if (!d) return k;
    var m = /^data:([^;]+);base64,(.*)$/.exec(d), bin = atob(m[2]), u = new Uint8Array(bin.length);
    for (var i = 0; i < bin.length; i++) u[i] = bin.charCodeAt(i);
    return (blobs[k] = URL.createObjectURL(new Blob([u], { type: m[1] })));
  }
  function resolveAssets(h) { return h.replace(/assets\\/(?:photos|img)\\/[\\w.\\-]+/g, function (k) { return blobUrl(k); }); }
  var icon = document.createElement('link'); icon.rel = 'icon'; icon.href = ASSETS['assets/img/logo-dark.svg']; document.head.appendChild(icon);

  function initPage() {
%(js)s
  }
  var cur = '';
  function pathOf(href, base) {
    var u = new URL(href, 'http://x/' + base), p = u.pathname.replace(/^\\//, '');
    if (p === '' || /index\\.html$/.test(p)) p = p.replace(/index\\.html$/, '');
    else if (/\\/$/.test(p) === false && PAGES[p + '/']) p += '/';
    return { p: p, h: u.hash.replace('#', '') };
  }
  function go(p, anchor) {
    if (!PAGES[p]) p = '404.html';
    var pg = PAGES[p];
    cur = p;
    document.title = pg.t;
    document.body.style.overflow = '';
    document.getElementById('app').innerHTML = resolveAssets(pg.b);
    initPage();
    if (anchor && document.getElementById(anchor)) document.getElementById(anchor).scrollIntoView();
    else window.scrollTo(0, 0);
  }
  function route() {
    var h = decodeURIComponent(location.hash.replace(/^#\\/?/, ''));
    var a = h.split('#'), p = a[0];
    if (p !== cur || !a[1]) go(p, a[1]);
    else if (a[1] && document.getElementById(a[1])) document.getElementById(a[1]).scrollIntoView();
  }
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[href]');
    if (!a || e.defaultPrevented || e.metaKey || e.ctrlKey) return;
    var href = a.getAttribute('href');
    if (/^(?:[a-z]+:|\\/\\/)/i.test(href)) { if (/^https?:/i.test(href)) a.target = '_blank'; return; }
    e.preventDefault();
    if (href.charAt(0) === '#') { var el = document.getElementById(href.slice(1)); if (el) el.scrollIntoView(); return; }
    var r = pathOf(href, cur), next = '#/' + r.p + (r.h ? '#' + r.h : '');
    if (location.hash === next) route(); else location.hash = next;
  });
  window.addEventListener('hashchange', route);
  route();
})();
</script></body></html>
''' % {'fonts': '\n'.join(fonts), 'css': css, 'pages': j(pages), 'assets': j(assets), 'js': js}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, 'w', encoding='utf-8').write(html)
    print('pages', len(pages), 'assets', len(assets), 'size %.1f MB' % (len(html.encode()) / 1e6))


if __name__ == '__main__':
    main()
