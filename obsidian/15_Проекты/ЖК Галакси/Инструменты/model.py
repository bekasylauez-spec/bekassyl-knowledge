# Building model of ЖК Галакси Тип А6 С2 in the coordinates of the user's sheet 2.1:
# x from axis 1, y from axis А/1, mm. Plan geometry = user's 2.1 (basement) + LIRA storey changes mapped onto it.
import pickle, os
HERE = os.path.dirname(os.path.abspath(__file__))

AX_X = {'1': 0, '2': 6800, '3': 13250, '4': 20050}
AX_Y = {'А/1': 0, 'А': 5000, 'Б': 14750, 'В': 22750, 'В/1': 28750}

# wall rectangles (x0, y0, x1, y1)
COMMON = [
    (125, -125, 1225, 125), (125, 22625, 1225, 22875), (125, 13725, 3225, 13975),          # axis 1 flanges, L
    (18825, -125, 19925, 125), (18825, 22625, 19925, 22875), (16825, 13725, 19925, 13975),  # axis 4 flanges, L
    (5875, -125, 6675, 125), (6925, -125, 7725, 125), (5375, 7425, 6675, 7675), (6925, 7425, 8225, 7675),       # T axis 2 flanges
    (12325, -125, 13125, 125), (13375, -125, 14175, 125), (11825, 7425, 13125, 7675), (13375, 7425, 14675, 7675),  # T axis 3 flanges
    (6675, 15225, 6925, 18025), (6925, 15225, 10275, 15475), (6925, 17775, 10275, 18025),   # lift core
    (10275, 15225, 10525, 22875), (6675, 20575, 6925, 22875),                               # x=10.4 wall, axis 2 top stub
    (13125, 15225, 13375, 22875), (11625, 15225, 13125, 15475),                              # axis 3 stair wall, stair wall
]
BASEMENT = COMMON + [
    (-125, -125, 125, 22875), (19925, -125, 20175, 22875),                                   # outer walls (openings 1200 as symbols)
    (6675, -125, 6925, 7675), (13125, -125, 13375, 7675),                                    # T stems
]
BASE_OPENINGS = [(-125, 3225, 125, 4425), (-125, 18725, 125, 19925), (19925, 3225, 20175, 4425), (19925, 18725, 20175, 19925)]
TYPICAL = COMMON + [
    (-125, -125, 125, 3175), (-125, 5750, 125, 17100), (-125, 20375, 125, 22875),            # axis 1 (LIRA 0..3.175, 5.75..12.1, 15.375..17.75)
    (19925, -125, 20175, 2775), (19925, 5750, 20175, 15675), (19925, 20375, 20175, 22875),   # axis 4 (LIRA 0..2.775, 5.75..10.675, 15.375..17.75)
    (6675, -125, 6925, 2775), (6675, 6175, 6925, 7675),                                       # axis 2 stem (LIRA 0..2.775, 6.175..8.0)
    (13125, -125, 13375, 2775), (13125, 6175, 13375, 7675),                                   # axis 3 stem
]
# roof storey +19.700: parapets t=200 h=1500 (LIRA type 1), lift shaft to +21.450, stair walls to +22.400
ROOF_PARAPET = [(-125, -125, 20175, 75), (-125, 75, 75, 22675), (19975, 75, 20175, 22675),
                (-125, 22675, 10275, 22875), (13375, 22675, 20175, 22875)]
ROOF_LIFT = [(6675, 15225, 6925, 18025), (6925, 15225, 10275, 15475), (6925, 17775, 10275, 18025)]
ROOF_STAIR = [(10275, 15225, 10525, 22875), (13125, 15225, 13375, 22875)]
# +22.400 stair roof parapet t=200 h=700
STAIR_PARAPET = [(10275, 15225, 13375, 15425), (10275, 15425, 10475, 22675), (13175, 15425, 13375, 22675), (10275, 22675, 13375, 22875)]

