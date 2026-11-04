# Фм-1 additional reinforcement zones from LIRA As (cm2/m) — vault 02_Фундамент/Фундаментная плита.md:
# base mesh by thickness/As (analog: Ø16 @200 both faces), dop bars at @200 between base bars (same level),
# a zone needs >= 4 cells, As for a cell = mean of two neighbouring cells perpendicular to the bar direction,
# dop Ø from the deficit (Ø10…Ø32), zone = rectangle of the connected area, bars run past the zone on anchorage.
import json, math, sys
sys.path.insert(0, '.')
import model as M
from shapely.geometry import box, Point
from shapely.ops import unary_union

C = json.load(open('arm/fm_cells.json'))
BARS = [(10, 3.93), (12, 5.65), (14, 7.70), (16, 10.05), (18, 12.72), (20, 15.71), (22, 19.01), (25, 24.54), (28, 30.79), (32, 40.21)]
BASE_D = 16; BASE_A = 10.05                # analog Фм-1: поз.1 Ø16 A500С ш.200
FM = box(*M.FM)
KEYS = [('bot_x', 0, 'x'), ('top_x', 1, 'x'), ('bot_y', 2, 'y'), ('top_y', 3, 'y')]   # AS1 bot X, AS2 top X, AS3 bot Y, AS4 top Y


def neighbours(c, axis):
    # cells touching c across its edges perpendicular to the bar direction (bars along x -> neighbours above/below)
    out = []
    for o in C:
        if o is c: continue
        if axis == 'x':
            if (abs(o['y0'] - c['y1']) < 5 or abs(o['y1'] - c['y0']) < 5) and min(o['x1'], c['x1']) - max(o['x0'], c['x0']) > 50: out.append(o)
        else:
            if (abs(o['x0'] - c['x1']) < 5 or abs(o['x1'] - c['x0']) < 5) and min(o['y1'], c['y1']) - max(o['y0'], c['y0']) > 50: out.append(o)
    return out


def bar_for(need):
    for d, a in BARS:
        if a >= need - 1e-6: return d, a
    return None


def zones(k, axis):
    eff = {}
    for c in C:
        nb = neighbours(c, axis)
        v = c['As'][k]
        eff[c['id']] = max([(v + o['As'][k]) / 2 for o in nb] or [v])
    hot = [c for c in C if eff[c['id']] > BASE_A + 0.01]
    # connected components (touching cells)
    rect = {c['id']: box(c['x0'] - 3, c['y0'] - 3, c['x1'] + 3, c['y1'] + 3) for c in hot}
    left = set(rect); comps = []
    while left:
        s = left.pop(); comp = {s}; st = [s]
        while st:
            a = st.pop()
            for b in list(left):
                if rect[a].intersects(rect[b]): left.discard(b); comp.add(b); st.append(b)
        comps.append(comp)
    res = []
    for comp in comps:
        if len(comp) < 4: continue
        cc = [c for c in hot if c['id'] in comp]
        req = max(eff[c['id']] for c in cc)
        x0 = min(c['x0'] for c in cc); x1 = max(c['x1'] for c in cc); y0 = min(c['y0'] for c in cc); y1 = max(c['y1'] for c in cc)
        bf = bar_for(req - BASE_A)
        res.append(dict(x0=round(x0), y0=round(y0), x1=round(x1), y1=round(y1), req=round(req, 2), ncell=len(cc),
                        area=round(sum((c['x1'] - c['x0']) * (c['y1'] - c['y0']) for c in cc) / 1e6, 2), d=bf[0] if bf else None))
    tot = sum((c['x1'] - c['x0']) * (c['y1'] - c['y0']) for c in C) / 1e6
    hot_area = sum((c['x1'] - c['x0']) * (c['y1'] - c['y0']) for c in hot) / 1e6
    return res, hot_area / tot


if __name__ == '__main__':
    out = {}
    for key, k, axis in KEYS:
        res, frac = zones(k, axis)
        out[key] = res
        print('==', key, 'zones', len(res), 'hot area %.0f%%' % (frac * 100))
        for r in sorted(res, key=lambda r: -r['req']): print('  ', r)
    json.dump(out, open('arm/fm_zones.json', 'w'), indent=1, ensure_ascii=False)
