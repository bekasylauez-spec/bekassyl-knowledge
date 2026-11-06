# existing sheets: spec-table row heights + X1 sketch text (same as the patched generator)
import json, prep, gx
marks = json.load(open(prep.LIRA + '/marks.json', encoding='utf-8'))
for M, p in prep.build(marks, first_no=5):
    if not p['tables']: continue
    P = p['P']; nd = len(M['specrows'])
    ops = [dict(t='theight', h=P + ':406488', rows=[[r, 400] for r in range(6, 9 + nd)]),
           dict(t='move', h=[P + ':40648D'], d=[150, 0])]
    o = gx.run(ops, 'ft' + P)
    print(p['no'], M['mark'], nd, [l for l in o.splitlines() if 'ERR' in l][:2], flush=True)
gx.run([dict(t='save')], 'sv', wait=300)
