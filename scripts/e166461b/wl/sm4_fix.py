# См-4 (5.14/5.15) corrections after comparing with the analog 4.13/4.14 (05.11 user: "қателер өте көп")
import sys, os, json; sys.path.insert(0, 'wl'); from common import *
from notes import notes
Y0 = 455939.0; X14, X15, X17, X11 = 1429800.0, 1489200.0, 1578300.0, 1281300.0
W = lambda X, x, y: [X + x, Y0 + y]
ops = []
# 1) vertical-elevation bar notes: shelf bar-to-bar, horizontal as in the analog (left target was dropped 300)
for h, idx, y in (('1B136C', 1, 31654), ('1B136A', 1, 19429), ('1B136B', 1, 25074), ('1B1368', 2, 35088)):
    N = {n['h']: n for n in notes(X15, Y0, 59400, 42000)} if not ops else N
    x = N[h]['pts'][idx][0]
    ops.append(dict(t='spmove', h=h, items=[[idx, X15 + x, Y0 + y]]))
ops.append(dict(t='spmove', h='197B1F', items=[[1, 1292439, 491292]]))
# 2) break polylines of piece B (it is a free wall end, not a cut)
R14 = listwin(X14, Y0, 59400, 42000, None); R15 = listwin(X15, Y0, 59400, 42000, None)
br = []
for R in (R14, R15):
    for r in R:
        if r['t'] == 'LWPOLYLINE' and r['lay'] == 'Размеры' and len(r['sp']) == 3 and r['x1'] - r['x0'] < 1500 and r['y1'] - r['y0'] > 3000 \
                and abs(r['sp'][0][0] - r['sp'][1][0]) < 300 and r['sp'][2][0] < r['sp'][1][0] - 400: br.append(r['h'])
ops.append(dict(t='erase', h=br))
# 3) dimension texts back to the analog places / inline
for h, x, y in (('1B134F', 12908, 7749), ('1B1418', 11249, 7155), ('1B143B', 12549, 7155), ('1B1409', 11658, 7749),
                ('1BB2C0', 15109, 7749), ('1BB2DC', 15809, 7749), ('1BB2CD', 14600, 6967), ('1BB2EB', 16620, 6967),
                ('1B15B8', 28705, 13123), ('1B153A', 28410, 17350)):
    ops.append(dict(t='dimtx', h=h, at=W(X15, x, y)))
ops += [dict(t='dimtx', h='1B1F91', at=W(X14, 41904, 14475)), dict(t='dimtx', h='1C6814', at=W(X17, 41904, 14475))]
# 4) horizontal elevation, piece B: middle notes to mid+700, right Ск to mid-300 (texts off the bars, no overlaps)
N = notes(X15, Y0, 59400, 42000)
for n in N:
    o = n['pts'][0]
    if abs(o[0] - 35830) < 5 and len(n['pts']) == 3:
        mid = (n['pts'][1][1] + n['pts'][2][1]) / 2; ops.append(dict(t='spmove', h=n['h'], items=[[0, X15 + o[0], Y0 + mid + 700]]))
    if 36200 < o[0] < 36400 and len(n['pts']) == 3 and n['l1'].startswith('Ск'):
        mid = (n['pts'][1][1] + n['pts'][2][1]) / 2; ops.append(dict(t='spmove', h=n['h'], items=[[0, X15 + o[0], Y0 + mid - 300]]))
# 5) plan 1-1, piece B: one note per level, texts left, origins right of their targets (no leader crosses a text)
ops += [dict(t='spmove', h='1BD124', items=[[0, X15 + 55500, Y0 + 27300]]),
        dict(t='spmove', h='1C78AE', items=[[0, X15 + 55950, Y0 + 28050], [1, X15 + 55750, Y0 + 25810], [2, X15 + 55850, Y0 + 25470]]),
        dict(t='spmove', h='1BD10F', items=[[0, X15 + 57127, Y0 + 28800]]),
        dict(t='spmove', h='1BD166', items=[[0, X15 + 57919, Y0 + 29550]]),
        dict(t='clone', h='1BD110', base=[0, 0], to=[0, 0], tag='S4CKR'),
        dict(t='spmove', h='S4CKR', items=[[0, X15 + 58410, Y0 + 30300], [1, 1547510.3, 481578.9]]),
        dict(t='erase', h=['1BD167'])]
# 6) plan titles lost on 5.8, 5.12, 5.15 (analog 4.8 / 4.12 / 4.14 have them): clone of the 5.14 title, set later per sheet
ops += [dict(t='clone', h='1B0E16', base=[1468195, 495135], to=[X15 + 51400, Y0 + 31100], tag='T515'),
        dict(t='settext', h='T515', s='{\LРазрез 1 - 1 (Армирование) М1:50}')]
# 7) 5.14 plan: piece B outline / hatch in the wall's highlight like piece A
ops.append(dict(t='eprops', src='1B0E15', h=['1B64F4'])); ops.append(dict(t='eprops', src='1B0E14', h=['1B64F3']))
ops.append(dict(t='save'))
print('breaks', len(br), 'ops', len(ops))
if '--run' in sys.argv:
    out = gx.run(ops, 'sm4fix'); print([l for l in out.splitlines() if 'ERR' in l or 'done' in l or 'rror' in l][-8:])
