# Wall/column/slab marks on sheets 2.1–2.5 as in the analog «2.Схема каркаса Тип С» (Блок F2 тип С):
# mark = all walls on one line (по оси), every wall piece gets its own SPDS note (clone of analog См-5), arrow on the face
# toward the plan centre, 45° leader, shelf opposite the arrow; free-spot search against everything already drawn.
import json, math, sys
import ezdxf
from shapely.geometry import box, LineString, Polygon
from shapely.ops import unary_union
from shapely.strtree import STRtree
import model as M

TPL = 'E7E6A'                      # analog note См-5 (Angle 0), origin = stretch point 0, leader end = 1
X21, Y21 = -232964.0, 464256.885
SW = 59400.0
SH = {1: (0.0, 0.0), 2: (SW, -500.0), 3: (2 * SW, -500.0), 4: (3 * SW, 2500.0), 5: (4 * SW, 2500.0)}

H = {'См-1': [(125, -125, 1225, 125), (5875, -125, 7725, 125), (12325, -125, 14175, 125), (18825, -125, 19925, 125)],
     'См-2': [(5375, 7425, 8225, 7675), (11825, 7425, 14675, 7675)],
     'См-3': [(125, 13725, 3225, 13975), (16825, 13725, 19925, 13975)],
     'См-4': [(6925, 15225, 10275, 15475), (11625, 15225, 13125, 15475)],
     'См-5': [(6925, 17775, 10275, 18025)],
     'См-6': [(125, 22625, 1225, 22875), (18825, 22625, 19925, 22875)]}
VT = {'См-7': [(-125, -125, 125, 3175), (-125, 5750, 125, 17100), (-125, 20375, 125, 22875)],
      'См-8': [(6675, 125, 6925, 2775), (6675, 6175, 6925, 7425), (6675, 15225, 6925, 18025), (6675, 20575, 6925, 22875)],
      'См-9': [(10275, 15225, 10525, 22875)],
      'См-10': [(13125, 125, 13375, 2775), (13125, 6175, 13375, 7425), (13125, 15225, 13375, 22875)],
      'См-11': [(19925, -125, 20175, 2775), (19925, 5750, 20175, 15675), (19925, 20375, 20175, 22875)]}
VB = {'См-7': [(-125, -125, 125, 22875)],
      'См-8': [(6675, 125, 6925, 7425), (6675, 15225, 6925, 18025), (6675, 20575, 6925, 22875)],
      'См-9': [(10275, 15225, 10525, 22875)],
      'См-10': [(13125, 125, 13375, 7425), (13125, 15225, 13375, 22875)],
      'См-11': [(19925, -125, 20175, 22875)]}
ROOF = {'См-4': [(6925, 15225, 10275, 15475)], 'См-5': [(6925, 17775, 10275, 18025)], 'См-8': [(6675, 15225, 6925, 18025)],
        'См-9': [(10275, 15225, 10525, 22875)], 'См-10': [(13125, 15225, 13375, 22875)],
        'ПтМ-1': [(-125, -125, 20175, 75), (-125, 22675, 10275, 22875)]}


def elements(sheet):
    E = []
    if sheet == 5:
        for k, v in ROOF.items(): E += [(k, r) for r in v]
        return E
    for k, v in H.items(): E += [(k, r) for r in v]
    for k, v in (VB if sheet == 1 else VT).items(): E += [(k, r) for r in v]
    if sheet in (1, 2): E += [('Км-1', c) for c in M.COLUMNS]
    return E


def tw(s): return 0.155 * 1000 * len(s) / 1.0 * 0.25 / 0.25 if False else 194 * len(s)   # ГОСТ 2.304 2.5 mm: См-5 = 775


