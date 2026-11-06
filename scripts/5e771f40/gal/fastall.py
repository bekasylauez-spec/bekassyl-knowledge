import sys, json, os, time, prep, b4rig, gx
marks = json.load(open(os.path.join(prep.LIRA, 'marks.json'), encoding='utf-8'))
sh = prep.build(marks)
start = sys.argv[1] if len(sys.argv) > 1 else '6.1'
go = False; n = 0
for M, p in sh:
    if p['no'] == start: go = True
    if not go: continue
    t0 = time.time()
    try:
        log = b4rig.run(M, p)
        print(p['no'], M['mark'], round(time.time() - t0), [l for l in log if 'ERR' in l][:2], flush=True)
    except Exception as ex:
        print(p['no'], M['mark'], 'EXC', ex, flush=True)
    n += 1
    gx.run([dict(t='save')], 'sv')
gx.run([dict(t='save')], 'sv')
print('ALLDONE', flush=True)
