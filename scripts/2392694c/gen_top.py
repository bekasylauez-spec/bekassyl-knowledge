# Top slabs Пм-5 (+21.450, lift) / Пм-6 (+22.400, stair) and parapet ПтМ-2 (+22.400…+23.100) from analog 5.2 sheets
# 5.43 (опалубка Пм-7/8), 5.44 (армирование), 5.45 (спецификация), 5.46 (выпуск +21.500), 6.3 (Птм-2) imported into
# slots 7.37…7.41 (W1…W5). Plans replaced by the plan of scheme 2.5 «+21.450, +22.400» (axes 2/3, Б/В, walls, dims);
# analog frames, titles, sections, tables kept and edited (levels, numbers, quantities).
import os, json, math, re
os.environ['SLAB'] = 'pm4'
import gx
import gen_dop as GD
import gen_parapet as GP
SW = 59400.0
S37, S38, S39, S40, S41 = 2280879.0, 2322879.0, 2364879.0, 2406879.0, 2448879.0
Y0 = 455939.0
SA2, SAB = 37761.0, 478282.0        # axis 2 / axis Б of the small plan on scheme sheet 2.5
XS5 = -243621.0 + 4 * SW
PM5 = (6675, 15225, 10275, 18025)
PM6 = (10275, 15225, 13375, 22875)


def L(nm):
    out = []
    for l in open(os.path.join(gx.S, 'w', nm + '.txt'), encoding='utf-8').read().splitlines():
        r = l.split('\t')
        if len(r) > 4 and r[0] == 'L' and r[4].startswith('E') and 'NaN' not in r[4]:
            out.append((r[1], r[2], r[3], list(map(float, r[4][1:].split(',')))))
    return out


def inside(nm, s, rx0, ry0, rx1, ry1, keep=(), types=None):
    return [h for t, h, lay, e in L(nm) if e[0] >= s + rx0 and e[2] <= s + rx1 and e[1] >= Y0 + ry0 and e[3] <= Y0 + ry1
            and h not in keep and (types is None or t in types) and t != 'SPDSFORMAT']


def small_plan(s, ax, ay, tagp, thin=False):
    """clone the small plan of 2.5 so that axis 2 / axis Б land at (s+ax, Y0+ay)"""
    d = [s + ax - SA2, Y0 + ay - SAB]
    ops = []
    for l in open(os.path.join(gx.S, 'w', 'all.txt'), encoding='utf-8'):
        f = l.rstrip('\n').split('\t')
        if f[0] != 'L': continue
        a = list(map(float, f[4][1:].split(',')))
        if not (a[0] >= XS5 + 36000 and a[2] <= XS5 + SW and a[1] >= 468000): continue
        if f[1] in ('SPDSNOTEPOSITION', 'SPDSFORMAT') or f[2] == 'E2DE4': continue
        op = {'t': 'clone', 'h': f[2], 'base': [0, 0], 'to': d, 'tag': tagp + f[2]}
        if thin and f[1] == 'LWPOLYLINE': op['lw'] = 5
        ops.append(op)
    return ops


def PP(s, ax, ay, x, y): return [s + ax + (x - 6800), Y0 + ay + (y - 14750), 0]


def notes_text(h, old, new):
    return {'t': 'trepl', 'win': [0, 0, 1e8, 1e8], 'pairs': [[old, new]]}


