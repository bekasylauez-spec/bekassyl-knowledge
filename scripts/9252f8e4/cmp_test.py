# v9 vs v10 ArmaDA results, element by element (map v9->v10 by geometry), with the four items the BI session raised:
# Км-2 basement columns (ΣAs vs 16Ø28 = 98.5 см²), ригель top As vs 4Ø28 = 24.63 см², Фм-1 shear (messages, ASW>0), stair flights As.
import sys, os, glob, csv, collections, math
sys.path.insert(0, r'D:\_claude_work\Kasymova')
from sub import load, heads, doc
K = r'D:\_claude_work\Kasymova'
LEV = [-7.0, -3.7, -0.1, 4.1, 8.3, 12.5, 16.4, 20.3, 24.2, 28.1, 32.0, 35.9, 40.1, 44.3, 47.3]
def lev(z): return max(a for a in LEV if a <= z + 0.01)
def entries(d):
    s = ' '.join(d[1:]).replace(')', ' ')
    return [e.split() for e in s.split('/') if e.strip()]
def model(txt):
    L = load(txt); h = heads(L)
    el = entries(doc(L, h, 1)); xyz = [tuple(map(float, e)) for e in entries(doc(L, h, 4))]
    out = []
    for e in el:
        p = [xyz[int(n) - 1] for n in e[2:] if int(n) > 0]
        out.append((int(e[0]), int(e[1]), p))
    return out
def fl(v):
    try: return float(v)
    except ValueError: return 0.0
def biggest(d, pat):
    fs = glob.glob(os.path.join(d, pat)); return max(fs, key=os.path.getsize)
def plates(d):
    P = {}; M = collections.defaultdict(set)
    for l in open(biggest(d, 'plates_*.csv'), encoding='utf-8', errors='replace'):
        f = l.rstrip('\n').replace('\ufeff', '').split(';')
        if len(f) < 8 or not f[0].isdigit(): continue
        if f[1].endswith('-R'): M[int(f[4])].add(f[7].strip()); continue
        if f[1].endswith('-S') or len(f) < 16: continue
        e = int(f[4])
        if e not in P: P[e] = [fl(x) for x in f[8:12]] + [fl(f[15])]
    return P, M
def bars(d):
    B = collections.defaultdict(list); M = collections.defaultdict(set); seen = set()
    for l in open(biggest(d, 'bars_*.csv'), encoding='utf-8', errors='replace'):
        f = l.rstrip('\n').replace('\ufeff', '').split(';')
        if len(f) < 8 or not f[0].isdigit(): continue
        if f[1].endswith('-R'):
            m = (f[9].strip() if len(f) > 9 and f[9].strip() else f[-2].strip()); M[int(f[4])].add(m.split('Q=')[0].strip()); continue
        if f[1].endswith('-S') or len(f) < 21: continue
        e, s = int(f[4]), f[5]
        if (e, s) in seen: continue
        seen.add((e, s)); B[e].append([fl(x) for x in f[10:21]])
    return B, M
mod9 = model(K + r'\v9\v9_final.txt'); mod10 = model(K + r'\v9\v9_final.txt')
P9, PM9 = plates(K + r'\res_v9'); P10, PM10 = plates(K + r'\res_v9')
B9, BM9 = bars(K + r'\res_v9'); B10, BM10 = bars(K + r'\res_v9')
mp = {i: i for i in range(1, len(mod9) + 1)}
def tot(rows): return max(sum(r[0:8]) for r in rows)
def top(rows): return max(r[2] + r[3] + r[5] for r in rows)    # AU3+AU4+AS2 (upper face, local Z1)
def bot(rows): return max(r[0] + r[1] + r[4] for r in rows)    # AU1+AU2+AS1
out = []
def say(s=''): out.append(s); print(s)
# --- 1. basement columns Колонна 600 (stiff 5)
def grp_bars(mod, B, st):
    return {i + 1: B[i + 1] for i, (t, s, p) in enumerate(mod) if s == st and (i + 1) in B}
c9 = grp_bars(mod9, B9, 5); c10 = grp_bars(mod10, B10, 5)
say('1) Колонна 600 (жертөле): ΣAs > 98.5 см² (16Ø28): v9 %d эл., v10 %d эл.; max v9 %.1f, v10 %.1f' % (
    sum(1 for r in c9.values() if tot(r) > 98.5), sum(1 for r in c10.values() if tot(r) > 98.5),
    max(tot(r) for r in c9.values()), max(tot(r) for r in c10.values())))
