import sys, json, os, prep, b4rig, subprocess
marks = json.load(open(os.path.join(prep.LIRA, 'marks.json'), encoding='utf-8'))
sh = prep.build(marks)
want = [a for a in sys.argv[1:] if not a.startswith('--')]
res = {}
for M, p in sh:
    if want and p['no'] not in want: continue
    try:
        log = b4rig.run(M, p)
        import fix
        n, out = fix.fix(p['no'], p['SX'], p['SY'], rounds=4)
        class R: pass
        r = R(); r.stdout = out
        tot = ['TOTAL %d' % n]
        errs = [l for l in log if 'ERR' in l]
        print(p['no'], M['mark'], tot, errs[:3], flush=True)
        if tot and tot[0] != 'TOTAL 0':
            print('\n'.join(l for l in r.stdout.splitlines() if l.startswith('  '))[:3000], flush=True)
    except Exception as ex:
        print(p['no'], M['mark'], 'EXC', ex, flush=True)
