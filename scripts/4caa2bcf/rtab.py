# spec / steel tables, ведомость деталей, stamp and notes of a rigel sheet (analog tables keep formulas)
from rgen import *

F2, F0 = '%lu2%pr2', '%lu2%pr0'


def quantities(B, NH):
    h = B['h']; dm = B['main']['top'][1]; dh = B['hoop']['d']
    nm = B['main']['top'][0]
    hw = round((B['b'] - 110) / (3.0 if nm == 4 else 1.0) * (2 if nm == 4 else 1) + dm + dh, -1)   # hoop over 3 bars, wire axis
    hh = round(h - 110 + dm + dh, -1)
    hook = 10 * dh
    xl = dict(bot=hw, top=hw + hook, hl=hh, hr=hh + hook)
    xl['L'] = xl['bot'] + xl['top'] + xl['hl'] + xl['hr']
    sk_v = h - 110; sk = dict(v=sk_v, l=250, L=250 + sk_v + 250)
    ends = 2
    Lm = (B['END1'] - B['END0'] - 40) / 1000.0
    cols = [sp for sp in B['sup'] if sp['kind'] in ('col', 'beam')]
    clear = (B['END1'] - B['END0']) - sum(sp['b'] - sp['a'] for sp in cols if B['END0'] <= sp['a'] and sp['b'] <= B['END1'])
    conc = B['b'] / 1000.0 * (h - B.get('slab', 0)) / 1000.0 * clear / 1000.0
    return dict(xl=xl, sk=sk, nsk=nm * ends, Lm=Lm, nH=NH * (2 if nm == 4 else 1), conc=conc, nm=nm)


def table_ops(s, B, q, nsplice):
    A = s.A; sp, stl = A(SPDS['spec']), A(SPDS['steel'])
    dop = sorted(B.get('dop', []), key=lambda d: d['pos'])
    nd = len(dop)
    ops = []
    if nd: ops.append(dict(t='trows', h=sp, mode='ins', at=6, **{'from': 5}, n=nd))
    rH = 6 + nd; rC = rH + 3
    ops.append(dict(t='trows', h=sp, mode='del', at=rH + 1, n=1))      # empty row
    rC = rH + 2
    dm = B['main']['top'][1]
    cells = [[3, 3, B['hoop']['d'], F0], [3, 9, q['xl']['L'], F0], [4, 3, 16, F0], [4, 9, q['sk']['L'], F0], [5, 3, dm, F0]]
    for i, d in enumerate(dop):
        cells += [[6 + i, 3, d['d'], F0], [6 + i, 9, round(d['u1'] - d['u0']), F0]]
    cells += [[rH, 3, dm, F0], [rH, 9, 10 * dm, F0]]
    ops.append(dict(t='tnum', h=sp, cells=cells))
    tx = [[2, 2, 'Ригель ' + B['mark']], [rH, 0, 'Н3']]
    for i, d in enumerate(dop):
        tx += [[6 + i, 0, str(d['pos'])], [6 + i, 8, 'L='], [6 + i, 4, 'A'], [6 + i, 5, '500С'], [6 + i, 1, 'ГОСТ 34028-2016'], [6 + i, 2, '%%C']]
    tx += [[3, 5, '240']]
    ops.append(dict(t='tset', h=sp, cells=tx))
    R = lambda r: r + 1
    fm = [[3, 10, '%d' % q['nH'], F0], [3, 11, 'D4*D4*3.1415926/4*0.00785*J4/1000', F2], [3, 12, 'L4*K4', F2],
          [4, 10, '%d' % q['nsk'], F0], [4, 11, 'D5*D5*3.1415926/4*0.00785*J5/1000', F2], [4, 12, 'L5*K5', F2],
          [5, 10, '%.2f*%d' % (q['Lm'], 2 * q['nm']), F2], [5, 11, 'D6*D6*3.1415926/4*0.00785*1', F2], [5, 12, 'L6*K6', F2]]
    for i, d in enumerate(dop):
        r = 6 + i
        fm += [[r, 10, '%d' % d['n'], F0], [r, 11, 'D%d*D%d*3.1415926/4*0.00785*J%d/1000' % (R(r), R(r), R(r)), F2], [r, 12, 'L%d*K%d' % (R(r), R(r)), F2]]
    fm += [[rH, 10, '%d*%d*2' % (nsplice, q['nm']), F0], [rH, 11, 'D%d*D%d*3.1415926/4*0.00785*J%d/1000' % (R(rH), R(rH), R(rH)), F2], [rH, 12, 'L%d*K%d' % (R(rH), R(rH)), F2],
           [2, 12, 'Sum(M4:M%d)' % R(rH), F2], [rC, 12, '%.3f' % q['conc'], F2]]
    ops.append(dict(t='tformula', h=sp, cells=fm))
    # steel: A240 Øhoop | Итого | A500C Ø12 Ø16 Ø20 Ø25 Ø28 | Итого | Всего
    ops.append(dict(t='tset', h=stl, cells=[[5, 1, '%%%%C%d' % B['hoop']['d']], [6, 0, 'Ригель ' + B['mark']]]))
    ops.append(('STEEL', sp, rH))
    return ops


