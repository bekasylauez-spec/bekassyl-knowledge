# См-2 specification sheet in Bekassyl's A3 layout (copy of his См-1 A3 sheet): replaces the analog A2 sheet at x 1279100
import sys, json; sys.path.insert(0, 'wl'); from common import *
J = json.load(open('wl/a3.json', encoding='utf-8'))
A, B = J['A'], J['B']
SRC, DST, Y0 = 1071200.0, 1279100.0, 455939.0
DX = DST - SRC
ops = []
# 1) Шп1 sketch of the analog See-2 (old A2 sheet) -> cell 0 of the new ведомость
SHP = ['156C23', '156C2F', '156C07', '156C21', '156C22', '156C24', '156C1F', '156C27']
for h in SHP: ops.append(dict(t='clone', h=h, base=[0, 0], to=[-26900, 10192], tag='SHP:' + h))
# 2) old A2 sheet away
ops.append(dict(t='erase', h=[h for t, h, e in B if h not in ()]))
# 3) copy of the См-1 A3 sheet
inA = lambda e, x0, x1, y0, y1: e and e[0] - SRC >= x0 and e[2] - SRC <= x1 and e[1] - Y0 >= y0 and e[3] - Y0 <= y1
drop = set()
for t, h, e in A:
    if e is None: continue
    # cell 0 content (keep its grid block) and cells 7..10 (content and grid)
    if inA(e, 1990, 8350, 35700, 37900) and not (t == 'INSERT' and e[2] - e[0] > 5000): drop.add(h)
    if inA(e, 1990, 21000, 15700, 21810) and not (t == 'ACAD_TABLE'): drop.add(h)
for t, h, e in A:
    if h in drop: continue
    ops.append(dict(t='clone', h=h, base=[0, 0], to=[DX, 0], tag='A3c:' + h))
# 4) texts: ведомость cells, tables, stamp
TX = {  # cell1 Х1, cell2 Х2, cell3 Х3 (hoop sketches): top, bottom, L
    '141198': '320', '14118F': '220', '14119E': '980',
    '1411B4': '195', '1411AB': '95', '1411BA': '730',
    '14165F': '245', '141656': '145', '141665': '830',
    # cell4..6 П: name, top, bottom, L
    '1411E7': 'Ск1', '1411DA': '980', '1411DD': '980', '1411DF': '2130',
    '1411ED': 'Ск2', '1411EF': '740', '1411F2': '740', '1411F7': '1650',
    '1411FF': 'Ск3', '141205': '860', '141207': '860', '14120C': '1890',
    '152875': 'Спецификация элементов стены См-2', '152878': '5.9'}
for h, s in TX.items(): ops.append(dict(t='settext', h='A3c:' + h, s=s))
ops.append(dict(t='tset', h='A3c:141248', cells=[[0, 2, 'Стена См-2']]))
ops.append(dict(t='tset', h='A3c:1415ED', cells=[[6, 0, 'Стена См-2']]))
ops.append(dict(t='save'))
print('ops', len(ops), 'dropped', len(drop))
if '--run' in sys.argv:
    out = gx.run(ops, 'sm2a3'); print([l for l in out.splitlines() if 'ERR' in l or 'done' in l][-6:])
    import os
    m = json.load(open(os.environ['TEMP'] + '/gx_map.json', encoding='utf-8-sig'))
    print('SP', m.get('A3c:141248'), 'ST', m.get('A3c:1415ED'))
