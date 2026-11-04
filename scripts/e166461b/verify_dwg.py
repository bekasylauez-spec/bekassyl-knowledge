# per-zone check on the REAL drawing (live.dxf + geom.txt) for 3.3–3.6 (Bekassyl 04.11: «барлығын жеке жеке тексер»):
#  1) the zone has a «200xN» spacing dim with ext points at its first/last bar, dim line ≤ 1100 from its bar ends;
#  2) every dim text of the sheet keeps clear of the bar lines and sits at its own segment (≤ 700 along, ≤ 1500 off);
#  3) the zone has its position callout (FD note) in the map.
import json, os, sys, re
import ezdxf, logging
logging.disable(logging.CRITICAL)
from shapely.geometry import LineString as LS, box
sys.path.insert(0, '.')
import gen_fm as G
F = json.load(open('arm/fm_final.json'))
m = json.load(open(os.environ['TEMP'] + '/gx_map.json', encoding='utf-8-sig'))
d = ezdxf.readfile('w/live.dxf'); ms = d.modelspace()
txt = {}
for ln in open('w/geom.txt', encoding='utf-8-sig'):
    f = ln.rstrip('\r\n').split('|')
    if f[0] == 'T' and len(f) > 7: txt.setdefault(f[1], []).append(box(*[float(v) for v in f[3:7]]))
dims = [e for e in ms if e.dxftype() == 'DIMENSION']
bars = [LS([(e.dxf.start.x, e.dxf.start.y), (e.dxf.end.x, e.dxf.end.y)]) for e in ms if e.dxftype() == 'LINE' and e.dxf.layer.startswith('диам')]
bad = []
for sh, key in (('3.3', 'bot_x'), ('3.4', 'top_x'), ('3.5', 'bot_y'), ('3.6', 'top_y')):
    fx, X, Y = G.origin(sh); axis = key.split('_')[1]
    W = box(fx, 455939, fx + 59400, 497939)
    sd = [e for e in dims if W.contains(box(e.dxf.defpoint.x - 1, e.dxf.defpoint.y - 1, e.dxf.defpoint.x + 1, e.dxf.defpoint.y + 1))]
    sb = [b for b in bars if b.intersects(W)]
    zs = F[key] + F.get(key + '_3', [])
    for k, z in enumerate(zs):
        if z['n'] > 1:
            ok = False
            for e in sd:
                p1, p2 = e.dxf.defpoint2, e.dxf.defpoint3
                if axis == 'x':
                    a, b = sorted((p1.y - Y, p2.y - Y)); line = e.dxf.defpoint.x - X; ends = (z['s0'], z['s1'])
                else:
                    a, b = sorted((p1.x - X, p2.x - X)); line = e.dxf.defpoint.y - Y; ends = (z['s0'], z['s1'])
                if abs(a - z['p0']) < 1 and abs(b - z['p1']) < 1 and min(abs(line - q) for q in ends) <= 1100: ok = True; break
            if not ok: bad.append('%s поз.%s: нет шага у своих стержней' % (sh, z['pos']))
        if 'FD%s_%d' % (sh, k) not in m: bad.append('%s поз.%s: нет выноски' % (sh, z['pos']))
    for e in sd:
        T = txt.get(e.dxf.handle, [])
        if not T: continue
        t = T[0]
        hits = [b for b in sb if b.intersects(t.buffer(-10))]
        if hits: bad.append('%s размер %s: текст на стержне @(%d,%d) #%s' % (sh, e.dxf.get('text') or round(e.get_measurement()), t.centroid.x - fx, t.centroid.y - 455939, e.dxf.handle))
        p1, p2 = e.dxf.defpoint2, e.dxf.defpoint3
        vert = abs((e.dxf.get('angle', 0) or 0) % 180 - 90) < 1 or (abs(p1.x - p2.x) < 1 and abs(p1.y - p2.y) > 1)
        c = t.centroid
        if vert:
            a, b = sorted((p1.y, p2.y)); along = max(a - c.y, c.y - b, 0); off = abs(c.x - e.dxf.defpoint.x)
        else:
            a, b = sorted((p1.x, p2.x)); along = max(a - c.x, c.x - b, 0); off = abs(c.y - e.dxf.defpoint.y)
        if along > 700 or off > 1500: bad.append('%s размер %s: текст далеко от участка @(%d,%d) #%s' % (sh, e.dxf.get('text') or round(e.get_measurement()), t.centroid.x - fx, t.centroid.y - 455939, e.dxf.handle))
for b in bad: print(b)
print('ИТОГО замечаний:', len(bad))
