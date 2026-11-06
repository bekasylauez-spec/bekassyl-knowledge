# Reinforcement of every mark (envelope of its runs): Ø28 A500С main, доп. Ø28 where As(LIRA) > As(main) (between the
# main bars, the rest 2nd row), side bars Ø12 (h > 700, <= 400 apart), hoops Х1 A240 Ø10 (Ø12 when Ø10@50 is short),
# 100/200 pattern of the analog, tightened where Asw needs it.
import pickle, json, math, os, collections, csv, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from design import LEVEL, AXX, AXY, where, axname, nodes, els
HERE = os.path.dirname(os.path.abspath(__file__))
rr, groups = pickle.load(open(os.path.join(HERE, 'groups.pkl'), 'rb'))
A28 = 6.158
STOCK = 11700
LAP_AN = 1120            # 40d Ø28

# ---- LIRA As per element section
raw = open(os.path.join(HERE, 'as_bar.csv'), 'rb').read().decode('utf-8', errors='replace').replace('﻿', '')
RA = collections.defaultdict(list)
for r in csv.reader(raw.splitlines(), delimiter=';'):
    if len(r) < 21 or not r[4].strip().isdigit(): continue
    try: v = [float(x or 0) for x in r[10:21]]
    except ValueError: continue
    RA[int(r[4])].append((int(r[5]), r[6].strip(), v))


def profile(r):
    """(t along A->B in mm, bot, top, asw)"""
    A, B, L = r['A'], r['B'], r['L']
    ux, uy = (B[0] - A[0]) / L, (B[1] - A[1]) / L
    pts = []
    for e in r['els']:
        rows = RA.get(e)
        if not rows: continue
        ns = max(s for s, _, _ in rows)
        ok = [x for x in rows if x[1] != '*'] or rows
        n1, n2 = [nodes[i - 1] for i in els[e - 1][2]]
        t1 = (n1[0] * 1000 - A[0]) * ux + (n1[1] * 1000 - A[1]) * uy
        t2 = (n2[0] * 1000 - A[0]) * ux + (n2[1] * 1000 - A[1]) * uy
        for s, _, v in ok:
            t = t1 + (t2 - t1) * (s - 1) / max(ns - 1, 1)
            pts.append((t, v[0] + v[1] + v[4], v[2] + v[3] + v[5], max(v[9], v[10])))
    return pts


def cap(legs, d, s): return legs * {10: 0.785, 12: 1.131, 14: 1.539}[d] * 1000.0 / s
def r100(x): return int(math.ceil(x / 100.0 - 1e-9)) * 100


def faces(r, rev):
    E = r['E1'] - r['E0']
    f = [0.0] + [c - r['E0'] for a, b, _ in r['sups'] for c in (a, b)] + [E]
    if rev: f = sorted(E - x for x in f)
    return f


def env(rs):
    """envelope in the template run's u; members mapped face-to-face (piecewise linear) when their faces differ"""
    P = []
    F0 = faces(*rs[0])
    for r, rev in rs:
        F = faces(r, rev); E = r['E1'] - r['E0']
        same = len(F) == len(F0)
        for t, b, tp, w in profile(r):
            u = t - r['E0']
            if rev: u = E - u
            if same:
                for i in range(len(F) - 1):
                    if F[i] - 1e-6 <= u <= F[i + 1] + 1e-6 or (i == 0 and u < F[0]) or (i == len(F) - 2 and u > F[-1]):
                        d = F[i + 1] - F[i]
                        u = F0[i] + (F0[i + 1] - F0[i]) * ((u - F[i]) / d if d > 1e-6 else 0.5)
                        break
            P.append((u, b, tp, w))
    return sorted(P)


def spans_of(r, rev):
    F = faces(r, rev)
    return [F[i + 1] - F[i] for i in range(0, len(F), 2)], F


