# -*- coding: utf-8 -*-
import math, json, pickle
import geom, design as D0, gen
S = geom.S

def kgm(d): return 0.00617 * d * d

def compute(res, z):
    pos = gen.positions(res, z); cnt = gen.zone_counts(res, z, pos)
    sl = geom.slab(z)
    area = sl['geom'].area / 1e6
    edge = sl['outer'].length + sum(h['geom'].length for h in sl['holes'])
    rows = []
    base_m = gen.base_quantities(z)
    rows.append(dict(p='1', des='214-210-0502 ГОСТ 34028-2016', d=10, cls='500С', L='м.п.', n=round(base_m, 1), u=round(kgm(10), 2)))
    rows[-1]['tot'] = round(rows[-1]['n'] * rows[-1]['u'], 2)
    for (d, L), p in sorted(pos.items(), key=lambda kv: kv[1]):
        n = cnt[(d, L)]; u = round(kgm(d) * L / 1000, 2)
        rows.append(dict(p=str(p), des='214-210-0501 ГОСТ 34028-2016', d=d, cls='500С', L=str(L), n=n, u=u, tot=round(n * u, 2)))
    nsk = math.ceil(edge / 200); nf = math.ceil(area)
    sk = dict(n=nsk, u=0.44, tot=round(nsk * 0.44, 2)); f1 = dict(n=nf, u=0.48, tot=round(nf * 0.48, 2))
    conc = round(area * 0.2, 2)
    # steel by class / diameter
    a500 = {}
    for r in rows: a500[r['d']] = a500.get(r['d'], 0) + r['tot']
    a500[8] = a500.get(8, 0) + sk['tot']
    tot500 = round(sum(a500.values()), 2); tot240 = f1['tot']
    total = round(tot500 + tot240, 1)
    return dict(rows=rows, sk=sk, f1=f1, conc=conc, a500=a500, tot500=tot500, tot240=tot240, total=total, area=area, edge=edge)

def fmt(v):
    return ('%.2f' % v) if v < 10000 else ('%.1f' % v)

def table_ops(C, h_spec, h_ved, cur_pos_rows, extra_del=None, d_cols=(8, 10, 12, 14, 16), d16as=None):
    ops = []
    npos = len(C['rows'])
    if extra_del is not None:
        ops.append({'t': 'trows', 'h': h_spec, 'mode': 'del', 'at': extra_del, 'n': 1})
    if npos > cur_pos_rows:
        ops.append({'t': 'trows', 'h': h_spec, 'mode': 'ins', 'at': cur_pos_rows + 1, 'from': cur_pos_rows, 'n': npos - cur_pos_rows})
    elif npos < cur_pos_rows:
        ops.append({'t': 'trows', 'h': h_spec, 'mode': 'del', 'at': npos + 1, 'n': cur_pos_rows - npos})
    cells = [[0, 11, fmt(C['total'])]]
    for i, r in enumerate(C['rows']):
        R = i + 1
        cells += [[R, 0, r['p']], [R, 1, r['des']], [R, 2, '%%C'], [R, 3, str(r['d'])], [R, 4, 'A'], [R, 5, r['cls']], [R, 8, 'L='], [R, 9, r['L']],
                  [R, 10, (('%.1f' % r['n']) if isinstance(r['n'], float) else str(r['n']))], [R, 11, '%.2f' % r['u']], [R, 12, fmt(r['tot'])]]
    R = npos + 1
    cells += [[R, 10, str(C['sk']['n'])], [R, 12, fmt(C['sk']['tot'])]]
    cells += [[R + 1, 10, str(C['f1']['n'])], [R + 1, 12, fmt(C['f1']['tot'])]]
    cells += [[R + 3, 10, '%.2f' % C['conc']]]
    ops.append({'t': 'tset', 'h': h_spec, 'cells': cells})
    a = C['a500']
    vc = [[6, 1, fmt(C['tot240'])], [6, 2, ''], [6, 3, fmt(C['tot240'])]]
    for col, d in zip((4, 5, 6, 7, 8), d_cols):
        vc.append([6, col, fmt(a[d]) if a.get(d) else ''])
    if d16as: vc.append([5, 8, '%%C' + str(d16as)])
    vc += [[6, 9, fmt(C['tot500'])], [6, 10, fmt(C['total'])]]
    ops.append({'t': 'tset', 'h': h_ved, 'cells': vc})
    return ops

def all_ops(res):
    C1 = compute(res, '7.0'); C2 = compute(res, '4.5')
    ops = []
    # Pm1: АВ-1 row (R19) removed, rows inserted after R16
    ops += table_ops(C1, 'BCEF4B62', 'BCEF4B09', 16, extra_del=19, d_cols=(8, 10, 12, 14, 22), d16as=22)
    ops += table_ops(C2, 'BCEEFBFC', 'BCEEFBA3', 13, d_cols=(8, 10, 12, 14, 16))
    # Ведомость деталей of Pm1: drop the АВ-1 row and lift Ф1
    ops.append({'t': 'erase', 'h': ['BCEF4684', 'BCEF469E', 'BCEF469F', 'BCEF46A0', 'BCEF46A1', 'BCEF46A3', 'BCEF46A5', 'BCEF46A7']})
    ops.append({'t': 'eraseregion', 'win': [-249100, -3127199, -242700, -3125150]})
    ops.append({'t': 'movewin', 'win': [-249100, -3129250, -242700, -3127150], 'd': [0, 2000]})
    return ops, C1, C2

if __name__ == '__main__':
    res, RS = pickle.load(open(S + r'\design.pkl', 'rb'))
    for z in res: D0.RAS[z] = D0.raster(z)
    ops, C1, C2 = all_ops(res)
    for C in (C1, C2):
        print('area %.1f m2 edge %.1f m conc %.2f total %.1f kg (A500 %.1f, A240 %.1f) %.1f kg/m3' % (C['area'], C['edge'] / 1000, C['conc'], C['total'], C['tot500'], C['tot240'], C['total'] / C['conc']))
        print('  by d', {k: round(v, 1) for k, v in sorted(C['a500'].items())})
