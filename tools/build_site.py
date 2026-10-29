#!/usr/bin/env python3
"""Генератор прототипа сайта SmartWall (направление A).

Читает tools/data/*.json (контент smart-wall.ru) и собирает статический сайт в site/.
Запуск: python3 tools/build_site.py
"""
import json, re, os, sys, html, shutil
from urllib.parse import urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'site')
DATA = os.path.join(ROOT, 'tools', 'data')
content = json.load(open(os.path.join(DATA, 'content.json'), encoding='utf-8'))
data = json.load(open(os.path.join(DATA, 'data.json'), encoding='utf-8'))
imgmap = json.load(open(os.path.join(DATA, 'imgmap.json'), encoding='utf-8'))
for _q in data['faq']:  # в исходных данных к последнему ответу прилипли тексты форм и отзывов
    for _i, _line in enumerate(_q['a']):
        if _line.startswith('Оставьте заявку'):
            _q['a'] = _q['a'][:_i]; break
E = lambda s: html.escape(str(s), quote=True)
sys.path.insert(0, os.path.join(ROOT, 'tools', 'texts'))
import products as _pt, categories_apps as _ct, info as _it, articles as _at
TEXTS = {}
TEXTS.update(_ct.TEXT); TEXTS.update(_it.TEXT)
PRODUCT_TEXT = _pt.PRODUCT_TEXT
ARTICLES = _at.ARTICLES

PHONE = '+7 (499) 755-88-45'
PHONE_HREF = 'tel:+74997558845'
MAIL = 'Info@smart-wall.ru'
TBD = '<i class="tbd">уточнить</i>'

# ---------------------------------------------------------------- данные
def norm_code(s):
    s = s.upper().replace('Н', 'H').replace('К', 'K').replace('С', 'C').replace('А', 'A').replace('В', 'B')
    return s

PRODUCTS = [
    dict(slug='smartwall-h7', code='H7', cat='zvukoizoljacionnye-gluhie', tags='solid quiet', price=30877,
         sub='Акустические раздвижные стены максимальной звукоизоляции', img='p-h7.jpg', sound='до 54 дБ',
         specs=[('Звукоизоляция', 'до 54 дБ'), ('Максимальная высота', '6 м, до 7 м опционально'), ('Толщина', '100, 113 мм'),
                ('Вес 1 м²', '40–70 кг'), ('Заполнение секций', 'ЛДСП, шпон, МДФ окрашенный, пластик, ткань, магнитно-маркерная поверхность')]),
    dict(slug='smartwall-h7k', code='H7K', cat='zvukoizoljacionnye-gluhie', tags='solid quiet', price=30877,
         sub='Акустические раздвижные стены для дома и офиса', img='p-h7k.jpg', sound='46 дБ',
         specs=[('Звукоизоляция', '46 дБ'), ('Заполнение секций', 'ЛДСП, шпон, МДФ окрашенный, пластик, ткань, магнитно-маркерная поверхность'),
                ('Высота секций', '2000–6000 мм'), ('Толщина', '98 мм'), ('Вес 1 м²', '39 кг')]),
    dict(slug='smartwall-h5', code='H5', cat='zvukoizoljacionnye-gluhie', tags='solid', price=21872,
         sub='Акустические раздвижные стены для дома и офиса', img='cat-gluhie', sound='44 дБ',
         specs=[('Звукоизоляция', '44 дБ'), ('Максимальная высота', '4 м'), ('Толщина', '85, 123 мм'), ('Вес 1 м²', '29–62 кг'), ('Управление', 'механика')]),
    dict(slug='smartwall-h5k', code='H5K', cat='zvukoizoljacionnye-gluhie', tags='solid', price=21872,
         sub='Акустические раздвижные стены для потолков до 4 м', img='p-h5k.jpg', sound='42 дБ',
         specs=[('Звукоизоляция', 'до 42 дБ'), ('Высота потолков', 'до 4 м'), ('Профиль', 'алюминиевый по периметру секций'),
                ('Толщина', '85 мм'), ('Вес 1 м²', '25 кг'),
                ('Заполнение секций', 'ЛДСП, МДФ, шпон, ткани, обои и другие материалы'), ('Двери', 'установка двери невозможна')]),
    dict(slug='smartwall-h5f', code='H5F', cat='zvukoizoljacionnye-gluhie', tags='solid', price=26790,
         sub='Огнестойкие акустические стены из панелей СМЛ', img='p-h5f.jpg', sound='42–50 дБ',
         specs=[('Звукоизоляция', 'от 42 до 50 дБ'), ('Максимальная высота', '4 м'), ('Заполнение секций', 'негорючий материал СМЛ, окрашенный по RAL'),
                ('Класс горючести', 'КМ0, подтверждён сертификатом'), ('Двери', 'установка двери невозможна')]),
    dict(slug='smartwall-wg5', code='WG5', cat='zvukoizoljacionnye-stekljannye', tags='glass', price=38170,
         sub='Светопрозрачная трансформируемая система', img='p-wg5.jpg', sound='42 дБ',
         specs=[('Звукоизоляция', '42 дБ'), ('Максимальная высота', '3 м'), ('Толщина', '85 мм'), ('Стекло', '6 мм: прозрачное, тонированное, с декорирующей плёнкой')]),
    dict(slug='smartwall-g5', code='G5', cat='celnostekljannye-razdvizhnye-steny', tags='glass', price=22913,
         sub='Цельностеклянные раздвижные стены', img='p-g5.jpg', sound=None,
         specs=[('Стекло', 'закалённое 10 мм (высота до 3 м) или 12 мм (до 3,5 м)'), ('Подвес', 'на двух роликах к потолочному треку'),
                ('Двери', 'дверная секция у паркинга или мобильная дверь'), ('Отделка', 'цветные плёнки, узоры, пескоструйная обработка')]),
    dict(slug='smartwall-h5c', code='H5C', cat='zvukoizoljacionnye-kombi', tags='combi', price=34996,
         sub='Комбинированные стены: панели снизу, стекло сверху', img='cat-kombi', sound='42 дБ',
         specs=[('Звукоизоляция', '42 дБ'), ('Конструкция', 'низ из стандартных отделочных материалов, верх из прозрачного стекла'), ('Высота, толщина, вес', None)]),
]
PBYSLUG = {p['slug']: p for p in PRODUCTS}
PBYCODE = {p['code']: p for p in PRODUCTS}
CATS = [
    ('zvukoizoljacionnye-gluhie', 'Глухие', 'solid'),
    ('zvukoizoljacionnye-stekljannye', 'Стеклянные акустические', 'glass'),
    ('zvukoizoljacionnye-kombi', 'Комбинированные', 'combi'),
    ('celnostekljannye-razdvizhnye-steny', 'Цельностеклянные', 'full'),
]
APPS = [
    ('peregorodki-dlya-ofisov', 'Офисы', 'a-office.jpg'),
    ('peregorodki-dlya-biznes-centrov', 'Бизнес-центры', 'a-bc.jpg'),
    ('peregorodki-dlya-konferenc-zalov', 'Конференц-залы', 'a-conf.jpg'),
    ('peregorodki-dlja-peregovornyh-komnat', 'Переговорные', 'pr-president.jpg'),
    ('peregorodki-dlya-torgovyh-centrov', 'Торговые центры', 'a-mall.jpg'),
    ('peregorodka-dlya-magazina', 'Магазины', 'a-shop.jpg'),
    ('peregorodki-dlya-gostinic', 'Гостиницы', 'a-hotel.jpg'),
    ('peregorodki-dlya-shkoly', 'Школы', 'a-school.jpg'),
    ('peregorodki-dlya-detskih-sadov', 'Детские сады', 'a-kids.jpg'),
    ('peregorodki-dlya-sportivnyh-zalov', 'Спортивные залы', 'a-sport.jpg'),
    ('peregorodki-dlya-tancevalnyh-studij', 'Танцевальные студии', 'a-dance.jpg'),
    ('peregorodki-dlya-koncertnih-zalov', 'Концертные залы', 'a-concert.jpg'),
    ('peregorodki-dlya-kvartir', 'Квартиры', 'a-flat.jpg'),
]
APPSET = {a[0] for a in APPS}
TYPES_SEO = [
    ('transformiruemye-peregorodki', 'Трансформируемые перегородки'),
    ('razdvizhnye-peregorodki', 'Раздвижные перегородки'),
    ('razdvizhnye-steny', 'Раздвижные стены'),
    ('razdvizhnye-steklyannye-peregorodki', 'Раздвижные стеклянные перегородки'),
    ('razdvizhnye-peregorodki-dlya-zonirovaniya', 'Перегородки для зонирования'),
    ('razdvizhnye-peregorodki-dlya-ofisa', 'Раздвижные перегородки для офиса'),
    ('zvukoizolyacionnye-peregorodki', 'Звукоизоляционные перегородки'),
    ('akusticheskie-razdvizhnye-peregorodki', 'Акустические раздвижные перегородки'),
    ('peregorodki-iz-zakalennogo-stekla', 'Перегородки из закалённого стекла'),
]
SHORT = {
    'about': 'О компании', 'proizvodstvo': 'Производство', 'sertifikaty': 'Сертификаты', 'otzyvy': 'Отзывы', 'partnerstvo': 'Партнёрство', 'kontakty': 'Контакты',
    'konsultacija': 'Консультация', 'dizajn': 'Дизайн', 'montazh': 'Монтаж и демонтаж', 'garantii': 'Гарантии', 'dostavka-razdvizhnyh-peregorodok': 'Доставка',
    'oplata-razdvizhnyh-peregorodok': 'Оплата', 'kak-jeto-rabotaet': 'Как это работает', 'vidy-otdelok': 'Виды отделок', 'faq': 'Вопросы и ответы', 'stati': 'Статьи',
    'news': 'Новости', 'video': 'Видео', 'kalkulyator': 'Калькулятор', 'primenenie': 'Где применяют', 'politika-konfidencialnosti': 'Политика конфиденциальности',
}
SHORT.update({a[0]: a[1] for a in APPS})
SHORT.update({a[0]: a[1] for a in TYPES_SEO})
SHORT.update({c[0]: c[1] for c in CATS})
GROUPS = [
    ('Компания', ['about', 'proizvodstvo', 'sertifikaty', 'otzyvy', 'partnerstvo', 'kontakty']),
    ('Услуги', ['konsultacija', 'dizajn', 'montazh', 'garantii', 'dostavka-razdvizhnyh-peregorodok', 'oplata-razdvizhnyh-peregorodok']),
    ('Знания', ['kak-jeto-rabotaet', 'vidy-otdelok', 'faq', 'stati', 'news', 'video']),
    ('Типы перегородок', [c[0] for c in CATS] + [t[0] for t in TYPES_SEO]),
    ('Где применяют', [a[0] for a in APPS]),
]
PROJ_TYPE = {
    'alkogolnaja-kompanija': 'Офисы', 'bank-v-kazahstane': 'Офисы', 'bc-prezident-g-ekaterinburg': 'Бизнес-центры', 'biznes-centr-oazis': 'Бизнес-центры',
    'bolshoj-teatr': 'Культура', 'hollidej-inn-jekspress-sheremetevo': 'Отели', 'kompanija-1s': 'Офисы', 'konsaltingovaja-kompanija-cbre': 'Офисы',
    'krasnye-holmy': 'Бизнес-центры', 'miratorg': 'Офисы', 'ofis-itella-connexion': 'Офисы', 'ofis-kompanii-paulig': 'Офисы', 'ofis-mail-ru': 'Офисы',
    'prostranstvo-dlja-uspeshnyh-peregovorov-kompanii-weatherford': 'Офисы', 'rosbank-nizhnij-novgorod': 'Офисы', 'shkola-olimp': 'Образование',
    'shkola': 'Образование', 'smartwall-v-afimolle': 'Торговые центры', 'tancevalnaja-studija': 'Танцы и спорт', 'vysshee-uchebnoe-zavedenie': 'Образование',
}
TYPE_APP = {'Офисы': 'peregorodki-dlya-ofisov', 'Бизнес-центры': 'peregorodki-dlya-biznes-centrov', 'Образование': 'peregorodki-dlya-shkoly',
            'Культура': 'peregorodki-dlya-koncertnih-zalov', 'Отели': 'peregorodki-dlya-gostinic', 'Торговые центры': 'peregorodki-dlya-torgovyh-centrov',
            'Танцы и спорт': 'peregorodki-dlya-tancevalnyh-studij'}
