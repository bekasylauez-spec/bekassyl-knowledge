# См-10 top storey (+19.700...+22.400): См-4 ends at +19.700, so piece 3 has a free left end at 15225 there. Bars 50 from the free face:
# 3 bars Ø18 ш.100 at 15275..15475 (in the См-4 band), from +19.700 - 61d (anchored in См-4 below) to the top; Ск leg; zone added to the
# section data (wl/sm10_vert.json D / LABELS) so that wall_sec draws the dots / note. Run after wall_vert cfg_sm10.
import sys, json; sys.path.insert(0, 'wl'); from common import *
SX, SY, AX1 = 2733600.0, 455939.0, 13951.0
L7, L8 = 50691, 53391; d = 18; lap = 1100; DX = 20
V = json.load(open('wl/sm10_vert.json', encoding='utf-8'))
if any(b.get('top') for b in V['BARS']): sys.exit('already added')
Ln = int(round(L8 - 30 - (L7 - lap), -1)); p = max(V['POS'].values()) + 1
V['POS']['%d|%d' % (d, Ln)] = p
V['BARS'].append(dict(pos=p, d=d, L=Ln, n=6, top=True))
V['BARS'].append(dict(pos='Ск1', d=d, L=2 * lap + 170, n=3, top=True)) if any(b['pos'] == 'Ск1' and b['d'] == d for b in V['BARS']) else None
V['D'][2][3] = [['L', 15275, 15475, d, 100, [15275, 15375, 15475], [[15275, 15475, 100, 2]]]] + V['D'][2][3]
V['LABELS']['2|3|L'] = str(p)
json.dump(V, open('wl/sm10_vert.json', 'w', encoding='utf-8'), ensure_ascii=False)
W = lambda x, y: [SX + AX1 + x, SY + y]
ops = [dict(t='pl', p=[W(x + DX, L7 - lap), W(x + DX, L8 - 30)], layer='диам%d' % d, lw=40) for x in (15275, 15475)]
ops.append(dict(t='pl', p=[W(15255 + DX, L8 - 30), W(15255 + DX, L8 - 30 - lap)], layer='диам%d' % d, lw=40))
ops += [dict(t='clone', h='2D2907', base=[0, 0], to=[0, 0], tag='TP10'),
        dict(t='spmove', h='TP10', items=[[0, *W(14250, L7 + 1300)], [1, *W(15275 + DX, L7 + 1300)], [2, *W(15475 + DX, L7 + 1300)]]),
        dict(t='mcset', h='TP10', set={'FirstLine': '%d(%%%%C%d)' % (p, d), 'SecondLine': 'ш.100'}),
        dict(t='spmove', h='2D2910', items=[[1, *W(15255 + DX, L8 - 330)]]), dict(t='save')]
out = gx.run(ops, 't10'); print('pos', p, 'L', Ln, [l for l in out.splitlines() if 'ERR' in l or 'done' in l])
