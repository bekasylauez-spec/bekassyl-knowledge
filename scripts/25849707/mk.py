# build one rigel sheet: import analog sheet (+sections, +ведомость деталей block) at slot k, then facade, sections, tables
import gx, rig, rigsec, rigtab, an61, json, sys
X0, Y0, PITCH = 133817.0, -1840000.0, 31500.0
def slot(k): return X0 + PITCH * k, Y0
def fresh(k, P):
    SX, SY = slot(k)
    ops = [dict(t='eraseregion', win=[SX - 10, SY - 10, SX + PITCH - 20, SY + 18000])]
    ops.append(dict(t='import', file=an61.SRC, h=an61.SHEET + an61.SECS, base=list(an61.AN0), to=[SX, SY], pre=P))
    return gx.run(ops, 'imp_' + P.rstrip(':'))
def make(k, P, F, no, conc, count, secdefs):
    SX, SY = slot(k)
    S = rig.Sheet(P, SX, SY)
    NH, spans = rig.build(S, F)
    out = gx.run(S.ops, 'g_' + P.rstrip(':')); err = [l for l in out.splitlines() if 'ERR' in l]
    S.ops = []
    for j, (word, T0, tops, bots, dpos) in enumerate(secdefs):
        rigsec.section(S, F, j, word, [T0[0] + S.dx, T0[1] + S.dy], tops, bots, dpos)
    S.add(t='eraseregion', win=[SX - 10, SY + 14860, SX + PITCH - 20, SY + 18000])        # analog staging sections above the frame
    out = gx.run(S.ops, 's_' + P.rstrip(':')); err += [l for l in out.splitlines() if 'ERR' in l]
    Lbar = (F['u1'] - F['u0']) - (20 if F['endL'] == 'end' else 0) - (20 if F['endR'] == 'end' else 0)
    Pp, geo = rigtab.positions(F, NH, Lbar)
    S.ops = []
    title = 'Ригель %s' % F['mark'] + (' (%d шт.)' % count if count > 1 else '')
    o = rigtab.ops(S, F, Pp, conc, title, gx.tagmap()) + rigtab.texts(S, F, geo, no, F['mark'])
    out = gx.run(o + [dict(t='save')], 't_' + P.rstrip(':')); err += [l for l in out.splitlines() if 'ERR' in l]
    return NH, Pp, err
