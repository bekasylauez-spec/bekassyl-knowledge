# Braces: LIRA (В_109_v3_КМ.lir) vs model (members.tsv), both directions, grouped by plane / bay.
import struct, math, sys
from collections import defaultdict, Counter
LIR = r"D:\Бекасыл КЖ КМ\Завод_В109_КМ\_авто\lira\В_109_v3_КМ.lir"
MEM = r"D:\Бекасыл КЖ КМ\Завод_В109_КМ\_авто\revit\members.tsv"
OUT = r"C:\Users\beka\AppData\Local\Temp\claude\208a25b89c99599c\b9d48af9-f7a2-4623-89d1-541fa9dfc459\scratchpad\_brace_cmp.txt"
b = open(LIR, 'rb').read()
N = [struct.unpack_from('<ddd', b, 166 + 28 * i) for i in range(2724)]
st = [struct.unpack_from('<H', b, 1517340 + 2 * k)[0] for k in range(6108)]
PROF = {1: '60Ш2', 2: '60Ш3', 3: '40Б1', 4: '30Б1', 5: '20Ш1', 6: '□100x3', 7: '□100x3', 8: 'I660 250-200', 9: '40Ш1', 10: '□100x5', 11: '□160x5',
        12: '□100x5', 13: '70Б1', 14: '30Б1', 16: '45Ш1', 17: '25Б1', 18: '27П', 19: '□200x6', 20: '□374x362x12', 21: '50Ш2', 22: '□120x5', 23: '□120x5',
        24: '□100x3', 25: '40Ш2', 26: 'пластина26'}
BR_MK = ('СВ1', 'СВ2', 'СВ3', 'ГС1', 'ВС1', 'ВФ1', 'Р1', 'Р2')
bars = []
for k in range(6108):
    r = b[76434 + 38 * k: 76434 + 38 * (k + 1)]
    H = struct.unpack_from('<H', r, 36)[0]; n1, n2 = struct.unpack_from('<ii', r, 4)
    if n1 <= 0 or n2 <= 0 or H == 2: continue
    a = [round(c * 1000) for c in N[n1 - 1]]; c2 = [round(c * 1000) for c in N[n2 - 1]]
    bars.append((k, st[k] + 1, a, c2))
mem = []
for l in open(MEM, encoding='utf-8'):
    f = l.rstrip('\n').split('\t'); p = [float(v) for v in f[4:10]]
    mem.append((f[1], f[3], p[0:3], p[3:6]))
def unit(a, c):
    u = [c[i] - a[i] for i in range(3)]; L = math.sqrt(sum(x * x for x in u)) or 1; return [x / L for x in u], L
def cover(a, c, p, q, tol=450):
    """segment a-c lies along p-q (parallel, mid within tol, inside span)"""
    u, L = unit(a, c); v, Lm = unit(p, q)
    if abs(sum(u[i] * v[i] for i in range(3))) < 0.97: return False
    mid = [(a[i] + c[i]) / 2 for i in range(3)]; w = [mid[i] - p[i] for i in range(3)]; t = sum(w[i] * v[i] for i in range(3))
    if t < -tol or t > Lm + tol: return False
    d = [w[i] - v[i] * t for i in range(3)]; return math.sqrt(sum(x * x for x in d)) <= tol
diag = lambda a, c: sum(1 for i in range(3) if abs(a[i] - c[i]) > 300) >= 2      # inclined bar
mb = [m for m in mem if m[0].split(' ')[0] in BR_MK]
lb = [x for x in bars if PROF.get(x[1], '').startswith('□') or x[1] == 18]
# LIRA bars that are braces: inclined □, or □ on a brace line; keep all □ bars, we classify by what the model has there
def plane(a, c):
    if abs(a[0] - c[0]) < 1: return 'X=%d' % a[0]
    if abs(a[1] - c[1]) < 1: return 'Y=%d' % a[1]
    return 'roof/incl'
out = []
# 1) LIRA → model
miss = []; prof = []
for k, t, a, c in lb:
    hit = [m for m in mem if cover(a, c, m[2], m[3])]
    if not hit: miss.append((k, t, a, c)); continue
    if not any(h[1] == PROF.get(t) for h in hit): prof.append((k, t, a, c, sorted(set(h[0] + ' ' + h[1] for h in hit))))
# 2) model → LIRA (each brace member: covered by LIRA bars along it? sample 5 points)
extra = []
for m in mb:
    p, q = m[2], m[3]; v, Lm = unit(p, q); bad = 0
    for s in (0.15, 0.35, 0.5, 0.65, 0.85):
        pt = [p[i] + v[i] * Lm * s for i in range(3)]
        ok = False
        for k, t, a, c in bars:
            u, L = unit(a, c)
            if abs(sum(u[i] * v[i] for i in range(3))) < 0.97: continue
            w = [pt[i] - a[i] for i in range(3)]; tt = sum(w[i] * u[i] for i in range(3))
            if tt < -50 or tt > L + 50: continue
            d = [w[i] - u[i] * tt for i in range(3)]
            if math.sqrt(sum(x * x for x in d)) <= 450: ok = True; break
        if not ok: bad += 1
    if bad >= 3: extra.append(m)
with open(OUT, 'w', encoding='utf-8') as fo:
    fo.write('LIRA □/27П bars %d, model brace members %d\n' % (len(lb), len(mb)))
    fo.write('\n== LIRA bars NOT in model: %d\n' % len(miss))
    g = defaultdict(list)
    for k, t, a, c in miss: g[(plane(a, c), PROF.get(t))].append((a, c))
    for key in sorted(g):
        fo.write('%s %s: %d\n' % (key[0], key[1], len(g[key])))
        for a, c in sorted(g[key])[:40]: fo.write('    (%d %d %d) -> (%d %d %d)\n' % (*a, *c))
    fo.write('\n== model brace members with NO LIRA bar along them: %d\n' % len(extra))
    g = defaultdict(list)
    for m in extra: g[(m[0].split(' ')[0], m[1], plane(m[2], m[3]))].append(m)
    for key in sorted(g):
        fo.write('%s %s %s: %d\n' % (key[0], key[1], key[2], len(g[key])))
        for m in sorted(g[key], key=lambda m: (m[2], m[3]))[:40]: fo.write('    (%d %d %d) -> (%d %d %d)\n' % (*m[2], *m[3]))
    fo.write('\n== profile differs: %d\n' % len(prof))
    for k, t, a, c, h in prof: fo.write('  LIRA %s model %s  (%d %d %d)->(%d %d %d)\n' % (PROF.get(t), h, *a, *c))
    fo.write('\n== model brace marks: %s\n' % sorted(Counter(m[0].split(' ')[0] + ' ' + m[1] for m in mb).items()))
    fo.write('== LIRA □ types: %s\n' % sorted(Counter(PROF.get(x[1]) + ' t%d' % x[1] for x in lb).items()))
print(open(OUT, encoding='utf-8').read()[:6000])