def steel_ops(stl, sp_handle, rH, B):
    """A500C columns 3..7 get the diameters actually used; each column = sum of the spec rows of that Ø"""
    dop = sorted(B.get('dop', []), key=lambda d: d['pos'])
    rows = {16: [5]}                                     # Ск1 (spec row 5 in 1-based = M5)
    dm = B['main']['top'][1]
    rows.setdefault(dm, []).extend([6, rH + 1])          # pos 1, Н3
    for i, d in enumerate(dop): rows.setdefault(d['d'], []).append(7 + i)
    used = sorted(rows)
    if len(used) > 5: raise Exception('too many diameters')
    rest = [x for x in (12, 20, 28, 32, 22) if x not in used]
    cols = sorted(used + rest[:5 - len(used)])
    cells = [[6, 1, 'Table({T:%s}).M4' % sp_handle, F2], [6, 2, 'Sum(B7:B7)', F2]]
    hdr = []
    for j, dd in enumerate(cols):
        c = 3 + j; hdr.append([5, c, '%%%%C%d' % dd])
        if dd in rows: cells.append([6, c, '+'.join('Table({T:%s}).M%d' % (sp_handle, r) for r in rows[dd]), F2])
        else: cells.append([6, c, 'TEXT:---'])
    cells += [[6, 8, 'Sum(D7:H7)', F2], [6, 9, 'I7+C7', F2]]
    return [dict(t='tset', h=stl, cells=hdr), dict(t='tformula', h=stl, cells=cells)]


def detail_texts(s, B, q):
    A = s.A; x = q['xl']; k = q['sk']
    T = {'406493': x['top'], '40648A': x['bot'], '40648B': x['hl'], '40648D': x['hr'], '406499': int(x['L']),
         '4064A7': k['v'], '4064A8': k['l'], '4064AB': k['l'], '4064B0': int(k['L'])}
    return [dict(t='settext', h=A(h), s=str(int(round(float(v))))) for h, v in T.items()]


def stamp_ops(s, B, no, title, nsheets_note=''):
    """replace the analog stamp block by the БДМ scheme stamp «Штамп№1» (x0.5) with sheet name / number"""
    A, D = s.A, s.D
    ops = [dict(t='erase', h=[A('40443F'), A(SPDS['no']), A(SPDS['name'])])]
    to = [203429 + D, 456189]
    base = [217417, -1787684]
    ops.append(dict(t='clone', h='5B4DF6', base=base, to=to, s=0.5, tag=s.P + 'STAMP'))
    ops.append(dict(t='clone', h='5B4DF7', base=base, to=to, s=0.5, tag=s.P + 'SNAME'))
    ops.append(dict(t='settext', h=s.P + 'SNAME', s=title))
    ops.append(dict(t='clone', h='5B4DF9', base=base, to=to, s=0.5, tag=s.P + 'SNO'))
    ops.append(dict(t='settext', h=s.P + 'SNO', s=no))
    notes = ('\\pxi-3.3333,l3.3333,t3.3333;1.\tОбщие указания см. л. - 1.1\\P2.\tДанный лист читать совместно с л. КЖ-2.1 ... 2.4'
             '\\P3.\tСтержни, указанные в "Ведомости деталей", должны гнуться механическим способом в холодном состоянии с радиусом гиба 3d - 5d, где d - диаметр стержня')
    if nsheets_note: notes += '\\P4.\t' + nsheets_note
    ops.append(dict(t='settext', h=A(SPDS['notes']), s=notes, w=9200))
    ops.append(dict(t='move', h=[A('406499'), A('4064B0'), A('4064A4'), A('4064B9')], d=[-150, 0]))
    return ops


def static_fixes(s):
    """analog «Узел А» texts that touch each other / their leaders"""
    A = s.A
    return [dict(t='move', h=[A('407B8C')], d=[0, 90]), dict(t='move', h=[A('407B8F')], d=[100, -200]), dict(t='move', h=[A('407B8E')], d=[120, -70]),
            dict(t='move', h=[A('407B95')], d=[-120, 0]), dict(t='move', h=[A('407BBE')], d=[0, -140])]
