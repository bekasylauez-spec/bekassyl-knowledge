import sys; sys.path.insert(0, 'wl'); from common import *
import ezdxf
gx.run([{'t': 'dxfout', 'file': gx.S + r'\w\kt.dxf'}], 'dx')
d = ezdxf.readfile(gx.S + r'\w\kt.dxf'); ops = []
for e in d.modelspace().query('TEXT MTEXT'):
    p = e.dxf.insert; s = e.text if e.dxftype() == 'MTEXT' else e.dxf.text
    if not (1578300 < p.x < 1697100 and 455939 < p.y < 497939): continue
    n = s.replace('^ J', '\P').replace('^J', '\P').replace('^ I', '\t').replace('^I', '\t')
    if '4.13}' in s: n = '{\C256;5.17}'
    if '4.14}' in s: n = '{\C256;5.18}'
    if 'Вертикальное,горизонтальное' in s: n = 'Армирование монолитной стены\Pмежду осями Б и В стена См-5 (тол.250мм)'
    if n != s: ops.append({'t': 'settext', 'h': e.dxf.handle, 's': n}); print(e.dxf.handle, repr(s[:60]), '->', repr(n[:60]))
ops.append({'t': 'save'}); print(gx.run(ops, 'ft')[-20:])
