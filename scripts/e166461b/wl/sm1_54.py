# См-1 sheet 5.4: plan «Разрез 1-1 (Армирования)» drawn x2 (axis 1 at 7075): drop 2/1, stretch pieces
import sys, json; sys.path.insert(0, 'wl'); from common import *
X0, Y0 = 1008200.0, 455939.0
MAP = [(9075, 9525), (18875, 18825), (20425, 20425), (20925, 20925), (22475, 22525), (31775, 31725), (33325, 33325), (33825, 33825), (35375, 35425), (45175, 44725), (46925, 46925)]
R = json.load(open('wl/f54.json', encoding='utf-8'))
er = []
for r in R:
    if r['y0'] < 8000 or r['y1'] > 21000: continue
    if r['h'] == '13CF3F': er.append(r['h']); continue
    if r['x0'] > 25600 and r['x1'] < 28300: er.append(r['h']); continue
    if r['t'] == 'DIMENSION' and any(min(abs(a - v) for v in (25825, 27825, 25925, 27725, 26375)) < 3 for a, b in r['sp'][:2]): er.append(r['h'])
ops = [dict(t='erase', h=er)] + stretch_ops(X0, Y0, MAP, xmax=50000, ymin=8000, ymax=21000) + [dict(t='save')]
print('erase', len(er), er)
out = gx.run(ops, 'sm1_54')
print('\n'.join(l for l in out.splitlines() if 'stretch' in l or 'ERR' in l or 'done' in l)[-800:])
