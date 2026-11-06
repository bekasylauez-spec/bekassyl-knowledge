# БДМ Блок 1 rigels: pieces (one b x h) from scheme lines + LIRA As -> reinforcement design + unified marks
import json, math, collections
L = json.load(open('lines2.json')); COLS = json.load(open('cols.json'))
AXX = [(0,'1'),(6000,'2'),(12000,'3'),(18000,'4'),(24000,'5'),(30000,'6'),(36000,'7'),(42000,'8'),(47500,'9'),(53500,'10'),(59500,'11'),(65900,'12'),(73100,'13'),(73750,'14')]
AXY = [(0,'А'),(9000,'Б'),(13900,'В'),(21000,'Г'),(27500,'Д'),(36000,'Е'),(39000,'Ж')]
LVK = {-0.05:'1', 4.5:'2', 7.0:'3'}
DS = [20, 22, 25, 28, 32]
def a(d): return math.pi * d * d / 400.0          # cm2
def axlab(v, axes):
    for p, n in axes:
        if abs(p - v) < 1: return n
    return None
def colsat(ln, u):
    """column rect crossing line ln at local coordinate u (+-50)"""
    k = LVK[ln['z']]; c = ln['c']; res = []
    for x0, y0, x1, y1 in COLS[k]:
        if ln['d'] == 'X':
            if y0 - 1 <= c <= y1 + 1 and x0 - 60 <= u <= x1 + 60: res.append((x0, x1))
        else:
            if x0 - 1 <= c <= x1 + 1 and y0 - 60 <= u <= y1 + 60: res.append((y0, y1))
    return res
def pieces(ln):
    """split line into pieces of constant section; spans = list of (faceL, faceR, h)"""
    segs = ln['segs']; prof = ln.get('prof') or []
    sp = []
    for s0, s1 in segs:
        hs = collections.Counter(p[5][1] for p in prof if p[1] > s0 + 1 and p[0] < s1 - 1)
        h = hs.most_common(1)[0][0] * 10 if hs else (ln['bh'][1] * 10 if ln.get('bh') else None)
        sp.append([s0, s1, h])
    out = [[sp[0]]]
    for s in sp[1:]:
        if s[2] == out[-1][-1][2]: out[-1].append(s)
        else: out.append([s])
    return out
def need(prof, a0, a1, i):
    v = [p[i] for p in prof if p[1] > a0 + 1 and p[0] < a1 - 1]
    return v
def dopz(prof, i, n, d, endL, endR):
    zones = []
    for p in prof:
        ex = p[i] - n * a(d)
        if ex > 0.05:
            k = math.ceil(ex / a(d) - 1e-6)
            if zones and p[0] - zones[-1][1] < 300: zones[-1][1] = p[1]; zones[-1][2] = max(zones[-1][2], k)
            else: zones.append([p[0], p[1], k])
    dz = []
    an = math.ceil(40 * d / 100.0) * 100
    for z0, z1, k in zones:
        u0, u1 = max(endL + 30, z0 - an), min(endR - 30, z1 + an)
        if dz and u0 <= dz[-1]['u1']:
            dz[-1]['u1'] = max(dz[-1]['u1'], u1); dz[-1]['k'] = max(dz[-1]['k'], k); continue
        dz.append(dict(u0=round(u0), u1=round(u1), k=k, d=d))
    for z in dz:
        Lz = math.ceil((z['u1'] - z['u0']) / 100.0) * 100; z['u1'] = z['u0'] + Lz; z['row2'] = z['k'] > n - 1
    return dz
def design(ln, sp):
    b = int(ln['b']); h = sp[0][2]
    n = 3 if b <= 300 else 4
    legs = 2 if b <= 300 else 4
    a0, a1 = sp[0][0], sp[-1][1]
    # supports at ends: column (main) or beam (secondary)
    cL = colsat(ln, a0 - 30); cR = colsat(ln, a1 + 30)
    endL = min(c[0] for c in cL) if cL else a0 - 250
    endR = max(c[1] for c in cR) if cR else a1 + 250
    prof = [p for p in ln.get('prof') or [] if p[1] > endL + 1 and p[0] < endR - 1]
    res = dict(b=b, h=h, n=n, a0=a0, a1=a1, endL=endL, endR=endR, colL=bool(cL), colR=bool(cR), spans=[(s[0], s[1]) for s in sp])
    for key, i in (('bot', 2), ('top', 3)):
        v = [p[i] for p in prof] or [0]
        vs = sorted(v); base = vs[int(0.7 * (len(vs) - 1))]
        d0 = next((d for d in DS if n * a(d) >= base), 32)
        for d in [x for x in DS if x >= d0]:
            dz = dopz(prof, i, n, d, endL, endR)
            if all(z['k'] <= n - 1 for z in dz): break
        res[key] = dict(d=d, n=n, max=round(max(v), 2), dop=dz)
    # hoops: support zone (1/4 span) step 100, middle 200
    sw = [p[4] for p in prof] or [0]
    swmax = max(sw)
    mid = []
    for f0, f1 in res['spans']:
        q = (f1 - f0) / 4.0
        mid += [p[4] for p in prof if p[0] >= f0 + q - 1 and p[1] <= f1 - q + 1]
    swmid = max(mid) if mid else 0
    dh = next((d for d in (8, 10, 12, 14, 16) if legs * a(d) * 10 >= swmax and legs * a(d) * 5 >= swmid), None)
    res['hoop'] = dict(d=dh or 16, legs=legs, swmax=round(swmax, 1), swmid=round(swmid, 1), ok=dh is not None)
    res['L'] = endR - endL
    return res
marks = []
for ln in L:
    if not ln.get('prof'): 
        marks.append(dict(z=ln['z'], d=ln['d'], c=ln['c'], nolira=True, segs=ln['segs'])); continue
    for sp in pieces(ln):
        r = design(ln, sp); r.update(z=ln['z'], d=ln['d'], c=ln['c'], lira_c=ln['lira_c'])
        marks.append(r)
json.dump(marks, open('pieces.json', 'w'), ensure_ascii=False)
for r in marks:
    if r.get('nolira'): print('NOLIRA', r['z'], r['d'], r['c']); continue
    ax = axlab(r['c'], AXY if r['d'] == 'X' else AXX)
    print('%5.2f %s %-6s b%d h%d L%5d sp%d  top %dØ%d(max%.1f)+%s  bot %dØ%d(max%.1f)+%s  hoop Ø%d/%d %s sw%.0f/%.0f' % (
        r['z'], r['d'], ax or r['c'], r['b'], r['h'], r['L'], len(r['spans']), r['n'], r['top']['d'], r['top']['max'],
        [ (z['k'], z['u1']-z['u0']) for z in r['top']['dop']], r['n'], r['bot']['d'], r['bot']['max'], [(z['k'], z['u1']-z['u0']) for z in r['bot']['dop']],
        r['hoop']['d'], r['hoop']['legs'], '' if r['hoop']['ok'] else 'NG', r['hoop']['swmax'], r['hoop']['swmid']))
