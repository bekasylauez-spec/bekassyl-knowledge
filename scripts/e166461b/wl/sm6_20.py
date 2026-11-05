import sys; sys.path.insert(0, 'wl'); from sm6_geom import *
X = 1726800.0; A1 = 8866
R, ops, er = elevation(X, A1, 15206, 19506, None)
H = {r['h']: r for r in R}
W = lambda x, y: [X + x, SY + y]
def dim(h, p1, p2):
    r = H[h]; return dict(t='dimpts', h=h, p1=W(p1, r['sp'][0][1]), p2=W(p2, r['sp'][1][1]), dl=W(p1, r['sp'][2][1]))
# basement opening diagonals: copies of the storey-1 ones (after their stretch), height 4300
diag = sorted([r for r in R if r['t'] == 'LWPOLYLINE' and len(r['sp']) == 3 and abs(r['sp'][0][1] - 19756) < 3], key=lambda r: r['x0'])
for i, r in enumerate(diag):
    x0 = A1 + 1225 if i == 0 else r['sp'][0][0]; x1 = A1 + 6675 if i == 0 else (A1 + 18825 if i == 3 else r['sp'][2][0])
    mx = r['sp'][1][0] - r['sp'][0][0]
    ops.append(dict(t='pl', p=[W(x0, 15206), W(x0 + mx, 19506 - 452), W(x1, 19506)], layer='Размеры', tag='BD%d' % i))
    ops.append(dict(t='eprops', src=r['h'], h=['BD%d' % i]))
# elevation chain + 2/1
ops += [dim('1DF0A0', A1 + 125, A1 + 1225), dim('1DF0ED', A1 + 6675, A1 + 1225), dim('1DF180', A1 + 18825, A1 + 13375), dim('1DF173', A1 + 18825, A1 + 19925),
        dim('1DF119', A1 + 10275, A1 + 10525)]
er += ['1DF0BC', '1DF107', '1E0CD2']
# plan 1-1 (axis 1 at 8925): corner piers only, hatch on them
P = 8925
ops += [xmove(H['1DED5C'], X, [(P + 1200, P + 1225)]), xmove(H['1DED5E'], X, [(P + 18850, P + 18825)]),
        dim('1DEE01', P + 1225, P + 125), dim('1DEDF4', P + 6675, P + 1225), dim('1DEE4E', P + 13375, P + 18825), dim('1DEE5B', P + 19925, P + 18825),
        dim('1DEE2A', P + 10525, P + 10275),
        dict(t='hatch', pat='ANSI36', sc=25, layer='.', loops=[[W(P + 125, 6669), W(P + 1225, 6669), W(P + 1225, 6919), W(P + 125, 6919)],
                                                              [W(P + 18825, 6669), W(P + 19925, 6669), W(P + 19925, 6919), W(P + 18825, 6919)]], tag='PH'),
        dict(t='eprops', src='1DED5F', h=['PH'])]
er += ['1DED5D', '1DED60', '1DED61', '1DED62', '1DED63', '1DED5F', '1DEE0E', '1DEE3C', '1DED1A']
# plan 2-2 (upper floors in the analog) is not needed: См-6 is the same on every storey
er += [r['h'] for r in R if r['x0'] > 32000 and r['y0'] > 21000 and r['y1'] < 32500 and r['t'] != 'SPDSFORMAT']
ops = [o for o in ops if o]
ops = [dict(t='erase', h=er)] + ops + [dict(t='save')]
print('erase', len(er), 'ops', len(ops))
if '--run' in sys.argv:
    out = gx.run(ops, 'sm6_20'); print([l for l in out.splitlines() if 'ERR' in l or 'done' in l or 'rror' in l][-6:])
