# Км-2 (rows 23100/28600) → 600×600 per LIRA (Bekassyl 04.11: «Лирада дұрыс»): dynamic visibility «Колонна 60х60»,
# edge columns shifted 50 inward to stay flush with the slab edge, dim ext points on old faces → new faces (2.1–2.3)
import json, ezdxf, logging
logging.disable(logging.CRITICAL)
import gen_marks as GM
d = ezdxf.readfile('w/live.dxf'); ms = d.modelspace()
OLDC = [(x0, y0) for y0 in (23100, 28600) for x0 in (-125, 6550, 13000, 19675)]   # old 500 boxes (x0, y0)
def newbox(x0, y0):
    cx, cy = x0 + 250, y0 + 250
    if x0 == -125: cx = 175
    if x0 == 19675: cx = 19875
    return cx - 300, cy - 300, cx + 300, cy + 300
XMAP = {}; YMAP = {}
for x0, y0 in OLDC:
    nb = newbox(x0, y0)
    XMAP[x0] = nb[0]; XMAP[x0 + 500] = nb[2]; YMAP[y0] = nb[1]; YMAP[y0 + 500] = nb[3]
ops = []
for sh in (1, 2, 3):
    DX, DY = GM.SH[sh]; X, Y = GM.X21 + DX, GM.Y21 + DY
    fx0 = -243621 + GM.SW * (sh - 1)
    for e in ms:
        t = e.dxftype()
        if t == 'INSERT' and e.dxf.name.startswith('*U'):
            p = e.dxf.insert
            for x0, y0 in OLDC:
                if abs(p.x - X - (x0 + 250)) < 3 and abs(p.y - Y - (y0 + 250)) < 3:
                    nb = newbox(x0, y0); ncx = (nb[0] + nb[2]) / 2
                    ops.append({'t': 'dyn', 'h': e.dxf.handle, 'prop': 'Видимость1', 'value': 'Колонна 60х60'})
                    if abs(ncx - (x0 + 250)) > 1: ops.append({'t': 'move', 'h': [e.dxf.handle], 'd': [ncx - (x0 + 250), 0]})
        if t == 'DIMENSION' and fx0 < e.dxf.defpoint.x < fx0 + GM.SW:
            pts = [e.dxf.defpoint2, e.dxf.defpoint3]; new = []; ch = False
            for q in pts:
                rx, ry = q.x - X, q.y - Y; nx, ny = rx, ry
                for x0, y0 in OLDC:
                    if x0 - 2 <= rx <= x0 + 502 and y0 - 2 <= ry <= y0 + 502:
                        for k, v in XMAP.items():
                            if abs(rx - k) < 2: nx = v
                        for k, v in YMAP.items():
                            if abs(ry - k) < 2: ny = v
                if abs(nx - rx) > 0.5 or abs(ny - ry) > 0.5: ch = True
                new.append([X + nx, Y + ny])
            if ch:
                ops.append({'t': 'dimpts', 'h': e.dxf.handle, 'p1': new[0], 'p2': new[1]})
json.dump(ops, open('ops/km2.json', 'w', encoding='utf-8'), ensure_ascii=False)
from collections import Counter
print(Counter(o['t'] for o in ops))
