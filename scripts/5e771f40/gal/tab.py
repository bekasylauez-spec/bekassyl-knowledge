# sheet 6.4: «Ведомость ригелей» — Марка | Сечение | Пролеты | Отм. | Кол-во, шт | Лист (3 blocks side by side)
import json, os, collections, gx, prep, stamp2
NO = '6.4'
SX = prep.SX0 - 31500.0          # slot left of sheet 6.5
marks = json.load(open(os.path.join(prep.LIRA, 'marks.json'), encoding='utf-8'))
W = [1300, 1500, 3000, 1200, 1000, 1500]
HDR = ['Марка', 'Сечение, мм', 'Пролеты в свету, мм', 'Отм. верха', 'Кол-во, шт', 'Лист']
RH, HH = 400.0, 800.0
TITLE_H = 'A5:4038B1'
TC = (305244.0, 470114.0)      # kit title mtext centre (attachment middle-centre, h150)
CELL_H = 'A5:4064A2'            # kit MText h125 Isocpeur, middle-centre
CC = (326654,468889)


def spans_txt(m):
    s = [int(round(b - a)) for a, b in m['spans']]
    out = []
    for v in s:
        if out and out[-1][0] == v: out[-1][1] += 1
        else: out.append([v, 1])
    return '; '.join('%d' % v if n == 1 else '%dх%d' % (v, n) for v, n in out)


def rows(first_no=5):
    L = collections.OrderedDict()
    for m, p in prep.build(marks, first_no=first_no): L.setdefault(m['mark'], []).append(p['no'])
    R = []
    for m in marks:
        ls = L[m['mark']]
        R.append([m['mark'], '%dх%d' % (m['b'], m['h']), spans_txt(m), '; '.join(m.get('levels') or [m['level']]), str(m['count']), ls[0] if len(ls) == 1 else '%s…%s' % (ls[0], ls[-1])])
    return R


def run():
    R = rows(); P = 'S64'; SY = prep.SY
    dx, dy = SX - 298179.0, SY - prep.KY
    ops = [dict(t='eraseregion', win=[SX - 50, SY - 50, SX + 31550, SY + 14900])]
    for r in ['A5:401330', 'A5:404440', 'A5:404442', 'A5:40443F']:
        ops.append(dict(t='clone', h=r, base=[0, 0], to=[dx, dy], tag=P + ':' + r[3:]))
    nb = 2; per = (len(R) + nb - 1) // nb
    TW = sum(W); gap = 900
    x0 = SX + 1700
    ytop = SY + 13300
    n = [0]
    def txt(s, cx, cy, title=False, w=None):
        n[0] += 1; t = '%s_T%d' % (P, n[0])
        ops.append(dict(t='clone', h=TITLE_H if title else CELL_H, base=list(TC if title else CC), to=[cx, cy], tag=t, text=s))
        ops.append(dict(t='settext', h=t, s=s, w=(w - 60) if w else 0))
    def line(p, lw):
        n[0] += 1; ops.append(dict(t='pl', p=p, layer='0', lw=lw, tag='%s_L%d' % (P, n[0])))
    # title over the whole table
    txt('Ведомость ригелей', SX + 1000 + 30250 / 2.0, ytop + 450, True)
    for k in range(nb):
        part = R[k * per:(k + 1) * per]
        if not part: continue
        xl = x0 + k * (TW + gap); xr = xl + TW
        yb = ytop - HH - RH * len(part)
        xs = [xl]
        for w in W: xs.append(xs[-1] + w)
        # header
        for i, h in enumerate(HDR): txt(h, (xs[i] + xs[i + 1]) / 2.0, ytop - HH / 2.0, w=W[i])
        for i, r in enumerate(part):
            yc = ytop - HH - RH * (i + 0.5)
            for j, v in enumerate(r): txt(v, (xs[j] + xs[j + 1]) / 2.0, yc, w=W[j])
        # lines: frame, header bottom, columns 0.30; rows 0.05
        line([[xl, ytop], [xr, ytop], [xr, yb], [xl, yb], [xl, ytop]], 30)
        line([[xl, ytop - HH], [xr, ytop - HH]], 30)
        for x in xs[1:-1]: line([[x, ytop], [x, yb]], 30)
        for i in range(1, len(part)):
            y = ytop - HH - RH * i; line([[xl, y], [xr, y]], 5)
    ops.append(dict(t='settext', h=P + ':404442', s='Ведомость ригелей'))
    ops.append(dict(t='settext', h=P + ':404440', s=NO))
    out = gx.run(ops, 'tab64')
    st = stamp2.stamp(dict(P=P, SX=SX, SY=SY))
    return out, st


if __name__ == '__main__':
    o, st = run()
    print([l for l in (o + st).splitlines() if 'ERR' in l or 'done' in l][:8])
