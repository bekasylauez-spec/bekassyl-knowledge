# Find the sheet frame (outer rectangle) around each stamp "Лист N" anchor in uz.dxf; print plot windows.
import sys, ezdxf, re
doc = ezdxf.readfile(sys.argv[1]); msp = doc.modelspace()
anch = [(804165, '1'), (846165, '2'), (888165, '3'), (917865, '4'), (1155165, '5'), (1392965, '6'), (1630765, '7'), (1690665, '8'), (1927965, '9'), (2165765, '10'), (2403565, '11'), (2581765, '12'), (2819565, '13')]
rects = []
for e in msp.query('LWPOLYLINE'):
    p = [(x, y) for x, y, *_ in e.get_points()]
    if len(p) in (4, 5) and (e.closed or len(p) == 5):
        xs = [q[0] for q in p]; ys = [q[1] for q in p]
        w, h = max(xs) - min(xs), max(ys) - min(ys)
        if w > 20000 and h > 10000: rects.append((min(xs), min(ys), max(xs), max(ys)))
# texts with "Лист" near anchors give y
for x0, n in anch:
    best = None
    for r in rects:
        if r[0] - 1 <= x0 <= r[2] + 1:
            a = (r[2] - r[0]) * (r[3] - r[1])
            if best is None or a > best[0]: best = (a, r)
    print(n, best[1] if best else None)
