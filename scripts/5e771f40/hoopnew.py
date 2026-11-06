    # ---- hoops per span (Bekassyl 06.11: steps 100/200 only, Ø up instead of step 50; no tails in the chain)
    zones, NH = [], 0
    def inspan(p): return any(fL <= p[0] <= fR for fL, fR in spans)
    peak_all = max([p[3] for p in Pf if inspan(p)] or [0])
    hd = next((d for d in (10, 12, 14, 16) if peak_all <= cap(legs, d, 100)), 16)
    for (fL, fR) in spans:
        sp = [p for p in Pf if fL <= p[0] <= fR]
        Ls_ = fR - fL
        free_l = fL < 1 and not any(abs(a) < 2 for a, _, _ in sups)
        free_r = fR > E - 1 and not any(abs(e - E) < 2 for _, e, _ in sups)
        aw = lambda u0, u1: max([p[3] for p in sp if u0 <= p[0] <= u1] or [0])
        mid = aw(fL + Ls_ / 4, fR - Ls_ / 4)
        def stp(pk): return 200 if pk <= cap(legs, hd, 200) else 100 if pk <= cap(legs, hd, 100) else 50
        smid = stp(mid)
        s_l, s_r = min(stp(aw(fL, fL + Ls_ / 2)), 100, smid), min(stp(aw(fR - Ls_ / 2, fR)), 100, smid)
        def zlen(side):
            pts = [p for p in sp if (p[0] - fL if side == 'L' else fR - p[0]) <= Ls_ / 2]
            far = [abs(p[0] - (fL if side == 'L' else fR)) for p in pts if p[3] > cap(legs, hd, smid)]
            return max(Ls_ / 4.0, (max(far) + 50) if far else 0)
        Lp = Ls_ - 100.0
        if s_l == smid == s_r or Lp < 2 * smid + s_l + s_r:
            s = min(s_l, s_r, smid); s_l = s_r = smid = s
            n1, n2, n3 = 0, int(Lp // s), 0
        else:
            n1 = 0 if free_l else int(math.ceil((zlen('L') - 50) / s_l))
            n3 = 0 if free_r else int(math.ceil((zlen('R') - 50) / s_r))
            n2 = int((Lp - n1 * s_l - n3 * s_r) // smid)
        r = Lp - n1 * s_l - n2 * smid - n3 * s_r
        k = 0
        while n1 + n3 and r >= min(s_l, s_r) - 1e-6:            # tail -> one more step of an end zone
            if (k % 2 == 0 and n1) or not n3:
                if r >= s_l - 1e-6: n1 += 1; r -= s_l
                else: n3 += 1; r -= s_r
            else:
                if r >= s_r - 1e-6: n3 += 1; r -= s_r
                else: n1 += 1; r -= s_l
            k += 1
        gl = 50 + math.floor(r / 2.0); h0 = fL + gl            # leftover < step -> into the face gaps
        h4 = h0 + n1 * s_l + n2 * smid + n3 * s_r
        lab = lambda s, n: '%dх%d' % (s, n) if n > 1 else '%d' % s
        segs = []; x = h0; ln = [h0]
        for s, n in ((s_l, n1), (smid, n2), (s_r, n3)):
            if not n: continue
            if segs and segs[-1][3] == s:
                segs[-1][1] += n * s; segs[-1][4] += n
            else:
                if segs: ln.append(x)
                segs.append([x, x + n * s, '', s, n])
            x += n * s
        assert abs(x - h4) < 1e-6
        ln.append(h4)
        segs = [(p, q, lab(s, n)) for p, q, _, s, n in segs]
        cnt = n1 + n2 + n3 + 1
        NH += cnt
        zones.append(dict(fL=fL, fR=fR, segs=segs, lines=sorted(set(round(v, 1) for v in ln)), cnt=cnt, s=(s_l, smid, s_r),
