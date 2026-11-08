# ================= Р2 □100x3 ends on the bottom chord side faces: fillet welds round the end
for c, u in gen.P2_ENDS:
    g = 'Узел Р2 ' + str(int(c[0])) + ' ' + str(int(c[1]))
    for a, dvec, out in (([0, -50, -50], [0, 1, 0], [0, 0, -1]), ([0, -50, 50], [0, 1, 0], [0, 0, 1]), ([0, -50, -50], [0, 0, 1], [0, -1, 0]), ([0, 50, -50], [0, 0, 1], [0, 1, 0])):
        weld(g, add(c, a), out, [-u[0], 0, 0], dvec, 4, 100)
# ================= ФФ1 lattice welded straight to the chords: fillet welds round the footprint of every cut end
def cross(a, b): return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]
def dot(a, b): return sum(a[i] * b[i] for i in range(3))
for k, e in enumerate(gen.TRUSS_ENDS):
    U = e['u']; Wv = [1, 0, 0]; Vv = gen.nrm(cross(U, Wv)); p, m, b = e['p'], e['m'], e['b']; hb = b / 2
    corners = []
    for sv, sw in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        o = [p[i] + Vv[i] * sv * hb + Wv[i] * sw * hb for i in range(3)]
        t = dot([p[i] - o[i] for i in range(3)], m) / dot(U, m)
        corners.append([o[i] + U[i] * t for i in range(3)])
    cen = [sum(c[i] for c in corners) / 4 for i in range(3)]
    g = 'шов решётки ФФ1 ' + str(int(p[0])) + ' ' + str(k)
    for q in range(4):
        a, bq = corners[q], corners[(q + 1) % 4]; dv = [bq[i] - a[i] for i in range(3)]; ln = math.sqrt(dot(dv, dv)); dv = [c / ln for c in dv]
        mid = [(a[i] + bq[i]) / 2 - cen[i] for i in range(3)]
        out = [mid[i] - dv[i] * dot(mid, dv) - m[i] * dot(mid, m) for i in range(3)]; out = gen.nrm(out)
        weld(g, a, out, [-c for c in U], dv, 4, ln)
# bottom chord tube ends: cap −6 outside the end, square to the chord
for (x, y, z, sgn) in gen.CHORD_ENDS:
    g = 'Заглушка НП ' + str(int(x)) + ' ' + str(int(y))
    dvec = gen.nrm([0, sgn, gen.dz(y) * sgn]); ev = gen.nrm(cross(dvec, [1, 0, 0])); eu = cross(ev, dvec)
    plt(g, [x, y, z], eu, ev, -60, -60, 60, 60, 6)
