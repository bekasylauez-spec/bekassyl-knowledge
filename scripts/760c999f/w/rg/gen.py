# generate V4OPS json: 9 A–В rigel sheets 7000+7000 -> 6500+6500, Рм-17 3850 -> 4000, specs, steel tables, level erase/move
import re, sys, json, pickle, math
sys.stdout.reconfigure(encoding='utf-8')
D = r'C:\Users\Admin\AppData\Local\Temp\claude\D---------\760c999f-c28c-44e9-ba81-9cb2aa467e81\scratchpad\w\rg\\'
dump = open(D + 'rig_dump.txt', encoding='utf-8').read()
rows = pickle.load(open(D + 'rigrows.pkl', 'rb'))
DD = pickle.load(open(D + 'dimdef.pkl', 'rb'))  # handle -> (xmin, xmax, x2, x3)
tabs = open(D + 'rig.tables.txt', encoding='utf-8').read()
# tables: handle -> {x,y,rows:[[cells]], f:[[formula]]}
T = {}; cur = None
for ln in tabs.splitlines():
    m = re.match(r'TABLE (\w+) pos \(([-\d.]+),([-\d.]+)', ln)
    if m: cur = m.group(1); T[cur] = {'x': float(m.group(2)), 'y': float(m.group(3)), 'rows': [], 'f': []}; continue
    m = re.match(r'  R(\d+) h=[\d.]+ \|(.*)', ln)
    if m and cur:
        cells = re.split(r' \| ', m.group(2).rstrip()); cells[-1] = cells[-1].rstrip('| ')
        vals = []; fs = []
        for c in cells:
            c = c.strip(); fm = re.search(r'\{F:(.*)\}$', c)
            fs.append(fm.group(1) if fm else None); vals.append(re.sub(r'\s*\{F:.*\}$', '', c))
        T[cur]['rows'].append(vals); T[cur]['f'].append(fs)
KG = lambda d, L: d * d * 3.1415926 / 4 * 0.00785 * L / 1000  # kg per bar of length L mm
ops = []; report = []
Y0, Y1 = 371000, 377050
sheets = {}
for s in re.split(r'\n==== SHEET ', dump)[1:]:
    hdr, body = s.split('\n', 1); sn = hdr.split()[0]
    sheets[sn] = (hdr, body, [int(v) for v in re.search(r'\[([-\d, ]+)\]', hdr).group(1).split(',')])

def window(fr):
    return [fr[0] + 10, Y0, fr[2] - 10, Y1]
def keep_tables(fr):
    return [h for h, t in T.items() if fr[0] <= t['x'] <= fr[2]]

def short_crossers(fr, c, skip):
    out = []
    for h, t, x0, y0, x1, y1, txt, lay in rows:
        if h in skip or x1 < fr[0] or x0 > fr[2] or y0 < Y0 or y1 > Y1: continue
        if x0 < c < x1 and x1 - x0 < 5000: out.append((t, h, round(x0), round(x1), txt[:20]))
    return out

def pick_cut(fr, zl, zr, skip):
    c0 = (zl + zr) / 2
    for k in range(0, 60):
        for c in (c0 - 50 * k, c0 + 50 * k):
            if c < zl + 150 or c > zr - 150: continue
            if not short_crossers(fr, c, skip): return c
    return None

def tick_at(fr, x):
    best = None
    for h, t, x0, y0, x1, y1, txt, lay in rows:
        if t == 'LWPOLYLINE' and x1 - x0 < 5 and 300 < y1 - y0 < 700 and abs(x0 - x) < 250 and fr[0] <= x0 <= fr[2] and 373500 < y0 < 376000:
            if best is None or abs(x0 - x) < best[0]: best = (abs(x0 - x), h)
    return best[1] if best else None

def spec_table(fr, mark):
    for h, t in T.items():
        if fr[0] <= t['x'] <= fr[2] and t['rows'] and t['rows'][0][2].strip() == 'Ригель ' + mark: return h, t
def steel_table(fr, mark):
    for h, t in T.items():
        if fr[0] <= t['x'] <= fr[2] and any(r and r[0].strip() == 'Ригель ' + mark for r in t['rows']): return h, t

def zone_text(txt, dn):
    m = re.match(r'(\d+)х(\d+)(=.*)?$', txt)
    step, n, eq = int(m.group(1)), int(m.group(2)) + dn, m.group(3)
    if eq and eq != '=<>': eq = '=%d' % (step * n)
    return '%dх%d%s' % (step, n, eq or '')

def num(v):
    return float(v.replace(',', '.'))

