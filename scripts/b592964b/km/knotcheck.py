# knotcheck.py <notes.tsv>  — проверка выносок СПДС по геометрии (вывод rn.cs op "notelist")
# Узел: полка должна идти от круга наружу — при Rack левее центра габарит выходит левее Rack, и наоборот.
# Позиционная выноска: длина выноски не больше 1500 мм модели (15 мм на листе М 1:100).
import sys, math
bad = 0
for line in open(sys.argv[1], encoding='utf-8-sig'):
    if not line.startswith('N\t'): continue
    f = line.rstrip('\n').split('\t')
    h, kind, l1, l2, knot, align = f[1], f[2], f[3], f[4], f[5], f[6]
    pts = [tuple(map(float, p.split(','))) for p in f[10:] if p and not p.startswith('E')]
    ext = next((list(map(float, p[1:].split(','))) for p in f[10:] if p.startswith('E')), None)
    if kind == 'SPDSNOTEKNOT' and len(pts) >= 2 and ext:
        (cx, cy), (rx, ry) = pts[0], pts[1]
        side_ok = (ext[0] < rx - 50) if rx < cx else (ext[2] > rx + 50)
        if not side_ok:
            bad += 1; print(f'УЗЕЛ {knot} ({h}): полка загнута к кругу — заменить копией правильного узла')
    elif kind == 'SPDSNOTEPOSITION' and len(pts) >= 2:
        L = math.dist(pts[0], pts[1])
        if L > 1500:
            bad += 1; print(f'ВЫНОСКА «{l1}{l2}» ({h}): длина выноски {L:.0f} > 1500')
print('замечаний:', bad)
