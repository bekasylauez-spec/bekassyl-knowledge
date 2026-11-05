# -*- coding: utf-8 -*-
"""2.x схемаларындағы колонналарды v4 бойынша өзгерту: Км-2 400×800, Км-3 400×1500 (ұзын жағы А–В бойымен, план Y).
Блок «Колонна 40х40» (динамикалық) → сол блоктың геометриясымен (контур lw 0.30, ANSI36 25, CENTER2 осьтер түс 12) тікбұрыш.
Бетке жанасқан размерлер мен ригель сызықтары бетпен бірге созылады (stretchwin only=DIMENSION / LWPOLYLINE:Ригель)."""
import ab, json, sys, re
sys.stdout.reconfigure(encoding='utf-8')
SH = json.load(open('w/sheets2.json'))
X1 = {'2.1': 15383, '2.2': 15383, '2.3': 15383, '2.4': 15383}
AY = {'2.1': 19703, '2.2': 17999, '2.3': 19758, '2.4': 19758}
PINK = [1, 4, 5, 6, 7, 8, 11]
def kind(i, row):            # i: 1..11, row: 'А','Б','В'
    if row == 'Б' and i in (1, 11): return 3
    if i in PINK and (row in 'АВ' or 4 <= i <= 8): return 2
    return 1
H = {2: 400, 3: 750}
def nodes(s):
    X0, Y0 = SH[s][0], SH[s][1]
    for k, row in enumerate('АБВ'):
        for i in range(1, 12):
            yield i, row, X0 + X1[s] + 6000 * (i - 1), Y0 + AY[s] + 6000 * k

def run(s, dry=False):
    ents = {}
    import km2_sec as K
    X0, Y0, X1_, Y1_ = SH[s]
    for e in K.listwin([X0, Y0, X1_, Y1_]):
        if e['t'] == 'INSERT':
            a = e['e']
            if abs((a[2] - a[0]) - 900) < 5 and abs((a[3] - a[1]) - 900) < 5:
                ents[(round((a[0] + a[2]) / 2), round((a[1] + a[3]) / 2))] = e['h']
    ops = []; done = []
    for i, row, x, y in nodes(s):
        k = kind(i, row)
        if k == 1: continue
        h = ents.get((round(x), round(y)))
        if h is None:
            near = [v for (cx, cy), v in ents.items() if abs(cx - x) < 30 and abs(cy - y) < 30]
            h = near[0] if near else None
        if h is None: print('no block at', s, i, row); continue
        hh = H[k]
        rect = [[x - 200, y - hh], [x + 200, y - hh], [x + 200, y + hh], [x - 200, y + hh]]
        ops += [{'t': 'erase', 'h': [h]},
                {'t': 'pl', 'p': rect, 'closed': True, 'layer': '0', 'lw': 30},
                {'t': 'hatch', 'pat': 'ANSI36', 'sc': 25, 'layer': '0', 'loops': [rect]},
                {'t': 'pl', 'p': [[x, y - hh - 100], [x, y + hh + 100]], 'layer': '0', 'ltype': 'CENTER2', 'color': 12, 'ltscale': 1},
                {'t': 'pl', 'p': [[x - 300, y], [x + 300, y]], 'layer': '0', 'ltype': 'CENTER2', 'color': 12, 'ltscale': 1},
                {'t': 'stretchwin', 'win': [x - 260, y + 190, x + 260, y + 210], 'd': [0, hh - 200], 'only': ['DIMENSION', 'LWPOLYLINE:Ригель']},
                {'t': 'stretchwin', 'win': [x - 260, y - 210, x + 260, y - 190], 'd': [0, -(hh - 200)], 'only': ['DIMENSION', 'LWPOLYLINE:Ригель']}]
        done.append((i, row, k))
    print(s, 'columns', len(done))
    if not dry:
        print(ab.run(ops + [{'t': 'save'}], 'cols_' + s, 900)[-300:])
    return done

if __name__ == '__main__':
    for s in sys.argv[1:]: run(s)
