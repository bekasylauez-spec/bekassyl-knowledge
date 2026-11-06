# Column geometry by Bekassyl's rules (05.11.2026):
# hoops per storey from lower level +50 up to beam bottom -50; that span S is split X + 2X + X (X = S/4),
# end zones step 100 (n = ceil(X/100)), middle step 200; the leftover (<=200) goes inside the 200 zone (middle of it).
# No hoops inside the beam height (meshes there). Main bars spliced every storey with накладки, staggered: corners +600, mids +1200.
import math

def storey_hoops(lo, beam_bot):
    a, b = lo + 50.0, beam_bot - 50.0
    S = b - a; X = S / 4.0
    n = int(math.ceil(X / 100.0 - 1e-9))
    best = None
    for n1 in (n, n - 1, n + 1):
        M = S - 200.0 * n1
        if M < 400: continue
        k = int(M // 200); r = M - 200 * k
        if r < 1e-6: cand = (0, n1, k, 0.0)
        else: cand = (1, n1, k, r)
        if best is None or cand[0] < best[0] or (cand[0] == best[0] and abs(cand[1] - X / 100) < abs(best[1] - X / 100)): best = cand
    _, n1, k, r = best
    steps = [100.0] * n1
    mid = [200.0] * k
    if r > 1e-6: mid.insert(len(mid) // 2, r)
    steps += mid + [100.0] * n1
    pos = [a]
    for s in steps: pos.append(pos[-1] + s)
    assert abs(pos[-1] - b) < 1e-6, (pos[-1], b)
    zones = (n1, len(mid), n1)
    return pos, zones, steps

def chain(levels, beams):
    """levels: [L0, L1, ...]; beams: beam height at L1, L2, ... -> (all hoop positions, chain segments (y1,y2,step,n))"""
    P = []; pts = [levels[0]]
    for i in range(len(levels) - 1):
        bb = levels[i + 1] - beams[i]
        p, z, s = storey_hoops(levels[i], bb); P += p
        pts += p + [bb, levels[i + 1]]
    d = [pts[k + 1] - pts[k] for k in range(len(pts) - 1)]
    segs = []; k = 0
    while k < len(d):
        m = k
        while m + 1 < len(d) and abs(d[m + 1] - d[k]) < 1e-6 and d[k] in (80.0, 100.0, 200.0): m += 1
        segs.append((pts[k], pts[m + 1], d[k], m - k + 1)); k = m + 1
    return P, segs

if __name__ == '__main__':
    for lo, bb in ((0, 4550 - 550), (4550, 8600 - 550)):
        p, z, s = storey_hoops(lo, bb); print(lo, z, len(p), s[:3], s[len(s)//2-1:len(s)//2+2])
    P, segs = chain([0, 4550, 8600], [550, 550]); print(len(P)); print(segs)