TYPE_KEY = {t: 't%d' % i for i, t in enumerate(sorted(set(PROJ_TYPE.values())))}
ALIAS = {'products': 'produkciya', 'kontakty-smartwall': 'kontakty', 'dostavka': 'dostavka-razdvizhnyh-peregorodok', 'kompaniya-1s': 'projects/kompanija-1s', 'news/kompaniya-1s': 'news/1107'}

def short(t, n):
    if len(t) <= n: return t
    cut = t[:n].rsplit(' ', 1)[0].rstrip(',;:—-')
    return cut + '…'

def photo(url):
    u = url.replace('http://', 'https://')
    fn = imgmap.get(u)
    return fn

def catimg(key):
    for c in data['categories']:
        if key == 'cat-gluhie' and 'zvukoizoljacionnye-gluhie' in c['href']: return photo(c['img'])
        if key == 'cat-kombi' and 'zvukoizoljacionnye-kombi' in c['href']: return photo(c['img'])
    return None

# ---------------------------------------------------------------- проекты
PROJECTS = []
home_dates = {p['href'].rstrip('/').split('/')[-1]: p['date'] for p in data.get('home_projects', [])}
cards = {c['href'].rstrip('/').split('/')[-1]: c for c in data['projects']}
for path, d in content.items():
    if not path.startswith('projects/'): continue
    slug = path.split('/')[1]
    card = cards.get(slug, {})
    text = re.sub(r'<[^>]+>', ' ', d['html'])
    m = re.search(r'Продукты?:\s*([^<\n]+)', text)
    systems_raw = card.get('systems') or (m.group(1) if m else '')
    codes = []
    for tok in re.findall(r'[A-Za-zА-Яа-я]{1,2}\d[A-Za-zА-Яа-я]?', systems_raw):
        c = norm_code(tok)
        if c in PBYCODE and c not in codes: codes.append(c)
    gal = [photo(g) for g in d['gallery']]
    gal = [g for g in gal if g]
    cover = photo(card['img']) if card.get('img') else (gal[0] if gal else None)
    PROJECTS.append(dict(slug=slug, path=path, title=d['h1'], html=d['html'], gallery=gal, cover=cover or (gal[0] if gal else None),
                         codes=codes, type=PROJ_TYPE.get(slug, 'Другое'), date=home_dates.get(slug, '')))
PROJECTS.sort(key=lambda p: (p['date'] == '', ))  # стабильный порядок

# ---------------------------------------------------------------- пути и ссылки
class Ctx:
    def __init__(self, path): self.path = path; self.depth = len([s for s in path.split('/') if s]) if path else 0
    def pre(self): return '../' * self.depth
    def link(self, target):
        t = target.strip('/')
        return self.pre() + (t + '/index.html' if t else 'index.html')
    def asset(self, p): return self.pre() + 'assets/' + p
    def img(self, name): return self.asset(('photos/' if re.match(r'^[0-9a-f]{12}\.', name) else 'img/') + name)

def known(path): return path in PAGES

def fix_links(h, ctx):
    def rep_a(m):
        href = m.group(1)
        if href.startswith(('mailto:', 'tel:')): return m.group(0)
        u = urlparse(href)
        host = u.netloc.replace('www.', '')
        if host in ('smart-wall.ru', ''):
            p = u.path.strip('/')
            p = ALIAS.get(p, p)
            if re.search(r'\.(jpg|jpeg|png|pdf)$', u.path, re.I):
                fn = photo('https://smart-wall.ru' + u.path)
                if fn: return '<a href="%s"' % ctx.img(fn)
                return '<a href="https://smart-wall.ru%s" target="_blank" rel="noopener"' % u.path
            if known(p): return '<a href="%s"' % ctx.link(p)
            return '<a href="#" title="Страница не входит в прототип"'
        return '<a href="%s" target="_blank" rel="noopener"' % href
    h = re.sub(r'<a href="([^"]*)"', rep_a, h)
    def rep_i(m):
        fn = photo(m.group(1))
        if not fn: return ''
        return '<img src="%s" alt="%s" loading="lazy">' % (ctx.img(fn), m.group(2))
    h = re.sub(r'<img src="([^"]*)" alt="([^"]*)">', rep_i, h)
    h = re.sub(r'<a href="[^"]*">\s*</a>', '', h)
    return h

def regroup(h):
    """Длинные абзацы без переносов делим на группы по 3 предложения."""
    def split_p(m):
        inner = m.group(1)
        if '<' in inner or len(inner) < 700: return m.group(0)
        sents = re.split(r'(?<=[.!?])\s+(?=[А-ЯЁA-Z«"])', inner)
        out, cur = [], []
        for s in sents:
            cur.append(s)
            if sum(len(x) for x in cur) > 320: out.append(' '.join(cur)); cur = []
        if cur: out.append(' '.join(cur))
        return ''.join('<p>%s</p>' % o for o in out)
    return re.sub(r'<p>(.*?)</p>', split_p, h, flags=re.S)

