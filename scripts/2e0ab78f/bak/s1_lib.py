# -*- coding: utf-8 -*-
"""Первичный отстойник КЖ: op builders over s1_ab.cs. Донорлар: Аэротенк (AE:) — рамка, штамп, СПДС размер/отметка/разрез; аналог (AN:) — стиль."""
import math, json
OPS = []
_n = [0]
import time as _t
_RUN = '%x' % int(_t.time())
ROW_Y = 600000.0
SLOTS = ['1.1', '1.2', '1.3', '1.4', '1.5', '2.1', '2.2', '2.3', '3.1', '3.2', '3.3', '3.4', '3.5', '3.6', '4.1', '5.1', '5.2', '5.3', '5.4', '5.5', '5.6', '5.7', '7.1']
SHEETX = {}
_x = 0.0
for _s in SLOTS:
    SHEETX[_s] = _x; _x += 42000.0 if _s == '1.2' else 59400.0
CEH_OD = "D:/РАБОЧКА/От Маке/Завод/Цех пере оброботки/1. Общие данные Цех предобработки.dwg".replace("/", chr(92))
CEH_X = {'1.1': 0.0, '1.2': 59400.0, '1.6': 274500.0, '1.7': 333900.0}


def imp_ceh(src, dst, pre):
    """Цех ОД парағын (src нөмірі) өз слотыма (dst) толық клондау"""
    w = 42000.0 if src == '1.2' else 59400.0
    h = 29700.0 if src == '1.2' else 42000.0
    X0 = SHEETX[dst]
    op(t='eraseregion', win=[X0 - 5, ROW_Y - 5, X0 + w + 5, ROW_Y + h + 5], mode='inside')
    op(t='import', file=CEH_OD, base=[CEH_X[src], 450000.0], to=[X0, ROW_Y], wins=[[CEH_X[src] - 5, 449995.0, CEH_X[src] + w + 5, 450000.0 + h + 5]], pre=pre)
    return X0


def op(**k):
    OPS.append(k); return k

def tag(p):
    _n[0] += 1; return 's1%s%s_%d' % (p, _RUN, _n[0])

A_FRAME = 'AE:1A2EF2'          # SPDSFORMAT A2 horizontal, origin (0,450000)
A_STAMP = 'AE:20A56B'; A_BASE = (0.0, 450000.0)
A_SNAME = 'AE:20A56C'; A_SNUM = 'AE:20A56E'; A_SOBJ = 'AE:20C116'
A_DIM = 'AE:194E2C'            # RotatedDimension, СПДС, dimscale 100
A_LEV_L = 'AE:214B1A'          # level mark pointing left: idx0 on element, idx2 arrow, idx1 text end; text '-0,600'
A_LEV_R = 'AE:214B1E'
A_SEC = 'AE:21409D'

L_CONT = 'Несущие колонны'     # 0.30
L_THIN = 'Тонкая'              # 0.05
L_DIM = 'Размеры'              # 0.05
L_TXT = 'О_Формат'


def pl(pts, layer=L_CONT, closed=False, lw=None, ltype=None, ltscale=None, color=None, b=None):
    d = dict(t='pl', p=[[float(p[0]), float(p[1])] for p in pts], layer=layer, closed=closed)
    if b: d['b'] = b
    if lw is not None: d['lw'] = lw
    if ltype: d['ltype'] = ltype
    if ltscale: d['ltscale'] = ltscale
    if color is not None: d['color'] = color
    return op(**d)


def line(p, q, **k):
    return pl([p, q], **k)


def circle(c, r, layer=L_CONT, **k):
    return op(t='circle', c=[float(c[0]), float(c[1])], r=float(r), layer=layer, **k)


def arc(c, r, a0, a1, layer=L_CONT, **k):
    return op(t='arc', c=[float(c[0]), float(c[1])], r=float(r), a0=math.radians(a0), a1=math.radians(a1), layer=layer, **k)


