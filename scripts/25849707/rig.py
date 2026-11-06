# БДМ Блок 1 — rigel sheet from the analog «Ресторан 6.1 Ригель Рм-1» (A4x3, 1:50).
# Every object is an analog object moved/stretched (plset, dimpts, spmove ...) or a clone of one (pools).
# Coordinates: analog absolute (sheet 6.1 frame min AN0) + sheet offset (dx, dy).
import json, math
import gx
from an61 import AN0, SRC, SHEET, SECS

# ---- analog anchors (absolute analog coordinates) ----
XL0 = -229569.0            # outer face of the left column (analog col 1)
XR0 = -208169.0            # outer face of the right column (analog col 6)
YT = 424560.0              # beam top
YB0 = 424160.0             # analog beam bottom (h 400)
COLS = ['40159B', '4018B7', '4018BA', '4018BD', '4018C0', '4018C3']
BRK = ['40159D', '40159E', '4018B8', '4018B9', '4018BB', '4018BC', '4018BE', '4018BF', '4018C1', '4018C2', '4018C4', '4018C5']
AXS = ['401290', '401291', '401295', '401299', '40129D', '4012A1']
SPANR = ['40159C', '402404', '403897', '403898', '403899']
HL = ['4015B6', '40389F', '4038A0', '4038A1', '4038A2', '4038A3', '4038A4', '4038A5', '4038A6', '4038A7', '4038A8', '4038A9',
      '4038AA', '4038AB', '4038AC', '4038AD', '4038AE', '4038AF', '4038B0']
ZD = ['4033EB', '4033C1', '403439', '403749', '40371D', '403733', '403816', '403810', '403813', '403843', '40383D', '403840',
      '403870', '40386A', '40386D']
ED = ['40347E', '403446', '403605', '40364D', '40364E', '403681', '403682', '4036B5', '4036B6', '4036E9']
CH = ['401296', '40129A', '40129E', '4012A2', '4012A5']
TOT = '401292'
N1 = ['4015B1', '40671E', '40671F', '406720']
POS2 = ['4274A9', '4274AB']
DOPBAR = ['4274A8', '4274AA']
SK = ['4015C2', '4069C0']
SKPL = ['4015C1', '4069BF']
STEP = '414D1E'
SEC = ['4015BF', '40F7E4', '40F7E6', '4015C0', '40F7E5', '4274AC', '4274AD']
COMB = ['4038F4', '403949', '4039A1']
PLATES = ['4038F3', '4038F2', '403948', '403947', '4039A0', '40399F']
SPLD = ['4038F1', '4038F5', '403992', '40394A', '4039A5', '4039A2']
ML, LM, TITLE = '42C86E', '4015A3', '4038B1'
HD = dict(h='4015A4', bot='4015AD', hin='401933', top='4015A9')
NSD = {20: 'Н1', 22: 'Н2', 25: 'Н3', 28: 'Н4', 32: 'Н5'}