SPEC_ROWS = [
    ('H5', '42', '100', '35', 'да', 'да', '900–1250', '2000–4000', 'да', 'нет', '2350'),
    ('H5K', '36', '85', '25', 'да', 'да', '900–1250', '2000–4000', 'нет', 'нет', '—'),
    ('H7', '46–50', '113', '39', 'да', 'да', '900–1250', '2000–6000', 'да', 'да', '2350 / 2500'),
    ('H7K', '46–50', '98', '39', 'да', 'да', '900–1250', '2000–6000', 'да', 'да', '2350 / 2500'),
    ('G5', 'не регламентируется', '10–12', '35', 'нет', 'да', '800–1200', '2000–3500', 'да', 'нет', '2000'),
    ('H5F', '36', '85', '25', 'да', 'да', '900–1250', '2000–4000', 'нет', 'нет', '—'),
    ('WG5', '41', '85', '45', 'нет', 'да', '900–1250', '2000–3000', 'да', 'нет', '2350'),
]
def spec_table():
    head = ['Система', 'Звукоизоляция, дБ', 'Толщина, мм', 'Вес, кг/м²', '1 ролик', '2 ролика', 'Ширина панели, мм', 'Высота панели, мм', 'Дверь 1-створч.', 'Дверь 2-створч.', 'Мин. высота с дверью, мм']
    return ('<table><thead><tr>%s</tr></thead><tbody>%s</tbody></table>'
            % (''.join('<th>%s</th>' % h for h in head), ''.join('<tr><td><b>SmartWall %s</b></td>%s</tr>' % (r[0], ''.join('<td>%s</td>' % c for c in r[1:])) for r in SPEC_ROWS)))

def orig_images(path, ctx, minkb=20, limit=9):
    h = content.get(path, {}).get('html', '')
    out = []
    for src, alt in re.findall(r'<img src="([^"]*)" alt="([^"]*)">', h):
        fn = photo(src)
        if not fn: continue
        fp = os.path.join(OUT, 'assets', 'photos', fn)
        if os.path.exists(fp) and os.path.getsize(fp) >= minkb * 1024 and fn not in [o[0] for o in out]: out.append((fn, alt))
    if not out: return ''
    return '<div class="pgal">%s</div>' % ''.join('<figure><img src="%s" alt="%s" loading="lazy"></figure>' % (ctx.img(fn), E(alt)) for fn, alt in out[:limit])

ORDER_STEPS = [
    ('Консультация', 'Менеджер выясняет задачу и помогает выбрать систему и отделку.'),
    ('Замер', 'Специалист выезжает на объект, снимает размеры и оценивает нагрузку на потолок.'),
    ('Проект и расчёт', 'Дизайн-проект с визуализацией и точная смета. Договор с графиком работ; авансовый платёж 70%% %s.' % '<i class="tbd">подтвердить</i>'),
    ('Производство', 'Изделия делают на собственном производстве в Московской области.'),
    ('Доставка и монтаж', 'Изделия приходят готовыми к установке, монтаж занимает один рабочий день.'),
    ('Сервис', 'Гарантия по договору и послегарантийное обслуживание.'),
]
def common_blocks(ctx):
    steps = ''.join('<li><b>%s.</b> %s</li>' % (t, d) for t, d in ORDER_STEPS)
    return ('<h2>Как проходит заказ</h2><ol>%s</ol><h2>Частые вопросы</h2>%s<p><a href="%s">Все вопросы и ответы</a></p>'
            % (steps, faq_block(data['faq'], 4), ctx.link('faq')))

COMMON_PAGES = APPSET | {c[0] for c in CATS} | {t[0] for t in TYPES_SEO}

def prose_html(path, ctx):
    if path in TEXTS:
        h = TEXTS[path]
        if path == 'kak-jeto-rabotaet': h += spec_table() + '<p class="note">Данные таблицы расходятся с карточками систем и сайтом NAYADA %s.</p>' % '<i class="tbd">сверить</i>' + orig_images(path, ctx, 30, 9)
        elif path in ('vidy-otdelok', 'sertifikaty', 'proizvodstvo'): h += orig_images(path, ctx, 25, 12)
        if path in COMMON_PAGES: h += common_blocks(ctx)
        return h
    d = content.get(path)
    if not d: return ''
    h = re.sub(r'\[/?caption[^\]]*\]', '', d['html'])
    h = re.sub(r'<h[2-4]>\s*</h[2-4]>', '', h)
    return regroup(fix_links(h, ctx))

# ---------------------------------------------------------------- компоненты
def page_title(path):
    if path in SHORT: return SHORT[path]
    d = content.get(path)
    return d['h1'] if d else path

def crumbs(ctx, items, plain=False):
    out = ['<a href="%s">Главная</a>' % ctx.link('')]
    for label, target in items:
        out.append('<i>/</i>')
        out.append('<a href="%s">%s</a>' % (ctx.link(target), E(label)) if target is not None else '<span>%s</span>' % E(label))
    return '<nav class="crumbs%s" aria-label="Навигация">%s</nav>' % (' crumbs--plain' if plain else '', ''.join(out))

NAV = [('produkciya', 'Системы'), ('primenenie', 'Где применяют'), ('projects', 'Проекты'), ('vidy-otdelok', 'Отделки'), ('about', 'Компания'), ('kontakty', 'Контакты')]

def group_of(path):
    first = path.split('/')[0] if path else ''
    if first in ('produkciya', 'products') or path in [c[0] for c in CATS]: return 'produkciya'
    if first == 'projects': return 'projects'
    if path in APPSET or first == 'primenenie': return 'primenenie'
    if path == 'vidy-otdelok': return 'vidy-otdelok'
    if path in ('about', 'proizvodstvo', 'sertifikaty', 'otzyvy', 'partnerstvo'): return 'about'
    if path == 'kontakty': return 'kontakty'
    return ''

def header(ctx, over=False):
    cur = group_of(ctx.path)
    nav = ''.join('<a href="%s"%s>%s</a>' % (ctx.link(p), ' aria-current="page"' if p == cur else '', l) for p, l in NAV)
    logo = 'logo.svg' if over else 'logo-dark.svg'
    return ('<header class="hdr%s"><div class="hdr__in"><a class="hdr__logo" href="%s" aria-label="SmartWall — на главную"><img src="%s" alt="SmartWall" width="120" height="34"></a>'
            '<nav class="hdr__nav" aria-label="Основное меню">%s</nav><a class="hdr__tel" href="%s">%s</a>'
            '<a class="btn btn--dark hdr__cta" href="%s">Рассчитать стоимость</a>'
            '<button class="burger" aria-label="Открыть меню" aria-expanded="false"><span></span><span></span><span></span></button></div></header>'
            % (' hdr--over' if over else '', ctx.link(''), ctx.asset('img/' + logo), nav, PHONE_HREF, PHONE, ctx.link('kalkulyator')))

def footer(ctx):
    sysl = ''.join('<a href="%s">SmartWall %s</a>' % (ctx.link('products/' + p['slug']), p['code']) for p in PRODUCTS)
    def col(title, slugs): return '<div><h4>%s</h4>%s</div>' % (title, ''.join('<a href="%s">%s</a>' % (ctx.link(s), E(SHORT[s])) for s in slugs))
    return ('<footer class="ftr"><div class="wrap"><div class="ftr__grid">'
            '<div><a class="ftr__logo" href="%s"><img src="%s" alt="SmartWall"></a><a class="ftr__tel" href="%s">%s</a><p><a href="mailto:%s">%s</a></p>'
            '<p style="margin-top:14px">Москва, Бережковская наб., 16А стр. 2<br>пн–пт 09:00–18:00</p></div>'
            '<div><h4>Системы</h4>%s</div>%s%s</div>'
            '<div class="ftr__legal"><span>© 2010–2026 Smart-Wall · торговая марка <a href="https://www.nayada.ru" target="_blank" rel="noopener" style="text-decoration:underline">NAYADA</a></span>'
            '<span><a href="%s">Политика конфиденциальности</a> · <a href="%s">Карта прототипа</a></span></div></div></footer>'
            % (ctx.link(''), ctx.asset('img/logo.svg'), PHONE_HREF, PHONE, MAIL, MAIL, sysl,
               col('Компания', ['about', 'proizvodstvo', 'sertifikaty', 'otzyvy', 'partnerstvo', 'kontakty']),
               col('Услуги', ['konsultacija', 'dizajn', 'montazh', 'garantii', 'dostavka-razdvizhnyh-peregorodok', 'oplata-razdvizhnyh-peregorodok']),
               ctx.link('politika-konfidencialnosti'), ctx.link('karta-prototipa')))

def layout(path, title, body, over=False, desc=''):
    ctx = Ctx(path)
    return ('<!DOCTYPE html>\n<html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
            '<meta name="robots" content="noindex, nofollow"><title>%s</title><meta name="description" content="%s">'
            '<link rel="icon" href="%s"><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
            '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Onest:wght@300;400;500;600&display=swap">'
            '<link rel="stylesheet" href="%s"></head><body>'
            '<a class="skip" href="#main">К содержимому</a>%s<main id="main">%s</main>%s'
            '<div class="mbar"><a class="btn btn--line" href="%s">Позвонить</a><a class="btn btn--dark" href="%s">Рассчитать</a></div>'
            '<script src="%s"></script></body></html>'
            % (E(title), E(desc), ctx.asset('img/logo-dark.svg'), ctx.asset('css/site.css'), header(ctx, over), body, footer(ctx),
               PHONE_HREF, ctx.link('kalkulyator'), ctx.asset('js/site.js')))

