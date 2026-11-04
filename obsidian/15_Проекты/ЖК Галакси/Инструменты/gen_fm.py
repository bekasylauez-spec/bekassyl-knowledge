# Фм-1 sheets 3.1–3.6 in the scheme DWG (after 2.7), composition of the analog «3.1 Фундамент» (Блок F2 тип С):
# 3.1 опалубка, 3.2 основное армирование, 3.3–3.6 доп. (низ/верх × буквенные/цифровые оси), first/last bar + «200хN».
import json, math, sys
sys.path.insert(0, '.')
import model as M
from dimtools import chain

SW = 59400.0
F0 = 172179.0                                   # frame x0 of 3.1 (right after 2.7)
YF0 = 455939.0
FR = {'3.1': 0, '3.2': 1, '3.3': 2, '3.4': 3, '3.5': 4, '3.6': 5, '3.7': 6, '3.8': 7}
TITLE = {'3.1': 'Опалубочный чертеж фундамента Фм-1 на отм. -4.650',
         '3.2': 'Основное армирование фундамента Фм-1 на отм. -4.650',
         '3.3': 'Дополнительное армирование фундамента Фм-1 нижней зоны по буквенным осям на отм. -4.650',
         '3.4': 'Дополнительное армирование фундамента Фм-1 верхней зоны по буквенным осям на отм. -4.650',
         '3.5': 'Дополнительное армирование фундамента Фм-1 нижней зоны по цифровым осям на отм. -4.650',
         '3.6': 'Дополнительное армирование фундамента Фм-1 верхней зоны по цифровым осям на отм. -4.650',
         '3.7': 'Разрезы фундамента Фм-1', '3.8': 'Спецификация фундамента Фм-1 на отм. -4.650'}
FX0, FY0, FX1, FY1 = M.FM
AXES21 = ['C8719', 'C871A', 'C8CF1', 'C8FBE', 'C9671', 'C9672', 'C9D3F', 'CA46F', 'CAA49']
# the user's 2.1 dims of axes / overall / Фм overhang (bottom row −4641, overall −5474, left −5502/−6202, top 30886)
DIMS21 = ['C8D2E', 'C8FFB', 'C92F3', 'C871B', 'D5721', 'D58E0', 'C9D7C', 'CA4AC', 'CAA86', 'CB1E2', 'C96A6', 'D56E4', 'D569A', 'D56B2', 'D56BF']
X21, Y21 = -232964.0, 464256.885
ops = []
def add(**k): ops.append(k); return k


def origin(sh):
    fx = F0 + SW * FR[sh]
    return fx, fx + 10657.0, Y21          # frame x0, plan X, plan Y


def frame(sh):
    fx, X, Y = origin(sh)
    d = fx - (-184221.0)                   # clone of 2.2's frame DC477 group
    for h in ('DC477', 'DC478', 'DC479', 'DC4E3', 'DC4E5'):
        add(t='clone', h=h, base=[0, 0], to=[d, 0], tag='FM%s_%s' % (sh, h))
    add(t='settext', h='FM%s_DC479' % sh, s=sh)
    add(t='settext', h='FM%s_DC4E3' % sh, s='{\\L' + TITLE[sh] + '}', w=30000)
    add(t='settext', h='FM%s_DC4E5' % sh, s=TITLE[sh], w=7000)


def background(sh, walls=False, hatch=False):
    fx, X, Y = origin(sh); dx = X - X21
    for h in AXES21: add(t='clone', h=h, base=[0, 0], to=[dx, 0], tag='FM%s_%s' % (sh, h))
    for h in DIMS21: add(t='clone', h=h, base=[0, 0], to=[dx, 0], tag='FM%s_%s' % (sh, h))
    x0, y0, x1, y1 = FX0, FY0, FX1, FY1
    add(t='pl', p=[[X + x0, Y + y0], [X + x1, Y + y0], [X + x1, Y + y1], [X + x0, Y + y1]], closed=True, layer='0', color=256,
        lw=50 if sh == '3.1' else 30, tag='FM%s_FMC' % sh)
    if walls:
        for i, r in enumerate(M.BASEMENT + M.COLUMNS):
            pts = [[X + r[0], Y + r[1]], [X + r[2], Y + r[1]], [X + r[2], Y + r[3]], [X + r[0], Y + r[3]]]
            add(t='pl', p=pts, closed=True, layer='0', color=256, lw=13 if not hatch else 30, tag='FM%s_W%d' % (sh, i))
            if hatch: add(t='hatch', pat='ANSI36', sc=20, ang=0, layer='.', loops=[pts], tag='FM%s_WH%d' % (sh, i))


