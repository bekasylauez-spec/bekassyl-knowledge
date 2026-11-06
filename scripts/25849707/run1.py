import json, mk, sys
M = json.load(open('w/marks2.json', encoding='utf-8'))
jobs = [(a.split('@')[0], int(a.split('@')[1]), int(a.split('@')[2])) for a in sys.argv[1:]]
for nm, k, no in jobs:
    m = [x for x in M if x['name'] == nm][0]
    n, errs = mk.run_mark(m, k, no, nm, len(m['locs']))
    print(nm, n, errs[:10])
