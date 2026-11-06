# replace the Galaxy stamp (TUNAY STROY block) by the BDM scheme stamp «Штамп№1» (x0.5 for the 1:50 sheets)
import sys, json, os, gx, prep
SRC = os.path.join(gx.S, 'w', 'scheme4.dwg'); H = '5BC8DC'; BASE = [469717.3304096889, -1801160.128777295]
marks = json.load(open(os.path.join(prep.LIRA, 'marks.json'), encoding='utf-8'))
sh = prep.build(marks)
want = [a for a in sys.argv[1:]]
for M, p in sh:
    if want and p['no'] not in want: continue
    P = p['P']; cx, cy = p['SX'] + 31250, p['SY'] + 250
    tag = P + '_STAMP'
    ops = [dict(t='import', file=SRC, h=[H], base=BASE, to=[cx, cy], pre=P + '_ST:'),
           dict(t='scalegrp', h=[P + '_ST:' + H], s=0.5, base=[cx, cy]),
           dict(t='erase', h=[P + ':40443F']),
           dict(t='moveto', h=P + ':404440', idx=0, to=[cx - 1375, cy + 1000]),
           dict(t='moveto', h=P + ':404442', idx=0, to=[cx - 4250, cy + 375])]
    out = gx.run(ops, 'st' + P)
    print(p['no'], [l for l in out.splitlines() if 'ERR' in l or 'import' in l][:3])
