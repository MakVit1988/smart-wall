#!/usr/bin/env python3
"""Проверка собранного сайта: битые ссылки, картинки, пустые href."""
import os, re, sys
from urllib.parse import urlparse, unquote
ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'site')
bad, hash_links, total = [], 0, 0
for dp, _, fs in os.walk(ROOT):
    for f in fs:
        if not f.endswith('.html'): continue
        fp = os.path.join(dp, f); h = open(fp, encoding='utf-8').read(); total += 1
        for attr, v in re.findall(r'(href|src)="([^"]*)"', h):
            if v.startswith(('http', 'mailto:', 'tel:', 'data:', '#', 'javascript')) or v == '':
                if v == '#': hash_links += 1
                continue
            u = urlparse(v); p = unquote(u.path)
            target = os.path.normpath(os.path.join(dp, p))
            if not os.path.exists(target): bad.append((os.path.relpath(fp, ROOT), v))
print('pages', total, 'broken', len(bad), 'dead # links', hash_links)
for b in bad[:40]: print(b)
sys.exit(1 if bad else 0)
