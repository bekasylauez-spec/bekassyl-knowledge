# table line check: every ACAD_TABLE inside the given sheet windows — row/column border lines present over their full length
import sys, json, ezdxf, collections
dxf = sys.argv[1]; sheets = json.load(open(sys.argv[2], encoding='utf-8'))
doc = ezdxf.readfile(dxf); msp = doc.modelspace()
bad = 0
for e in msp.query('ACAD_TABLE'):
    ins = e.dxf.insert
    name = next((n for n, (x0, y0, x1, y1) in sheets.items() if x0 <= ins.x <= x1 and y0 <= ins.y <= y1), None)
    if not name: continue
    try: blk = doc.blocks.get(e.dxf.block_name) if e.dxf.hasattr('block_name') else None
    except Exception: blk = None
    if blk is None:
        try: blk = doc.entitydb[e.dxf.block_record_handle].block
        except Exception: pass
    segs = []
    for v in e.virtual_entities():
        if v.dxftype() == 'LINE':
            a, b = v.dxf.start, v.dxf.end
            segs.append(((round(a.x, 1), round(a.y, 1)), (round(b.x, 1), round(b.y, 1))))
    H = collections.defaultdict(list); V = collections.defaultdict(list)
    for (x1, y1), (x2, y2) in segs:
        if abs(y1 - y2) < 0.5: H[round(y1)].append((min(x1, x2), max(x1, x2)))
        elif abs(x1 - x2) < 0.5: V[round(x1)].append((min(y1, y2), max(y1, y2)))
    if not H: print(name, e.dxf.handle, 'no lines read'); bad += 1; continue
    xs = [x for y in H for a, b in H[y] for x in (a, b)]; ys = [y for x in V for a, b in V[x] for y in (a, b)]
    X0, X1, Y0, Y1 = min(xs), max(xs), min(ys), max(ys)
    def cover(iv, lo, hi):
        iv = sorted(iv); c = lo
        for a, b in iv:
            if a > c + 1: return False
            c = max(c, b)
        return c >= hi - 1
    # outer frame
    for y in (Y0, Y1):
        if not cover(H.get(round(y), []), X0, X1): print(name, e.dxf.handle, 'outer horizontal line broken at y', round(y - Y0)); bad += 1
    for x in (X0, X1):
        if not cover(V.get(round(x), []), Y0, Y1): print(name, e.dxf.handle, 'outer vertical line broken at x', round(x - X0)); bad += 1
    # every horizontal line must end on vertical lines; every line inside the frame
    for y, iv in H.items():
        for a, b in iv:
            if a < X0 - 1 or b > X1 + 1: print(name, e.dxf.handle, 'line outside', y); bad += 1
    print(name, e.dxf.handle, 'rows', len(H), 'cols', len(V), 'ok' if bad == 0 else '')
print('TABLE BAD', bad)
