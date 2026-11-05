# restore the main inscription (stamp) of a sheet by cloning the stamp box of a good sheet of the same format, then its texts
# usage: python wl/stampfix.py target_X src_X W title number [--keep-target]
import sys, re; sys.path.insert(0, 'wl'); from common import *
from lwin import lw
TX, SX, W = (float(v) for v in sys.argv[1:4]); title, num = sys.argv[4], sys.argv[5]; Y = 455939.0
box = lambda X: (X + W - 20600, Y - 700, X + W + 5, Y + 6300)
src = [r for r in lw(*box(SX)) if r['ext'] and r['t'] != 'SPDSFORMAT' and r['ext'][0] >= SX + W - 20600 and r['ext'][2] <= SX + W + 5 and r['ext'][1] >= Y - 700 and r['ext'][3] <= Y + 6300]
tgt = [r for r in lw(*box(TX)) if r['ext'] and r['t'] != 'SPDSFORMAT' and r['ext'][0] >= TX + W - 20600 and r['ext'][2] <= TX + W + 5 and r['ext'][1] >= Y - 700 and r['ext'][3] <= Y + 6300]
print('src', len(src), 'tgt', len(tgt))
ops = [dict(t='erase', h=[r['h'] for r in tgt])] + [dict(t='clone', h=r['h'], base=[SX, 0], to=[TX, 0], tag='SF%d' % i) for i, r in enumerate(src)]
out = gx.run(ops + [dict(t='save')], 'sf1'); print([l for l in out.splitlines() if 'ERR' in l or 'done' in l][-3:])
# texts: the source's title (longest MTEXT/TEXT in the name field) and sheet number
import ezdxf
gx.run([{'t': 'dxfout', 'file': gx.S + r'\w\sf.dxf'}], 'dx')
doc = ezdxf.readfile(gx.S + r'\w\sf.dxf'); ops = []
for e in doc.modelspace().query('TEXT MTEXT'):
    p = e.dxf.insert
    if not (TX + W - 20600 <= p.x <= TX + W and Y - 700 <= p.y <= Y + 6300): continue
    s = e.text if e.dxftype() == 'MTEXT' else e.dxf.text
    if re.fullmatch(r'\s*[45]\.\d+\s*', s): ops.append(dict(t='settext', h=e.dxf.handle, s=num))
    elif TX + W - 12400 <= p.x <= TX + W - 6200 and p.y < Y + 2400 and len(s) > 12: ops.append(dict(t='settext', h=e.dxf.handle, s=title))
print('texts', [(o['h'], o['s'][:40]) for o in ops])
print(gx.run(ops + [dict(t='save')], 'sf2')[-40:])
