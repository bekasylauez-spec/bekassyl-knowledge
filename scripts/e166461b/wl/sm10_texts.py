# См-10 sheet texts: wall mark, sheet numbers, notes (sheet range, 61d), section sheet stamp title
import sys, re, ezdxf; sys.path.insert(0, 'wl'); from common import *
gx.run([{'t': 'dxfout', 'file': gx.S + r'\w\kt.dxf'}], 'dx')
doc = ezdxf.readfile(gx.S + r'\w\kt.dxf'); msp = doc.modelspace(); ops = []
SH = [(2632200, 59400, 42000, '5.39'), (2733600, 42000, 59400, '5.41'), (2775600, 42000, 59400, '5.42'), (2817600, 59400, 42000, '5.43')]
for X0, W, H, num in SH:
    for e in msp.query('TEXT MTEXT'):
        p = e.dxf.insert
        if not (X0 < p.x < X0 + W and 455939 - 800 < p.y < 455939 + H): continue
        s = e.text if e.dxftype() == 'MTEXT' else e.dxf.text
        n = s.replace('стена См-7', 'стена См-10').replace('КЖ-4.26 ... 4.29', 'КЖ-5.39 ... 5.44').replace('71d', '61d')
        if re.fullmatch(r'\s*4\.\d+\s*', s): n = num
        if 'Армирование' in s and 'М(1:50)' in s: n = 'Разрезы 1-1, 2-2, 3-3 (Армирование) М1:50 стены См-10'
        n = n.replace('^I', '\t')
        if n != s.replace('^I', '\t'): ops.append({'t': 'settext', 'h': e.dxf.handle, 's': n}); print(num, s[:60].replace('\n', ' '), '->', n[:60])
ops.append({'t': 'save'})
print(len(ops), gx.run(ops, 'tx10')[-40:])
