# ---------------- node «Б» (1:50) and mesh С1 (1:25), own drawing instead of the template ones
ERASE_NEW += [PRE + r['old'] for r in R if 8300 < r['e'][0] and r['e'][2] < 20600 and 9800 < r['e'][1] and r['e'][3] < 13600
              and r['old'] not in ('18D64',) and not (15300 < r['e'][0] and r['e'][2] < 18600 and r['e'][3] < 7000)]
NX, NY = 10200, 10500                      # node: column centre x, beam bottom y
zs0, hb0 = col['nodes'][0]
def Nd(y, z): return W(NX + y, NY + z - (zs0 - hb0))
pl('3E8749', [Nd(-C.BY / 2, zs0 - hb0 - 500), Nd(-C.BY / 2, zs0 - hb0)]); pl('3E8749', [Nd(C.BY / 2, zs0 - hb0 - 500), Nd(C.BY / 2, zs0 - hb0)])
for s_ in (-1, 1):
    a = s_ * C.BY / 2; b = s_ * (C.BY / 2 + 500)
    pl('3E8749', [Nd(a, zs0 - hb0), Nd(b, zs0 - hb0)]); pl('3E8749', [Nd(a, zs0 + 0), Nd(b, zs0)])
    ln([Nd(b, zs0 + 120), Nd(b, zs0 - hb0 / 2 + 50), Nd(b - s_ * 50, zs0 - hb0 / 2), Nd(b + s_ * 50, zs0 - hb0 / 2 - 30), Nd(b, zs0 - hb0 / 2 - 80), Nd(b, zs0 - hb0 - 120)], 'Размеры', 5)
ln([Nd(-C.BY / 2 - 500, zs0), Nd(C.BY / 2 + 500, zs0)], 'Размеры', 5)
for y in C.YS: pl('3E879A', [Nd(y, zs0 - hb0 - 500), Nd(y, zs0 - 20)], layer='диам28')
mz = list(range(int(zs0 - hb0 + 50), int(zs0 - 49), 100))
for z in mz: ln([Nd(-C.BY / 2 + 20, z), Nd(C.BY / 2 - 20, z)], 'диам10', 30)
ch = [zs0 - hb0, mz[0], mz[-1], zs0]
for k, (a, b) in enumerate(zip(ch, ch[1:])):
    t_ = '100х%d' % (len(mz) - 1) if k == 1 else None
    tx_ = None if k == 1 else W(NX + C.BY / 2 + 860, NY + (a + b) / 2 - (zs0 - hb0) + (-60 if k == 0 else 60))
    dim('3E8855', Nd(C.BY / 2, a), Nd(C.BY / 2, b), W(NX + C.BY / 2 + 650, 0), True, t_, tx_)
dim('3E874A', Nd(-C.BY / 2, zs0 - hb0), Nd(-C.BY / 2, zs0), W(NX - C.BY / 2 - 900, 0), True)
for a, b in ((-C.BY / 2, -C.BY / 2 + 20), (-C.BY / 2 + 20, C.BY / 2 - 20), (C.BY / 2 - 20, C.BY / 2)):
    tx_ = W(NX + a - 150, NY - 900) if b - a < 100 and a < 0 else (W(NX + b + 150, NY - 900) if b - a < 100 else None)
    dim('3E8855', Nd(a, zs0 - hb0 - 500), Nd(b, zs0 - hb0 - 500), W(0, NY - 800), False, None, tx_)
note('С1', '%d шт.' % len(mz), Nd(-C.BY / 2 + 20, mz[2]), W(NX - C.BY / 2 - 300, NY + 300), 'Oblique')
ERASE_NEW += [PRE + '18D72', PRE + '18D73']
add(t='moveto', h=PRE + '18D64', idx=0, to=W(NX - 1500, NY + hb0 + 700))
add(t='settext', h=PRE + '18D64', s='%%UУзел Б. Расположение сеток С1')
# mesh С1 plan 1:25
MX, MY = 15000, 11400
def M(x, y): return W(MX + 2 * x, MY + 2 * y)
a_, b_ = C.MESH
xb = list(range(30, a_ - 29, 100)); yb_ = list(range(30, b_ - 29, 100))
for y in yb_: ln([M(0, y), M(a_, y)], 'диам10', 30)
for x in xb: ln([M(x, 0), M(x, b_)], 'диам10', 30)
dim('18CF8', M(0, 0), M(a_, 0), M(0, -260), False)
for k, (a, b) in enumerate(zip([0, xb[0], xb[-1]], [xb[0], xb[-1], a_])):
    dim('18CF8', M(a, 0), M(b, 0), M(0, -120), False, '100х%d' % (len(xb) - 1) if k == 1 else None,
        None if k == 1 else (M(a - 70, -200) if k == 0 else M(b + 70, -200)))
dim('18CF8', M(a_, 0), M(a_, b_), M(a_ + 260, 0), True)
for k, (a, b) in enumerate(zip([0, yb_[0], yb_[-1]], [yb_[0], yb_[-1], b_])):
    dim('18CF8', M(a_, a), M(a_, b), M(a_ + 120, 0), True, '100х%d' % (len(yb_) - 1) if k == 1 else None,
        None if k == 1 else (M(a_ + 200, a - 70) if k == 0 else M(a_ + 200, b + 70)))
note('10', '(%%C10) ш.100', M(xb[2], yb_[-2]), M(-160, b_ + 120), 'Oblique')
note('11', '(%%C10) ш.100', M(xb[-2], yb_[3]), M(-160, yb_[3] - 300), 'Oblique')
h = clone('18CB6'); add(t='settext', h=h, s='{\LСетка С1}')
add(t='moveto', h=h, idx=0, to=M(0, b_ + 330))

add(t='erase', h=ERASE_NEW)
add(t='vpset2', layout=SNO, media='ISO_full_bleed_A2_(594.00_x_420.00_MM)', win=[X0, Y0, X0 + 29700, Y0 + 21000], scale=50)
add(t='save')
json.dump(O, open('ops/g4_%s.json' % MARK, 'w', encoding='utf-8'), ensure_ascii=False)
print(len(O), 'ops, erase', len(ERASE_NEW))
if RUN:
    out = ab.run(O, 'g4', 1800)
    print('\n'.join(l for l in out.splitlines() if 'ERR' in l or 'errors' in l or 'no prop' in l or 'xception' in l)[-2500:])
