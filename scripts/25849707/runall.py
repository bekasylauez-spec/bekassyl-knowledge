# all marks in order -> slots/sheet numbers 6.1 ... ; args: [names...] to (re)build only those
import json, mk, plan, sys, time, traceback, gx
M = json.load(open('w/marks2.json', encoding='utf-8'))
plan_ = []; k = 0
for m in M:
    F = plan.build_F(m, m['name']); n = len(plan.fragments(F))
    plan_.append((m, k, n)); k += n
only = [a for a in sys.argv[1:] if a.startswith('Рм')]
start = [int(a[7:]) for a in sys.argv[1:] if a.startswith('--from=')]
log = open('runall.log', 'a', encoding='utf-8')
W = lambda s: (log.write(s + '\n'), log.flush())
for idx, (m, k0, n) in enumerate(plan_):
    if only and m['name'] not in only: continue
    if start and idx + 1 < start[0]: continue
    t = time.time()
    for attempt in range(2):
        try:
            nn, errs = mk.run_mark(m, k0, k0 + 1, m['name'], len(m['locs']), log=W)
            W('%s done %d sheets slot %d..%d errs %d %.0fs %s' % (m['name'], nn, k0, k0 + nn - 1, len(errs), time.time() - t, errs[:5]))
            break
        except Exception:
            W('%s FAIL(%d) %s' % (m['name'], attempt, traceback.format_exc()[-800:]))
            W('restart %s' % (gx.restart_acad()[0],))
W('ALL DONE')