def hatch(loops, pat='ANSI36', sc=20, layer=L_DIM, lw=5, ang=None):
    d = dict(t='hatch', pat=pat, sc=sc, layer=layer, lw=lw, loops=[[[float(p[0]), float(p[1])] for p in lp] for lp in loops])
    if ang is not None: d['ang'] = ang
    return op(**d)


def ring_pts(c, r, n=96):
    return [(c[0] + r * math.cos(2 * math.pi * i / n), c[1] + r * math.sin(2 * math.pi * i / n)) for i in range(n)]


def mtext(s, x, y, h=250, att=1, layer=L_TXT, w=None, rot=None):
    d = dict(t='mtext', at=[float(x), float(y)], h=h, att=att, s=s, style='Isocpeur', layer=layer)
    if w: d['w'] = w
    if rot is not None: d['rot'] = rot
    return op(**d)


def title(s, x, y):
    """аналог 2BDE22: h=450, Isocpeur, асты сызылған, қабат «Размеры»; ортасы x"""
    return mtext('{\\L' + s + '}', x, y, 450, att=2, layer=L_DIM)


def dim(p1, p2, dl, rot=0.0, lfac=None, txt=None, tx=None):
    d = dict(t='dim', h=A_DIM, p1=list(map(float, p1)), p2=list(map(float, p2)), dl=list(map(float, dl)), rot=rot, dscale=100, layer=L_DIM)
    if lfac: d['lfac'] = lfac
    if txt: d['txt'] = txt
    if tx: d['tx'] = list(tx)
    return op(**d)


def chain_h(xs, y_ext, y_dl, lfac=None, texts=None):
    for i in range(len(xs) - 1):
        dim((xs[i], y_ext), (xs[i + 1], y_ext), (xs[i], y_dl), 0.0, lfac, texts[i] if texts else None)


def chain_v(ys, x_ext, x_dl, lfac=None, texts=None):
    for i in range(len(ys) - 1):
        dim((x_ext, ys[i]), (x_ext, ys[i + 1]), (x_dl, ys[i]), math.pi / 2, lfac, texts[i] if texts else None)


def adim(p1, p2, dl, lfac=None):
    d = dict(t='adim', h=A_DIM, p1=list(map(float, p1)), p2=list(map(float, p2)), dl=list(map(float, dl)), dscale=100)
    if lfac: d['lfac'] = lfac
    return op(**d)


def ddim(c, r, ang_deg, lfac=None, tx_out=900):
    a = math.radians(ang_deg)
    p1 = (c[0] + r * math.cos(a), c[1] + r * math.sin(a)); p2 = (c[0] - r * math.cos(a), c[1] - r * math.sin(a))
    d = dict(t='ddim', h=A_DIM, p1=list(p1), p2=list(p2), dscale=100, layer=L_DIM)
    if lfac: d['lfac'] = lfac
    if tx_out is not None: d['tx'] = [c[0] + (r + tx_out) * math.cos(a), c[1] + (r + tx_out) * math.sin(a)]
    return op(**d)


import sys as _sys
_sys.path.insert(0, 'D:/Бекасыл КЖ КМ/_Стандарт_КЖ/скрипттер'.replace('/', chr(92)))
import kzh_note_rule as KNR
NOTES_LOG = []          # check() үшін: әр выносканың target/origin/ends_on


def note(l1, l2, origin, target, on='line', kind='pos', dist=None):
    """КЖ выноскасы (ЕРЕЖЕЛЕР №119, kzh_note_rule.note_params): target — элементке тиетін нүкте; origin — бағыт береді,
    излом нүктесі target-тен 300…600 мм-ге келтіріледі (dist берілсе — сол); on: 'line' → засечка, 'dot' → засечкасыз;
    полка излом нүктесінен элементке кері жаққа."""
    dx, dy = origin[0] - target[0], origin[1] - target[1]; d = math.hypot(dx, dy) or 1.0
    dd = dist if dist is not None else min(max(d, KNR.SHELF_MIN), KNR.SHELF_MAX)
    o = (target[0] + dx / d * dd, target[1] + dy / d * dd)
    arrow, angle = KNR.note_params(target, o, on, kind)
    NOTES_LOG.append(dict(l1=l1, target=tuple(target), origin=o, ends_on=on, kind=kind, arrow=arrow, angle=angle))
    return op(t='note', l1=l1, l2=l2 or '', origin=[float(o[0]), float(o[1])], target=list(map(float, target)), scale=100, ts=2.5,
              arrow=arrow.lower(), angle=angle, layer=L_DIM, align='Center', style='ГОСТ 2.304')


