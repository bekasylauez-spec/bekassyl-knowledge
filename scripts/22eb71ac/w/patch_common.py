# checklist №28/30 rows, №32 text avoids axis/level lines, frame A3 at any scale, notes scaled to the sheet
import sys
for p in ('common.py', 'gen1.py'):
    s = open(p, encoding='utf-8').read()
    # --- dim(): avoid axis / level lines crossing the text
    a = "        k = dict(t='dim', h=SRC['dim'], p1=p1, p2=p2, dl=dl, rot=rot, dscale=s.sc)\n        if tx: k['tx'] = s.P(tx[1], tx[0]) if vert else s.P(tx[0], tx[1])\n        return add(**k)"
    b = ("        if tx is None:                                    # №32: no axis/level line through the text\n"
         "            av = getattr(s, 'avoid_y' if vert else 'avoid_x', [])\n"
         "            th = 2.5 * s.sc; lo, hi = min(a, b), max(a, b); mid = (a + b) / 2\n"
         "            w = len(str(int(round(hi - lo)))) * 0.72 * th\n"
         "            hit = [v for v in av if abs(v - mid) < w / 2 + 0.3 * th]\n"
         "            if hit and hi - lo >= 7 * s.sc:\n"
         "                v = hit[0]; right = (hi - v) >= (v - lo)\n"
         "                along = v + (w / 2 + 0.5 * th) if right else v - (w / 2 + 0.5 * th)\n"
         "                tx = (along, off[1] - 0.9 * th if vert else off[1] + 0.9 * th)\n"
         "        k = dict(t='dim', h=SRC['dim'], p1=p1, p2=p2, dl=dl, rot=rot, dscale=s.sc)\n"
         "        if tx: k['tx'] = s.P(tx[1], tx[0]) if vert else s.P(tx[0], tx[1])\n"
         "        return add(**k)")
    assert a in s, (p, 'dim'); s = s.replace(a, b)
    # --- Sheet init: avoid lists default to plan axes
    a = "    def __init__(s, ox, oy, sc): s.ox, s.oy, s.sc = ox, oy, sc"
    b = "    def __init__(s, ox, oy, sc): s.ox, s.oy, s.sc = ox, oy, sc; s.avoid_x = list(AX.values()); s.avoid_y = list(AY.values())"
    assert a in s, (p, 'init'); s = s.replace(a, b)
    # --- plan rows 10 mm on paper from the contour, then +10 mm (checklist №28/30)
    a = "    s.chain(xs, y0, y0 - 1175); s.dim(AX['1'], AX['3'], (y0, y0 - 1975))\n    s.chain(ys, x0, x0 - 1175, vert=True); s.dim(AY['А'], AY['Д'], (x0, x0 - 1975), vert=True)"
    b = "    R = 10 * s.sc                                         # №28/30: first row 10 mm from the contour, next +10 mm\n    s.chain(xs, y0, y0 - R); s.dim(AX['1'], AX['3'], (y0, y0 - 2 * R))\n    s.chain(ys, x0, x0 - R, vert=True); s.dim(AY['А'], AY['Д'], (x0, x0 - 2 * R), vert=True)"
    if a in s: s = s.replace(a, b)
    s = s.replace("    for k, x in AX.items(): s.axis(pre + 'ax' + k, k, (x, y1 + 700), (x, y0 - 2475))\n    for k, y in AY.items(): s.axis(pre + 'ay' + k, k, (x1 + 700, y), (x0 - 2475, y))",
                  "    for k, x in AX.items(): s.axis(pre + 'ax' + k, k, (x, y1 + 700), (x, y0 - 2500))\n    for k, y in AY.items(): s.axis(pre + 'ay' + k, k, (x1 + 700, y), (x0 - 2500, y))")
    # --- frame: A3 at any scale (SPDS format resized by DbEntity.Scale)
    a = "    add(t='clone', h=src, base=list(so), to=[fx, fy], tag='frame' + num)\n    f = sc / 100"
    b = "    add(t='clone', h=src, base=list(so), to=[fx, fy], tag='frame' + num)\n    if fmt == 'A3' and sc != 100: add(t='mcscale', h='frame' + num, v=sc)\n    f = sc / 100"
    if a in s: s = s.replace(a, b)
    # --- notes scaled to the sheet
    a = "def notes(fx, fy, top, lines):"
    b = "def notes(fx, fy, top, lines, sc=100):"
    if a in s: s = s.replace(a, b)
    a = "    add(t='mtext', at=[fx + 23000, fy + 500 + 5712 + 250], h=250, w=18500, att=7, style='Isocpeur', layer='О_Формат', s=txt)"
    b = "    f = sc / 100.0\n    add(t='mtext', at=[fx + 23000 * f, fy + (500 + 5712 + 250) * f], h=250 * f, w=18500 * f, att=7, style='Isocpeur', layer='О_Формат', s=txt)"
    if a in s: s = s.replace(a, b)
    open(p, 'w', encoding='utf-8').write(s)
    print(p, 'ok')
