import pickle, re, collections, sys
rows = pickle.load(open(sys.argv[1] + 'rows.pkl', 'rb'))
pat = sys.argv[2]
print('n rows', len(rows))
frames = [r for r in rows if r[1] == 'ACAD_PROXY_ENTITY' and r[5] - r[3] > 15000 and r[6].startswith('Формат')]
print('frames', len(frames))
for r in sorted(frames, key=lambda r: (r[2], r[3])):
    print('  F', r[0], [round(v) for v in r[2:6]], r[6][:40])
c = collections.Counter()
for r in rows:
    if r[1] in ('TEXT', 'MTEXT') and re.fullmatch(pat, r[6].strip()):
        c[r[7]] += 1
        print('  N', r[0], r[1], r[7], repr(r[6]), round(r[2]), round(r[3]))
print(c)
