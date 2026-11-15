# Groups the dumped strings of a model by topic keywords (for the analysis of the reinforcement approach).
import sys, re, collections
tag, src, dst = sys.argv[1], sys.argv[2], sys.argv[3]
groups = collections.OrderedDict([
    ('notes', r'Примечан|Защитн|защитн|нахл[её]ст|Нахл[её]ст|анкеровк|Анкеровк|перепуск|Перепуск|вразбежку|сварк|ГОСТ|СП РК|СН РК|СНиП|бетон кл|Бетон кл|C\d\d/\d\d|В\d\d(,\d)?\b|W\d|F\d{2,3}'),
    ('sheets_views', r'Лист|лист|Схема|схема|Разрез|разрез|Сечение|сечение|Узел|узел|Опалубк|опалубк|План |план |Фасад|Развертк|развертк|Общие данные|Ведомость|ведомость|Спецификац|спецификац'),
    ('rebar', r'А500|A500|А400|A400|А240|A240|А-I|А-III|Ø|⌀|∅|Стерж|стерж|Хомут|хомут|Скоба|скоба|Шпильк|шпильк|Каркас|каркас|Сетк|сетк|Арматур|арматур|Rebar|rebar|Shape|Форма арм|Выпуск|выпуск|Фон|фон\b|Доп|доп\.|Основн|основн|Обрамлен|обрамлен|Поперечн|поперечн|Продольн|продольн|Конструктивн|конструктивн|Закладн'),
    ('elements', r'Стена|стена|Плита|плита|Колонн|колонн|Ригел|ригел|Балк|балк|Фундамент|фундамент|Пилон|пилон|Лестниц|лестниц|Диафрагм|Перекрыт|перекрыт|Ростверк|ростверк|Сва[яи]|Парапет|парапет|Приямок|Лифт|лифт|Шахт|шахт'),
    ('params_families', r'ADSK|Мрк\.|Арм\.|BI_|RAS|Weandrevit|BIM|Rebarbar|ModPlus|КЖ_|KJ|KM|Марка|марка|Позиция|позиция|Масса|масса|Длина|длина|Шаг|шаг'),
])
lines = open(src, encoding='utf-8').read().splitlines()
out = open(dst, 'w', encoding='utf-8')
for g, rx in groups.items():
    r = re.compile(rx); hits = []
    for ln in lines:
        c, p, t = ln.split('\t', 2)
        if len(t) > 400: t = t[:400] + '…'
        if r.search(t): hits.append((int(c), t))
    out.write('=== %s (%d)\n' % (g, len(hits)))
    for c, t in hits: out.write('%6d  %s\n' % (c, t))
out.close()
print(tag, 'lines', len(lines))