# --- 2. ригель top
r9 = grp_bars(mod9, B9, 7); r10 = grp_bars(mod10, B10, 7)
say('2) Ригель 450×500: үстіңгі (AU3+AU4+AS2) > 24.63 см² (4Ø28): v9 %d эл., v10 %d эл.; max v9 %.1f, v10 %.1f; астыңғы max v9 %.1f, v10 %.1f' % (
    sum(1 for r in r9.values() if top(r) > 24.63), sum(1 for r in r10.values() if top(r) > 24.63),
    max(top(r) for r in r9.values()), max(top(r) for r in r10.values()), max(bot(r) for r in r9.values()), max(bot(r) for r in r10.values())))
new_b = [j for j in r10 if j not in set(mp.values())]
if new_b:
    say('   жаңа v10 ригельдері: %d эл. нәтижесі бар; ΣAs max %.1f см², үстіңгі max %.1f, астыңғы max %.1f; хабарламасы бар: %d' % (
        len(new_b), max(tot(r10[j]) for j in new_b), max(top(r10[j]) for j in new_b), max(bot(r10[j]) for j in new_b), sum(1 for j in new_b if BM10.get(j))))
miss = [i + 1 for i, (t, s, p) in enumerate(mod10) if t == 10 and (i + 1) not in B10]
say('   v10 стерженьдерінің нәтижесіз қалғаны: %d %s' % (len(miss), miss[:10]))
# --- 3. Фм-1 (stiff 1)
f9 = [i + 1 for i, (t, s, p) in enumerate(mod9) if s == 1]; f10 = [i + 1 for i, (t, s, p) in enumerate(mod10) if s == 1]
def shear_msgs(ids, PM): return sum(1 for e in ids if any('попереч' in m for m in PM.get(e, ())))
say('3) Фм-1 t=800: «Сечение мало по поперечной силе» v9 %d эл., v10 %d эл.; ASW>0 v9 %.0f %%, v10 %.0f %%' % (
    shear_msgs(f9, PM9), shear_msgs(f10, PM10), 100 * sum(1 for e in f9 if P9.get(e, [0] * 5)[4] > 0) / len(f9), 100 * sum(1 for e in f10 if P10.get(e, [0] * 5)[4] > 0) / len(f10)))
# --- 4. stair flights (stiff 9, inclined)
def flights(mod):
    return [i + 1 for i, (t, s, p) in enumerate(mod) if s == 9 and max(q[2] for q in p) - min(q[2] for q in p) > 0.01]
fl9, fl10 = flights(mod9), flights(mod10)
say('4) Марштар: As max v9 %.1f, v10 %.1f см²/м; > 15 см²/м v9 %d эл., v10 %d эл.' % (
    max(max(P9[e][:4]) for e in fl9), max(max(P10[e][:4]) for e in fl10), sum(1 for e in fl9 if max(P9[e][:4]) > 15), sum(1 for e in fl10 if max(P10[e][:4]) > 15)))
# --- 5. element-by-element change
chg = []
for a, b in mp.items():
    t, s, p = mod10[b - 1]
    if a in P9 and b in P10:
        d = max(abs(x - y) for x, y in zip(P9[a][:4], P10[b][:4])); base = max(P9[a][:4] + [1.0])
    elif a in B9 and b in B10:
        d = abs(tot(B9[a]) - tot(B10[b])); base = max(tot(B9[a]), 1.0)
    else: continue
    c = tuple(sum(q[k] for q in p) / len(p) for k in range(3))
    chg.append((d, d / base, b, s, c))
big = [x for x in chg if x[0] > 2.0 and x[1] > 0.2]
say('5) Элементтер: салыстырылды %d; өзгерісі > 2 см² және > 20 %%: %d' % (len(chg), len(big)))
zone = collections.Counter()
for d, r, b, s, c in big:
    near = 'x=51' if abs(c[0] - 51) < 3 and 4 < c[1] < 13 else ('y=34' if abs(c[1] - 34) < 3 and 28 < c[0] < 36 else 'басқа')
    zone[(near, s, lev(c[2]))] += 1
for k, n in sorted(zone.items(), key=lambda t: -t[1])[:25]: say('   %s жесткость %d деңгей %s: %d' % (k[0], k[1], k[2], n))
open('C:\\Users\\beka\\AppData\\Local\\Temp\\claude\\61d567fc0ab17a45\\9252f8e4-753b-43e2-aae3-c6e03c79625e\\scratchpad\\cmp_test.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