def unify2(groups, tol=600):
    """Block 1 rule (Bekassyl): same b x h, same faces count, every span within tol (direct or mirrored), any level ->
    one mark; template = the longest; kept only if As/Asw of all members are covered"""
    G = [list(rs) for _, rs in groups]
    G.sort(key=lambda g: -(g[0][0]['E1'] - g[0][0]['E0']))
    changed = True
    while changed:
        changed = False
        for i in range(len(G)):
            for j in range(len(G)):
                if i == j or not G[i] or not G[j]: continue
                a, b = G[i][0][0], G[j][0][0]
                if (a['b'], a['h']) != (b['b'], b['h']): continue
                if (a['E1'] - a['E0']) < (b['E1'] - b['E0']): continue
                sa, Fa = spans_of(*G[i][0]); sb, Fb = spans_of(*G[j][0])
                if len(Fa) != len(Fb) or len(sa) != len(sb): continue
                # support kinds per face pair must agree only in count; widths within tol
                direct = all(abs(x - y) <= tol for x, y in zip(sa, sb)) and all(abs((Fa[k+1]-Fa[k]) - (Fb[k+1]-Fb[k])) <= tol for k in range(1, len(Fa) - 1, 2))
                mirror = all(abs(x - y) <= tol for x, y in zip(sa, sb[::-1]))
                if not (direct or mirror): continue
                flip = not direct
                cand = G[i] + [(r, (not rev) if flip else rev) for r, rev in G[j]]
                D = design(cand, 'x')
                if check(D, cand): continue
                G[i] = cand; G[j] = []; changed = True
    return [(None, g) for g in G if g]


def bars_x(b):
    n = 6 if b >= 700 else 4 if b >= 350 else 3
    c = 55 if b >= 350 else 45
    return [round(c + (b - 2 * c) * i / (n - 1)) for i in range(n)]


def side_bars(h):
    if h <= 700: return 0
    return max(1, int(math.ceil((h - 2 * 70) / 400.0)) - 1)       # per face


