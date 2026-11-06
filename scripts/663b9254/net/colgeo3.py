# Column geometry, Bekassyl rules (05.11.2026) + Block 3 specifics.
# Hoops per storey: from lower level +50 to beam bottom -50, split X+2X+X: ends step 100, middle 200.
# Leftover of the middle zone: 100..200 -> one step inside the 200 zone (rule); a leftover < 100 is joined with two 200 steps
# and split in three equal steps (e.g. 50 + 400 -> 150x3), so no step is < 100 or > 200.
# A storey with a hoop zone shorter than 2000 (foundation top -> grade beam, short upper storeys) gets equal steps <= 100.
import math

def storey_hoops(lo, beam_bot):
    a, b = lo + 50.0, beam_bot - 50.0
    S = b - a
    if S < 2000:                                       # end zones X would meet: the whole storey at step <= 100
        n = max(1, int(math.ceil(S / 100.0 - 1e-9)))
        st = S / n
        return [a + st * i for i in range(n + 1)], (n, 0, 0), [st] * n
    X = S / 4.0
    n1 = int(math.ceil(X / 100.0 - 1e-9))
    M = S - 200.0 * n1
    k = int(M // 200); r = M - 200 * k
    if r < 1e-6: mid = [200.0] * k
    elif r >= 100 - 1e-6: mid = [200.0] * k; mid.insert(len(mid) // 2, r)
    else:
        k -= 2; q = (r + 400.0) / 3.0
        mid = [200.0] * k
        for _ in range(3): mid.insert(len(mid) // 2, q)
    steps = [100.0] * n1 + mid + [100.0] * n1
    pos = [a]
    for s in steps: pos.append(pos[-1] + s)
    assert abs(pos[-1] - b) < 1e-6, (pos[-1], b)
    return pos, (n1, len(mid), n1), steps

def chain(levels, beams):
    """levels [L0, L1, ...] (L0 = foundation top), beams[i] = beam height at levels[i+1]
    -> (hoop positions, chain segments (y1, y2, step, n), per-storey (pos, zones))"""
    P = []; pts = [levels[0]]; per = []
    for i in range(len(levels) - 1):
        bb = levels[i + 1] - beams[i]
        p, z, s = storey_hoops(levels[i], bb); P += p; per.append((p, z))
        pts += p + [bb, levels[i + 1]]
    d = [pts[k + 1] - pts[k] for k in range(len(pts) - 1)]
    segs = []; k = 0
    while k < len(d):
        m = k
        while m + 1 < len(d) and abs(d[m + 1] - d[k]) < 1e-6 and d[k] < 250: m += 1
        segs.append((pts[k], pts[m + 1], d[k], m - k + 1)); k = m + 1
    return P, segs, per

if __name__ == '__main__':
    for L, B in (([0, 1150, 8200], [900, 900]), ([0, 1150, 5700, 8200], [900, 900, 900])):
        P, segs, per = chain(L, B)
        print(len(P), [(round(a), round(b), round(s), n) for a, b, s, n in segs])
