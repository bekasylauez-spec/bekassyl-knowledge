# Рм-4 (6.4) and Рм-5 (6.5): main Ø20, dop Ø20 per layout.py, sections updated
#   python gen_b.py 3|4 [--run]
import sys, json
from common import *

YDT = 468620.0


def build4():
    k = 3; X0 = SX(k); X = lambda u: X0 + 6278.0 + u
    E = ents(k); E65 = ents(4)
    ops = []; add = lambda **kw: ops.append(kw)
    for h in ('2D06A7', '2D06CD'):
        e = [x for x in E if x['h'] == h][0]
        add(t='plset', h=h, p=[list(q) for q in e['p'][:2]], layer='диам20')
    add(t='noteset', win=[X0, 467000, X0 + 31500, 470500], **{'from': '1', 'to': '1', 'l2': '(ф20)'})
    add(t='plset', h='2D0B78', p=[[X(-3255), YDT], [X(105), YDT], [X(105), YDT - 240]], layer='диам20')
    add(t='mcset', h='2D0B79', set={'SecondLine': '(ф20)'})
    add(t='erase', h=['2D0B74'])                                   # facade mark 2-2 (one section 1-1 now)
    old = inside(E, [X0 + 5100, 460200, X0 + 14700, 465400])
    add(t='erase', h=[e['h'] for e in old])
    dx = X0 - SX(4) - 5000.0
    for e in inside(E65, [308300, 460600, 312800, 465400]):
        add(t='clone', h=e['h'], base=[0, 0], to=[dx, 0], tag='t3_' + e['h'])
    add(t='settext', h='t3_2D31B2', s='Разрез 1 - 1')
    for h in ('2D31B5', '2D31B6'):
        add(t='mcset', h='t3_' + h, set={'SecondLine': '(ф20)'})
    add(t='mcset', h='t3_2D3304', set={'FirstLine': '2', 'SecondLine': '(ф20)'})
    return ops


def build5():
    k = 4; X0 = SX(k); X = lambda u: X0 + 3003.0 + (u - 23050.0)
    E = ents(k)
    ops = []; add = lambda **kw: ops.append(kw)
    for h in ('2D2506', '2D252C'):
        e = [x for x in E if x['h'] == h][0]
        add(t='plset', h=h, p=[list(q) for q in e['p'][:2]], layer='диам20')
    add(t='noteset', win=[X0, 467000, X0 + 31500, 470500], **{'from': '1', 'to': '1', 'l2': '(ф20)'})
    add(t='plset', h='2D29D7', p=[[X(26230), YDT], [X(30600), YDT]], layer='диам20')
    add(t='mcset', h='2D29D8', set={'SecondLine': '(ф20)'})
    add(t='plset', h='2D29D9', p=[[X(23070), 468250 + 240], [X(23070), 468250], [X(26090), 468250]], layer='диам20')
    add(t='mcset', h='2D29DA', set={'SecondLine': '(ф20)'})
    # pos 4: 2nd top row
    add(t='clone', h='2D29D7', tag='p4l')
    add(t='plset', h='p4l', p=[[X(26730), 468575], [X(29750), 468575]], layer='диам20')
    add(t='clone', h='2D29D8', base=[305632.0, 468620.0], to=[X(29200), 468575.0], tag='p4n')
    add(t='mcset', h='p4n', set={'FirstLine': '4', 'SecondLine': '(ф20)'})
    # section texts
    for h in ('2D2FFB', '2D2FFC', '2D31B5', '2D31B6', '2D3304', '2D3385', '2D3386'):
        add(t='mcset', h=h, set={'SecondLine': '(ф20)'})
    # titles up 600 (room for the 3rd stacked shelf in 2-2)
    add(t='move', h=['2D2FF8', '2D31B2', '2D3382'], d=[0, 600])
    # 2-2: 2nd row 4 dots + comb «4»
    for h in ('2D3197', '2D31F1', '2D31F8', '2D319E'):
        add(t='clone', h=h, base=[0, 0], to=[0, -112.5], tag='r2_' + h)
    add(t='clone', h='2D3304', base=[0, 0], to=[0, 507], tag='c4')
    add(t='mcset', h='c4', set={'FirstLine': '4', 'SecondLine': '(ф20)'})
    ys, ye = 463548.0, 465209.5
    segs = [[[x, ys], [x + 585.0, ye]] for x in (310729, 311029, 311329, 311629)]
    add(t='combsegs', h='c4', segs=segs, start=[312214.0, ye], end=[311314.0, ye])
    # 3-3: bottom dop 3 dots, comb «3» stacked under the pos-1 comb, dims down 600
    for dxx in (-600, -300):
        add(t='clone', h='2D34BF', base=[0, 0], to=[dxx, 0], tag='b3_%d' % -dxx)
    add(t='erase', h=['2D34C6'])
    add(t='clone', h='2D3386', base=[0, 0], to=[0, -507], tag='c3')
    add(t='mcset', h='c3', set={'FirstLine': '3', 'SecondLine': '(ф20)'})
    segs = [[[x, 462532.5], [x + 413.0, 461653.0]] for x in (315879, 316179, 316479)]
    segs.append(segs[-1])
    add(t='combsegs', h='c3', segs=segs)
    D = json.load(open(os.path.join(S, 'py', 'dims33.json')))
    for h, (p1, p2, dl) in D.items():
        add(t='dimpts', h=h, p1=p1, p2=p2, dl=[dl[0], dl[1] - 600])
    return ops


if __name__ == '__main__':
    k = int(sys.argv[1])
    ops = build4() if k == 3 else build5()
    json.dump(ops, open(os.path.join(S, 'ops', 'b%d.json' % k), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print(len(ops), 'ops')
    if '--run' in sys.argv:
        r, lg, errs = run(ops, 'b%d' % k)
        print(r[:200]); print('\n'.join(errs[:30]))
