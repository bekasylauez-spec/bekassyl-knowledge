# hoop positions per storey: 50 | 100 x n1 | 150 | 200 x n2 | 100 x n3 | 50  (X + 2X + X, one 150 step at the 100→200 change)
def storey(a, b):
    H = b - a; inner = H - 100
    best = None
    for n1 in range(5, 20):
        for n3 in range(5, 20):
            r = inner - 100 * n1 - 150 - 100 * n3
            if r < 0 or r % 200: continue
            n2 = int(r // 200)
            X1, X3, X2 = 50 + 100 * n1, 50 + 100 * n3, 150 + 200 * n2
            sc = abs(X1 - H / 4) + abs(X3 - H / 4) + abs(X2 - H / 2) + (0 if n3 >= n1 else 1)
            if best is None or sc < best[0]: best = (sc, n1, n2, n3)
    _, n1, n2, n3 = best
    p = [a + 50]
    for _ in range(n1): p.append(p[-1] + 100)
    p.append(p[-1] + 150)
    for _ in range(n2 - 1): p.append(p[-1] + 200)
    for _ in range(n3): p.append(p[-1] + 100) if False else None
    # rebuild cleanly
    p = [a + 50]
    for _ in range(n1): p.append(p[-1] + 100)
    p.append(p[-1] + 150)
    for _ in range(n2): p.append(p[-1] + 200)
    for _ in range(n3): p.append(p[-1] + 100)
    assert abs(p[-1] - (b - 50)) < 1e-6, (p[-1], b)
    zones = [(a, p[n1] + 50, 100), (p[n1] + 50, p[n1 + 1 + n2] , 200), (p[n1 + 1 + n2], b, 100)]
    return p, (n1, n2, n3)

def chain(levels):
    """hoop positions for all storeys + merged chain segments [(y1,y2,step,n)]"""
    P = []
    for a, b in zip(levels, levels[1:]):
        p, n = storey(a, b); P += p
    seq = [levels[0]] + P + [levels[-1]]
    d = [round(seq[k + 1] - seq[k]) for k in range(len(seq) - 1)]
    segs = []; k = 0
    while k < len(d):
        m = k
        while m + 1 < len(d) and d[m + 1] == d[k] and d[k] in (100, 200): m += 1
        segs.append((seq[k], seq[m + 1], d[k], m - k + 1)); k = m + 1
    return P, segs

if __name__ == '__main__':
    for a, b in ((0, 4550), (4550, 8600)): print(storey(a, b)[1])
    P, s = chain([0, 4550, 8600]); print(len(P)); print(s)