def bars_sheet(s, ax, ay):
    """main bars of Пм-5 / Пм-6 like 7.2: representative bars, Ск1 pieces, notes, chains 50|200хN|rest"""
    ops = []
    P = lambda x, y: PP(s, ax, ay, x, y)
    for i, (x0, y0, x1, y1) in enumerate((PM5, PM6)):
        xb, yb = (x0 + x1) / 2 - 300, (y0 + y1) / 2 + 200
        ops += [{'t': 'lineset', 'h': '2B8500', 's': P(x0, yb), 'e': P(x1, yb), 'layer': 'диам12'},
                {'t': 'lineset', 'h': '2B8500', 's': P(xb, y0), 'e': P(xb, y1), 'layer': 'диам12'}]
        for s_, e_ in ((P(x0, yb + 20), P(x0 + 610, yb + 20)), (P(x1 - 610, yb + 20), P(x1, yb + 20)),
                       (P(xb - 20, y0), P(xb - 20, y0 + 610)), (P(xb - 20, y1 - 610), P(xb - 20, y1))):
            ops.append({'t': 'lineset', 'h': '2B8500', 's': s_, 'e': e_, 'layer': 'диам12'})
        tg = 'TB%d' % i
        ops += [{'t': 'clone', 'h': GD.T_NOTE, 'tag': tg},
                {'t': 'spmove', 'h': tg, 'items': [[0] + P(xb + 700, yb + 500)[:2], [1] + P(xb, yb + 500)[:2], [2] + P(xb + 700, yb)[:2]]},
                {'t': 'noteh', 'h': tg, 'l1': '1', 'l2': 'ш.200'}]
        for j, (px, py, sx, sy) in enumerate(((x0 + 300, yb + 20, x0 + 900, yb + 700), (xb - 20, y0 + 300, xb + 700, y0 + 900))):
            tg = 'TC%d%d' % (i, j)
            ops += [{'t': 'clone', 'h': GD.T_NOTE, 'tag': tg},
                    {'t': 'spmove', 'h': tg, 'items': [[0] + P(sx, sy)[:2], [1] + P(px, py)[:2], [2] + P(px, py)[:2]]},
                    {'t': 'noteh', 'h': tg, 'l1': 'Ск1', 'l2': 'ш.200'}]
        for vert, lo, hi in ((False, x0, x1), (True, y0, y1)):
            f = lo + 50; n = int((hi - 50 - f) // 200)
            pts = [(lo, f, ''), (f, f + 200 * n, '200х%d' % n), (f + 200 * n, hi, '')]
            for p, q, t in pts:
                if vert: op = {'t': 'dim', 'h': GD.T_DV, 'p1': P(x1, p), 'p2': P(x1, q), 'dl': P((x0 - 1200) if i == 0 else (x1 + 600), p), 'rot': math.pi / 2, 'txt': t}
                else: op = {'t': 'dim', 'h': GD.T_DH, 'p1': P(p, y1), 'p2': P(q, y1), 'dl': P(p, y1 + (600 if i == 0 else 1800)), 'rot': 0, 'txt': t}
                if not t: op['tx'] = (P(((x0 - 1200) if i == 0 else (x1 + 600)) - 60, p - 250 if p == lo else q + 250) if vert else P(p - 250 if p == lo else q + 250, y1 + (600 if i == 0 else 1800) + 180))
                ops.append(op)
    return ops


def run():
    ops = []
    # ---------- 7.37 опалубка Пм-5, Пм-6 (W1)
    s = S37
    ops.append({'t': 'erase', 'h': inside('w1', s, 3000, 10500, 36000, 27500, keep=('335BFE',))})
    sec = inside('w1', s, 3000, 2900, 19500, 13000)
    ops.append({'t': 'movegrp', 'h': sec, 'd': [18500, 11200]})
    ops += small_plan(s, 7500, 11500, 'T7_')
    for i, (x0, y0, x1, y1) in enumerate((PM5, PM6)):
        tg = 'TCont%d' % i
        ops += [{'t': 'clone', 'h': '335ADC', 'tag': tg},
                {'t': 'plset', 'h': tg, 'p': [PP(s, 7500, 11500, x0, y0), PP(s, 7500, 11500, x1, y0), PP(s, 7500, 11500, x1, y1), PP(s, 7500, 11500, x0, y1)], 'closed': True}]
    ops.append({'t': 'settext', 'h': '335BFE', 's': '{\\L\\C0;Опалубочный чертеж плит перекрытия Пм-5, Пм-6 на отм. +21.450, +22.400}'})
    ops.append({'t': 'move', 'h': ['335BFE'], 'd': [s + 4500 - 2284449, Y0 + 26200 - 483360]})
    ops.append({'t': 'clone', 'h': '335C21', 'tag': 'TS37'})
    ops.append({'t': 'spmove', 'h': 'TS37', 'items': [[0] + PP(s, 7500, 11500, 7400, 16600)[:2], [1] + PP(s, 7500, 11500, 5400, 16600)[:2]]})
    ops.append({'t': 'levelval', 'h': '335C3A', 'old': '+20.550;+21.500', 'value': '+21.450;+22.400'})
    ops += [{'t': 'settext', 'h': '335C00', 's': '{\\C0;Опалубочный чертеж плит перекрытия Пм-5, Пм-6 на отм. +21.450, +22.400}'},
            {'t': 'settext', 'h': '335AC8', 's': '7.37'}]
    # ---------- 7.38 армирование Пм-5, Пм-6 (W2)
    s = S38
    ops.append({'t': 'erase', 'h': inside('w2', s, 3000, 10500, 36000, 26800, keep=('336CC3',))})
    sec = inside('w2', s, 3000, 2900, 19500, 12500)
    ops.append({'t': 'movegrp', 'h': sec, 'd': [18500, 11200]})
    ops += small_plan(s, 7500, 11500, 'T8_', thin=True)
    ops += bars_sheet(s, 7500, 11500)
    ops.append({'t': 'settext', 'h': '336CC3', 's': '{\\L\\C256;Основное армирование плит перекрытия Пм-5, Пм-6 на отм. +21.450, +22.400}'})
    ops.append({'t': 'move', 'h': ['336CC3'], 'd': [s + 2500 - 2325177, Y0 + 26200 - 483901]})
    ops += [{'t': 'settext', 'h': '336ADA', 's': '{\\C0;Основное армирование плит перекрытия Пм-5, Пм-6 на отм. +21.450, +22.400}'},
            {'t': 'settext', 'h': '336AD7', 's': '7.38'}]
    # ---------- 7.39 спецификация Пм-5, Пм-6 (W3): quantities by the analog formulas, our geometry
    s = S39
    ops += [{'t': 'settext', 'h': '337BA5', 's': '{\\C0;Спецификация плит перекрытия Пм-5, Пм-6 на отм. +21.450, +22.400}'},
            {'t': 'settext', 'h': '337BA7', 's': '7.39'},
            {'t': 'tset', 'h': '337B0F', 'cells': [[0, 2, 'Плита Пм-5'], [2, 9, '1340'], [3, 9, '1092']]},
            {'t': 'tformula', 'h': '337B0F', 'cells': [[0, 12, '(Sum(M2:M4))', '%lu2%pr2'], [1, 10, '(195.2*1.05)', '%lu2%pr1'], [1, 11, '(D2*D2*3.1415926/4*0.00785*1)', '%lu2%pr2'], [1, 12, '(L2*K2)', '%lu2%pr2'],
                                                      [2, 10, '(64)', '%lu2%pr0'], [2, 11, '(D3*D3*3.1415926/4*0.00785*J3/1000)', '%lu2%pr2'], [2, 12, '(L3*K3)', '%lu2%pr2'],
                                                      [3, 10, '(26)', '%lu2%pr0'], [3, 11, '(D4*D4*3.1415926/4*0.00785*J4/1000)', '%lu2%pr2'], [3, 12, '(L4*K4)', '%lu2%pr2'],
                                                      [5, 12, '(10.08*0.25)', '%lu2%pr2']]},
            {'t': 'tset', 'h': '337C18', 'cells': [[0, 2, 'Плита Пм-6'], [2, 9, '1260'], [3, 9, '1540'], [4, 9, '1180']]},
            {'t': 'tformula', 'h': '337C18', 'cells': [[0, 12, '(Sum(M2:M5))', '%lu2%pr2'], [1, 10, '(234.8*2*1.05)', '%lu2%pr1'], [1, 11, '(D2*D2*3.1415926/4*0.00785*1)', '%lu2%pr2'], [1, 12, '(L2*K2)', '%lu2%pr2'],
                                                      [2, 10, '(208)', '%lu2%pr0'], [2, 11, '(D3*D3*3.1415926/4*0.00785*J3/1000)', '%lu2%pr2'], [2, 12, '(L3*K3)', '%lu2%pr2'],
                                                      [3, 10, '(54*2)', '%lu2%pr0'], [3, 11, '(D4*D4*3.1415926/4*0.00785*J4/1000)', '%lu2%pr2'], [3, 12, '(L4*K4)', '%lu2%pr2'],
                                                      [4, 10, '(60)', '%lu2%pr0'], [4, 11, '(D5*D5*3.1415926/4*0.00785*J5/1000)', '%lu2%pr2'], [4, 12, '(L5*K5)', '%lu2%pr2'],
                                                      [6, 12, '(23.715*0.25)', '%lu2%pr2']]},
            {'t': 'tset', 'h': '337CC9', 'cells': [[6, 0, 'Пм-5']]}, {'t': 'tset', 'h': '337CF2', 'cells': [[6, 0, 'Пм-6']]},
            {'t': 'tformula', 'h': '337CC9', 'cells': [[6, 1, '(Table({T:337B0F}).Evaluate(Sum(M2:M4)))', '%lu2%pr2'], [6, 2, '(Sum(B7:B7))', '%lu2%pr2'], [6, 3, '(C7)', '%lu2%pr2']]},
            {'t': 'tformula', 'h': '337CF2', 'cells': [[6, 1, '(Table({T:337C18}).Evaluate(Sum(M2:M5)))', '%lu2%pr2'], [6, 2, '(Sum(B7:B7))', '%lu2%pr2'], [6, 3, '(C7)', '%lu2%pr2']]}]
    # notes / sheet references of 7.37…7.39
    ops.append({'t': 'trepl', 'win': [S37 - 5, Y0 - 5, S40 + 5, Y0 + 30000], 'pairs': [['КЖ-5.43 ... 5.45', 'КЖ-7.37 ... 7.39']]})
    ops.append({'t': 'save'})
    out = gx.run(ops, 'top1')
    print('7.37-7.39', [l for l in out.splitlines() if 'ERR' in l or 'level' in l or 'done' in l][:8])


def run2():
    """7.40 выпуск из плиты покрытия Пм-6 into ПтМ-2 (1:100 like 7.33), 7.41 ПтМ-2 (W5)"""
    SEG = [('bot', 'x', 10275, 13375, 15225, 1), ('left', 'y', 15425, 22675, 10275, 1), ('right', 'y', 15425, 22675, 13375, -1), ('top', 'x', 10275, 13375, 22875, -1)]
    s, ax, ay = S40, 2500 + 4200, 5000
    P = lambda x, y: PP(s, ax, ay, x, y)
    ops = [{'t': 'erase', 'h': inside('w4', s, 0, 2500, 24500, 29000)}]
    ops += small_plan(s, ax, ay, 'TV_', thin=True)
    for nm, axx, a, b, o, sg in SEG:
        for off in (46, 154):
            c = o + sg * off
            for t in GP.bars_along(a, b):
                x, y = (t, c) if axx == 'x' else (c, t)
                ops.append({'t': 'pl', 'p': [P(x - 25, y), P(x + 25, y)], 'b': [1, 1], 'closed': True, 'w': 50, 'layer': 'диам12'})
    i0, i1, j0, j1, ch = 10275 + 550, 13375 - 550, 15225 + 550, 22875 - 550, 250
    pts = [(i0 + ch, j0), (i1 - ch, j0), (i1, j0 + ch), (i1, j1 - ch), (i1 - ch, j1), (i0 + ch, j1), (i0, j1 - ch), (i0, j0 + ch), (i0 + ch, j0)]
    ops.append({'t': 'pl', 'p': [P(*q) for q in pts], 'layer': 'диам12', 'lw': 40})
    for i, (nm, axx, a, b, o, sg) in enumerate(SEG):
        mid = (a + b) / 2
        sh = (mid, o + sg * 1100) if axx == 'x' else (o + sg * 1100, mid + 1200)
        ar1 = (mid, o + sg * 154) if axx == 'x' else (o + sg * 154, mid + 1200)
        ar2 = (mid, o + sg * 550) if axx == 'x' else (o + sg * 550, mid + 1200)
        tg = 'TVN%d' % i
        ops += [{'t': 'clone', 'h': GD.T_NOTE, 'tag': tg}, {'t': 'spmove', 'h': tg, 'items': [[0] + P(*sh)[:2], [1] + P(*ar1)[:2], [2] + P(*ar2)[:2]]},
                {'t': 'noteh', 'h': tg, 'l1': '2', 'l2': 'ш.200'}]
        xs = GP.bars_along(a, b)
        cp = [a, xs[0], xs[0] + 200 * (len(xs) - 2), xs[-1], b]
        line = o - sg * 700
        for p, q in zip(cp, cp[1:]):
            if q - p < 1: continue
            txt = '200х%d' % ((q - p) // 200) if q - p >= 400 and abs((q - p) % 200) < 1 else ''
            if axx == 'x': op = {'t': 'dim', 'h': GD.T_DH, 'p1': P(p, o), 'p2': P(q, o), 'dl': P(p, line), 'rot': 0, 'txt': txt}
            else: op = {'t': 'dim', 'h': GD.T_DV, 'p1': P(o, p), 'p2': P(o, q), 'dl': P(line, p), 'rot': math.pi / 2, 'txt': txt}
            if txt: op['tx'] = P((p + q) / 2, line + 180) if axx == 'x' else P(line - 60, (p + q) / 2)
            elif q - p < 300: op['tx'] = P(p - 250 if p == a else q + 250, line + 180) if axx == 'x' else P(line - 60, p - 250 if p == a else q + 250)
            ops.append(op)
    ops += [{'t': 'levelval', 'h': '33906F', 'old': '+21.500', 'value': '+22.400'}, {'t': 'levelval', 'h': '339070', 'old': '+22.200', 'value': '+23.100'},
            {'t': 'settext', 'h': '338C50', 's': '{\\C0;Схема расположения выпуск из плиты покрытия на отм. +22.400}'}, {'t': 'settext', 'h': '338C52', 's': '7.40'},
            {'t': 'trepl', 'win': [s - 5, Y0 - 5, s + 42005, Y0 + 30000], 'pairs': [['КЖ-5.46', 'КЖ-7.37 ... 7.41'], ['+21.500', '+22.400']]},
            {'t': 'mtext', 'x': s + 3500, 'y': Y0 + 27500}] if False else [
            {'t': 'levelval', 'h': '33906F', 'old': '+21.500', 'value': '+22.400'}, {'t': 'levelval', 'h': '339070', 'old': '+22.200', 'value': '+23.100'},
            {'t': 'settext', 'h': '338C50', 's': '{\\C0;Схема расположения выпуск из плиты покрытия на отм. +22.400}'}, {'t': 'settext', 'h': '338C52', 's': '7.40'},
            {'t': 'trepl', 'win': [s - 5, Y0 - 5, s + 42005, Y0 + 30000], 'pairs': [['КЖ-5.46', 'КЖ-7.37 ... 7.41'], ['+21.500', '+22.400']]}]
    ops.append({'t': 'save'})
    out = gx.run(ops, 'top2')
    print('7.40', [l for l in out.splitlines() if 'ERR' in l or 'level' in l or 'done' in l][:8])


if __name__ == '__main__':
    import sys
    if 'a' in sys.argv[1:]: run()
    if 'b' in sys.argv[1:]: run2()
