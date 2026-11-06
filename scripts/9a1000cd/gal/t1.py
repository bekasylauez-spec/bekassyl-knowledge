import sys, json, prep, b4rig
marks = json.load(open(prep.LIRA + '/marks.json', encoding='utf-8'))
want = sys.argv[1:]
sh = prep.build([m for m in marks if m['mark'] in want])
for M, p in sh:
    print(p['no'], M['mark'], p['P'], p['SX'], p['secpos'])
    for l in b4rig.run(M, p): print('  ', l)
