"""spec table helpers (АБК): proportional quantities, masses = qty * unit mass"""
KL = 144.0 / 68.0          # strip/wall length ratio (perimeter 2*(60+12) / 2*(11.5+22.5))
KA = 720.0 / 258.75        # slab area ratio (60*12 / 11.5*22.5)
KP = (64.2 * 16.2) / (15.7 * 26.7)   # pit plan area ratio
KG = {8: 0.394585, 10: 0.616538, 12: 0.887814, 14: 1.208413, 16: 1.578336, 20: 2.466150}
f2 = lambda v: '%.2f' % v


def fq(v):
    if abs(v - round(v)) < 1e-6:
        return '%d' % round(v)
    return '%.2f' % v


def rowops(h, rows, total_cell, extra=()):
    """rows: (row, dia, cls, L_mm_or_None, qty, unit_mass_or_None)"""
    ops = []; tot = 0.0; bydia = {}
    for r, dia, cls, L, q, um in rows:
        if um is None:
            um = KG[dia] * (L / 1000.0 if L else 1.0)
        m = q * um; tot += m
        bydia[(cls, dia)] = bydia.get((cls, dia), 0) + m
        ops.append([r, 10, fq(q)]); ops.append([r, 11, f2(um)]); ops.append([r, 12, f2(m)])
        if L:
            ops.append([r, 9, '%d' % L])
    ops.append([total_cell[0], total_cell[1], f2(tot)])
    for e in extra:
        ops.append(list(e))
    return {'t': 'tset', 'h': h, 'cells': ops}, tot, bydia


def steel(h, row, cols, bydia):
    ops = []
    for c, k in cols:
        if k[0] == 'itogo':
            v = sum(m for (cl, d), m in bydia.items() if cl == k[1])
        elif k[0] == 'all':
            v = sum(m for (cl, d), m in bydia.items() if cl in ('A240', 'A500'))
        else:
            v = bydia.get(k, 0.0)
        ops.append([row, c, f2(v)])
    return {'t': 'tset', 'h': h, 'cells': ops}
