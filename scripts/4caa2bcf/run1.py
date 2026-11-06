import gx, sys, json, rgen, rfac, beams
mark, k = sys.argv[1], int(sys.argv[2])
B = beams.BEAMS[mark]
SX = 172179.0 + 31500 * k
P = 'R%d:' % k
if '--import' in sys.argv:
    hs = rgen.sheet_handles()
    out = gx.run([dict(t='import', file=gx.S + r'\an\a61.dwg', h=hs, base=list(rgen.AN0), to=[SX, rgen.FY], pre=P)], 'imp%d' % k)
    print('import', [l for l in out.splitlines() if 'import' in l or 'ERR' in l][:3])
s = rgen.Sheet(SX, P)
rfac.facade(s, B, B['parts'][int(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[3].isdigit() else 0])
out = gx.run(s.ops + [dict(t='save')], 'f%d' % k)
print([l for l in out.splitlines() if 'ERR' in l or 'done' in l][:20])
