# ---------------- elevation: Фм (part, with breaks), подготовка, column, beam stubs, console
z1 = col['z1']; zl_top = z1 or top
PADH = 1000
fm = [E(-PADH, -1500), E(PADH, -1500), E(PADH, -500), E(-PADH, -500)]
pl('3E8793', [E(-PADH, -500), E(PADH, -500)]); pl('3E8793', [E(-PADH, -1500), E(PADH, -1500)])
for s_ in (-1, 1):
    b = s_ * PADH
    ln([E(b, -400), E(b, -930), E(b - s_ * 60, -1000), E(b + s_ * 60, -1040), E(b, -1100), E(b, -1700)], 'Размеры', 5)
th = clone('3E8792'); add(t='hatchset', h=th, loops=[fm])
pl('3E8793', [E(-PADH, -1600), E(PADH, -1600)])
pl('3E8749', [E(-C.BY / 2, -500), E(C.BY / 2, -500), E(C.BY / 2, zl_top), E(-C.BY / 2, zl_top)], closed=True)
if z1:
    pl('3E8749', [E(-C.UB / 2, z1), E(C.UB / 2, z1), E(C.UB / 2, top), E(-C.UB / 2, top)], closed=True)
for zs, hb, sides in col['nodes']:
    if sides is None: continue
    for s_ in ((-1, 1) if sides == 0 else (sides,)):
        a = s_ * C.BY / 2; b = s_ * (C.BY / 2 + 700)
        pl('3E8749', [E(a, zs - hb), E(b, zs - hb)]); pl('3E8749', [E(a, zs), E(b, zs)])
        zz = [E(b, zs + 150), E(b, zs - hb / 2 + 60), E(b - s_ * 60, zs - hb / 2), E(b + s_ * 60, zs - hb / 2 - 40), E(b, zs - hb / 2 - 100), E(b, zs - hb - 150)]
        ln(zz, 'Размеры', 5)
        if zs < 8000: pl('3E8749', [E(a, zs - 200), E(b, zs - 200)])          # slab underside
CONS = col.get('cons')
if CONS:
    cl, ch_ = C.CONS['l'], C.CONS['h']
    pl('3E8749', [E(C.BY / 2, z1 - ch_), E(C.BY / 2 + cl, z1 - ch_ + 250), E(C.BY / 2 + cl, z1), E(C.BY / 2, z1)])

# ---------------- elevation bars
zb = sch['zend']
joints = sch['joints']
for y in C.YS:
    corner = y in (C.YS[0], C.YS[-1])
    js = [j + (600 if corner else 1200) for j in joints]
    for i_, zj in enumerate(js):
        z_to = js[i_ + 1] if i_ + 1 < len(js) else zb
        pl('3E879A', [E(y, zj), E(y, z_to)], layer='диам28')
        for s_ in (-1, 1):
            x0 = y + s_ * 14; x1 = y + s_ * 42
            pl('3E878C', [E(x0, zj - 140), E(x1, zj - 140), E(x1, zj + 140), E(x0, zj + 140)], closed=True, layer='диам28')
    pl('3E878D', [E(y, -1440), E(y, js[0])])                     # dowel Вп (dashed, see sheet 3.6)
if z1:
    for y in (-C.UO, C.UO):
        pl('3E879A', [E(y, z1 - C.ANCH), E(y, top - 20)], layer='диам28')
    pl('3E879A', [E(0, z1 + 50), E(0, top - 20)], layer='диам28')
HX = C.YS[-1] + C.OFF
UX = C.UO + C.OFF
st = C.storeys(col)
zone_marks = []
for lo, hi, hb in st:
    upper = bool(z1) and lo >= z1
    p, (n1, n2, n3), stp = C.colgeo.storey_hoops(lo, hi - hb)
    hx = UX if upper else HX
    for k in sorted({0, n1, n1 + n2, len(p) - 1}):
        ln([E(-hx, p[k]), E(hx, p[k])], 'диам10', 30)
    zone_marks.append(p)
    if hb:
        for zm in range(int(hi - hb + 50), int(hi - 49), 100):
            ln([E(-C.BY / 2 + 20, zm), E(C.BY / 2 - 20, zm)], 'диам10', 30)
