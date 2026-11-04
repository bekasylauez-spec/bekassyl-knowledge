# Фм-1 3.3–3.6 redo (Bekassyl 04.11 evening): bars = clones of the analog LINE bars, spacing of stacked zones in ONE chain
# on one line per column («200x12 | 125 | 1475 | 200x3»), length chains along the bars, position = СПДС note with leaders
# to the first and the last bar. Obstacle scoring keeps texts off lines/texts and close to their segment.
import json, math, sys
sys.path.insert(0, '.')
import model as M
import gen_fm as G
from dimtools import chain, tw as dtw
from shapely.geometry import LineString as LS, box

NOTE = 'E7E6A'; NOTE_O = [986.812891713809, -2983441.65079645]
# analog bar templates (fm.dwg handles) — imported by import op with prefix 'BT:'
TPLH = {10: '2CB008', 12: '2CAD37', 14: '2CA799', 16: '2CB151', 25: '2CABE1'}
TPL_FOR = lambda d: TPLH.get(d, '2CB151')
ops = []
A_X = M.AX_X; A_Y = M.AX_Y


def ntw(s): return 194 * len(s)


def _aa(l):
    (x0, y0), (x1, y1) = l.coords[0], l.coords[-1]
    if abs(y0 - y1) < 1: return ('h', y0, min(x0, x1), max(x0, x1))
    if abs(x0 - x1) < 1: return ('v', x0, min(y0, y1), max(y0, y1))
    return None


class Occ:
    def __init__(s): s.lines = []; s.texts = []; s.dl = []
    def near_dl(s, l, gap=1000):
        a = _aa(l); c = 0
        if a is None: return 0
        for b in s.dl:
            if b[0] == a[0] and abs(a[1] - b[1]) < gap and min(a[3], b[3]) - max(a[2], b[2]) > -300: c += 30
        return c
    def par(s, L):
        c = 0
        for l in L:
            a = _aa(l)
            if a is None or a[3] - a[2] < 150: continue
            for o in s.lines:
                b = _aa(o)
                if b is None or b[0] != a[0]: continue
                if abs(a[1] - b[1]) < 150 and min(a[3], b[3]) - max(a[2], b[2]) > 50: c += 25
        return c
    def cost(s, L, T):
        c = s.par(L)
        for t in T:
            tt = t.buffer(-15)
            c += sum(4 for l in s.lines if l.intersects(tt)) + sum(12 for o in s.texts if o.intersects(t.buffer(50)))
        for l in L:
            c += sum(6 for o in s.texts if o.intersects(l))
        return c
    def add(s, L, T): s.lines += L; s.texts += T


def dim_geom(op):
    p1, p2, dl = op['p1'], op['p2'], op['dl']
    vert = abs(op['rot']) > 1
    Lm = abs((p2[1] - p1[1]) if vert else (p2[0] - p1[0]))
    txt = op.get('txt') or '%d' % round(Lm)
    w = 0.64 * 250 * len(txt) + 40; h = 290
    if vert:
        x = dl[0]; L = [LS([(x, p1[1]), (x, p2[1])]), LS([(p1[0], p1[1]), (x, p1[1])]), LS([(p2[0], p2[1]), (x, p2[1])])]
        cx, cy = op['tx'] if 'tx' in op else (x - 225, (p1[1] + p2[1]) / 2)
        T = [box(cx - h / 2, cy - w / 2, cx + h / 2, cy + w / 2)]
    else:
        y = dl[1]; L = [LS([(p1[0], y), (p2[0], y)]), LS([(p1[0], p1[1]), (p1[0], y)]), LS([(p2[0], p2[1]), (p2[0], y)])]
        cx, cy = op['tx'] if 'tx' in op else ((p1[0] + p2[0]) / 2, y + 225)
        T = [box(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)]
    if 'tx' in op:                                  # leader from the dim line to a displaced text
        if vert: L.append(LS([(x, min(max(cy, min(p1[1], p2[1])), max(p1[1], p2[1]))), (cx, cy)]))
        else: L.append(LS([(min(max(cx, min(p1[0], p2[0])), max(p1[0], p2[0])), y), (cx, cy)]))
    return [l for l in L if l.length > 1], T


def dims_geom(ch):
    L = []; T = []
    for op in ch:
        a, b = dim_geom(op); L += a; T += b
    return L, T


def far_text(ch):
    """text farther than 700 beyond its segment along the line, or 650 off the line → reject (Bekassyl: «мәні алысқа кетпесін»)"""
    for op in ch:
        if 'tx' not in op: continue
        p1, p2, dl, tx = op['p1'], op['p2'], op['dl'], op['tx']
        if abs(op['rot']) > 1:
            a, b = sorted((p1[1], p2[1])); c = tx[1]; off = abs(tx[0] - dl[0])
        else:
            a, b = sorted((p1[0], p2[0])); c = tx[0]; off = abs(tx[1] - dl[1])
        if c < a - 700 or c > b + 700 or off > 650: return True
    return False


