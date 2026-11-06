import io, os
# 1) b4rig: spec table grows downwards on inserted rows -> lift it by the added height (rows 400)
b = io.open('b4rig.py', encoding='utf-8').read()
old = """        if nd > 2: ops.append(dict(t='trows', h=sp, mode='ins', at=7, n=nd - 2, **{'from': 7}))"""
new = """        if nd > 2:
            ops.append(dict(t='trows', h=sp, mode='ins', at=7, n=nd - 2, **{'from': 7}))
            ops.append(dict(t='move', h=[sp], d=[0, 400.0 * (nd - 2)]))"""
assert old in b; b = b.replace(old, new)
io.open('b4rig.py', 'w', encoding='utf-8').write(b)

# 2) rdesign: one length for all top доп and one for all bottom доп of a mark (positions 2 / 3)
p = os.path.join('..', 'lira', 'rdesign.py')
r = io.open(p, encoding='utf-8').read()
old2 = """    Ls = sorted(set(d['L'] for d in dops), reverse=True)
    for d in dops: d['pos'] = str(2 + Ls.index(d['L']))"""
new2 = """    for top in (True, False):              # one length per group: the longest one, bars re-centred inside the beam
        grp = [d for d in dops if d['top'] == top]
        if not grp: continue
        Lg = max(d['L'] for d in grp)
        for d in grp:
            c = (d['a'] + d['b']) / 2.0; a, b_ = c - Lg / 2.0, c + Lg / 2.0
            if a < 50: b_ += 50 - a; a = 50
            if b_ > E - 50: a -= b_ - (E - 50); b_ = E - 50
            d['a'], d['b'], d['L'] = a, b_, Lg
    kinds = [k for k in (True, False) if any(d['top'] == k for d in dops)]
    for d in dops: d['pos'] = str(2 + kinds.index(d['top']))
    Ls = kinds"""
assert old2 in r; r = r.replace(old2, new2)
io.open(p, 'w', encoding='utf-8').write(r)
print('ok')
