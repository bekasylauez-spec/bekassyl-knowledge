# per sheet: vertical axes (construction lines), piece outlines (x ranges) in the elevation, plan pieces
import sys, json; sys.path.insert(0, 'wl'); from common import *
def probe(X0, W=59400, H=42000):
    R = listwin(X0, 455939, W, H, None)
    for r in R:
        if r['t'] == 'INSERT' and r['x1'] - r['x0'] > 15000 and r['x0'] < 12000:
            gx.run([{'t': 'explode', 'h': r['h']}], 'ex'); R = listwin(X0, 455939, W, H, None); break
    ax = sorted(round((r['x0'] + r['x1']) / 2) for r in R if r['t'] == 'SPDSCONSTRUCTIONLINE' and r['y1'] - r['y0'] > 3000)
    pcs = sorted(set((round(r['x0']), round(r['x1'])) for r in R if r['t'] == 'LWPOLYLINE' and len(r['sp']) == 4 and r['y1'] - r['y0'] > 2000 and r['x1'] - r['x0'] < 5000))
    return R, ax, pcs
if __name__ == '__main__':
    for X0 in [float(v) for v in sys.argv[1].split(',')]:
        R, ax, pcs = probe(X0)
        print(int(X0), 'axes', ax); print('  pieces', pcs)