def near_axis(v, axis):
    A = M.AX_X if axis == 'x' else M.AX_Y
    return min(A.values(), key=lambda a: abs(a - v))


def zone_ops(sh, z, axis, third=False):
    """bars along x (axis 'x'): s along x, p across (y). Along y: s along y, p across (x)."""
    fx, X, Y = origin(sh)
    lay = 'диам%d' % z['d']
    P = lambda s, p: [X + s, Y + p] if axis == 'x' else [X + p, Y + s]
    out = []
    ps = [z['p0']] + ([z['p1']] if z['n'] > 1 else [])
    for p in ps:
        o = {'t': 'pl', 'p': [P(z['s0'], p), P(z['s1'], p)], 'closed': False, 'layer': lay}
        if third: o['ltype'] = 'DASHED'; o['ltscale'] = 10
        out.append(o)
    # spacing chain across the bars at 250 from the zone start, bound to the nearest axis
    sx = z['s0'] + min(350, (z['s1'] - z['s0']) / 4)
    ax = near_axis(z['p0'], 'y' if axis == 'x' else 'x')
    pts = sorted(set([ax, z['p0'], z['p1']]))
    cpts = [(sx, q) if axis == 'x' else (q, sx) for q in pts]
    if axis == 'x': ch = chain(cpts, sx - 0, True, -1, X=X, Y=Y, side=True)
    else: ch = chain(cpts, sx - 0, False, -1, X=X, Y=Y, side=True)
    for d in ch:
        L = abs((d['p2'][1] - d['p1'][1]) if axis == 'x' else (d['p2'][0] - d['p1'][0]))
        if z['n'] > 1 and abs(L - (z['p1'] - z['p0'])) < 1: d['txt'] = '200x%d' % (z['n'] - 1)
        out.append(d)
    # length chain along the last bar, 300 beyond it, split at axes inside the zone
    A = M.AX_X if axis == 'x' else M.AX_Y
    inside = [a for a in A.values() if z['s0'] < a < z['s1']]
    sp = [z['s0'], z['s1']] + inside
    if not inside: sp.append(near_axis(z['s0'] if abs(near_axis(z['s0'], axis) - z['s0']) < abs(near_axis(z['s1'], axis) - z['s1']) else z['s1'], axis))
    if z.get('lap'):                                   # second bar of a lapped pair: its chain below the first bar
        line = z['p0'] - 300; ref = z['p0']; outw = -1
    else:
        line = z['p1'] + 300; ref = z['p1']; outw = 1
    lpts = [(q, ref) if axis == 'x' else (ref, q) for q in sorted(set(sp))]
    out += chain(lpts, line, axis == 'y', outw, X=X, Y=Y, side=True)
    # position: dimension between the first and the last bar with the position number (analog 3.3 «6», «7», «8»)
    if z['n'] > 1:
        A2 = M.AX_X if axis == 'x' else M.AX_Y
        c = z['s0'] + (z['s1'] - z['s0']) * (0.62 if z.get('lap') else 0.5)
        while any(abs(c - a) < 400 for a in A2.values()): c += 450
        d = chain([(c, z['p0']), (c, z['p1'])] if axis == 'x' else [(z['p0'], c), (z['p1'], c)], c, axis == 'x', 1, X=X, Y=Y)[0]
        d['txt'] = z['pos']
        out.append(d)
    return out


def dop_sheet(sh, key, F):
    frame(sh); background(sh)
    axis = key.split('_')[1]
    for z in F[key]: ops.extend(zone_ops(sh, z, axis))
    for z in F.get(key + '_3', []): ops.extend(zone_ops(sh, z, axis, third=True))


