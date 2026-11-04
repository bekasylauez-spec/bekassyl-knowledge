# Read LIRA mosaic PNG -> required As per cell, mapped to KZh coords (mm)
import sys, json, numpy as np
from PIL import Image
def legend(im):
    a = np.asarray(im.convert('RGB')).astype(int)
    row = a[20]                      # legend bar row
    xs = [x for x in range(60, 1215) if not (row[x] == [255, 255, 255]).all() and not (row[x] < 60).all()]
    segs = []; cur = None
    for x in xs:
        c = tuple(row[x])
        if cur and sum(abs(c[i] - cur[1][i]) for i in range(3)) < 30 and x - cur[0][-1] <= 2: cur[0].append(x)
        else:
            if cur: segs.append(cur)
            cur = ([x], c)
    if cur: segs.append(cur)
    segs = [s for s in segs if len(s[0]) > 40]
    return [(s[1], min(s[0]), max(s[0])) for s in segs]
def analyse(path, bins):
    im = Image.open(path); a = np.asarray(im.convert('RGB')).astype(int)
    leg = legend(im)
    assert len(leg) == len(bins), (len(leg), bins)
    # grid lines: green (0,128,0)-ish
    g = (abs(a[:, :, 0] - 0) < 40) & (abs(a[:, :, 1] - 128) < 40) & (abs(a[:, :, 2] - 0) < 40)
    colx = np.where(g[150:1000].sum(axis=0) > 300)[0]; rowy = np.where(g[:, 250:1050].sum(axis=1) > 300)[0]
    def merge(v):
        out = []
        for x in v:
            if out and x - out[-1][-1] <= 2: out[-1].append(x)
            else: out.append([x])
        return [int(np.mean(o)) for o in out]
    colx = merge(colx); rowy = [y + 0 for y in merge(rowy)]
    cells = []
    for i in range(len(colx) - 1):
        for j in range(len(rowy) - 1):
            cx = (colx[i] + colx[i + 1]) // 2; cy = (rowy[j] + rowy[j + 1]) // 2
            c = a[cy, cx]
            if (c > 245).all(): continue          # opening
            d = [sum(abs(c[k] - L[0][k]) for k in range(3)) for L in leg]
            k = int(np.argmin(d))
            cells.append((colx[i], rowy[j], colx[i + 1], rowy[j + 1], bins[k], k))
    return cells, colx, rowy
if __name__ == '__main__':
    p = sys.argv[1]; bins = [float(b) for b in sys.argv[2].split(',')]
    cells, cx, cy = analyse(p, bins)
    print(len(cells), 'cells; cols', len(cx), cx[:3], cx[-3:], 'rows', len(cy), cy[:3], cy[-3:])
    import collections; print(collections.Counter(c[4] for c in cells))
