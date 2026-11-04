# Chains of rotated dimensions cloned from the user's template (style СПДС, layer 0), text placement like the user's 2.1:
# text in the text row (225 from the line), short ones shifted along the line beyond the segment end, else one row further out.
import math
TPL = 'CC00A'          # user's vertical dimension (rot 90, default text)
TH = 250.0             # text height on the sheet (2.5 mm x 100)
OFF = 225.0            # text centre offset from the dim line


def tw(s):
    return 0.64 * TH * len(s)


def chain(pts, line, vertical, outward, tpl=TPL, X=0.0, Y=0.0, occupied=None, minlen=1, side=False, avoid=()):
    """pts: list of (x, y) extension origins (relative). vertical chain: line = x of dim line, coordinate = y;
    horizontal: line = y, coordinate = x. outward: +1/-1 side away from the building (for the 2nd text row).
    Returns ops. occupied: list of (a, b, row) text intervals already used on this line (shared between calls)."""
    key = 1 if vertical else 0
    pts = sorted(pts, key=lambda p: p[key])
    segs = []
    for p, q in zip(pts, pts[1:]):
        L = q[key] - p[key]
        if L < minlen: continue
        segs.append((p, q, L))
    occ = occupied if occupied is not None else []
    place = {}
    # texts that fit between their extension lines stay in the middle
    for i, (p, q, L) in enumerate(segs):
        s = '%d' % round(L); w = tw(s)
        if L >= w + 230:
            c = (p[key] + q[key]) / 2; place[i] = (c, 0); occ.append((c - w / 2, c + w / 2, 0))
    allc = [pt[key] for pt in pts]
    def free(a, b, row):
        if row == 0 and any(a - 40 < c < b + 40 for c in allc): return False
        return all(b + 40 <= o[0] or a - 40 >= o[1] for o in occ if o[2] == row)
    for i, (p, q, L) in enumerate(segs):
        if i in place or not side: continue
        # Bekassyl 04.11 (✓ sample): a short text goes to the OUTER side of the chain, right at its own segment, on a
        # short shelf; neighbours that collide step one more column outward — never far along the line, never inside
        s = '%d' % round(L); w = tw(s)
        mid = (p[key] + q[key]) / 2
        done = False
        for row in (1, 2, 3, 4):
            near = [v for v in avoid if abs(v - mid) < w]
            cs = [mid, mid + w / 4, mid - w / 4] + [v + sg * (w / 2 + 80) for v in near for sg in (1, -1)]
            cs = [c for c in cs if abs(c - mid) <= w]          # stay at the own segment
            for c in cs:
                if any(c - w / 2 - 60 < v < c + w / 2 + 60 for v in avoid): continue
                if all(c + w / 2 + 60 <= o[0] or c - w / 2 - 60 >= o[1] for o in occ if o[2] == row):
                    place[i] = (c, row); occ.append((c - w / 2, c + w / 2, row)); done = True; break
            if done: break
        if not done:
            place[i] = (mid, 4); occ.append((mid - w / 2, mid + w / 2, 4))
    for i, (p, q, L) in enumerate(segs):
        if i in place: continue
        s = '%d' % round(L); w = tw(s)
        a, b = p[key], q[key]
        cands = []
        first, last = i == 0, i == len(segs) - 1
        after = b + w / 2 + 90; before = a - w / 2 - 90
        if last: cands = [after, before]
        elif first: cands = [before, after]
        else:
            # toward the longer neighbour
            ln = segs[i - 1][2]; rn = segs[i + 1][2]
            cands = [after, before] if rn >= ln else [before, after]
        done = False
        for c in cands:
            if free(c - w / 2, c + w / 2, 0):
                place[i] = (c, 0); occ.append((c - w / 2, c + w / 2, 0)); done = True; break
        if not done:
            for k in range(1, 2):
                for c in (after + k * (w + 60), before - k * (w + 60)):
                    if free(c - w / 2, c + w / 2, 0):
                        place[i] = (c, 0); occ.append((c - w / 2, c + w / 2, 0)); done = True; break
                if done: break
        if not done:
            c = (a + b) / 2
            place[i] = (c, 1); occ.append((c - w / 2, c + w / 2, 1))
    ops = []
    for i, (p, q, L) in enumerate(segs):
        c, row = place[i]
        if vertical:
            dl = [X + line, Y + q[1]]
            txx = line - OFF if row == 0 else (line - OFF - 450 * row if outward < 0 else line + OFF + 500 + 420 * (row - 1))
            tx = [X + txx, Y + c]
            op = {'t': 'dim', 'h': tpl, 'p1': [X + p[0], Y + p[1]], 'p2': [X + q[0], Y + q[1]], 'dl': dl, 'rot': math.pi / 2}
            mid = (p[1] + q[1]) / 2
        else:
            dl = [X + q[0], Y + line]
            tyy = line + OFF if row == 0 else (line + OFF + 450 * row if outward > 0 else line - OFF - 225 - 420 * (row - 1))
            tx = [X + c, Y + tyy]
            op = {'t': 'dim', 'h': tpl, 'p1': [X + p[0], Y + p[1]], 'p2': [X + q[0], Y + q[1]], 'dl': dl, 'rot': 0.0}
            mid = (p[0] + q[0]) / 2
        if abs(c - mid) > 1 or row: op['tx'] = tx
        ops.append(op)
    return ops
