import sys, ezdxf, collections, re
doc = ezdxf.readfile(sys.argv[1]); msp = doc.modelspace()
sh = []
for l in open(sys.argv[2], encoding='utf-8'):
    m = re.match(r"(\d+) \| лист \['(\d+)'\]", l)
    if m: sh.append((int(m.group(1)), m.group(2)))
sh.sort()
def which(x):
    prev = -1e18
    for xr, n in sh:
        if prev < x <= xr + 10: return n
        prev = xr
    return None
cnt = collections.Counter(); kinds = collections.defaultdict(collections.Counter); ex = collections.defaultdict(list)
types = collections.Counter()
for e in msp:
    t = e.dxftype(); types[t] += 1
    if t == 'DIMENSION' or (t == 'INSERT' and e.dxf.name.upper().startswith(('SPDS', '_SPDS'))) or t.startswith('MCS') or t.startswith('SPDS') or t == 'ACAD_PROXY_ENTITY':
        try: p = e.dxf.defpoint if t == 'DIMENSION' else e.dxf.insert
        except Exception:
            try: p = e.proxy_graphic and None
            except Exception: p = None
        if p is None: continue
        n = which(p.x)
        if n is None: continue
        kinds[n][t] += 1
        if t == 'DIMENSION':
            try: ex[n].append(round(e.get_measurement()) if not isinstance(e.get_measurement(), tuple) else 0)
            except Exception: pass
for xr, n in sh:
    v = ex[n]
    print(n, dict(kinds[n]), 'vals', sorted(collections.Counter(v).items())[:40])
print(types.most_common(30))
