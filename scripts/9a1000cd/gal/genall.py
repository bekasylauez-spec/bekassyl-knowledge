import sys, json, prep, b4rig, stamp2, gx, fix, time
marks = json.load(open(prep.LIRA + '/marks.json', encoding='utf-8'))
want = sys.argv[1:]
k = 0
for M, p in prep.build(marks):
    if want and p['no'] not in want: continue
    t0 = time.time()
    try:
        gx.run([dict(t='eraseregion', win=[p['SX'] - 50, p['SY'] - 50, p['SX'] + 31550, p['SY'] + 14900])], 'er')
        log = b4rig.run(M, p)
        st = stamp2.stamp(p)
        errs = [l for l in log + st.splitlines() if 'ERR' in l]
        n, out = fix.fix(p['no'], p['SX'], p['SY'], rounds=4)
        print(p['no'], M['mark'], p['suffix'], 'TOTAL', n, 'ERR' if errs else '', errs[:2], '%ds' % (time.time() - t0), flush=True)
        if n: print('\n'.join(l for l in out.splitlines() if l.startswith('  '))[:800], flush=True)
    except Exception as ex:
        print(p['no'], M['mark'], 'EXC', ex, flush=True)
    k += 1
    if k % 10 == 0: gx.run([dict(t='save')], 'sv')
gx.run([dict(t='save')], 'sv')
print('ALL DONE', flush=True)
