# 3.8 fixes: detail sketches from analog, steel summary shift + 1-decimal values
import json, gx, re
src = open('gen_fm3.py', encoding='utf-8').read()
src = src[:src.index('# ---- frame portrait')]
ns = {}; exec(src, ns)
items, tot = ns['items'], ns['tot']
fx8 = 543429.0; fy = 455938.9
hs = '2C2FAE 2C2FAF 2C2FB1 2C2FB2 2C2FB7 2C2FBF 2C2FC0 2C2FC1 2C2FC3 2C2FC4 2C2FC5 2C2FCA 2C2FCB 2C2FD0 2C2FD1 2C2FDB 2C2FDC 2C2FDD'.split()
by = {}
for p, d, L, n, mu in items: by[d] = by.get(d, 0) + n * mu
DS = [10, 12, 14, 16, 18, 20, 22, 25, 28, 32]
sc = [[6, 11, '%.1f' % tot], [6, 12, '%.1f' % tot]] + [[6, 1 + j, '%.1f' % by.get(d, 0)] for j, d in enumerate(DS)]
ops = [{'t': 'import', 'file': gx.S + r'\an\fm.dwg', 'h': hs, 'base': [-1899642.490348523, -1314010.663930005], 'to': [fx8 + 23500, fy + 14000], 'pre': 'D38:'},
       {'t': 'move', 'h': ['F0D09'], 'd': [-900, 0]},
       {'t': 'tset', 'h': 'F0D09', 'cells': sc}]
print(gx.run(ops, 'f38b')[-300:])
