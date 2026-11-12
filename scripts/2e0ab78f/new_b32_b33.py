def frag1(x0, yb):
    """Разрез 1-1 (армирование) — ернеу/вут фрагменті ×4 (аналог л.8 «Разрез 1-1»): x0 — r=rc парақ x-і, yb — Z_BOT парақ y-і"""
    k = 4.0; rc = 8600.0
    f1x, f1y = x0 - rc * k, yb - Z_BOT * k
    def F(r, z): return (f1x + r * k, f1y + z * k)
    lp = [F(rc, z_top(rc)), F(R_HT, Z_HT), F(R_WI, Z_JOINT), F(R_WO, Z_JOINT), F(R_WO, Z_FL), F(R_OUT, Z_FL), F(R_OUT, Z_BOT), F(R_B1, Z_B1), F(rc, z_bot(rc))]
    L.pl(lp, layer=L.L_THIN); L.brk(F(rc, z_top(rc) + 60), F(rc, z_bot(rc) - 160))
    L.line(F(R_WI, Z_JOINT), F(R_WI, Z_JOINT + 330), layer=L.L_THIN); L.line(F(R_WO, Z_JOINT), F(R_WO, Z_JOINT + 330), layer=L.L_THIN)
    L.brk(F(R_WI - 40, Z_JOINT + 330), F(R_WO + 40, Z_JOINT + 330))
    edge_arm(F, k, rc)
    yd = yb - 900
    L.dim((F(R_HT, 0)[0], yb - 200), (F(R_WI, 0)[0], yb - 200), (F(R_HT, 0)[0], yd), 0.0, 0.25,
          tx=(F(R_HT, 0)[0] + 1450, yd + 30))     # мәтін 1100-дің шығару сызығынан оңға
    L.chain_h([F(v, 0)[0] for v in (R_WI, R_WO, R_OUT)], yb - 200, yd, lfac=0.25)
    L.chain_h([F(v, 0)[0] for v in (RE - LP, RE, R_OUT)], yb - 200, yd - 1100, lfac=0.25)
    nd = int((RE - 50 - rc) // 100)                                      # төменгі тор нүктелерінің қадамы (edge_arm-дағы нүктелер)
    L.dim((F(RE - 50 - 100 * nd, 0)[0], yb - 200), (F(RE - 50, 0)[0], yb - 200), (F(rc, 0)[0], yd - 2200), 0.0, 0.25, txt='100хn')
    xv = F(R_OUT, 0)[0] + 900
    L.chain_v([F(0, v)[1] for v in (Z_BOT, Z_BOT + 50, Z_FL - 50, Z_FL)], F(R_OUT, 0)[0] + 150, xv, lfac=0.25)
    L.dim((F(R_OUT, 0)[0] + 150, F(0, Z_BOT)[1]), (F(R_OUT, 0)[0] + 150, F(0, Z_FL)[1]), (xv + 700, F(0, Z_BOT)[1]), math.pi / 2, 0.25)
    L.lev(Z_FL, F(R_OUT, Z_FL), 'R', ext=3300); L.lev(Z_BOT, F(R_OUT, Z_BOT), 'R', ext=3300); L.lev(Z_JOINT, F(R_WI, Z_JOINT), 'L', ext=3300)
    L.note('1', 'ш.100', F(8900, -1350), F(9000, z_top(9000) - 50)); L.note('1', 'ш.100', F(8850, -2900), F(9000, z_bot(9000) + 50))
    L.note('5', 'ш.100', F(11250, -1150), F(RE - 12, -1900)); L.note('6', 'ш.100', F(9060, -850), F(9700, -1612))
    L.note('7', '', F(9550, -500), F(9724, -1602), on='dot'); L.note('Вп1', 'ш.100, см. л. 3.5', F(10800, -600), F(R_WO - 49, -1100))
    L.note('Кр-1', 'ш.1200х1200', F(9150, -3250), F(9300, -2050))
    for r in (9200.0, 9450.0):                                           # Кр-1 шартты
        L.pl([F(r, z_bot(r) + 70), F(r, z_top(r) - 70)], layer='ф16_арм', lw=40)
    return F


def pr_plan(Pc):
    """Армирование приямка — план ×4 (аналог л.8 «Армирование днища приямка»): тор поз.2, радиал поз.3, сақина поз.4"""
    k = 4.0
    def Q_(x, y): return (Pc[0] + x * k, Pc[1] + y * k)
    L.circle(Pc, R_PT * k, layer=L.L_THIN); L.circle(Pc, R_PB * k, layer=L.L_THIN); L.circle(Pc, R_B3 * k, layer=L.L_THIN, ltype='HIDDEN', ltscale=30)
    L.circle(Pc, R_COL_O * k, layer=L.L_THIN); L.circle(Pc, R_COL_I * k, layer=L.L_THIN)
    for i in range(31):                                                  # поз.2 — днище торы ш.100 (қима 2-2: ±1500, ұшы ±1541)
        x = -1500.0 + 100 * i; h = math.sqrt(1541.0 ** 2 - x * x)
        D.bar([Q_(x, -h), Q_(x, h)]); D.bar([Q_(-h, x), Q_(h, x)])
    o = off([(R_PB, Z_PB), (R_PT, Z_PT)], -86)                           # поз.4 — жоғарғы тор сақиналары (қима 2-2 нүктелері)
    rings = [p[0] for p in along(o[0], o[1], 100, 50)]
    for r in rings: L.circle(Pc, r * k, layer='ф18_арм', lw=40)
    inn = off([(R_PB - 430, Z_PB), (R_PB, Z_PB), (R_PT, Z_PT), (R_PT + LP, z_top(R_PT + LP))], -68)
    r0, r1 = inn[0][0], inn[-1][0]
    a0 = math.radians(20.0); da = 100.0 / R_PT                           # поз.3 — радиал, ш.100 жиекте (бірнешеуі)
    for j in range(-3, 4):
        a = a0 + j * da; D.bar([Q_(r0 * math.cos(a), r0 * math.sin(a)), Q_(r1 * math.cos(a), r1 * math.sin(a))])
    L.ddim(Pc, R_PT * k, 145, lfac=0.25, tx_out=900); L.ddim(Pc, R_PB * k, 235, lfac=0.25, tx_out=-1400)
    hh = math.sqrt(1541.0 ** 2 - 1500.0 ** 2)
    L.chain_h([Q_(-1500, 0)[0], Q_(1500, 0)[0]], Q_(0, hh)[1], Pc[1] + R_PT * k + 700, lfac=0.25, texts=['100х30=3000'])
    L.section(2, (Pc[0] - R_PT * k - 1300, Pc[1]), (Pc[0] + R_PT * k + 1300, Pc[1]))
    L.note('2', 'ш.100', Q_(-1500, -1700), Q_(-1000, -1000))
    aa = a0 + 3 * da; L.note('3', 'ш.100', Q_(2900 * math.cos(aa) - 300, 2900 * math.sin(aa) + 600), Q_(2600 * math.cos(aa), 2600 * math.sin(aa)))
    a4 = math.radians(-40); L.note('4', 'ш.100', Q_((rings[-1] + 600) * math.cos(a4), (rings[-1] + 600) * math.sin(a4) - 300), Q_(rings[-1] * math.cos(a4), rings[-1] * math.sin(a4)))


def km_vyp(Kc):
    """Схема расположения выпусков в опору Км-1 — план ×4 (аналог л.8 «Схема расположения выпусков»)"""
    k = 4.0
    L.circle(Kc, R_COL_O * k, layer=L.L_THIN); L.circle(Kc, R_COL_I * k, layer=L.L_THIN)
    for r, n in ((651, Q.NVO), (449, Q.NVI)):
        for i in range(n):
            a = 2 * math.pi * i / n; D.dot((Kc[0] + r * k * math.cos(a), Kc[1] + r * k * math.sin(a)), 9 * k)
    L.ddim(Kc, R_COL_O * k, 200, lfac=0.25, tx_out=1500); L.ddim(Kc, R_COL_I * k, -20, lfac=0.25, tx_out=2600)
    L.chain_h([Kc[0] + v * k for v in (R_COL_I, R_COL_I + 40, 660, R_COL_O)], Kc[1], Kc[1] - R_COL_O * k - 700, lfac=0.25)
    a = 2 * math.pi * 5 / Q.NVO
    L.note('1', 'ш.100 (%d шт.)' % Q.NVO, (Kc[0] + 3500, Kc[1] + 3200), (Kc[0] + 651 * k * math.cos(a), Kc[1] + 651 * k * math.sin(a)), on='dot')
    a = 2 * math.pi * 10 / Q.NVI
    L.note('1', 'ш.100 (%d шт.)' % Q.NVI, (Kc[0] - 4200, Kc[1] + 3300), (Kc[0] + 449 * k * math.cos(a), Kc[1] + 449 * k * math.sin(a)), on='dot')


def b32():
    sh = L.Sheet('3.2', 'Схема расположения основной арматуры фундамента Фм-1')
    C = sh.P(17000, 25500)
    L.title('Схема расположения основной арматуры фундамента Фм-1', C[0] + 2500, sh.Y0 + 40500)
    L.circle(C, R_OUT, layer=L.L_THIN); L.circle(C, R_PT, layer=L.L_THIN); L.circle(C, R_B2, layer=L.L_THIN, ltype='HIDDEN', ltscale=30)
    L.circle(C, R_COL_O, layer=L.L_THIN); L.circle(C, R_COL_I, layer=L.L_THIN); L.hatch([L.ring_pts(C, R_COL_O), L.ring_pts(C, R_COL_I)])
    D.axes(C, hgap=[(-11900, -10500), (10500, 11900)])
    L.ddim(C, R_OUT, 160)
    def ch(y): return math.sqrt(RE * RE - y * y)
    for yy in (-6000, -6100):
        x = ch(yy); D.bar([(C[0] - x, C[1] + yy), (C[0] + x, C[1] + yy)])
    for xx in (5000, 5100):
        y = ch(xx); D.bar([(C[0] + xx, C[1] - y), (C[0] + xx, C[1] + y)])
    L.note('1', 'ш.100', (C[0] + 1800, C[1] - 5000), (C[0] + 2600, C[1] - 6000))
    L.note('1', 'ш.100', (C[0] + 6200, C[1] + 3600), (C[0] + 5100, C[1] + 2900))
    x = ch(-6000)
    for sg in (1, -1):                                                   # жиек скобалары (поз.5) — хорда ұштарында
        D.bar([(C[0] + sg * x, C[1] - 6240), (C[0] + sg * (x - LP), C[1] - 6240)])
        L.note('5', 'ш.100', (C[0] + sg * (x + 700), C[1] - 7400), (C[0] + sg * (x - 500), C[1] - 6240))
    y = ch(5000)
    for sg in (1, -1):
        D.bar([(C[0] + 5240, C[1] + sg * y), (C[0] + 5240, C[1] + sg * (y - LP))])
        L.note('5', 'ш.100', (C[0] + 6600, C[1] + sg * (y + 300)), (C[0] + 5240, C[1] + sg * (y - 500)))
    L.note('Выпуски в стену См-1', 'см. лист 3.5', (C[0] - 9800, C[1] + 9600), (C[0] + 10175 * math.cos(math.radians(140)), C[1] + 10175 * math.sin(math.radians(140))))
    L.section(1, (C[0] - 11700, C[1]), (C[0] + 11700, C[1]))
    # ---- Разрез 1-1 (армирование), сол-төменде ----
    L.title('Разрез 1 - 1 (Армирование)', sh.X0 + 9500, sh.Y0 + 12800)
    frag1(sh.X0 + 4000, sh.Y0 + 5500)
    # ---- Армирование приямка, оң-жоғарыда ----
    Pc = sh.P(42500, 30000)
    L.title('Армирование приямка', Pc[0], sh.Y0 + 40500)
    pr_plan(Pc)
    # ---- Выпуски в опору Км-1 ----
    Kc = sh.P(51000, 15800)
    L.title('Схема расположения выпусков в опору Км-1', Kc[0], Kc[1] + R_COL_O * 4 + 1900)
    km_vyp(Kc)
    # ---- узел стыковки — аналог л.8-ден клон (төменгі орта) ----
    bx, by = AN07[0] + 22500, AN07[1] + 1800
    tx, ty = sh.X0 + 21500, sh.Y0 + 2700
    L.op(t='import', file=AN, base=[bx, by], to=[tx, ty], wins=[[bx, by, bx + 16800, by + 8000]], pre='N32:')
    L.op(t='txtrep', win=[tx - 100, ty - 100, tx + 17000, ty + 8200], pairs=[['верхей', 'верхней']])
    L.op(t='eraseregion', win=[tx + 4600, ty + 800, tx + 5900, ty + 2000], mode='inside')
    L.title('Узел стыковки одиночных арматур внахлест (без сварки)', tx + 8000, ty + 9300)
    L.mtext('Стыки стержней поз. 1 - внахлестку 71d = 1280 мм, вразбежку,\\Pне более 50% стержней в одном сечении.', tx + 300, ty - 600, 250, att=1, w=16000)
    sh.notes(['Общие указания см. л. 1.1.', 'Данный лист читать совместно с л. 3.1, 3.3, 3.4.'] + NOTES[1:] +
             ['Основные сетки (поз. 1): верхняя и нижняя, стержни %%C18 А500С с шагом 100 в двух направлениях; в зоне приямка стержни прерываются и стыкуются с радиальными стержнями поз. 3.'.replace('%%C', 'Ø'),
              'Защитный слой бетона для арматуры фундамента - 50 мм.'])
    return sh


def edge_arm(F, k, rc, with_wall=True):
    """ернеу/вут армированиесі (фрагмент 1): F — (r,z)→парақ"""
    # төменгі тор
    bot = [(RE, Z_BOT + 50), (R_B1, Z_BOT + 50), (rc, z_bot(rc) + 50)]
    D.bar([F(*p) for p in bot])
    top = [(rc, z_top(rc) - 50), (R_HT, Z_HT - 50), (RE, Z_FL - 50)]
    D.bar([F(*p) for p in top])
    for r in [RE - 50 - 100 * i for i in range(int((RE - 50 - rc) // 100) + 1)]:
        zb = (Z_BOT + 50 if r >= R_B1 else z_bot(r) + 50) + 18; D.dot(F(r, zb), 9 * k)
        zt = (Z_FL - 50 - (R_OUT - 50 - r) * 42.0 / 1300 if r >= R_HT else z_top(r) - 50) - 18; D.dot(F(r, zt), 9 * k)
    # П-скоба 5
    D.bar([F(RE - LP, Z_FL - 72), F(RE - 12, Z_FL - 72), F(RE - 12, Z_BOT + 72), F(RE - LP, Z_BOT + 72)])
    # вут стержені 6 + сақиналар 7
    p1 = (9460.0, -1852.0); p2 = (9960.0, -1352.0)
    D.bar([F(p1[0] - 648, p1[1] - 54), F(*p1), F(*p2), F(p2[0], p2[1] + 650)])
    for t in (0.2, 0.5, 0.8): D.dot(F(p1[0] + 500 * t + 14, p1[1] + 500 * t - 14), 9 * k)
    if with_wall:
        xi, xo = R_WI + 49, R_WO - 49
        D.bar([F(xi, Z_JOINT + 330), F(xi, Z_BOT + 90), F(xo, Z_BOT + 90), F(xo, Z_JOINT + 330)])


def b33():
    sh = L.Sheet('3.3', 'Разрезы фундамента Фм-1 (армирование)')
    k = 6.0; lf = 1.0 / 6
    rc = 2900.0
    f2x = sh.X0 + 23000; yb = sh.Y0 + 23500; f2y = yb - Z_B3 * k
    def G(r, z): return (f2x + r * k, f2y + z * k)
    L.title('Разрез 2 - 2 (Армирование)', f2x, sh.Y0 + 40500)
    lp = [G(-rc, z_top(rc)), G(-R_PT, Z_PT), G(-R_PB, Z_PB), G(R_PB, Z_PB), G(R_PT, Z_PT), G(rc, z_top(rc))]
    lb = [G(rc, z_bot(rc)), G(R_B2, Z_B2), G(R_B3, Z_B3), G(-R_B3, Z_B3), G(-R_B2, Z_B2), G(-rc, z_bot(rc))]
    L.pl(lp, layer=L.L_THIN); L.pl(lb, layer=L.L_THIN)
    ri = min(R_PT + LP, rc - 30); ro = min(R_B2 + LP, rc - 30)
    for sg in (1, -1):
        L.brk(G(sg * rc, z_top(rc) + 60), G(sg * rc, z_bot(rc) - 160))
        L.line(G(sg * R_COL_O, Z_PB), G(sg * R_COL_O, Z_PB + 900), layer=L.L_THIN); L.line(G(sg * R_COL_I, Z_PB), G(sg * R_COL_I, Z_PB + 900), layer=L.L_THIN)
        inn = off([(R_PB - 430, Z_PB), (R_PB, Z_PB), (R_PT, Z_PT), (ri, z_top(ri))], -68)          # радиал 3: жоғарғы қабат
        D.bar([G(sg * r, z) for r, z in inn])
        out = off([(R_B3 - 430, Z_B3), (R_B3, Z_B3), (R_B2, Z_B2), (ro, z_bot(ro))], 68)           # радиал 3: төменгі қабат
        D.bar([G(sg * r, z) for r, z in out])
        for a, b, dd in (((R_PB, Z_PB), (R_PT, Z_PT), -86), ((R_B3, Z_B3), (R_B2, Z_B2), 86)):     # сақина 4
            o = off([a, b], dd)
            for p in along(o[0], o[1], 100, 50): D.dot(G(sg * p[0], p[1]), 9 * k)
        D.bar([G(sg * (R_PT + 150), z_top(R_PT + 150) - 50), G(sg * (rc - 30), z_top(rc - 30) - 50)])      # поз.1 жалғасы
        D.bar([G(sg * (R_B2 + 150), z_bot(R_B2 + 150) + 50), G(sg * (rc - 30), z_bot(rc - 30) + 50)])
        for r, fo in ((651, 1), (449, -1)):                                                         # Км-1 выпуск
            D.bar([G(sg * (r + fo * 400), Z_B3 + 110), G(sg * r, Z_B3 + 110), G(sg * r, Z_PB + 900)])
    L.brk(G(-R_COL_O - 40, Z_PB + 900), G(R_COL_O + 40, Z_PB + 900))
    L.line(G(0, Z_B3 - 150), G(0, Z_PT + 250), **D.AX)
    D.bar([G(-1541, Z_B3 + 50), G(1541, Z_B3 + 50)]); D.bar([G(-1541, Z_PB - 50), G(1541, Z_PB - 50)])       # приямок түбі (поз.2)
    for i in range(31):
        r = -1500 + 100 * i; D.dot(G(r, Z_B3 + 68), 9 * k); D.dot(G(r, Z_PB - 68), 9 * k)
    # ---- размерлер ----
    L.chain_h([G(v, 0)[0] for v in (-R_B2, -R_B3, 0, R_B3, R_B2)], yb - 200, yb - 900, lfac=lf)
    L.chain_h([G(v, 0)[0] for v in (-R_B3, -1500, 1500, R_B3)], yb - 200, yb - 1600, lfac=lf, texts=[None, '100х30=3000', None])
    yt = G(0, z_top(rc))[1]
    L.chain_h([G(v, 0)[0] for v in (-R_PT, -R_PB, 0, R_PB, R_PT)], G(0, Z_PT)[1] + 200, yt + 900, lfac=lf)
    xr = G(rc, 0)[0] + 900
    L.chain_v([G(0, v)[1] for v in (Z_B3, Z_B3 + 50, Z_PB - 50, Z_PB)], G(rc, 0)[0] + 150, xr, lfac=lf)
    L.dim((G(rc, 0)[0] + 150, G(0, Z_B3)[1]), (G(rc, 0)[0] + 150, G(0, Z_PB)[1]), (xr + 700, G(0, Z_B3)[1]), math.pi / 2, lf)
    # қиғаш бойындағы сақина қадамы
    for (a, b, dd, sg) in (((R_PB, Z_PB), (R_PT, Z_PT), -86, 1), ((R_B3, Z_B3), (R_B2, Z_B2), 86, -1)):
        o = off([a, b], dd); ps = along(o[0], o[1], 100, 50)
        p1 = G(sg * ps[0][0], ps[0][1]); p2 = G(sg * ps[-1][0], ps[-1][1])
        ux, uy = p2[0] - p1[0], p2[1] - p1[1]; ul = math.hypot(ux, uy); ux, uy = ux / ul, uy / ul
        nx, ny = -uy, ux                                                    # сол жақ нормаль: оң қиғашта — бос жаққа, сол қиғашта — сыртқа
        dl = (p1[0] + nx * 1100, p1[1] + ny * 1100)
        L.dim(p1, p2, dl, math.atan2(uy, ux), lf, txt='100х%d=%d' % (len(ps) - 1, 100 * (len(ps) - 1)))
    # ---- отметкалар (екі жақта) ----
    L.lev(Z_PT, G(-R_PT, Z_PT), 'L', ext=(rc - R_PT) * k + 900); L.lev(Z_B3, G(-R_B3, Z_B3), 'L', ext=(rc - R_B3) * k + 900)
    L.lev(Z_PT, G(R_PT, Z_PT), 'R', ext=(rc - R_PT) * k + 2400); L.lev(Z_B3, G(R_B3, Z_B3), 'R', ext=(rc - R_B3) * k + 2400)
    L.lev(Z_PB, G(R_PB - 60, Z_PB), 'L', ext=250); L.lev(Z_PB, G(-R_PB + 60, Z_PB), 'R', ext=250)
    # ---- выноскалар ----
    L.note('2', 'ш.100', G(900, -5050), G(600, Z_B3 + 50)); L.note('2', 'ш.100', G(-1000, -3600), G(-1050, Z_PB - 50))
    L.note('3', 'ш.100', G(2500, -3900), G(1870, -3760)); L.note('3', 'ш.100', G(900, -2700), G(1700, -3210))
    L.note('4', 'ш.100', G(-2650, -4100), G(-1830, -3830), on='dot'); L.note('4', 'ш.100', G(-900, -2800), G(-1740, -3100), on='dot')
    L.note('1', 'ш.100', G(2700, -1900), G(2700, z_top(2700) - 50)); L.note('1', 'ш.100', G(2700, -3300), G(2700, z_bot(2700) + 50))
    L.note('Выпуски Км-1 поз. 1', 'см. лист 3.2', G(-1300, -2300), G(-651, -3300))
    # ---- Ведомость деталей (аналог л.9: разрездер парағында) ----
    L.details(sh.X0 + 44500, sh.Y0 + 39000, DET_FM1)
    # ---- Каркас Кр-1 — аналог л.9-дан клон ----
    bx, by = AN08[0] + 2500, AN08[1] + 1000
    tx, ty = sh.X0 + 3500, sh.Y0 + 9000
    L.op(t='import', file=AN, base=[bx, by], to=[tx, ty], wins=[[bx, by, bx + 16500, by + 7800]], pre='N33:')
    sh.notes(['Общие указания см. л. 1.1.', 'Данный лист читать совместно с л. 3.1, 3.2, 3.4.', 'Защитный слой бетона для арматуры фундамента - 50 мм.',
              'Каркасы Кр-1 устанавливать с шагом 1200х1200 для фиксации верхней сетки.', NOTES[3]])
    return sh


