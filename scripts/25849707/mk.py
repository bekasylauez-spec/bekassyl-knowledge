# build all sheets of one mark: import analog sheet per fragment, facade, sections, (last sheet) tables
import gx, rig, rigsec, rigtab, an61, plan, json, math


class Stuck(Exception): pass


def R(ops, name, wait=900):
    out = gx.run(ops, name, wait=wait)
    if out.strip().startswith('timeout') or 'eAtMaxReaders' in out: raise Stuck(name + ': ' + out[-300:])
    return out
X0, Y0, PITCH = 133817.0, -1840000.0, 31500.0
SEC_X0, SEC_X1, SEC_Y = -224000.0, -210800.0, 417700.0


def slot(k): return X0 + PITCH * k, Y0


def fresh(k, P):
    SX, SY = slot(k)
    ops = [dict(t='erase', h=[v]) for kk, v in gx.tagmap().items() if kk.startswith(P) or kk.startswith(P.rstrip(':') + '_') or kk.startswith(P.rstrip(':') + 'S')]
    ops.append(dict(t='eraseregion', win=[SX - 10, SY - 10, SX + PITCH - 20, SY + 18000]))
    ops.append(dict(t='eraseins', win=[SX - 10, SY - 10, SX + PITCH - 20, SY + 18000]))
    ops.append(dict(t='import', file=an61.SRC, h=an61.SHEET + an61.SECS, base=list(an61.AN0), to=[SX, SY], pre=P))
    return R(ops, 'imp_' + P.rstrip(':'))


def sec_layout(G):
    defs = G['secdefs']; b = G['b']
    SEC_Y = min(417700.0, 420195.0 - 3.5 * G['h'] + (250.0 if G['h'] >= 1000 else 0.0))
    n = len(defs)
    G['secLM'] = not (n >= 3 and (b + 1408) * 2.5 * n > SEC_X1 - SEC_X0)
    w = ((b + 1408) if G['secLM'] else (b + 1083)) * 2.5
    room = SEC_X1 - SEC_X0
    step = min(w, room / max(n, 1))
    x0 = SEC_X0 + (room - step * n) / 2.0 + (583 if G['secLM'] else 590) * 2.5         # beam left face inside its slot
    return [(word, (x0 + step * j, SEC_Y), tp, bt, dpos) for j, (word, tp, bt, dpos) in enumerate(defs)]


def recycle():
    # MultiCAD read-opens leak (eAtMaxReaders): save, then discard and reopen the document from disk
    R([dict(t='save')], 'sv')
    return R([dict(t='reopen')], 'ro', wait=300)


def run_mark(m, k0, no0, mark, count, log=print):
    recycle()
    F = plan.build_F(m, mark)
    frags = plan.fragments(F)
    G_all = [plan.sheetF(F, fr) for fr in frags]
    NHt = 0; errs = []
    for i, G in enumerate(G_all):
        k = k0 + i; P = 'K%d:' % k
        SX, SY = slot(k)
        fresh(k, P)
        S = rig.Sheet(P, SX, SY)
        NH, spans = rig.build(S, G); NHt += NH
        dH = G['h'] - 400.0
        sh = max(0.0, min(dH - 150.0, 450.0))
        if sh > 0:   # left analog details (node A, a-a, splice node, Ск detail, plate table) down, clear of the deeper facade
            S.add(t='movewin', win=[S.x(-231600), S.y(412300), S.x(-222300), S.y(421300)], d=[0, -sh])
        out = R(S.ops, 'g_' + P.rstrip(':')); errs += [l for l in out.splitlines() if 'ERR' in l]
        S.ops = []
        for j, (word, T0, tp, bt, dpos) in enumerate(sec_layout(G)):
            rigsec.section(S, G, j, word, [T0[0] + S.dx, T0[1] + S.dy], tp, bt, dpos)
        S.add(t='eraseregion', win=[SX - 10, SY + 14860, SX + PITCH - 20, SY + 18000])
        out = R(S.ops, 's_' + P.rstrip(':')); errs += [l for l in out.splitlines() if 'ERR' in l]
        S.ops = []
        no = '6.%d' % (no0 + i)
        last = i == len(G_all) - 1
        if last:
            Lbar = (F['supall'][-1][1] - F['supall'][0][0]) - 40
            P_, geo = rigtab.positions(dict(G, endL='end', endR='end',
                                            dopspec=dopspec(F), nspec=nspec(F)), NHt, Lbar)
            conc = round(G['b'] / 1000.0 * (G['h'] - 200) / 1000.0 * sum(b - a for a, b in spans_all(F)) / 1000.0, 2)
            title = 'Ригель %s' % mark + (' (%d шт.)' % count if count > 1 else '')
            o = rigtab.ops(S, G, P_, conc, title, gx.tagmap())
        else:
            P_, geo = rigtab.positions(dict(G, endL='end', endR='end', dopspec=[], nspec={}), 0, 0)
            o = [dict(t='erase', h=[S.A(rigtab.SPEC), S.A(rigtab.STEEL)])]
        o += rigtab.texts(S, G, geo, no, mark)
        out = R(o + [dict(t='save')], 't_' + P.rstrip(':')); errs += [l for l in out.splitlines() if 'ERR' in l]
        log('%s sheet %s slot %d frag %s errs %d' % (mark, no, k, frags[i], len(errs)))
    return len(G_all), errs


def spans_all(F):
    s = F['supall']; return [(s[i][1], s[i + 1][0]) for i in range(len(s) - 1)]


def dopspec(F):
    out = {}
    for d in F['dopall']:
        o = out.setdefault(d['pos'], dict(pos=d['pos'], d=d['d'], L=int(d['L']), q=0)); o['q'] += d['k']
    return sorted(out.values(), key=lambda x: int(x['pos']))


def nspec(F):
    n = F['top']['n']; out = {}
    for key in ('top', 'bot'):
        dd = F[key]['d']
        out[dd] = out.get(dd, 0) + len(F['splall'][key]) * n * 2
    return {d: q for d, q in out.items() if q}
