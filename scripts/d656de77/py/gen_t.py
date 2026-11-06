# spec + steel tables of rigel sheets 6.1-6.5 (formulas kept as formulas)
#   python gen_t.py <k> [--run]
import sys, os, re
from common import *

TB = {0: ('2CA93D', '2CAA2A'), 1: ('2CD66C', '2CD759'), 2: ('2CE5D2', '2CE6BF'), 3: ('2D1A54', '2D1B04'), 4: ('2D2745', '2D2832')}
# items after X1/Ск1: (pos, D, J or None for пог.м., count formula or None = keep existing pos-1 formula)
H1 = ('Н1', 20, 200, '3*4*2')
ITEMS = {
    0: [('1', 20, None, None), ('2*', 20, 2765, '2*2'), ('3', 20, 4790, '2*2'), H1],
    1: [('1', 20, None, None), ('2*', 20, 3295, '2*1'), ('3', 20, 3190, '2*2'), H1],
    2: [('1', 20, None, None), ('2*', 20, 2365, '3*2'), ('3', 20, 3940, '3*2'), H1],
    3: [('1', 20, None, None), ('2*', 20, 3600, '3*1')],
    4: [('1', 20, None, None), ('2', 20, 4370, '3*1'), ('3*', 20, 3260, '3*1'), ('4', 20, 3020, '4*1')],
}


def tform(h):
    gx.run([dict(t='tform', h=h)], 'tf')
    F = {}
    for l in gx.log().splitlines():
        if l.startswith('F '):
            a = l.split('\t'); r, c = map(int, a[0][2:].split(',')); F[(r, c)] = a[1].strip()
    return F


def strip(f): return f[1:-1] if f.startswith('(') and f.endswith(')') else f


def build(k):
    hs, hv = TB[k]; items = ITEMS[k]
    F = tform(hs)
    bet = [r for (r, c), f in F.items() if c == 12 and '0.45*' in f][0]
    mat = bet - 1
    slots = mat - 3; need = 2 + len(items); ins = max(0, need - slots)
    ops = []; add = lambda **kw: ops.append(kw)
    if ins: add(t='trows', h=hs, mode='ins', at=mat, **{'from': mat - 1, 'n': ins})
    bet += ins; last = 3 + need - 1
    texts = []; nums = []; forms = []
    for i, (pos, d, j, kf) in enumerate(items):
        r = 5 + i; R = r + 1
        texts += [[r, 0, pos], [r, 1, 'ГОСТ 34028-2016'], [r, 2, '%%C'], [r, 4, 'A'], [r, 5, '500С'], [r, 8, 'L=']]
        nums.append([r, 3, d, '%lu2%pr0'])
        if j is None:
            texts.append([r, 9, 'пог.м.'])
            forms += [[r, 10, strip(F[(5, 10)]), '%lu2%pr2'], [r, 11, 'D%d*D%d*3.1415926/4*0.00785*1' % (R, R), '%lu2%pr2']]
        else:
            nums.append([r, 9, j, '%lu2%pr0'])
            forms += [[r, 10, kf, '%lu2%pr0'], [r, 11, 'D%d*D%d*3.1415926/4*0.00785*J%d/1000' % (R, R, R), '%lu2%pr2']]
        forms.append([r, 12, 'L%d*K%d' % (R, R), '%lu2%pr2'])
    for r in range(5 + len(items), mat + ins):                       # spare rows: empty
        texts += [[r, c, ''] for c in range(13)]
    for r in (3, 4):
        for c in (10, 11, 12): forms.append([r, c, strip(F[(r, c)]), '%lu2%pr0' if c == 10 else '%lu2%pr2'])
    forms.append([2, 12, 'Sum(M4:M%d)' % (last + 1), '%lu2%pr2'])
    forms.append([bet, 12, strip(F[(bet - ins, 12)]), '%lu2%pr2'])
    add(t='tset', h=hs, cells=texts)
    for r in range(6, 5 + len(items)): add(t='trowcopy', h=hs, src=5, dst=r)
    add(t='tnum', h=hs, cells=nums)
    add(t='theight', h=hs, rows=[[r, 400] for r in range(2, bet + 1)])
    # all formulas of the table in ONE call, top->bottom (separate calls / later row ops wipe rows 3-4)
    add(t='tformula', h=hs, cells=sorted(forms, key=lambda c: (c[0], c[1])))
    # steel table
    add(t='tset', h=hv, cells=[[6, 6, '---']])
    T = '{T:%s}' % hs
    add(t='tformula', h=hv, cells=[[6, 1, 'Table(%s).M4' % T, '%lu2%pr2'], [6, 2, 'Sum(B7:B7)', '%lu2%pr2'],
                                    [6, 4, 'Table(%s).M5' % T, '%lu2%pr2'],
                                    [6, 5, 'Table(%s).Evaluate(Sum(M6:M%d))' % (T, last + 1), '%lu2%pr2'],
                                    [6, 8, 'Sum(D7:H7)', '%lu2%pr2'], [6, 9, 'I7+C7', '%lu2%pr2']])
    return ops


if __name__ == '__main__':
    k = int(sys.argv[1]); ops = build(k)
    if '--run' in sys.argv:
        r, lg, errs = run(ops, 't%d' % k); print(r[:150], errs)
        hs, hv = TB[k]
        for h in (hs, hv):
            gx.run([dict(t='tdump', h=h)], 'td'); print(gx.log())
    else:
        import json; print(json.dumps(ops, ensure_ascii=False, indent=0)[:3000])
