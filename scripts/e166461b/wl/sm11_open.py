# См-11 openings (LIRA x = 20050): storey +3.950: 9175..14625, from the floor 2200 high; storeys +7.100 ... +16.550: windows 6675..7675,
# sill 520, height 2130. Outline as the piece outlines (cloned style), one diagonal (lower-left -> upper-right, rule), dims on the op sheet.
import sys, re; sys.path.insert(0, 'wl'); from common import *
Y = 455939.0
SH = [(2906700, 11503, [10670, 15220, 19270, 22420, 25570, 28720, 31870, 35020], '333EE1', ('333FBE', '333FBE')),
      (3008100, 15030, [27970, 32520, 36570, 39720, 42870, 46020, 49170, 52320], '335B56', None),
      (3050100, 15030, [27970, 32520, 36570, 39720, 42870, 46020, 49170, 52320], '337011', None)]
OP = [(2, 9175, 14625, 0, 2200)] + [(s, 6675, 7675, 520, 2650) for s in (3, 4, 5, 6)]
ops = []
for X, A, L, src, dims in SH:
    P = lambda x, y: [X + A + x, Y + y]
    for k, (s, a, b, z0, z1) in enumerate(OP):
        y0, y1 = L[s] + z0, L[s] + z1
        ops.append(dict(t='pl', p=[P(a, y0), P(b, y0), P(b, y1), P(a, y1)], closed=True, layer='Размеры', tag='O11_%d_%d' % (X, k)))
        ops.append(dict(t='eprops', src=src, h=['O11_%d_%d' % (X, k)]))
        ops.append(dict(t='pl', p=[P(a, y0), P(b, y1)], layer='Размеры', lw=13))
        if dims and k in (0, 1):                          # op sheet: the large opening and the first window dimensioned
            t = dims[0]; ym = (y0 + y1) / 2
            ops.append(dict(t='dim', h=t, p1=P(5750, ym - 300), p2=P(a, ym - 300), dl=P((5750 + a) / 2, ym - 300), rot=0, txt=''))
            ops.append(dict(t='dim', h=t, p1=P(a, ym + 300), p2=P(b, ym + 300), dl=P((a + b) / 2, ym + 300), rot=0, txt=''))
            xv = b + 350
            ops.append(dict(t='dim', h=t, p1=P(b, L[s]), p2=P(b, y0), dl=P(xv, (L[s] + y0) / 2), rot=1.5707963, txt='')) if z0 > 0 else None
            ops.append(dict(t='dim', h=t, p1=P(b, y0), p2=P(b, y1), dl=P(xv, (y0 + y1) / 2), rot=1.5707963, txt=''))
ops = [o for o in ops if o] + [dict(t='save')]
out = gx.run(ops, 'o11'); print([l for l in out.splitlines() if 'ERR' in l or 'done' in l][-5:])