def design(rs, mark):
    r0 = rs[0][0]; rev0 = rs[0][1]
    b, h = r0['b'], r0['h']
    E = r0['E1'] - r0['E0']
    sups = [(a - r0['E0'], e - r0['E0'], k) for a, e, k in r0['sups']]
    if rev0: sups = sorted((E - e, E - a, k) for a, e, k in sups)
    P = env(rs)
    inside = lambda u: any(a + 1 < u < e - 1 for a, e, _ in sups)
    Pf = [p for p in P if not inside(p[0])]
    BX = bars_x(b); n = len(BX)
    Asm = n * A28
    legs = 4 if b >= 350 else 2
    faces = [0.0] + [c for a, e, _ in sups for c in (a, e)] + [E]
    spans = [(faces[i], faces[i + 1]) for i in range(0, len(faces), 2) if faces[i + 1] - faces[i] > 1]
    dops = []
    # ---- top доп at supports
    for i, (a, e, k) in enumerate(sups):
        left = [s for s in spans if abs(s[1] - a) < 2]; right = [s for s in spans if abs(s[0] - e) < 2]
        Ll = left[0][1] - left[0][0] if left else 0; Lr = right[0][1] - right[0][0] if right else 0
        reg = [p for p in Pf if (left and a - Ll / 2.0 <= p[0] <= a + 2) or (right and e - 2 <= p[0] <= e + Lr / 2.0)]
        if not reg: continue
        req = max(p[2] for p in reg)
        if req <= Asm + 0.05: continue
        nd = int(math.ceil((req - Asm) / A28 - 1e-6))
        over = [p[0] for p in reg if p[2] > Asm + 0.05]
        xl = min(over); xr = max(over)
        ext_l = max(a - xl + LAP_AN, Ll / 4.0) if left else 0
        ext_r = max(xr - e + LAP_AN, Lr / 4.0) if right else 0
        da = max(50, a - r100(ext_l)) if left else 50 if a < 1 else a + 50
        db = min(E - 50, e + r100(ext_r)) if right else E - 50 if e > E - 1 else e - 50
        dops.append(dict(top=True, a=da, b=db, n=nd, req=round(req, 2), at=i))
    # merge overlapping top доп (same count -> one bar run)
    dops.sort(key=lambda d: d['a'])
    mg = []
    for d in dops:
        if mg and d['a'] <= mg[-1]['b'] + 200:
            mg[-1]['b'] = max(mg[-1]['b'], d['b']); mg[-1]['n'] = max(mg[-1]['n'], d['n']); mg[-1]['req'] = max(mg[-1]['req'], d['req'])
        else: mg.append(d)
    dops = mg
    # ---- bottom доп
    over = [p for p in Pf if p[1] > Asm + 0.05]
    if over:
        xs = sorted(p[0] for p in over)
        grp = [[xs[0], xs[0]]]
        for x in xs[1:]:
            if x - grp[-1][1] <= 1500: grp[-1][1] = x
            else: grp.append([x, x])
        for g0, g1 in grp:
            req = max(p[1] for p in over if g0 <= p[0] <= g1)
            nd = int(math.ceil((req - Asm) / A28 - 1e-6))
            da = max(50, g0 - LAP_AN); db = min(E - 50, g1 + LAP_AN)
            if db - da < 1500: c = (da + db) / 2; da, db = max(50, c - 750), min(E - 50, c + 750)
            dops.append(dict(top=False, a=round(da / 50) * 50, b=round(db / 50) * 50, n=nd, req=round(req, 2)))
    for d in dops:                       # lengths in 250 steps -> fewer positions; grow symmetrically inside the beam
        L0 = d['b'] - d['a']; L1 = int(math.ceil(L0 / 250.0 - 1e-9)) * 250; g = (L1 - L0) / 2.0
        a, b_ = d['a'] - g, d['b'] + g
        if a < 50: b_ += 50 - a; a = 50
        if b_ > E - 50: a -= b_ - (E - 50); b_ = E - 50
        d['a'], d['b'] = max(50, a), b_; d['L'] = int(round(d['b'] - d['a']))
    for top in (True, False):              # one length per group: the longest one, bars re-centred inside the beam
        grp = [d for d in dops if d['top'] == top]
        if not grp: continue
        Lg = max(d['L'] for d in grp)
        for d in grp:
            c = (d['a'] + d['b']) / 2.0; a, b_ = c - Lg / 2.0, c + Lg / 2.0
            if a < 50: b_ += 50 - a; a = 50
            if b_ > E - 50: a -= b_ - (E - 50); b_ = E - 50
            d['a'], d['b'], d['L'] = a, b_, Lg
    out = []                               # lengthened bars of one row must not overlap: merge them
    for top in (True, False):
        g = sorted([d for d in dops if d['top'] == top], key=lambda d: d['a'])
        for d in g:
            if out and out[-1]['top'] == top and d['a'] < out[-1]['b'] + 100:
                o = out[-1]; o['b'] = max(o['b'], d['b']); o['n'] = max(o['n'], d['n']); o['L'] = int(round(o['b'] - o['a']))
            else: out.append(d)
    dops = out
    Ls = sorted(set((d['top'], d['L']) for d in dops), key=lambda q: (not q[0], -q[1]))
    for d in dops: d['pos'] = str(2 + Ls.index((d['top'], d['L'])))
    nside = side_bars(h)
    side_pos = str(2 + len(Ls)) if nside else None
    # ---- hoops per span
    hd = 10
    zones, NH = [], 0
    for (fL, fR) in spans:
        sp = [p for p in Pf if fL <= p[0] <= fR]
        Ls_ = fR - fL
        free_l = fL < 1 and not any(abs(a) < 2 for a, _, _ in sups)
        free_r = fR > E - 1 and not any(abs(e - E) < 2 for _, e, _ in sups)
        aw = lambda u0, u1: max([p[3] for p in sp if u0 <= p[0] <= u1] or [0])
        peak = aw(fL, fR)
        if peak > cap(legs, hd, 50) and hd < 14: hd = 12 if peak <= cap(legs, 12, 50) else 14
        mid = aw(fL + Ls_ / 4, fR - Ls_ / 4)
        smid = 200 if mid <= cap(legs, hd, 200) else 100 if mid <= cap(legs, hd, 100) else 50
        def ssup(pk): return 100 if pk <= cap(legs, hd, 100) else 50
        s_l, s_r = min(ssup(aw(fL, fL + Ls_ / 2)), smid), min(ssup(aw(fR - Ls_ / 2, fR)), smid)
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
        if Lm < smid:
            s = min(s_l, s_r)
            nn = int(Lp // s); rr_ = Lp - nn * s
            segs = [(h0, h0 + nn * s, '%dх%d' % (s, nn))] + ([(h0 + nn * s, h4, '%d' % round(rr_))] if rr_ > 0.5 else [])
            cnt = nn + 1 + (1 if rr_ > 0.5 else 0)
            ln = [h0, h4]
        else:
            n2 = int(Lm // smid); rr_ = Lm - n2 * smid
            x = h0; ln = [h0]
            if n1: segs.append((x, x + n1 * s_l, '%dх%d' % (s_l, n1))); x += n1 * s_l; ln.append(x)
            if n2: segs.append((x, x + n2 * smid, '%dх%d' % (smid, n2))); x += n2 * smid
            if rr_ > 0.5: segs.append((x, x + rr_, '%d' % round(rr_))); x += rr_
            if n3: ln.append(x); segs.append((x, x + n3 * s_r, '%dх%d' % (s_r, n3))); x += n3 * s_r
            assert abs(x - h4) < 1, (mark, fL, fR, x, h4)
            if ln[-1] != h4: ln.append(h4)
            cnt = n1 + n2 + n3 + 1 + (1 if rr_ > 0.5 else 0)
        NH += cnt
        zones.append(dict(fL=fL, fR=fR, segs=segs, lines=sorted(set(round(v, 1) for v in ln)), cnt=cnt, s=(s_l, smid, s_r),
                          asw=(round(aw(fL, fL + Ls_ / 4), 1), round(mid, 1), round(aw(fR - Ls_ / 4, fR), 1))))
    top_req = max([p[2] for p in Pf] or [0]); bot_req = max([p[1] for p in Pf] or [0])
    return dict(mark=mark, b=b, h=h, E=E, sups=sups, spans=spans, n=n, bx=BX, Asm=round(Asm, 2), dops=dops, legs=legs, hd=hd,
                nside=nside, side_pos=side_pos, zones=zones, NH=NH, top_req=round(top_req, 2), bot_req=round(bot_req, 2),
                asw_req=round(max([p[3] for p in Pf] or [0]), 1))


def check(D, rs):
    bad = []
    inside = lambda u: any(a + 1 < u < e - 1 for a, e, _ in D['sups'])
    for u, bo, to, w in env(rs):
        if inside(u): continue
        At = D['Asm'] + sum(d['n'] * A28 for d in D['dops'] if d['top'] and d['a'] <= u <= d['b'])
        Ab = D['Asm'] + sum(d['n'] * A28 for d in D['dops'] if not d['top'] and d['a'] <= u <= d['b'])
        if to > At + 0.05: bad.append(('top', round(u), to, round(At, 2)))
        if bo > Ab + 0.05: bad.append(('bot', round(u), bo, round(Ab, 2)))
        for z in D['zones']:
            if z['fL'] <= u <= z['fR']:
                for (p, q, t) in z['segs']:
                    if p - 1 <= u <= q + 1 and 'х' in t:
                        s = int(t.split('х')[0])
                        if w > cap(D['legs'], D['hd'], s) + 0.05: bad.append(('asw', round(u), w, round(cap(D['legs'], D['hd'], s), 1)))
    return bad


def colpos(rs):
    r0, rev = rs[0]; E = r0['E1'] - r0['E0']
    s = [((a + b) / 2.0 - r0['E0']) for a, b, k in r0['sups'] if k == 'col']
    return sorted((E - x) if rev else x for x in s), E


def unify(groups, tol=300):
    """merge groups: same level/section, length within tol, same column supports within tol (direct or mirrored);
    the template is the group with more supports; the merge is kept only if As/Asw of every member are covered"""
    G = [list(rs) for _, rs in groups]
    changed = True
    while changed:
        changed = False
        for i in range(len(G)):
            for j in range(len(G)):
                if i == j or not G[i] or not G[j]: continue
                a, b = G[i][0][0], G[j][0][0]
                if (a['z'], a['b'], a['h']) != (b['z'], b['b'], b['h']): continue
                if len(a['sups']) < len(b['sups']): continue          # i = template (more supports)
                ca, Ea = colpos(G[i]); cb, Eb = colpos(G[j])
                if abs(Ea - Eb) > tol or len(ca) != len(cb): continue
                direct = all(abs(x - y) <= tol for x, y in zip(ca, cb))
                mirror = all(abs(x - (Eb - y)) <= tol for x, y in zip(ca, sorted(cb, reverse=True)))
                if not (direct or mirror): continue
                flip = not direct
                cand = G[i] + [(r, (not rev) if flip else rev) for r, rev in G[j]]
                D = design(cand, 'x')
                if check(D, cand): continue
                G[i] = cand; G[j] = []; changed = True
    G = [g for g in G if g]
    G.sort(key=lambda g: (min(r['z'] for r, _ in g), -g[0][0]['h'], -g[0][0]['b'], g[0][0]['dir'], -(g[0][0]['E1'] - g[0][0]['E0'])))
    return [(None, g) for g in G]


if __name__ == '__main__':
    marks = []
    n0 = len(groups)
    groups = unify2(groups, int(os.environ.get('UTOL', '600')))
    print('unify: %d -> %d marks' % (n0, len(groups)))
    pickle.dump(groups, open(os.path.join(HERE, 'groups_u.pkl'), 'wb'))
    for k, (s, rs) in enumerate(groups, 1):
        D = design(rs, 'Рм-%d' % k)
        r0 = rs[0][0]
        lv = sorted({r['z'] for r, _ in rs})
        D.update(level=LEVEL[r0['z']], levels=[LEVEL[z] for z in lv], z=r0['z'], dir=r0['dir'], count=len(rs),
                 runs=[dict(A=r['A'], B=r['B'], E0=r['E0'], E1=r['E1'], rev=rev, where=where(r)) for r, rev in rs],
                 where='; '.join(where(r) for r, _ in rs))
        # axes along the mark (local u)
        r, rev = rs[0]
        ax = []
        if r['dir'] in 'XY':
            AX = AXX if r['dir'] == 'X' else AXY
            k = 0 if r['dir'] == 'X' else 1
            sgn = 1 if r['B'][k] >= r['A'][k] else -1
            for c, v in AX.items():
                u = (c - r['A'][k]) * sgn - r['E0']
                if rev: u = D['E'] - u
                if any(a - 1 <= u <= e + 1 for a, e, _ in D['sups'] if _ == 'col'): ax.append((round(u), v))
        D['axes'] = sorted(ax)
        bad = check(D, rs)
        D['bad'] = bad[:5]; D['nbad'] = len(bad)
        marks.append(D)
        print('%-6s %s %s %dx%d L=%5d n=%d sp=%d main %dØ28 верх %.1f низ %.1f | доп %s | бок %s | Х1 Ø%d asw %.1f %s | NH %d bad %d'
              % (D['mark'], D['level'], D['dir'], D['b'], D['h'], D['E'], D['count'], len(D['spans']), D['n'], D['top_req'], D['bot_req'],
                 ' '.join('%s%s:%dØ28 L%d' % ('в' if d['top'] else 'н', d['pos'], d['n'], d['L']) for d in D['dops']),
                 ('%dx2Ø12' % D['nside']) if D['nside'] else '-', D['hd'], D['asw_req'], ' '.join('/'.join(map(str, z['s'])) for z in D['zones']), D['NH'], len(bad)))
    json.dump(marks, open(os.path.join(HERE, 'marks.json'), 'w'), ensure_ascii=False, indent=1)