def lev_txt(z):
    v = z / 1000.0
    if abs(v) < 0.0005: return '0,000'
    return ('+' if v > 0 else '-') + ('%.3f' % abs(v)).replace('.', ',')


def lev(z, at, side='R', ext=None):
    """СПДС отметка: at — деңгей сызығының элементтегі нүктесі; side — сөре жағы; ext — at-тан стрелкаға дейін"""
    src = A_LEV_L if side == 'L' else A_LEV_R
    t = tag('lv'); op(t='clone', h=src, tag=t)
    t2 = tag('lt'); op(t='levelval', h=t, old='-0,600', value=lev_txt(z), tag=t2)
    op(t='moveto', h=t2, idx=0, to=[float(at[0]), float(at[1])])
    if ext is not None:
        sg = -1 if side == 'L' else 1
        op(t='sp_set', h=t2, pts=[[2, at[0] + sg * ext, at[1]], [1, at[0] + sg * (ext + 1254), at[1] + 600]])
    return t2


def section(word, p0, p1, dirn=None):
    t = tag('se'); op(t='clone', h=A_SEC, tag=t)
    op(t='sp_set', h=t, pts=[[0, p0[0], p0[1]], [1, p1[0], p1[1]]])
    st = {'Word': str(word), 'Scale': 100}
    if dirn is not None: st['Dir'] = dirn
    op(t='mcset', h=t, set=st)
    return t


def brk(p, q, layer=L_THIN, amp=120):
    """үзік (обрыв) сызығы p→q, ортасында зигзаг"""
    mx, my = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
    dx, dy = q[0] - p[0], q[1] - p[1]; L = math.hypot(dx, dy); ux, uy = dx / L, dy / L; nx, ny = -uy, ux
    pts = [p, (mx - ux * amp * 0.5, my - uy * amp * 0.5), (mx - ux * amp * 0.25 + nx * amp, my - uy * amp * 0.25 + ny * amp),
           (mx + ux * amp * 0.25 - nx * amp, my + uy * amp * 0.25 - ny * amp), (mx + ux * amp * 0.5, my + uy * amp * 0.5), q]
    return pl(pts, layer=layer)


class Sheet:
    """A2 альбом 1:100: рамка СПДС + Штамп_АБК (Аэротенк доноры)"""
    W, H = 59400.0, 42000.0

    def __init__(self, num, name):
        self.num, self.name = num, name
        self.X0, self.Y0 = float(SHEETX[num]), ROW_Y
        X0, Y0 = self.X0, self.Y0
        op(t='eraseregion', win=[X0 - 5, Y0 - 5, X0 + self.W + 5, Y0 + self.H + 5], mode='inside')
        t = tag('fr'); op(t='clone', h=A_FRAME, tag=t)
        op(t='mcset', h=t, set={'Origin': [X0, Y0]})
        for h, txt in ((A_STAMP, None), (A_SNAME, name), (A_SNUM, str(num)), (A_SOBJ, 'Первичный отстойник')):
            d = dict(t='clone', h=h, base=list(A_BASE), to=[X0, Y0], tag=tag('st'))
            if txt is not None: d['text'] = txt
            op(**d)
        self.stamp = (X0 + 40400, Y0 + 500, X0 + 58900, Y0 + 6000)

    def P(self, x, y):
        return (self.X0 + x, self.Y0 + y)

    def notes(self, lines, w=18300):
        s = '\\pxi-3.3333,l3.3333,ql,t3.3333;' + '\\P'.join('%d.\t%s' % (i + 1, l) for i, l in enumerate(lines))
        return mtext(s, self.stamp[0] + 200, self.stamp[3] + 460, 250, att=7, w=w)