def near_axis(v, A): return min(A.values(), key=lambda a: abs(a - v))


GAPMAX = 2200; MAXC = 99


ENDTOL = 300


def clusters(zs):
    """Bekassyl 04.11 19:50: one chain only for zones whose bar ends on the chain side are within ENDTOL of each other;
    the chain then sits right past those ends. Returns [(members, side)], side 'lo' (s0 end), 'hi' (s1 end) or None."""
    cl = []
    for z in sorted(zs, key=lambda q: q[0]['p0']):
        zz = z[0]; best = None
        for c in cl:
            ms, side = c
            if any(not (zz['p0'] > m[0]['p1'] or zz['p1'] < m[0]['p0']) for m in ms): continue
            if min(min(abs(zz['p0'] - m[0]['p1']), abs(m[0]['p0'] - zz['p1'])) for m in ms) > GAPMAX: continue
            if len(ms) >= MAXC: continue
            for sd in (('lo', 'hi') if side is None else (side,)):
                k = 's0' if sd == 'lo' else 's1'
                dv = max(abs(zz[k] - m[0][k]) for m in ms)
                if dv <= ENDTOL and (best is None or dv < best[0]): best = (dv, c, sd)
        if best:
            best[1][0].append(z); best[1][1] = best[2]
        else:
            cl.append([[z], None])
    return [(ms, side) for ms, side in cl]


