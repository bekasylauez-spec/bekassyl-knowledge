import shutil
shutil.copy('gen3.py', 'gen3_sq.py')
s = open('gen3.py', encoding='utf-8').read()
def R(a, b_, cnt=1):
    global s
    assert s.count(a) == cnt, (a[:70], s.count(a))
    s = s.replace(a, b_)

R("""b, nf, D = float(TY['b']), int(TY['nf']), float(TY['D'])""",
  """b, D = float(TY['b']), float(TY['D'])
h = float(TY.get('h', b)); nb = int(TY.get('nb', TY.get('nf', 3))); nh = int(TY.get('nh', nb)); nf = nb   # b = x (elevation face), h = y""")
R("""n = 4 * (nf - 1)
facepos = [e + k * (b - 2 * e) / (nf - 1) for k in range(nf)]
step = (b - 2 * e) / (nf - 1)
NPIN = 0 if nf <= 3 else 2 * (nf - 2)""",
  """n = 2 * nb + 2 * (nh - 2)
fpb = [e + k * (b - 2 * e) / (nb - 1) for k in range(nb)]
fph = [e + k * (h - 2 * e) / (nh - 1) for k in range(nh)]
facepos = fpb
DIAMOND = (nb == 3 and nh == 3 and abs(b - h) < 1)
NPB, NPH = nb - 2, nh - 2                               # S-pins: vertical (span h) at inner b-face bars, horizontal (span b) at inner h-face bars
NPIN = 0 if DIAMOND else NPB + NPH""")
R("""    pts = set()
    for p_ in facepos:
        for q in (facepos[0], facepos[-1]):
            pts.add((p_, q)); pts.add((q, p_))
    return sorted""",
  """    pts = set()
    for p_ in fpb: pts.add((p_, fph[0])); pts.add((p_, fph[-1]))
    for q in fph: pts.add((fpb[0], q)); pts.add((fpb[-1], q))
    return sorted""")
R("""[[0, SX + ox + Kx * b, SY + oy], [1, SX + ox + Kx * b, SY + oy + Kx * b], [2, SX + ox, SY + oy + Kx * b], [3, SX + ox, SY + oy]]""",
  """[[0, SX + ox + Kx * b, SY + oy], [1, SX + ox + Kx * b, SY + oy + Kx * h], [2, SX + ox, SY + oy + Kx * h], [3, SX + ox, SY + oy]]""")
R("""    xs = [0, 40, b / 2, b - 40, b]
    for h_, i in ((b40l, 0)""",
  """    xs = [0, 40, b / 2, b - 40, b]; ys = [0, 40, h / 2, h - 40, h]
    for h_, i in ((b40l, 0)""")
R("""        add(t='dimpts', h=T(h_), p1=W(ox, oy + Kx * xs[i]), p2=W(ox, oy + Kx * xs[i + 1]), dl=W(xl1, oy + Kx * (xs[i] + xs[i + 1]) / 2))
    add(t='dimpts', h=T(l250b), p1=W(ox, oy), p2=W(ox, oy + Kx * b / 2), dl=W(xl2, oy + Kx * b / 4))
    add(t='dimpts', h=T(l250t), p1=W(ox, oy + Kx * b / 2), p2=W(ox, oy + Kx * b), dl=W(xl2, oy + Kx * 3 * b / 4))""",
  """        add(t='dimpts', h=T(h_), p1=W(ox, oy + Kx * ys[i]), p2=W(ox, oy + Kx * ys[i + 1]), dl=W(xl1, oy + Kx * (ys[i] + ys[i + 1]) / 2))
    add(t='dimpts', h=T(l250b), p1=W(ox, oy), p2=W(ox, oy + Kx * h / 2), dl=W(xl2, oy + Kx * h / 4))
    add(t='dimpts', h=T(l250t), p1=W(ox, oy + Kx * h / 2), p2=W(ox, oy + Kx * h), dl=W(xl2, oy + Kx * 3 * h / 4))""")
