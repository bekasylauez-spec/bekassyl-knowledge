# A3 specification sheet of a wall = copy of the См-2 A3 sheet 5.9 (Bekassyl's layout): ведомость деталей one column left,
# spec right, steel summary bottom, A3 stamp. Ведомость cells are rebuilt from the 5.9 cells (hoop / П / Шп1 types).
# usage: python wl/a3make.py sm1|sm3 [--run]
import sys, os, json; sys.path.insert(0, 'wl'); from common import *
SRC, Y0 = 1192200.0, 455939.0   # 5.9 after the sheets were packed (05.11); f59.json is relative to it
R59 = json.load(open('wl/f59.json'))
CEN = [36799, 34799, 32799, 30799, 28799, 26799, 24799]               # 5.9 cell centres: Шп1, Х1, Х2, Х3, Ск1, Ск2, Ск3
GRID = ['164249', '164251', '164254', '164257', '16425A', '16425D', '164260']
HOOP = dict(src=1, name='163E72', top='163E7C', bot='163E73', side='163E76', L='163E82')
PCELL = dict(src=4, name='163EB2', top='163EAB', bot='163EAE', lab='163EAD', L='163EB0')
SHP = dict(src=0, name='163E5E', L='163E6A')
W = dict(
    sm1=dict(X=1071200.0, no='5.5', wall='См-1', items=[
        ('h', 'Х1', 295, 195, 930), ('h', 'Х2', 320, 220, 980), ('h', 'Х3', 245, 145, 830),
        ('p', 'Ск1', 860, 860, 1890), ('p', 'Ск2', 1530, 1530, 3230),
        ('p', '15', 1310, 860, 2340), ('p', '16', 1810, 860, 2840), ('p', '17', 1310, 980, 2460),
        ('p', '18', 1810, 980, 2960), ('p', '19', 1310, 730, 2220), ('p', '20', 1810, 730, 2720)]),
    sm3=dict(X=1487000.0, no='5.13', wall='См-3', items=[
        ('s', 'Шп1', 0, 0, 370), ('h', 'Х1', 320, 220, 980),
        ('p', 'Ск1', 980, 980, 2130), ('p', 'Ск2', 1100, 1100, 2370), ('p', 'Ск3', 860, 860, 1890), ('p', 'Ск4', 740, 740, 1650)]),
    sm4=dict(X=1548600.0, no='5.16', wall='См-4', items=[
        ('s', 'Шп1', 0, 0, 370), ('h', 'Х1', 320, 220, 980), ('h', 'Х2', 220, 120, 780), ('h', 'Х3', 270, 170, 880),
        ('p', 'Ск1', 730, 730, 1630), ('p', 'Ск2', 730, 730, 1630), ('p', 'Ск3', 1220, 1220, 2610), ('p', 'Ск4', 740, 740, 1650),
        ('p', 'Ск5', 860, 860, 1890), ('p', 'Ск6', 980, 980, 2130)]))
k = sys.argv[1]; C = W[k]; X = C['X']; DX = X - SRC; tg = lambda h, *a: 'A3%s%s:%s' % (k, ''.join('_%s' % v for v in a), h)
inside = lambda r: r['x0'] >= -5 and r['x1'] <= 29705 and r['y0'] >= -5 and r['y1'] <= 42005
vedcell = lambda r: r['x1'] <= 8350 and r['y0'] >= 23790 and r['y1'] <= 37810            # cell content and grids (not header/title)
ops = []
# 0) the slot must be empty: earlier leftovers (invisible blocks) away
R0 = listwin(X - 5, Y0 - 5, 29710, 42010, None)
R0 = [r for r in R0 if r['x0'] >= X - 5 and r['x1'] <= X + 29705]
if R0: ops.append(dict(t='erase', h=[r['h'] for r in R0]))
# 1) everything of 5.9 except the ведомость cells
for r in R59:
    if not inside(r) or vedcell(r): continue
    ops.append(dict(t='clone', h=r['h'], base=[0, 0], to=[DX, 0], tag=tg(r['h'])))
# 2) ведомость: one cell per item, cloned from the 5.9 cell of the same type
def cell_ents(i):
    c = CEN[i]
    return [r for r in R59 if inside(r) and r['x1'] <= 8350 and abs((r['y0'] + r['y1']) / 2 - c) < 999]
for j, (typ, name, top, bot, L) in enumerate(C['items']):
    T = {'h': HOOP, 'p': PCELL, 's': SHP}[typ]; src = T['src']; dy = (CEN[0] - 2000 * j) - CEN[src]
    for r in cell_ents(src): ops.append(dict(t='clone', h=r['h'], base=[0, 0], to=[DX, dy], tag=tg(r['h'], j)))
    ops.append(dict(t='settext', h=tg(T['name'], j), s=name))
    ops.append(dict(t='settext', h=tg(T['L'], j), s=str(L)))
    if typ == 'h':
        ops += [dict(t='settext', h=tg(T['top'], j), s=str(top)), dict(t='settext', h=tg(T['bot'], j), s=str(bot)), dict(t='settext', h=tg(T['side'], j), s='270')]
    if typ == 'p':
        ops += [dict(t='settext', h=tg(T['top'], j), s=str(top)), dict(t='settext', h=tg(T['bot'], j), s=str(bot)), dict(t='settext', h=tg(T['lab'], j), s='по н.г.')]
# 3) stamp, table headers
ops += [dict(t='settext', h=tg('164243'), s='Спецификация элементов стены %s' % C['wall']), dict(t='settext', h=tg('164246'), s=C['no']),
        dict(t='tset', h=tg('163EEB'), cells=[[0, 2, 'Стена %s' % C['wall']]]), dict(t='tset', h=tg('164172'), cells=[[6, 0, 'Стена %s' % C['wall']]]),
        dict(t='save')]
print(k, 'ops', len(ops), 'cleared', len(R0))
if '--run' in sys.argv:
    out = gx.run(ops, 'a3' + k); print([l for l in out.splitlines() if 'ERR' in l or 'done' in l][-6:])
    m = json.load(open(os.environ['TEMP'] + '/gx_map.json', encoding='utf-8-sig'))
    print('SP', m.get(tg('163EEB')), 'ST', m.get(tg('164172')))
