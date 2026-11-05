# audit of note leader ticks: every leader end (tick) must sit on a bar line; no tick where a leader/shelf only crosses a bar
import sys, collections; sys.path.insert(0, 'wl'); from common import *
from notes import notes
def bars(R):
    B = []
    for r in R:
        if r['t'] in ('LINE', 'LWPOLYLINE') and r['lay'].lower().startswith('диам'):
            for (x1, y1), (x2, y2) in zip(r['sp'], r['sp'][1:]): B.append((x1, y1, x2, y2, r['lay']))
    return B
def on_bar(p, B, tol=15):
    x, y = p
    for x1, y1, x2, y2, lay in B:
        if abs(x1 - x2) < 1 and abs(x - x1) < tol and min(y1, y2) - tol <= y <= max(y1, y2) + tol: return lay
        if abs(y1 - y2) < 1 and abs(y - y1) < tol and min(x1, x2) - tol <= x <= max(x1, x2) + tol: return lay
    return None
def audit(SX, H, ylo=0, show=True):
    R = listwin(SX, 455939, 59400, H, None); B = bars(R); bad = []
    for n in notes(SX, 455939, 59400, H):
        o = n['pts'][0]
        if o[1] < ylo or n['t'] not in ('SPDSNOTEPOSITION',) and False: continue
        for j, p in enumerate(n['pts'][1:], 1):
            lay = on_bar(p, B)
            onshelf = abs(p[1] - o[1]) < 30
            if lay is None or onshelf: bad.append((n['h'], n['l1'], j, (round(p[0]), round(p[1])), lay, onshelf))
    if show:
        for b in bad: print(b)
    return bad, B
if __name__ == '__main__':
    bad, _ = audit(float(sys.argv[1]), float(sys.argv[2]) if len(sys.argv) > 2 else 42000)
    print('BAD', len(bad))
