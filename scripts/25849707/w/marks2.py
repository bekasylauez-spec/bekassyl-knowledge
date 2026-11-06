# envelope unification: pieces with the same geometry -> one mark designed on the max-envelope of their LIRA profiles
import json, math, collections
import design as D
L = {(round(l['z'], 3), l['d'], l['c'], l['segs'][0][0]): l for l in json.load(open('lines2.json'))}
P = [p for p in json.load(open('pieces.json')) if not p.get('nolira')]
def rel_prof(p):
    ln = [l for k, l in L.items() if k[0] == round(p['z'], 3) and k[1] == p['d'] and k[2] == p['c'] and l['segs'][0][0] <= p['a0'] + 1 and l['segs'][-1][1] >= p['a1'] - 1][0]
    return [(q[0] - p['endL'], q[1] - p['endL'], q[2], q[3], q[4]) for q in ln['prof'] if q[1] > p['endL'] + 1 and q[0] < p['endR'] - 1]
def geo(p):
    sp = tuple(round(b - a, -2) for a, b in p['spans'])
    gaps = tuple(round(p['spans'][i + 1][0] - p['spans'][i][1], -2) for i in range(len(p['spans']) - 1))
    ends = (round(p['spans'][0][0] - p['endL'], -2), round(p['endR'] - p['spans'][-1][1], -2), p['colL'], p['colR'])
    return (p['b'], p['h'], sp, gaps, ends)
def geo_rev(p):
    g = geo(p); return (g[0], g[1], g[2][::-1], g[3][::-1], (g[4][1], g[4][0], g[4][3], g[4][2]))
groups = collections.OrderedDict()
for p in sorted(P, key=lambda r: (r['z'], r['d'] == 'Y', r['c'], r['a0'])):
    g = geo(p); gr = geo_rev(p)
    if g in groups: groups[g].append((p, False))
    elif gr in groups: groups[gr].append((p, True))
    else: groups[g] = [(p, False)]
def envelope(members):
    p0 = members[0][0]; Lt = p0['endR'] - p0['endL']
    bins = []
    u = 0.0
    while u < Lt - 1:
        bins.append([u, min(Lt, u + 250.0), 0.0, 0.0, 0.0]); u += 250.0
    for p, rev in members:
        Lp = p['endR'] - p['endL']
        for q in rel_prof(p):
            a, b = q[0], q[1]
            if rev: a, b = Lp - q[1], Lp - q[0]
            for bn in bins:
                if bn[1] > a + 1 and bn[0] < b - 1:
                    bn[2] = max(bn[2], q[2]); bn[3] = max(bn[3], q[3]); bn[4] = max(bn[4], q[4])
    return bins
def core(p0, prof):
    """design on relative profile (u from endL); reuse D logic"""
    b = p0['b']; n = 3 if b <= 300 else 4; legs = 2 if b <= 300 else 4
    endL, endR = 0.0, p0['endR'] - p0['endL']
    spans = [(a - p0['endL'], c - p0['endL']) for a, c in p0['spans']]
    pr = [(q[0], q[1], q[2], q[3], q[4], None) for q in prof]
    res = dict(b=b, h=p0['h'], n=n, endL=endL, endR=endR, colL=p0['colL'], colR=p0['colR'], spans=spans, L=endR)
    for key, i in (('bot', 2), ('top', 3)):
        v = [q[i] for q in pr] or [0]
        vs = sorted(v); base = vs[int(0.7 * (len(vs) - 1))]
        d0 = next((d for d in D.DS if n * D.a(d) >= base), 32)
        for d in [x for x in D.DS if x >= d0]:
            dz = D.dopz(pr, i, n, d, endL, endR)
            if all(z['k'] <= n - 1 for z in dz): break
        res[key] = dict(d=d, n=n, max=round(max(v), 2), dop=dz)
    sw = [q[4] for q in pr] or [0]; swmax = max(sw); mid = []
    for f0, f1 in spans:
        qq = (f1 - f0) / 4.0; mid += [q[4] for q in pr if q[0] >= f0 + qq - 1 and q[1] <= f1 - qq + 1]
    swmid = max(mid) if mid else 0
    dh = next((d for d in (8, 10, 12, 14, 16) if legs * D.a(d) * 10 >= swmax and legs * D.a(d) * 5 >= swmid), None)
    res['hoop'] = dict(d=dh or 16, legs=legs, swmax=round(swmax, 1), swmid=round(swmid, 1), ok=dh is not None)
    return res
def mx(p):
    pr = rel_prof(p); return (max([q[3] for q in pr] or [0]), max([q[2] for q in pr] or [0]), max([q[4] for q in pr] or [0]))
clusters = []
for g, mem in groups.items():
    mem = sorted(mem, key=lambda t: -mx(t[0])[0])
    cl = []
    for t in mem:
        v = mx(t[0])
        for c in cl:
            if all(v[i] >= 0.7 * c['v'][i] - 1.0 for i in range(3)): c['m'].append(t); break
        else: cl.append(dict(v=v, m=[t]))
    for c in cl:
        c['m'].sort(key=lambda t: (t[0]['c'], t[0]['a0'])); clusters.append(c['m'])
clusters.sort(key=lambda m: (m[0][0]['z'], m[0][0]['d'] == 'Y', m[0][0]['c'], m[0][0]['a0']))
marks = []
for mem in clusters:
    p0 = mem[0][0]
    r = core(p0, envelope(mem))
    locs = []
    for p, rev in mem:
        ax = D.AXY if p['d'] == 'X' else D.AXX
        lab = D.axlab(p['c'], ax)
        near = lambda u: min((D.AXX if p['d'] == 'X' else D.AXY), key=lambda q: abs(q[0] - u))[1]
        locs.append(dict(z=p['z'], d=p['d'], c=p['c'], lab=lab, frm=near(p['endL']), to=near(p['endR']), endL=p['endL'], endR=p['endR'], rev=rev))
    marks.append(dict(name='Рм-%d' % (len(marks) + 1), z=p0['z'], d=p0['d'], p0=p0, r=r, locs=locs))
json.dump(marks, open('marks2.json', 'w'), ensure_ascii=False)
ns = 0
for m in marks:
    r = m['r']; L_ = r['L']
    nsh = max(1, math.ceil((L_ + 500) / 21400.0))
    ns += nsh
    print('%-6s %5.2f b%dx%-4d L%5d sp%-2d top %dØ%d+%d bot %dØ%d+%d X Ø%d/%d%s x%d sh%d  %s' % (m['name'], m['z'], r['b'], r['h'], L_, len(r['spans']), r['n'], r['top']['d'], len(r['top']['dop']), r['n'], r['bot']['d'], len(r['bot']['dop']), r['hoop']['d'], r['hoop']['legs'], '' if r['hoop']['ok'] else ' NG', len(m['locs']), nsh,
          '; '.join('%s %s(%s-%s)' % (l['d'], l['lab'] or int(l['c']), l['frm'], l['to']) for l in m['locs'])))
print(len(marks), 'marks, sheets ~', ns)
