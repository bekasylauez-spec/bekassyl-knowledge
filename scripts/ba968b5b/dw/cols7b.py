# -*- coding: utf-8 -*-
"""7.x: колонна беттеріне тірелген контур/қабырға/размерлерді жаңа беттерге созу."""
import ab, json, sys, cols
sys.stdout.reconfigure(encoding='utf-8')
ONLY = ['LWPOLYLINE:Размеры', 'LWPOLYLINE:размер', 'LWPOLYLINE:Ригель', 'DIMENSION', 'LINE']
def run(s):
    E = json.load(open('w/l%s.json' % s, encoding='cp1251'))
    bl = [((e['e'][0]+e['e'][2])/2, (e['e'][1]+e['e'][3])/2) for e in E if e['t'] == 'INSERT' and abs(e['e'][2]-e['e'][0]-900) < 5 and abs(e['e'][3]-e['e'][1]-900) < 5]
    xs = sorted(set(round(v[0]) for v in bl)); ys = sorted(set(round(v[1]) for v in bl))
    ops = []
    for x, y in bl:
        i = xs.index(round(x)) + 1; row = 'АБВ'[ys.index(round(y))]; k = cols.kind(i, row)
        if k == 1: continue
        up = {'А': 400, 'В': 0, 'Б': 200 if k == 2 else 550}[row]
        dn = {'А': 0, 'В': 400, 'Б': 200 if k == 2 else 550}[row]
        if up: ops.append({'t': 'stretchwin', 'win': [x-260, y+150, x+260, y+260], 'd': [0, up], 'only': ONLY})
        if dn: ops.append({'t': 'stretchwin', 'win': [x-260, y-260, x+260, y-150], 'd': [0, -dn], 'only': ONLY})
    r = ab.run(ops + [{'t': 'save'}], 'c7b_' + s, 900)
    print(s, len(ops), sum(int(l.split()[2]) + int(l.split()[4]) for l in r.splitlines() if l.startswith('stretchwin moved')))
for s in sys.argv[1:]: run(s)
