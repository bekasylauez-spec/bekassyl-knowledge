# rigel marks on the scheme sheets 2.2 (-0.050), 2.3 (+4.500), 2.4 (+7.000): SPDS position note (clone of the analog
# note), arrow on the beam face at the middle of its longest clear piece, 45° leader, shelf away from the beam.
import json, gx, autobeam as AB

A = json.load(open(gx.S + r'\beams_auto.json', encoding='utf-8'))
MK = {m['mark']: m for m in AB.MK}
SHK = {'-0.050': 1, '+4.500': 2, '+7.000': 3}
Y0 = -1773284.0


def org(lev):
    k = SHK[lev]
    return 229592 - 84100 + 84100 * k, Y0


def ops(dx=600, dy=600):
    out = []; n = 0
    for mk, B in A.items():
        m = MK[mk]; lev = B['levels'][0]; X0, Y0_ = org(lev); d = m['d']
        for li, c in enumerate(m['lines']):
            x0 = m['x0s'][li]
            cs = AB.perp(d, c)
            s0, s1 = AB.along(d, x0), AB.along(d, x0 + m['L'])
            # clear pieces between supports of this instance
            sup = [((B['sup'][k]['a'] - B['sup'][0]['a']) + AB.along(d, x0 + m['sup'][0]) - (B['sup'][0]['a'] + B['sup'][0]['b']) / 2.0 if m['sup'] else 0) for k in range(len(B['sup']))] if False else None
            pts = sorted([AB.along(d, x0 + q) for q in m['sup']]) if m['sup'] else []
            cuts = [s0] + pts + [s1]
            segs = [(a, b) for a, b in zip(cuts, cuts[1:]) if b - a > 300]
            a, b = max(segs, key=lambda t: t[1] - t[0]) if segs else (s0, s1)
            u = (a + b) / 2.0
            half = B['b'] / 2.0
            if d == 'X':
                arrow = [X0 + u, Y0_ + cs + half]; shelf = [arrow[0] + dx, arrow[1] + dy]
            else:
                arrow = [X0 + cs + half, Y0_ + u]; shelf = [arrow[0] + dx, arrow[1] + dy]
            n += 1; tg = 'SM%d' % n
            out.append(dict(t='clone', h='A:4274A9', base=[0, 0], to=[0, 0], tag=tg))
            out.append(dict(t='spmove', h=tg, items=[[0, shelf[0], shelf[1]], [1, arrow[0], arrow[1]]]))
            out.append(dict(t='mcset', h=tg, set={'FirstLine': mk, 'SecondLine': '', 'Scale': 100}))
    return out


if __name__ == '__main__':
    o = ops()
    print(len(o) // 3, 'marks')
    json.dump(o, open(gx.S + r'\ops\schmarks.json', 'w', encoding='utf-8'), ensure_ascii=False)