HEAD_DEFAULT = ['hero.jpg', 'pr-olimp.jpg', 'a-bc.jpg', 'pr-cbre.jpg', 'a-conf.jpg', 'a-office.jpg', 'a-school.jpg']
def head_img(path):
    for slug, name, img in APPS:
        if slug == path: return img
    if path.startswith('products/') and path.split('/')[1] in PBYSLUG:
        pr = PBYSLUG[path.split('/')[1]]
        return catimg(pr['img']) if pr['img'].startswith('cat-') else pr['img']
    for c in CATS:
        if c[0] == path:
            pr = [x for x in PRODUCTS if x['cat'] == path][0]
            return catimg(pr['img']) if pr['img'].startswith('cat-') else pr['img']
    if path.startswith('projects/'):
        for pr in PROJECTS:
            if pr['path'] == path and pr['cover']: return pr['cover']
    if path in ('projects', 'otzyvy'): return 'pr-olimp.jpg'
    if path in ('produkciya', 'kalkulyator'): return 'hero.jpg'
    return HEAD_DEFAULT[sum(ord(ch) for ch in path) % len(HEAD_DEFAULT)]

def pagehead(ctx, h1, crumb_items, lead='', long=False, extra='', img=None):
    bg = img or head_img(ctx.path)
    return ('<section class="pagehead%s"><img class="pagehead__bg" src="%s" alt=""><div class="wrap">%s<div class="pagehead__row"><div><h1>%s</h1>%s</div>%s</div></div></section>'
            % (' pagehead--long' if long else '', ctx.img(bg), crumbs(ctx, crumb_items), E(h1), ('<p class="lead">%s</p>' % lead) if lead else '', extra))

def form(ctx, product='', idp='f', consent_link=True):
    return ('<form class="form" data-lead novalidate><input type="hidden" name="product" value="%s">'
            '<label class="f">Имя<input type="text" name="name" autocomplete="name"></label>'
            '<label class="f">Телефон *<input type="tel" name="phone" autocomplete="tel" placeholder="+7 (___) ___-__-__" required></label>'
            '<label class="f">Задача<textarea name="msg" placeholder="Помещение, размеры, сроки"></textarea></label>'
            '<label class="file">Планировка или ТЗ: <input type="file" name="file"></label>'
            '<label class="consent"><input type="checkbox" required><span>Согласен(а) на <a href="%s">обработку персональных данных</a></span></label>'
            '<p class="err" role="alert" hidden></p><button class="btn btn--dark" type="submit">Получить расчёт</button>'
            '<p class="ok" hidden><b>Спасибо!</b> Это демо-режим: в рабочей версии заявка уйдёт менеджеру. Менеджер перезвонит в течение <i class="tbd">N минут</i>.</p></form>'
            % (E(product), ctx.link('politika-konfidencialnosti')))

def lead_section(ctx, title='Оставьте заявку — замер бесплатно', product='', paper=True):
    return ('<section class="sec%s" id="lead"><div class="wrap leadsec"><div><p class="kicker kicker--dark">Бесплатный замер</p><h2>%s</h2>'
            '<p>Перезвоним, уточним задачу и подготовим расчёт. Можно прикрепить планировку или техническое задание.</p>'
            '<a class="leadsec__tel" href="%s">%s</a></div>%s</div></section>'
            % (' sec--paper' if paper else '', E(title), PHONE_HREF, PHONE, form(ctx, product)))

CALC_OPTIONS = ''.join('<option data-price="%d" value="%s">SmartWall %s — %s</option>'
                       % (p['price'], p['code'], p['code'], p['sound'] or 'цельное стекло') for p in sorted(PRODUCTS, key=lambda x: -x['price']))
def calc_block(ctx, selected=None, heading='Оцените стоимость за минуту', idx='02'):
    opts = CALC_OPTIONS
    if selected: opts = opts.replace('value="%s"' % selected, 'value="%s" selected' % selected)
    return ('<section class="calc" id="calc" data-calc><div class="calc__intro"><span class="idx idx--l">%s</span><h2>%s</h2>'
            '<p>Выберите систему и размеры — получите ориентир по цене «от». Точный расчёт и КП подготовит менеджер после бесплатного замера.</p></div>'
            '<div class="calc__panel"><label class="fld"><span>Система</span><select data-sys>%s</select></label>'
            '<label class="fld"><span>Ширина <b data-w-out></b></span><input type="range" min="1" max="20" step="0.5" value="6" data-w></label>'
            '<label class="fld"><span>Высота <b data-h-out></b></span><input type="range" min="2" max="5" step="0.1" value="3" data-h></label>'
            '<div class="calc__res"><div><small>Площадь</small><b data-area></b></div><div><small>Цена «от»</small><b data-price-out></b></div>'
            '<div class="calc__total"><small>Ориентир</small><b data-out></b></div></div>'
            '<a class="btn btn--light" href="#lead">Получить точный расчёт</a>'
            '<p class="calc__note">Менеджер перезвонит в течение <i class="tbd tbd--l">N минут</i>, КП — за <i class="tbd tbd--l">N часов</i>.</p></div></section>'
            % (idx, E(heading), opts))

def sec_head(idx, title, text=''):
    return '<div class="sec__head"><span class="idx">%s</span><h2>%s</h2>%s</div>' % (idx, E(title), ('<p>%s</p>' % text) if text else '')

def row(ctx, p):
    img = catimg(p['img']) if p['img'].startswith('cat-') else p['img']
    return ('<a class="row" href="%s" data-tags="%s"><div class="row__name"><h3>SmartWall %s</h3><span>%s</span></div>'
            '<div class="row__spec">%s</div><div class="row__spec">%s</div><div class="row__spec">%s</div>'
            '<div class="row__price"><small>от</small> %s ₽/м²</div><img class="row__img" src="%s" alt="" loading="lazy"></a>'
            % (ctx.link('products/' + p['slug']), p['tags'], p['code'], E(p['sub']), p['sound'] or '—', TBD, TBD,
               '{:,}'.format(p['price']).replace(',', ' '), ctx.img(img)))

def rows_table(ctx, prods, filters=False, count_id=None):
    head = '<div class="thead"><span>Система</span><span>Звукоизоляция</span><span>Срок</span><span>Гарантия</span><span>Цена</span><span></span></div>'
    return head + '<div class="rows">' + ''.join(row(ctx, p) for p in prods) + '</div>'

def tile(ctx, href, img, title, small=''):
    return ('<a class="tile" href="%s"><img src="%s" alt="" loading="lazy"><span>%s%s</span></a>'
            % (href, ctx.img(img), ('<small>%s</small>' % E(small)) if small else '', E(title)))

def proj_tile(ctx, p):
    return ('<a class="tile" href="%s" data-tags="%s"><img src="%s" alt="" loading="lazy"><span><small>%s%s</small>%s</span></a>'
            % (ctx.link(p['path']), TYPE_KEY.get(p['type'], 'x'), ctx.img(p['cover']), E(p['type']), (' · ' + E(p['date'])) if p['date'] else '', E(p['title'])))

def logos(ctx):
    names = [('c-sber.jpg', 'Сбербанк'), ('c-mailru.jpg', 'Mail.ru Group'), ('c-alfa.jpg', 'Альфа-Лизинг'), ('c-ge.jpg', 'General Electric'), ('c-castrol.jpg', 'Castrol'), ('c-1c.jpg', '1С')]
    return '<div class="logos">%s</div>' % ''.join('<img src="%s" alt="%s" loading="lazy">' % (ctx.img(f), n) for f, n in names)

MATS = [('Шпон', 'linear-gradient(90deg,#b98a5b,#a87644)', 'натуральное дерево'), ('ЛДСП EGGER', '#e8e3d9', 'более 200 декоров'), ('МДФ окрашенный', '#2f4a63', 'цвета по RAL'),
        ('Пластик', '#c8ccd0', ''), ('Ткань и обои', 'repeating-linear-gradient(45deg,#7c8b86 0 2px,#85948f 2px 4px)', ''), ('Магнитно-маркерная', '#fff;border:1px solid #d9dadb', 'для переговорных и классов'),
        ('Панели СМЛ по RAL', '#9fb8a6', 'негорючие'), ('Стекло', 'linear-gradient(135deg,#dfeef0,#b9d3d8)', 'прозрачное, окрашенное, с плёнкой')]
def mats_block(ctx):
    return '<div class="mats">%s</div><p class="note">Образцы условные — в рабочей версии заменим фотографиями реальных образцов. <a class="link" href="%s">Все виды отделок</a></p>' % (
        ''.join('<div><i style="background:%s"></i>%s%s</div>' % (bg, E(n), ('<small>%s</small>' % E(s)) if s else '') for n, bg, s in MATS), ctx.link('vidy-otdelok'))

