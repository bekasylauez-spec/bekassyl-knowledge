# Sheet 6.1 «Опалубочный чертеж Пм-1 на отм. -0.100» = analog 5.1 sheet 1 (frame, title, notes, Разрез 1-1, opening style)
# + plan background cloned from our scheme 2.2 (axes, walls, columns, rigels, chains) -- scheme is the primary geometry source.
import gx, json, os
S = gx.S
X22, Y22 = -184221.0, 455939.0          # 2.2 frame min
NX, NY = 172179.0, 455939.0             # new sheet frame min
DX = NX - X22
OX, OY = -173564.0 + DX, 463756.885      # axis 1 / axis А/1 on the new sheet

EXCL = {'DC477', 'DC478', 'DC4E3', 'DC4E5', 'E3FF2', 'E1452'}
hs = []
for l in open(os.path.join(S, 'w', 'all.txt'), encoding='utf-8'):
    f = l.rstrip('\n').split('\t')
    if f[0] != 'L': continue
    a = list(map(float, f[4][1:].split(',')))
    if not (a[0] >= X22 and a[2] <= X22 + 59400 and a[1] >= 455900): continue
    if f[1] in ('SPDSNOTEPOSITION', 'SPDSSECTION', 'SPDSFORMAT') or f[2] in EXCL: continue
    hs.append(f[2])

ops = [{'t': 'clone', 'h': h, 'base': [0, 0], 'to': [DX, 0], 'tag': 'P61_' + h} for h in hs]

# analog plan block + analog plan dims (not those of Разрез 1-1)
ADIMS = ['2B4406', '2B4415', '2B4422', '2B443E', '2B4450', '2B4462', '2B4471', '2B447E', '2B448D', '2B44DA', '2B44E9',
         '2B44F6', '2B4505', '2B451F', '2B452C', '2B453A', '2B4549', '2B4558', '2B4567']
ops.append({'t': 'erase', 'h': ['2B4327', '2B4539'] + ADIMS})


def P(x, y): return [OX + x, OY + y]


# slab contour = analog contour (layer Размеры, 0.50) set to our slab
ops.append({'t': 'plset', 'h': '2B43FD', 'p': [P(-125, -3275), P(20175, -3275), P(20175, 31175), P(-125, 31175)], 'closed': True})
# openings (LIRA −0.100: lift + stair/basement stair, faces of the walls)
OPEN = [(6925, 15475, 10275, 17775), (6925, 18025, 10275, 20575), (10525, 15475, 13125, 20575)]
for h, (a, b, c, d) in zip(['2B43FE', '2B44D9'], OPEN[:2]):
    ops.append({'t': 'plset', 'h': h, 'p': [P(a, b), P(c, b), P(c, d), P(a, d)], 'closed': True})
ops.append({'t': 'clone', 'h': '2B43FE', 'tag': 'P61_OP3'})
a, b, c, d = OPEN[2]
ops.append({'t': 'plset', 'h': 'P61_OP3', 'p': [P(a, b), P(c, b), P(c, d), P(a, d)], 'closed': True})
# opening symbol (Bekassyl's style, Obsidian 05_Плиты): corner -> break (0.15w; 0.89h) -> opposite corner, layer _0, 0.20
for a, b, c, d in OPEN:
    w, h = c - a, d - b
    ops.append({'t': 'pl', 'p': [P(a, b), P(a + 0.15 * w, b + 0.89 * h), P(c, d)], 'layer': '_0', 'lw': 20})
# opening chains: clone analog dims (style of the analog sheet)
HD, VD = '2B4431', '2B4512'
xs = [6800, 6925, 10275, 10525, 13125, 13250]
for i, (p, q) in enumerate(zip(xs, xs[1:])):
    tg = 'P61_HD%d' % i
    ops.append({'t': 'clone', 'h': HD, 'tag': tg})
    ops.append({'t': 'dimpts', 'h': tg, 'p1': P(p, 14300) + [0], 'p2': P(q, 14300) + [0], 'dl': P(p, 14300) + [0]})
ys = [14750, 15475, 17775, 18025, 20575, 22750]
for i, (p, q) in enumerate(zip(ys, ys[1:])):
    tg = 'P61_VD%d' % i
    ops.append({'t': 'clone', 'h': VD, 'tag': tg})
    ops.append({'t': 'dimpts', 'h': tg, 'p1': P(13950, p) + [0], 'p2': P(13950, q) + [0], 'dl': P(13950, p) + [0]})
ops.append({'t': 'erase', 'h': [HD, VD]})
# section mark 1-1 over the axis-1 wall, title to the scheme title place, Разрез 1-1 detail to the free right part
ops.append({'t': 'move', 'h': ['2B449A'], 'd': [OX - 190196, OY + 9000 - 478710]})
ops.append({'t': 'move', 'h': ['2B449B'], 'd': [-170320 + DX - 192601, 496001 - 494655]})
DET = ['2B449E', '2B449F', '2B44A1', '2B44A2', '2B44A3', '2B44A4', '2B44A5', '2B44A6', '2B44B5', '2B44B6', '2B44B7', '2B44B8',
       '2B44C7', '2B44D6', '2B44D7']
ops.append({'t': 'movegrp', 'h': DET, 'd': [38000, 13000]})
ops.append({'t': 'save'})
if __name__ == '__main__':
    out = gx.run(ops, 'g61')
    print(len(hs), [l for l in out.splitlines() if 'ERR' in l or 'fail' in l or 'done' in l or 'no ' in l][:20])