def zones(fL, fR):
    """hoops from face+50 to face-50: 100xN1 | 200xN2 (+ odd r) | 100xN3 (Galaxy rg.zones)"""
    h0, h4 = fL + 50, fR - 50
    Lp = h4 - h0
    if Lp < 2500:
        n = int(Lp // 100); r = Lp - 100 * n
        segs = [(h0, h0 + 100 * n, '100х%d' % n)] + ([(h0 + 100 * n, h4, '%d' % round(r))] if r else [])
        return segs, ([h0, h0 + 100 * n, h4] if r else [h0, h4]), n + 1 + (1 if r else 0)
    n1 = int(round(Lp / 4 / 100.0)); n3 = n1
    rest = Lp - 100 * (n1 + n3)
    n2 = int(rest // 200); r = rest - 200 * n2
    if abs(r) < 0.5: r = 0
    elif abs(r - 100) < 0.5: n3 += 1; r = 0
    segs = []; x = h0
    segs.append((x, x + 100 * n1, '100х%d' % n1)); x += 100 * n1
    segs.append((x, x + 200 * n2, '200х%d' % n2)); x += 200 * n2
    if r: segs.append((x, x + r, '%d' % round(r))); x += r
    segs.append((x, x + 100 * n3, '100х%d' % n3)); x += 100 * n3
    lines = [h0, h0 + 100 * n1, h0 + 100 * n1 + 200 * n2 + r, h4]
    count = n1 + n2 + n3 + 1 + (1 if r else 0)
    return segs, lines, count


class Sheet:
    def __init__(self, P, SX, SY):
        self.P = P; self.dx = SX - AN0[0]; self.dy = SY - AN0[1]
        self.ops = []; self.k = 0
    def A(self, h): return self.P + h
    def x(self, ax): return ax + self.dx
    def y(self, ay): return ay + self.dy
    def add(self, **k): self.ops.append(k)
    def tag(self, s):
        self.k += 1; return '%s_%s%d' % (self.P.rstrip(':'), s, self.k)
    def clone(self, h, s):
        t = self.tag(s); self.add(t='clone', h=h, tag=t); return t
    def pool(self, hs): return [self.A(h) for h in hs]
    def take(self, pool, proto, s):
        return pool.pop(0) if pool else self.clone(self.A(proto), s)


def build(S, F):
    """F: fragment dict (beam-local u along the rigel, mm):
       u0,u1 fragment extents (outer faces / cut points), sup=[(f0,f1,kind,axlab or None,uaxis)],
       h,b, endL/endR in ('end','cut'), top/bot (n,d,pos), dop=[dict(pos,top,u0,u1,k,d)], hoop=dict(d,pos),
       spl=dict(top=[c...], bot=[c...]) splice group centres, d (main Ø), level '+7.000', mark, secs=[(word,u)]"""
    h = F['h']; dH = h - 400.0
    YB = YT - h
    YTB, YBB = YT - 30, YB + 50
    X = lambda u: S.x(XL0 + (u - F['u0']))
    Y = lambda ay: S.y(ay)
    cmp_ = 250.0 if h >= 1000 else 0.0              # deep beams: lower rows a bit closer (room for the 1:20 sections)
    YL = lambda ay: S.y(ay - dH + cmp_)            # analog objects below the beam: shifted down by dH
    A = S.A; add = S.add
    sup = F['sup']
    # ---- supports: columns (rect + breaks) or supporting beams (rect, no breaks)
    cp = S.pool(COLS); bp = S.pool(BRK)
    for (f0, f1, kind, lab, ua) in sup:
        hc = S.take(cp, COLS[0], 'COL')
        if kind == 'col':
            yt, yb = YT + 97, YB - 180
        else:
            yt, yb = YT, YT - F.get('hsup', 900)
        add(t='plset', h=hc, p=[[X(f0), Y(yt)], [X(f1), Y(yt)], [X(f1), Y(yb)], [X(f0), Y(yb)]], closed=True)
        if kind == 'col':
            for yy in (yt - 47.4, yb + 50.4):
                hb = S.take(bp, BRK[0], 'BRK')
                add(t='mcset', h=hb, set={'StartPoint': [X(f0) - 30, Y(yy)], 'EndPoint': [X(f1) + 30, Y(yy)],
                                          'ClipZonePoint': [X(f1) + 30, Y(yy)], 'Length': f1 - f0 + 60})
    for side in ('L', 'R'):
        if F['end' + side] != 'cut': continue
        xb = X(F['u0'] + 150) if side == 'L' else X(F['u1'] - 150)
        hb = S.take(bp, BRK[0], 'BRK')
        add(t='mcset', h=hb, set={'StartPoint': [xb, Y(YB) - 120], 'EndPoint': [xb, Y(YT) + 120], 'ClipZonePoint': [xb, Y(YT) + 120], 'Length': h + 240})
    add(t='erase', h=cp + bp)
    # ---- axes (SPDS construction lines with bubble)
    ap = S.pool(AXS)
    axes = [(ua, lab) for (f0, f1, kind, lab, ua) in sup if lab]
    for ua, lab in axes:
        add(t='axis', h=S.take(ap, AXS[0], 'AX'), s=[X(ua), Y(YT)], e=[X(ua), YL(422221 + 150 - 150)], val=lab)
    add(t='erase', h=ap)
    # ---- beam outline per span (between support faces / cut ends)
    faces = [F['u0']] + [c for s in sup for c in s[:2]] + [F['u1']]
    spans = [(faces[i], faces[i + 1]) for i in range(0, len(faces), 2) if faces[i + 1] - faces[i] > 1]
    rp = S.pool(SPANR)
    for (a, b) in spans:
        add(t='plset', h=S.take(rp, SPANR[0], 'SP'), p=[[X(b), Y(YB)], [X(b), Y(YT)], [X(a), Y(YT)], [X(a), Y(YB)]], closed=True)
    add(t='erase', h=rp)
    # ---- main bars + Ск at real ends
    e0 = X(F['u0']) + (20 if F['endL'] == 'end' else 0)
    e1 = X(F['u1']) - (20 if F['endR'] == 'end' else 0)
    lay = 'диам%d' % F['top']['d']
    add(t='plset', h=A('4015A8'), p=[[e0, Y(YTB)], [e1, Y(YTB)]], layer='диам%d' % F['top']['d'])
    add(t='plset', h=A('4015AE'), p=[[e0, Y(YBB)], [e1, Y(YBB)]], layer='диам%d' % F['bot']['d'])
    L = 10 * F['sk']['d'] + 90          # leg (analog Ск1 Ø16: 250)
    yk = (Y(YBB) + 20 + Y(YTB) - 20) / 2
    for side, hp, hn, e in (('L', SKPL[0], SK[0], e0), ('R', SKPL[1], SK[1], e1)):
        end = F['endL'] if side == 'L' else F['endR']
        if end != 'end':
            add(t='erase', h=[A(hp), A(hn)]); continue
        s = 1 if side == 'L' else -1
        add(t='plset', h=A(hp), p=[[e + s * L, Y(YBB) + 20], [e + s * 25, Y(YBB) + 20], [e, Y(YBB) + 45], [e, Y(YTB) - 45], [e + s * 25, Y(YTB) - 20], [e + s * L, Y(YTB) - 20]])
        if side == 'R':
            add(t='move', h=[A(hn)], d=[e - S.x(XR0), 0])
        add(t='spmove', h=A(hn), items=[[1, e, yk]])
        add(t='mcset', h=A(hn), set={'FirstLine': F['sk']['pos'], 'SecondLine': '(ф%d)' % F['sk']['d']})
    # ---- доп bars (analog pos 2 Ø12 bars + notes as prototypes)
    barp, notep = S.pool(DOPBAR), S.pool(POS2)
    for d in F['dop']:
        y = Y(YTB) - 50 if d['top'] else Y(YBB) + 50
        hb = S.take(barp, DOPBAR[0], 'DB')
        add(t='plset', h=hb, p=[[X(d['u0']), y], [X(d['u1']), y]], layer='диам%d' % d['d'])
        hn = S.take(notep, POS2[0], 'DN')
        xn = X(d['nx'])
        add(t='spmove', h=hn, items=[[0, xn, Y(YT + 538.6)], [1, xn, y]])
        add(t='mcset', h=hn, set={'FirstLine': d['pos'], 'SecondLine': '(ф%d)' % d['d']})
    add(t='erase', h=barp + notep)
    # ---- hoop zones: boundary lines + chain (zone dims row, edge dims from the axes)
    hl, zd, ed = S.pool(HL), S.pool(ZD), S.pool(ED)
    NH = 0
    supc = [(s[0], s[1], s[4]) for s in sup]
    zy = YL(YB0 - 818)
    for i, (a, b) in enumerate(spans):
        if (F['endL'] == 'cut' and abs(a - F['u0']) < 1) or (F['endR'] == 'cut' and abs(b - F['u1']) < 1): continue
        segs, lines, cnt = zones(a, b); NH += cnt
        for xx in lines:
            add(t='plset', h=S.take(hl, HL[0], 'HL'), p=[[X(xx), Y(YBB)], [X(xx), Y(YTB)]], layer='диам%d' % F['hoop']['d'])
        for s0, s1, txt in segs:
            hz = S.take(zd, ZD[0], 'ZD')
            add(t='dimpts', h=hz, p1=[X(s0), Y(YB), 0], p2=[X(s1), Y(YB), 0], dl=[X(s1), zy, 0])
            add(t='dimtext', h=hz, s=txt if 'х' in txt else '')
        # edge dims axis -> first/last hoop (only where an axis exists at that face)
        left = [s for s in supc if abs(s[1] - a) < 1]
        right = [s for s in supc if abs(s[0] - b) < 1]
        for k, (lst, q) in enumerate(((left, lines[0]), (right, lines[-1]))):
            if not lst: continue
            p = lst[0][2]
            he = S.take(ed, ED[0], 'ED')
            add(t='dimpts', h=he, p1=[X(q), Y(YB), 0], p2=[X(p), Y(YB), 0], dl=[X(p), zy, 0])
            add(t='dimtx', h=he, at=[X(lines[0]) + 34 + 0 if k == 0 else X(p) - 19, YL(422956 if k == 0 else 422840), 0])
    add(t='erase', h=hl + zd + ed)
    # ---- axis chain + total
    cp2 = S.pool(CH)
    axu = sorted(set([s[4] for s in sup]))          # every support: its axis, or its centre when it is not on an axis
    for p, q in zip(axu, axu[1:]):
        add(t='dimpts', h=S.take(cp2, CH[0], 'CH'), p1=[X(p), YL(422221), 0], p2=[X(q), YL(422221), 0], dl=[X(q), YL(422633), 0])
    add(t='erase', h=cp2)
    if len(axu) > 2:
        add(t='dimpts', h=A(TOT), p1=[X(axu[0]), YL(422221), 0], p2=[X(axu[-1]), YL(422221), 0], dl=[X(axu[-1]), YL(422271), 0])
    else:
        add(t='erase', h=[A(TOT)])
    # ---- height dims at the left end
    xe = X(F['u0'])
    add(t='dimpts', h=A(HD['h']), p1=[xe, Y(YT), 0], p2=[xe, Y(YB), 0], dl=[S.x(-230541), Y(YB), 0])
    add(t='dimpts', h=A(HD['bot']), p1=[xe, Y(YB), 0], p2=[xe + 20, Y(YBB), 0], dl=[S.x(-230006), Y(YBB), 0])
    add(t='dimpts', h=A(HD['hin']), p1=[xe + 20, Y(YBB), 0], p2=[xe + 20, Y(YTB), 0], dl=[S.x(-230006), Y(YTB), 0])
    add(t='dimpts', h=A(HD['top']), p1=[xe + 20, Y(YTB), 0], p2=[xe, Y(YT), 0], dl=[S.x(-230006), Y(YT), 0])
    # ---- splices: plates (pairs 500 apart) + dims from the axis + combs
    plp, sdp, cbp = S.pool(PLATES), S.pool(SPLD), S.pool(COMB)
    for top, cs in (('top', F['spl'].get('top', [])), ('bot', F['spl'].get('bot', []))):
        for c, ua in cs:
            yb_ = Y(YTB) if top == 'top' else Y(YBB)
            for xc in (c - 250, c + 250):
                hp = S.take(plp, PLATES[0], 'PL')
                add(t='plset', h=hp, p=[[X(xc) - 125, yb_ - 15], [X(xc) - 125, yb_ + 15], [X(xc) + 125, yb_ + 15], [X(xc) + 125, yb_ - 15]], closed=True)
            yref = Y(YT) if top == 'top' else Y(YB)
            ydl = Y(YT + 999) if top == 'top' else YL(423650)
            h1 = S.take(sdp, SPLD[0], 'SD'); h2 = S.take(sdp, SPLD[1], 'SD')
            add(t='dimpts', h=h1, p1=[X(c - 250), yb_, 0], p2=[X(ua), yref, 0], dl=[X(ua), ydl, 0])
            add(t='dimpts', h=h2, p1=[X(c + 250), yb_, 0], p2=[X(c - 250), yb_, 0], dl=[X(c - 250), ydl, 0])
            hc = S.take(cbp, COMB[0], 'CB')
            # comb: two leaders to the plates; text = Н-mark
            ysh = Y(YT + 450) if top == 'top' else Y(YT + 450)
            add(t='combsegs', h=hc, segs=[[[X(c - 250), yb_ + 15], [X(c - 250) - 300, ysh]], [[X(c + 250), yb_ + 15], [X(c - 250) - 300, ysh]]],
                start=[X(c - 250) - 300, ysh], end=[X(c - 250) - 900, ysh])
            add(t='mcset', h=hc, set={'FirstLine': NSD[F['top']['d'] if top == 'top' else F['bot']['d']]})
    add(t='erase', h=plp + sdp + cbp)
    # ---- callouts of the main bars «1 (фd)» (one per span, in the 200-zone)
    n1 = S.pool(N1)
    for (a, b) in spans:
        if b - a < 2500 or (F['endL'] == 'cut' and abs(a - F['u0']) < 1) or (F['endR'] == 'cut' and abs(b - F['u1']) < 1): continue
        segs, lines, cnt = zones(a, b)
        bad = [(c - 1500, c + 500) for c, ua in F['spl'].get('top', [])] + [(d['nx'] - 900, d['nx'] + 900) for d in F['dop']]
        bad += [(u - 500, u + 500) for w, u in F['secs']]
        cand = [lines[1] + 300, lines[2] - 300, (lines[1] + lines[2]) / 2.0, lines[1] + 800, lines[2] - 800] + [a + (b - a) * t for t in (0.2, 0.3, 0.4, 0.6, 0.7, 0.8)]
        dist = lambda u: min([0 if p <= u <= q else min(abs(u - p), abs(u - q)) for p, q in bad] + [1e9])
        best = max(cand, key=dist)
        if dist(best) < 300: continue          # no free place: the main bars are labelled in the other spans
        xx = X(best)
        hn = S.take(n1, N1[0], 'N1')
        add(t='spmove', h=hn, items=[[0, xx, Y(YT + 538.6)], [1, xx, Y(YBB)], [2, xx, Y(YTB)]])
        add(t='mcset', h=hn, set={'FirstLine': F['top']['pos'], 'SecondLine': '(ф%d)' % F['top']['d']})
    add(t='erase', h=n1)
    # ---- step note at the right end
    add(t='move', h=[A(STEP)], d=[X(F['u1']) - S.x(XR0), -dH])
    add(t='mcset', h=A(STEP), set={'FirstLine': 'Шаг хомута', 'SecondLine': '%s(ф%d)' % (F['hoop']['pos'], F['hoop']['d'])})
    # ---- section marks
    sp = S.pool(SEC)
    for (w, u) in F['secs']:
        hs = S.take(sp, SEC[0], 'SEC')
        add(t='sp_set', h=hs, pts=[[0, X(u), Y(425653.5)], [1, X(u), YL(421693.7 + 150)]])
        add(t='mcset', h=hs, set={'Word': w})
    add(t='erase', h=sp)
    # ---- level mark + title
    add(t='erase', h=[A(ML)])
    levels = F.get('levels') or [F['level']]
    add(t='levelval', h=A(LM), old='-0.100', value=levels[0], tag=A(LM))
    if len(levels) > 1:       # upper level: one-line multilayer note of the analog sheet 6.6 stacked above the level mark
        add(t='move', h=[A('42FC64')], d=[-157484.0, 257.0])
        add(t='levelval', h=A('42FC64'), old='+4.395', value=levels[1], tag=A('42FC64'))
    else:
        add(t='erase', h=[A('42FC64')])
    add(t='settext', h=A(TITLE), s='Ригель ' + F['mark'])
    return NH, spans
