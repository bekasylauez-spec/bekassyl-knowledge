import ezdxf, sys, re, io
d = ezdxf.readfile(sys.argv[1])
out = io.open(sys.argv[2], 'w', encoding='utf-8')
pat = re.compile(sys.argv[3], re.I)
def dec(s): return re.sub(r'\\U\+([0-9A-Fa-f]{4})', lambda g: chr(int(g.group(1), 16)), s)
def texts(space):
    for e in space:
        t = None
        if e.dxftype() == 'TEXT': t = e.dxf.text
        elif e.dxftype() == 'MTEXT': t = e.plain_text()
        elif e.dxftype() == 'INSERT':
            for a in e.attribs: yield dec(a.dxf.text), e
        if t: yield dec(t), e
for lay in d.layouts:
    for t, e in texts(lay):
        if pat.search(t): out.write('[%s] %s\n' % (lay.name, t.replace('\n', ' | ')[:600]))
for b in d.blocks:
    if b.name.startswith('*') and not b.name.startswith('*U'): continue
    for t, e in texts(b):
        if pat.search(t): out.write('{%s} %s\n' % (b.name, t.replace('\n', ' | ')[:600]))