# ---------------- кестелер (Цех «5. Стены» л.5.6 донорлары: CW:67A317 бас жол, CW:679DB6 дене, CW:67A8A5 расход стали) ----------------
KGM = {6: 0.222, 8: 0.395, 10: 0.617, 12: 0.888, 14: 1.208, 16: 1.578, 18: 1.998, 20: 2.466, 22: 2.984, 25: 3.853, 28: 4.834}
CODE = {'A240': 'ГОСТ 34028-2016 (214-210-0101)', 'A500C': 'ГОСТ 34028-2016 (214-210-0502)'}
BETON = ('ГОСТ 7473-2010 (212-101-1103)', 'Бетон С25/30, W8, F150, м³')
PODG = ('ГОСТ 7473-2010 (212-101-0309)', 'Бетон С8/10 (подготовка), м³')
FMT2 = '%lu2%pr2'; FMT1 = '%lu2%pr1'


def row_mass(r):
    """спецификация жолының массасы — кестедегі дөңгелектеумен бірдей"""
    d = r['d']
    if r['L'] is None: return math.ceil(r['tot_m']) * KGM[d]
    return r['n'] * round(r['L'] / 1000.0 * KGM[d], 3)


def spec(x, ytop, elname, rows, mats, bent=(), qty=1):
    """Спецификация элементов: rows — s1_qty жолдары; mats — [(обозначение, наименование, мән)]; bent — «*» қойылатын позициялар.
    қайтарады: (дене кестесінің тегі, кестенің төменгі y-і)"""
    th = tag('th'); tb = tag('tb')
    op(t='clone', h='CW:67A317', base=[20200, 722204], to=[x, ytop], tag=th)
    op(t='clone', h='CW:679DB6', base=[20200, 719904], to=[x, ytop - 2300], tag=tb)
    n = len(rows)
    if n > 8: op(t='trows', h=tb, mode='ins', at=9, **{'from': 8}, n=n - 8)
    elif n < 8: op(t='trows', h=tb, mode='del', at=1 + n, n=8 - n)
    cells = [[0, 2, elname], [0, 12, '']]
    fcells = []
    for i, r in enumerate(rows):
        R = 1 + i; cls = r['cls']; d = r['d']
        mp = r['L'] is None
        cells += [[R, 0, r['pos'] + ('*' if r['pos'] in bent else '')], [R, 1, CODE[cls]], [R, 2, '%%C'], [R, 3, str(d)], [R, 4, 'A'], [R, 5, cls[1:].replace('C', 'С')],
                  [R, 8, 'L='], [R, 9, 'пог.м.' if mp else str(r['L'])],
                  [R, 10, str(int(math.ceil(r['tot_m']))) if mp else str(r['n'])], [R, 11, ('%.3f' % KGM[d]) if mp else ('%.3f' % (r['L'] / 1000.0 * KGM[d]))]]
        fcells.append([R, 12, 'K%d*L%d' % (R + 1, R + 1), FMT1])
    R = 1 + n          # бос жол
    cells += [[R, c, ''] for c in range(13)]
    rm = R + 1
    # материалдар: донорда 1 жол (rm+1); қажет болса қосамыз
    if len(mats) > 1: op(t='trows', h=tb, mode='ins', at=rm + 2, **{'from': rm + 1}, n=len(mats) - 1)
    for j, (code, name, val) in enumerate(mats):
        cells += [[rm + 1 + j, 1, code], [rm + 1 + j, 2, r'\A1;' + name], [rm + 1 + j, 12, ('%.2f' % val)]]
    op(t='tset', h=tb, cells=cells)
    fcells.append([0, 12, 'SUM(M2:M%d)' % (1 + n), FMT1])
    op(t='tformula', h=tb, cells=fcells)
    nrows = 1 + n + 1 + 1 + len(mats) + 1
    return tb, ytop - 2300 - 800 * nrows


