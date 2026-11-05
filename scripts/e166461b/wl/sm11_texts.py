# См-11 sheet texts (clones of См-7): wall mark / axis 4 / sheet numbers / note range; horizontal axis marks «1» -> «4»
import sys, re, ezdxf; sys.path.insert(0, 'wl'); from common import *
gx.run([{'t': 'dxfout', 'file': gx.S + r'\w\kt.dxf'}], 'dx')
doc = ezdxf.readfile(gx.S + r'\w\kt.dxf'); msp = doc.modelspace(); ops = []
SH = [(2906700, 59400, 42000, '5.45'), (2966100, 42000, 29700, '5.46'), (3008100, 42000, 59400, '5.47'), (3050100, 42000, 59400, '5.48'), (3092100, 59400, 42000, '5.49')]
NUM = {'5.24': '5.45', '5.25': '5.46', '5.26': '5.47', '5.27': '5.48', '5.29': '5.49'}
for X0, W, H, num in SH:
    for e in msp.query('TEXT MTEXT'):
        p = e.dxf.insert
        if not (X0 < p.x < X0 + W and 455939 - 800 < p.y < 455939 + H): continue
        s = e.text if e.dxftype() == 'MTEXT' else e.dxf.text
        n = s.replace('по оси 1 стена См-7', 'по оси 4 стена См-11').replace('стены См-7', 'стены См-11').replace('стена См-7', 'стена См-11').replace('КЖ-5.24 ... 5.29', 'КЖ-5.45 ... 5.50')
        if s.strip() in NUM: n = NUM[s.strip()]
        n = n.replace('^I', '\t')
        if n != s.replace('^I', '\t'): ops.append({'t': 'settext', 'h': e.dxf.handle, 's': n}); print(num, s[:50].replace('\n', ' '), '->', n[:50].replace('\n', ' '))
    for r in listwin(X0, 455939, W, H, None):
        if r['t'] == 'SPDSCONSTRUCTIONLINE' and abs(r['sp'][0][1] - r['sp'][1][1]) < 1:
            (sx, sy), (ex, ey) = r['sp'][0], r['sp'][1]
            ops.append(dict(t='axis', h=r['h'], s=[X0 + sx, 455939 + sy], e=[X0 + ex, 455939 + ey], val='4'))
ops.append({'t': 'save'})
out = gx.run(ops, 'tx11'); print(len(ops), [l for l in out.splitlines() if 'ERR' in l or 'done' in l])
