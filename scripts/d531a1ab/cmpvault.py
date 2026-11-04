import os, sys, hashlib, re, json, datetime
loc, sh = sys.argv[1], sys.argv[2]
skip = re.compile(r'^\.obsidian[\\/]workspace.*\.json$|^\.trash[\\/]', re.I)
def walk(root):
    out = {}
    for d, _, fs in os.walk(root):
        for f in fs:
            p = os.path.join(d, f); r = os.path.relpath(p, root)
            if not skip.match(r): out[r.lower()] = (r, p)
    return out
def h(p):
    m = hashlib.sha256()
    with open(p, 'rb') as fh:
        for c in iter(lambda: fh.read(1 << 20), b''): m.update(c)
    return m.hexdigest()
L, S = walk(loc), walk(sh)
only, diff, same = [], [], 0
for k, (r, p) in sorted(L.items()):
    if k not in S: only.append(r); continue
    q = S[k][1]; a, b = os.stat(p), os.stat(q)
    if a.st_size == b.st_size and h(p) == h(q): same += 1
    else:
        t = lambda s: datetime.datetime.fromtimestamp(s.st_mtime).strftime('%d.%m %H:%M')
        diff.append({'path': r, 'local': [a.st_size, t(a)], 'shared': [b.st_size, t(b)]})
res = {'local': len(L), 'shared': len(S), 'same': same, 'only_local': only, 'diff': diff}
json.dump(res, open(sys.argv[3], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f"local={len(L)} shared={len(S)} same={same} only_local={len(only)} diff={len(diff)}")