def quiz_block(ctx):
    def q(n, legend, opts, name):
        return '<fieldset%s><legend>%s</legend>%s</fieldset>' % (' class="is-on"' if n == 1 else '', legend, ''.join(
            '<label class="opt"><input type="radio" name="%s" value="%s"><span>%s</span></label>' % (name, E(o), E(o)) for o in opts))
    return ('<section class="sec" id="quiz-sec"><div class="wrap leadsec"><div><p class="kicker kicker--dark">Подбор системы</p><h2>Не знаете, какая система подойдёт?</h2>'
            '<p>Ответьте на 4 вопроса — менеджер подберёт решение и пришлёт расчёт. Это быстрее, чем изучать весь каталог.</p></div>'
            '<form class="quiz" id="quiz" novalidate><div class="quiz__bar"><span></span></div><p class="quiz__step"></p>%s%s%s%s'
            '<fieldset><legend>Куда отправить подбор?</legend><div class="form"><label class="f">Имя<input type="text" name="name"></label>'
            '<label class="f">Телефон *<input type="tel" name="phone" placeholder="+7 (___) ___-__-__"></label>'
            '<label class="consent"><input type="checkbox"><span>Согласен(а) на <a href="%s">обработку персональных данных</a></span></label></div></fieldset>'
            '<p class="err" role="alert" hidden></p><div class="quiz__nav"><button type="button" class="btn btn--line" data-back hidden>Назад</button>'
            '<button type="button" class="btn btn--dark" data-next>Далее</button></div>'
            '<p class="ok" hidden><b>Спасибо!</b> Это демо-режим: в рабочей версии подбор уйдёт менеджеру.</p></form></div></section>'
            % (q(1, 'Где будут использоваться перегородки?', ['Офисное здание', 'Школа / детский сад', 'Торговый центр', 'Жилое помещение'], 'object'),
               q(2, 'Площадь перегородок', ['15–50 м²', '50–100 м²', '100–200 м²', 'более 200 м²'], 'area'),
               q(3, 'Нужная звукоизоляция', ['Не требуется', '30–35 дБ', '35–42 дБ', '42–50 дБ'], 'sound'),
               q(4, 'Облицовочный материал', ['Стекло', 'ЛДСП / пластик', 'Шпон', 'Ткань'], 'finish'), ctx.link('politika-konfidencialnosti')))

def faq_block(items, n=None):
    items = items[:n] if n else items
    return '<div class="faq">%s</div>' % ''.join('<details><summary>%s</summary><div>%s</div></details>' % (E(i['q']), ''.join('<p>%s</p>' % E(a) for a in i['a'])) for i in items)

def side(ctx, path):
    for name, slugs in GROUPS:
        if path in slugs:
            lis = ''.join('<li><a href="%s"%s>%s</a></li>' % (ctx.link(s), ' aria-current="page"' if s == path else '', E(SHORT[s])) for s in slugs if known(s))
            return ('<aside class="side"><h4>%s</h4><ul>%s</ul><div class="side__cta"><p>Рассчитаем стоимость и приедем на замер бесплатно.</p>'
                    '<a class="btn btn--light" href="%s">Рассчитать стоимость</a></div></aside>' % (name, lis, ctx.link('kalkulyator')))
    return ('<aside class="side"><div class="side__cta"><p>Рассчитаем стоимость и приедем на замер бесплатно.</p><a class="btn btn--light" href="%s">Рассчитать стоимость</a></div></aside>'
            % ctx.link('kalkulyator'))

def rside(ctx, path):
    ps = projects_for_app(path)[:2] if path in APPSET else []
    if len(ps) < 2: ps = ps + [p for p in PROJECTS if p['slug'] in ('bolshoj-teatr', 'konsaltingovaja-kompanija-cbre', 'ofis-mail-ru') and p not in ps][:2 - len(ps)]
    tiles = ''.join(proj_tile(ctx, p) for p in ps)
    facts = ('<div class="rside__card"><h4>Коротко о системах</h4><ul><li>секции движутся по потолочному треку, пол не затрагивается</li><li>звукоизоляция до 54 дБ</li>'
             '<li>в секции можно встроить дверь</li><li>монтаж возможен без остановки работы офиса</li></ul></div>')
    card = ('<div class="rside__card"><h4>Связаться</h4><a class="tel" href="%s">%s</a><p>пн–пт 09:00–18:00</p><p><a class="link" href="%s">Рассчитать стоимость</a></p></div>'
            % (PHONE_HREF, PHONE, ctx.link('kalkulyator')))
    return '<aside class="rside">%s%s%s</aside>' % (tiles, facts, card)

def group_name(path):
    for name, slugs in GROUPS:
        if path in slugs: return name
    return None

def related_systems(ctx, codes=None):
    prods = [PBYCODE[c] for c in codes] if codes else PRODUCTS
    return '<div class="chips">%s</div>' % ''.join('<a href="%s">SmartWall %s</a>' % (ctx.link('products/' + p['slug']), p['code']) for p in prods)

def apps_tiles(ctx, apps=None, cls='tiles'):
    apps = apps or APPS
    return '<div class="%s">%s</div>' % (cls, ''.join(tile(ctx, ctx.link(s), img, name) for s, name, img in apps))

def projects_for_app(slug):
    types = [t for t, a in TYPE_APP.items() if a == slug]
    return [p for p in PROJECTS if p['type'] in types]

# ---------------------------------------------------------------- страницы
PAGES = {}
def add(path, fn): PAGES[path] = fn

def html_page_generic(path):
    d = content[path]; ctx = Ctx(path)
    grp = group_name(path)
    items = [(grp, None)] if grp else []
    items.append((page_title(path), None))
    body = pagehead(ctx, d['h1'], items, long=len(d['h1']) > 38)
    extra = ''
    if path in APPSET:
        ps = projects_for_app(path)
        extra += ('<section class="sec sec--paper"><div class="wrap">%s<div class="tiles">%s</div></div></section>' % (
            sec_head('', 'Наши проекты', 'Объекты этого типа, где установлены перегородки SmartWall.') if ps else '', ''.join(proj_tile(ctx, p) for p in ps[:6]))) if ps else ''
        extra = '<section class="sec"><div class="wrap">%s%s</div></section>' % (sec_head('', 'Подходящие системы', 'Подберём систему под задачу и бюджет.'), rows_table(ctx, PRODUCTS[:6])) + extra
    if path in [c[0] for c in CATS]:
        cat_p = [p for p in PRODUCTS if p['cat'] == path]
        extra = '<section class="sec"><div class="wrap">%s%s</div></section>' % (sec_head('', 'Системы в этой категории'), rows_table(ctx, cat_p))
    if path in [t[0] for t in TYPES_SEO]:
        extra = '<section class="sec"><div class="wrap">%s%s</div></section>' % (sec_head('', 'Системы SmartWall', 'Шесть основных систем: от цельного стекла до акустических панелей.'), rows_table(ctx, PRODUCTS[:6]))
    prose = prose_html(path, ctx)
    body += '<div class="wrap page page--3">%s<div class="prose">%s</div>%s</div>' % (side(ctx, path), prose, rside(ctx, path))
    body += extra + lead_section(ctx, paper=bool(extra) is False)
    return layout(path, d['title'] or d['h1'], body, desc=d['desc'])

