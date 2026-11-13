src=open(r'C:\Users\Admin\AppData\Local\Temp\claude\a7137524bdaa49d0\c55bc92b-0511-4932-9c00-c1294111057c\scratchpad\rmc_nodes.py', encoding='utf-8-sig').read().split("ALL = (-1e4, 1e4)")[0].replace('g.buffer(10, join_style=2)','g.buffer(5, join_style=2)').replace('gus.simplify(0.5)','gus.simplify(4)')
exec(src)
import math
from shapely.geometry import box
ALL=(-1e4,1e4)
print('##### Узел 8, t=20, Р1 + беті, диагональдар − беті')
cases = [('8 A/G СВ1 (1–2, 10–11)', 5843, 8541.6, None), ('8 D СВ2 (1–2, 10–11)', 5843, 9493, None),
         ('8а A СВ1 + СВ3 (A/4–5)', 5993, 8541.6, ('СВ3', (5996, 1350))),
         ('8а D СВ2 + СВ3 (D/4–5, 7–8)', 5993, 9493, ('СВ3', (5996, 1350))),
         ('8б A/G СВ1 + СВ5 (A/7–8, G/4–5, G/7–8)', 5993, 8541.6, ('СВ5', (6000, 3736)))]
for title, span, zup, low in cases:
    obst = [(box(-4, 4000, 4, 8000), ALL)]
    mem = [M('Р1', (0, 6000), (1, 0), +1, 140, fixed=146), M('upper', (4, 6070), (span - 3 - 4, zup - 6070), -1, 140)]
    if low: mem.append(M(low[0], (4, 5930), (low[1][0] - 4, low[1][1] - 5930), -1, 140))
    pl = solve0(mem, obst, 20, box(-100, 0, 18, 20000))
    report(title, pl, 20, [(4, 5900), (4, 6100)], sup_lines=[((4, 5000), (4, 7000))])
print('##### Узел 7 A/G t=14: Р1 +, СВ1 −')
for span in (5993, 5843):
    Z_TF, Z_BF = 8969.3, 8323.3
    obst = [(box(-125, Z_TF, 125, Z_TF+12), ALL), (box(-125, Z_BF-12, 125, Z_BF), ALL), (box(-160, 8286, 160, 8311), ALL), (box(-3, 8000, 3, 9100), ALL), (box(-4, 7000, 4, 8286), ALL)]
    mem=[M('Р1', (0, 8641.6), (1, 0), +1, 140), M('СВ1 %d'%span, (3, 8541.6), (span - 7, 6070 - 8541.6), -1, 140)]
    pl = solve0(mem, obst, 14, box(-200, 0, 130, 20000))
    report('7 A/G %d'%span, pl, 14, [(3, Z_BF), (3, Z_TF), (125, Z_TF), (125, Z_BF)], sup_lines=[((3, Z_BF), (3, Z_TF)), ((3, Z_TF), (125, Z_TF)), ((3, Z_BF), (125, Z_BF))])
print('##### Узел 7D жота пластинасы t=20: Р2 + (модель ұшы 325), СВ2 −')
for span in (5993, 5843):
    obst = [(box(-175, 9850, 175, 9868), ALL), (box(-175, 9318, 175, 9336), ALL), (box(-170, 9293, 170, 9318), ALL), (box(-4, 8000, 4, 9293), ALL)]
    mem=[M('Р2', (0, 9593), (1, 0), +1, 150, fixed=321), M('СВ2 %d'%span, (4, 9493), (span - 8, 6070 - 9493), -1, 140)]
    pl = solve0(mem, obst, 20, box(-200, 0, 180, 20000))
    report('7D %d'%span, pl, 20, [(4, 9318), (4, 9868), (185, 9868), (185, 9318), (170,9318)], sup_lines=[((4, 9318), (4, 9868)), ((4, 9868), (175, 9868)), ((4, 9336), (175, 9336))])

