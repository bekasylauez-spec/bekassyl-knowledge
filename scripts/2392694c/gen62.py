# Sheet 6.2 «Основное армирование Пм-1 -0.100» = analog 5.1 sheet 2 reworked:
# plan background from scheme 2.2 (axes, walls, columns, rigels, outer axis chains), analog bars/Ск1/notes/chains moved,
# rule Bekassyl 05.11: no slab bar inside a rigel strip, the layout starts 50 mm from the rigel face.
import gx, json, os, math
S = gx.S
X22 = -184221.0
NX = 231579.0
DX = NX - X22
OX, OY = -173564.0 + DX, 463756.885
dims = json.load(open(os.path.join(S, 'w', 'dims22.json')))
EXCL = {'DC477', 'DC478', 'DC4E3', 'DC4E5', 'E3FF2'} | set(dims['drop'])
ops = []
for l in open(os.path.join(S, 'w', 'all.txt'), encoding='utf-8'):
    f = l.rstrip('\n').split('\t')
    if f[0] != 'L': continue
    a = list(map(float, f[4][1:].split(',')))
    if not (a[0] >= X22 and a[2] <= X22 + 59400 and a[1] >= 455900): continue
    if f[1] in ('SPDSNOTEPOSITION', 'SPDSSECTION', 'SPDSFORMAT') or f[2] in EXCL: continue
    op = {'t': 'clone', 'h': f[2], 'base': [0, 0], 'to': [DX, 0], 'tag': 'P62_' + f[2]}
    if f[1] == 'LWPOLYLINE': op['lw'] = 5          # contours 0.05 on rebar sheets (Obsidian 05_Плиты)
    ops.append(op)


def P(x, y): return [OX + x, OY + y, 0]


SX0, SY0, SX1, SY1 = -125, -3275, 20175, 31175
YB, XB = 10500, 4000                     # representative bars
# analog plan reference on this sheet
AX0, AX1, AY0, AY1, AYB, AXB = 249471, 269771, 471149, 492149, 476233, 255279
ops.append({'t': 'erase', 'h': ['2B479B']})                     # analog plan block
ops.append({'t': 'lineset', 'h': '2B483B', 's': P(SX0, YB), 'e': P(SX1, YB)})
ops.append({'t': 'lineset', 'h': '2B483C', 's': P(XB, SY0), 'e': P(XB, SY1)})
ops.append({'t': 'lineset', 'h': '2B483D', 's': P(SX0, YB + 20), 'e': P(SX0 + 710, YB + 20)})
ops.append({'t': 'lineset', 'h': '2B483F', 's': P(SX1 - 710, YB + 20), 'e': P(SX1, YB + 20)})
ops.append({'t': 'lineset', 'h': '2B4841', 's': P(XB - 20, SY0), 'e': P(XB - 20, SY0 + 710)})
ops.append({'t': 'lineset', 'h': '2B4843', 's': P(XB - 20, SY1 - 710), 'e': P(XB - 20, SY1)})
ops.append({'t': 'erase', 'h': ['2B483B', '2B483C', '2B483D', '2B483F', '2B4841', '2B4843']})
bx, by = P(SX0, YB)[0] - AX0, P(0, YB)[1] - AYB
ops.append({'t': 'move', 'h': ['2B483E'], 'd': [bx, by]})
ops.append({'t': 'move', 'h': ['2B4840'], 'd': [P(SX1, 0)[0] - AX1, by]})
ops.append({'t': 'move', 'h': ['2B4842'], 'd': [P(XB, 0)[0] - AXB, P(0, SY0)[1] - AY0]})
ops.append({'t': 'move', 'h': ['2B4844'], 'd': [P(XB, 0)[0] - AXB, P(0, SY1)[1] - AY1]})
ops.append({'t': 'move', 'h': ['2B4845'], 'd': [P(XB, 0)[0] - AXB, by]})

# rigel strips (scheme 2.2 / gen_beams): x strips of Рм-4/Рм-5, y strips of Рм-1/2/3
RX = [(-125, 325), (6575, 7025), (13025, 13475), (19725, 20175)]
RY = [(-1225, -775), (23125, 23575), (28625, 29075)]


def chain(lo, hi, strips):
    """Bekassyl 05.11: in each bay start 50 from the edge/rigel face and go on @200; the rest closes the bay"""
    bounds, segs, cur = [], [], lo
    for a, b in strips:
        if b <= lo or a >= hi: continue
        if a > cur: bounds.append((cur, a))
        segs.append((max(a, lo), min(b, hi), None)); cur = max(cur, b)
    if cur < hi: bounds.append((cur, hi))
    out = []
    for a, b in bounds:
        f = a + 50
        n = int((b - 50 - f) // 200)
        out += [(a, f, None), (f, f + 200 * n, '200х%d' % n), (f + 200 * n, b, None)]
    return sorted(out + segs)


def place(pts, vert):
    """dims of one chain; short texts staggered on two sides of the dim line"""
    res, k = [], 0
    for p, q, t in pts:
        L = q - p
        op = {'t': 'dim', 'h': '2B4879' if vert else '2B4846', 'rot': math.pi / 2 if vert else 0}
        if vert: op.update(p1=P(SX1, p), p2=P(SX1, q), dl=P(SX1 + CH, p))
        else: op.update(p1=P(p, SY1), p2=P(q, SY1), dl=P(p, SY1 + CH))
        if t: op['txt'] = t
        elif L < 700:
            side = 1 if k % 2 == 0 else -1; k += 1
            c = (p + q) / 2; off = 330 * side + (0 if side > 0 else -40)
            op['tx'] = P(SX1 + CH + off, c) if vert else P(c, SY1 + CH + off)
        else: k = 0
        res.append(op)
    return res


CH = 900
ops += place(chain(SX0, SX1, RX), False)
ops += place(chain(SY0, SY1, RY), True)
ops.append({'t': 'erase', 'h': ['2B4846', '2B4858', '2B486A', '2B4879', '2B488B', '2B489D', '2B48AC']})
# section mark, title, Разрез 1-1 detail
ops.append({'t': 'move', 'h': ['2B47A4'], 'd': [OX - (AX0 + 125), OY + 9000 - 478710]})
ops.append({'t': 'move', 'h': ['2B47A5'], 'd': [-170320 + DX - 252001, 496001 - 495714]})
DET = ['2B47A8', '2B47A9', '2B47AA', '2B47AB', '2B47AC', '2B47AD', '2B47AE', '2B47DF', '2B47E0', '2B47E1', '2B47F0', '2B4801',
       '2B4810', '2B4821', '2B4822', '2B4823', '2B4824', '2B4825', '2B4826', '2B4827', '2B4828', '2B4829', '2B4838', '2B4839', '2B47A7']
DET += ['2B47%02X' % i for i in range(0xAF, 0xDF)]
ops.append({'t': 'movegrp', 'h': DET, 'd': [32000, 11200]})
ops.append({'t': 'save'})
if __name__ == '__main__':
    print(chain(SX0, SX1, RX)); print(chain(SY0, SY1, RY))
    out = gx.run(ops, 'g62')
    print([l for l in out.splitlines() if 'ERR' in l or 'fail' in l or 'done' in l or 'no ' in l][:20])
