# group columns into Км types: section, levels, bars, hoop mode (from Asw)
import json, math, collections
A28 = math.pi * 2.8 ** 2 / 4
AS = json.load(open('as.json', encoding='utf-8'))
NOTES0 = json.load(open(r'..\coltypes.json', encoding='utf-8'))[0]['notes']
def hoop(asw):                       # LIRA Asw (A240, cm2/m) -> A500 need; Ø10, 4 legs: s200 15.7, s100 31.4, s80 39.3
    req = asw * 170.0 / 300.0
    return 'std' if req <= 15.7 else ('100' if req <= 31.4 else '80')
def bars(c):
    if c['bx'] == 900: return 5, 6
    if c['bx'] == 700: return 4, 4
    return (5, 5) if c['kind'] == 'upper' else (4, 4)
G = collections.OrderedDict()
for c in AS:
    nb, nh = bars(c)
    lv = tuple(tuple(x) for x in c['lv'])
    key = (c['bx'], c['by'], lv, c['base'], nb, nh, hoop(c['asw']), c['kind'] == 'upper')
    G.setdefault(key, []).append(c)
order = sorted(G, key=lambda k: (-k[0], k[7], {'std': 0, '100': 1, '80': 2}[k[6]] if k[0] != 900 else 0, -len(G[k])))
order = sorted(G, key=lambda k: (-k[0], k[7], -len(G[k]) if k[0] == 700 else 0, list(G).index(k)))
TY = []; assign = {}
for i, k in enumerate(order, 1):
    bx, by, lv, base, nb, nh, hm, up = k
    cs = G[k]; mk = 'Км-%d' % i
    ns = 2 * nb + 2 * nh - 4
    asmax = max(c['asum'] for c in cs); aswmax = max(c['asw'] for c in cs)
    T = dict(mark=mk, b=bx, h=by, nb=nb, nh=nh, ns=ns, levels=[l for l, _ in lv], beams=[h for _, h in lv],
             df=1200 if up else 1700, base=base, vp='выпуски из колонны/ригеля' if up else 'см. фундамент', n=len(cs),
             hoop=hm, As_lira=asmax, As_prov=round(ns * A28, 2), Asw_lira=aswmax, ids=[c['id'] for c in cs], notes=NOTES0)
    assert T['As_prov'] >= asmax
    TY.append(T)
    for c in cs: assign[c['id']] = mk
if __name__ == '__main__':
    for T in TY:
        print(T['mark'], '%dx%d' % (T['b'], T['h']), T['levels'], T['beams'], 'base', T['base'], '%dØ28' % T['ns'], 'hoop', T['hoop'],
              'As %.1f/%.1f' % (T['As_lira'], T['As_prov']), 'Asw', T['Asw_lira'], 'n', T['n'], T['ids'][:6])
    print('total', sum(T['n'] for T in TY))
    json.dump(TY, open('types_b3.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    json.dump(assign, open('assign.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
