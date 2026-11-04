# post-process fm_design.json: zones of one face/direction never share a bar (vault 04.11 «арматура бірінің үстіне бірі келмейді»):
# the weaker zone is cut around the stronger one with a 50 mm gap; >Ø32 demand -> 3rd mesh zone (vault: foundation only).
import json, math
R = json.load(open('arm/fm_design.json'))
AREA = {10: 3.93, 12: 5.65, 14: 7.70, 16: 10.05, 18: 12.72, 20: 15.71, 22: 19.01, 25: 24.54, 28: 30.79, 32: 40.21}
BASE = 10.05
def strength(z): return (z['d'], z['req'])
def lines(z): return set(range(int(z['p0']), int(z['p1']) + 1, 200))
out = {}
for key, zs in R.items():
    zs = [dict(z) for z in zs]
    changed = True
    while changed:
        changed = False
        zs.sort(key=strength, reverse=True)
        for i, A in enumerate(zs):
            for B in zs[i + 1:]:
                if not (min(A['p1'], B['p1']) >= max(A['p0'], B['p0']) and min(A['s1'], B['s1']) > max(A['s0'], B['s0']) - 50): continue
                # B weaker: try trimming along the bar
                parts = []
                if B['s0'] < A['s0'] - 50 - 1000: parts.append(dict(B, s1=A['s0'] - 50))
                if B['s1'] > A['s1'] + 50 + 1000: parts.append(dict(B, s0=A['s1'] + 50))
                # lines of B outside A's line range keep their full length
                if B['p0'] < A['p0']: parts.append(dict(B, p1=A['p0'] - 200))
                if B['p1'] > A['p1']: parts.append(dict(B, p0=A['p1'] + 200))
                # the trimmed-in-length parts apply only to the shared lines
                fixed = []
                for q in parts:
                    if q['p0'] == B['p0'] and q['p1'] == B['p1'] and (q['s0'] != B['s0'] or q['s1'] != B['s1']):
                        q = dict(q, p0=max(B['p0'], A['p0']), p1=min(B['p1'], A['p1']))
                    if q['p1'] >= q['p0']:
                        q['n'] = int((q['p1'] - q['p0']) / 200) + 1; fixed.append(q)
                zs.remove(B); zs += fixed; changed = True; break
            if changed: break
    third = []
    for z in zs:
        if z.get('flag'):
            need = z['req'] - BASE - AREA[32]
            d = next(dd for dd, a in sorted(AREA.items()) if a >= need)
            third.append(dict(z, d=d, flag='3rd', req=round(need, 2)))
            z['flag'] = None
    out[key] = sorted(zs, key=lambda z: (z['p0'], z['s0']))
    out[key + '_3'] = third
    print(key, len(zs), 'third', [(t['d'], t['n'], t['s1'] - t['s0']) for t in third])
# check: no two zones share a bar position
for key in ('bot_x', 'top_x', 'bot_y', 'top_y'):
    zs = out[key]; bad = 0
    for i, A in enumerate(zs):
        for B in zs[i + 1:]:
            if lines(A) & lines(B) and min(A['s1'], B['s1']) > max(A['s0'], B['s0']) - 49: bad += 1
    print('overlaps', key, bad)
json.dump(out, open('arm/fm_final.json', 'w'), indent=1)
