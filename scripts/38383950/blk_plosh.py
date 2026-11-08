# ================= площадка +4.000 / +7.600 (ЛИРА): fins on every beam end
X = lambda a: AX[a - 1]
for lev in (4000.0, 7600.0):
    ylines = gen.YL[lev]; pl = 'Площадка %d ' % lev
    cz = lambda pr: lev - H[pr] / 2
    for x, mk, pr in ylines:
        pc = colprof(x, 60000); hfc = H[pc] / 2
        fin(pl + mk + ' ' + str(int(x)) + ' К3', [x, 50197, cz(pr)], [0, -1, 0], [1, 0, 0], TW[pr] / 2, 16, clearI(pr, cz(pr)), TW[pr])
        fin(pl + mk + ' ' + str(int(x)) + ' К', [x, 60000 - hfc - 10, cz(pr)], [0, 1, 0], [1, 0, 0], TW[pr] / 2, 10, clearI(pr, cz(pr)), TW[pr])
    for j in range(len(ylines) - 1):
        (xa, ma, pa), (xb, mb, pb) = ylines[j], ylines[j + 1]
        for xe, sx in ((xa, 1), (xb, -1)):
            fin(pl + 'Б1-К3 ' + str(int(xe)) + ' ' + str(sx), [xe + sx * 197, 50000, cz('25Б1')], [-sx, 0, 0], [0, 1, 0], TW['25Б1'] / 2, 10, clearI('25Б1', cz('25Б1')), TW['25Б1'])
            pr = colprof(xe, 60000); g = pl + 'Б1-К ' + str(int(xe)) + ' ' + str(sx)
            fin(g, [xe + sx * 160, 60000, cz('25Б1')], [-sx, 0, 0], [0, 1, 0], TW['25Б1'] / 2, 160 - TW[pr] / 2, clearI('25Б1', cz('25Б1')), TW['25Б1'])
            for dzz in (H['25Б1'] / 2 - TF['25Б1'] / 2, -(H['25Б1'] / 2 - TF['25Б1'] / 2)): colstiff(g, xe, 60000, cz('25Б1') + dzz, pr, (sx,))
        for y in (52500.0, 55000.0, 57500.0):
            for xe, sx, ps in ((xa, 1, pa), (xb, -1, pb)):
                band = clearI('30Б1', cz('30Б1')); sb_ = clearI(ps, cz(ps)); band = (max(band[0], sb_[0]), min(band[1], sb_[1]))
                fin(pl + 'Б2 ' + str(int(xe)) + ' ' + str(int(y)) + ' ' + str(sx), [xe + sx * (BW[ps] / 2 + 10), y, cz('30Б1')], [-sx, 0, 0], [0, 1, 0], TW['30Б1'] / 2, BW[ps] / 2 + 10 - TW[ps] / 2, band, TW['30Б1'])