R("""add(t='dimtx', h=T(l40t), at=W(xl1, oy + Kx * b + 300))
    for h_, yy in ((l250b, oy + Kx * b / 4), (l250t, oy + Kx * 3 * b / 4)):""",
  """add(t='dimtx', h=T(l40t), at=W(xl1, oy + Kx * h + 300))
    for h_, yy in ((l250b, oy + Kx * h / 4), (l250t, oy + Kx * 3 * h / 4)):""")
R("""    av, ah = axes; cx, cy = ox + Kx * b / 2, oy + Kx * b / 2
    add(t='spmove', h=T(av), items=[[0, SX + cx, SY + oy + Kx * b + (900 if nf > 3 else 720)]""",
  """    av, ah = axes; cx, cy = ox + Kx * b / 2, oy + Kx * h / 2
    add(t='spmove', h=T(av), items=[[0, SX + cx, SY + oy + Kx * h + (900 if nb > 3 else 720)]""")
R("""S1 = (9314.0, 17388.0 - (b - 400))""", """S1 = (9314.0, 17388.0 - (h - 400))""")
R("""S2 = (13824.0, 17441.0 - (b - 400))""", """S2 = (13824.0, 17441.0 - (h - 400))""")
R("""R2 = Kx * b - 128 - 96
add(t='dyn', h=T('1113BF'), prop='Расстояние1', value=R2); add(t='dyn', h=T('1113BF'), prop='Расстояние2', value=R2)""",
  """add(t='dyn', h=T('1113BF'), prop='Расстояние1', value=Kx * b - 224); add(t='dyn', h=T('1113BF'), prop='Расстояние2', value=Kx * h - 224)""")
R("""    span = Kx * (b - 2 * e)
    for k in range(1, nf - 1):
        q = Kx * facepos[k]
        for j, (ins, ang) in enumerate(((W(ox + Kx * e, oy + q), 0.0), (W(ox + q, oy + Kx * e), math.pi / 2))):
            tg = PRE + 'PIN%d_%d' % (k, j)
            add(t='clone', h=PRE + 'PIN:19EC6', base=[SX + 40000, SY], to=ins, tag=tg)
            if ang: add(t='xform', h=tg, base=ins, to=ins, ang=ang)
            add(t='dyn', h=tg, prop='Расстояние1', value=span + 1)""",
  """    PINS = [(W(ox + Kx * fpb[k], oy + Kx * e), math.pi / 2, Kx * (h - 2 * e), 'v%d' % k) for k in range(1, nb - 1)]
    PINS += [(W(ox + Kx * e, oy + Kx * fph[k]), 0.0, Kx * (b - 2 * e), 'h%d' % k) for k in range(1, nh - 1)]
    for ins, ang, span, nm_ in PINS:
        tg = PRE + 'PIN' + nm_
        add(t='clone', h=PRE + 'PIN:19EC6', base=[SX + 40000, SY], to=ins, tag=tg)
        if ang: add(t='xform', h=tg, base=ins, to=ins, ang=ang)
        add(t='dyn', h=tg, prop='Расстояние1', value=span + 1)""")
R("""top = [p_ for p_ in B if abs(p_[1] - (oy + Kx * (b - e))) < 1]""", """top = [p_ for p_ in B if abs(p_[1] - (oy + Kx * (h - e))) < 1]""")
R("""origin=W(ox + Kx * b + 520, oy + Kx * b + 230), targets=[W(*p_) for p_ in sorted(top""",
  """origin=W(ox + Kx * b + 520, oy + Kx * h + 230), targets=[W(*p_) for p_ in sorted(top""")
