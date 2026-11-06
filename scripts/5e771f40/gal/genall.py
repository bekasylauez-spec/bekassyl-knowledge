# generate rigel sheets; AutoCAD hang -> kill, reopen, redo the sheet (saved after every sheet)
import sys, os, json, prep, b4rig, stamp2, gx, fix, time
marks = json.load(open(prep.LIRA + '/marks.json', encoding='utf-8'))
FIRST = 5
want = sys.argv[1:]
for M, p in prep.build(marks, first_no=FIRST):
    if want and p['no'] not in want: continue
    for attempt in range(3):
        t0 = time.time()
        try:
            gx.run([dict(t='eraseregion', win=[p['SX'] - 50, p['SY'] - 50, p['SX'] + 31550, p['SY'] + 14900])], 'er')
            log = b4rig.run(M, p)
            st = stamp2.stamp(p)
            errs = [l for l in log + st.splitlines() if 'ERR' in l]
            n, out = (fix.fix(p['no'], p['SX'], p['SY'], rounds=4) if not os.environ.get('NOFIX') else (-1, ''))
            gx.run([dict(t='save')], 'sv', wait=200)
            print(p['no'], M['mark'], p['suffix'], 'TOTAL', n, 'ERR' if errs else '', errs[:2], '%ds' % (time.time() - t0), flush=True)
            if n: print('\n'.join(l for l in out.splitlines() if l.startswith('  '))[:800], flush=True)
            break
        except gx.Hang as h:
            print(p['no'], 'HANG in', h, '-> relaunch:', gx.relaunch().strip().replace('\n', ' | '), flush=True)
        except Exception as ex:
            print(p['no'], M['mark'], 'EXC', ex, flush=True); break
print('ALL DONE', flush=True)
