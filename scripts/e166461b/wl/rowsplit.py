# rows of horizontal bars: first 50 above the slab, last 50 below the next slab, the leftover (< step) one space in the middle
def rows(yb, yt, st, slab=250.0):
    y0, y1 = yb + 50, yt - slab - 50
    D = y1 - y0; n = int(D // st + 1e-6); rem = int(round(D - n * st))
    sp = [st] * n if rem < 5 else [st] * (n // 2) + [rem] + [st] * (n - n // 2)
    pos = [y0]
    for v in sp: pos.append(pos[-1] + v)
    segs = []; y = y0
    for v in sp:
        if segs and segs[-1][2] == v: segs[-1] = (segs[-1][0], y + v, v, segs[-1][3] + 1)
        else: segs.append((y, y + v, v, 1))
        y += v
    return pos, segs
