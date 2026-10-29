# SmartWall — прототип обновлённого сайта

Статичный прототип главной страницы `smart-wall.ru` с предложенными улучшениями.

- `index.html` — страница
- `assets/css/styles.css`, `assets/js/main.js` — стили и скрипты (без сборки и зависимостей, кроме шрифта Manrope с Google Fonts)
- `assets/img/` — изображения, скопированные с текущего сайта
- `docs/ANALYSIS.md` — анализ текущего сайта и список предложений
- `docs/COMPETITORS.md` — конкуренты и дилеры (Foldin, NAYADA, Перегородка LAB и др.)
- `directions/` — три направления визуала: `index.html` (обзор и сравнение), `a-architectural.html`, `b-material.html`, `c-tech.html`
- Макеты в Figma: https://www.figma.com/design/ah9k5Vlp798z1mjDmExiDE (страница «Направления визуала», фреймы A, B, C шириной 1280 px)
- `docs/original/` — скриншоты текущего сайта для сравнения

## Запуск

Откройте `index.html` в браузере или поднимите локальный сервер:

```bash
python3 -m http.server 8000
```

Формы работают в демо-режиме (данные никуда не отправляются). Страница помечена `noindex`.
