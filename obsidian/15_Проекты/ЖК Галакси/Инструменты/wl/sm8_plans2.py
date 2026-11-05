# См-8 plan sheet fixes after sm8_plans: hatches to outlines, axis dims 5000|9750|8000, degenerate dims, axis «2» line,
# plan 3-3 (top) cropped to the piece 15225..18025 between axes Б-В, titles.
import sys, json; sys.path.insert(0, 'wl'); from common import *
NX, Y = 2268600.0, 455939.0
R = json.load(open('w/r8p.json')); H = {r['h']: r for r in R}
W = lambda x, y: [NX + x, Y + y]
ops = []
def fit(hh, pl):
    p = H[pl]; ops.append(dict(t='hatchfit', h=hh, loops=[[W(p['x0'], p['y0']), W(p['x1'], p['y0']), W(p['x1'], p['y1']), W(p['x0'], p['y1'])]]))
def fitnew(src, pl, tag):
    p = H[pl]; ops.append(dict(t='clone', h=src, base=[0, 0], to=[0, 0], tag=tag))
    ops.append(dict(t='hatchfit', h=tag, loops=[[W(p['x0'], p['y0']), W(p['x1'], p['y0']), W(p['x1'], p['y1']), W(p['x0'], p['y1'])]]))
# 1-1 (A0 6600, wall y 25300)
fit('22D059', '22D05A'); fit('22D3AE', '22D3A0'); fitnew('22D3AE', '22D05B', 'P8h1')
# 2-2 (A0 6600, wall y 16500)
fit('22D379', '22D37A'); fit('22D419', '22D41A'); fit('22D473', '22D474'); fitnew('22D473', '22D2B0', 'P8h2')
A0 = 6600
for (d1, d2, d3), er, yl, yd in ((('22D093', '22D0A2', '22D0B1'), ['22D0CD', '22D0C0', '22D061', '22D070', '22D17A', '22D160', '22D16D'], 23700, 22794),
                                 (('22D2C4', '22D2D3', '22D2E2'), ['22D2FE', '22D2F1'], 14900, 13994)):
    for h, (a, b) in zip((d1, d2, d3), ((0, 5000), (5000, 14750), (14750, 22750))):
        ops.append(dict(t='dimpts', h=h, p1=W(A0 + a, yl), p2=W(A0 + b, yl), dl=W(A0 + (a + b) / 2, yd)))
        ops.append(dict(t='dimdef', h=[h]))
    ops.append(dict(t='erase', h=er))
for h, y in (('22D058', 25300), ('22D2AF', 16500)):
    ops.append(dict(t='axis', h=h, s=W(A0 + 22750, y), e=W(A0 - 2029, y), val='2'))
# 3-3 top (A0 -7100): only the piece 15225..18025, axes Б (7650) and В (15650)
keep = {'22D3B0', '22D418', '22D3D7', '22D3E5', '22D3F7', '22D18E', '22D18F', '22D1E6', '22D190', '22D231'}
er = []
for r in R:
    cy = (r['y0'] + r['y1']) / 2; cx = (r['x0'] + r['x1']) / 2
    if not (2500 < cy < 9000) or r['h'] in keep or r['t'] in ('SPDSFORMAT',) or r['x0'] > 30000: continue
    if r['t'] == 'MTEXT' and cx < -900: continue                     # op sheet notes / stamp
    if r['x1'] > -12500 and (cx < 7400 or cx > 11700): er.append(r['h'])
ops.append(dict(t='erase', h=er))
ops.append(dict(t='dimpts', h='22D1E6', p1=W(7650, 5800), p2=W(15650, 5800), dl=W(11650, 4894))); ops.append(dict(t='dimdef', h=['22D1E6']))
ops.append(dict(t='axis', h='22D190', s=W(15650, 7400), e=W(7650 - 2029, 7400), val='2'))
ops.append(dict(t='move', h=['22D231'], d=[11650 - 1550, -800]))
ops.append(dict(t='settext', h='22D231', s='{\LРазрез 3 - 3 (Опалубка) М1:100}'))
ops.append(dict(t='settext', h='22D32D', s='{\LРазрез 2 - 2 (Опалубка) М1:100}'))
ops.append(dict(t='settext', h='P8F_204407', s='Разрезы 1-1, 2-2, 3-3 (Опалубка) стены См-8'))
ops.append(dict(t='save'))
print('erase top', len(er))
out = gx.run(ops, 'p82'); print([l for l in out.splitlines() if 'ERR' in l or 'done' in l][-6:])
