if SHEET == '3.4':
    seen = {}
    for kind, a, b, line in F.spans():
        hz = F.hoops(a, b)
        for z in hz:
            if kind == 'x': ln([(z, line - 145), (z, line + 145)], 'диам10', 30)
            else: ln([(line - 145, z), (line + 145, z)], 'диам10', 30)
        seen.setdefault((kind, round(b - a)), (a, b, line, hz))

    def runs_of(a, b, hz):
        pts = [a] + hz + [b]; dd = [round(q - p) for p, q in zip(pts, pts[1:])]; R_ = []; k = 0
        while k < len(dd):
            m = k
            while m + 1 < len(dd) and dd[m + 1] == dd[k]: m += 1
            R_.append((pts[k], pts[m + 1], dd[k], m - k + 1)); k = m + 1
        return R_

    for kind, ln_ref, span_len, at_off in (('x', AYY[0], 4000, -900), ('y', AXX[-1], 3000, 900)):
        a, b, line = next((s_[1], s_[2], s_[3]) for s_ in F.spans() if s_[0] == kind and s_[3] == ln_ref and round(s_[2] - s_[1]) == span_len)
        hz = F.hoops(a, b)
        R_ = runs_of(a, b, hz)
        vals = [R_[0][0]] + [r[1] for r in R_]
        texts = {k: ('%dх%d' % (r[2], r[3]) if r[3] > 1 else None) for k, r in enumerate(R_)}
        sm = {}
        for k, r in enumerate(R_):
            if r[1] - r[0] < 450:
                c = r[0] - 260 if k == 0 else (r[1] + 260 if k == len(R_) - 1 else (r[0] + r[1]) / 2)
                sm[k] = (c, line + at_off - 170) if kind == 'x' else (line + at_off + 170, c)
        chain(vals, line + at_off, kind == 'y', line, texts, sm)
    note('Х1(%%C10)', 'по схеме', (AXX[6] - 1400, AYY[0]), (AXX[6] - 900, AYY[0] + 1900))
    rows = []
    for key in sorted(seen):
        a, b, line, hz = seen[key]
        rr = runs_of(a, b, hz)
        rows.append('пролет %d (%s): %s - %d шт.' % (key[1], 'буквенные оси' if key[0] == 'x' else 'цифровые оси',
                    ', '.join(('%dх%d' % (r[2], r[3])) if r[3] > 1 else '%d' % r[2] for r in rr), len(hz)))
    O.append({'t': 'mtext', 'at': [SLOT + 2300, Y0 + 13300], 'h': 250, 'w': 36000, 'layer': 'Размеры',
              's': '1. Хомуты Х1 (%%C10 А500С) фундаментных балок 350х600 ставятся только в пролетах между подушками; в подушках - сетки поз. 1...4 (листы 3.2, 3.3).\\P'
                   '2. Шаг хомутов от грани подушки: 50, приопорные четверти пролета - шаг 100, середина - шаг 200. Размеры показаны на пролетах 6-7/А и А-Б/8, в остальных пролетах:\\P'
                   + '\\P'.join('    ' + r for r in rows)})

