import sys, json, os
sys.path.insert(0, r'C:\Users\Admin\AppData\Local\Temp\claude\210ab68cad67e8c1\e166461b-bde0-4f75-9345-660eafbd0735\scratchpad')
import gx
DOC1 = '5.1.Стена См-1...См-6.dwg'
F = json.load(open(gx.S + r'\st\frames.json', encoding='utf-8'))
def frame(k, i): return F[k][i][:2]
def listwin(X0, Y0, w, h, doc):
    gx.run([{'t': 'list', 'win': [X0, Y0, X0 + w, Y0 + h]}], 'lst', doc)
    R = []
    for l in open(os.environ['TEMP'] + '/gx_log.txt', encoding='utf-8').read().splitlines():
        if not l.startswith('L\t'): continue
        r = l.split('\t'); e = [float(v) for v in r[4][1:].split(',')]
        sp = [tuple(float(c) for c in p.split(',')) for p in r[5:]]
        R.append(dict(t=r[1], h=r[2], lay=r[3], x0=e[0] - X0, y0=e[1] - Y0, x1=e[2] - X0, y1=e[3] - Y0, sp=[(p[0] - X0, p[1] - Y0) for p in sp]))
    return R
def stretch_ops(X0, Y0, MAP, axis='x', lo=-1e9, hi=1e9, xmax=33000, ymin=0, ymax=42000):
    """piecewise map of analog coords -> ours, as successive STRETCH windows (left to right)"""
    ops = []; cum = 0.0
    for a, b in sorted(MAP):
        cur = a + cum; dlt = b - cur
        if abs(dlt) < 0.5: continue
        if axis == 'x': ops.append(dict(t='stretch', win=[X0 + cur - 1, Y0 + ymin, X0 + xmax, Y0 + ymax], d=[dlt, 0]))
        else: ops.append(dict(t='stretch', win=[X0 + lo, Y0 + cur - 1, X0 + hi, Y0 + ymax], d=[0, dlt]))
        cum += dlt
    return ops
