# БДМ Блок 2 — rigel sheet generator from the analog «Ресторан 6.1 Ригель» (A4x3, 1:50).
# Ported from ЖК Галакси rigx.py/sec1.py (same analog handles, same sheet coordinate system:
# sheet frame = (SX, 455939), analog sheet 6.1 frame (-232572, 411799) maps onto it).
# Everything is a copy of an analog object (import with prefix P, then edited by handle tag P+<analog handle>).
import gx, json, os, math

AN0 = (-232572.0, 411799.0)
SHIFT = 3000000.0                       # parked analog copy (tags A:<h>) sits at analog + (3e6, 0)
INV = json.load(open(gx.S + r'\an\inv.json', encoding='utf-8'))
FY = 455939.0

SPDS = dict(ax=['401290', '401291', '401295', '401299', '40129D', '4012A1'],
            brk=['40159D', '40159E', '4018B8', '4018B9', '4018BB', '4018BC', '4018BE', '4018BF', '4018C1', '4018C2', '4018C4', '4018C5'],
            comb=['4038F4', '403949', '4039A1'], n1=['4015B1', '40671E', '40671F', '406720'],
            sk=['4015C2', '4069C0'], step='414D1E', sec=['4015C0', '4274AC', '4015BF', '40F7E4', '40F7E5', '4274AD', '40F7E6'],
            ml='42C86E', lm='4015A3', spec='406488', steel='4064CF', notes='40443D', no='404440', name='404442', title='4038B1')
COLS = ['40159B', '4018B7', '4018BA', '4018BD', '4018C0', '4018C3']
OUTL = ['40159C', '402404', '403897', '403898', '403899']
AXD = ['401296', '40129A', '40129E', '4012A2', '4012A5']
HL = ['4015B6', '40389F', '4038A0', '4038A1', '4038A2', '4038A3', '4038A4', '4038A5', '4038A6', '4038A7', '4038A8', '4038A9',
      '4038AA', '4038AB', '4038AC', '4038AD', '4038AE', '4038AF', '4038B0']
ZD = ['4033EB', '4033C1', '403439', '403749', '40371D', '403733', '403816', '403810', '403813', '403843', '40383D', '403840',
      '403870', '40386A', '40386D']
ED = ['40347E', '403446', '403605', '40364D', '40364E', '403681', '403682', '4036B5', '4036B6', '4036E9']
PLATES = ['4038F3', '4038F2', '403948', '403947', '4039A0', '40399F']
SPLD = ['4038F1', '4038F5', '403992', '40394A', '4039A5', '4039A2']
POS2 = dict(bar=['4274A8', '4274AA'], note=['4274A9', '4274AB'])
# analog section 1-1 (1:20 frame)
SEC = dict(outl='40444A', bot=['40444B', '404886', '40488D', '40445E'], top=['404468', '40490C', '404913', '40446F'],
           hoop=['404492', '40600F'], dimb=['404452', '40498B', '4049B4', '40499A', '404465'], dimw='4044EF',
           dimv=['404455', '404458', '40445B'], dimh='4044EE', brk=['4044B3', '4044B2'], ml='42C86F', lev='4044D9',
           title='4044B4', ctop='4044EA', cbot='4044EB', cx1='406008')
SEC_HS = [h for v in SEC.values() for h in (v if isinstance(v, list) else [v])]


def sheet_handles():
    """analog handles inside sheet 6.1 frame (plus the «Узел стыковки» title)"""
    x0, y0, x1, y1 = AN0[0], AN0[1], -201072.0, 426649.0
    hs = []
    for h, r in INV.items():
        e = r['e']
        if e[0] >= x0 - 5 and e[2] <= x1 + 5 and e[1] >= y0 - 5 and e[3] <= y1 + 5: hs.append(h)
    return hs


def sec_handles():
    return [h for h in SEC_HS if h in INV]


class Sheet:
    def __init__(s, SX, P):
        s.SX, s.P = SX, P
        s.D = SX - 172179.0
        s.ops = []

    def A(s, h): return s.P + h
    def add(self_, **k): self_.ops.append(k)


def zones2(fL, fR, sEnd, sMid):
    """hoops face+50 .. face-50 : sEnd x n1 | sMid x n2 (+r) | sEnd x n3 ; returns segs, boundary lines, count"""
    h0, h4 = fL + 50, fR - 50
    Lp = h4 - h0
    if sEnd == sMid or Lp < 4 * sEnd * 2:
        n = int(round(Lp / sEnd)); r = Lp - n * sEnd
        segs = [(h0, h4, '%dх%d' % (sEnd, n) if abs(r) < 0.5 else '')]
        if abs(r) >= 0.5:      # not divisible: n*s + r
            n = int(Lp // sEnd); r = Lp - n * sEnd
            segs = [(h0, h0 + sEnd * n, '%dх%d' % (sEnd, n)), (h0 + sEnd * n, h4, '%d' % round(r))]
            return segs, [h0, h0 + sEnd * n, h4], n + 2
        return segs, [h0, h4], n + 1
    n1 = int(round(Lp / 4.0 / sEnd)); n3 = n1
    rest = Lp - sEnd * (n1 + n3)
    n2 = int(rest // sMid); r = rest - sMid * n2
    if abs(r) < 0.5: r = 0
    elif abs(r - sEnd) < 0.5: n3 += 1; r = 0
    segs = []; x = h0
    segs.append((x, x + sEnd * n1, '%dх%d' % (sEnd, n1))); x += sEnd * n1
    segs.append((x, x + sMid * n2, '%dх%d' % (sMid, n2))); x += sMid * n2
    if r: segs.append((x, x + r, '%d' % round(r))); x += r
    segs.append((x, x + sEnd * n3, '%dх%d' % (sEnd, n3))); x += sEnd * n3
    assert abs(x - h4) < 0.5
    lines = [h0, h0 + sEnd * n1, h0 + sEnd * n1 + sMid * n2 + r, h4]
    return segs, lines, n1 + n2 + n3 + 1 + (1 if r else 0)


def pool(lst, s, tagbase):
    """take analog handles from a list; when exhausted clone the first one"""
    q = list(lst); used = []; n = [0]
    def take():
        if q:
            h = s.A(q.pop(0)); used.append(h); return h
        n[0] += 1
        tg = '%s%s_X%d' % (s.P, tagbase, n[0])
        s.add(t='clone', h=s.A(lst[0]), base=[0, 0], to=[0, 0], tag=tg)
        return tg
    def rest(): return [s.A(h) for h in q]
    return take, rest
