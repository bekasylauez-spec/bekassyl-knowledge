# Рм-1..Рм-3 (sheets 6.1-6.3): main 4+4 Ø20, splices Н1, top dop Ø20 (pos 2 Г-hooked at end supports, pos 3 at
# internal supports), sections 1-1 / 2-2 cloned from sheet 6.5 (analog-derived), section marks 2-2 on the facade.
#   python gen_a.py <k> [--run]
import sys, json
from common import *
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from layout import L as LAYOUT

MARK = {0: 'Рм-1', 1: 'Рм-2', 2: 'Рм-3'}
YT, YB, YDT = 468670.0, 468200.0, 468620.0
HK = 240.0
# note positions (u) per dop piece index and section-2 marker positions (u)
NOTE_U = {'Рм-1': [900, 5300, 12450, 19000], 'Рм-2': [6300, 12450, 19000], 'Рм-3': [900, 5300, 12450, 19000]}
MARK2_U = {'Рм-1': [1700, 6200], 'Рм-2': [14500, 18300], 'Рм-3': [1700, 6200]}
SRC_DOPLINE, SRC_DOPNOTE, SRC_SECMARK = '2D29D7', '2D29D8', '2D29D3'   # sheet 6.5 (pos2 top line / note / mark «2»)
NOTE_BASE = (305632.0, 468620.0)
SEC_WIN65 = [303300, 460600, 312800, 465400]


def build(k):
    mk = MARK[k]; X0 = SX(k)
    X = lambda u: X0 + 3128.0 + u
    E = ents(k); E65 = ents(4)
    ops = []; add = lambda **kw: ops.append(kw)
    # 1. main bars -> Ø20 layer
    for e in E:
        if e['t'] == 'LWPOLYLINE' and e['lay'] == 'диам25' and abs(e['e'][1] - e['e'][3]) < 1 and e['e'][2] - e['e'][0] > 15000:
            add(t='plset', h=e['h'], p=[list(q) for q in e['p'][:2]], layer='диам20')
    # 2. facade position notes «1 (ф25)» -> (ф20)
    add(t='noteset', win=[X0, 467000, X0 + 31500, 470500], **{'from': '1', 'to': '1', 'l2': '(ф20)'})
    # 3. splices: rect 250 -> 200 centred, label Н3 -> Н1
    for e in E:
        x0, y0, x1, y1 = e['e']
        if e['t'] == 'LWPOLYLINE' and e['lay'] == 'Размеры' and abs((x1 - x0) - 250) < 2 and abs((y1 - y0) - 30) < 2 and 468000 < y0 < 468800:
            c = (x0 + x1) / 2
            add(t='plset', h=e['h'], p=[[c - 100, y0], [c - 100, y1], [c + 100, y1], [c + 100, y0]], closed=True)
        if e['t'] == 'SPDSNOTECOMB' and 467900 < y0 < 469300 and y1 < 469300:
            add(t='mcset', h=e['h'], set={'FirstLine': 'Н1'})
    # 4. dop bars + notes
    pieces = LAYOUT[mk]
    for i, (pos, side, n, u0, u1, h0, h1) in enumerate(pieces):
        y = YDT
        p = [[X(u0), y], [X(u1), y]]
        if h0: p.insert(0, [X(u0), y - HK])
        if h1: p.append([X(u1), y - HK])
        tag = 'dl%d_%d' % (k, i)
        add(t='clone', h=SRC_DOPLINE, tag=tag)
        add(t='plset', h=tag, p=p, layer='диам20')
        nt = 'dn%d_%d' % (k, i)
        ux = NOTE_U[mk][i]
        assert u0 + 150 < ux < u1 - 150, (mk, i, ux)
        add(t='clone', h=SRC_DOPNOTE, base=list(NOTE_BASE), to=[X(ux), y], tag=nt)
        add(t='mcset', h=nt, set={'FirstLine': pos, 'SecondLine': '(ф20)'})
    # 5. sections: erase old 1-1, clone 6.5 1-1 + 2-2
    old = inside(E, [X0 + 10200, 460200, X0 + 14800, 465000])
    add(t='erase', h=[e['h'] for e in old])
    dx = X0 + 10362.0 - 303420.0
    for e in inside(E65, SEC_WIN65):
        add(t='clone', h=e['h'], base=[0, 0], to=[dx, 0], tag='s%d_%s' % (k, e['h']))
    T = lambda h: 's%d_%s' % (k, h)
    for h in ('2D2FFB', '2D2FFC', '2D31B5', '2D31B6'):
        add(t='mcset', h=T(h), set={'SecondLine': '(ф20)'})
    n_sup = max(p[2] for p in pieces)
    add(t='mcset', h=T('2D3304'), set={'FirstLine': '2;3' if any(p[0] == '2' for p in pieces) else '3', 'SecondLine': '(ф20)'})
    ys, ye = 463660.0, 464702.5
    if n_sup == 2:
        add(t='erase', h=[T('2D32F6')])
        tx = [310879 + dx, 311479 + dx]
    else:
        tx = [310879 + dx, 311179 + dx, 311479 + dx]
    segs = [[[x, ys], [x + 429.671361502, ye]] for x in tx]
    while len(segs) < 4: segs.append(segs[-1])
    add(t='combsegs', h=T('2D3304'), segs=segs)
    # 6. facade marks «2»: clone 6.5 mark (zone point x 306332) to X(u)
    for j, u in enumerate(MARK2_U[mk]):
        add(t='clone', h=SRC_SECMARK, base=[306332.0, 0], to=[X(u), 0], tag='m%d_%d' % (k, j))
    return ops


if __name__ == '__main__':
    k = int(sys.argv[1])
    ops = build(k)
    json.dump(ops, open(os.path.join(S, 'ops', 'a%d.json' % k), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print(len(ops), 'ops')
    if '--run' in sys.argv:
        r, lg, errs = run(ops, 'a%d' % k)
        print(r[:300]); print('\n'.join(errs[:30]))
