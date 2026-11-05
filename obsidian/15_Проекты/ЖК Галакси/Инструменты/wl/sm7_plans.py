# См-7 opalubka plans 1-1 (basement, full wall) and 2-2 (upper storeys, 3 pieces) rebuilt in the analog plan's styles
import sys; sys.path.insert(0, 'wl'); from common import *
X, Y = 1934700.0, 455939.0
A = 39615
W = lambda x, y: [X + A + x, Y + y]
R = listwin(X, Y, 59400, 42000, None)
PL = {'1-1': dict(y0=37485, ylo=32500, yhi=40000, walls=[(-125, 22875)], ax='1F5AEC',
                  vax=['1F5AE9', '1F5AF1', '1F5AF2', '1F5AEA', '1F5AF3']),
      '2-2': dict(y0=18065, ylo=14000, yhi=22000, walls=[(-125, 3175), (5750, 17100), (20375, 22875)], ax='1F5F7E',
                  vax=['1F5F7B', '1F5F83', '1F5F84', '1F5F7C', '1F5F85'] )}
tdim = '1F5B27'; tpl = '1F5AEE'; thatch = '1F5AED'; tins = '1F5AF4'
ops = [dict(t='clone', h=h, base=[0, 0], to=[0, -100000], tag='T' + h) for h in (tdim, tpl, thatch, tins)]
er = []
for k, p in PL.items():
    for r in R:
        if r['x0'] > 33500 and p['ylo'] < r['y0'] and r['y1'] < p['yhi'] and r['t'] in ('DIMENSION', 'LWPOLYLINE', 'HATCH', 'INSERT', 'LINE'): er.append(r['h'])
ops.append(dict(t='erase', h=er))
for k, p in PL.items():
    y0 = p['y0']; y1 = y0 + 250
    for i, (a, b) in enumerate(p['walls']):
        tg = 'W%s%d' % (k, i)
        ops += [dict(t='pl', p=[W(a, y0), W(b, y0), W(b, y1), W(a, y1), W(a, y0)], layer='0', tag=tg), dict(t='eprops', src='T' + tpl, h=[tg])]
        ops += [dict(t='hatch', pat='ANSI36', sc=25, layer='.', loops=[[W(a, y0), W(b, y0), W(b, y1), W(a, y1)]], tag='H' + tg), dict(t='eprops', src='T' + thatch, h=['H' + tg])]
    for x in (0, 13850, 22750):                                    # perpendicular walls (См-1, См-3, См-6)
        ops.append(dict(t='clone', h='T' + tins, base=[X + A, Y - 100000 + 37485], to=W(x, y0)))
    # axes: А/1 0, А 5000, Б 14750, В 22750 (А/2, Б/1 of the analog dropped)
    va = p['vax']
    yb, yt = Y + y0 - 3000 + 0, Y + y0 + 841
    for h, x, v in ((va[0], 0, 'А/1'), (va[1], 5000, 'А'), (va[3], 14750, 'Б'), (va[4], 22750, 'В')):
        ops.append(dict(t='axis', h=h, s=[X + A + x, yt], e=[X + A + x, yb + 1100], val=v))
    ops.append(dict(t='erase', h=[va[2]]))
    ops.append(dict(t='axis', h=p['ax'], s=W(23700, y0 + 125), e=W(-1950, y0 + 125)))
    # dims: walls / openings chain, axes chain, total
    if k == '1-1': ch = [(-125, 125, ''), (125, 13725, ''), (13725, 13975, ''), (13975, 22625, ''), (22625, 22875, '')]
    else: ch = [(-125, 3175, ''), (3175, 5750, ''), (5750, 17100, ''), (17100, 20375, ''), (20375, 22875, '')]
    for a, b, t in ch: ops.append(dict(t='dim', h='T' + tdim, p1=W(a, y0), p2=W(b, y0), dl=W(a, y0 - 1100), rot=0, txt=t))
    for a, b in ((0, 5000), (5000, 14750), (14750, 22750)): ops.append(dict(t='dim', h='T' + tdim, p1=W(a, y0 - 1600), p2=W(b, y0 - 1600), dl=W(a, y0 - 1900), rot=0, txt=''))
    ops.append(dict(t='dim', h='T' + tdim, p1=W(0, y0 - 1600), p2=W(22750, y0 - 1600), dl=W(0, y0 - 2500), rot=0, txt=''))
ops.append(dict(t='erase', h=['T' + h for h in (tdim, tpl, thatch, tins)]))
ops.append(dict(t='save'))
print('erase', len(er), 'ops', len(ops))
if '--run' in sys.argv:
    out = gx.run(ops, 'sm7pl'); print([l for l in out.splitlines() if 'ERR' in l or 'done' in l][-4:])
