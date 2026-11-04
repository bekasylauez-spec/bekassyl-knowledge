# Beams (ригели) on 2.2 (−0.100) and 2.3 (+3.950) from LIRA «Тип А6 С2» (stiffness 8, S0 45×55 → b=450, h=550),
# drawn under the slab with the hidden linetype, face to face of columns/walls (rules 31.10: one common hidden contour,
# no lines through columns); marks Рм-1…Рм-5; column marks Км-1 (row −1250, LIRA 50×50) / Км-2 (rows 23100/28600,
# LIRA 60×60) on 2.1–2.3.
import json, sys
sys.path.insert(0, '.')
import model as M
import gen_marks as GM

B = 450
CX = [125, 6800, 13250, 19925]             # column centres (scheme 2.1)
ROWS = [-1000, 23350, 28850]
SLAB_Y0, SLAB_Y1 = M.SLAB_BIG[1], M.SLAB_BIG[3]
beams = []                                  # (mark, x0, y0, x1, y1)
for k, yc in enumerate(ROWS):
    row = sorted([c for c in M.COLUMNS if c[1] < yc < c[3]], key=lambda c: c[0])
    for a, b in zip(row, row[1:]):
        beams.append(('Рм-%d' % (k + 1), a[2], yc - B / 2, b[0], yc + B / 2))
for xc in CX:
    # edge beams flush with the slab edge like the edge columns (−125 / 20175)
    bx0 = M.SLAB_BIG[0] if xc < 1000 else (M.SLAB_BIG[2] - B if xc > 19000 else xc - B / 2)
    bx1 = bx0 + B
    beams.append(('Рм-4', bx0, SLAB_Y0, bx1, -1250))
    beams.append(('Рм-4', bx0, -750, bx1, -125))
    beams.append(('Рм-5', bx0, 23650, bx1, 28550))
    beams.append(('Рм-5', bx0, 29150, bx1, SLAB_Y1))
# outer columns are flush with the slab edge: clip the beam to the slab contour in x
SX0, SX1 = M.SLAB_BIG[0], M.SLAB_BIG[2]
beams = [(n, max(x0, SX0), y0, min(x1, SX1), y1) for n, x0, y0, x1, y1 in beams]


def draw(sheet):
    DX, DY = GM.SH[sheet]; X, Y = GM.X21 + DX, GM.Y21 + DY
    ops = []
    for n, x0, y0, x1, y1 in beams:
        horiz = (x1 - x0) > (y1 - y0)
        sides = [((x0, y0), (x1, y0)), ((x0, y1), (x1, y1))] if horiz else [((x0, y0), (x0, y1)), ((x1, y0), (x1, y1))]
        for a, b in sides:
            # a side lying on the slab contour is already drawn by the contour
            if (not horiz and (abs(a[0] - SX0) < 1 or abs(a[0] - SX1) < 1)): continue
            ops.append({'t': 'pl', 'p': [[X + a[0], Y + a[1]], [X + b[0], Y + b[1]]], 'closed': False, 'layer': '0',
                        'ltype': 'невидимая', 'ltscale': 100, 'lw': 5})
    return ops, X, Y


if __name__ == '__main__':
    allops = []
    for sheet in (2, 3):
        ops, X, Y = draw(sheet); allops += ops
    json.dump(allops, open('ops/beams.json', 'w', encoding='utf-8'), ensure_ascii=False)
    print(len(allops), 'beam lines', len(beams), 'beams')
