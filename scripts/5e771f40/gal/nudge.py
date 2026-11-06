# residual oc issues: slide the offending SPDS object (section mark / доп. callout) along x until the sheet is clean
import sys, re, gx, fix
SHEETS = sys.argv[1:]


def sheet_xy(no):
    k = int(no.split('.')[1]); return 172179.0 + (k - 5) * 31500.0, 420000.0


def cls(h):
    o = gx.run([dict(t='sp_get', h=[h])], 'spg')
    m = re.search(r'SP \S+ \S+ (\S+):', o)
    return m.group(1) if m else ''


for no in SHEETS:
    sx, sy = sheet_xy(no)
    n, out = fix.check(no, sx, sy)
    tried = set()
    for it in range(8):
        if n == 0: break
        iss = [l for l in out.splitlines() if l.startswith('  ')]
        target = None
        for l in iss:
            q = re.search(r'"([^"]*)"', l)
            if not q: continue
            q = q.group(1); lab = q.split('|')[0].split('#')[0]
            m1 = re.search(r'#([0-9A-F]+)', q); h1 = m1.group(1) if m1 else None
            m2 = re.search(r'<>\s+(?:.*?#)?([0-9A-F]+)\s+@', l); h2 = m2.group(1) if m2 else None
            for h in ([h2] if lab.startswith('Н4') else [h1, h2]):
                if h and h not in tried and cls(h).startswith('SPDS') and 'COMB' not in cls(h):
                    target = h; break
            if target: break
        if not target: break
        tried.add(target)
        best = None
        for dx in (600, -600, 1000, -1000, 1400, -1400, 1800, -1800, 2400, -2400):
            gx.run([dict(t='move', h=[target], d=[dx, 0])], 'ng')
            n2, out2 = fix.check(no, sx, sy)
            if n2 < n: best = (dx, n2, out2); break
            gx.run([dict(t='move', h=[target], d=[-dx, 0])], 'ng')
        if best:
            n, out = best[1], best[2]
            print(no, 'moved', target, best[0], '->', n, flush=True)
    print(no, 'TOTAL', n, flush=True)
    if n: print('\n'.join(l for l in out.splitlines() if l.startswith('  ')), flush=True)
gx.run([dict(t='save')], 'sv', wait=300)