def steel(x, ytop, elname, rows):
    """Ведомость расхода стали, кг: rows — s1_qty жолдары (бір элемент)"""
    t = tag('ts')
    op(t='clone', h='CW:67A8A5', base=[0, 729000], to=[x, ytop], tag=t)
    col = {6: 1, 8: 2, 12: 4, 14: 5, 16: 6, 18: 7, 20: 8, 22: 9, 25: 10, 28: 11}
    sums = {}
    for r in rows: sums[r['d']] = sums.get(r['d'], 0.0) + row_mass(r)
    cells = [[6, 0, elname]] + [[6, c, '---'] for c in (1, 2, 4, 5, 6, 7, 8, 9, 10, 11)]
    for d, v in sums.items(): cells.append([6, col[d], '%.1f' % v])
    op(t='tset', h=t, cells=cells)
    L_ = 'ABCDEFGHIJKLMN'
    a240 = [L_[col[d]] + '7' for d in sums if d in (6, 8)]; a500 = [L_[col[d]] + '7' for d in sums if d >= 12]
    f = []
    f.append([6, 3, '+'.join(a240) if a240 else '0', FMT1]); f.append([6, 12, '+'.join(a500) if a500 else '0', FMT1]); f.append([6, 13, 'D7+M7', FMT1])
    op(t='tformula', h=t, cells=f)
    return t


def details(x, ytop, items, title='Ведомость деталей', w0=3000, w1=11000, rh=2600):
    """Ведомость деталей: items — [(поз, [(dx,dy,'мәтін')...] сегменттер, r_text)], эскиз сызықпен (арматура 0.40)"""
    mtext(r'{\L' + title + '}', x + (w0 + w1) / 2, ytop + 900, 350, att=2, layer=L_DIM)
    y = ytop
    pl([(x, y), (x + w0 + w1, y), (x + w0 + w1, y - 1200 - rh * len(items)), (x, y - 1200 - rh * len(items))], closed=True, layer=L_CONT)
    line((x + w0, y), (x + w0, y - 1200 - rh * len(items)), layer=L_CONT)
    line((x, y - 1200), (x + w0 + w1, y - 1200), layer=L_CONT)
    mtext('Поз.', x + w0 / 2, y - 600, 250, att=5); mtext('Эскиз', x + w0 + w1 / 2, y - 600, 250, att=5)
    y -= 1200
    for pos, segs, rt in items:
        if y != ytop - 1200: line((x, y), (x + w0 + w1, y), layer=L_THIN)
        mtext(pos, x + w0 / 2, y - rh / 2, 250, att=5)
        tx = sum(abs(s[0]) for s in segs); ty = sum(abs(s[1]) for s in segs)
        xs = [0.0]; ys = [0.0]
        for sg_ in segs: xs.append(xs[-1] + sg_[0]); ys.append(ys[-1] + sg_[1])
        bw, bh = max(xs) - min(xs), max(ys) - min(ys)
        k = min((w1 - 4500) / max(bw, 1), (rh - 1100) / max(bh, 1))
        ox = x + w0 + (w1 - bw * k) / 2 - min(xs) * k - 400; oy = y - rh / 2 - (max(ys) + min(ys)) / 2 * k
        pts = [(ox + a * k, oy + b * k) for a, b in zip(xs, ys)]
        pl(pts, layer='ф18_арм', lw=40, color=7)
        for i, sg_ in enumerate(segs):
            dx, dy, tx_ = sg_[:3]
            if not tx_: continue
            mx, my = (pts[i][0] + pts[i + 1][0]) / 2, (pts[i][1] + pts[i + 1][1]) / 2
            if len(sg_) > 3: mtext(tx_, mx + sg_[3][0], my + sg_[3][1], 250, att=sg_[3][2], layer=L_DIM)   # (ox, oy, att): мәтін сызыққа түспесін (қиғаш сегмент)
            elif abs(dx) >= abs(dy): mtext(tx_, mx, my + 130, 250, att=8, layer=L_DIM)
            else: mtext(tx_, mx + 150, my, 250, att=4, layer=L_DIM)
        if rt: mtext(rt, x + w0 + w1 - 300, y - 450, 250, att=3, layer=L_DIM)
        y -= rh
    return y