def base_sheet(sh):
    frame(sh); background(sh, walls=True)
    fx, X, Y = origin(sh)
    e = 50
    nX = int((FY1 - FY0 - 2 * e) / 200); nY = int((FX1 - FX0 - 2 * e) / 200)
    YB, XB = 2400.0, 10025.0                          # one bar per direction in free bays (analog 3.2)
    add(t='pl', p=[[X + FX0 + e, Y + YB], [X + FX1 - e, Y + YB]], closed=False, layer='диам16')
    add(t='pl', p=[[X + XB, Y + FY0 + e], [X + XB, Y + FY1 - e]], closed=False, layer='диам16')
    # «50 | 200xN=… | rest» along the top and the right side (analog / Резервуар 3.2)
    top = FY1 + 1000
    ops.extend(chain([(FX0, FY1), (FX0 + e, FY1), (FX0 + e + 200 * nY, FY1), (FX1, FY1)], top, False, 1, X=X, Y=Y, side=True))
    for o in ops[-3:]:
        if o['t'] == 'dim' and abs(abs(o['p2'][0] - o['p1'][0]) - 200 * nY) < 1: o['txt'] = '200x%d=%d' % (nY, 200 * nY)
    rx = FX1 + 1000
    ops.extend(chain([(FX1, FY0), (FX1, FY0 + e), (FX1, FY0 + e + 200 * nX), (FX1, FY1)], rx, True, 1, X=X, Y=Y, side=True))
    for o in ops[-3:]:
        if o['t'] == 'dim' and abs(abs(o['p2'][1] - o['p1'][1]) - 200 * nX) < 1: o['txt'] = '200x%d=%d' % (nX, 200 * nX)


def form_sheet(sh):
    frame(sh); background(sh, walls=True, hatch=True)


if __name__ == '__main__':
    F = json.load(open('arm/fm_final.json'))
    form_sheet('3.1'); base_sheet('3.2')
    for sh, key in (('3.3', 'bot_x'), ('3.4', 'top_x'), ('3.5', 'bot_y'), ('3.6', 'top_y')): dop_sheet(sh, key, F)
    json.dump(ops, open('ops/fm_plans.json', 'w', encoding='utf-8'), ensure_ascii=False)
    print(len(ops))


# ---------------- obstacle-aware placement of the zone dimensions ----------------
from shapely.geometry import LineString as _LS, box as _box
from shapely.strtree import STRtree as _TREE


def dim_geom(op):
    """approximate drawn geometry of a dim op: (lines, text boxes)"""
    p1, p2, dl = op['p1'], op['p2'], op['dl']; txt = op.get('txt') or '%d' % round(abs((p2[1] - p1[1]) if abs(op['rot']) > 1 else (p2[0] - p1[0])))
    w = 0.64 * 250 * len(txt) + 40; h = 290
    if abs(op['rot']) > 1:          # vertical
        x = dl[0]; L = [_LS([(x, p1[1]), (x, p2[1])]), _LS([(p1[0], p1[1]), (x, p1[1])]), _LS([(p2[0], p2[1]), (x, p2[1])])]
        if 'tx' in op: cx, cy = op['tx'][0] - 0, op['tx'][1]
        else: cx, cy = x - 225, (p1[1] + p2[1]) / 2
        T = [_box(cx - h / 2, cy - w / 2, cx + h / 2, cy + w / 2)]
    else:
        y = dl[1]; L = [_LS([(p1[0], y), (p2[0], y)]), _LS([(p1[0], p1[1]), (p1[0], y)]), _LS([(p2[0], p2[1]), (p2[0], y)])]
        if 'tx' in op: cx, cy = op['tx'][0], op['tx'][1] - 0
        else: cx, cy = (p1[0] + p2[0]) / 2, y + 225
        T = [_box(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)]
    return [l for l in L if l.length > 1], T


class Occ:
    def __init__(s): s.lines = []; s.texts = []
    def score(s, dops):
        sc = 0
        for op in dops:
            L, T = dim_geom(op)
            for t in T:
                tt = t.buffer(-20)
                sc += sum(3 for l in s.lines if l.intersects(tt)) + sum(10 for o in s.texts if o.intersects(t.buffer(40)))
            for l in L:
                sc += sum(5 for o in s.texts if o.intersects(l))
        return sc
    def add(s, dops):
        for op in dops:
            L, T = dim_geom(op); s.lines += L; s.texts += T


