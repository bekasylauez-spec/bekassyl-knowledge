    for i in BRACED:
        xa, xb = AX[i] + 150, AX[i + 1] - 150; xm = (AX[i] + AX[i + 1]) / 2
        B('Р1', 'Tb', '□100x5', [AX[i] + 160 + EXT, y, 5020], [AX[i + 1] - 160 - EXT, y, 5020])   # 10.11: one Р1 through the bay (ЛИРА node at mid-bay)
        # 10.11 user: vertical bracing as in ЛИРА (В_109_v3_КМ.lir, types 11 / 12) — not the X of «Разрез 6-6»:
        #   −0.300…+5.020  СВ1 □160x5 Λ: column bases → the Р1 +5.020 bottom face at mid-bay
        #   +5.020…+10.340 СВ1 □160x5 V: the Р1 +5.020 top face at mid-bay → the columns at +10.340 (web gusset with the Р1 +10.340)
        #   +10.340…top     СВ2 / СВ3 □100x5 V: the Р1 +10.340 top face at mid-bay → the column top band (узел 1, разрез 2-2)
        # mid-bay ends: gusset −10 welded on the Р1 face (key «p1» in b109_11), the pair kept apart by apex()
        bw = 160
        for xc in (xa, xb):
            a, b = [xm, y, 5020.0 - 50], [xc, y, 0.0]
            th = math.atan2(abs(b[2] - a[2]), abs(xc - xm)); tc = bw / 2 * max(math.tan(th), 1 / math.tan(th)) + 10
            pa, pb = trim(a, b, apex(bw, th) + EXT, tc + EXT); B('СВ1', 'Tb', '□160x5', pa, pb)
            a, b = [xm, y, 5020.0 + 50], [xc, y, 10340.0]
            th = math.atan2(abs(b[2] - a[2]), abs(xc - xm)); tc = bw / 2 * max(math.tan(th), 1 / math.tan(th)) + 10
            pa, pb = trim(a, b, apex(bw, th) + EXT, tc + EXT); B('СВ1', 'Tb', '□160x5', pa, pb)
        mark = 'СВ2' if r in 'AM' else 'СВ3'; bw2 = 100
        for xc, ic in ((xa, i), (xb, i + 1)):
            zmax = coltop(ic, r); zmin = ts_top(ic, r); zn = (zmax + zmin) / 2
            BRACE_TOP.append((AX[ic], y, zmin, zmax, 1 if xm > xc else -1))
            a, b = [xm, y, 10340.0 + 50], [xc, y, zn]
            th = math.atan2(abs(b[2] - a[2]), abs(xc - xm)); tc = bw2 / 2 * max(math.tan(th), 1 / math.tan(th)) + 10
            pa, pb = trim(a, b, apex(bw2, th) + EXT, tc + 20); B(mark, 'Tb', '□100x5', pa, pb)   # top: end at the flange edge (узел 1)
