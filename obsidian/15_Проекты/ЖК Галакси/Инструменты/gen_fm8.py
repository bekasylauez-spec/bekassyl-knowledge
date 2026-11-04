# Фм-1 sheet 3.8 «Поперечное армирование фундамента Фм-1 на отм. -4.650» (analog 3.7): shear zones from LIRA ASW,
# rectangles (layer Размеры) + TRIANG hatch on диамNN, chains to the axes, СПДС notes «поз / ш.200х200» with an arrow.
# The specification sheet moves one frame to the right and becomes 3.9.
import json, math, sys
sys.path.insert(0, '.')
import model as M
import gen_fm as G
import gen_fm4 as F4
from dimtools import chain
from shapely.geometry import LineString as LS, box

FX8 = 543429.0
G.TITLE['3.8'] = 'Поперечное армирование фундамента Фм-1 на отм. -4.650'
_orig = G.origin
G.origin = lambda sh: (FX8, FX8 + 10657.0, G.Y21) if sh == '3.8' else _orig(sh)
Z = json.load(open('arm/fm_shear.json'))
FIRST = False
ops = []
fx, X, Y = G.origin('3.8')


def run():
    # 0) spec sheet → right by one A2 landscape frame, renamed 3.9
    if FIRST:
        ops.append({'t': 'movewin', 'win': [FX8 - 5, 455939 - 5, FX8 + 42000 + 5, 455939 + 59400 + 5], 'd': [59400, 0]})
        ops.append({'t': 'settext', 'h': 'FM3.8_DC479', 's': '3.9'})
    else:
        ops.append({'t': 'eraseregion', 'win': [FX8 - 5, 455939 - 5, FX8 + 59400 + 5, 455939 + 42000 + 5]})
    G.ops.clear(); G.frame('3.8'); G.background('3.8')
    ops.extend(G.ops)
    occ = F4.Occ()
    for v in M.AX_X.values(): occ.lines.append(LS([(X + v, Y + M.FM[1] - 3000), (X + v, Y + M.FM[3] + 500)]))
    for v in M.AX_Y.values(): occ.lines.append(LS([(X + M.FM[0] - 3000, Y + v), (X + M.FM[2] + 500, Y + v)]))
    fx0, fy0, fx1, fy1 = M.FM
    occ.lines.append(LS([(X + fx0, Y + fy0), (X + fx1, Y + fy0), (X + fx1, Y + fy1), (X + fx0, Y + fy1), (X + fx0, Y + fy0)]))
    # 1) zones
    rects = {}
    for z in Z:
        x0, x1, y0, y1 = z['x0'] - 100, z['x1'] + 100, z['y0'] - 100, z['y1'] + 100
        z['R'] = (x0, y0, x1, y1)
        pts = [[X + x0, Y + y0], [X + x1, Y + y0], [X + x1, Y + y1], [X + x0, Y + y1]]
        ops.append({'t': 'pl', 'p': pts, 'closed': True, 'layer': 'Размеры'})
        ops.append({'t': 'hatch', 'pat': 'TRIANG', 'sc': 10, 'ang': 0, 'layer': 'диам%d' % z['d'], 'loops': [pts], 'lw': 5})
        occ.lines.append(LS(pts + [pts[0]])); occ.texts.append(box(X + x0, Y + y0, X + x1, Y + y1))
        rects.setdefault(z['r'], []).append(z)
    # 2) chains: along each rectangle's long side split at the bands, across it; both bound to the nearest axis
    for r, bands in sorted(rects.items(), key=lambda q: -len(q[1])):
        x0 = min(b['R'][0] for b in bands); x1 = max(b['R'][2] for b in bands)
        y0 = min(b['R'][1] for b in bands); y1 = max(b['R'][3] for b in bands)
        xs = sorted(set([x0, x1] + [b['R'][0] for b in bands] + [b['R'][2] for b in bands]))
        ys = sorted(set([y0, y1] + [b['R'][1] for b in bands] + [b['R'][3] for b in bands]))
        for horiz in (True, False):
            q = xs if horiz else ys
            A = M.AX_X if horiz else M.AX_Y
            inside = [a for a in A.values() if q[0] < a < q[-1]]
            if not inside:
                na0 = min(A.values(), key=lambda a: abs(a - q[0])); na1 = min(A.values(), key=lambda a: abs(a - q[-1]))
                inside = [na0 if abs(na0 - q[0]) <= abs(na1 - q[-1]) else na1]
            q = sorted(set(q + inside))
            cands = []
            for side, ref in ((1, y1 if horiz else x1), (-1, y0 if horiz else x0)):
                for off in (400, 650, 900, 1200):
                    lp = [(v, ref) if horiz else (ref, v) for v in q]
                    ch = chain(lp, ref + side * off, not horiz, side, X=X, Y=Y, side=True, avoid=[a for a in (M.AX_Y if horiz else M.AX_X).values()])
                    L, T = F4.dims_geom(ch)
                    cands.append((occ.cost(L, T) + (500 if F4.far_text(ch) else 0) + off / 200, ch))
            cost, ch = min(cands, key=lambda c: c[0])
            L, T = F4.dims_geom(ch); occ.add(L, T); ops.extend(ch)
    # 3) notes: arrow to the band's edge facing the plan centre, shelf 300–600 off the zone, toward the centre
    cx, cy = X + (fx0 + fx1) / 2, Y + (fy0 + fy1) / 2
    SH_W = 194 * 9 + 300
    for k, z in enumerate(Z):
        x0, y0, x1, y1 = [v + (X if i % 2 == 0 else Y) for i, v in enumerate(z['R'])]
        best = None
        for tx in (0.5, 0.3, 0.7):
            for face in ('t', 'b', 'l', 'r'):
                if face in 'tb':
                    T = (x0 + (x1 - x0) * tx, y1 if face == 't' else y0); n = (0, 1 if face == 't' else -1)
                else:
                    T = (x1 if face == 'r' else x0, y0 + (y1 - y0) * tx); n = (1 if face == 'r' else -1, 0)
                for dd in (450, 600, 800, 1100):
                    for sg in (1, -1):
                        O = (T[0] + n[0] * dd + (sg * dd if n[0] == 0 else 0), T[1] + n[1] * dd + (sg * dd if n[1] == 0 else 0))
                        left = O[0] < T[0]
                        lab = box(O[0] - SH_W if left else O[0], O[1] - 420, O[0] if left else O[0] + SH_W, O[1] + 420)
                        ld = LS([O, (T[0] - n[0] * 30, T[1] - n[1] * 30)])
                        cst = 6 * sum(1 for l in occ.lines if l.intersects(lab.buffer(30))) + 20 * sum(1 for o in occ.texts if o.intersects(lab.buffer(60)))
                        cst += 10 * sum(1 for o in occ.texts if o.intersects(ld)) + 2 * sum(1 for l in occ.lines if l.crosses(ld))
                        cst += dd / 300 + (0 if (O[0] - T[0]) * (cx - T[0]) >= 0 or (O[1] - T[1]) * (cy - T[1]) >= 0 else 2)
                        if best is None or cst < best[0]: best = (cst, O, (T[0] - n[0] * 30, T[1] - n[1] * 30), lab, ld, left)
        cst, O, Tp, lab, ld, left = best
        occ.texts.append(lab); occ.lines.append(ld)
        tag = 'FS_%d' % k
        ops.append({'t': 'clone', 'h': F4.NOTE, 'base': F4.NOTE_O, 'to': list(O), 'tag': tag})
        ops.append({'t': 'spmove', 'h': tag, 'items': [[1, Tp[0], Tp[1]]]})
        ops.append({'t': 'mcset', 'h': tag, 'set': {'FirstLine': z['pos'], 'SecondLine': 'ш.200х200', 'Angle': math.pi if left else 0.0, 'Arrow': 'Arrow'}})
    import gen_fm2 as N
    N.ops.clear()
    N.notes_mtext(FX8, ['Общие указания см. л. 1.1.', 'Данный лист читать совместно с л. 2.1 и 3.1 ... 3.9.',
                        'Поперечные стержни устанавливать в узлах пересечения стержней основных сеток (ш.200х200), с загибами вокруг стержней верхней и нижней сеток.',
                        'Поперечное армирование принято по расчетной модели ЛИРА "Тип А6 С2" (ASW); в полосе между осями А и Б - условно.'], tag='N3.8s')
    ops.extend(N.ops)


if __name__ == '__main__':
    run()
    json.dump(ops, open('ops/fm8.json', 'w', encoding='utf-8'), ensure_ascii=False)
    print(len(ops))
