# Ops for sheets 2.2–2.5 (plans) from the user's sheet 2.1 + model.py
import json, math, sys
import ezdxf
import model as M
from dimtools import chain

X21, Y21 = -232964.0, 464256.885          # axis 1 / axis А/1 on sheet 2.1
SW = 59400.0                               # sheet width (A2 at 1:100)
live = ezdxf.readfile(sys.argv[1] if len(sys.argv) > 1 else 'w/live.dxf')
msp = live.modelspace()

AXES = ['C8719', 'C871A', 'C8CF1', 'C8FBE', 'C9671', 'C9672', 'C9D3F', 'CA46F', 'CAA49']
COLS = ['CC0F8', 'CC16F', 'CC178', 'CC181', 'D3B95', 'D3B9E', 'D3BA7', 'D3BB0', 'D6432', 'D643B', 'D6444', 'D644D']


def rel(p): return (p[0] - X21, p[1] - Y21)


def inrect(p, r, e=1.0): return r[0] - e <= p[0] <= r[2] + e and r[1] - e <= p[1] <= r[3] + e


# classify the user's dims on 2.1
DIMS = {}
for e in msp:
    if e.dxftype() != 'DIMENSION': continue
    p1 = rel(e.dxf.defpoint2); p2 = rel(e.dxf.defpoint3); dl = rel(e.dxf.defpoint)
    rot = round(e.dxf.get('angle', 0)) % 180
    if not (-9000 < p1[0] < 30000 and -9000 < p1[1] < 34000): continue
    if rot == 90 and (abs(dl[0] + 1721) < 5 or abs(dl[0] - 21663) < 5): cls = 'side'
    elif rot == 90 and (abs(dl[0] - 4791) < 5 or abs(dl[0] - 11241) < 5): cls = 'stem'
    elif any(abs(round(v)) in (825, 20875) for v in (p1[0], p2[0])) or any(v in (-1950, 29800) for v in (round(p1[1]), round(p2[1]))): cls = 'fm'
    elif any(inrect(p, c) for c in M.COLUMNS for p in (p1, p2)): cls = 'col'
    elif rot == 90 and abs(dl[0] + 5502) < 5 and round(abs(p2[1] - p1[1])) == 6000: cls = 'axV1'
    else: cls = 'keep'
    DIMS[e.dxf.handle] = (cls, p1, p2, dl)

# dims on the roof sheet that reference walls missing there
ROOF_DROP = {'CFA41', 'DDE21', 'CF0F2', 'CD42E', 'CF14B', 'CD3C5', 'CD3D8',
             'D59A0', 'D5997', 'D5A60', 'D5A5D', 'D599D', 'D599A', 'D5A5F', 'D5A5E',
             'CD20F', 'CD197', 'CD230', 'CD227', 'CD1DF', 'CD1AF', 'CD22D', 'CD22A',
             'CD39A', 'CD16D', 'CD3B2', 'CD185'}


def walls_ops(rects, X, Y, tagp):
    ops = []
    for i, (x0, y0, x1, y1) in enumerate(rects):
        pts = [[X + x0, Y + y0], [X + x1, Y + y0], [X + x1, Y + y1], [X + x0, Y + y1]]
        ops.append({'t': 'pl', 'p': pts, 'closed': True, 'layer': '0', 'color': 124, 'lw': 30, 'tag': '%sW%d' % (tagp, i)})
        ops.append({'t': 'hatch', 'pat': 'ANSI36', 'sc': 20, 'ang': 0, 'layer': '.', 'loops': [pts], 'tag': '%sH%d' % (tagp, i)})
    return ops


def rect_pl(r, X, Y, tag, lw=30, color=256, ltype=None):
    x0, y0, x1, y1 = r
    op = {'t': 'pl', 'p': [[X + x0, Y + y0], [X + x1, Y + y0], [X + x1, Y + y1], [X + x0, Y + y1]], 'closed': True,
          'layer': '0', 'color': color, 'lw': lw, 'tag': tag}
    if ltype: op['ltype'] = ltype
    return op


def section_mark(word, p0, p1, X, Y, tag):
    # template E0650 (Онкоцентр 1:100): p0 = (1421234.9, -1320597.1)
    return [{'t': 'clone', 'h': 'E0650', 'base': [1421234.9, -1320597.1], 'to': [X + p0[0], Y + p0[1]], 'tag': tag},
            {'t': 'spmove', 'h': tag, 'items': [[1, X + p1[0], Y + p1[1]]]},
            {'t': 'mcset', 'h': tag, 'set': {'Word': word}}]


