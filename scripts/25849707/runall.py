# all marks in order -> slots/sheet numbers 6.1 ... ; args: [names...] to (re)build only those; --from N
import json, mk, plan, sys, time, traceback
M = json.load(open('w/marks2.json', encoding='utf-8'))
plan_ = []; k = 0
for m in M:
    F = plan.build_F(m, m['name']); n = len(plan.fragments(F))
    plan_.append((m, k, n)); k += n
only = [a for a in sys.argv[1:] if a.startswith('Рм')]
log = open('runall.log', 'a', encoding='utf-8')
for m, k0, n in plan_:
    if only and m['name'] not in only: continue
    t = time.time()
    try:
        nn, errs = mk.run_mark(m, k0, k0 + 1, m['name'], len(m['locs']), log=lambda s: (log.write(s + '\n'), log.flush()))
        log.write('%s done %d sheets slot %d..%d errs %d %.0fs %s\n' % (m['name'], nn, k0, k0 + nn - 1, len(errs), time.time() - t, errs[:5])); log.flush()
    except Exception as ex:
        log.write('%s FAIL %s\n' % (m['name'], traceback.format_exc())); log.flush()