R("""t2 = W(ox + Kx * b * 0.75, oy + Kx * b * 0.75) if NPIN == 0 else W(ox + Kx * b * 0.75, oy + Kx * facepos[1])
add(t='spmove', h=T('11190A'), items=[[0, SX + ox + Kx * b + 520, SY + oy + Kx * b / 2 + 120], [1, SX + ox + Kx * b - 64, SY + oy + Kx * b * 0.72], [2, t2[0], t2[1]]])
add(t='mcset', h=T('11190A'), set={'FirstLine': 'Х1;Х2' if NPIN == 0 else 'Х1;Шп1'})""",
  """t2 = W(ox + Kx * b * 0.75, oy + Kx * h * 0.75) if NPIN == 0 else (W(ox + Kx * b * 0.75, oy + Kx * fph[1]) if NPH else W(ox + Kx * fpb[1], oy + Kx * h * 0.3))
TWO_PINS = bool(NPB and NPH and abs(b - h) > 1)
HLAB = 'Х1;Х2' if NPIN == 0 else ('Х1;Шп1;Шп2' if TWO_PINS else 'Х1;Шп1')
add(t='spmove', h=T('11190A'), items=[[0, SX + ox + Kx * b + 520, SY + oy + Kx * h / 2 + 120], [1, SX + ox + Kx * b - 64, SY + oy + Kx * h * 0.72], [2, t2[0], t2[1]]])
add(t='mcset', h=T('11190A'), set={'FirstLine': HLAB})""")
R("""add(t='pl', p=[Pp(e, e), Pp(b - e, b - e)], layer='диам16', lw=40); add(t='pl', p=[Pp(e, b - e), Pp(b - e, e)], layer='диам16', lw=40)
for k in range(1, nf - 1):
    q = facepos[k]
    add(t='pl', p=[Pp(q, e), Pp(q, b - e)], layer='диам16', lw=40); add(t='pl', p=[Pp(e, q), Pp(b - e, q)], layer='диам16', lw=40)""",
  """add(t='pl', p=[Pp(e, e), Pp(b - e, h - e)], layer='диам16', lw=40); add(t='pl', p=[Pp(e, h - e), Pp(b - e, e)], layer='диам16', lw=40)
for q in fpb[1:-1]: add(t='pl', p=[Pp(q, e), Pp(q, h - e)], layer='диам16', lw=40)
for q in fph[1:-1]: add(t='pl', p=[Pp(e, q), Pp(b - e, q)], layer='диам16', lw=40)""")
R("""[1, SX + ox + Kx * (b - e) - 40, SY + oy + Kx * (b - e) - 40],
                                      [2, SX + ox + Kx * facepos[-2], SY + oy + Kx * b * 0.3], [3, SX + ox + Kx * facepos[-2], SY + oy + Kx * b * 0.3], [4, SX + ox + Kx * facepos[-2], SY + oy + Kx * b * 0.3]])""",
  """[1, SX + ox + Kx * (b - e) - 40, SY + oy + Kx * (h - e) - 40 * h / b],
                                      [2, SX + ox + Kx * fpb[-2], SY + oy + Kx * h * 0.3], [3, SX + ox + Kx * fpb[-2], SY + oy + Kx * h * 0.3], [4, SX + ox + Kx * fpb[-2], SY + oy + Kx * h * 0.3]])""")
