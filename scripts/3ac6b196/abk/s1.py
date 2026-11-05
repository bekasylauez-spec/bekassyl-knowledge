import ezdxf, collections, sys, re, io
out = io.open(sys.argv[2], 'w', encoding='utf-8')
d = ezdxf.readfile(sys.argv[1]); m = d.modelspace()
def dec(s):
    return re.sub(r'\\U\+([0-9A-Fa-f]{4})', lambda g: chr(int(g.group(1), 16)), s)
ex = collections.defaultdict(list)
for e in m:
    if e.dxftype() in ('TEXT', 'MTEXT'):
        t = e.dxf.text if e.dxftype() == 'TEXT' else e.plain_text()
        p = e.dxf.insert
        ex[round(p.y / 60)].append((p.x, dec(t).replace('\n', ' '), e.dxf.layer[:6]))
for y in sorted(ex, reverse=True):
    r = sorted(ex[y])
    # split row into clusters separated by >3000 gap
    cl = [[r[0]]]
    for a in r[1:]:
        if a[0] - cl[-1][-1][0] > 3000: cl.append([a])
        else: cl[-1].append(a)
    for c in cl:
        out.write('%7d %8d | %s\n' % (y * 60, c[0][0], ' '.join(t for _, t, _ in c)))
