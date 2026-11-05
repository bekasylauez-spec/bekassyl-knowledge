# «Ведомость деталей» on analog sheet 5.4 (block exploded): П cells -> our Ск / U-bars, Х3 sizes; empty cell gets a copy of cell 25
import sys, json; sys.path.insert(0, 'wl'); from common import *
X0, Y0 = 1008200.0, 455939.0
T = json.load(open('wl/v54.json', encoding='utf-8'))
R = listwin(X0, Y0, 59400, 84100, None)
ops = []
def cell(name, xl, xr):
    c = next(t for t in T if t[3].strip() == name and xl < t[0] < xr)
    return c, [t for t in T if xl < t[0] < xr and c[1] - 1000 < t[1] < c[1] + 1000]
def put(name, xl, xr, new, top, bot, L, txts=None):
    c, ts = cell(name, xl, xr) if txts is None else txts
    digs = [t for t in ts if t[3].strip().isdigit() and t[3].strip() not in ('170',) and t is not c]
    Lt = max(digs, key=lambda t: t[0]); legs = [t for t in digs if t is not Lt]
    tp = max(legs, key=lambda t: t[1]); bt = min(legs, key=lambda t: t[1])
    for h, s in ((c[2], new), (tp[2], str(top)), (bt[2], str(bot)), (Lt[2], str(L))): ops.append(dict(t='settext', h=h, s=s))
RC = (45500, 52500); LC = (39300, 45300)
put('Ск1', *RC, 'Ск1', 860, 860, 1890); put('Ск2', *RC, 'Ск2', 1530, 1530, 3230)
put('Ск3', *RC, '15', 1310, 860, 2340); put('Ск4', *RC, '16', 1810, 860, 2840)
put('23', *RC, '17', 1310, 980, 2460); put('24', *RC, '18', 1810, 980, 2960)
put('25', *LC, '19', 1310, 730, 2220)
for h, s in (('185125', '245'), ('18511C', '145'), ('18512B', '830')): ops.append(dict(t='settext', h=h, s=s))
# cell 25 content -> empty cell below (-2000), texts 20
c25 = next(t for t in T if t[3].strip() == '25' and LC[0] < t[0] < LC[1]); cy = c25[1] - 118
src = [r for r in R if r['x0'] > 39200 and r['x1'] < 45500 and r['y0'] > cy - 1150 and r['y1'] < cy + 1150 and r['t'] not in ('INSERT', 'SPDSFORMAT')]
for r in src: ops.append(dict(t='clone', h=r['h'], base=[0, 0], to=[0, -2000], tag='V20:' + r['h']))
ts = [t for t in T if LC[0] < t[0] < LC[1] and cy - 1000 < t[1] < cy + 1000]
tg = lambda t: ['V20:' + t[2]] + list(t[1:])
c, = [t for t in ts if t[2] == c25[2]]
put(None, 0, 0, '20', 1810, 730, 2720, txts=(['V20:' + c[2] if False else 0, 0, 'V20:' + c[2], c[3]], [[t[0], t[1], 'V20:' + t[2], t[3]] for t in ts]))
ops.append(dict(t='save'))
print(len(src), 'cloned;', [(o['h'], o['s']) for o in ops if o['t'] == 'settext'])
if '--run' in sys.argv:
    out = gx.run(ops, 'v54'); print([l for l in out.splitlines() if 'ERR' in l or 'done' in l][-4:])
