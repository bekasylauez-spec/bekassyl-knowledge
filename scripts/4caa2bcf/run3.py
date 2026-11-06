# one rigel sheet from beams_auto.json:  python run3.py <mark> <part index>   (sheet slot = sheet number index)
import gx, sys, json, os, rgen, rfac, rfac2, rsec, rtab

A = json.load(open(gx.S + r'\beams_auto.json', encoding='utf-8'))
ORDER = sorted(A, key=lambda k: int(k.split('-')[1]))
SHEETS = [(mk, i) for mk in ORDER for i in range(len(A[mk]['parts']))]


def sheet_no(mark, pi): return SHEETS.index((mark, pi)) + 1


def run(mark, pi, log=print):
    B = dict(A[mark]); B['mark'] = mark
    part = dict(B['parts'][pi])
    n = sheet_no(mark, pi); part['no'] = '6.%d' % n
    k = n; SX = 172179.0 + 31500 * k; P = 'R%d:' % k
    # clear the slot and its staging area, import the analog sheet
    gx.run([{'t': 'eraseregion', 'win': [SX + 11, 455950, SX + 31489, 470780], 'mode': 'intersect'},
            {'t': 'eraseregion', 'win': [2599000 + 20000 * k, 250000, 2616000 + 20000 * k, 400000], 'mode': 'intersect'}], 'er')
    out = gx.run([dict(t='import', file=gx.S + r'\an\a61.dwg', h=rgen.sheet_handles(), base=list(rgen.AN0), to=[SX, rgen.FY], pre=P)], 'imp%d' % k)
    s = rgen.Sheet(SX, P)
    g = rfac.facade(s, B, part)
    u0, u1 = g['u0'], g['u1']; ut = (u0 + u1) / 2.0
    marks = []; secs = []
    for sc in B['secs']:
        on = [u for u in sc['at'] if u0 + 200 <= u <= u1 - 200]
        if not on: continue
        ok = [u for u in on if abs(u - ut) > 2300]
        if not ok:
            key = (tuple(map(tuple, sc['top'])), tuple(map(tuple, sc['bot'])))
            for u in on:
                for du in range(300, 4000, 200):
                    for v in (u + du, u - du):
                        if u0 + 300 < v < u1 - 300 and abs(v - ut) > 2300 and arr(B, v) == key and not in_col(B, v):
                            ok = [v]; break
                    if ok: break
                if ok: break
        marks.append(((ok or on)[0], sc['word'])); secs.append(sc)
    rfac2.facade2(s, B, part, marks)
    out = gx.run(s.ops, 'f%d' % k)
    errs = [l for l in out.splitlines() if 'ERR' in l]
    types = {h: r['t'] for h, r in rgen.INV.items()}
    nS = len(secs)
    keep_nodes = nS <= 2
    if keep_nodes: lo, hi = 9600, 22600
    else:
        lo, hi = 700, 22600
        gx.run([dict(t='eraseregion', win=[SX + 100, rgen.FY + 200, SX + 11300, rgen.FY + 9750], mode='inside')], 'en%d' % k)
    W = min((B['b'] + 1910) * rsec.SC + 200, (hi - lo) / float(max(nS, 1)))
    withML = W >= (B['b'] + 1910) * rsec.SC
    xc0 = SX + (lo + hi) / 2.0 - (nS - 1) * W / 2.0
    for i, sc in enumerate(secs):
        Pst = 'ST%d_%s:' % (k, sc['word'])
        OX, OY = 2600000 + 3000 * i + 20000 * k, 300000
        ops, tags, base = rsec.build_stage(B, sc, OX, OY, Pst, withML or i == 0)
        ty = {}
        for t_ in tags:
            h0 = t_.split(':', 1)[1]
            if h0 in types: ty[t_] = types[h0]
            elif h0.startswith('B'): ty[t_] = 'CIRCLE'
            elif h0.startswith('H'): ty[t_] = 'HATCH'
            elif h0.startswith('C'): ty[t_] = 'SPDSNOTECOMB'
            elif h0 == 'ML': ty[t_] = 'SPDSNOTEMULTILAYER'
            else: ty[t_] = ''
        out = gx.run(ops, 'st%d' % k); errs += [l for l in out.splitlines() if 'ERR' in l]
        s2 = rgen.Sheet(SX, P)
        rsec.place(s2, tags, base, [xc0 + W * i, rgen.FY + 5000], ty)
        out = gx.run(s2.ops, 'pl%d' % k); errs += [l for l in out.splitlines() if 'ERR' in l]
    s3 = rgen.Sheet(SX, P)
    ops = rtab.stamp_ops(s3, B, part['no'], 'Ригель ' + mark) + (rtab.static_fixes(s3) if keep_nodes else [])
    if not keep_nodes:
        ops.append(dict(t='settext', h=P + rgen.SPDS['notes'], s='\pxi-3.3333,l3.3333,t3.3333;1.	Общие указания см. л. - 1.1\P2.	Данный лист читать совместно с л. КЖ-2.1 ... 2.4'
                        '\P3.	Стержни, указанные в "Ведомости деталей", должны гнуться механическим способом в холодном состоянии с радиусом гиба 3d - 5d, где d - диаметр стержня'
                        '\P4.	Узел А, сечение а-а, узел стыковки со скобами и таблицу накладок см. л. 6.2', w=9200))
    if pi == 0:
        q = rtab.quantities(B, total_hoops(B))
        top, bot = rfac2.splices(B)
        ops += [o for o in rtab.table_ops(s3, B, q, len(top) + len(bot)) if isinstance(o, dict)]
        ops += rtab.detail_texts(s3, B, q)
        out = gx.run(ops, 'tb%d' % k); errs += [l for l in out.splitlines() if 'ERR' in l]
        m = gx.tagmap(); rH = 6 + len(rtab.grouped(B))
        out = gx.run(rtab.steel_ops(P + rgen.SPDS['steel'], m[P + rgen.SPDS['spec']], rH, B) +
                     [dict(t='theight', h=P + rgen.SPDS['spec'], rows=[[rH + 1, 400], [rH + 3, 400]])], 'stl%d' % k)
        errs += [l for l in out.splitlines() if 'ERR' in l]
        if len(rtab.grouped(B)) > 2:
            # spec taller than the analog: notes go to the free bottom-left corner (or above the steel table title)
            if not keep_nodes:
                out = gx.run([dict(t='moveto', h=P + rgen.SPDS['notes'], to=[SX + 800, rgen.FY + 2900])], 'nt%d' % k)
            errs += [l for l in out.splitlines() if 'ERR' in l]
    else:
        # continuation sheet: tables and ведомость деталей are on the first sheet of the mark
        ops += [dict(t='erase', h=[P + rgen.SPDS['spec'], P + rgen.SPDS['steel']]),
                dict(t='eraseregion', win=[SX + 27700, 466300, SX + 31480, 470700], mode='inside')]
        ops.append(dict(t='settext', h=P + rgen.SPDS['notes'], s='\\pxi-3.3333,l3.3333,t3.3333;1.\tОбщие указания см. л. - 1.1\\P2.\tДанный лист читать совместно с л. КЖ-2.1 ... 2.4'
                        '\\P3.\tСпецификацию и ведомость деталей ригеля %s см. л. %s' % (mark, '6.%d' % sheet_no(mark, 0)), w=9200))
        out = gx.run(ops, 'tb%d' % k); errs += [l for l in out.splitlines() if 'ERR' in l]
    allout = gx.log()
    if any('eAtMaxReaders' in e for e in errs): raise RuntimeError('eAtMaxReaders - not saved')
    out = gx.run([dict(t='save')], 'sv')
    if 'ERR' in out: raise RuntimeError('save failed ' + out[-200:])
    log('%s part %d -> %s slot %d  errors %d %s' % (mark, pi, part['no'], k, len(errs), errs[:5]))
    return k


def arr(B, u):
    t = [x for x in B['dop'] if x['top'] and x['u0'] <= u <= x['u1']]
    b = [x for x in B['dop'] if not x['top'] and x['u0'] <= u <= x['u1']]
    return (tuple((x['pos'], x['n'], x['d'], x['row']) for x in t), tuple((x['pos'], x['n'], x['d'], x['row']) for x in b))


def in_col(B, u):
    return any(sp['a'] - 200 <= u <= sp['b'] + 200 for sp in B['sup'])


def total_hoops(B):
    s = rgen.Sheet(0, 'Q:')
    rfac.facade(s, B, dict(i0=0, i1=len(B['sup']) - 1, brkL=False, brkR=False))
    return s.NH


if __name__ == '__main__':
    mark = sys.argv[1]
    for pi in ([int(sys.argv[2])] if len(sys.argv) > 2 else range(len(A[mark]['parts']))):
        run(mark, pi)
