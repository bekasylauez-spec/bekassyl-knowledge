# Check dop zones against LIRA: provided (base + dop) vs required (averaged) As at every raster point; draw plots.
import json, sys
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt, matplotlib.patches as pa
from design import SLABS, slab_geom, raster, required, as200, BASE
Z = json.load(open(sys.argv[1] if len(sys.argv) > 1 else 'zones3.json'))
names = ['As1 X низ', 'As2 X верх', 'As3 Y низ', 'As4 Y верх']
col = {10: '#1f77b4', 12: '#2ca02c', 14: '#ff7f0e', 16: '#d62728', 18: '#9467bd', 20: '#000000'}
for k in SLABS:
    xs, ys, A, inside = raster(k)
    X, Y = np.meshgrid(xs, ys)
    fig, axs = plt.subplots(2, 2, figsize=(24, 22))
    for f in range(4):
        R = required(A, f); prov = np.where(inside, BASE, np.nan); cnt = np.zeros(R.shape)
        for z in Z[k]:
            if z['f'] != f: continue
            for p in z['pos']:
                if f in (0, 1): m = (np.abs(Y - p) <= 100) & (X >= z['L0']) & (X <= z['L1'])
                else: m = (np.abs(X - p) <= 100) & (Y >= z['L0']) & (Y <= z['L1'])
                prov = np.where(m, prov + as200(z['d']), prov); cnt += m
        short = inside & (R > prov + 0.05)
        dbl = (cnt > 1).sum()
        print(k, names[f], 'short pts', int(short.sum()), 'max short %.2f' % float(np.nanmax(np.where(short, R - prov, 0))), 'double-cover pts', int(dbl))
        ax = axs.flat[f]
        ax.imshow(np.where(inside, R, np.nan), origin='lower', extent=(xs[0] - 50, xs[-1] + 50, ys[0] - 50, ys[-1] + 50), cmap='Greys', vmin=0, vmax=14)
        ax.contour(X, Y, np.where(inside, R, 0), levels=[BASE], colors='m', linewidths=0.6)
        sy, sx = np.nonzero(short); ax.plot(xs[sx], ys[sy], 'r.', ms=2)
        for z in Z[k]:
            if z['f'] != f: continue
            if f in (0, 1): x0, x1, y0, y1 = z['L0'], z['L1'], z['pos'][0], z['pos'][-1]
            else: y0, y1, x0, x1 = z['L0'], z['L1'], z['pos'][0], z['pos'][-1]
            ax.add_patch(pa.Rectangle((x0, y0), max(x1 - x0, 50), max(y1 - y0, 50), fill=False, ec=col[z['d']], lw=1.2))
            ax.text((x0 + x1) / 2, (y0 + y1) / 2, 'Ø%d' % z['d'], fontsize=6, color=col[z['d']], ha='center')
        bx = slab_geom(k)
        for geom in [r for p in (bx.geoms if hasattr(bx,'geoms') else [bx]) for r in [p.exterior]+list(p.interiors)]:
            gx, gy = geom.xy; ax.plot(gx, gy, 'k-', lw=0.8)
        ax.set_title(names[f]); ax.set_aspect('equal')
    plt.tight_layout(); plt.savefig('zc_%s.png' % k, dpi=70)
