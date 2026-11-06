# per plan column: LIRA elements + levels/beams (marks rel. to column bottom) from the LIRA txt
import re, json, collections, sys
TXT = r"C:/Users/Admin/AppData/Local/Temp/claude/210ab68cad67e8c1/6399190a-f172-4888-a7c9-e3d967ee3eb0/scratchpad/b3/lira/model.txt"
from b3plan import C
T = open(TXT, encoding='utf-8-sig').read()
docs = {}
for m in re.finditer(r'\(\s*(\d+)\s*/(.*?)\)', T, re.S): docs.setdefault(int(m.group(1)), m.group(2))
el = [list(map(int, r.split())) for r in docs[1].split('/') if r.strip()]
xyz = [list(map(float, r.split()[:3])) for r in docs[4].split('/') if r.strip()]
S0 = {}
for r in docs[3].split('/'):
    p = r.split()
    if len(p) >= 5 and p[1] == 'S0': S0[int(p[0])] = (float(p[3]), float(p[4]))
COL = {14, 15, 18, 19}
nb = collections.defaultdict(list)
for i, r in enumerate(el, 1):
    if r[0] == 10 and len(r) == 4:
        for n in r[2:]: nb[n].append(i)
def k2(p): return (round(p[0], 2), round(p[1], 2))
colel = collections.defaultdict(list)          # (x,y) -> [(el, st, z0, z1, top node)]
for i, r in enumerate(el, 1):
    if r[0] == 10 and len(r) == 4 and r[1] in COL:
        a, b = xyz[r[2] - 1], xyz[r[3] - 1]
        if abs(a[0] - b[0]) < 1e-3 and abs(a[1] - b[1]) < 1e-3:
            lo, hi = (r[2], r[3]) if a[2] < b[2] else (r[3], r[2])
            colel[k2(a)].append((i, r[1], min(a[2], b[2]), max(a[2], b[2]), hi))
def beams_at(n):
    hs = []
    for j in nb[n]:
        rr = el[j - 1]; p, q = xyz[rr[2] - 1], xyz[rr[3] - 1]
        if abs(p[2] - q[2]) < 1e-3 and rr[1] in S0 and rr[1] not in COL: hs.append(S0[rr[1]][1] * 10)
    return max(hs) if hs else 0
OUT = []
for c in C:
    key = tuple(c['lira'])
    es = colel[key]
    if c['kind'] == 'upper': es = [e for e in es if e[2] >= 6.9]
    else: es = [e for e in es if e[2] >= -0.06 and e[3] <= 6.96]
    es.sort(key=lambda e: e[2])
    base = round((es[0][2] + 0.05) * 1000)
    if c['kind'] != 'upper': base = 0
    lv = []
    for e in es:
        h = beams_at(e[4])
        if h: lv.append([round((e[3] + 0.05) * 1000) - base, int(h)])
    st = sorted({e[1] for e in es})
    OUT.append(dict(id=c['id'], els=[e[0] for e in es], st=st, base=base, lv=lv, z=[es[0][2], es[-1][3]]))
if __name__ == '__main__':
    for o in OUT: print(o['id'], o['st'], o['base'], o['lv'], o['z'], len(o['els']))
    json.dump(OUT, open('geo.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
