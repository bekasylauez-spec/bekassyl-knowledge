# Spec tables (Спецификация элементов, Ведомость расхода стали) for Пм1 and Пм2 from the dop zones.
import json, math
import gen
from gen import spec, SL, RHO

ops = []
def add(**k): ops.append(k); return k
def f2(v): return ('%.1f' % v) if v >= 10000 else ('%.2f' % v)

for k in ('P70', 'P45'):
    for i, (kind, faces) in enumerate(gen.KINDS[k]):
        if kind == 'dop':
            gen.dop_sheet(gen.Sheet(k, i), faces)
            if k == 'P70' and faces == (2,): gen.stair_ab(gen.Sheet(k, i))
summary = {}
for k, tag in (('P70', '70'), ('P45', '45')):
    rows, nsk, nf, conc = spec(k)
    name = SL[k]['name']; lvl = SL[k]['lvl']
    body = []
    steel = {}       # (class, d) -> kg
    for p, d, L, n, unit in rows:
        if L == 'м.п.':
            tot = n * RHO[d]; body.append([p, '214-210-0502 ГОСТ 34028-2016', d, '500С', 'м.п.', ('%.1f' % n), f2(RHO[d]), f2(tot)])
        else:
            tot = RHO[d] * L / 1000 * n; body.append([p, '214-210-0501 ГОСТ 34028-2016', d, '500С', str(L), str(n), f2(RHO[d] * L / 1000), f2(tot)])
        steel[('A500', d)] = steel.get(('A500', d), 0) + tot
    sk = RHO[8] * 1.12 * nsk; ff = RHO[8] * 1.22 * nf
    steel[('A500', 8)] = steel.get(('A500', 8), 0) + sk; steel[('A240', 8)] = ff
    total = sum(steel.values())
    npos = len(body)
    t1 = 't%s_1' % tag
    base = 8 if k == 'P70' else 10                                  # position rows in the analog table (Пм1 / Пм3)
    if npos > base: add(t='edit', h=t1, insrows=[2, 2, npos - base], cells=[])
    elif npos < base: add(t='edit', h=t1, delrows=[2, base - npos], cells=[])
    if k == 'P45': add(t='edit', h=t1, delrows=[npos + 3, 1], cells=[])      # Х1 row (no opening framing)
    cells = [[0, 2, 'Плита %s на отм. %s' % (name.replace('Пм', 'Пм-'), lvl)], [0, 11, f2(total)]]
    for r, (p, ob, d, cl, L, n, unit, tot) in enumerate(body, 1):
        cells += [[r, 0, p], [r, 1, ob], [r, 2, '%%C'], [r, 3, str(d)], [r, 4, 'A'], [r, 5, cl], [r, 8, 'L='], [r, 9, L], [r, 10, n], [r, 11, unit], [r, 12, tot]]
    r = npos + 1
    cells += [[r, 9, '1120'], [r, 10, str(nsk)], [r, 11, '0.44'], [r, 12, f2(sk)], [r + 1, 9, '1220'], [r + 1, 10, str(nf)], [r + 1, 11, '0.48'], [r + 1, 12, f2(ff)]]
    if k == 'P70':
        nab = gen.SL[k].get('ab1', 9); ab = RHO[14] * 2.5 * nab
        steel[('A500', 14)] = steel.get(('A500', 14), 0) + ab; total = sum(steel.values())
        cells += [[r + 2, 9, '2500'], [r + 2, 10, str(nab)], [r + 2, 11, f2(RHO[14] * 2.5)], [r + 2, 12, f2(ab)], [r + 4, 10, f2(conc)], [0, 11, f2(total)]]
    else: cells += [[r + 3, 10, f2(conc)]]
    add(t='edit', h=t1, cells=cells, rowh=[1, 800])
    # steel summary
    t0 = 't%s_0' % tag
    ds = sorted(d for (c, d) in steel if c == 'A500')
    cols = [8, 10, 12, 14, 16] + ([18] if 18 in ds else [])
    if 18 in ds: add(t='inscol', h=t0, at=9, **{'from': 8}, n=1)
    a240 = steel[('A240', 8)]
    c = [[6, 0, 'Плита %s на отм. %s' % (name, lvl)], [6, 1, f2(a240)], [6, 2, ''], [6, 3, f2(a240)]]
    for j, d in enumerate(cols):
        c.append([5, 4 + j, '%%C' + str(d)]); c.append([6, 4 + j, f2(steel.get(('A500', d), 0)) if steel.get(('A500', d), 0) else ''])
    ia = 4 + len(cols)
    a500 = sum(v for (cl, d), v in steel.items() if cl == 'A500')
    c += [[6, ia, f2(a500)], [6, ia + 1, f2(total)]]
    add(t='edit', h=t0, cells=c)
    summary[k] = dict(npos=npos, total=round(total, 1), conc=conc, kg_m3=round(total / conc, 1), steel={'%s Ø%d' % kk: round(v, 1) for kk, v in steel.items()}, nsk=nsk, nf=nf)

json.dump(ops, open('ops_spec.json', 'w', encoding='utf-8'), ensure_ascii=False)
json.dump(summary, open('spec_summary.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(json.dumps(summary, ensure_ascii=False, indent=1))
