"""place dimension texts at exact centres using AutoCAD feedback (geomdump), 2 corrections"""
import ab, os
def centres(win):
    f = ab.S + r'\w\gd_local.txt'
    ab.run([{'t': 'geomdump', 'win': list(win), 'file': f}], 'gdl')
    C = {}
    for ln in open(f, encoding='utf-8-sig'):
        p = ln.rstrip('\r\n').split('|')
        if p[0] == 'T' and len(p) > 7 and p[7].strip():
            b = [float(v) for v in p[3:7]]
            C.setdefault(p[1], []).append(((b[0] + b[2]) / 2, (b[1] + b[3]) / 2))
    return {h: v[0] for h, v in C.items()}
def place(targets, win, rounds=2):
    at = dict(targets)
    ab.run([{'t': 'dimtx', 'h': h, 'at': list(p)} for h, p in at.items()], 'pl0')
    for r in range(rounds):
        C = centres(win)
        ops = []
        for h, (tx, ty) in targets.items():
            if h not in C: continue
            cx, cy = C[h]
            if abs(cx - tx) + abs(cy - ty) < 5: continue
            at[h] = (at[h][0] + (tx - cx), at[h][1] + (ty - cy))
            ops.append({'t': 'dimtx', 'h': h, 'at': list(at[h])})
        if not ops: break
        ab.run(ops, 'pl%d' % (r + 1))
    ab.run([{'t': 'save'}], 'plsave')