def dop_sheet2(sh, key, F):
    frame(sh); background(sh)
    fx, X, Y = origin(sh)
    axis = key.split('_')[1]
    zs = [(z, False) for z in F[key]] + [(z, True) for z in F.get(key + '_3', [])]
    P = lambda s_, p: [X + s_, Y + p] if axis == 'x' else [X + p, Y + s_]
    occ = Occ()
    # fixed: bars, axes, slab contour
    for z, th in zs:
        for p in ([z['p0']] + ([z['p1']] if z['n'] > 1 else [])):
            o = {'t': 'pl', 'p': [P(z['s0'], p), P(z['s1'], p)], 'closed': False, 'layer': 'диам%d' % z['d']}
            if th: o['ltype'] = 'DASHED'; o['ltscale'] = 10
            ops.append(o); occ.lines.append(_LS(o['p']))
    for v in M.AX_X.values(): occ.lines.append(_LS([(X + v, Y + FY0 - 3000), (X + v, Y + FY1 + 500)]))
    for v in M.AX_Y.values(): occ.lines.append(_LS([(X + FX0 - 3000, Y + v), (X + FX1 + 500, Y + v)]))
    occ.lines.append(_LS([(X + FX0, Y + FY0), (X + FX1, Y + FY0), (X + FX1, Y + FY1), (X + FX0, Y + FY1), (X + FX0, Y + FY0)]))
    A = M.AX_X if axis == 'x' else M.AX_Y
    A2 = M.AX_Y if axis == 'x' else M.AX_X
    for z, th in sorted(zs, key=lambda q: -(q[0]['s1'] - q[0]['s0']) * q[0]['n']):
        L = z['s1'] - z['s0']
        # 1) length chain along a bar, split at the axes inside
        inside = [a for a in A.values() if z['s0'] < a < z['s1']]
        sp = [z['s0'], z['s1']] + inside
        if not inside:
            na0 = near_axis(z['s0'], axis); na1 = near_axis(z['s1'], axis)
            sp.append(na0 if abs(na0 - z['s0']) <= abs(na1 - z['s1']) else na1)
        cands = []
        for ref, sgn in ((z['p1'], 1), (z['p0'], -1)) if not z.get('lap') else ((z['p0'], -1), (z['p1'], 1)):
            for off in (300, 600, 900, 1200):
                lpts = [(q, ref) if axis == 'x' else (ref, q) for q in sorted(set(sp))]
                cands.append(chain(lpts, ref + sgn * off, axis == 'y', sgn, X=X, Y=Y, side=True))
        best = min(cands, key=occ.score); occ.add(best); ops.extend(best)
        # 2) spacing chain across the bars, bound to the nearest axis
        ax = near_axis(z['p0'], 'y' if axis == 'x' else 'x')
        pts = sorted(set([ax, z['p0']] + ([z['p1']] if z['n'] > 1 else [])))
        cands = []
        for sx in (z['s0'] + 350, z['s1'] - 350, z['s0'] + L * 0.25, z['s0'] + L * 0.75, z['s0'] + 800, z['s1'] - 800, z['s0'] + L * 0.4, z['s0'] + L * 0.6):
            if any(abs(sx - a) < 300 for a in A.values()): continue
            cpts = [(sx, q) if axis == 'x' else (q, sx) for q in pts]
            ch = chain(cpts, sx, axis == 'x', -1, X=X, Y=Y, side=True)
            for d in ch:
                Ld = abs((d['p2'][1] - d['p1'][1]) if axis == 'x' else (d['p2'][0] - d['p1'][0]))
                if z['n'] > 1 and abs(Ld - (z['p1'] - z['p0'])) < 1: d['txt'] = '200x%d' % (z['n'] - 1)
            cands.append(ch)
        if cands:
            best = min(cands, key=occ.score); occ.add(best); ops.extend(best)
        # 3) position number on a dim between the first and the last bar (analog «6», «7», «8»)
        if z['n'] > 1:
            cands = []
            for f in (0.5, 0.4, 0.6, 0.3, 0.7, 0.2, 0.8, 0.12, 0.88):
                c = z['s0'] + L * f
                if any(abs(c - a) < 300 for a in A.values()): continue
                d = chain([(c, z['p0']), (c, z['p1'])] if axis == 'x' else [(z['p0'], c), (z['p1'], c)], c, axis == 'x', 1, X=X, Y=Y)[0]
                d['txt'] = z['pos'] + ('*' if th else '')
                cands.append([d])
            if cands:
                best = min(cands, key=occ.score); occ.add(best); ops.extend(best)
