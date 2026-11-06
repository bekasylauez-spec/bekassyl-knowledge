# Replace section 4 (tables) of gen3.py with a version that inserts rows for Шп2 / Ск3 / mesh poz.11 (rectangular columns)
s = open('gen3.py', encoding='utf-8').read()
a = s.index('# ================= 4. tables')
b_ = s.index("add(t='settext', h=T('1118CE'), s=SHEET)")
NEW = r'''# ================= 4. tables, ведомость деталей, notes, stamp =================
HD = 10                                                  # hoops / pins Ø10 (Bekassyl 06.11)
envb, envh = b - 80, h - 80; dia = round(envb / math.sqrt(2) / 10) * 10
X1L = 2 * (envb + envh) + 200; X2L = 4 * dia + 200
PINLv = (h - 2 * e) + 200; PINLh = (b - 2 * e) + 200    # vertical pins span h, horizontal span b
SKV = round((h - 2 * e) / 10) * 10; SKH = round((b - 2 * e) / 10) * 10
SKD = round(math.hypot(b - 2 * e, h - 2 * e) / 10) * 10
NHOOP = len(P)
NODES = len(L) - 1                                       # mesh nodes: every floor
SQ = abs(b - h) < 1
V = {'1117B8': envb + 100, '1117AF': envb, '1117B0': envh, '1117B2': envh + 100, '1117BE': X1L,
     '1117D3': dia + 100, '1117CB': dia, '1117CD': dia + 100, '1117CA': dia, '1117D9': X2L if NPIN == 0 else (PINLv if NPB else PINLh),
     '11172F': LEG, '11172E': SKV if NPB else SKH, '111732': LEG, '111737': 2 * LEG + (SKV if NPB else SKH),
     '111745': LEG, '111744': SKD, '111748': LEG, '11174D': 2 * LEG + SKD}
for h_, v in V.items(): add(t='settext', h=T(h_), s='%d' % v)
SPM = PRE + '18D93'; STM = PRE + '18DCA'
SPMh = m[SPM]
Ltot = (L[-1] - L[0]) / 1000.0
lens = {}
for x, y0_, y1_, gi, i in segs_bar:
    lens.setdefault((gi, i), set()).add(round(y1_ - y0_))
if len(SPLV) == 1:
    pos_rows = [('1', lens[(0, 0)], 4), ('2', lens[(1, 0)], n - 4)]
else:
    a0 = lens[(0, 0)] | lens[(1, 0)]
    pos_rows = [('1', a0, n), ('2', lens[(0, 1)], 4), ('3', lens[(1, 1)], n - 4)]
for r_ in pos_rows: assert len(r_[1]) == 1, r_
# hoop / pin rows
hoop_rows = [('Х1', X1L, NHOOP)]
if NPIN == 0: hoop_rows.append(('Х2', X2L, NHOOP))
elif SQ: hoop_rows.append(('Шп1', PINLv, NHOOP * NPIN))
else:
    if NPB: hoop_rows.append(('Шп1', PINLv, NHOOP * NPB))
    if NPH: hoop_rows.append(('Шп2' if NPB else 'Шп1', PINLh, NHOOP * NPH))
# П-elements on top (NП = n/2): straight across h (inner b-face bars), straight across b (inner h-face bars), 2 diagonals
sk_rows = []
if SQ:
    if NPB: sk_rows.append(('Ск1', 2 * LEG + SKV, NPB + NPH))
else:
    if NPB: sk_rows.append(('Ск1', 2 * LEG + SKV, NPB))
    if NPH: sk_rows.append(('Ск%d' % (len(sk_rows) + 1), 2 * LEG + SKH, NPH))
sk_rows.append(('Ск%d' % (len(sk_rows) + 1), 2 * LEG + SKD, 2))
mesh_rows = [('10', b - 40, len(rods) + 1 + (0 if SQ else len(rodsh) + 1) * 0 + (len(rodsh) + 1 if SQ else 0))] if SQ else \
            [('10', h - 40, len(rods) + 1), ('11', b - 40, len(rodsh) + 1)]
# template rows: 1-2 hoops, 3-4 Ск, 5-7 positions, 8 blank, 9 Н, 10 С1, 11 Материалы, 12 concrete, 13 'Сетка С1', 14 mesh rod, 15 footnote
nh_extra = len(hoop_rows) - 2; nsk_extra = len(sk_rows) - 2; nm_extra = len(mesh_rows) - 1; npos_extra = len(pos_rows) - 3
assert nh_extra >= -1 and nsk_extra >= -1
if nm_extra > 0: add(t='trows', h=SPM, mode='ins', at=15, n=nm_extra, **{'from': 14})
if npos_extra > 0: add(t='trows', h=SPM, mode='ins', at=8, n=npos_extra, **{'from': 7})
if nsk_extra > 0: add(t='trows', h=SPM, mode='ins', at=5, n=nsk_extra, **{'from': 4})
if nh_extra > 0: add(t='trows', h=SPM, mode='ins', at=3, n=nh_extra, **{'from': 2})
oh = max(nh_extra, 0); osk = oh + max(nsk_extra, 0); opos = osk + max(npos_extra, 0); om = opos
r_h = [1 + i for i in range(max(len(hoop_rows), 2))]
r_sk = [3 + oh + i for i in range(max(len(sk_rows), 2))]
r_pos = [5 + osk + i for i in range(max(len(pos_rows), 3))]
r_N = 9 + opos; r_C1 = 10 + opos; r_conc = 12 + opos; r_mesh = [14 + om + i for i in range(len(mesh_rows))]
cells = [[0, 2, 'Колонна ' + MARK]]
blank_rows = []
def fill(rows_idx, data, d_):
    for k, r in enumerate(rows_idx):
        if k < len(data):
            lab, Lr, q = data[k]
            cells.extend([[r, 0, lab], [r, 3, '%d' % d_], [r, 9, '%d' % Lr], [r, 10, '%d' % q]])
        else:
            cells.extend([[r, c_, ''] for c_ in (0, 1, 2, 3, 4, 5, 8, 9)]); blank_rows.append(r)
fill(r_h, hoop_rows, HD)
fill(r_sk, sk_rows, 16)
fill(r_pos, [(lab, list(ls)[0], q) for lab, ls, q in pos_rows], D)
fill([r_N], [(NM, 10 * D, 2 * n * len(SPLV))], D)
NMESH_TOT = NMESH * NODES
cells += [[r_C1, 10, '%d' % NMESH_TOT], [r_conc, 12, '%.2f' % (b * h / 1e6 * Ltot)]]
fill(r_mesh, mesh_rows, 10)
add(t='tset', h=SPM, cells=cells)
if blank_rows: add(t='tformula', h=SPM, cells=sum([[[r, 10, 'TEXT:'], [r, 11, 'TEXT:'], [r, 12, 'TEXT:']] for r in blank_rows], []))
F = []
for r in [x for x in r_h + r_sk + r_pos + [r_N] + r_mesh if x not in blank_rows]:
    Rr = r + 1
    F += [[r, 11, 'D%d*D%d*3.1415926/4*0.00785*J%d/1000' % (Rr, Rr, Rr)], [r, 12, 'L%d*K%d' % (Rr, Rr)]]
F += [[r_C1, 11, '+'.join('M%d' % (r + 1) for r in r_mesh)], [r_C1, 12, 'L%d*K%d' % (r_C1 + 1, r_C1 + 1)], [0, 12, 'Sum(M2:M%d)' % (r_C1 + 1)]]
add(t='tformula', h=SPM, cells=F)
TT = 'Table({T:%s})' % SPMh
add(t='tformula', h=STM, cells=[[6, 2, '0'],
                                [6, 4, '%s.Evaluate(Sum(M%d:M%d))+%s.M%d' % (TT, r_h[0] + 1, r_h[-1] + 1, TT, r_C1 + 1)],
                                [6, 5, '%s.Evaluate(Sum(M%d:M%d))' % (TT, r_sk[0] + 1, r_sk[-1] + 1)],
                                [6, 6, '%s.Evaluate(Sum(M%d:M%d))' % (TT, r_pos[0] + 1, r_N + 1)]])
add(t='tset', h=STM, cells=[[5, 6, '%%%%C%d' % D], [6, 0, 'Колонна ' + MARK]])
add(t='evalf')
if NPIN:
    add(t='settext', h=T('1117D3'), s=''); add(t='settext', h=T('1117CD'), s=''); add(t='settext', h=T('1117CA'), s='')
TAB = dict(hoop=hoop_rows, sk=sk_rows, pos=[(a_, list(b2)[0], q) for a_, b2, q in pos_rows], mesh=mesh_rows, N=(NM, 10 * D, 2 * n * len(SPLV)), C1=NMESH_TOT)
'''
s = s[:a] + NEW + s[b_:]
s = s.replace("""print(len(ops), 'ops', 'n=%d D=%d pins=%d hoops=%d rods=%s pos=%s' % (n, D, NPIN, NHOOP, rods, [(a, list(b_)[0], q) for a, b_, q in pos_rows]))""",
              """print(len(ops), 'ops', 'n=%d D=%d pins=%d hoops=%d' % (n, D, NPIN, NHOOP), json.dumps(TAB, ensure_ascii=False))""")
open('gen3.py', 'w', encoding='utf-8').write(s)
print('ok')
