# БДМ Блок 4 rigel sheets: the finished ЖК Галакси sheet 6.5 (analog «Ресторан 6.1», approved style) is cloned and
# stretched for one Рм (or one part of a long Рм). Kit roles = Galaxy tags A5:<analog handle>, A5S0_<staging handle>.
# Splice objects (накладки) and node «А» come from Galaxy sheet 6.1 (tags A1:...).
import gx, json, sys, os, math

W = os.path.join(gx.S, 'w')
K = json.load(open(os.path.join(W, 'k65.json'), encoding='utf-8'))
K1 = json.load(open(os.path.join(W, 'k61.json'), encoding='utf-8'))
KX, KY = 298179.0, 455939.0          # kit 6.5 sheet origin
K1X = 172179.0                       # kit 6.1 sheet origin (same y)
XE0 = 301182.0                       # kit beam end E0 (x)
YT, YB = 468700.0, 468150.0
SEC0 = (305617.0, 462413.0)          # kit section S0: beam bottom-left (xL, yb), drawn x2.5
SSC = 2.5                            # sections x2.5 (1:20 on the 1:50 sheet, as the analog)
DIA = 28
_R65 = set(k[2:] for k in K)
NODE_A = [k for k in K1 if k.startswith('A1:407B') and k[2:] not in _R65]
SPL = dict(top=['A1:4038F3', 'A1:4038F2'], bot=['A1:403948', 'A1:403947'], tdim=['A1:4038F1', 'A1:4038F5'],
           bdim=['A1:403992', 'A1:40394A'], tcomb='A1:4038F4', bcomb='A1:403949')


def e0(k):
    v = k['e']
    return [float(q) for q in v[1:].split(',')] if v.startswith('E') else None


def level_ops(s, h, base, value, off1, off2):
    """set the value of the SPDS level mark h placed at base (point 0)"""
    if len(value) <= 6:
        s.add(t='levelval', h=h, old='-0.100', value=value, tag=h)
        return
    t = h + '_L7'
    s.add(t='clone', h='E3B69', tag=t)
    s.add(t='mcset', h=t, set={'Scale': 50})
    s.add(t='levelval', h=t, old='+10.250', value=value, tag=t)
    s.add(t='moveto', h=t, idx=0, to=base)
    s.add(t='spmove', h=t, items=[[2, base[0] + off2, base[1]], [1, base[0] + off1, base[1] + 300]])
    s.add(t='erase', h=[h])


