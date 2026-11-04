# marks: rename existing column notes Км-1 → Км-1/Км-2 on 2.1/2.2, new column marks on 2.3, beam marks Рм-1..5 on 2.2/2.3
import json, os, sys
sys.path.insert(0, '.')
import model as M, gen_marks as GM, gen_beams as GB
m = json.load(open(os.environ['TEMP'] + '/gx_map.json', encoding='utf-8-sig'))
ops = []
def cmark(c): return 'Км-1' if c[1] == -1250 else 'Км-2'
for sh in (1, 2):
    E = GM.elements(sh)
    for i, (n, r) in enumerate(E):
        if n == 'Км-1':
            tag = 'MK%d_M%d' % (sh, i)
            if tag in m: ops.append({'t': 'mcset', 'h': tag, 'set': {'FirstLine': cmark(r)}})
for sh in [int(v) for v in os.environ.get('BM_SHEETS', '2,3').split(',')]:
    DX, DY = GM.SH[sh]; X, Y = GM.X21 + DX, GM.Y21 + DY
    fx0 = -243621 + GM.SW * (sh - 1); frame = (fx0, 455939, fx0 + GM.SW, 497939)
    obst = GM.load('w/live.dxf', 'w/geom.txt', frame)
    E = [(n, (x0, y0, x1, y1)) for n, x0, y0, x1, y1 in GB.beams]
    if sh == 3: E += [(cmark(c), c) for c in M.COLUMNS]
    o, miss = GM.place(sh, X, Y, E, obst, X + 10025, Y + 11375, frame, 'RB%d_' % sh)
    ops += o
    print(sh, len(o) // 3, 'placed, miss', miss)
json.dump(ops, open('ops/beammarks.json', 'w', encoding='utf-8'), ensure_ascii=False)