# ---------- 9 sheets ----------
for sn, mark, ratio_old in [('6.3', 'Рм-3', 14.56), ('6.4', 'Рм-4', 14.56), ('6.6', 'Рм-6', 17.56), ('6.7', 'Рм-7', 17.56), ('6.8', 'Рм-8', 17.56),
                            ('6.9', 'Рм-9', 17.56), ('6.11', 'Рм-11', 17.56), ('6.13', 'Рм-13', 17.56), ('6.15', 'Рм-15', 17.56)]:
    hdr, body, fr = sheets[sn]
    w = window(fr)
    zones = re.findall(r'^D (\w+) \((-?\d+),(-?\d+)\)-\((-?\d+),(-?\d+)\) (\d+) txt=\'((?:100|200)х\d+(?:=.*)?)\'$', body, re.M)
    zones = [(z[0], DD[z[0]][0], DD[z[0]][1], z[6]) for z in zones]  # (h, xl, xr, txt) def-point x range
    zones.sort(key=lambda z: z[1])
    z200 = [z for z in zones if z[3].startswith('200')]
    assert len(z200) == 2, (sn, z200)
    zL, zR = z200
    # outer 100-zones adjacent
    oL = [z for z in zones if z[3].startswith('100') and abs(z[2] - zL[1]) < 5][0]
    oR = [z for z in zones if z[3].startswith('100') and abs(z[1] - zR[2]) < 5][0]
    tL, tR = tick_at(fr, zL[1]), tick_at(fr, zR[2])
    assert tL and tR, (sn, tL, tR)
    cR = pick_cut(fr, zR[1], zR[2], {zR[0]}); cL = pick_cut(fr, zL[1], zL[2], {zL[0]})
    assert cR and cL, (sn, cL, cR)
    ops.append({'t': 'stretchWinX', 'w': w, 'xcut': cR, 'dx': -500, 'keep': keep_tables(fr), 'tag': sn + ' R'})
    ops.append({'t': 'stretchWinX', 'w': w, 'xcut': cL, 'dx': -500, 'keep': keep_tables(fr), 'tag': sn + ' L'})
    def dimshift(h, xedge, dx, v):  # shift the extension point of dim h that sits at xedge
        x2, x3 = DD[h][2], DD[h][3]
        key = 'dx1' if abs(x2 - xedge) < abs(x3 - xedge) else 'dx2'
        ops.append({'t': 'dimdx', 'h': h, key: dx, 'v': v})
    dimshift(oL[0], zL[1], 100, zone_text(oL[3], 1)); dimshift(zL[0], zL[1], 100, zone_text(zL[3], -3))
    ops.append({'t': 'move', 'h': tL, 'dx': 100, 'dy': 0})
    dimshift(zR[0], zR[2], -100, zone_text(zR[3], -3)); dimshift(oR[0], zR[2], -100, zone_text(oR[3], 1))
    ops.append({'t': 'move', 'h': tR, 'dx': -100, 'dy': 0})
    # NB: dims whose XLine1/XLine2 orientation is reversed: handled by checking defpoints later (verify step)
    # ---- spec ----
    h, t = spec_table(fr, mark); R = t['rows']; F = t['f']
    cells = []; tot = 0.0; bydia = {}
    for r in range(1, len(R)):
        row = R[r]
        if len(row) < 13 or not row[0].strip() or row[0].startswith('Позиции'): continue
        pos = row[0].strip(); d = int(row[3]); L = row[9].strip(); n_txt = row[10].strip(); f = F[r][10]
        if pos in ('Х1*', 'Шп1*'):
            n_old = int(n_txt); n = n_old - 8
            unit = KG(d, num(L)); m = round(unit * n, 2)
            cells += [[r, 10, str(n)], [r, 12, '%.2f' % m]]
        elif 'пог' in L:
            fm = re.match(r'\((\d+\.\d+)\*(\d+)\)', f); Lold = float(fm.group(1)); mult = int(fm.group(2))
            Lnew = Lold - 1.0; n = Lnew * mult; unit = KG(d, 1000); m = round(unit * n, 2)
            cells += [[r, 10, str(int(round(n)))], [r, 12, '%.2f' % m]]
        else:
            m = num(row[12])
        tot += m; bydia[d] = bydia.get(d, 0) + m
    # concrete
    rc = [r for r in range(len(R)) if 'бетона' in R[r][2]][0]
    fm = re.match(r'\(([\d.]+)\*([\d.]+)\)', F[rc][12]); Lc = float(fm.group(1)) * (ratio_old - 1) / ratio_old; b = float(fm.group(2))
    cells += [[rc, 12, '%.2f' % (Lc * b)]]
    cells += [[0, 12, '%.2f' % tot]]
    ops.append({'t': 'cells', 'h': h, 'nolayout': 1, 'cells': cells})
    # ---- steel table ----
    hs, ts = steel_table(fr, mark); rs = [i for i, r in enumerate(ts['rows']) if r[0].strip() == 'Ригель ' + mark][0]
    hdrrow = [i for i, r in enumerate(ts['rows']) if any('%%C' in c for c in r)][0]
    cols = ts['rows'][hdrrow]; sc = []
    d8 = bydia.get(8, 0); other = sum(v for k, v in bydia.items() if k != 8)
    for ci, c in enumerate(cols):
        c = c.strip(); mm = re.match(r'%%C(\d+)', c)
        if mm:
            dd = int(mm.group(1)); v = bydia.get(dd, 0)
            sc.append([rs, ci, '%.2f' % v if v else '---'])
        elif 'Итого' in c:
            first = ci < 3
            sc.append([rs, ci, '%.2f' % (d8 if first else other)])
    sc.append([rs, len(cols) - 1, '%.2f' % tot])
    ops.append({'t': 'cells', 'h': hs, 'nolayout': 1, 'cells': sc})
    report.append('%s %s: cutL %d cutR %d | %s->%s, %s->%s | %s->%s, %s->%s | tot %.2f | steel %s' % (
        sn, mark, cL, cR, oL[3], zone_text(oL[3], 1), zL[3], zone_text(zL[3], -3), zR[3], zone_text(zR[3], -3), oR[3], zone_text(oR[3], 1), tot, sc))

