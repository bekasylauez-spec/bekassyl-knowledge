# every dop zone must have its «200xN» spacing dim with the dim line ≤ 900 from its own bar end (Bekassyl 04.11)
import json, sys
sys.path.insert(0, '.')
import gen_fm as G
F = json.load(open('arm/fm_final.json')); ops = json.load(open('ops/fm4.json', encoding='utf-8'))
dims = [o for o in ops if o.get('t') == 'dim']
bad = 0
for sh, key in (('3.3', 'bot_x'), ('3.4', 'top_x'), ('3.5', 'bot_y'), ('3.6', 'top_y')):
    fx, X, Y = G.origin(sh); axis = key.split('_')[1]
    for z in F[key] + F.get(key + '_3', []):
        if z['n'] < 2: continue
        P = lambda s_, p: (X + s_, Y + p) if axis == 'x' else (X + p, Y + s_)
        ok = False
        for d in dims:
            k = 1 if axis == 'x' else 0
            a, b = sorted((d['p1'][k], d['p2'][k]))
            u, v = sorted((P(0, z['p0'])[k], P(0, z['p1'])[k]))
            if abs(a - u) > 1 or abs(b - v) > 1: continue
            line = d['dl'][0] if axis == 'x' else d['dl'][1]
            ends = (P(z['s0'], 0)[0], P(z['s1'], 0)[0]) if axis == 'x' else (P(z['s0'], 0)[1], P(z['s1'], 0)[1])
            if min(abs(line - e) for e in ends) <= 1100: ok = True; break
        if not ok: bad += 1; print('NO SPACING NEAR', sh, 'pos', z['pos'])
print('zones without own spacing:', bad)