def side_chains(kind, X, Y):
    """left (axis 1) and right (axis 4) vertical chains, stems of axes 2/3."""
    big = kind in ('22', '23')
    if kind == 'roof':
        L = [(-125, -125), (-125, 0), (75, 75), (-125, 5000), (-125, 14750), (75, 22675), (-125, 22750), (-125, 22875)]
        R = [(20175, -125), (20175, 0), (19975, 75), (20175, 5000), (20175, 14750), (19975, 22675), (20175, 22750), (20175, 22875)]
    else:
        L = [(-125, -125), (-125, 0), (-125, 3175), (-125, 5000), (-125, 5750), (125, 13725), (125, 13975), (-125, 14750),
             (-125, 17100), (-125, 20375), (-125, 22750), (-125, 22875)]
        R = [(20175, -125), (20175, 0), (20175, 2775), (20175, 5000), (20175, 5750), (19925, 13725), (19925, 13975),
             (20175, 14750), (20175, 15675), (20175, 20375), (20175, 22750), (20175, 22875)]
    if kind == '22':
        L = [p for p in L if p[1] != 22875] + [(-125, 23100), (-125, 23600), (-125, 28600), (-125, 28750), (-125, 29100)]
        R = [p for p in R if p[1] != 22875] + [(20175, 23100), (20175, 23600), (20175, 28600), (20175, 28750), (20175, 29100)]
    if big:
        L += [(-125, -3275), (-125, 31175)]; R += [(20175, -3275), (20175, 31175)]
        if kind == '23': L += [(-125, 28750)]; R += [(20175, 28750)]
    AV = (0, 5000, 14750, 22750, 28750)
    ops = chain(L, -1721, True, -1, X=X, Y=Y, side=True, avoid=AV) + chain(R, 21663, True, 1, X=X, Y=Y, side=True)
    if kind != 'roof':
        S2 = [(5875, -125), (5875, 0), (5875, 125), (6675, 2775), (6675, 6175), (5375, 7425), (5375, 7675)]
        S3 = [(12325, -125), (12325, 0), (12325, 125), (13125, 2775), (13125, 6175), (11825, 7425), (11825, 7675)]
        ops += chain(S2, 4791, True, -1, X=X, Y=Y, side=True, avoid=AV) + chain(S3, 11241, True, -1, X=X, Y=Y, side=True, avoid=AV)
    return ops


def outer_chains(kind, X, Y):
    ops = []
    big = kind in ('22', '23')
    # bottom row of the axis chain (y −4641): slab edges 125 at both ends
    ops += chain([(-125, -125 if not big else -3275), (0, -5541)], -4641, False, -1, X=X, Y=Y)
    ops += chain([(20050, -5541), (20175, -125 if not big else -3275)], -4641, False, -1, X=X, Y=Y)
    if big:   # left outer chain: slab edges to the end axes
        ops += chain([(-125, -3275), (-6702, 0)], -5502, True, -1, X=X, Y=Y)
        ops += chain([(-6702, 28750), (-125, 31175)], -5502, True, -1, X=X, Y=Y)
    else:
        ops += chain([(-125, -125), (-6702, 0)], -5502, True, -1, X=X, Y=Y)
        ops += chain([(-6702, 22750), (-125, 22875)], -5502, True, -1, X=X, Y=Y)
        ops += [{'t': 'dim', 'h': 'C96A6', 'p1': [X - 6702, Y + 0], 'p2': [X - 6702, Y + 22750], 'dl': [X - 6202, Y + 22750], 'rot': math.pi / 2}]
    return ops


def plan_sheet(n, kind, title):
    """n = sheet number 2..5 -> offset; kind: '22' (−0.100 with columns), '23' (+3.950), 'typ', 'roof'"""
    DX = SW * (n - 1); dy = -1000.0 if kind in ('22', '23') else 2500.0
    X = X21 + DX; Y = Y21 + dy
    tp = 'S%d_' % n
    ops = []
    # axes
    for h in AXES:
        if kind in ('typ', 'roof') and h == 'CAA49': continue
        ops.append({'t': 'clone', 'h': h, 'base': [0, 0], 'to': [DX, dy], 'tag': tp + h})
        if kind in ('typ', 'roof') and h in ('C8719', 'C871A', 'C8CF1', 'C8FBE'):
            ops.append({'t': 'spmove', 'h': tp + h, 'items': [[0, X + M.AX_X['1234'['C8719 C871A C8CF1 C8FBE'.split().index(h)]], Y + 22750]]})
    # walls
    rects = M.TYPICAL if kind != 'roof' else M.ROOF_PARAPET + M.ROOF_LIFT + M.ROOF_STAIR
    ops += walls_ops(rects, X, Y, tp)
    # columns
    if kind == '22':
        for h in COLS: ops.append({'t': 'clone', 'h': h, 'base': [0, 0], 'to': [DX, dy], 'tag': tp + h})
    # slab contour
    slab = M.SLAB_BIG if kind in ('22', '23') else M.SLAB_TYP
    ops.append(rect_pl(slab, X, Y, tp + 'SLAB'))
    # user's dims that stay
    for h, (cls, p1, p2, dl) in DIMS.items():
        if cls == 'keep' or (cls == 'col' and kind == '22'):
            if kind == 'roof' and (h in ROOF_DROP or abs(dl[1] - 21094) < 5 or h == 'CFA83'): continue
            if kind in ('typ', 'roof') and h in ('CB1E2', 'C96A6'): continue
            ops.append({'t': 'clone', 'h': h, 'base': [0, 0], 'to': [DX, dy], 'tag': tp + 'D' + h})
        elif cls == 'axV1' and kind in ('22', '23'):
            ops.append({'t': 'clone', 'h': h, 'base': [0, 0], 'to': [DX, dy], 'tag': tp + 'D' + h})
    ops += side_chains(kind, X, Y)
    ops += outer_chains(kind, X, Y)
    if kind == 'roof':
        # core / stair room bindings (rows of 2.1 that lost their walls)
        ops += chain([(10525, 15225), (13125, 15225)], 13289, False, -1, X=X, Y=Y)
        ops += chain([(13375, 15225), (13375, 22750)], 15442, True, 1, X=X, Y=Y)
        ops += chain([(6675, 18025), (6675, 22675)], 5204, True, -1, X=X, Y=Y)
        ops += chain([(-125, -125), (0, -125), (75, 75), (19975, 75), (20050, -125), (20175, -125)], -1721, False, -1, X=X, Y=Y)
        ops += chain([(-125, 22875), (0, 22750), (75, 22675), (10275, 22875), (10525, 22875), (13125, 22875), (13375, 22875),
                      (19975, 22675), (20050, 22750), (20175, 22875)], 23875, False, 1, X=X, Y=Y)
    # section marks (outside all chains)
    top = 31175 if kind in ('22', '23') else 22875
    ytop = top + 1200 if kind in ('22', '23') else 25600
    ops += section_mark('1', (11900, ytop), (11900, -7600 if dy == 0 else -6900), X, Y, tp + 'SEC1')
    ops += section_mark('2', (23000, 1500), (-7300, 1500), X, Y, tp + 'SEC2')
    ops += section_mark('3', (23000, 16600), (-7300, 16600), X, Y, tp + 'SEC3')
    if kind == 'roof':
        ops += small_plan(X, Y, DX, dy, tp)
    return ops


