# Targeted views of the dumped strings: full notes, sheet/view titles, rebar families/types/shapes.
import sys, re
src, dst = sys.argv[1], sys.argv[2]
rows = []
for ln in open(src, encoding='utf-8').read().splitlines():
    c, p, t = ln.split('\t', 2); rows.append((int(c), p, t))
out = open(dst, 'w', encoding='utf-8')
def sec(title, pred, full=False, lim=300):
    hits = [(c, t) for c, p, t in rows if pred(t)]
    out.write('\n=== %s (%d)\n' % (title, len(hits)))
    for c, t in hits:
        if not full and len(t) > lim: t = t[:lim] + '…'
        out.write('%5d  %s\n' % (c, t))
# 1. notes with numbered items (full text)
sec('NOTES', lambda t: (('\\n2' in t or '\\r\\n2' in t or '\\n 2' in t) and len(t) > 60) or t.startswith('Примечани') and len(t) > 15, full=True)
# 2. titles of sheets / views
T = re.compile(r'^(Армирование|Армир|Схема|Опалуб|План|Разрез|Сечение|Узел|Узлы|Спецификац|Ведомост|Общие|Фрагмент|Деталь|Развертка|Фасад|КЖ|Нижн|Верхн|Доп|Фон|Основн|Каркас|Сетк|Выпуск|Монолит|Стен|Плит|Колонн|Ригел|Фундамент|Лестниц|Пилон|Перекр|Покрыт|Стык|Анкер|Нахл)', re.I)
sec('TITLES', lambda t: bool(T.match(t)) and len(t) < 160)
# 3. rebar related names
R = re.compile(r'Хомут|Скоба|Шпильк|Каркас|Сетк|Стержень|Стерж|Rebar|Арматур|Форма|П-образ|Г-образ|Обрамлен|Доп\.|Фон|Выпуск|Закладн|Поддерж|Подставк|Фиксатор|Лягушк|Кр-|Кп-|Шп', re.I)
sec('REBAR', lambda t: bool(R.search(t)) and len(t) < 160 and not t.startswith('adp:'))
out.close()
