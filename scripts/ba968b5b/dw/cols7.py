# -*- coding: utf-8 -*-
"""7.x плита парақтарындағы «Колонна 40х40» блоктарын v4 колонналарымен ауыстыру (cols.py + colsfix.py геометриясы)."""
import ab, json, sys
import cols
sys.stdout.reconfigure(encoding='utf-8')
def run(s, dry=False):
    E = json.load(open('w/l%s.json' % s, encoding='cp1251'))
    bl = {}
    for e in E:
        a = e['e']
        if e['t'] == 'INSERT' and abs(a[2]-a[0]-900) < 5 and abs(a[3]-a[1]-900) < 5:
            bl[e['h']] = ((a[0]+a[2])/2, (a[1]+a[3])/2)
    xs = sorted(set(round(v[0]) for v in bl.values())); ys = sorted(set(round(v[1]) for v in bl.values()))
    assert len(xs) == 11 and len(ys) == 3, (s, len(xs), len(ys))
    ops = []; n = 0
    for h, (x, y) in bl.items():
        i = xs.index(round(x)) + 1; row = 'АБВ'[ys.index(round(y))]
        k = cols.kind(i, row)
        if k == 1: continue
        if k == 3: lo, hi = y-750, y+750
        elif row == 'А': lo, hi = y-200, y+600
        elif row == 'В': lo, hi = y-600, y+200
        else: lo, hi = y-400, y+400
        rect = [[x-200, lo], [x+200, lo], [x+200, hi], [x-200, hi]]
        ops += [{'t': 'erase', 'h': [h]},
                {'t': 'pl', 'p': rect, 'closed': True, 'layer': '0', 'lw': 30},
                {'t': 'hatch', 'pat': 'ANSI36', 'sc': 25, 'layer': '0', 'loops': [rect]},
                {'t': 'pl', 'p': [[x, lo-100], [x, hi+100]], 'layer': '0', 'ltype': 'CENTER2', 'color': 12, 'ltscale': 1},
                {'t': 'pl', 'p': [[x-300, y], [x+300, y]], 'layer': '0', 'ltype': 'CENTER2', 'color': 12, 'ltscale': 1}]
        n += 1
    print(s, n)
    if not dry: print(ab.run(ops + [{'t': 'save'}], 'c7_' + s, 900)[-80:])
for s in sys.argv[1:]: run(s)
