import io, re, collections

def docs(path):
    s = io.open(path, encoding='utf-8-sig').read()
    out = {}
    for m in re.finditer(r'\(\s*(\d+)/(.*?)\n\s*\)', s, re.S):
        out.setdefault(int(m.group(1)), m.group(2))
    return s, out

def recs(body):
    return [r.split() for r in body.replace('\n', ' ').split('/') if r.strip()]

def load(path):
    s, d = docs(path)
    els = [list(map(int, r)) for r in recs(d[1])]          # type stiff nodes...
    nodes = [tuple(map(float, r)) for r in recs(d[4])]
    l6 = [list(map(int, r[:5])) for r in recs(d[6])]
    l7 = {}
    for r in recs(d[7]):
        l7[int(r[0])] = list(map(float, r[1:]))
    return s, d, els, nodes, l6, l7