def sheet(sh, key, F):
    fx, X, Y = G.origin(sh)
    axis = key.split('_')[1]                       # 'x': bars along x
    A = A_X if axis == 'x' else A_Y               # axes crossing the bars
    A2 = A_Y if axis == 'x' else A_X              # axes parallel to the bars
    P = lambda s_, p: [X + s_, Y + p] if axis == 'x' else [X + p, Y + s_]
    zs = [(z, False) for z in F[key]] + [(z, True) for z in F.get(key + '_3', [])]
    occ = Occ()
    # bars (first + last), analog LINE clones
    for z, th in zs:
        for p in ([z['p0']] + ([z['p1']] if z['n'] > 1 else [])):
            o = {'t': 'lineset', 'h': 'BT:' + TPL_FOR(z['d']), 's': P(z['s0'], p), 'e': P(z['s1'], p), 'layer': 'диам%d' % z['d']}
            if th: o['ltype'] = 'DASHED'; o['ltscale'] = 10
            ops.append(o); occ.lines.append(LS([o['s'], o['e']]))
    for v in A_X.values(): occ.lines.append(LS([(X + v, Y + M.FM[1] - 3000), (X + v, Y + M.FM[3] + 500)]))
    for v in A_Y.values(): occ.lines.append(LS([(X + M.FM[0] - 3000, Y + v), (X + M.FM[2] + 500, Y + v)]))
    fx0, fy0, fx1, fy1 = M.FM
    occ.lines.append(LS([(X + fx0, Y + fy0), (X + fx1, Y + fy0), (X + fx1, Y + fy1), (X + fx0, Y + fy1), (X + fx0, Y + fy0)]))
    bars = [(z, LS([P(z['s0'], p), P(z['s1'], p)])) for z, th in zs for p in ([z['p0']] + ([z['p1']] if z['n'] > 1 else []))]
    # 1) spacing chains per column
    for c, side in clusters(zs):
        members = [m[0] for m in c]
        s0 = min(z['s0'] for z in members); s1 = max(z['s1'] for z in members)
        p_lo = min(z['p0'] for z in members); p_hi = max(z['p1'] if z['n'] > 1 else z['p0'] for z in members)
        pts = []
        for z in members: pts += [z['p0']] + ([z['p1']] if z['n'] > 1 else [])
        inside = [a for a in A2.values() if p_lo < a < p_hi and not any(z['p0'] - 1 < a < z['p1'] + 1 for z in members)]
        if inside: pts += inside
        else:
            na = near_axis(p_lo, A2) if abs(near_axis(p_lo, A2) - p_lo) <= abs(near_axis(p_hi, A2) - p_hi) else near_axis(p_hi, A2)
            if not any(z['p0'] - 1 < na < z['p1'] + 1 for z in members): pts.append(na)
        pts = sorted(set(round(q, 1) for q in pts))
        cands = []
        lo_end = min(z['s0'] for z in members); hi_end = max(z['s1'] for z in members)
        # the row-0 text sits left of a vertical dim line / above a horizontal one: on that side the line must be far
        # enough from the bar ends for the text to fit between (Bekassyl 04.11: «975» lay on the bar)
        lo_off = (600, 750) if axis == 'y' else (350, 500)
        hi_off = (600, 750) if axis == 'x' else (350, 500)
        scs = ([lo_end - o for o in lo_off] if side in (None, 'lo') else []) + ([hi_end + o for o in hi_off] if side in (None, 'hi') else [])
        scs = [q for q in scs if not any(abs(q - a) < 300 for a in A.values())] or scs
        for sc in scs:
            outw = -1 if sc < lo_end else 1
            cp = [(sc, q) if axis == 'x' else (q, sc) for q in pts]
            ch = chain(cp, sc, axis == 'x', outw, X=X, Y=Y, side=True, avoid=[a for a in A2.values()])
            spans = {(min(z['p0'], z['p1']), max(z['p0'], z['p1'])): z['n'] - 1 for z in members if z['n'] > 1}
            for d in ch:
                k = 1 if axis == 'x' else 0
                a_, b_ = sorted((d['p1'][k] - (Y if axis == 'x' else X), d['p2'][k] - (Y if axis == 'x' else X)))
                for (u, v), n in spans.items():
                    if abs(a_ - u) < 1 and abs(b_ - v) < 1: d['txt'] = '200x%d' % n
            # ext lines go from the bar ends to the chain line: penalise crossing other zones' bars
            L, T = dims_geom(ch)
            pen = 0
            line_geo = LS([P(sc, pts[0]), P(sc, pts[-1])])
            for z, b in bars:
                if z in members: continue
                if line_geo.crosses(b) or line_geo.intersects(b): pen += 40
            cost = occ.cost(L, T) + pen + (500 if far_text(ch) else 0) + abs(sc - (lo_end if sc < lo_end else hi_end)) / 100 + occ.near_dl(line_geo)
            cands_line = line_geo
            cands.append((cost, ch, line_geo))
        cost, ch, lg = min(cands, key=lambda q: q[0])
        L, T = dims_geom(ch); occ.add(L, T); ops.extend(ch); occ.dl.append(_aa(lg))
    # 2) length chains along a bar, split at the crossing axes
    for z, th in sorted(zs, key=lambda q: -(q[0]['s1'] - q[0]['s0']) * q[0]['n']):
        insideA = [a for a in A.values() if z['s0'] < a < z['s1']]
        sp = [z['s0'], z['s1']] + insideA
        if not insideA:
            na0 = near_axis(z['s0'], A); na1 = near_axis(z['s1'], A)
            sp.append(na0 if abs(na0 - z['s0']) <= abs(na1 - z['s1']) else na1)
        cands = []
        refs = ((z['p1'], 1), (z['p0'], -1)) if z['n'] > 1 else ((z['p0'], 1), (z['p0'], -1))
        for ref, sgn in refs:
            # text between the line and the bars? (vertical dims: text left of the line; horizontal: above it)
            between = (axis == 'y' and sgn > 0) or (axis == 'x' and sgn < 0)
            for off in ((650, 800, 1000) if between else (250, 400, 600, 850)):
                lp = [(q, ref) if axis == 'x' else (ref, q) for q in sorted(set(sp))]
                ch = chain(lp, ref + sgn * off, axis == 'y', sgn, X=X, Y=Y, side=True, avoid=[a for a in A.values()])
                L, T = dims_geom(ch)
                cands.append((occ.cost(L, T) + (500 if far_text(ch) else 0) + off / 200, ch))
        cost, ch = min(cands, key=lambda q: q[0])
        L, T = dims_geom(ch); occ.add(L, T); ops.extend(ch)
    return


if __name__ == '__main__':
    F = json.load(open('arm/fm_final.json'))
    import gen_fm2 as N
    only = sys.argv[1].split(',') if len(sys.argv) > 1 else None
    for sh, key in (('3.3', 'bot_x'), ('3.4', 'top_x'), ('3.5', 'bot_y'), ('3.6', 'top_y')):
        if only and sh not in only: continue
        GAPMAX, MAXC = (1200, 4) if sh == '3.5' else (2200, 99)
        fx, X, Y = G.origin(sh)
        ops.append({'t': 'eraseregion', 'win': [fx - 5, 455939 - 5, fx + 59400 + 5, 455939 + 42000 + 5]})
        G.ops.clear(); G.frame(sh); G.background(sh); ops.extend(G.ops)
        sheet(sh, key, F)
        N.ops.clear()
        ex = ['Позиции со "*" - третья сетка: укладывается над основной нижней сеткой с зазором 60 мм, за расчетную зону выходит на анкеровку.'] if sh == '3.5' else []
        N.notes_mtext(fx, N.NOTES + ex, tag='N' + sh); ops.extend(N.ops)
    json.dump(ops, open('ops/fm4.json', 'w', encoding='utf-8'), ensure_ascii=False)
    print(len(ops))