def small_plan(X, Y, DX, dy, tp):
    SX, SY = 26325.0, -3225.0
    x, y = X + SX, Y + SY
    ops = []
    for h, k, p0, p1 in [('C871A', 'v', (6800, 22750), (6800, 12250)), ('C8CF1', 'v', (13250, 22750), (13250, 12250)),
                         ('C9D3F', 'h', (13250, 14750), (3300, 14750)), ('CA46F', 'h', (13250, 22750), (3300, 22750))]:
        ops.append({'t': 'clone', 'h': h, 'base': [0, 0], 'to': [DX + SX, dy + SY], 'tag': tp + 'sp' + h})
        ops.append({'t': 'spmove', 'h': tp + 'sp' + h, 'items': [[0, x + p0[0], y + p0[1]], [1, x + p1[0], y + p1[1]]]})
    ops.append(rect_pl(M.SLAB_LIFT, x, y, tp + 'spL'))
    ops.append(rect_pl(M.SLAB_STAIR, x, y, tp + 'spS'))
    ops += walls_ops(M.STAIR_PARAPET, x, y, tp + 'spP')
    ops += chain([(6675, 15225), (6800, 14750), (10525, 15225), (13250, 14750), (13375, 15225)], 13700, False, -1, X=x, Y=y)
    ops += chain([(6800, 14750), (13250, 14750)], 12950, False, -1, X=x, Y=y)
    ops += chain([(13375, 14750), (13375, 15225), (13375, 22750), (13375, 22875)], 14900, True, 1, X=x, Y=y)
    ops += chain([(6675, 14750), (6675, 15225), (6675, 18025), (6675, 22750)], 5150, True, -1, X=x, Y=y)
    ops += chain([(10275, 22875), (10475, 22675), (13175, 22675), (13375, 22875)], 23700, False, 1, X=x, Y=y)
    ops.append({'t': 'mtext', 'at': [x + 8600, y + 16625], 'h': 250, 'att': 5, 's': 'отм. +21.450', 'layer': '0', 'style': 'Isocpeur', 'tag': tp + 'spT1'})
    ops.append({'t': 'mtext', 'at': [x + 11825, y + 19800], 'h': 250, 'att': 5, 's': 'отм.\P+22.400', 'layer': '0', 'style': 'Isocpeur', 'tag': tp + 'spT2'})
    ops.append({'t': 'mtext', 'at': [x + 10025, y + 25600], 'h': 350, 'att': 5, 'w': 9000,
                's': '{\LСхема расположения элементов на отм. +21.450, +22.400}', 'layer': 'О_Формат', 'style': 'Isocpeur', 'tag': tp + 'spTT'})
    return ops


if __name__ == '__main__':
    allops = {}
    allops[2] = plan_sheet(2, '22', None)
    allops[3] = plan_sheet(3, '23', None)
    allops[4] = plan_sheet(4, 'typ', None)
    allops[5] = plan_sheet(5, 'roof', None)
    for n, o in allops.items():
        json.dump(o, open('ops/plan%d.json' % n, 'w', encoding='utf-8'), ensure_ascii=False)
        print(n, len(o))
    import collections
    print(collections.Counter(c for c, *_ in DIMS.values()))