# ---------- Рм-17 ----------
hdr, body, fr = sheets['6.17']; w = window(fr)
ops.append({'t': 'stretchWinX', 'w': w, 'xcut': 416970, 'dx': -50, 'keep': keep_tables(fr), 'tag': '6.17 gap'})
ops.append({'t': 'stretchWinX', 'w': w, 'xcut': 416500, 'dx': 200, 'keep': keep_tables(fr), 'tag': '6.17 zone'})
ops.append({'t': 'dimdx', 'h': '3BC1D2', 'v': '200х8'})
h, t = spec_table(fr, 'Рм-17'); R = t['rows']; cells = []; tot = 0; bydia = {}
for r in range(1, len(R)):
    row = R[r]
    if len(row) < 13 or not row[0].strip() or row[0].startswith('Позиции'): continue
    pos = row[0].strip(); d = int(row[3]); L = row[9].strip()
    if pos in ('Х1*', 'Шп1*'):
        n = int(row[10]) + 2; m = round(KG(d, num(L)) * n, 2); cells += [[r, 10, str(n)], [r, 12, '%.2f' % m]]
    elif L == '4310':
        n = int(row[10]); m = round(KG(d, 4460) * n, 2); cells += [[r, 9, '4460'], [r, 11, '%.2f' % KG(d, 4460)], [r, 12, '%.2f' % m]]
    else: m = num(row[12])
    tot += m; bydia[d] = bydia.get(d, 0) + m
rc = [r for r in range(len(R)) if 'бетона' in R[r][2]][0]
cells += [[rc, 12, '%.2f' % (4.4 * 4000 / 3850 * 0.45)], [0, 12, '%.2f' % tot]]
ops.append({'t': 'cells', 'h': h, 'nolayout': 1, 'cells': cells})
hs, ts = steel_table(fr, 'Рм-17'); rs = [i for i, r in enumerate(ts['rows']) if r[0].strip() == 'Ригель Рм-17'][0]
hdrrow = [i for i, r in enumerate(ts['rows']) if any('%%C' in c for c in r)][0]; cols = ts['rows'][hdrrow]; sc = []
d8 = bydia.get(8, 0); other = sum(v for k, v in bydia.items() if k != 8)
for ci, c in enumerate(cols):
    c = c.strip(); mm = re.match(r'%%C(\d+)', c)
    if mm: v = bydia.get(int(mm.group(1)), 0); sc.append([rs, ci, '%.2f' % v if v else '---'])
    elif 'Итого' in c: sc.append([rs, ci, '%.2f' % (d8 if ci < 3 else other)])
sc.append([rs, len(cols) - 1, '%.2f' % tot])
ops.append({'t': 'cells', 'h': hs, 'nolayout': 1, 'cells': sc})
report.append('6.17 Рм-17: tot %.2f cells %s steel %s' % (tot, cells, sc))

# ---------- levels ----------
ops.append({'t': 'erase', 'h': ['382255', '397A7C', '3A50CF']})   # 6.10 +13.400, 6.12 upper +13.400, 6.14 +13.400 (lower marks fixed via GUI level op)
json.dump(ops, open(D + 'fx_rig2.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('\n'.join(report)); print('ops', len(ops))
