"""Помещение обезвоживания: geometry (mm, axis 1/А origin)"""
import math
from shapely.geometry import box, Point, LineString
from shapely.ops import unary_union
AX = [0, 3250, 7750, 12250, 16750, 20000, 26000, 32000]
AY = [0, 6000, 12000]
PX, PY = 1000, 1500          # pad half sizes (2000 x 3000)
BW = 350                     # foundation beam width
def pads():
    return [box(x-PX, y-PY, x+PX, y+PY) for x in AX for y in AY]
def beams():
    B = [box(AX[0], y-BW/2, AX[-1], y+BW/2) for y in AY]
    B += [box(x-BW/2, AY[0], x+BW/2, AY[-1]) for x in AX]
    return B
def found():
    return unary_union(pads()+beams())
def piles():
    F = []   # under foundations
    for x in AX:
        for y in AY:
            for dx in (-1000, 0, 1000):
                for dy in (-1500, -500, 500, 1500):
                    F.append((x+dx, y+dy))
    for y in AY:
        for a, b in zip(AX, AX[1:]):
            g0, g1 = a+PX, b-PX; n = math.ceil((g1-g0)/1000)-1
            F += [(g0+(g1-g0)*k/(n+1), y) for k in range(1, n+1)]
    for x in AX:
        for a, b in zip(AY, AY[1:]):
            g0, g1 = a+PY, b-PY; n = math.ceil((g1-g0)/1000)-1
            F += [(x, g0+(g1-g0)*k/(n+1)) for k in range(1, n+1)]
    F = sorted(set((round(x), round(y)) for x, y in F))
    S = []   # under slab on grade: per bay the densest grid (step <= 2000) keeping >= 900 from foundation piles
    fp = found().buffer(250)
    def ok(p): return min(math.dist(p, q) for q in F) >= 900 and not fp.contains(Point(p))
    for a, b in zip(AX, AX[1:]):
        for c, d in zip(AY, AY[1:]):
            best = []
            for nx in range(math.ceil((b-a)/2000)-1, 0, -1):
                for ny in range(math.ceil((d-c)/2000)-1, 0, -1):
                    pts = [(round(a+(b-a)*i/(nx+1)), round(c+(d-c)*j/(ny+1))) for i in range(1, nx+1) for j in range(1, ny+1)]
                    if all(ok(p) for p in pts) and len(pts) > len(best): best = pts
            S += best
    return F, S
if __name__ == '__main__':
    F, S = piles(); print(len(F), len(S))
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(20, 9))
    g = found()
    for poly in (g.geoms if hasattr(g, 'geoms') else [g]):
        ax.plot(*poly.exterior.xy, 'k', lw=.8)
        for r in poly.interiors: ax.plot(*r.xy, 'k', lw=.8)
    for p in F: ax.add_patch(plt.Circle(p, 250, fill=False, color='b'))
    for p in S: ax.add_patch(plt.Circle(p, 250, fill=False, color='r'))
    ax.set_aspect('equal'); fig.savefig('w/piles.png', dpi=70, bbox_inches='tight')