# Км-1 row −1250: 500×500; Км-2 rows 23100/28600: 600×600 per LIRA (Bekassyl 04.11), edge ones flush with the slab edge
COLUMNS = [(x0, -1250, x0 + 500, -750) for x0 in (-125, 6550, 13000, 19675)] +           [(x0, yc - 300, x0 + 600, yc + 300) for yc in (23350, 28850) for x0 in (-125, 6500, 12950, 19575)]

FM = (-825, -1950, 20875, 29800)            # user's Фм contour
PODG = (-925, -2050, 20975, 29900)
SLAB_BIG = (-125, -3275, 20175, 31175)       # LIRA −0.1/+3.95 slab −3.275..26.175 mapped
SLAB_TYP = (-125, -125, 20175, 22875)
SLAB_LIFT = (6675, 15225, 10525, 18025)      # +21.450
SLAB_STAIR = (10275, 15225, 13375, 22875)    # +22.400

# levels (top of element), mm
LEV = [-4650, -100, 3950, 7100, 10250, 13400, 16550, 19700]
T_SLAB = 250; T_FM = 700; T_PODG = 100


def fy(y):
    """LIRA y (m) -> user y (mm): below 8.0 unchanged, above 8.875 +5000, linear between."""
    y = y * 1000.0
    if y <= 8000: return y
    if y >= 8875: return y + 5000
    return 8000 + (y - 8000) * (13875 - 8000) / 875.0


def boxes():
    """3D boxes (kind, x0, y0, x1, y1, z0, z1) of the structure (walls, columns, Фм, slabs, parapets)."""
    B = []
    B.append(('podg',) + PODG + (-4650 - T_FM - T_PODG, -4650 - T_FM))
    B.append(('fm',) + FM + (-4650 - T_FM, -4650))
    for w in BASEMENT: B.append(('wall',) + w + (-4650, -100 - T_SLAB))
    for c in COLUMNS: B.append(('col',) + c + (-4650, -100 - T_SLAB))
    for c in COLUMNS: B.append(('col',) + c + (-100, 3950 - T_SLAB))
    for i in range(1, 7):                       # storeys −0.1..19.7
        z0, z1 = LEV[i], LEV[i + 1] - T_SLAB
        for w in TYPICAL: B.append(('wall',) + w + (z0, z1))
    for w in ROOF_PARAPET: B.append(('wall',) + w + (19700, 21200))
    for w in ROOF_LIFT: B.append(('wall',) + w + (19700, 21450 - T_SLAB))
    for w in ROOF_STAIR: B.append(('wall',) + w + (19700, 22400 - T_SLAB))
    for w in STAIR_PARAPET: B.append(('wall',) + w + (22400, 23100))
    B.append(('slab',) + SLAB_LIFT + (21450 - T_SLAB, 21450))
    B.append(('slab',) + SLAB_STAIR + (22400 - T_SLAB, 22400))
    return B


def lira_plates():
    """LIRA slabs (type 5) and stairs (type 2) as quads in user coords: list of (kind, [(x,y,z)...])."""
    hor, ver, bars = pickle.load(open(os.path.join(HERE, 'lira6', 'g.pkl'), 'rb'))
    els, nodes = pickle.load(open(os.path.join(HERE, 'lira6', 'm.pkl'), 'rb'))
    out = []
    for r in els:
        t, st = int(r[0]), int(r[1])
        if t not in (41, 42, 44) or st not in (2, 5): continue
        ns = [nodes[int(i) - 1] for i in r[2:]]
        zs = [n[2] for n in ns]
        if st == 5 and max(zs) - min(zs) > 1e-3: continue
        if st == 5 and (abs(zs[0] - 21.45) < 1e-3 or abs(zs[0] - 22.4) < 1e-3): continue   # drawn from the plan model
        pts = [(n[0] * 1000.0, fy(n[1]), n[2] * 1000.0) for n in ns]
        out.append(('slab' if st == 5 else 'stair', pts))
    return out
