import gx, subprocess, sys, sec1
sec1.build()
ops = sec1.ops
groups = {'A': [o for o in ops if o['t'] in ('plset', 'insat')], 'B': [o for o in ops if o['t'] == 'dyn'],
          'C': [o for o in ops if o['t'] in ('dimpts', 'move', 'mcset') and 'SecondLine' not in str(o.get('set', ''))],
          'D': [o for o in ops if o['t'] in ('erase', 'clone', 'levelval')],
          'E': [o for o in ops if o['t'] == 'combsegs'], 'F': [o for o in ops if o['t'] in ('spmove',) or 'SecondLine' in str(o.get('set', ''))]}
for k in sys.argv[1]:
    out = gx.run(groups[k] + [dict(t='wblock', file=gx.S + r'\w\snap.dwg')], 'b' + k)
    r = subprocess.run(['python', '-X', 'utf8', gx.S + r'\an\ptest.py'], capture_output=True, text=True)
    print(k, len(groups[k]), [l for l in out.splitlines() if 'ERR' in l][:3], r.stdout.strip())
    if 'FAIL' in r.stdout: break
