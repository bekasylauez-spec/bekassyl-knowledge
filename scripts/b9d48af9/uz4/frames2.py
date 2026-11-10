import sys, ezdxf
doc = ezdxf.readfile(sys.argv[1]); msp = doc.modelspace()
keys = ['Схема расположения база', 'Схема расположения колонн и вертикальных', 'распорок и вертикальных связей на отм', 'балок площадки', 'подкрановых балок на отм', 'по нижним поясам', 'прогонов и связей', 'Разрезы 1 - 1', 'Разрезы 4 - 4', 'Общие данные (начало)', 'Ведомость рабочих', 'Техническая спецификация']
for e in msp.query('TEXT MTEXT INSERT'):
    if e.dxftype() == 'INSERT':
        continue
    t = e.dxf.text if e.dxftype() == 'TEXT' else e.plain_text()
    for k in keys:
        if k in t:
            p = e.dxf.insert; h = e.dxf.height if e.dxftype() == 'TEXT' else e.dxf.char_height
            print(round(p.x), round(p.y), round(h, 1), t[:70].replace('\n', ' '))
# frame candidates: big LINEs / polylines bbox stats near y of stamps
import collections
big = collections.Counter()
for e in msp.query('INSERT'):
    n = e.dxf.name
    if 'формат' in n.lower() or 'format' in n.lower() or 'рамк' in n.lower() or 'штамп' in n.lower() or 'A1' in n or 'А1' in n:
        big[n] += 1
print(big.most_common(20))