class Sheet:
    def __init__(s, M, part):
        s.M = M; s.part = part
        s.P = part['P']; s.dx = part['SX'] - KX; s.dy = part['SY'] - KY
        s.b, s.h = M['b'], M['h']
        s.u0, s.u1 = part['u0'], part['u1']
        s.cutL, s.cutR = s.u0 > 1, s.u1 < M['E'] - 1
        s.ops = []; s.n = 0
        s.YT = YT + s.dy; s.YB = s.YT - s.h
        s.YTB = s.YT - 50; s.YBB = s.YB + 50
        s.dl = -(s.h - 550.0)
        s.lay = 'диам25'

    def add(*a, **k): a[0].ops.append(k)
    def T(s, r): return s.P + r[2:]
    def X(s, u): return XE0 + s.dx + (u - s.u0)
    def lo(s, y): return y + s.dy + s.dl
    def up(s, y): return y + s.dy
    def clone(s, src, label):
        s.n += 1; t = '%s_%s%d' % (s.P, label, s.n)
        s.add(t='clone', h=src, tag=t); return t

    # ------------------------------------------------------------------ kit clone
    def clone_ops(s, splices):
        import re
        mp = gx.tagmap(); rx = re.compile('^' + re.escape(s.P) + '(?=[:XSN_])')
        old = [v for k, v in mp.items() if rx.match(k)]
        ops = ([dict(t='erase', h=old)] if old else []) + [dict(t='eraseregion', win=[KX + s.dx - 10, KY + s.dy - 10, KX + s.dx + 31510, KY + s.dy + 14860])]
        for r in K:
            if not r.startswith('A5') or r.startswith('A5S1_') or r.startswith('A5S2_'): continue
            ops.append(dict(t='clone', h=K[r]['h'], base=[0, 0], to=[s.dx, s.dy], tag=s.P + r[2:]))
        if splices:
            for r in list(SPL['top']) + SPL['bot'] + SPL['tdim'] + SPL['bdim'] + [SPL['tcomb'], SPL['bcomb']] + NODE_A:
                ops.append(dict(t='clone', h=K1[r]['h'], base=[K1X, 0], to=[KX + s.dx, s.dy], tag=s.P + 'N' + r[3:]))
        return ops

    # ------------------------------------------------------------------ elevation
    def elevation(s):
        M = s.M; T, X, lo = s.T, s.X, s.lo
        u0, u1 = s.u0, s.u1
        inn = lambda u: u0 - 1 <= u <= u1 + 1
        sups = [(max(a, u0), min(b, u1), k) for a, b, k in M['sups'] if b > u0 - 1 and a < u1 + 1]
        ycol_t, ycol_b = s.YT + 97, s.YB - 180
        colp = [T('A5:40159B'), T('A5:4018B7')]
        brk = [(T('A5_BR0t'), T('A5_BR0b')), (T('A5_BR1t'), T('A5_BR1b'))]
        nb = 0
        for i, (a, b, k) in enumerate(sups):
            if k == 'col':
                h = colp.pop(0) if colp else s.clone(T('A5:40159B'), 'COL')
                s.add(t='plset', h=h, p=[[X(a), ycol_t], [X(b), ycol_t], [X(b), ycol_b], [X(a), ycol_b]], closed=True)
                bt, bb = brk.pop(0) if brk else (s.clone(T('A5_BR0t'), 'BRt'), s.clone(T('A5_BR0b'), 'BRb'))
                for hh, y in ((bt, ycol_t), (bb, ycol_b)):
                    s.add(t='mcset', h=hh, set={'StartPoint': [X(a), y], 'EndPoint': [X(b), y], 'ClipZonePoint': [X(b), y], 'Length': X(b) - X(a)})
            else:   # supporting beam: its section outline (no breaks)
                hb = M.get('suph', {}).get(str(round((a + b) / 2)), s.h)
                h = colp.pop(0) if colp else s.clone(T('A5:40159B'), 'COL')
                s.add(t='plset', h=h, p=[[X(a), s.YT], [X(b), s.YT], [X(b), s.YT - hb], [X(a), s.YT - hb]], closed=True)
        s.add(t='erase', h=colp + [q for p in brk for q in p])
        # vertical break lines at cut ends (analog SPDSBREAK, turned vertical)
        for u in ([u0] if s.cutL else []) + ([u1] if s.cutR else []):
            hb = s.clone(T('A5_BR0t'), 'CUT')
            s.add(t='mcset', h=hb, set={'StartPoint': [X(u), s.YB - 250], 'EndPoint': [X(u), s.YT + 250], 'ClipZonePoint': [X(u), s.YT + 250], 'Length': s.h + 500})
        # axes
        axp = [T('A5:401290'), T('A5:401291')]
        for (x, v) in [(x, v) for x, v in M['axes'] if inn(x)]:
            h = axp.pop(0) if axp else s.clone(T('A5:401290'), 'AX')
            s.add(t='axis', h=h, s=[X(x), s.YT], e=[X(x), lo(466361)], val=v)
        s.add(t='erase', h=axp)
        # beam outline per span (between faces / ends / cuts)
        faces = [u0] + [c for a, b, _ in sups for c in (a, b)] + [u1]
        spans = [(faces[i], faces[i + 1]) for i in range(0, len(faces), 2) if faces[i + 1] - faces[i] > 1]
        rp = [T('A5:40159C'), T('A5:402404')]
        for (a, b) in spans:
            h = rp.pop(0) if rp else s.clone(T('A5:40159C'), 'SP')
            s.add(t='plset', h=h, p=[[X(b), s.YB], [X(b), s.YT], [X(a), s.YT], [X(a), s.YB]], closed=True)
        s.add(t='erase', h=rp)
        # main bars (to the cut line at a cut end), Ск1 only at real beam ends
        xa = X(u0) + (0 if s.cutL else 20); xb = X(u1) - (0 if s.cutR else 20)
        s.add(t='plset', h=T('A5:4015A8'), p=[[xa, s.YTB], [xb, s.YTB]], layer=s.lay)
        s.add(t='plset', h=T('A5:4015AE'), p=[[xa, s.YBB], [xb, s.YBB]], layer=s.lay)
        yb, yt = s.YBB + 20, s.YTB - 20; yk = (yb + yt) / 2; L = 250
        if s.cutL: s.add(t='erase', h=[T('A5:4015C1'), T('A5:4015C2')])
        else:
            e0 = X(u0) + 20
            s.add(t='plset', h=T('A5:4015C1'), p=[[e0 + L, yb], [e0 + 25, yb], [e0, yb + 25], [e0, yt - 25], [e0 + 25, yt], [e0 + L, yt]])
            s.add(t='moveto', h=T('A5:4015C2'), idx=1, to=[e0, yk])
            s.add(t='spmove', h=T('A5:4015C2'), items=[[0, e0 - 226, s.up(469197)]])
        if s.cutR: s.add(t='erase', h=[T('A5:4069BF'), T('A5:4069C0')])
        else:
            e1 = X(u1) - 20
            s.add(t='plset', h=T('A5:4069BF'), p=[[e1 - L, yb], [e1 - 25, yb], [e1, yb + 25], [e1, yt - 25], [e1 - 25, yt], [e1 - L, yt]])
            s.add(t='moveto', h=T('A5:4069C0'), idx=1, to=[e1, yk])
            s.add(t='spmove', h=T('A5:4069C0'), items=[[0, e1 + 226, s.up(469197)]])
        # доп bars of this part
        barp = [T('A5:4274A8'), T('A5:4274AA')]; notep = [T('A5:4274A9'), T('A5:4274AB')]
        s.dopx = []
        for d in M['dops']:
            a, b = max(d['a'], u0), min(d['b'], u1)
            if b - a < 1: continue
            y = s.YTB - 50 if d['top'] else s.YBB + 50
            hb = barp.pop(0) if barp else s.clone(T('A5:4274A8'), 'DB')
            s.add(t='plset', h=hb, p=[[X(a), y], [X(b), y]], layer=s.lay)
            hn = notep.pop(0) if notep else s.clone(T('A5:4274A9'), 'DN')
            # free spot on the top callout row: away from splice combs, section marks, Ск1, other callouts
            busy = list(s.dopx) + [x for _, x, _ in s.part['secs']]
            for kind, c, _ in s.part.get('spl', []): busy += [c - 480, c - 250, c + 250] if kind == 'top' else [c - 180, c, c + 500]
            if not s.cutL: busy.append(u0)
            if not s.cutR: busy.append(u1)
            L_ = b - a
            cand = ([a + min(600, L_ / 3), a + L_ * 0.5, a + L_ * 0.25, a + L_ * 0.75, a + 300, b - 300] if d['top'] else
                    [b - min(600, L_ / 3), a + L_ * 0.5, a + L_ * 0.75, a + L_ * 0.25, b - 300, a + 300])
            cand = [c for c in cand if a + 150 <= c <= b - 150]
            ok = [c for c in cand if all(abs(c - q) > 1100 for q in busy)]
            un = ok[0] if ok else max(cand, key=lambda c: min([abs(c - q) for q in busy] or [1e9]))
            s.dopx.append(un)
            xn = X(un)
            ysh = s.up(469289) if d['top'] else s.up(469289) - 30
            s.add(t='spmove', h=hn, items=[[0, xn, ysh], [1, xn, y]])
            s.add(t='mcset', h=hn, set={'FirstLine': d['pos'], 'SecondLine': '(ф%d)' % DIA})
        s.add(t='erase', h=barp + notep)
        # hoop zones: boundary lines + chain (axis/end -> first hoop | zones | last hoop -> axis/end)
        HL = [T(r) for r in ['A5:4015B6', 'A5:40389F', 'A5:4038A0', 'A5:4038A1', 'A5:4038A2', 'A5:4038A3']]
        ZD = [T(r) for r in ['A5:4033EB', 'A5:4033C1', 'A5:403439', 'A5:403749']]
        ED = [T(r) for r in ['A5:40347E', 'A5:403446', 'A5:403605']]
        ych, ytx = lo(467342), lo(467400)
        chain = []
        supc = [((a + b) / 2.0, k) for a, b, k in M['sups']]
        def ref_left(fL):
            for c, k in supc:
                for a, b, kk in M['sups']:
                    if abs(b - fL) < 2: return (a + b) / 2.0
            return 0.0
        for z in M['zones']:
            if z['fR'] < u0 + 1 or z['fL'] > u1 - 1: continue
            def refp(a, b):          # axis inside the support, else its centre
                ax_in = [u for u, _ in M['axes'] if a - 1 <= u <= b + 1]
                return ax_in[0] if ax_in else (a + b) / 2.0
            l0 = next((refp(a, b) for a, b, _ in M['sups'] if abs(b - z['fL']) < 2), z['fL'] if z['fL'] > 1 else 0.0)
            l1 = next((refp(a, b) for a, b, _ in M['sups'] if abs(a - z['fR']) < 2), z['fR'] if z['fR'] < M['E'] - 1 else M['E'])
            l0, l1 = max(l0, u0), min(l1, u1)
            for x in z['lines']:
                h = HL.pop(0) if HL else s.clone(T('A5:4015B6'), 'HL')
                s.add(t='plset', h=h, p=[[X(x), s.YBB], [X(x), s.YTB]], layer='диам10')
            first = z['segs'][0][0]; last = z['segs'][-1][1]
            chain.append((l0, first, '', 'E'))
            for (p, q, t) in z['segs']: chain.append((p, q, t, None))
            chain.append((last, l1, '', 'E'))
        for i, (p, q, txt, side) in enumerate(chain):
            if q - p < 1: continue
            if 'х' in txt: h = ZD.pop(0) if ZD else s.clone(T('A5:4033EB'), 'ZD')
            else: h = ED.pop(0) if ED else s.clone(T('A5:40347E'), 'ED')
            s.add(t='dimpts', h=h, p1=[X(p), s.YB, 0], p2=[X(q), s.YB, 0], dl=[X(q), ych, 0])
            s.add(t='dimtext', h=h, s=txt); s.add(t='dimdef', h=[h])
            if 'х' not in txt and q - p < 500:     # short: text outside, near the edge
                left = (i == 0) or (i + 1 < len(chain) and chain[i + 1][0] - q > 1)
                s.add(t='dimtx', h=h, at=[X(p) - 190 if i == 0 else X(q) + 190 if i == len(chain) - 1 else (X(p) + X(q)) / 2, ytx if i in (0, len(chain) - 1) else ytx - 250, 0])
        s.add(t='erase', h=HL + ZD + ED)
        # row 2: faces / ends; row 3: axes + ends
        r2 = sorted(set([round(u0)] + [round(c) for a, b, _ in sups for c in (a, b)] + [round(u1)]))
        cp = [T(r) for r in ['A5:401296', 'A5:40129A', 'A5:40129E', 'A5:4012A2', 'A5:4012A5']]
        for j, (p, q) in enumerate(zip(r2, r2[1:])):
            h = cp.pop(0) if cp else s.clone(T('A5:40129E'), 'R2')
            s.add(t='dimpts', h=h, p1=[X(p), lo(466361), 0], p2=[X(q), lo(466361), 0], dl=[X(q), lo(466773), 0])
            s.add(t='dimtext', h=h, s=''); s.add(t='dimdef', h=[h])
            if q - p < 400: s.add(t='dimtx', h=h, at=[X(p) - 190 if j == 0 else X(q) + 190, lo(466830), 0])
        s.add(t='erase', h=cp)
        ax = [x for x, v in M['axes'] if inn(x)]
        r3 = sorted(set(([round(u0)] if round(u0) not in [round(a) for a in ax] else []) + [round(a) for a in ax] + [round(u1)]))
        r3p = [T('A5:401292'), T('A5_R31')]
        for j, (p, q) in enumerate(zip(r3, r3[1:])):
            h = r3p.pop(0) if r3p else s.clone(T('A5:401292'), 'R3')
            s.add(t='dimpts', h=h, p1=[X(p), lo(466361), 0], p2=[X(q), lo(466361), 0], dl=[X(q), lo(466411), 0])
            s.add(t='dimtext', h=h, s=''); s.add(t='dimdef', h=[h])
            if q - p < 400: s.add(t='dimtx', h=h, at=[X(q) + 190, lo(466470), 0])
        s.add(t='erase', h=r3p)
        # heights at the left end
        x0 = X(u0)
        s.add(t='dimpts', h=T('A5:4015A4'), p1=[x0, s.YT, 0], p2=[x0, s.YB, 0], dl=[x0 - 972, s.YB, 0])
        s.add(t='dimpts', h=T('A5:4015AD'), p1=[x0, s.YB, 0], p2=[x0 + 20, s.YBB, 0], dl=[x0 - 437, s.YBB, 0])
        s.add(t='dimpts', h=T('A5:401933'), p1=[x0 + 20, s.YBB, 0], p2=[x0 + 20, s.YTB, 0], dl=[x0 - 437, s.YTB, 0])
        s.add(t='dimpts', h=T('A5:4015A9'), p1=[x0 + 20, s.YTB, 0], p2=[x0 - 7, s.YT, 0], dl=[x0 - 437, s.YT, 0])
        hd4 = [T('A5:4015A4'), T('A5:4015AD'), T('A5:401933'), T('A5:4015A9')]
        for hh in hd4: s.add(t='dimtext', h=hh, s='')
        s.add(t='dimdef', h=hd4)
        # «1 (ф28)» callouts: one per span longer than 2.5 m, 300 inside the first hoop-zone boundary
        n1 = [T('A5:4015B1'), T('A5:40671E')]
        for z in M['zones']:
            if z['fR'] - z['fL'] < 2500 or z['fR'] < u0 + 1 or z['fL'] > u1 - 1: continue
            busy = [c for _, c, _ in s.part.get('spl', [])] + [x for _, x, _ in s.part['secs']] +                    list(s.dopx)
            cand = ([z['lines'][1] + 300] if len(z['lines']) > 2 else []) + [(z['fL'] + z['fR']) / 2, z['fL'] + (z['fR'] - z['fL']) * 0.35,
                    z['fL'] + (z['fR'] - z['fL']) * 0.65, z['fL'] + 600, z['fR'] - 600]
            cand = [c for c in cand if u0 + 300 < c < u1 - 300 and all(abs(c - b) > 1300 for b in busy)]
            if not cand: continue
            xx = cand[0]
            h = n1.pop(0) if n1 else s.clone(T('A5:4015B1'), 'N1')
            s.add(t='spmove', h=h, items=[[0, X(xx), s.up(469238.6)], [1, X(xx), s.YBB], [2, X(xx), s.YTB]])
            s.add(t='mcset', h=h, set={'SecondLine': '(ф%d)' % DIA})
        s.add(t='erase', h=n1)
        s.add(t='moveto', h=T('A5:414D1E'), idx=1, to=[X(u1) + 120, ych])
        s.add(t='mcset', h=T('A5:414D1E'), set={'FirstLine': 'Шаг хомута', 'SecondLine': 'Х1(ф%d)' % M['hd']})
        # section marks
        sp = [T(r) for r in ['A5:4015BF', 'A5:40F7E4', 'A5:40F7E6']]
        for (w, x, _) in s.part['secs']:
            h = sp.pop(0) if sp else s.clone(T('A5:4015BF'), 'SM')
            s.add(t='sp_set', h=h, pts=[[0, X(x), s.up(469793.5)], [1, X(x), lo(465833.7)]])
            s.add(t='mcset', h=h, set={'Word': w})
        s.add(t='erase', h=sp)
        # level: one value (top of rigel) on the analog mark; the two-level note removed
        s.add(t='moveto', h=T('A5:4015A3'), idx=0, to=[x0 + 400, s.YT])
        level_ops(s, T('A5:4015A3'), [x0 + 400, s.YT], M['level'], -2346.9, -1726.4)
        s.add(t='erase', h=[T('A5_ML')])
        xc = (X(u0) + X(u1)) / 2
        s.add(t='moveto', h=T('A5:4038B1'), idx=0, to=[xc, s.up(470114)])
        s.add(t='settext', h=T('A5:4038B1'), s='Ригель ' + M['mark'] + s.part.get('suffix', ''))
        s.spans = spans; s.sups = sups
        if s.part.get('node'):      # tall rigel: node «А» moved below the section
            s.add(t='move', h=[s.P + 'N' + r[3:] for r in NODE_A], d=list(s.part['node']))

    # ------------------------------------------------------------------ splices (накладки Н4 Ø28)
    def splices(s):
        T, X, lo = s.T, s.X, s.lo
        st = s.part.get('spl', [])
        if not st:
            return
        tops = [p for p in st if p[0] == 'top']; bots = [p for p in st if p[0] == 'bot']
        def plate(hh, c, y):
            s.add(t='plset', h=hh, p=[[X(c) - 140, y - 15], [X(c) - 140, y + 15], [X(c) + 140, y + 15], [X(c) + 140, y - 15]], closed=True)
        for i, (_, c, ref) in enumerate(tops):
            hp = [(s.P + 'N4038F3'), (s.P + 'N4038F2')] if i == 0 else [s.clone((s.P + 'N4038F3'), 'PL'), s.clone((s.P + 'N4038F2'), 'PL')]
            plate(hp[0], c - 250, s.YTB); plate(hp[1], c + 250, s.YTB)
            hd = [(s.P + 'N4038F1'), (s.P + 'N4038F5')] if i == 0 else [s.clone((s.P + 'N4038F1'), 'PD'), s.clone((s.P + 'N4038F5'), 'PD')]
            s.add(t='dimpts', h=hd[0], p1=[X(c - 250), s.YTB, 0], p2=[X(ref), s.YT, 0], dl=[X(ref), s.up(469559), 0])
            s.add(t='dimpts', h=hd[1], p1=[X(c + 250), s.YTB, 0], p2=[X(c - 250), s.YTB, 0], dl=[X(c - 250), s.up(469559), 0])
            hc = (s.P + 'N4038F4') if i == 0 else s.clone((s.P + 'N4038F4'), 'PC')
            k = K1['A1:4038F4']; px, py = map(float, k['pts'][0].split(','))
            s.add(t='move', h=[hc], d=[X(c - 250) - (px - K1X + KX + s.dx) - 230, s.up(468950) - (py + s.dy) + 0])
            s.add(t='mcset', h=hc, set={'FirstLine': 'Н4'})
        if not tops: s.add(t='erase', h=[s.P + 'N' + r for r in ['4038F3', '4038F2', '4038F1', '4038F5', '4038F4']])
        for i, (_, c, ref) in enumerate(bots):
            hp = [(s.P + 'N403948'), (s.P + 'N403947')] if i == 0 else [s.clone((s.P + 'N403948'), 'PL'), s.clone((s.P + 'N403947'), 'PL')]
            plate(hp[0], c, s.YBB); plate(hp[1], c + 500, s.YBB)
            hd = [(s.P + 'N403992'), (s.P + 'N40394A')] if i == 0 else [s.clone((s.P + 'N403992'), 'PD'), s.clone((s.P + 'N40394A'), 'PD')]
            s.add(t='dimpts', h=hd[0], p1=[X(c), s.YB, 0], p2=[X(ref), s.YB, 0], dl=[X(ref), lo(467665), 0])
            s.add(t='dimpts', h=hd[1], p1=[X(c + 500), s.YBB, 0], p2=[X(c), s.YBB, 0], dl=[X(c), lo(467665), 0])
            hc = (s.P + 'N403949') if i == 0 else s.clone((s.P + 'N403949'), 'PC')
            k = K1['A1:403949']; px, py = map(float, k['pts'][0].split(','))
            s.add(t='move', h=[hc], d=[X(c) - (px - K1X + KX + s.dx) - 180, s.up(468834) - (py + s.dy)])
            s.add(t='mcset', h=hc, set={'FirstLine': 'Н4'})
        if not bots: s.add(t='erase', h=[s.P + 'N' + r for r in ['403948', '403947', '403992', '40394A', '403949']])

    # ------------------------------------------------------------------ sections (kit S0 x2.5 -> ours x2)
    def sections(s):
        M = s.M; b, h, sl = s.b, s.h, M['slab']
        S0 = [r for r in K if r.startswith('A5S0_')]
        BX = M['bx']; nb = len(BX)
        yT, yB = h - 50.0, 50.0
        f = SSC / 2.5
        for j, (w, xcut, dops) in enumerate(s.part['secs']):
            ox, oy = s.part['secpos'][j]
            g = lambda u, v: [ox + SSC * u, oy + SSC * v]
            pre = '%sX%d_' % (s.P, j)
            for r in S0:
                s.add(t='clone', h=s.T(r), base=[SEC0[0] + s.dx, SEC0[1] + s.dy], to=[ox, oy], s=f, tag=pre + r[5:])
            Q = lambda r: pre + r
            dims = [Q(r[5:]) for r in S0 if K[r]['t'] == 'DIMENSION']
            s.add(t='dimset', h=dims, lfac=1.0 / SSC, dscale=50)
            for r in S0:
                if K[r]['t'].startswith('SPDS') and K[r]['t'] != 'SPDSBREAK': s.add(t='mcset', h=Q(r[5:]), set={'Scale': 50})
            s.add(t='plset', h=Q('2CAF82'), p=[g(b, 0), g(b, h - sl), g(b + 173, h - sl), g(b + 173, h), g(-173, h), g(-173, h - sl), g(0, h - sl), g(0, 0)], closed=True)
            bot = ['2CAF83', '2CB036', '2CB03D', '2CAFDE']; top = ['2CAFF5', '2CB044', '2CB04B', '2CAFFC']
            if nb == 3: bot = ['2CAF83', '2CB036', '2CAFDE']; top = ['2CAFF5', '2CB044', '2CAFFC']; s.add(t='erase', h=[Q('2CB03D'), Q('2CB04B'), Q('2CB080')])
            if nb == 6:
                for k in range(2):
                    for lst, src in ((bot, '2CB036'), (top, '2CB044')):
                        t_ = '%s_X%d' % (src, k); s.add(t='clone', h=Q(src), tag=Q(t_)); lst.insert(2, t_)
            for hh, x in zip(bot, BX):
                s.add(t='insat', h=Q(hh), at=g(x, yB)); s.add(t='dyn', h=Q(hh), prop='Вид', value='Ø%d' % DIA)
            for hh, x in zip(top, BX):
                s.add(t='insat', h=Q(hh), at=g(x, yT)); s.add(t='dyn', h=Q(hh), prop='Вид', value='Ø%d' % DIA)
            cover = 3 if nb == 6 else 2                      # one hoop spans BX[i]..BX[i+cover]
            hoops = [('2CB003', BX[0])] if nb == 3 else [('2CB003', BX[0]), ('2CB080', BX[-1 - cover])]
            for hh, x in hoops:
                ix, iy = g(x, yB + 10.8)
                s.add(t='insat', h=Q(hh), at=[ix, iy])
                # dynamic parameters of a cloned block do not regenerate -> explode to the hoop polyline and stretch it
                s.add(t='explode', h=Q(hh), pre=Q(hh) + 'P')
                hp = Q(hh) + 'P0'
                # hoop around the bars: right / top outer edge = bar centre + 14 (Ø28/2) + 10 (hoop)
                s.add(t='pfit', h=hp, right=g(x + (BX[cover] - BX[0]) + 24, 0)[0], top=g(0, yT + 24)[1])
            # side bars Ø12 (h > 700): both faces inside the hoop legs, equal spacing between the rows
            ns = M.get('nside', 0)
            ysides = [yB + (yT - yB) * (i + 1) / (ns + 1) for i in range(ns)]
            for i, yy in enumerate(ysides):
                for side, xx in (('L', BX[0] + 7), ('R', BX[-1] - 7)):
                    t_ = '%sS%s%d' % (pre, side, i)
                    s.add(t='clone', h=Q('2CAF83'), tag=t_); s.add(t='insat', h=t_, at=g(xx, yy)); s.add(t='dyn', h=t_, prop='Вид', value='Ø12')
            yd = -306.0
            s.add(t='dimpts', h=Q('2CAF9A'), p1=g(BX[0], 0) + [0], p2=g(0, 0) + [0], dl=g(0, yd) + [0])
            s.add(t='dimpts', h=Q('2CB052'), p1=g(BX[-1], 0) + [0], p2=g(BX[0], 0) + [0], dl=g(BX[0], yd) + [0])
            st = (BX[-1] - BX[0]) / (nb - 1)
            s.add(t='dimtext', h=Q('2CB052'), s='%dх%d=%d' % (round(st), nb - 1, round(BX[-1] - BX[0])))
            s.add(t='dimpts', h=Q('2CAFE5'), p1=g(b, 0) + [0], p2=g(BX[-1], 0) + [0], dl=g(BX[-1], yd) + [0])
            s.add(t='dimpts', h=Q('2CB028'), p1=g(0, yd) + [0], p2=g(b, yd) + [0], dl=g(b, -648) + [0])
            xv = -230.0
            for hh, (p, q) in zip(['2CAFAA', '2CAFBB', '2CAFCA'], [(0, yB), (yB, yT), (yT, h)]):
                s.add(t='dimpts', h=Q(hh), p1=g(BX[0] + 50, p) + [0], p2=g(BX[0] + 50, q) + [0], dl=g(xv, q) + [0])
            s.add(t='dimpts', h=Q('2CB01B'), p1=g(-173, h) + [0], p2=g(0, 0) + [0], dl=g(-400, 0) + [0])
            for hh in ['2CAF9A', '2CAFE5', '2CB028', '2CAFAA', '2CAFBB', '2CAFCA', '2CB01B']: s.add(t='dimtext', h=Q(hh), s='')
            s.add(t='dimdef', h=[Q(hh) for hh in ['2CB028', '2CAFBB', '2CB01B']])
            s.add(t='dimdef', h=[Q('2CB052')])
            s.add(t='dimtx', h=Q('2CAF9A'), at=g(-95, yd + 45) + [0])
            s.add(t='dimtx', h=Q('2CAFE5'), at=g(b + 95, yd + 45) + [0])
            s.add(t='dimtx', h=Q('2CAFAA'), at=g(xv - 45, -95) + [0])
            s.add(t='dimtx', h=Q('2CAFCA'), at=g(xv - 45, h + 95) + [0])
            for hh, x in (('2CB014', b + 173), ('2CB015', -173)):
                s.add(t='mcset', h=Q(hh), set={'StartPoint': g(x, h - sl), 'EndPoint': g(x, h), 'ClipZonePoint': g(x, h), 'Length': SSC * sl})
            s.add(t='moveto', h=Q('2CB018'), idx=0, to=g(-173, h))
            level_ops(s, Q('2CB018'), g(-173, h), M['level'], -1734.1, -1113.7)
            s.add(t='erase', h=[Q('2CC663')])
            ys = h + 170
            s.add(t='combsegs', h=Q('2CB019'), segs=[[g(x, yT - 1), g(x + 90, ys)] for x in BX], start=g(BX[-1] + 90, ys), end=g(BX[0] + 90, ys), trim=True)
            s.add(t='mcset', h=Q('2CB019'), set={'SecondLine': '(ф%d)' % DIA})
            yk = yB - 151
            s.add(t='combsegs', h=Q('2CB01A'), segs=[[g(x, yB - 2), g(x + 75, yk)] for x in BX], start=g(BX[-1] + 115, yk), end=g(BX[0] + 75, yk), trim=True)
            s.add(t='mcset', h=Q('2CB01A'), set={'SecondLine': '(ф%d)' % DIA})
            ym = max((yB + yT) / 2, yB + 340) if not ns else max((yB + ysides[0]) / 2, yB + 340)
            legs = [[g(BX[-1] + 15, ym), g(b + 190, ym)]] + ([[g(BX[cover] + 15, ym), g(b + 190, ym)]] if nb >= 4 else [])
            s.add(t='combsegs', h=Q('2CB07F'), segs=legs, trim=True)
            s.add(t='spmove', h=Q('2CB07F'), items=[[0] + g(b + 190, ym)])
            s.add(t='mcset', h=Q('2CB07F'), set={'SecondLine': '(ф%d)' % M['hd']})
            if ns:      # side-bar callout: comb from the right-face bars to a shelf right of the section
                t_ = '%sSC' % pre
                ysh = ysides[-1] + 120
                s.add(t='clone', h=Q('2CB01A'), tag=t_)
                segs = [[g(BX[-1] - 7, yy), g(b + 120, ysh)] for yy in ysides]
                s.add(t='combsegs', h=t_, segs=segs, start=g(b + 120, ysh), end=g(b + 120 + 220, ysh), trim=True)
                s.add(t='mcset', h=t_, set={'FirstLine': M['side_pos'], 'SecondLine': '(ф12)'})
            s.add(t='moveto', h=Q('2CB016'), idx=0, to=g(b / 2.0, h + 470))
            s.add(t='settext', h=Q('2CB016'), s='Разрез %s - %s' % (w, w))
            # доп bars in this cut: between the main bars (first row), the rest 2nd row 70 clear below/above
            for d in dops:
                gaps = [(BX[i] + BX[i + 1]) / 2 for i in range(nb - 1)]
                order = [gaps[0], gaps[-1], gaps[len(gaps) // 2]] if len(gaps) == 3 else gaps
                xs1 = order[:min(d['n'], len(order))]
                rest = d['n'] - len(xs1)
                y = yT if d['top'] else yB
                y2 = y - 98 if d['top'] else y + 98
                pts = [(x, y) for x in sorted(xs1)] + [(x, y2) for x in [BX[0], BX[-1], BX[1], BX[-2]][:rest]]
                src = Q('2CAFF5' if d['top'] else '2CAF83')
                for i, (xx, yy) in enumerate(pts):
                    t = '%sD%s%s_%d' % (pre, 'T' if d['top'] else 'B', d['pos'], i)
                    s.add(t='clone', h=src, tag=t); s.add(t='insat', h=t, at=g(xx, yy))
                t = '%sDC%s%s' % (pre, 'T' if d['top'] else 'B', d['pos'])
                s.add(t='clone', h=Q('2CB019' if d['top'] else '2CB01A'), tag=t)
                if d['top']:
                    ysh = h + 330
                    segs = [[g(xx, yy - 1), g(xx - (ysh - yy) * 0.45, ysh)] for xx, yy in pts]
                    xe = [q[1][0] for q in segs]
                    s.add(t='combsegs', h=t, segs=segs, start=[max(xe), segs[0][1][1]], end=[min(xe) - SSC * 220, segs[0][1][1]], trim=True)
                else:
                    ysh = yB + 105 + (60 if any(yy > yB + 50 for _, yy in pts) else 0)
                    segs = [[g(xx, yy + 2), g(b + 120, ysh)] for xx, yy in pts]
                    s.add(t='combsegs', h=t, segs=segs, start=g(b + 120, ysh), end=g(b + 120 + 220, ysh), trim=True)
                s.add(t='mcset', h=t, set={'FirstLine': d['pos'], 'SecondLine': '(ф%d)' % DIA})
        s.add(t='erase', h=[s.T(r) for r in K if r.startswith('A5S0_')])
        s.add(t='regen')

    # ------------------------------------------------------------------ details, texts
    def texts(s):
        M = s.M; T = s.T
        X1, SK = M['X1'], M['SK']
        vals = {'A5:406493': X1[0], 'A5:40648A': X1[1], 'A5:40648B': X1[2], 'A5:40648D': X1[3], 'A5:406499': sum(X1),
                'A5:4064A7': SK[1], 'A5:4064A8': SK[0], 'A5:4064AB': SK[2], 'A5:4064B0': sum(SK)}
        for r, v in vals.items(): s.add(t='settext', h=T(r), s=str(v))
        s.add(t='move', h=[T('A5:4064B0'), T('A5:4064B9'), T('A5:406499'), T('A5:4064A4')], d=[-260, 0])
        s.add(t='move', h=[T('A5:40648D')], d=[150, 0])      # X1 sketch: right height text clear of the hoop line
        s.add(t='settext', h=T('A5:404440'), s=s.part['no'])
        s.add(t='settext', h=T('A5:404442'), s='Ригель ' + M['mark'])
        s.add(t='settext', h=T('A5:40443D'), s='\\pxi-3.3333,l3.3333,t3.3333;1.\tОбщие указания см. л. - 1.1\\P2.\tДанный лист читать '
              'совместно с л. 6.1 ... 6.4\\P3.\tСтержни, указанные в "Ведомости деталей", должны гнуться механическим способом '
              'в холодном состоянии с радиусом гиба 3d - 5d, где d - диаметр стержня')

    # ------------------------------------------------------------------ tables (whole mark; on the last part)
    def tables(s):
        M = s.M; sp, stl = s.T('A5:406488'), s.T('A5:4064CF')
        F, I = '%lu2%pr2', '%lu2%pr0'
        rows = list(M['specrows'])                    # [(pos, dia, L or None, count)]
        nd = len(rows)
        ops = []
        if nd < 2: ops.append(dict(t='trows', h=sp, mode='del', at=6 + nd, n=2 - nd))
        ops.append(dict(t='theight', h=sp, rows=[[r_, 400] for r_ in range(6, 9 + nd)]))   # deleted rows must not stretch the rest
        if nd > 2:
            ops.append(dict(t='trows', h=sp, mode='ins', at=7, n=nd - 2, **{'from': 7}))
            ops.append(dict(t='move', h=[sp], d=[0, 400.0 * (nd - 2)]))
        last = 5 + nd; conc = last + 2
        side_row = next((6 + i for i, q in enumerate(rows) if q[2] is None), 0)
        cells_t = [[2, 2, 'Ригель ' + M['mark']], [3, 0, 'Х1*'], [3, 5, '240']]
        nums = [[3, 3, M['hd'], I], [3, 9, sum(M['X1']), I], [4, 3, 16, I], [4, 9, sum(M['SK']), I], [5, 3, DIA, I]]
        forms = [[3, 10, '%d*%d' % (M['NH'], M['legs'] // 2), I], [3, 11, 'D4*D4*3.1415926/4*0.00785*J4/1000', F], [3, 12, 'L4*K4', F],
                 [4, 10, '%d*2' % M['n'], I], [4, 11, 'D5*D5*3.1415926/4*0.00785*J5/1000', F], [4, 12, 'L5*K5', F],
                 [5, 10, '%.2f*%d' % ((M['E'] - 40) / 1000.0, 2 * M['n']), F], [5, 11, 'D6*D6*3.1415926/4*0.00785*1', F], [5, 12, 'L6*K6', F]]
        for i, (pos, dia, L, n) in enumerate(rows):
            r = 6 + i; R = r + 1
            cells_t += [[r, 0, pos], [r, 1, 'ГОСТ 34028-2016'], [r, 2, '%%C'], [r, 4, 'A'], [r, 5, '500С'], [r, 8, 'L=']]
            nums += [[r, 3, dia, I]]
            if L is None:
                cells_t += [[r, 9, 'пог.м.']]
                forms += [[r, 10, '%.2f' % n, F], [r, 11, 'D%d*D%d*3.1415926/4*0.00785*1' % (R, R), F], [r, 12, 'L%d*K%d' % (R, R), F]]
            else:
                nums += [[r, 9, L, I]]
                forms += [[r, 10, '%d' % n, I], [r, 11, 'D%d*D%d*3.1415926/4*0.00785*J%d/1000' % (R, R, R), F], [r, 12, 'L%d*K%d' % (R, R), F]]
        forms += [[2, 12, 'Sum(M4:M%d)' % (last + 1), F],
                  [conc, 12, '%.2f*%.2f*%.2f' % (M['b'] / 1000.0, (M['h'] - M['slab']) / 1000.0, M['clear'] / 1000.0), F]]
        ops += [dict(t='tnum', h=sp, cells=nums), dict(t='tset', h=sp, cells=cells_t), dict(t='tformula', h=sp, cells=forms)]
        m = gx.tagmap()
        ops += [dict(t='tset', h=stl, cells=[[5, 1, '%%%%C%d' % M['hd']], [6, 0, 'Ригель ' + M['mark']]]),
                dict(t='tformula', h=stl, cells=[[6, 1, 'Table({T:%s}).M4' % m[sp], F], [6, 2, 'Sum(B7:B7)', F], [6, 4, 'Table({T:%s}).M5' % m[sp], F],
                     [6, 6, 'TEXT:---'], [6, 5, 'TEXT:---'],
                     [6, 3, 'Table({T:%s}).M%d' % (m[sp], side_row + 1), F] if side_row else [6, 3, 'TEXT:---'],
                     [6, 7, 'Table({T:%s}).Evaluate(%s)' % (m[sp], '+'.join('M%d' % (r_ + 1) for r_ in range(5, last + 1) if r_ != side_row)), F],
                     [6, 8, 'Sum(D7:H7)', F], [6, 9, 'I7+C7', F]])]
        return ops


def run(M, part, clone=True, geom=True, tables=True):
    s = Sheet(M, part)
    log = []
    if clone:
        out = gx.run(s.clone_ops(bool(part.get('spl'))), 'cl' + part['P'])
        log += [l for l in out.splitlines() if 'ERR' in l or 'done' in l][:6]
    if geom:
        s.elevation(); s.splices(); s.sections(); s.texts()
        out = gx.run(s.ops, 'rg' + part['P'])
        log += [l for l in out.splitlines() if 'ERR' in l or 'done' in l or 'no prop' in l or 'not found' in l][:25]
    if not part.get('tables', True):
        gx.run([dict(t='erase', h=[part['P'] + ':' + q for q in ['406488', '4064CF', '4064A2', '4064A3', '4064A6', '4064B8', '40648A', '40648B',
               '40648C', '40648D', '406493', '406499', '4064A4', '4064A7', '4064A8', '4064AA', '4064AB', '4064B0', '4064B9']])], 'nt' + part['P'])
    if tables and part.get('tables', True):
        out = gx.run(s.tables(), 'rt' + part['P'])
        log += [l[:160] for l in out.splitlines() if 'ERR' in l or 'done' in l][:10]
    return log
