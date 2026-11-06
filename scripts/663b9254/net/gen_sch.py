# Column schema sheet 4.1: marks (clones of the Онкоцентр schema note «Км-1.1», C681D imported as ONN:...) at every Block-3 column,
# title, stamp texts. usage: python gen_sch.py marks.json [--run]
#   marks.json: {"x,y" (LIRA, mm from axis 22 / axis А): "Км-1", ...}
import json, sys, os
import gx
MK = json.load(open(sys.argv[1], encoding='utf-8'))
DX, DY = 180617 - 217417, 271898 - (-1795185)        # schema sheet 2.2 -> this drawing
X22, YA = 229917.0, -1780735.0                       # axis 22 / axis А in the schema file (sheet 2.2)
R = json.load(open(os.path.join(gx.S, 'w', 'schcols.json')))
rects = [r for r in R if r['sh'] == 1]
ops = []
def add(**k): ops.append(k)
m = gx.tagmap()
NOTE = 'ONN:C681D'                                    # Онкоцентр «Км-1.1»: origin = shelf start, pt1 = arrow tip; tip->origin = (+735, +770)
used = []
for k, mark in sorted(MK.items(), key=lambda kv: (int(kv[0].split(',')[1]), int(kv[0].split(',')[0]))):
    x, y = map(float, k.split(','))
    sx, sy = X22 + x, YA + y
    r = min(rects, key=lambda r: (r['cx'] - sx) ** 2 + (r['cy'] - sy) ** 2)
    d = ((r['cx'] - sx) ** 2 + (r['cy'] - sy) ** 2) ** 0.5
    assert d < 700, (k, d)
    used.append(r['hd'])
    tip = (r['x1'] + DX, r['y1'] + DY)                # top-right corner of the column
    org = (tip[0] + 735, tip[1] + 770)
    tg = 'SCHM:' + k
    add(t='clone', h=NOTE, base=[0, 0], to=[0, 0], tag=tg)
    add(t='spmove', h=tg, items=[[0, org[0], org[1]], [1, tip[0], tip[1]]])
    add(t='mcset', h=tg, set={'FirstLine': mark})
print(len(MK), 'marks;', len(set(used)), 'distinct rects')
json.dump(ops, open(os.path.join(gx.S, 'ops', 'sch_marks.json'), 'w', encoding='utf-8'), ensure_ascii=False)
if '--run' in sys.argv: print(gx.run(ops + [{'t': 'save'}], 'sch_marks')[-600:])