def load(dxf, geom, win):
    x0, y0, x1, y1 = win
    W = box(*win)
    lines, texts, solids = [], [], []
    for ln in open(geom, encoding='utf-8-sig'):
        f = ln.rstrip('\r\n').split('|')
        if f[0] == 'S':
            a = (float(f[3]), float(f[4])); b = (float(f[5]), float(f[6]))
            if a != b:
                g = LineString([a, b])
                if g.intersects(W) and g.length < 60000: lines.append(g)
        elif f[0] == 'T':
            g = box(*[float(v) for v in f[3:7]])
            if g.intersects(W): texts.append(g)
    d = ezdxf.readfile(dxf); m = d.modelspace()
    for e in m:
        t = e.dxftype()
        if t == 'LWPOLYLINE':
            p = [tuple(q[:2]) for q in e.get_points('xy')]
            if e.closed: p = p + p[:1]
            if len(p) < 2: continue
            g = LineString(p)
            if g.intersects(W) and g.length < 200000:
                lines.append(g)
                if e.closed and e.dxf.color == 124 and len(p) == 5: solids.append(Polygon(p))
        elif t in ('MTEXT', 'TEXT'):
            ins = e.dxf.insert
            if not (x0 < ins[0] < x1 and y0 < ins[1] < y1): continue
            if t == 'MTEXT':
                txt = e.plain_text().split('\n'); h = e.dxf.char_height; w = max(len(s) for s in txt) * 0.7 * h; hh = len(txt) * 1.6 * h
                ap = e.dxf.get('attachment_point', 1)
                dx = {1: 0, 2: -w / 2, 3: -w}[(ap - 1) % 3 + 1]; dy = {0: -hh, 1: -hh / 2, 2: 0}[(ap - 1) // 3]
                texts.append(box(ins[0] + dx, ins[1] + dy, ins[0] + dx + w, ins[1] + dy + hh))
    return lines, texts, solids


def place(sheet, X, Y, elems, obst, cx, cy, frame, tagp):
    lines, texts, solids = obst
    occ_lab = []; occ_ld = []
    allg = lines + texts + solids
    tree = STRtree(allg)
    def hits(g, skip=None):
        for i in tree.query(g):
            o = allg[i]
            if skip is not None and o.equals(skip): continue
            if o.intersects(g): return True
        return any(o.intersects(g) for o in occ_lab + occ_ld)
    ops = []; miss = []
    fx0, fy0, fx1, fy1 = frame
    inner = box(fx0 + 2000 + 100, fy0 + 600, fx1 - 600, fy1 - 600)
    stamp = box(fx1 - 500 - 18500, fy0, fx1, fy0 + 500 + 5500 + 300)
    for k, (name, r) in enumerate(elems):
        x0, y0, x1, y1 = r[0] + X, r[1] + Y, r[2] + X, r[3] + Y
        R = box(x0, y0, x1, y1)
        vert = (y1 - y0) > (x1 - x0)
        Lsh = tw(name) + 300
        # faces: toward the centre first
        if vert:
            faces = [(x0, -1), (x1, 1)] if cx < (x0 + x1) / 2 else [(x1, 1), (x0, -1)]
        else:
            faces = [(y0, -1), (y1, 1)] if cy < (y0 + y1) / 2 else [(y1, 1), (y0, -1)]
        best = None
        C0 = [(d, d) for d in (400, 500, 650, 800, 1000)] + [(dn, ds) for dn in (200, 300) for ds in (400, 600, 800, 1000)] +              [(dn, ds) for ds in (150, 250) for dn in (450, 650, 900)] + [(d, d) for d in (1300, 1700, 2200)]
        C1 = [(d, d) for d in (400, 650, 1000, 1500, 2000)] + [(dn, ds) for dn in (200, 300) for ds in (500, 900, 1400)]
        for relax in (0, 1, 2):
            if best: break
            for fv, n in faces:
                if best: break
                for t in (0.5, 0.35, 0.65, 0.2, 0.8, 0.1, 0.9):
                    if best: break
                    for dn, ds in (C0 if not relax else C1 if relax == 1 else [(dn, ds) for dn in (100, 200, 400, 700) for ds in (300, 600, 1000, 1500, 2000)]):
                        if best: break
                        for s in (1, -1):
                            if vert: T = (fv, y0 + t * (y1 - y0)); O = (fv + n * dn, T[1] + s * ds)
                            else: T = (x0 + t * (x1 - x0), fv); O = (T[0] + s * ds, fv + n * dn)
                            left = O[0] < T[0]
                            lab = box(O[0] - Lsh if left else O[0], O[1] - 40, O[0] if left else O[0] + Lsh, O[1] + 420)
                            if not inner.contains(lab) or lab.intersects(stamp): continue
                            ld = LineString([O, T])
                            ldt = LineString([O, (T[0] + (O[0] - T[0]) * 40 / ld.length, T[1] + (O[1] - T[1]) * 40 / ld.length)])
                            if hits(lab.buffer(60 if not relax else 30 if relax == 1 else 5)): continue
                            if not relax and hits(ldt): continue
                            if relax and (any(o.intersects(ldt) for o in texts + solids + occ_lab) or sum(1 for o in lines if o.crosses(ldt)) > (2 if relax == 1 else 5)): continue
                            best = (O, T, left, lab, ld); break
        if best is None:
            miss.append((name, r)); continue
        O, T, left, lab, ld = best
        occ_lab.append(lab.buffer(40)); occ_ld.append(ld.buffer(20))
        tag = '%sM%d' % (tagp, k)
        ops += [{'t': 'clone', 'h': TPL, 'base': [986.812891713809, -2983441.65079645], 'to': [O[0], O[1]], 'tag': tag},
                {'t': 'spmove', 'h': tag, 'items': [[1, T[0], T[1]]]},
                {'t': 'mcset', 'h': tag, 'set': {'FirstLine': name, 'Angle': math.pi if left else 0.0}}]
    return ops, miss


if __name__ == '__main__':
    out = {}
    for sh in (1, 2, 3, 4, 5):
        DX, DY = SH[sh]
        X, Y = X21 + DX, Y21 + DY
        fx0 = -243621 + SW * (sh - 1)
        frame = (fx0, 455939, fx0 + SW, 497939)
        obst = load('w/live.dxf', 'w/geom.txt', frame)
        E = elements(sh)
        cx, cy = X + 10025, Y + 11375
        ops, miss = place(sh, X, Y, E, obst, cx, cy, frame, 'MK%d_' % sh)
        out[sh] = ops
        print(sh, len(E), 'placed', len(ops) // 3, 'miss', miss)
        json.dump(ops, open('ops/marks%d.json' % sh, 'w', encoding='utf-8'), ensure_ascii=False)