# mesh С1: element A = rods along b (length h-40) + one bar (b-40); element B = rods along h (length b-40) + one bar (h-40)
R("""LM = 2 * (b - 40); rods = [35 + 100 * i for i in range(int((b - 40 - 35 - 100) // 100) + 1)]
x0, y0 = 13769.0, 11403.0
rx = [x0 + 2 * v for v in rods]
for x in rx: add(t='lineset', h=T('111466'), s=W(x, y0), e=W(x, y0 + LM))
yc = y0 + LM - 70
add(t='lineset', h=T('111467'), s=W(x0, yc), e=W(x0 + LM, yc))""",
  """LMb, LMh = 2 * (b - 40), 2 * (h - 40)
rodsf = lambda w: [35 + 100 * i for i in range(int((w - 40 - 35 - 100) // 100) + 1)]
rods, rodsh = rodsf(b), rodsf(h)
x0, y0 = 13769.0, 11403.0 - (LMh - LMb)
rx = [x0 + 2 * v for v in rods]
for x in rx: add(t='lineset', h=T('111466'), s=W(x, y0), e=W(x, y0 + LMh))
yc = y0 + LMh - 70
add(t='lineset', h=T('111467'), s=W(x0, yc), e=W(x0 + LMb, yc))""")
R("""add(t='dimpts', h=T('111468'), p1=W(rx[-1], y0), p2=W(x0 + LM, yc))
add(t='dimpts', h=T('111428'), p1=W(x0 + LM, yc), p2=W(x0, yc))
add(t='dimpts', h=T('111437'), p1=W(x0 + LM, yc), p2=W(rx[-1], y0 + LM))
add(t='dimpts', h=T('111448'), p1=W(x0 + LM, yc), p2=W(rx[-1], y0))
add(t='dimpts', h=T('111457'), p1=W(rx[-1], y0 + LM), p2=W(rx[-1], y0))""",
  """add(t='dimpts', h=T('111468'), p1=W(rx[-1], y0), p2=W(x0 + LMb, yc))
add(t='dimpts', h=T('111428'), p1=W(x0 + LMb, yc), p2=W(x0, yc))
add(t='dimpts', h=T('111437'), p1=W(x0 + LMb, yc), p2=W(rx[-1], y0 + LMh))
add(t='dimpts', h=T('111448'), p1=W(x0 + LMb, yc), p2=W(rx[-1], y0))
add(t='dimpts', h=T('111457'), p1=W(rx[-1], y0 + LMh), p2=W(rx[-1], y0))""")
R("""xa, yb = 17797.0, 11121.0
ry = [yb + 2 * v for v in rods]
for y in ry: add(t='lineset', h=T('1114DA'), s=W(xa, y), e=W(xa + LM, y))
xr = xa + LM - 70
add(t='lineset', h=T('1114DB'), s=W(xr, yb), e=W(xr, yb + LM))""",
  """xa, yb = 17797.0, 11121.0 - (LMh - LMb)
ry = [yb + 2 * v for v in rodsh]
for y in ry: add(t='lineset', h=T('1114DA'), s=W(xa, y), e=W(xa + LMb, y))
xr = xa + LMb - 70
add(t='lineset', h=T('1114DB'), s=W(xr, yb), e=W(xr, yb + LMh))""")
R("""add(t='dimtext', h=T('1114EE'), s='100х%d' % (len(rods) - 1))""", """add(t='dimtext', h=T('1114EE'), s='100х%d' % (len(rodsh) - 1))""")
R("""add(t='dimpts', h=T('1114DC'), p1=W(xa, ry[-1]), p2=W(xr, yb + LM))
add(t='dimpts', h=T('11149C'), p1=W(xr, yb), p2=W(xr, yb + LM))
add(t='dimpts', h=T('1114AB'), p1=W(xr, yb + LM), p2=W(xa + LM, ry[-1]))
add(t='dimpts', h=T('1114BC'), p1=W(xr, yb + LM), p2=W(xa, ry[-1]))
add(t='dimpts', h=T('1114CB'), p1=W(xa + LM, ry[-1]), p2=W(xa, ry[-1]))""",
  """add(t='dimpts', h=T('1114DC'), p1=W(xa, ry[-1]), p2=W(xr, yb + LMh))
add(t='dimpts', h=T('11149C'), p1=W(xr, yb), p2=W(xr, yb + LMh))
add(t='dimpts', h=T('1114AB'), p1=W(xr, yb + LMh), p2=W(xa + LMb, ry[-1]))
add(t='dimpts', h=T('1114BC'), p1=W(xr, yb + LMh), p2=W(xa, ry[-1]))
add(t='dimpts', h=T('1114CB'), p1=W(xa + LMb, ry[-1]), p2=W(xa, ry[-1]))""")
open('gen3.py', 'w', encoding='utf-8').write(s)
print('patched')
