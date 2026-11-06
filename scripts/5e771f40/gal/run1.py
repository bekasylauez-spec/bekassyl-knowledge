import sys, json, os, prep, b4rig
marks = json.load(open(os.path.join(prep.LIRA, 'marks.json'), encoding='utf-8'))
sh = prep.build(marks)
want = [a for a in sys.argv[1:] if not a.startswith('--')]
for M, p in sh:
    if p['no'] in want or M['mark'] in want:
        print(p['no'], M['mark'], p['P'], p['SX'], p['secpos'])
        for l in b4rig.run(M, p, clone=('--noclone' not in sys.argv)): print('  ', l)
