# Tables (spec, steel), Ведомость деталей texts, notes, stamp of a rigel sheet — analog objects edited in place
import math, gx

SPEC, STEEL = '406488', '4064CF'
F2, F0 = '%lu2%pr2', '%lu2%pr0'
STAMP_OLD, NO_OLD, NAME_OLD = '40443F', '404440', '404442'
SCH_STAMP, SCH_NAME, SCH_NO = '5B508C', '5B508D', '5B508F'          # scheme sheet 2.4 stamp block + its name / number texts
SCH_STAMP_PT = (469717.3304096889, -1787684.128777295)
AN_STAMP_PT = (-201322.0, 411886.0)


def hoop_dims(F):
    """hoop over 3 bars (Galaxy rule): bottom w, top w+100 (hook), legs g, g+100"""
    from rigsec import barx
    bx = barx(F['b'], F['top']['n'])
    w = (bx[2] - bx[0]) + F['top']['d'] + F['hoop']['d']
    g = (F['h'] - 100) + F['top']['d'] + F['hoop']['d']
    w = int(math.ceil(w / 10.0) * 10); g = int(math.ceil(g / 10.0) * 10)
    return w, g, 2 * w + 2 * g + 200


def positions(F, NH, nmarks_len):
    """spec positions of one rigel: list of dict(pos, star, d, cls, L (mm) or None (пог.м.), q)"""
    n = F['top']['n']
    w, g, Lh = hoop_dims(F)
    hp = 1 if n == 3 else 2
    P = [dict(pos=F['hoop']['pos'], star=True, d=F['hoop']['d'], cls='240', L=Lh, q=NH * hp)]
    nends = sum(1 for e in (F['endL'], F['endR']) if e == 'end')
    leg = 10 * F['sk']['d'] + 90; web = F['h'] - 80
    if nends: P.append(dict(pos=F['sk']['pos'], star=True, d=F['sk']['d'], cls='500С', L=2 * leg + web, q=nends * n))
    Lm = nmarks_len / 1000.0
    if F['top']['d'] == F['bot']['d']:
        P.append(dict(pos=F['top']['pos'], star=False, d=F['top']['d'], cls='500С', L=None, q=round(Lm * 2 * n, 2)))
    else:
        P.append(dict(pos=F['top']['pos'], star=False, d=F['top']['d'], cls='500С', L=None, q=round(Lm * n, 2)))
        P.append(dict(pos=F['bot']['pos'], star=False, d=F['bot']['d'], cls='500С', L=None, q=round(Lm * n, 2)))
    for d in F.get('dopspec', []):
        P.append(dict(pos=d['pos'], star=False, d=d['d'], cls='500С', L=d['L'], q=d['q']))
    for d, q in sorted(F.get('nspec', {}).items()):
        P.append(dict(pos='Н%d' % {20: 1, 22: 2, 25: 3, 28: 4, 32: 5}[d], star=False, d=d, cls='500С', L=10 * d, q=q))
    return P, (w, g, Lh, leg, web)


