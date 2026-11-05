"""1-D grid retile of an analog sheet: every entity is cloned (style kept) and its control points are remapped
from the analog axis grid to the new one.  Node-local entities are replicated to every new node built from that
analog node, bay entities to every new bay, global entities (long walls, outlines, overall dims) are remapped once,
polylines/hatch loops spanning interior nodes get their vertex runs repeated per new node."""
import math, re
import ext

INF = 1e18
RIGID_TYPES = {'TEXT', 'MTEXT', 'INSERT', 'CIRCLE', 'SPDSLEVELMARK', 'SPDSPLANELEVELMARK', 'WIPEOUT', 'MULTILEADER',
               'SPDSNOTEPOSITION', 'SPDSNOTECOMB', 'SPDSNOTEMULTILAYER', 'SPDSNOTEKNOT', 'SPDSRELATIONMARK', 'SPDSBOUNDFORM',
               'ARC', 'POINT', 'SPDSWELD'}
MULTI_TYPES = {'SPDSCONSTRUCTIONLINE', 'SPDSSECTION', 'SPDSBREAK'}


class Pass:
    def __init__(s, axis, apos, groups, primary, r, npos, nodemap, baymap):
        s.ax = 0 if axis == 'x' else 1
        s.apos, s.groups, s.primary, s.r, s.npos = apos, groups, primary, r, npos
        s.nodemap, s.baymap = nodemap, baymap
        s.zone = []
        for gi, g in enumerate(groups):
            lo = -INF if gi == 0 else apos[g[0]] - r
            hi = INF if gi == len(groups) - 1 else apos[g[-1]] + r
            s.zone.append((lo, hi))
        # new unit sequence: (kind, new index, template position)
        tn = {}
        for gi, js in nodemap.items():
            for j in js: tn[j] = gi
        tb = {}
        for gi, js in baymap.items():
            for j in js: tb[j] = gi
        s.NU = []
        for j in range(len(npos)):
            s.NU.append(('n', j, 2 * tn[j]))
            if j < len(npos) - 1:
                s.NU.append(('b', j, 2 * tb[j] + 1))

    def anchor(s, v):
        for gi, (lo, hi) in enumerate(s.zone):
            if lo <= v <= hi:
                g = s.groups[gi]; a0 = s.apos[g[0]]; a1 = s.apos[g[-1]]
                off = v - a0 if v <= a0 else (v - a1 if v >= a1 else 0.0)
                sub = min(g, key=lambda i: abs(v - s.apos[i]))
                return ('n', gi, off, sub)
        for gi in range(len(s.groups) - 1):
            hi = s.zone[gi][1]; lo = s.zone[gi + 1][0]
            if hi < v < lo:
                return ('b', gi, (v - hi) / (lo - hi), None)
        raise ValueError(v)

    @staticmethod
    def pos(a):
        return 2 * a[1] + (1 if a[0] == 'b' else 0)

    def newv(s, a, inst):
        if a[0] == 'n':
            j = inst['n'].get(a[1])
            if j is None: return None
            return s.npos[j] + a[2]
        j = inst['b'].get(a[1])
        if j is None: return None
        hi = s.npos[j] + s.r; lo = s.npos[j + 1] - s.r
        return hi + a[2] * (lo - hi)

    def node_inst(s, gi, j):
        return {'n': {gi: j}, 'b': {}}

    def bay_inst(s, gi, j):
        return {'n': {gi: j, gi + 1: j + 1}, 'b': {gi: j}}

    def global_inst(s):
        inst = {'n': {}, 'b': {}}
        for gi, js in s.nodemap.items():
            if js: inst['n'][gi] = js[0]
        for gi, js in s.baymap.items():
            if js: inst['b'][gi] = js[0]
        return inst

    def global_inst_last(s):
        inst = {'n': {}, 'b': {}}
        for gi, js in s.nodemap.items():
            if js: inst['n'][gi] = js[-1]
        for gi, js in s.baymap.items():
            if js: inst['b'][gi] = js[-1]
        return inst

    def classify(s, anchors):
        """-> list of instances, or 'global', or [] (drop)"""
        ps = [s.pos(a) for a in anchors]
        lo, hi = min(ps), max(ps)
        if lo == hi and lo % 2 == 0:
            gi = lo // 2
            return [s.node_inst(gi, j) for j in s.nodemap.get(gi, [])]
        g0 = lo // 2 if lo % 2 == 0 else (lo - 1) // 2
        if hi <= 2 * g0 + 2:
            if lo == 2 * g0 + 2:  # pure node g0+1 handled above
                pass
            return [s.bay_inst(g0, j) for j in s.baymap.get(g0, [])]
        return 'global'

    # ---- polyline run expansion for global polylines ----
    def expand_run(s, verts):
        """verts: list of (coord_along, other, bulge, anchor) -> list of (new_along, other, bulge)"""
        if not verts: return []
        runs = []
        for v in verts:
            p = s.pos(v[3])
            if runs and runs[-1][0] == p: runs[-1][1].append(v)
            else: runs.append([p, [v]])
        # chains of monotone template position
        chains = []
        cur = [runs[0]]; d = 0
        for r in runs[1:]:
            step = (r[0] > cur[-1][0]) - (r[0] < cur[-1][0])
            if d == 0 or step == d:
                d = step if step else d; cur.append(r)
            else:
                chains.append((d, cur)); cur = [cur[-1], r] if False else [r]; d = step
        chains.append((d, cur))
        out = []
        for d, ch in chains:
            tps = [r[0] for r in ch]
            idx_first = [k for k, u in enumerate(s.NU) if u[2] == tps[0]]
            idx_last = [k for k, u in enumerate(s.NU) if u[2] == tps[-1]]
            if not idx_first or not idx_last:
                # chain starts/ends in a dropped unit: map units independently
                rng = [k for k, u in enumerate(s.NU) if u[2] in set(tps)]
                if d < 0: rng = rng[::-1]
            elif d >= 0:
                a, b = idx_first[0], idx_last[-1]
                rng = list(range(a, b + 1)) if b >= a else [a]
            else:
                a, b = idx_first[-1], idx_last[0]
                rng = list(range(a, b - 1, -1)) if a >= b else [a]
            for k in rng:
                kind, j, tp = s.NU[k]
                inst = s.node_inst(tp // 2, j) if kind == 'n' else s.bay_inst(tp // 2, j)
                for r in ch:
                    if r[0] != tp: continue
                    for v in r[1]:
                        nv = s.newv(v[3], inst)
                        if nv is not None: out.append((nv, v[1], v[2]))
        # dedupe consecutive
        res = []
        for v in out:
            if res and abs(res[-1][0] - v[0]) < 0.01 and abs(res[-1][1] - v[1]) < 0.01: continue
            res.append(v)
        return res


def P(pt, ax, val):
    q = list(pt)
    q[ax] = val
    return q


def hloops(e):
    m = re.match(r'hl=(.*?)\|pat=', e.info)
    if not m: return []
    loops = []
    for lp in m.group(1).split('#'):
        pts = []
        for q in lp.split(';'):
            a = q.split(',')
            if len(a) == 3: pts.append((float(a[0]), float(a[1]), float(a[2])))
        loops.append(pts)
    return loops


def dim_rot(e):
    m = re.search(r'rot=(-?[\d.]+)', e.info)
    if m: return float(m.group(1))
    p = e.dimpts()
    if len(p) >= 2: return math.atan2(p[1][1] - p[0][1], p[1][0] - p[0][0])
    return 0.0


def plan_pass(es, ps, pre, opts=None):
    """es: entities to retile; ps: Pass. returns (ops, erase_handles, stats)"""
    ops = []; erase = []; stats = {'local': 0, 'bay': 0, 'global': 0, 'drop': 0, 'skip': 0, 'clones': 0}
    ax = ps.ax
    seen = set()
    k = 0

    def emit_clone(e, d, inst_id):
        nonlocal k
        tg = '%s%d_' % (pre, inst_id)
        dv = [0.0, 0.0]; dv[ax] = d
        ops.append({'t': 'clonexf', 'hs': [e.h], 'd': dv, 'pre': tg})
        stats['clones'] += 1
        return tg + e.h

    for e in es:
        t = e.dxf
        try:
            if t in ('SPDSFORMAT', 'ACAD_TABLE'):
                stats['skip'] += 1; continue
            if t == 'DIMENSION':
                p = e.dimpts()
                if len(p) < 3: stats['skip'] += 1; continue
                p1, p2, dl = p[0], p[1], p[2]
                rot = dim_rot(e)
                horiz = abs(math.sin(rot)) < 0.5   # measures along x
                along = (ax == 0) == horiz          # this pass changes the measured length
                if along:
                    ctrl = [p1[ax], p2[ax]]
                else:
                    ctrl = [p1[ax], p2[ax], dl[ax]]
                anc = [ps.anchor(v) for v in ctrl]
                cls = ps.classify(anc)
                insts = [ps.global_inst()] if cls == 'global' else cls
                if not insts: stats['drop'] += 1; erase.append(e.h); continue
                stats['global' if cls == 'global' else ('local' if len(set(ps.pos(a) for a in anc)) == 1 else 'bay')] += 1
                udt = e.kv.get('udt', '1') == '1'
                tp = None
                if not udt:
                    m = re.search(r'tp=(-?[\d.]+)_(-?[\d.]+)', e.info)
                    if m: tp = (float(m.group(1)), float(m.group(2)))
                for ii, inst in enumerate(insts):
                    n = [ps.newv(a, inst) for a in anc]
                    if any(v is None for v in n): continue
                    q1 = P(p1, ax, n[0]); q2 = P(p2, ax, n[1])
                    if along:
                        if abs(n[0] - n[1]) < 1.0: continue
                        q3 = P(dl, ax, (n[0] + n[1]) / 2)
                    else:
                        q3 = P(dl, ax, n[2])
                    pp = sorted([(round(q1[0]), round(q1[1])), (round(q2[0]), round(q2[1]))])
                    key = ('D', pp[0], pp[1], round(q3[ax ^ 1] if along else q3[ax]))
                    if key in seen: continue
                    seen.add(key)
                    h = emit_clone(e, 0, k); k += 1
                    op = {'t': 'dimset2', 'h': h, 'p1': q1, 'p2': q2, 'dl': q3}
                    if tp is not None:
                        a3 = ps.anchor(tp[ax]); v3 = ps.newv(a3, inst)
                        if v3 is None: v3 = (n[0] + n[1]) / 2
                        op['tx'] = P(tp, ax, v3)
                    ops.append(op)
                erase.append(e.h); continue
            if t == 'LWPOLYLINE' or t == 'HATCH':
                if t == 'LWPOLYLINE':
                    loops = [e.plpts()]; closed = e.info.startswith('plc')
                else:
                    loops = hloops(e); closed = True
                if not loops or not loops[0]: stats['skip'] += 1; continue
                if t == 'HATCH' and any(len(lp) < 3 for lp in loops):
                    loops = None
            if t == 'HATCH' and loops is None:
                pass
            elif t == 'LWPOLYLINE' or t == 'HATCH':
                allv = [v for lp in loops for v in lp]
                anc_all = [ps.anchor(v[ax]) for v in allv]
                cls = ps.classify(anc_all)
                if cls == []: stats['drop'] += 1; erase.append(e.h); continue
                if cls == 'global':
                    stats['global'] += 1
                    newloops = []
                    for lp in loops:
                        vv = [(v[ax], v[ax ^ 1], v[2], ps.anchor(v[ax])) for v in lp]
                        if closed and len(vv) > 2:
                            imin = min(range(len(vv)), key=lambda i: (ps.pos(vv[i][3]), vv[i][0]))
                            vv = vv[imin:] + vv[:imin]
                        res = ps.expand_run(vv)
                        newloops.append([([r[0], r[1]] if ax == 0 else [r[1], r[0]]) + [r[2]] for r in res])
                    newloops = [lp for lp in newloops if len(lp) >= 2]
                    if not newloops or len(newloops) < len(loops):
                        stats['drop'] += 1; erase.append(e.h); continue
                    insts_loops = [newloops]
                else:
                    stats['local' if len(set(ps.pos(a) for a in anc_all)) == 1 else 'bay'] += 1
                    insts_loops = []
                    for inst in cls:
                        nl = []
                        ok = True
                        for lp in loops:
                            q = []
                            for v in lp:
                                nv = ps.newv(ps.anchor(v[ax]), inst)
                                if nv is None: ok = False; break
                                q.append(P(v[:2], ax, nv) + [v[2]])
                            nl.append(q)
                        if ok: insts_loops.append(nl)
                for nl in insts_loops:
                    key = ('P', t, e.lay) + tuple(sorted((round(v[0]), round(v[1])) for lp in nl for v in lp))
                    if key in seen: continue
                    seen.add(key)
                    h = emit_clone(e, 0, k); k += 1
                    if t == 'LWPOLYLINE':
                        ops.append({'t': 'plset', 'h': h, 'p': [v[:2] for v in nl[0]], 'b': [v[2] for v in nl[0]]})
                    else:
                        ops.append({'t': 'hatchset', 'h': h, 'loops': nl})
                erase.append(e.h); continue
            if t == 'LINE':
                m = re.match(r'ln=(-?[\d.]+),(-?[\d.]+);(-?[\d.]+),(-?[\d.]+)', e.info)
                p1 = (float(m.group(1)), float(m.group(2))); p2 = (float(m.group(3)), float(m.group(4)))
                anc = [ps.anchor(p1[ax]), ps.anchor(p2[ax])]
                cls = ps.classify(anc)
                if cls == []: stats['drop'] += 1; erase.append(e.h); continue
                if cls == 'global':
                    stats['global'] += 1
                    gi1 = ps.global_inst()
                    pairs = [(ps.newv(anc[0], gi1), ps.newv(anc[1], gi1))]
                else:
                    stats['local' if len(set(ps.pos(a) for a in anc)) == 1 else 'bay'] += 1
                    pairs = [(ps.newv(anc[0], inst), ps.newv(anc[1], inst)) for inst in cls]
                for n1, n2 in pairs:
                    if n1 is None or n2 is None: continue
                    q1 = P(p1, ax, n1); q2 = P(p2, ax, n2)
                    key = ('L', e.lay, round(q1[0]), round(q1[1]), round(q2[0]), round(q2[1]))
                    if key in seen: continue
                    seen.add(key)
                    h = emit_clone(e, 0, k); k += 1
                    ops.append({'t': 'lnset', 'h': h, 'p1': q1, 'p2': q2})
                erase.append(e.h); continue
            if t in MULTI_TYPES:
                sp = e.sp
                if not sp: stats['skip'] += 1; continue
                anc = [ps.anchor(q[ax]) for q in sp]
                cls = ps.classify(anc)
                if cls == []: stats['drop'] += 1; erase.append(e.h); continue
                if cls == 'global':
                    stats['global'] += 1
                    gi1 = ps.global_inst()
                    lst = [[ps.newv(a, gi1) for a in anc]]
                else:
                    stats['local' if len(set(ps.pos(a) for a in anc)) == 1 else 'bay'] += 1
                    lst = [[ps.newv(a, inst) for a in anc] for inst in (cls[:1] if t == 'SPDSSECTION' else cls)]
                for n in lst:
                    if any(v is None for v in n): continue
                    key = ('M', t) + tuple(round(v) for v in n) + tuple(round(q[ax ^ 1]) for q in sp)
                    if key in seen: continue
                    seen.add(key)
                    d0 = n[0] - sp[0][ax]
                    h = emit_clone(e, d0, k); k += 1
                    items = []
                    for i, q in enumerate(sp):
                        if abs(n[i] - q[ax] - d0) > 0.01:
                            items.append([i] + P(q, ax, n[i]))
                    if items: ops.append({'t': 'spmove', 'h': h, 'items': items})
                erase.append(e.h); continue
            # rigid
            if t == 'SPDSNOTEPOSITION' and len(e.sp) >= 2: rep = e.sp[1]
            elif e.sp: rep = e.sp[0]
            elif e.bb: rep = (e.cx, e.cy)
            else: stats['skip'] += 1; continue
            a = ps.anchor(rep[ax])
            cls = ps.classify([a])
            if cls == []: stats['drop'] += 1; erase.append(e.h); continue
            insts = [ps.global_inst()] if cls == 'global' else cls
            stats['local' if a[0] == 'n' else 'bay'] += 1
            txt = e.kv.get('txt', '') + e.kv.get('blk', '')
            if t in ('MTEXT', 'TEXT') and len(re.sub(r'\[A-Za-z][^;]*;|[{}]', '', txt)) >= 15:
                insts = insts[:1]   # titles / notes are unique
            for inst in insts:
                nv = ps.newv(a, inst)
                if nv is None: continue
                d = nv - rep[ax]
                key = ('R', t, e.lay, txt, round(rep[ax ^ 1]), round(nv))
                if key in seen: continue
                seen.add(key)
                emit_clone(e, d, k); k += 1
            erase.append(e.h)
        except Exception as ex:
            stats['skip'] += 1
            print('ERR', e, ex)
    return ops, erase, stats
