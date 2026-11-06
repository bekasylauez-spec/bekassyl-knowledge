import sys, json, fix, gx, prep, time
marks = json.load(open(prep.LIRA + '/marks.json', encoding='utf-8'))
want = sys.argv[1:]
for M, p in prep.build(marks, first_no=5):
    if p['no'] not in want: continue
    t0 = time.time()
    try:
        n, out = fix.fix(p['no'], p['SX'], p['SY'], rounds=4, width=20750 if p.get('a3') else 31250)
        gx.run([dict(t='save')], 'sv', wait=200)
    except gx.Hang as h:
        print(p['no'], 'HANG', gx.relaunch().strip().replace('\n', ' | '), flush=True); continue
    print(p['no'], 'TOTAL', n, '%ds' % (time.time() - t0), flush=True)
    if n: print('\n'.join(l for l in out.splitlines() if l.startswith('  '))[:800], flush=True)
print('ALL DONE', flush=True)