if SHEET == '3.6':
    for i, x in enumerate(AXX):
        for j, y in enumerate(AYY):
            ln([(x - 350, y - 450), (x + 350, y - 450), (x + 350, y + 450), (x - 350, y + 450), (x - 350, y - 450)], 'Размеры', 30)
    note('Вп1, Вп2', 'см. узел 1', (AXX[0] + 350, AYY[0] + 300), (AXX[0] + 1300, AYY[0] + 1900))
    O.append({'t': 'mtext', 'at': [SLOT + 2300, Y0 + 13300], 'h': 250, 'w': 36000, 'layer': 'Размеры',
              's': '1. Выпуски Вп1 (4 угловых, выступают на 600) и Вп2 (10 средних, выступают на 1200) %%C28 А500С - одинаковые во всех 24 подушках под колоннами Км-1...Км-6; привязка - по узлу 1.\\P'
                   '2. Выпуски опираются на нижнюю сетку подушки (лапка 200), фиксируются хомутами Х2 (%%C10, 3 шт.), устанавливаются до бетонирования.\\P'
                   '3. Стыковка с продольной арматурой колонн - накладками Н2 (ГОСТ 14098-2014, С21-Рн), вразбежку (см. листы 4.1...4.6).'})

    def Q(cx, cy, k): return lambda x, y: [round(cx + k * x, 1), round(cy + k * y, 1)]

    def lnw(pts, layer, lw, closed=False):
        O.append({'t': 'pl', 'p': pts, 'layer': layer, 'lw': lw, 'closed': closed, 'tag': tag()})

    def dimw(p1, p2, at, vertical, lfac, txt=None, tx=None):
        o = {'t': 'dim', 'h': DIM_T, 'p1': p1, 'p2': p2, 'dl': [at, p1[1]] if vertical else [p1[0], at], 'rot': math.pi / 2 if vertical else 0, 'txt': txt or '', 'lfac': lfac}
        if tx: o['tx'] = tx
        O.append(o)

    def notew(l1, l2, tgt, org, arrow='Oblique'):
        h = tag(); O.append({'t': 'clone', 'h': NOTE_T, 'tag': h})
        O.append({'t': 'moveto', 'h': h, 'idx': 1, 'to': tgt})
        O.append({'t': 'mcset', 'h': h, 'set': {'FirstLine': l1, 'SecondLine': l2, 'Origin': org, 'Angle': 0.0 if org[0] > tgt[0] else math.pi, 'Arrow': arrow}})

    def ttlw(text, x, y):
        t = tag(); O.append({'t': 'clone', 'h': TTL, 'tag': t, 'base': [0, 0], 'to': [0, 0]})
        O.append({'t': 'settext', 'h': t, 's': '{\\L%s}' % text}); O.append({'t': 'moveto', 'h': t, 'idx': 0, 'to': [x, y]})

    S = Q(SLOT + 9000, Y0 + 6300, 4)
    lnw([S(-350, -450), S(350, -450), S(350, 450), S(-350, 450)], 'Размеры', 30, True)
    for (bx, by) in F.DOW:
        c = S(bx, by); r = 56
        O.append({'t': 'circle', 'c': c, 'r': r, 'layer': 'диам28'})
        O.append({'t': 'hatch', 'pat': 'SOLID', 'layer': 'диам28', 'loops': [[[c[0] + r * math.cos(a / 8 * math.pi), c[1] + r * math.sin(a / 8 * math.pi)] for a in range(16)]]})
    a2, b2 = F.X2
    lnw([S(-a2 / 2, -b2 / 2), S(a2 / 2, -b2 / 2), S(a2 / 2, b2 / 2), S(-a2 / 2, b2 / 2)], 'диам10', 30, True)
    xs = [-350] + F.COLX + [350]; ys = [-450] + F.COLY + [450]
    for k, (p, q) in enumerate(zip(xs, xs[1:])):
        tx = S(p - 120, -450 - 330) if k == 0 else (S(q + 120, -450 - 330) if k == len(xs) - 2 else None)
        dimw(S(p, -450), S(q, -450), S(0, -450 - 250)[1], False, 0.25, None, tx)
    dimw(S(-350, -450), S(350, -450), S(0, -450 - 450)[1], False, 0.25)
    for k, (p, q) in enumerate(zip(ys, ys[1:])):
        tx = S(-350 - 330, p - 120) if k == 0 else (S(-350 - 330, q + 120) if k == len(ys) - 2 else None)
        dimw(S(-350, p), S(-350, q), S(-350 - 250, 0)[0], True, 0.25, None, tx)
    dimw(S(-350, -450), S(-350, 450), S(-350 - 450, 0)[0], True, 0.25)
    notew('Вп1', '4 шт.', S(F.COLX[-1], F.COLY[-1]), S(600, 650), 'None')
    notew('Вп2', '10 шт.', S(F.COLX[-1], F.COLY[2]), S(600, 150), 'None')
    notew('Х2(%%C10)', '3 шт.', S(a2 / 2, -200), S(600, -350))
    ttlw('Узел 1. Выпуски в подушке (план)', SLOT + 9000 - 3000, Y0 + 6300 + 2700)
    T2 = Q(SLOT + 25000, Y0 + 5600, 2)
    lnw([T2(-1500, -1500), T2(1500, -1500), T2(1500, -500), T2(-1500, -500)], 'Размеры', 30, True)
    lnw([T2(-1600, -1600), T2(1600, -1600), T2(1600, -1500), T2(-1600, -1500)], 'Размеры', 5, True)
    lnw([T2(-450, -500), T2(-450, 1400)], 'Размеры', 5); lnw([T2(450, -500), T2(450, 1400)], 'Размеры', 5)
    lnw([T2(-1450, -1440), T2(1450, -1440)], 'диам20', 40); lnw([T2(-1375, -560), T2(1375, -560)], 'диам16', 40)
    zb = -1500 + 50 + 40
    for y in F.COLY:
        top = -500 + (600 if y in (F.COLY[0], F.COLY[-1]) else 1200)
        s_ = -1 if y < 0 else 1
        lnw([T2(y + s_ * 200, zb), T2(y, zb), T2(y, top)], 'диам28', 40)
    for z in (-700, -950, -1200):
        lnw([T2(-F.X2[1] / 2, z), T2(F.X2[1] / 2, z)], 'диам10', 30)
    for p, q in ((-1500, -500), (-500, 100), (100, 700)):
        dimw(T2(1500, p), T2(1500, q), T2(1500 + 450, 0)[0], True, 0.5)
    dimw(T2(1500, -1600), T2(1500, -1500), T2(1500 + 450, 0)[0], True, 0.5, None, T2(1500 + 700, -1700))
    notew('Вп1', '(%%C28)', T2(F.COLY[-1], 0), T2(F.COLY[-1] + 500, 700))
    notew('Вп2', '(%%C28)', T2(F.COLY[3], 400), T2(F.COLY[-1] + 500, 1300))
    notew('Х2(%%C10)', '', T2(-F.X2[1] / 2, -950), T2(-1500 - 300, -300))
    ttlw('Узел 1. Разрез по подушке', SLOT + 25000 - 3000, Y0 + 5600 + 2 * 1500 + 1300)