def page_home():
    ctx = Ctx('')
    hero = ('<section class="hero"><img class="hero__img" src="%s" alt="Переговорная со стеклянными раздвижными перегородками SmartWall"><div class="hero__shade"></div>'
            '<div class="hero__body"><p class="kicker">Раздвижные перегородки · собственное производство с 2009 года</p><h1>Пространство, которое меняется за&nbsp;минуту</h1>'
            '<div class="hero__row"><p class="hero__sub">Стеклянные и глухие системы со звукоизоляцией до 54&nbsp;дБ. Замер, проект, производство и монтаж — одной командой.</p>'
            '<div class="hero__cta"><a class="btn btn--light" href="%s">Рассчитать стоимость</a><a class="link link--l" href="#systems">Смотреть системы&nbsp;↓</a></div></div></div></section>'
            % (ctx.img('hero.jpg'), ctx.link('kalkulyator')))
    facts = ('<section class="facts"><div class="facts__i"><b>до 54 дБ</b><span>звукоизоляция системы H7</span></div>'
             '<div class="facts__i"><b>3000+</b><span>реализованных проектов%s</span></div><div class="facts__i"><b>2009</b><span>собственное производство</span></div>'
             '<div class="facts__i"><b>от 21 872 ₽</b><span>за м² — цены на сайте</span></div></section>' % TBD)
    systems = ('<section class="sec sec--white" id="systems"><div class="wrap">%s%s<p class="note">Метки «уточнить» — данные, которые должна подтвердить компания (сроки производства и гарантия).</p>'
               '<p class="more"><a class="btn btn--line" href="%s">Все системы и фильтры</a></p></div></section>'
               % (sec_head('01', 'Системы', 'Шесть основных систем для разных задач: от цельного стекла до акустических панелей с максимальной изоляцией.'), rows_table(ctx, PRODUCTS[:6]), ctx.link('produkciya')))
    pr = [('01', 'Секции', 'Лёгкие рамы из алюминиевого профиля. Внутри — акустический наполнитель, стекло или их сочетание.'),
          ('02', 'Ролики и трек', 'Секции висят на роликах и едут по направляющей в потолке. Пол остаётся целым, напольное покрытие не вскрывают.'),
          ('03', 'Стык', 'Торцы смыкаются по системе «шип-паз», а уплотнители и магнитная лента закрывают щели: от них зависят децибелы.'),
          ('04', 'Паркинг', 'Открытая стена собирается в нише, у стены или в соседней комнате и освобождает весь зал.')]
    principle = ('<section class="sec sec--dark"><div class="wrap">%s<div class="steps4">%s</div><p class="more"><a class="btn btn--line" href="%s">Подробнее о принципе работы</a></p></div></section>'
                 % (sec_head('02', 'Как работает перегородка', 'Четыре узла, из которых складывается стена, исчезающая по команде.'),
                    ''.join('<div><b>%s</b><h3>%s</h3><p>%s</p></div>' % x for x in pr), ctx.link('kak-jeto-rabotaet')))
    band = ('<section class="band"><img class="band__bg" src="%s" alt=""><div class="band__in"><h2>Один зал — два помещения, и обратно</h2>'
            '<p>Секции складываются в паркинг за считанные минуты. В закрытом виде перегородка выглядит как капитальная стена, в открытом — освобождает весь зал.</p>'
            '<a class="btn btn--light" href="%s">Рассчитать стоимость</a></div></section>' % (ctx.img('pr-olimp.jpg'), ctx.link('kalkulyator')))
    finishes = '<section class="sec sec--paper"><div class="wrap">%s%s</div></section>' % (sec_head('04', 'Отделки', 'Панели заполняются тем, что подходит интерьеру. Подберём материал и цвет под ваш проект.'), mats_block(ctx))
    order = ['shkola-olimp', 'bolshoj-teatr', 'konsaltingovaja-kompanija-cbre']
    big = sorted([p for p in PROJECTS if p['slug'] in order], key=lambda p: order.index(p['slug']))
    projects = ('<section class="sec sec--dark" id="projects"><div class="wrap">%s<div class="projbig">%s</div>%s<p class="more"><a class="btn btn--line" href="%s">Все проекты</a></p></div></section>'
                % (sec_head('05', 'Проекты', 'Большой театр, Mail.ru, CBRE, Афимолл Сити — и более 3000 объектов%s.' % TBD.replace('<i class="tbd">', '<i class="tbd tbd--l">')), ''.join(proj_tile(ctx, p) for p in big), logos(ctx), ctx.link('projects')))
    areas = ('<section class="sec" style="padding-bottom:0"><div class="wrap">%s</div></section><div class="mosaic">%s</div>'
             % (sec_head('06', 'Где применяют', 'Офисы, бизнес-центры, школы, гостиницы, театры, спортивные залы и частные интерьеры.'), ''.join(tile(ctx, ctx.link(sl), im, nm) for sl, nm, im in APPS[:8])))
    rs = [('Собственное производство', 'Профиль, панели, направляющие и отделку выпускаем сами в Домодедовском районе Московской области.'),
          ('Полный цикл', 'Дизайн-проект, изготовление, доставка, монтаж и сервис — в одной команде, без передачи между подрядчиками.'),
          ('Монтаж за один день', 'Изделия приходят готовыми, на объекте ничего не режут и не подгоняют. Работа офиса продолжается.'),
          ('Без перепланировки', 'Для установки не нужно согласование перепланировки, а перегородку можно переставить или убрать.'),
          ('Отделка под проект', 'Шпон, ЛДСП EGGER, окраска по RAL, ткань, стекло и магнитно-маркерные поверхности — под ваш интерьер.'),
          ('Двери и стекло в секциях', 'В полотно встраивают двери, а чтобы добавить света, часть секций заменяют стеклянными.')]
    reasons = ('<section class="sec sec--paper"><div class="wrap">%s<div class="reasons">%s</div></div></section>'
               % (sec_head('07', 'Почему SmartWall', 'Шесть причин, по которым нас выбирают для офисов, школ, отелей и частных интерьеров.'),
                  ''.join('<div><h3>%s</h3><p>%s</p></div>' % x for x in rs)))
    revs = data['reviews'][:2]
    reviews = ('<section class="sec"><div class="wrap">%s<div class="reviews">%s</div><p class="more"><a class="btn btn--line" href="%s">Все отзывы</a></p></div></section>'
               % (sec_head('08', 'Отзывы клиентов'), ''.join(
                   '<figure class="rev"><div class="rev__h"><img src="%s" alt="%s" loading="lazy"><div><b>%s</b><span>%s</span></div></div><p>%s</p></figure>' % (
                       ctx.img(photo(r['logo'])), E(r['company']), E(r['company']), E(r['role']), E(r['text'])) for r in revs), ctx.link('otzyvy')))
    arts = ('<section class="sec" style="padding-bottom:0"><div class="wrap">%s</div></section>%s'
            % (sec_head('09', 'Статьи', 'Как выбрать систему, стекло и отделку, на что смотреть при монтаже и акустике.'), art_cards(ctx, ARTICLES[:3])))
    faq = '<section class="sec"><div class="wrap">%s%s<p class="more"><a class="link" href="%s">Все вопросы и ответы</a></p></div></section>' % (
        sec_head('10', 'Частые вопросы'), faq_block(data['faq'], 5), ctx.link('faq'))
    body = hero + facts + systems + principle + band + calc_block(ctx, idx='03') + finishes + projects + areas + reasons + quiz_block(ctx) + reviews + arts + faq + lead_section(ctx, paper=True)
    return layout('', 'Smart Wall | Системы раздвижных перегородок', body, over=True, desc='Раздвижные перегородки SmartWall для зонирования пространства: глухие, стеклянные, комбинированные. Собственное производство. ' + PHONE)

def page_produkciya():
    ctx = Ctx('produkciya')
    cats = ''.join('<a class="cat" href="%s"><img src="%s" alt="" loading="lazy"><div><h3>%s</h3><p>%s</p><span>Смотреть →</span></div></a>' % (
        ctx.link(c['href'].replace('https://smart-wall.ru/', '').strip('/')), ctx.img(photo(c['img'])), E(re.sub(r'\s*\(.*?\)', '', c['title'])), E(short(c['desc'], 170)))
        for c in data['categories'])
    flt = ('<div class="filters" data-target=".rows .row"><button class="is-on" data-f="all">Все системы (%d)</button><button data-f="solid">Глухие</button>'
           '<button data-f="glass">Стеклянные</button><button data-f="combi">Комбинированные</button><button data-f="quiet">Звукоизоляция от 46 дБ</button></div>' % len(PRODUCTS))
    body = pagehead(ctx, 'Системы раздвижных перегородок', [('Системы', None)], 'Раздвижные перегородки SmartWall построены по принципу подвеса секций на роликах к потолочному треку. Выберите тип и сравните системы.')
    body += '<section class="sec"><div class="wrap">%s<div class="cats">%s</div></div></section>' % (sec_head('01', 'Типы перегородок'), cats)
    body += '<section class="sec sec--paper"><div class="wrap">%s%s%s<p class="note">Цены — «от», за м². Сроки и гарантия %s подтверждаются компанией.</p></div></section>' % (
        sec_head('02', 'Все системы', 'Сравните звукоизоляцию, срок и цену.'), flt, rows_table(ctx, PRODUCTS), TBD)
    body += calc_block(ctx, idx='03') + quiz_block(ctx) + lead_section(ctx)
    return layout('produkciya', 'Продукция SmartWall: раздвижные перегородки', body, desc='Каталог раздвижных перегородок SmartWall: глухие, стеклянные, комбинированные.')