# П elements: top of the lower part (Ск1/Ск2) and of the upper part (Ск3)
pl('3E879A', [E(C.YS[0] - 22, zb - C.LAP_N), E(C.YS[0] - 22, zb - 8), E(C.YS[-1] + 22, zb - 8), E(C.YS[-1] + 22, zb - C.LAP_N)], layer='диам16')
if z1:
    zt = top - 20
    pl('3E879A', [E(-C.UO - 22, zt - C.LAP_N), E(-C.UO - 22, zt - 8), E(C.UO + 22, zt - 8), E(C.UO + 22, zt - C.LAP_N)], layer='диам16')
if CONS:
    zk = z1 - 60
    ln([E(C.YS[0] + 30, zk - 400), E(C.YS[0] + 30, zk), E(C.BY / 2 + cl - 30, zk), E(C.BY / 2 + cl - 30, zk - 600)], 'диам28', 40)
    for yk in range(int(C.BY / 2 + 60), int(C.BY / 2 + cl - 29), 100):
        zbk = z1 - ch_ + 250 * (yk - C.BY / 2) / cl + 40
        ln([E(yk, zbk), E(yk, z1 - 40)], 'диам10', 30)

# ---------------- elevation dims: left level chain + overall, right hoop chain
LV = sorted(set([-1500, bot] + [zs - hb for zs, hb, _ in col['nodes']] + [zs for zs, hb, _ in col['nodes']] + [top] + ([z1] if z1 else [])))
XL1, XL2 = FL - 1100, FL - 1500
for a, b in zip(LV, LV[1:]):
    dim('3E874A', E(-C.BY / 2, a), E(-C.BY / 2, b), W(XL1, 0), True)
dim('3E874A', E(-C.BY / 2, bot), E(-C.BY / 2, top), W(XL2, 0), True)
P, segs = C.colgeo.chain([bot] + [s[1] for s in st], [s[2] for s in st])
XR = FR + (650 + C.CONS['l'] if CONS else 650)
colx = 0
for (y1, y2, stp, n) in segs:
    txt = ('%dх%d' % (stp, n)) if n > 1 else None
    small = (y2 - y1) < 450
    tx = None
    if small:
        tx = W(XR + (260 if colx == 0 else 520), YB + (y1 + y2) / 2); colx = 1 - colx
    else:
        colx = 0
    dim('3E8855', E(C.BY / 2, y1), E(C.BY / 2, y2), W(XR, 0), True, txt, tx)

# ---------------- level marks: first = template «-2.000» (fixed text), the rest clones of 3E8738 (stored zero fixed by levbase)
add(t='move', h=[T('3E8739')], d=[0, YB - 11700 - 500])
fmt = lambda v: ('+' if v > 0 else '-') + ('%.3f' % abs(v / 1000)).replace('.', ',')
LVM = LV
for k, z in enumerate(LVM):
    if k == 0:
        add(t='move', h=[T('3E8737')], d=[FL - 4103, YB + z - 9700])
        add(t='levelval', h=T('3E8737'), old='-2.000', value=('%.3f' % (z / 1000)).replace('.', ','))
        continue
    h0 = clone('3E8738')
    add(t='move', h=[h0], d=[FL - 4103, YB + z - 11700])
    tg = 'lv_%s_%d' % (MARK, k)
    add(t='levbase', h=h0, old=Y0 + YB + 500, new=Y0 + YB, tol=3, tag=tg)
    add(t='levelval', h=tg, old=fmt(z - 500), value=fmt(z))
ERASE_NEW += [T('3E8738'), T('3E873B'), T('3E873A')]

