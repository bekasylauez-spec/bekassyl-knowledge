# Column As from LIRA «Арматура в стержнях» CSV (cp1251): per column (x,y) the max over all its RC elements/sections.
import csv, json, sys, collections, math
CSV = sys.argv[1]
C = json.load(open('lcols.json', encoding='utf-8'))
el2col = {}
for k, v in C.items():
    for z0, z1, st, sec, el, ft in v:
        if sec.startswith('S0'): el2col[el] = (k, z0, z1, sec)
rows = list(csv.reader(open(CSV, encoding='cp1251', errors='replace'), delimiter=';'))
hdr = [r for r in rows[:15]]
for r in hdr: print('H', r[:24])
R = collections.defaultdict(list)
for r in rows:
    if len(r) < 18 or not r[4].strip().isdigit(): continue
    e = int(r[4])
    if e not in el2col: continue
    try: v = [float(x.replace(',', '.')) if x.strip() else 0.0 for x in r[10:22]]
    except ValueError: continue
    R[e].append((r[5].strip(), r[6].strip('﻿ ').strip(), v))
cols = {}
for e, rr in R.items():
    k, z0, z1, sec = el2col[e]
    for s, star, v in rr:
        if star == '*': continue
        tot = sum(v[0:8]); au = max(v[0:4]); asf = max(v[4:8]); asw = max(v[9:11])
        c = cols.setdefault(k, dict(sec=sec.split()[2] + 'x' + sec.split()[3], tot=0, au=0, asf=0, asw=0, n=0, zt=None))
        c['n'] += 1
        if tot > c['tot']: c['tot'] = tot; c['zt'] = (round(z0, 2), round(z1, 2), s)
        c['au'] = max(c['au'], au); c['asf'] = max(c['asf'], asf); c['asw'] = max(c['asw'], asw)
json.dump(cols, open('colas.json', 'w'), ensure_ascii=False, indent=0)
A28 = math.pi * 2.8 ** 2 / 4
for k in sorted(cols, key=lambda k: (cols[k]['sec'], tuple(map(int, k.split(','))))):
    c = cols[k]
    print('%-12s %-7s tot %6.2f (z %s) AUmax %5.2f ASmax %5.2f ASW %5.2f -> n28 %.1f' % (k, c['sec'], c['tot'], c['zt'], c['au'], c['asf'], c['asw'], c['tot'] / A28))
print(len(cols), 'columns with data; elements', len(R))
