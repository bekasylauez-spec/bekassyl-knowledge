# build LAYFIX json (renames + jobs from plotc.json) and PLOTL win jobs per file
import json, os, sys
C = r'C:\Users\Admin\AppData\Local\Temp\claude\D---------\760c999f-c28c-44e9-ba81-9cb2aa467e81\scratchpad\w\chk'
src = {k: 'pM_' + k for k in ['g11','g12','sch','fnd','vyp','col','wal','rig','p71','p72','st8','rmp']}
ren = {'g11': [['1.5', '1.1']], 'sch': [[str(i), '2.%d' % i] for i in range(1, 11)], 'fnd': [['3.2.', '3.2']]}
for k, folder in src.items():
    J = json.load(open(os.path.join(C, folder, 'plotc.json'), encoding='utf-8-sig'))
    jobs = [{'n': j['n'], 'x0': j['x0'], 'y0': j['y0'], 'x1': j['x1'], 'y1': j['y1'], 'sc': j['sc'], 'w': j['w'], 'h': j['h'], 'media': j['media']} for j in J]
    json.dump({'ren': ren.get(k, []), 'jobs': jobs}, open(os.path.join(C, 'lay_%s.json' % k), 'w', encoding='utf-8'), ensure_ascii=False)
    od = os.path.join(C, 'pL_' + k); os.makedirs(od, exist_ok=True)
    pl = [{'layout': j['n'], 'out': os.path.join(od, j['n'] + '.pdf'), 'win': [0, 0, j['w'], j['h']], 'wmedia': j['media']} for j in J]
    json.dump(pl, open(os.path.join(od, 'plotl.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    # plotc.json copy for merge.py (w/h/out)
    json.dump([dict(j, out=os.path.join(od, j['n'] + '.pdf')) for j in J], open(os.path.join(od, 'plotc.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    print(k, len(jobs), 'jobs', ren.get(k, []))