def page_product(p):
    path = 'products/' + p['slug']; ctx = Ctx(path)
    d = content.get(path, {})
    h = d.get('html', '')
    h = re.sub(r'Максимальная высота\s*[-–]?\s*[^.]*?(?:м|метров|опция)\.?\s*', '', h) if False else h
    cleaners = [r'Максимальная высота\s*[-–]\s*[^.<]*\.\s*', r'Толщина\s*[-–]\s*[\d, ]+мм\s*', r'Вес м2\s*[-–]\s*[\d –-]+кг\s*', r'Управление\s*[-–]\s*механика\s*',
                r'Звукоизоляция\s*[-–]?\s*(?:до\s*)?\d+\s*Дб(?: по российскому стандарту)?\.?\s*', r'Максимальная высота\s*3\s*м\.\s*']
    for c in cleaners: h = re.sub(c, '', h)
    desc = regroup(fix_links(h, ctx))
    if p['slug'] in PRODUCT_TEXT: desc = PRODUCT_TEXT[p['slug']] + common_blocks(ctx)
    main = photo(d['gallery'][0]) if d.get('gallery') else None
    primary = catimg(p['img']) if p['img'].startswith('cat-') else p['img']
    imgs = [primary]
    if main and main not in imgs: imgs.append(main)
    for pr in PROJECTS:
        if p['code'] in pr['codes'] and pr['cover'] not in imgs and len(imgs) < 5: imgs.append(pr['cover'])
    thumbs = ''.join('<button class="%s" data-src="%s" aria-label="Фото %d"><img src="%s" alt=""></button>' % ('is-on' if i == 0 else '', ctx.img(im), i + 1, ctx.img(im)) for i, im in enumerate(imgs)) if len(imgs) > 1 else ''
    specs = ''.join('<tr><th>%s</th><td>%s</td></tr>' % (E(k), E(v) if v else TBD) for k, v in p['specs'])
    specs += '<tr><th>Срок производства</th><td>%s</td></tr><tr><th>Гарантия</th><td>%s</td></tr>' % (TBD, TBD)
    cat_name = [c[1] for c in CATS if c[0] == p['cat']][0]
    body = pagehead(ctx, 'SmartWall %s' % p['code'], [('Системы', 'produkciya'), (cat_name, p['cat']), ('SmartWall ' + p['code'], None)]) if False else ''
    body = ('<section class="prod-wrap"><div class="wrap" style="padding-top:28px">%s</div></section>' % crumbs(ctx, [('Системы', 'produkciya'), (cat_name, p['cat']), ('SmartWall ' + p['code'], None)], plain=True))
    body += ('<section class="prod-wrap"><div class="wrap prod"><div class="gal"><div class="gal__main"><img src="%s" alt="SmartWall %s"></div><div class="gal__thumbs">%s</div></div>'
             '<div class="prod__info"><h1>SmartWall %s</h1><p class="prod__sub">%s</p><p class="prod__price"><small>от</small> %s ₽/м²</p>'
             '<div class="prod__cta"><a class="btn btn--dark" href="#calc">Рассчитать стоимость</a><a class="btn btn--line" href="#lead">Заказать замер</a></div>'
             '<table class="specs">%s</table></div></div></section>'
             % (ctx.img(imgs[0]), p['code'], thumbs, p['code'], E(p['sub']), '{:,}'.format(p['price']).replace(',', ' '), specs))
    body += '<section class="sec sec--paper"><div class="wrap page" style="padding-top:0;padding-bottom:0"><aside class="side"><h4>Другие системы</h4><ul>%s</ul></aside><div class="prose">%s</div></div></section>' % (
        ''.join('<li><a href="%s"%s>SmartWall %s</a></li>' % (ctx.link('products/' + q['slug']), ' aria-current="page"' if q is p else '', q['code']) for q in PRODUCTS), desc or '<h2>Описание</h2><p>Подробное описание системы готовит компания.</p>')
    body += calc_block(ctx, selected=p['code'])
    ps = [x for x in PROJECTS if p['code'] in x['codes']]
    if ps:
        body += '<section class="sec"><div class="wrap">%s<div class="tiles">%s</div></div></section>' % (sec_head('03', 'Проекты с SmartWall %s' % p['code']), ''.join(proj_tile(ctx, x) for x in ps[:6]))
    body += lead_section(ctx, product='SmartWall ' + p['code'])
    return layout(path, d.get('title') or 'SmartWall ' + p['code'], body, desc=d.get('desc', ''))

def page_projects():
    ctx = Ctx('projects')
    types = sorted(set(p['type'] for p in PROJECTS))
    flt = '<div class="filters" data-target=".mosaic .tile" data-count="#pcount"><button class="is-on" data-f="all">Все</button>%s</div>' % ''.join('<button data-f="%s">%s</button>' % (TYPE_KEY[t], t) for t in types)
    body = pagehead(ctx, 'Проекты', [('Проекты', None)], 'Офисы, торговые центры, гостиницы, театры, вузы, школы и детские сады: как решена задача зонирования в каждом конкретном случае.')
    body += '<section class="sec" style="padding-bottom:0"><div class="wrap">%s<p class="note" style="margin:-16px 0 24px">Показано проектов: <b id="pcount">%d</b></p></div></section><div class="mosaic mosaic--3">%s</div>' % (flt, len(PROJECTS), ''.join(proj_tile(ctx, p) for p in PROJECTS))
    body += lead_section(ctx)
    return layout('projects', 'Проекты раздвижных перегородок SmartWall', body)

def page_project(p):
    path = p['path']; ctx = Ctx(path)
    text = fix_links(p['html'], ctx)
    text = re.sub(r'<p>\s*(?:<br>\s*)*Продукты?:.*?</p>', '', text, flags=re.S)
    text = re.sub(r'(?:<br>\s*)*Продукты?:[^<]*', '', text)
    text = regroup(text)
    sys = ('<p style="margin-top:28px"><b>Системы в проекте</b></p>' + related_systems(ctx, p['codes'])) if p['codes'] else ''
    gal = ''.join('<figure><img src="%s" alt="%s" loading="lazy"></figure>' % (ctx.img(g), E(p['title'])) for g in p['gallery'])
    others = [q for q in PROJECTS if q['slug'] != p['slug'] and q['type'] == p['type']][:3]
    if len(others) < 3: others += [q for q in PROJECTS if q['slug'] != p['slug'] and q not in others][:3 - len(others)]
    app = TYPE_APP.get(p['type'])
    body = pagehead(ctx, p['title'], [('Проекты', 'projects'), (p['title'], None)], long=True,
                    extra='<p class="kicker kicker--dark" style="margin:0">%s%s</p>' % (E(p['type']), (' · ' + E(p['date'])) if p['date'] else ''))
    body += ('<section class="sec"><div class="wrap"><div class="page" style="padding:0"><aside class="side"><h4>О проекте</h4><ul><li><a href="%s">Тип объекта: %s</a></li>%s</ul></aside>'
             '<div><div class="prose">%s%s</div></div></div>%s</div></section>'
             % (ctx.link(app) if app and known(app) else '#', E(p['type']), '<li><a href="%s">Все проекты</a></li>' % ctx.link('projects'), text, sys,
                ('<div class="tiles" style="margin-top:48px;grid-template-columns:repeat(2,1fr)">%s</div>' % ''.join(
                    '<figure class="tile" style="aspect-ratio:3/2"><img src="%s" alt="" loading="lazy"></figure>' % ctx.img(g) for g in p['gallery'])) if p['gallery'] else ''))
    body += '<section class="sec sec--paper"><div class="wrap">%s<div class="tiles">%s</div></div></section>' % (sec_head('', 'Другие проекты'), ''.join(proj_tile(ctx, q) for q in others))
    body += lead_section(ctx, 'Нужна перегородка для вашего объекта?', paper=False)
    return layout(path, content[path]['title'] or p['title'], body, desc=content[path]['desc'])

def page_primenenie():
    ctx = Ctx('primenenie')
    body = pagehead(ctx, 'Где применяют перегородки SmartWall', [('Где применяют', None)], 'Офисы, торговые и бизнес-центры, гостиницы, образовательные и государственные учреждения, театры, спортивные центры и частные интерьеры.')
    body += '<div class="mosaic mosaic--3">%s</div>' % ''.join(tile(ctx, ctx.link(sl), im, nm) for sl, nm, im in APPS)
    body += lead_section(ctx)
    return layout('primenenie', 'Где применяют раздвижные перегородки SmartWall', body)

def page_news():
    ctx = Ctx('news')
    items = sorted(data['news'], key=lambda n: n['date'], reverse=True)
    cards = ''
    for n in items:
        slug = n['href'].replace('https://smart-wall.ru/', '').strip('/')
        slug = ALIAS.get(slug, slug)
        cards += '<a class="nc" href="%s"><img src="%s" alt="" loading="lazy"><time datetime="%s">%s</time><h3>%s</h3></a>' % (ctx.link(slug) if known(slug) else '#', ctx.img(photo(n['img'])) if photo(n['img']) else '', n['date'], n['date'], E(n['title']))
    body = pagehead(ctx, 'Новости компании', [('Знания', None), ('Новости', None)]) + '<section class="sec"><div class="wrap"><div class="news">%s</div></div></section>' % cards
    return layout('news', 'Новости компании SmartWall', body)

def page_article(path):
    d = content[path]; ctx = Ctx(path)
    date = ''
    for n in data['news']:
        if n['href'].rstrip('/').endswith('/' + path.split('/')[-1]): date = n['date']
    body = pagehead(ctx, d['h1'], [('Новости', 'news'), (d['h1'], None)], long=True)
    body += '<div class="wrap page">%s<div class="prose">%s%s</div></div>' % (side(ctx, 'news'), ('<p class="art__date">%s</p>' % date) if date else '', prose_html(path, ctx))
    body += lead_section(ctx)
    return layout(path, d['title'] or d['h1'], body, desc=d['desc'])

def art_cards(ctx, items):
    return '<div class="articles">%s</div>' % ''.join('<a href="%s"><small>%s</small><h3>%s</h3><p>%s</p><span>Читать →</span></a>' % (ctx.link('stati/' + a['slug']), E(a['tag']), E(a['title']), E(a['lead'])) for a in items)

def page_stati():
    ctx = Ctx('stati')
    intro = ''.join(re.findall(r'<p>.*?</p>', content['stati']['html'], flags=re.S)[:3])
    intro = fix_links(intro, ctx)
    cards = ''.join(tile(ctx, ctx.link(c['href'].replace('https://smart-wall.ru/', '').strip('/')) if known(c['href'].replace('https://smart-wall.ru/', '').strip('/')) else '#', photo(c['img']), c['title']) for c in data['stati'] if photo(c['img']))
    body = pagehead(ctx, 'Статьи о раздвижных перегородках', [('Знания', None), ('Статьи', None)], 'Как устроены системы, что учесть при выборе и монтаже, как подобрать стекло, отделку и звукоизоляцию.')
    body += '<section class="sec" style="padding-bottom:0"><div class="wrap"><div class="prose" style="margin-bottom:40px">%s</div></div></section>' % intro
    body += art_cards(ctx, ARTICLES)
    body += '<section class="sec"><div class="wrap">%s</div></section><div class="mosaic mosaic--3">%s</div>' % (sec_head('', 'Разделы по типам перегородок'), cards)
    body += lead_section(ctx)
    return layout('stati', 'Статьи о раздвижных перегородках SmartWall', body)

