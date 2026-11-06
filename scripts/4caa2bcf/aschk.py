# As(drawing) >= As(LIRA) check along a beam: main + dop covering the point (dop must extend >= anch beyond the point)
import json, sys, math
M = {m['mark']: m for m in json.load(open('b2/marks.json', encoding='utf-8'))}
AR = lambda d: math.pi * d * d / 400.0
def check(mark, B, off=0.0, anch=0):
    m = M[mark]; bad = []; rows = []
    for li, pts in enumerate(m['pts']):
        x0 = m['x0s'][li]
        for q in pts:
            u = (q[0] + x0) * 1000 + off       # LIRA m -> scheme mm
            for side, need, k in (('bot', q[1], 'bot'), ('top', q[2], 'top')):
                have = B['main'][k][0] * AR(B['main'][k][1])
                for dp in B.get('dop', []):
                    if dp['top'] == (k == 'top') and dp['u0'] + anch <= u <= dp['u1'] - anch: have += dp['n'] * AR(dp['d'])
                if need > have + 1e-6: bad.append((round(u), side, round(need, 2), round(have, 2)))
            n_leg = B['hoop'].get('legs', 4); s = B['hoop']['s_end']
            aw = n_leg * AR(B['hoop']['d']) * 1000.0 / s
            if q[3] > aw + 1e-6: bad.append((round(u), 'asw', round(q[3], 2), round(aw, 2)))
    return bad
if __name__ == '__main__':
    import beams
    b = check(sys.argv[1], beams.BEAMS[sys.argv[1]])
    print(len(b)); [print(x) for x in sorted(set(b))[:60]]
