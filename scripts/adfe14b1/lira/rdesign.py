# Reinforcement of every mark (envelope of its runs) — Ø28 A500С main, доп. Ø28 where As(LIRA) > As(main),
# hoops Х1 A240 Ø10 (Ø12 when Ø10@50 is not enough), 100/200 pattern of the analog, tightened where Asw needs it.
import pickle, json, math, os, collections
from design import LEVEL, AXX, AXY, sig
HERE = os.path.dirname(os.path.abspath(__file__))
rr, groups = pickle.load(open(os.path.join(HERE, 'groups.pkl'), 'rb'))
A25 = 6.158   # Ø28 (name kept)
STOCK = 11700
LAP_AN = 1120            # 40d Ø28


def cap(legs, d, s):     # cm2/m
    a = {10: 0.785, 12: 1.131}[d]
    return legs * a * 1000.0 / s


def r100(x): return int(math.ceil(x / 100.0 - 1e-9)) * 100


def env(rs):
    """profile in local u (from E0): list of (u, bot, top, asw)"""
    P = []
    for r in rs:
        for pos, b, t, w in r['prof']:
            P.append((pos - r['E0'], b, t, w))
    return sorted(P)


def design(rs, mark):
    r0 = rs[0]
    b, h = r0['b'], r0['h']
    E = r0['E1'] - r0['E0']
    sups = [(a - r0['E0'], e - r0['E0'], k) for a, e, k in r0['sups']]
    P = env(rs)
    inside = lambda u: any(a + 1 < u < e - 1 for a, e, _ in sups)
    Pf = [p for p in P if not inside(p[0])]
    n = 4 if b >= 350 else 3
    Asm = n * A25
    legs = 4 if b >= 350 else 2
    faces = [0.0] + [c for a, e, _ in sups for c in (a, e)] + [E]
    spans = [(faces[i], faces[i + 1]) for i in range(0, len(faces), 2) if faces[i + 1] - faces[i] > 1]
    # ---- top доп at supports
    dops = []
    for i, (a, e, k) in enumerate(sups):
        left = [s for s in spans if abs(s[1] - a) < 2]; right = [s for s in spans if abs(s[0] - e) < 2]
        Ll = left[0][1] - left[0][0] if left else 0; Lr = right[0][1] - right[0][0] if right else 0
        reg = [p for p in Pf if (left and a - Ll / 2.0 <= p[0] <= a) or (right and e <= p[0] <= e + Lr / 2.0)]
        if not reg: continue
        req = max(p[2] for p in reg)
        if req <= Asm + 0.05: continue
        nd = int(math.ceil((req - Asm) / A25 - 1e-6))
        over = [p[0] for p in reg if p[2] > Asm + 0.05]
        xl = min(over); xr = max(over)
        ext_l = max(a - xl + LAP_AN, Ll / 4.0) if left else 0
        ext_r = max(xr - e + LAP_AN, Lr / 4.0) if right else 0
        da = max(50, a - r100(ext_l)) if left else max(0, a) + 50
        db = min(E - 50, e + r100(ext_r)) if right else e - 50
        if not left: da = 50 if a < 1 else a + 50
        if not right: db = E - 50 if e > E - 1 else e - 50
        dops.append(dict(top=True, a=da, b=db, n=nd, req=round(req, 2), at=i))
    # ---- bottom доп: regions where bot > Asm
    over = [p for p in Pf if p[1] > Asm + 0.05]
    if over:
        xs = sorted(p[0] for p in over)
        grp = [[xs[0], xs[0]]]
        for x in xs[1:]:
            if x - grp[-1][1] <= 1500: grp[-1][1] = x
            else: grp.append([x, x])
        for g0, g1 in grp:
            req = max(p[1] for p in over if g0 <= p[0] <= g1)
            nd = int(math.ceil((req - Asm) / A25 - 1e-6))
            da = max(50, g0 - LAP_AN); db = min(E - 50, g1 + LAP_AN)
            if db - da < 1500: c = (da + db) / 2; da, db = max(50, c - 750), min(E - 50, c + 750)
            dops.append(dict(top=False, a=round(da / 50) * 50, b=round(db / 50) * 50, n=nd, req=round(req, 2)))
    for d in dops: d['L'] = int(round(d['b'] - d['a']))
    # positions: unique length -> pos 2, 3, ...
    Ls = sorted(set(d['L'] for d in dops), reverse=True)
    for d in dops: d['pos'] = str(2 + Ls.index(d['L']))
    # ---- hoops per span
    hd = 10
    zones, lines, NH = [], [], 0
    for (fL, fR) in spans:
        sp = [p for p in Pf if fL <= p[0] <= fR]
        Ls_ = fR - fL
        free_l = fL < 1 and not any(abs(a) < 2 for a, _, _ in sups)
        free_r = fR > E - 1 and not any(abs(e - E) < 2 for _, e, _ in sups)
        aw = lambda u0, u1: max([p[3] for p in sp if u0 <= p[0] <= u1] or [0])
        mid = aw(fL + Ls_ / 4, fR - Ls_ / 4)
        smid = 200 if mid <= cap(legs, hd, 200) else 100 if mid <= cap(legs, hd, 100) else 50
        peak = aw(fL, fR)
        while peak > cap(legs, hd, 50) and hd == 10: hd = 12
        def ssup(pk):
            for s in (100, 50):
                if pk <= cap(legs, hd, s) or s == 50: return s if pk > cap(legs, hd, 100) else 100
        s_l, s_r = ssup(aw(fL, fL + Ls_ / 2)), ssup(aw(fR - Ls_ / 2, fR))
        s_l, s_r = min(s_l, smid), min(s_r, smid)
        # support zone length: where asw > cap(mid), at least L/4
        def zlen(side):
            pts = [p for p in sp if (p[0] - fL if side == 'L' else fR - p[0]) <= Ls_ / 2]
            far = [abs(p[0] - (fL if side == 'L' else fR)) for p in pts if p[3] > cap(legs, hd, smid)]
            return max(Ls_ / 4.0, max(far) if far else 0)
        h0, h4 = fL + 50, fR - 50
        Lp = h4 - h0
        n1 = int(math.ceil((zlen('L') - 50) / s_l)); n3 = int(math.ceil((zlen('R') - 50) / s_r))
        if free_l: n1 = 0
        if free_r: n3 = 0
        Lm = Lp - n1 * s_l - n3 * s_r
        segs = []
        if Lm < smid:                                     # short span: one step all along
            s = min(s_l, s_r) if not (free_l and free_r) else smid
            if free_l or free_r: s = min(s_l, s_r) if (n1 or n3) else s
            nn = int(Lp // s); r = Lp - nn * s
            segs = [(h0, h0 + nn * s, '%dх%d' % (s, nn))] + ([(h0 + nn * s, h4, '%d' % round(r))] if r > 0.5 else [])
            cnt = nn + 1 + (1 if r > 0.5 else 0)
            ln = [h0, h4]
        else:
            n2 = int(Lm // smid); r = Lm - n2 * smid
            x = h0; ln = [h0]
            if n1: segs.append((x, x + n1 * s_l, '%dх%d' % (s_l, n1))); x += n1 * s_l; ln.append(x)
            if n2: segs.append((x, x + n2 * smid, '%dх%d' % (smid, n2))); x += n2 * smid
            if r > 0.5: segs.append((x, x + r, '%d' % round(r))); x += r
            if n3: ln.append(x); segs.append((x, x + n3 * s_r, '%dх%d' % (s_r, n3))); x += n3 * s_r
            assert abs(x - h4) < 1, (mark, fL, fR, x, h4)
            if ln[-1] != h4: ln.append(h4)
            cnt = n1 + n2 + n3 + 1 + (1 if r > 0.5 else 0)
        NH += cnt
        zones.append(dict(fL=fL, fR=fR, segs=segs, lines=sorted(set(round(v, 1) for v in ln)), cnt=cnt,
                          s=(s_l, smid, s_r), asw=(round(aw(fL, fL + Ls_ / 4), 1), round(mid, 1), round(aw(fR - Ls_ / 4, fR), 1))))
    # check capacity at every point
    cap_ok = True
    # As provided vs required (report)
    top_req = max([p[2] for p in Pf] or [0]); bot_req = max([p[1] for p in Pf] or [0])
    return dict(mark=mark, b=b, h=h, E=E, sups=sups, spans=spans, n=n, Asm=round(Asm, 2), dops=dops, legs=legs, hd=hd,
                zones=zones, NH=NH, top_req=round(top_req, 2), bot_req=round(bot_req, 2),
                asw_req=round(max([p[3] for p in Pf] or [0]), 1))


def check(D, rs):
    """As(drawing) >= As(LIRA) at every LIRA point; Asw likewise"""
    bad = []
    P = env(rs)
    inside = lambda u: any(a + 1 < u < e - 1 for a, e, _ in D['sups'])
    for u, bo, to, w in P:
        if inside(u): continue
        At = D['Asm'] + sum(d['n'] * A25 for d in D['dops'] if d['top'] and d['a'] <= u <= d['b'])
        Ab = D['Asm'] + sum(d['n'] * A25 for d in D['dops'] if not d['top'] and d['a'] <= u <= d['b'])
        if to > At + 0.05: bad.append(('top', u, to, round(At, 2)))
        if bo > Ab + 0.05: bad.append(('bot', u, bo, round(Ab, 2)))
        for z in D['zones']:
            if z['fL'] <= u <= z['fR']:
                for (p, q, t) in z['segs']:
                    if p - 1 <= u <= q + 1 and 'х' in t:
                        s = int(t.split('х')[0])
                        if w > cap(D['legs'], D['hd'], s) + 0.05: bad.append(('asw', u, w, round(cap(D['legs'], D['hd'], s), 1)))
    return bad


if __name__ == '__main__':
    marks = []
    k = 0
    for s, rs in groups:
        k += 1
        D = design(rs, 'Рм-%d' % k)
        r0 = rs[0]
        D.update(level=LEVEL[r0['z']], z=r0['z'], dir=r0['dir'],
                 runs=[dict(c=r['c'], a=r['a'], e=r['e'], E0=r['E0'], E1=r['E1']) for r in rs],
                 where=', '.join(('по оси %s' % (AXY if r['dir'] == 'X' else AXX).get(r['c'], r['c'])) for r in rs))
        bad = check(D, rs)
        D['bad'] = bad[:5]; D['nbad'] = len(bad)
        marks.append(D)
        print('%-6s %s %s %dx%d L=%5d sp=%d main %dØ28 top_req %.1f bot_req %.1f | доп %s | Х1 Ø%d legs %d asw %.1f steps %s | NH %d bad %d'
              % (D['mark'], D['level'], D['dir'], D['b'], D['h'], D['E'], len(D['spans']), D['n'], D['top_req'], D['bot_req'],
                 ' '.join('%s%s%dØ28 L%d' % ('в' if d['top'] else 'н', d['pos'], d['n'], d['L']) for d in D['dops']),
                 D['hd'], D['legs'], D['asw_req'], ' '.join('/'.join(map(str, z['s'])) for z in D['zones']), D['NH'], len(bad)))
    json.dump(marks, open(os.path.join(HERE, 'marks.json'), 'w'), ensure_ascii=False, indent=1)