def page_art(a):
    path = 'stati/' + a['slug']; ctx = Ctx(path)
    others = [x for x in ARTICLES if x is not a][:3]
    body = pagehead(ctx, a['title'], [('Статьи', 'stati'), (a['tag'], None)], long=True)
    body += '<div class="wrap page page--3">%s<div class="prose">%s</div>%s</div>' % (side(ctx, 'stati'), a['html'], rside(ctx, path))
    body += '<section class="sec sec--paper"><div class="wrap">%s</div></section>%s' % (sec_head('', 'Читайте также'), art_cards(ctx, others))
    body += lead_section(ctx)
    return layout(path, a['title'], body, desc=a['lead'])

def page_otzyvy():
    ctx = Ctx('otzyvy')
    revs = ''.join('<figure class="rev"><div class="rev__h"><img src="%s" alt="%s" loading="lazy"><div><b>%s</b><span>%s</span></div></div><p>%s</p></figure>' % (
        ctx.img(photo(r['logo'])), E(r['company']), E(r['company']), E(r['role']), E(r['text'])) for r in data['reviews'])
    body = pagehead(ctx, 'Отзывы', [('Компания', None), ('Отзывы', None)], 'Что говорят клиенты о перегородках SmartWall. Подлинность и разрешение на публикацию отзывов %s подтверждает компания.' % TBD)
    body += '<section class="sec"><div class="wrap"><div class="reviews">%s</div>%s</div></section>' % (revs, logos(ctx))
    body += lead_section(ctx)
    return layout('otzyvy', 'Отзывы о компании SmartWall', body)

def page_faq():
    ctx = Ctx('faq')
    body = pagehead(ctx, 'Вопросы и ответы', [('Знания', None), ('FAQ', None)])
    body += '<div class="wrap page">%s<div>%s</div></div>' % (side(ctx, 'faq'), faq_block(data['faq']))
    body += lead_section(ctx, 'Не нашли ответ? Спросите менеджера')
    return layout('faq', 'FAQ — часто задаваемые вопросы', body)

def page_kontakty():
    ctx = Ctx('kontakty')
    req = [r for r in data['contacts_requisites'][1:] if not re.match(r'(Банковские|Наименование банка|Расчетный|БИК|Корреспондентский)', r)]
    body = pagehead(ctx, 'Контакты', [('Компания', None), ('Контакты', None)])
    body += ('<section class="sec"><div class="wrap"><div class="contacts"><div><h3>Офис в Москве</h3><p>Бережковская наб., д. 16А, стр. 2, БЦ «Riverside Station»</p><p>пн–пт: 09:00–18:00<br>сб–вс: выходной</p></div>'
             '<div><h3>Производство</h3><p>142030, Московская обл., Домодедовский район, село Ям</p><p>пн–пт: 09:00–18:00</p></div>'
             '<div><h3>Связь</h3><p><a href="%s" class="link">%s</a></p><p><a href="mailto:%s" class="link">%s</a></p><p>Приём заявок: пн–пт 09:00–18:00</p></div></div>'
             '<div class="mapbox">Здесь будет карта (Яндекс.Карты): офис в 15 минутах от станции метро «Киевская»</div>'
             '<div class="req">%s</div><p class="note">Банковские реквизиты в прототип не включены.</p></div></section>' % (PHONE_HREF, PHONE, MAIL, MAIL, ''.join('<p>%s</p>' % E(r) for r in req)))
    body += lead_section(ctx, 'Напишите нам')
    return layout('kontakty', 'Контакты SmartWall — производителя раздвижных перегородок', body)

def page_video():
    ctx = Ctx('video')
    v = data['videos'][0] if data['videos'] else None
    body = pagehead(ctx, 'Видео', [('Знания', None), ('Видео', None)])
    body += '<div class="wrap page">%s<div class="prose prose--wide">%s</div></div>' % (side(ctx, 'video'), (
        '<h2>%s</h2><video controls preload="none" src="%s"></video><p class="note">Видео загружается с текущего сайта smart-wall.ru.</p>' % (E(v['title']), E(v['src']))) if v else '')
    body += lead_section(ctx)
    return layout('video', 'Видео — SmartWall', body)

def page_kalkulyator():
    ctx = Ctx('kalkulyator')
    body = pagehead(ctx, 'Калькулятор стоимости', [('Калькулятор', None)], 'Выберите систему и размеры — получите ориентир по цене «от». Это не коммерческое предложение: точный расчёт делает менеджер после бесплатного замера.')
    body += calc_block(ctx, idx='01') + lead_section(ctx, 'Получите точный расчёт', paper=False)
    return layout('kalkulyator', 'Калькулятор стоимости раздвижных перегородок', body)

def page_map():
    ctx = Ctx('karta-prototipa')
    def ul(title, items): return '<h2>%s</h2><ul>%s</ul>' % (title, ''.join('<li><a href="%s">%s</a></li>' % (ctx.link(p), E(t)) for p, t in items))
    groups = [('Главные', [('', 'Главная'), ('produkciya', 'Системы (каталог)'), ('kalkulyator', 'Калькулятор'), ('primenenie', 'Где применяют'), ('projects', 'Проекты'), ('kontakty', 'Контакты')]),
              ('Системы', [('products/' + p['slug'], 'SmartWall ' + p['code']) for p in PRODUCTS]),
              ('Проекты', [(p['path'], p['title']) for p in PROJECTS])]
    for name, slugs in GROUPS: groups.append((name, [(s, SHORT[s]) for s in slugs if known(s)]))
    arts = [(p, content[p]['h1']) for p in content if p.startswith('news/') and known(p)]
    groups.append(('Статьи (новые)', [('stati/' + a['slug'], a['title']) for a in ARTICLES]))
    groups.append(('Новости и материалы', arts))
    groups.append(('Служебные', [('politika-konfidencialnosti', 'Политика конфиденциальности')]))
    body = pagehead(ctx, 'Карта прототипа', [('Карта прототипа', None)], 'Служебная страница: все страницы прототипа, сгруппированные по разделам.')
    body += '<div class="wrap" style="padding-top:32px;padding-bottom:80px"><div class="prose prose--wide">%s</div></div>' % ''.join(ul(n, [(p if p != '' else '', t) for p, t in items]) for n, items in groups)
    return layout('karta-prototipa', 'Карта прототипа', body)

def page_404():
    ctx = Ctx('')
    body = pagehead(ctx, 'Страница не найдена', [('404', None)], 'Такой страницы нет или она не входит в прототип.')
    body += '<div class="wrap" style="padding:32px var(--pad) 96px"><a class="btn btn--dark" href="%s">На главную</a></div>' % ctx.link('')
    return layout('', 'Страница не найдена', body)

# ---------------------------------------------------------------- регистрация
for p in PRODUCTS: add('products/' + p['slug'], (lambda p=p: page_product(p)))
for p in PROJECTS: add(p['path'], (lambda p=p: page_project(p)))
SPECIAL = {'': page_home, 'produkciya': page_produkciya, 'projects': page_projects, 'primenenie': page_primenenie, 'news': page_news, 'stati': page_stati,
           'otzyvy': page_otzyvy, 'faq': page_faq, 'kontakty': page_kontakty, 'video': page_video, 'kalkulyator': page_kalkulyator, 'karta-prototipa': page_map}
for k, fn in SPECIAL.items(): add(k, fn)
SKIP = {'products', 'kontakty-smartwall', 'dostavka', 'news/1107', 'news/kompaniya-1s'}  # дубли
for path in content:
    if path in PAGES or path in SKIP or path.startswith('Info@') or path in ('home',): continue
    if path.startswith('news/'): add(path, (lambda path=path: page_article(path)))
    else: add(path, (lambda path=path: html_page_generic(path)))
for _a in ARTICLES: add('stati/' + _a['slug'], (lambda a=_a: page_art(a)))
# дубли новостей (две записи про 1С): оставляем первую
add('news/1107', lambda: page_article('news/1107'))

def build():
    if os.path.isdir(OUT):
        for name in os.listdir(OUT):
            if name == 'assets': continue
            p = os.path.join(OUT, name)
            shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
    count = 0
    for path, fn in sorted(PAGES.items()):
        html_text = fn()
        fp = os.path.join(OUT, path, 'index.html') if path else os.path.join(OUT, 'index.html')
        os.makedirs(os.path.dirname(fp), exist_ok=True)
        open(fp, 'w', encoding='utf-8').write(html_text)
        count += 1
    open(os.path.join(OUT, '404.html'), 'w', encoding='utf-8').write(page_404())
    print('pages:', count + 1)

if __name__ == '__main__':
    build()
