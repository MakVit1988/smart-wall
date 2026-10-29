#!/usr/bin/env python3
"""Сверка новых текстов с источниками: доля совпадающих 5-словных фрагментов (шинглов).
Источники: smart-wall.ru (tools/data/content.json), nayada.ru и smartwall.nayada.ru (tools/data/nayada_*.json).
Запуск: python3 tools/check_uniqueness.py [порог_в_процентах]"""
import json, re, os, sys, html
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'texts'))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, 'tools', 'data')
K = 5
def words(t):
    t = html.unescape(re.sub(r'<[^>]+>', ' ', t)).lower().replace('ё', 'е')
    return re.findall(r'[a-zа-я0-9]+', t)
def shingles(ws): return {' '.join(ws[i:i + K]) for i in range(len(ws) - K + 1)}
src = set()
for p, d in json.load(open(os.path.join(D, 'content.json'), encoding='utf-8')).items(): src |= shingles(words(d['html']))
for f in ('nayada_corpus.json', 'nayada_landing.json'):
    for k, d in json.load(open(os.path.join(D, f), encoding='utf-8')).items(): src |= shingles(words(d['text']))
import products, categories_apps, info, articles
items = {}
for k, v in products.PRODUCT_TEXT.items(): items['products/' + k] = v
for k, v in categories_apps.TEXT.items(): items[k] = v
for k, v in info.TEXT.items(): items[k] = v
for a in articles.ARTICLES: items['stati/' + a['slug']] = a['html']
limit = float(sys.argv[1]) if len(sys.argv) > 1 else 8.0
rows = []
for k, v in items.items():
    sh = shingles(words(v))
    if not sh: continue
    rows.append((100.0 * len(sh & src) / len(sh), len(sh), k))
rows.sort(reverse=True)
tot_sh = sum(r[1] for r in rows); tot_hit = sum(r[0] * r[1] / 100 for r in rows)
print('страниц: %d, 5-грамм: %d, совпадений: %.1f%%' % (len(rows), tot_sh, 100 * tot_hit / tot_sh))
for pct, n, k in rows[:25]: print('%5.1f%%  %4d  %s%s' % (pct, n, k, '   <-- выше порога' if pct > limit else ''))
sys.exit(1 if rows and rows[0][0] > limit else 0)
