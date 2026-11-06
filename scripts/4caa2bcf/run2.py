import gx, sys, json, rgen, rfac, rfac2, rsec, beams
mark, k, pi = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
B = dict(beams.BEAMS[mark]); B['mark'] = mark
part = B['parts'][pi]
SX = 172179.0 + 31500 * k; P = 'R%d:' % k
if '--import' in sys.argv:
    out = gx.run([dict(t='import', file=gx.S + r'\an\a61.dwg', h=rgen.sheet_handles(), base=list(rgen.AN0), to=[SX, rgen.FY], pre=P)], 'imp%d' % k)
    print('import', [l for l in out.splitlines() if 'import' in l or 'ERR' in l][:3])
s = rgen.Sheet(SX, P)
g = rfac.facade(s, B, part)
marks = [(u, sc['word']) for sc in B['secs'] for u in sc['at']]
rfac2.facade2(s, B, part, marks)
out = gx.run(s.ops + [dict(t='save')], 'f%d' % k)
print('facade', [l for l in out.splitlines() if 'ERR' in l or 'done' in l][:20])
# sections present on this sheet
u0, u1 = g['u0'], g['u1']
secs = [sc for sc in B['secs'] if any(u0 <= u <= u1 for u in sc['at'])]
secs.sort(key=lambda sc: sc['word'])
types = {}
for h, r in rgen.INV.items(): types[h] = r['t']
n = len(secs); W = (B['b'] + 453 + 1050) * rsec.SC + 300
xc0 = SX + 16000 - (n - 1) * W / 2.0
for i, sc in enumerate(secs):
    Pst = 'ST%d%s:' % (k, sc['word'])
    OX, OY = 2600000 + 3000 * i + 20000 * k, 300000
    ops, tags, base = rsec.build_stage(B, sc, OX, OY, Pst)
    ty = {}
    for t_ in tags:
        h0 = t_.split(':', 1)[1] if ':' in t_ else t_
        ty[t_] = types.get(h0, 'INSERT' if t_.endswith(tuple('D%d' % j for j in range(9))) else ('SPDSNOTEMULTILAYER' if t_.endswith('ML') else ('SPDSNOTECOMB' if t_.endswith(('CDT', 'CDB')) else '')))
    out = gx.run(ops, 'st%d%s' % (k, sc['word']))
    print('stage', sc['word'], [l for l in out.splitlines() if 'ERR' in l or 'done' in l][:12])
    s2 = rgen.Sheet(SX, P)
    rsec.place(s2, tags, base, [xc0 + W * i, rgen.FY + 5000], ty)
    out = gx.run(s2.ops + [dict(t='save')], 'pl%d%s' % (k, sc['word']))
    print('place', sc['word'], [l for l in out.splitlines() if 'ERR' in l or 'done' in l][:12])
# tables, details, stamp
import rtab
s3 = rgen.Sheet(SX, P)
q = rtab.quantities(B, s.NH)
top, bot = s.splices
ops = [o for o in rtab.table_ops(s3, B, q, len(top) + len(bot)) if isinstance(o, dict)]
ops += rtab.detail_texts(s3, B, q)
nl = len(beams.BEAMS[mark].get('lines', []))
ops += rtab.stamp_ops(s3, B, part['no'], 'Ригель ' + mark, B.get('note4', '')) + rtab.static_fixes(s3)
out = gx.run(ops, 'tb%d' % k)
print('tables', [l for l in out.splitlines() if 'ERR' in l or 'done' in l][:12])
m = gx.tagmap()
rH = 6 + len(B.get('dop', []))
out = gx.run([rtab.steel_ops(P + rgen.SPDS['steel'], m[P + rgen.SPDS['spec']], rH), dict(t='theight', h=P + rgen.SPDS['spec'], rows=[[rH + 1, 400], [rH + 3, 400]]), dict(t='tdump', h=P + rgen.SPDS['spec']), dict(t='tdump', h=P + rgen.SPDS['steel']), dict(t='save')], 'stl%d' % k)
print('steel', [l for l in out.splitlines() if 'ERR' in l or 'done' in l][:12])
print('\n'.join(l for l in gx.log().splitlines() if l.startswith('R')))