# ---------------- callouts on the elevation (left, shelf away from the column)
OX = FL - 230
lows = [s for s in st if not (z1 and s[0] >= z1)]
for i_, (lo, hi, hb) in enumerate(lows):
    zc_ = lo + (hi - hb - lo) * 0.62
    note(str(2 * i_ + 1), '(%%C28)', E(C.YS[0], zc_), W(OX, YB + zc_ + 300), 'Oblique')
    note(str(2 * i_ + 2), '(%%C28)', E(C.YS[1], zc_ + 900), W(OX, YB + zc_ + 1200), 'Oblique')
    note('С1', '%d шт.' % (int((hb - 100) // 100) + 1), E(-C.BY / 2 + 20, hi - hb / 2), W(OX, YB + hi - hb / 2 - 450), 'Oblique')
hz = zone_marks[0]
note('Х1...Х3', '(%%C10)', E(-HX, hz[len(hz) // 3]), W(OX, YB + hz[len(hz) // 3] + 300), 'Oblique')
note('Н2', '(%%C28)', E(C.YS[0] - 42, bot + 600), W(OX, YB + bot + 950), 'Oblique')
note('Вп1, Вп2', 'см. лист 3.6', E(C.YS[-1], -1000), W(FR + 1000, YB - 1100), 'Oblique')
if z1:
    up = [s for s in st if s[0] >= z1][0]
    zc_ = (up[0] + up[1]) / 2
    note(str(len(joints) * 2 + 1), '(%%C28)', E(-C.UO, zc_), W(OX, YB + zc_ + 300), 'Oblique')
    hzu = zone_marks[-1]
    note('Х4, Х5', '(%%C10)', E(-UX, hzu[len(hzu) // 4]), W(OX, YB + hzu[len(hzu) // 4] - 350), 'Oblique')
    note('Ск1, Ск2', '(%%C16)', E(C.YS[0] - 22, zb - 150), W(OX - 500, YB + zb + 250), 'Oblique')
    add(t='moveto', h=T('3E8E9D'), idx=1, to=E(C.UO + 22, top - 140))
    add(t='mcset', h=T('3E8E9D'), set={'FirstLine': 'Ск3', 'SecondLine': '(%%C16)', 'Origin': W(CX + 900, YB + top + 950), 'Angle': 0.0, 'Arrow': 'Oblique'})
else:
    add(t='moveto', h=T('3E8E9D'), idx=1, to=E(C.YS[-1] + 22, zb - 120))
    add(t='mcset', h=T('3E8E9D'), set={'FirstLine': 'Ск1, Ск2', 'SecondLine': '(%%C16)', 'Origin': W(FR + 900, YB + top + 950), 'Angle': 0.0, 'Arrow': 'Oblique'})
if CONS:
    note('К1', '(%%C28)', E(C.BY / 2 + cl - 30, zk - 300), W(FR + cl + 450, YB + zk + 200), 'Oblique')
    note('Хк', '(%%C10)', E(C.BY / 2 + 360, z1 - 300), W(FR + cl + 450, YB + z1 - 700), 'Oblique')

# ---------------- section marks, knot, title
lo0, hi0, hb0_ = st[0]
zc = lo0 + (hi0 - hb0_ - lo0) * 0.40
add(t='spmove', h=T('3E8EA3'), items=[[0] + E(-C.BY / 2 - 450, zc), [1] + E(C.BY / 2 + 450, zc)])
add(t='secset', h=T('3E8EA3'), word='1')
if z1:
    zc2 = (up[0] + up[1]) / 2 + 500
    s2 = clone('3E8EA3')
    add(t='spmove', h=s2, items=[[0] + E(-C.UB / 2 - 450, zc2), [1] + E(C.UB / 2 + 450, zc2)])
    add(t='secset', h=s2, word='2')
    add(t='spmove', h=T('3E8E9A'), items=[[0] + E(-C.UB / 2 - 450, top + 450), [1] + E(C.UB / 2 + 450, top + 450)])
    add(t='secset', h=T('3E8E9A'), word='3')
else:
    add(t='spmove', h=T('3E8E9A'), items=[[0] + E(-C.BY / 2 - 450, top + 450), [1] + E(C.BY / 2 + 450, top + 450)])
    add(t='secset', h=T('3E8E9A'), word='2')
zs0, hb0 = col['nodes'][0][:2]
kc = E(0, zs0 - hb0 / 2)
add(t='mcset', h=T('3E8E99'), set={'Center': kc, 'Rack': [kc[0] - 1150, kc[1] - 1150], 'XRadius': 650.0, 'YRadius': 650.0, 'Knot': 'Б'})
add(t='settext', h=T('3E8736'), s='{\\LКолонна %s (%s шт.)}' % (MARK, col['n']))
add(t='moveto', h=T('3E8736'), idx=0, to=W(CX - 700, YB + top + 1900))

