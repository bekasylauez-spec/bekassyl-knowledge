# A4x3 rigel sheet -> A3 (analog «Ресторан 6.6»): A3 SPDS frame from «Шаблон для Кж.dwg» (9ABEA, 1:50),
# elevation/section/Узел stay left, right column = Ведомость деталей, Спецификация, Ведомость стали, notes, stamp.
import os, gx
TPL = r'C:\Users\Admin\AppData\Local\Temp\claude\210ab68cad67e8c1\9a1000cd-e0d9-42b2-b432-f6f3db0e7099\scratchpad\an\tpl.dwg'
FRAME_H, FRAME_BASE = '9ABEA', [282859.0, 249893.0]
W = 21000.0
SKETCH = ['40648A', '40648B', '40648C', '40648D', '406493', '406499', '4064A2', '4064A3', '4064A4', '4064A6', '4064A7',
          '4064A8', '4064AA', '4064AB', '4064B0', '4064B8', '4064B9']


def eligible(M, part):
    return M['E'] <= 6300 and len(part['secs']) == 1 and not part.get('spl') and len(M['specrows']) <= 1 and part.get('tables', True)


def ops(M, part):
    P, SX, SY = part['P'], part['SX'], part['SY']
    nd = len(M['specrows']) + (1 if M.get('npin') else 0)      # + Шп1 row
    T = lambda r: '%s:%s' % (P, r)
    spec_top = 12300.0
    spec_h = (9 + nd) * 400.0 + 400.0
    spec_bottom = spec_top - spec_h
    steel_top = spec_bottom - 300.0
    o = [dict(t='erase', h=[T('401330'), T('407C04')]),
         dict(t='import', file=TPL, h=[FRAME_H], base=FRAME_BASE, to=[SX, SY], pre=P + '_A3:'),
         dict(t='move', h=[T(r) for r in SKETCH] + part.get('pktags', []), d=[-10500.0, 1000.0]),
         dict(t='move', h=[T('406488')], d=[-10500.0, spec_top - 9660.0 - 400.0 * max(0, nd - 2)]),
         dict(t='move', h=[T('40443D')], d=[-10500.0, 0.0]),
         dict(t='move', h=[T('4064CF')], d=[20750.0 - 21992.0, steel_top - 3330.0])]
    return o
