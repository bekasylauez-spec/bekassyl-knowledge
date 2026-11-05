"""2.4: consoles КН-1 also at axes 1 and 6 (as in LIRA): clone the console ring + КН-1 mark of axis 2 / axis 5 by the axis spacing."""
import os, sys, ab
X0, Y0 = -1285503.0, -1749172.0
WIN = [X0, Y0, X0 + 42000, Y0 + 29700]
ab.run([{'t': 'list', 'win': WIN}], 'si')
E = []
for l in open(os.path.join(os.environ['TEMP'], 'ob_log.txt'), encoding='utf-8-sig'):
    f = l.rstrip('\n').split('\t')
    if f[0] == 'L' and len(f) >= 5:
        E.append(dict(t=f[1], h=f[2], lay=f[3], e=list(map(float, f[4][1:].split(','))), pts=[tuple(map(float, q.split(',')[:2])) for q in f[5:] if ',' in q]))
V = sorted([e for e in E if e['t'] == 'SPDSCONSTRUCTIONLINE' and abs(e['pts'][0][0] - e['pts'][1][0]) < 1], key=lambda e: e['pts'][0][0])
AXW = [e['pts'][0][0] for e in V]
print('axes', [round(a - AXW[0]) for a in AXW])
f = os.path.abspath('w/g24.txt')
ab.run([{'t': 'geomdump', 'win': WIN, 'file': f}], 'g')
kn = set()
for l in open(f, encoding='utf-8'):
    p = l.rstrip('\n').split('|')
    if p[0] == 'T' and 'КН-1' in p[7]: kn.add((p[1], float(p[3])))
x2, x5 = AXW[1], AXW[4]
rings = [e for e in E if e['t'] == 'LWPOLYLINE' and abs((e['e'][2] - e['e'][0]) - 700) < 3 and 550 < (e['e'][3] - e['e'][1]) < 650 and abs((e['e'][0] + e['e'][2]) / 2 - x2) < 5]
marks2 = [h for h, xx in kn if abs(xx - x2) < 2500 and xx > x2 - 200]
print('rings', [r['h'] for r in rings], 'marks', marks2, kn)
d1, d6 = AXW[0] - x2, AXW[5] - x2
O = [{'t': 'sysvar', 'n': 'TILEMODE', 'v': 1}]
for i, d in enumerate((d1, d6)):
    O.append({'t': 'clonexf', 'hs': [r['h'] for r in rings] + list(marks2), 'd': [d, 0], 'pre': 'kn24_%d_' % i})
O.append({'t': 'txtrep', 'win': WIN, 'pairs': [['в составе колонн Км-4', 'в составе колонн Км-4, Км-5']]})
O.append({'t': 'save'})
if len(sys.argv) > 1:
    print(ab.run(O, 'p24')[-400:])
