# types: geometry (section, levels) + As from LIRA CSV «Арматура в стержнях» -> Км marks
import json, math, sys, collections
sys.path.insert(0, r'..'); import csvread
from b3plan import C
GEO = {g['id']: g for g in json.load(open('geo.json', encoding='utf-8'))}
A28 = math.pi * 2.8 ** 2 / 4
def merge(lv):
    lv = [list(x) for x in lv]; i = 1
    while i < len(lv):
        clear = (lv[i][0] - lv[i][1]) - lv[i - 1][0]
        if clear < 600:
            lv[i] = [lv[i][0], lv[i][0] - (lv[i - 1][0] - lv[i - 1][1])]; del lv[i - 1]
        else: i += 1
    return lv
LAYOUTS = {900: [(5, 6), (6, 6), (6, 7)], 700: [(4, 4), (5, 5), (6, 6)], 500: [(3, 3), (4, 4), (5, 5)]}
def nbars(nb, nh): return 2 * nb + 2 * nh - 4
def pick(b, need):
    for nb, nh in LAYOUTS[b]:
        if nbars(nb, nh) * A28 >= need - 1e-6: return nb, nh
    raise SystemExit('As too big %s %s' % (b, need))
if __name__ == '__main__':
    g, rows = csvread.load(sys.argv[1])
    byel = collections.defaultdict(list)
    for r in rows:
        if r['typ'] != '*': byel[r['el']].append(r)
    res = []
    for c in C:
        G = GEO[c['id']]
        rr = [r for e in G['els'] for r in byel.get(e, [])]
        if not rr: print('NO CSV ROWS', c['id'], G['els']); continue
        asum = max(sum(r['au']) + sum(r['as_']) for r in rr)
        asw = max(max(r['asw']) for r in rr)
        msg = sorted({r['msg'] for r in rr if r['msg']})
        res.append(dict(c, asum=round(asum, 2), asw=round(asw, 2), lv=merge(G['lv']), base=G['base'], msg=msg, grp=sorted({r['g'] for r in rr})))
    for r in res: print(r['id'], r['bx'], r['by'], r['lv'], 'As=%.2f n28=%.1f Asw=%.2f' % (r['asum'], r['asum'] / A28, r['asw']), r['msg'][:2], r['grp'])
    json.dump(res, open('as.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print({k: v[:90] for k, v in g.items()})
