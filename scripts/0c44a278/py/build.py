# -*- coding: utf-8 -*-
import json, math, pickle, os, shutil, sys
import geom, design as D0, gen, run
from gen import tp, PARK
S = geom.S
W = S
OUT1 = W + r'\b1_1.dwg'

def pm1(k):
    sh = gen.pm1_sheet(k); sh.ax0 = 5500; sh.yA = -47000; return sh
def pm2(k):
    return gen.pm2_sheet(k)

def stage_prep():
    shutil.copy(W + r'\b3.dwg', W + r'\b1_0.dwg')
    if os.path.exists(W + r'\map.json'): os.remove(W + r'\map.json')
    ops = [{'t': 'freezefields'}] + gen.park_ops()
    # Pm2 opal sections 1-1/2-2 -> clones 3-3/4-4 (500x900) parked later by handle lists
    ops.append({'t': 'replace', 'win': [-900000, -3400000, 0, -3000000], 'a': 'Блок 3', 'b': 'Блок 1'})
    print(run.run(ops, W + r'\b1_0.dwg', W + r'\b1_1.dwg', 'prep'))

def erase_ops():
    ops = []
    for k in range(1, 7):
        sh = pm1(k)
        ops.append({'t': 'eraseregion', 'win': [sh.x0 + 2300, sh.top - 56800, sh.x0 + 62600, sh.top - 9300]})
        ops.append({'t': 'eraselayer', 'layer': 'Кж каркас', 'win': [sh.x0, sh.top - 59400, sh.x0 + 84100, sh.top]})
        if k == 5: ops.append({'t': 'eraseregion', 'win': [sh.x0 + 61000, sh.top - 48000, sh.x0 + 84000, sh.top - 2000]})
    for k in range(1, 5):
        sh = pm2(k)
        ops.append({'t': 'eraseregion', 'win': [sh.x0 + 2300, sh.top - 29000, sh.x0 + 32000, sh.top - 6500]})
        ops.append({'t': 'eraselayer', 'layer': 'Кж каркас', 'win': [sh.x0, sh.top - 42000, sh.x0 + 59400, sh.top]})
    return ops

SEC = {  # analog pm1 opal sections: center x, slab bottom (rel), window
    '1': (69000, -7800), '2': (75000, -14300), '3': (69000, -20800), '4': (75000, -27300), '5': (69000, -33800)}
def sections_pm1_ops():
    sh = pm1(1); x0, top = sh.x0, sh.top
    mem = json.load(open(S + r'\secmembers.json'))['pm1']
    # new layout: (src, new number, dx, dy, half-width change (units, 1:25 => x4), depth change)
    plan = [('1', '1', 5318, 4053, 400, 0),     # 600x700 interior (Д)
            ('2', '2', 391, 3105, 200, 0),     # 500x700 edge (А, Е, Ж)
            ('3', '3', 5318, 2158, 200, -400),  # 500x900 interior (digit axes)
            ('4', '4', 391, 10, 200, -400),    # 500x900 edge (axes 3, 13)
            ('5', '5', 5018, -2137, 0, 0),      # 250x600 secondary
            ('3', '6', 5318, -22984, 200, 1200)] # 600x1200 interior (В 7-13, Д 4-5)
    ops = []
    for src, num, dx, dy, dw, dh in plan:
        cx, sb = SEC[src]
        if num == '6':
            hs = []
            for i, h in enumerate(mem[src]):
                ops.append({'t': 'clone', 'h': h, 'base': [0, 0], 'to': [0, dy - 2158], 'tag': 'S6_%d' % i}); hs.append('S6_%d' % i)
        else:
            hs = list(mem[src])
            ops.append({'t': 'move', 'h': hs, 'd': [dx, dy]})
        ncx = x0 + cx + dx; nsb = top + sb + dy
        if dw:
            ops.append({'t': 'stretch', 'hs': hs, 'win': [ncx + 5, nsb - 30000, ncx + 30000, nsb + 30000], 'd': [dw, 0]})
            ops.append({'t': 'stretch', 'hs': hs, 'win': [ncx - 30000, nsb - 30000, ncx - 5, nsb + 30000], 'd': [-dw, 0]})
        if dh:
            ops.append({'t': 'stretch', 'hs': hs, 'win': [ncx - 30000, nsb - 30000, ncx + 30000, nsb - 100], 'd': [0, -dh]})
        if num == '6':
            ops.append({'t': 'replace', 'win': [ncx - 9000, nsb - 12000, ncx + 9000, nsb + 4000], 'a': '3 - 3', 'b': '6 - 6'})
    return ops