def ops(S, F, P, conc, title, tm):
    """tm = tag map (gx.tagmap()) for table handles"""
    A = S.A; o = []
    sp, st = A(SPEC), A(STEEL)
    extra = max(0, len(P) - 5)
    if extra: o.append(dict(t='trows', h=sp, mode='ins', at=8, n=extra, **{'from': 7}))
    texts, nums, forms = [[2, 2, title]], [], []
    last = 3 + len(P) - 1
    for i, p in enumerate(P):
        r = 3 + i; R = r + 1
        texts += [[r, 0, p['pos'] + ('*' if p['star'] else '')], [r, 1, 'ГОСТ 34028-2016'], [r, 2, '%%C'], [r, 4, 'A'], [r, 5, p['cls']], [r, 8, 'L=']]
        nums += [[r, 3, p['d'], F0]]
        if p['L'] is None:
            texts.append([r, 9, 'пог.м.'])
            nums.append([r, 10, p['q'], F2])
            forms.append([r, 11, 'D%d*D%d*3.1415926/4*0.00785*1' % (R, R), F2])
        else:
            nums += [[r, 9, p['L'], F0], [r, 10, p['q'], F0]]
            forms.append([r, 11, 'D%d*D%d*3.1415926/4*0.00785*J%d/1000' % (R, R, R), F2])
        forms.append([r, 12, 'L%d*K%d' % (R, R), F2])
    for r in range(3 + len(P), 8 + extra):            # blank remaining rows
        texts += [[r, c, ''] for c in range(13)]
    forms = [[2, 12, 'Sum(M4:M%d)' % (last + 1), F2]] + forms
    o += [dict(t='tset', h=sp, cells=texts), dict(t='tnum', h=sp, cells=nums + [[9 + extra, 12, conc, F2]]), dict(t='tformula', h=sp, cells=forms)]
    # steel table: A240 column = hoops, A500 columns by Ø
    used = sorted(set(p['d'] for p in P if p['cls'] != '240'))
    hdr = list(used)
    for d in (12, 16, 20, 25, 28, 22, 32, 14, 10):
        if len(hdr) >= 5: break
        if d not in hdr: hdr.append(d)
    hdr = sorted(hdr[:5])
    ref = lambda R: 'Table({T:%s}).M%d' % (tm[sp], R)
    sf = [[6, 1, ref(4), F2], [6, 2, 'Sum(B7:B7)', F2]]
    for k, d in enumerate(hdr):
        rows = [3 + i + 1 for i, p in enumerate(P) if p['cls'] != '240' and p['d'] == d]
        sf.append([6, 3 + k, '+'.join(ref(R) for R in rows), F2] if rows else [6, 3 + k, 'TEXT:---'])
    sf += [[6, 8, 'Sum(D7:H7)', F2], [6, 9, 'I7+C7', F2]]
    o += [dict(t='tset', h=st, cells=[[5, 1, '%%C' + str(F['hoop']['d'])]] + [[5, 3 + k, '%%C%d' % d] for k, d in enumerate(hdr)] + [[6, 0, title]]),
          dict(t='tformula', h=st, cells=sf)]
    return o


def texts(S, F, geo, no, mark):
    w, g, Lh, leg, web = geo
    A = S.A; o = []
    T = {'406493': str(w + 100), '40648A': str(w), '40648B': str(g), '40648D': str(g + 100), '406499': str(Lh),
         '4064A7': str(web), '4064A8': str(leg), '4064AB': str(leg), '4064B0': str(2 * leg + web)}
    o += [dict(t='settext', h=A(k), s=v) for k, v in T.items()]
    o.append(dict(t='settext', h=A('40443D'), s='\\pxi-3.3333,l3.3333,t3.3333;1.\tОбщие указания см. л. - 1.1\\P2.\tДанный лист читать '
                  'совместно с л. КЖ-2.1 ... 2.4\\P3.\tСтержни, указанные в "Ведомости деталей", должны гнуться механическим способом '
                  'в холодном состоянии с радиусом гиба 3d - 5d, где d - диаметр стержня'))
    # stamp: project stamp Штамп№1 (scheme sheets) instead of the foreign analog stamp block
    base = list(SCH_STAMP_PT); to = [AN_STAMP_PT[0] + S.dx, AN_STAMP_PT[1] + S.dy]
    t1, t2, t3 = S.tag('STP'), S.tag('STN'), S.tag('STNO')
    o += [dict(t='erase', h=[A(STAMP_OLD), A(NO_OLD), A(NAME_OLD)]),
          dict(t='clone', h=SCH_STAMP, base=base, to=to, s=0.5, tag=t1),
          dict(t='clone', h=SCH_NAME, base=base, to=to, s=0.5, tag=t2, text='\\pxsm1,qc;{\\T0.95;Ригель %s}' % mark),
          dict(t='clone', h=SCH_NO, base=base, to=to, s=0.5, tag=t3, text=no)]
    return o
