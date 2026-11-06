# generate sheets (by number) + stamp
import sys, json, prep, b4rig, stamp2, gx
marks = json.load(open(prep.LIRA + '/marks.json', encoding='utf-8'))
want = sys.argv[1:]
for M, p in prep.build(marks):
    if want and p['no'] not in want: continue
    gx.run([dict(t='eraseregion', win=[p['SX'] - 50, p['SY'] - 50, p['SX'] + 31550, p['SY'] + 14900])], 'er')
    log = b4rig.run(M, p)
    st = stamp2.stamp(p)
    errs = [l for l in log + st.splitlines() if 'ERR' in l]
    print(p['no'], M['mark'], p['suffix'], 'ERR' if errs else 'ok', errs[:3], flush=True)