def move_right_groups():
    ops = []
    sh = pm1(2); ops.append({'t': 'movewin', 'win': [sh.x0 + 68000, sh.top - 28500, sh.x0 + 82500, sh.top - 9500], 'd': [1000, 0]})
    for k in (4, 6):
        sh = pm1(k); ops.append({'t': 'movewin', 'win': [sh.x0 + 63900, sh.top - 17900, sh.x0 + 73900, sh.top - 12600], 'd': [5500, -1500]})
    return ops

SECMARK = {  # number: (X, Y, rot) abs plan coords
    '1': (27000, 27500, 0), '2': (15000, -250, 0), '3': (24000, 18000, math.pi / 2),
    '4': (12000, 11000, math.pi / 2), '5': (45000, 30340, 0), '6': (50000, 13900, 0)}
def opal_extra(sh):
    ops = []
    sl = geom.slab(sh.z)
    AX = sorted(v for k, v in geom.AXX.items() if k != '14'); AY = sorted(geom.AXY.values())
    for H in sl['holes']:
        x0, y0, x1, y1 = H['geom'].bounds
        ax = max([a for a in AX if a <= x0 + 1] or [AX[0]]); ay = max([a for a in AY if a <= y0 + 1] or [AY[0]])
        ydl = y1 + 450
        pts = sorted(set([ax, x0, x1]))
        ops += gen.chainH(sh, pts, y1, ydl)
        xdl = x1 + 450
        pts = sorted(set([ay, y0, y1]))
        ops += gen.chainV(sh, pts, x1, xdl)
    if sh.z == '7.0':
        for num, (X, Y, rot) in SECMARK.items():
            ops.append({'t': 'clone', 'h': tp('secmark'), 'base': [-781272, -3162000 + PARK], 'to': sh.T(X, Y), 'rot': rot, 'attr': num})
    else:
        for num, (X, Y, rot) in {'1': (15000, 3000, 0), '2': (21000, -250, 0)}.items():
            ops.append({'t': 'clone', 'h': tp('secmark'), 'base': [-781272, -3162000 + PARK], 'to': sh.T(X, Y), 'rot': rot, 'attr': num})
    return ops

def build_all(stage_from='prep'):
    res, RS = pickle.load(open(S + r'\design.pkl', 'rb'))
    for z in res: D0.RAS[z] = D0.raster(z)
    if stage_from == 'prep':
        stage_prep()
    ops = erase_ops() + move_right_groups() + sections_pm1_ops()
    # ---- Pm1
    pos1 = gen.positions(res, '7.0'); pos2 = gen.positions(res, '4.5')
    sh = pm1(1); ops += gen.plan_common(sh, 'opal') + opal_extra(sh)
    sh = pm1(2); ops.append({'t': 'replace', 'win': [sh.x0, sh.top - 59400, sh.x0 + 84100, sh.top], 'a': '(400,250)', 'b': '(600,250)'})
    ops += gen.plan_common(sh, 'main') + gen.main_bars(sh); sk, skL1 = gen.sk_marks(sh); ops += sk
    for k, f in ((3, 0), (4, 1), (5, 2), (6, 3)):
        sh = pm1(k); ops += gen.plan_common(sh, 'dop') + gen.dop_sheet(sh, res['7.0'][f], f, pos1)
    # ---- Pm2
    sh = pm2(1); ops += gen.plan_common(sh, 'opal') + opal_extra(sh)
    sh = pm2(2); ops += gen.plan_common(sh, 'main') + gen.main_bars(sh); sk, skL2 = gen.sk_marks(sh); ops += sk
    sh = pm2(3); ops += gen.plan_common(sh, 'dop') + gen.dop_sheet(sh, res['4.5'][0] + res['4.5'][2] if False else res['4.5'][0], 0, pos2)
    sh3 = pm2(3); sh3.occ = sh.occ; ops += gen.dop_sheet(sh3, res['4.5'][2], 2, pos2)
    sh = pm2(4); ops += gen.plan_common(sh, 'dop') + gen.dop_sheet(sh, res['4.5'][1], 1, pos2)
    sh4 = pm2(4); sh4.occ = sh.occ; ops += gen.dop_sheet(sh4, res['4.5'][3], 3, pos2)
    import spec
    sops, C1, C2 = spec.all_ops(res); ops += sops
    json.dump({'sk': {'7.0': skL1, '4.5': skL2}}, open(S + r'\skl.json', 'w'))
    print('ops', len(ops))
    out = run.run(ops, W + r'\b1_1.dwg', W + r'\b1_2.dwg', 'build', timeout=3000)
    print(out[-3000:])

if __name__ == '__main__':
    build_all(sys.argv[1] if len(sys.argv) > 1 else 'prep')
