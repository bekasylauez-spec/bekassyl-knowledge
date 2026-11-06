# Block 3 column types from LIRA geometry (colbeams.json, lcols.json) + As (colas.json) -> types/*.json, marks.json, rows.json, as_table.json
import json, math, collections, os
W = os.path.dirname(os.path.abspath(__file__)); T = os.path.join(W, '..', 'types')
CB = json.load(open(os.path.join(W, 'colbeams.json')))
AS = {}   # Bekassyl 06.11: «арматурасын тексермей барлығын 28 дік қоя сал» -> minimal symmetric layout, all Ø28
LC = json.load(open(os.path.join(W, 'lcols.json'), encoding='utf-8'))
A28 = math.pi * 2.8 ** 2 / 4
LAY = {'sq': [(3, 3), (4, 4), (5, 5), (6, 6)], 'rect': [(3, 4), (3, 5), (4, 5), (4, 6), (5, 6), (5, 7), (6, 7)]}
cols = []
for k, lv in CB.items():
    x, y = map(int, k.split(','))
    if x in (0, 53950): continue                                 # axes 22 / 33: neighbour blocks (Bekassyl 06.11)
    sec = [s for s in LC[k] if s[3].startswith('S0')][0][3].split()
    B, H = int(float(sec[2]) * 10), int(float(sec[3]) * 10)    # LIRA B x H, cm -> mm
    b, h = (min(B, H), max(B, H))                               # schema: 800 along x, 1200 along y
    fl = {}
    for z, secs in lv.items():
        z = float(z)
        if z <= -1.19 or z > 7.001: continue
        fl[round(z, 3)] = max(int(s.split('x')[1]) * 10 for s in secs)
    fl.setdefault(-0.05, 0)                                    # slab on grade without a beam
    floors = sorted(fl.items())
    splice = [-0.05] + ([4.5] if 4.5 in fl and fl[4.5] > 0 else [])
    a = AS.get(k)
    tot = a['tot'] if a else None
    sq = b == h
    lay = LAY['sq' if sq else 'rect'][0]
    if tot is not None:
        need = math.ceil(tot / A28 - 1e-9)
        for nb, nh in LAY['sq' if sq else 'rect']:
            if 2 * nb + 2 * (nh - 2) >= need: lay = (nb, nh); break
    cols.append(dict(k=k, x=x, y=y, b=b, h=h, floors=floors, splice=splice, tot=tot, au=a and a['au'], asf=a and a['asf'], asw=a and a['asw'], lay=lay))
geo = collections.OrderedDict()
for c in sorted(cols, key=lambda c: (-c['b'] * c['h'], len(c['floors']), str(c['floors']), c['y'], c['x'])):
    geo.setdefault((c['b'], c['h'], tuple(c['floors']), tuple(c['splice'])), []).append(c)
types = []; marks = {}; rows = []; sheet = 2
for gi, (g, cs) in enumerate(geo.items(), start=1):
    var = collections.OrderedDict()
    for c in cs: var.setdefault(c['lay'], []).append(c)
    for vi, (lay, cc) in enumerate(var.items(), start=1):
        mark = 'Км-%d' % gi if len(var) == 1 else 'Км-%d.%d' % (gi, vi)
        b, h, floors, splice = g
        nb, nh = lay
        n = 2 * nb + 2 * (nh - 2)
        t = dict(mark=mark, sheet='4.%d' % sheet, b=b, h=h, nb=nb, nh=nh, D=28, L0=-1.2, floors=[list(f) for f in floors], splice=list(splice), qty=len(cc),
                 cols=[c['k'] for c in cc], As_prov=round(n * A28, 2))
        types.append(t); sheet += 1
        for c in cc: marks[c['k']] = mark
        rows.append([mark, '%dх%d' % (b, h) if b != h else '%dх%d' % (b, b), '-1,200 / +7,000', '%d%%%%C28 А500С' % n, len(cc), t['sheet']])
rows.append(['Итого', '', '', '', sum(t['qty'] for t in types), ''])
json.dump(types, open(os.path.join(T, 'types.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(marks, open(os.path.join(T, 'marks.json'), 'w', encoding='utf-8'), ensure_ascii=False)
json.dump(rows, open(os.path.join(T, 'rows.json'), 'w', encoding='utf-8'), ensure_ascii=False)
for t in types:
    print('%-7s %s %4dx%-4d %d bars qty %2d floors %s splice %s cols %s' % (t['mark'], t['sheet'], t['b'], t['h'], 2 * t['nb'] + 2 * (t['nh'] - 2), t['qty'], t['floors'], t['splice'], t['cols']))
print('total', sum(t['qty'] for t in types), 'columns,', len(types), 'types')
