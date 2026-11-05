# -*- coding: utf-8 -*-
"""Данные для «Проверка АБК.xlsx» из CSV ЛИРА (Shift+Выполнить расчет, таблицы «Все»).
tbl01 узлы, tbl03 перемещения (мм), tbl07 инерционные силы (т), tbl08 веса масс (т), tbl05 периоды."""
import sys, json, math, collections
sys.stdout.reconfigure(encoding='utf-8'); sys.path.insert(0, '.')
from lr import rows

LEV = [-2.0, 0.0, 3.3, 6.6]
def lev(z):
    return min(LEV, key=lambda L: abs(L - z))

xyz = {}
for r in rows('tbl01.101.csv'):
    if len(r) > 6 and r[0].isdigit() and r[2].strip().isdigit():
        xyz[int(r[2])] = tuple(float(v) for v in r[3:6])
print('nodes', len(xyz))

# --- веса масс (загр. 13), т
W = collections.defaultdict(float)
for r in rows('tbl08.17_1.csv'):
    if len(r) > 6 and r[0].isdigit() and r[2].strip() == '13':
        W[lev(xyz[int(r[4])][2])] += float(r[5])
# --- инерционные силы по формам
F = collections.defaultdict(lambda: collections.defaultdict(float))   # F[(case,mode)][lev] (dir of case)
FZtot = collections.defaultdict(float)
for r in rows('tbl07.11_1.csv'):
    if len(r) > 7 and r[0].isdigit() and ' - ' in r[2]:
        c, m = [int(t) for t in r[2].split(' - ')]
        if c not in (13, 14): continue
        z = xyz[int(r[4])][2]
        F[(c, m)][lev(z)] += float(r[5] if c == 13 else r[6])
        FZtot[(c, m)] += float(r[5] if c == 13 else r[6]) * (z - LEV[0])   # момент относительно подошвы
# --- перемещения по формам, узлы на отметках этажей
D = collections.defaultdict(dict)   # D[(case,mode)][node] = (dx,dy)
for r in rows('tbl03.5_1.csv'):
    if len(r) > 7 and r[0].isdigit() and ' - ' in r[2]:
        c, m = [int(t) for t in r[2].split(' - ')]
        if c not in (13, 14): continue
        n = int(r[4]); z = xyz[n][2]
        if any(abs(z - L) < 1e-3 for L in LEV):
            D[(c, m)][n] = (float(r[5]), float(r[6]))
modes = {c: sorted(m for cc, m in D if cc == c) for c in (13, 14)}
print('modes', modes)
# --- периоды / модальные массы
per = {}
for r in rows('tbl05.9_1.csv'):
    if len(r) > 15 and r[3].isdigit():
        per[(int(r[2]), int(r[3]))] = dict(T=float(r[7]), M=float(r[11]), S=float(r[14]))

def floor_nodes(L):
    # узлы перекрытия: на отметке, внутри плана (для 0.000 и -2.000 — все узлы отметки)
    return [n for n, p in xyz.items() if abs(p[2] - L) < 1e-3]

out = dict(levels=LEV, W={str(L): W[L] for L in LEV}, modes=modes, per={'%d-%d' % k: v for k, v in per.items()})
dom = {13: max(modes[13], key=lambda m: per[(13, m)]['M']), 14: max(modes[14], key=lambda m: per[(14, m)]['M'])}
out['dom'] = dom
for c, k in ((13, 0), (14, 1)):
    disp = {}; srss = {}
    for L in LEV:
        ns = [n for n in floor_nodes(L) if n in D[(c, dom[c])]]
        v = [abs(D[(c, dom[c])][n][k]) for n in ns]
        s = [math.sqrt(sum(D[(c, m)][n][k] ** 2 for m in modes[c])) for n in ns]
        disp[str(L)] = dict(max=max(v), min=min(v), avg=sum(v) / len(v), n=len(v))
        srss[str(L)] = dict(max=max(s), min=min(s), avg=sum(s) / len(s))
    Fl = {str(L): math.sqrt(sum(F[(c, m)][L] ** 2 for m in modes[c])) for L in LEV}
    Fdom = {str(L): F[(c, dom[c])][L] for L in LEV}
    V = {}
    for i, L in enumerate(LEV):
        V[str(L)] = math.sqrt(sum(sum(F[(c, m)][LL] for LL in LEV[i + 1:]) ** 2 for m in modes[c])) if i < len(LEV) - 1 else 0.0
    Mov = math.sqrt(sum(FZtot[(c, m)] ** 2 for m in modes[c]))
    Vbase = math.sqrt(sum(sum(F[(c, m)].values()) ** 2 for m in modes[c]))
    out['dir%d' % c] = dict(disp_dom=disp, disp_srss=srss, F=Fl, Fdom=Fdom, V=V, Mov=Mov, Vbase=Vbase)
json.dump(out, open('chk.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1)[:6000])
