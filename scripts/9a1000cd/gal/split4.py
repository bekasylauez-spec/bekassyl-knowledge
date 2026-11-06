# split w/layfix.json into 4 parts: w/lay2_p0..3.json (+ lay2_all.json); argv[1] = file with existing layout names (one per line)
import json, sys
L = json.load(open('w/layfix.json', encoding='utf-8'))
names = [l.strip() for l in open(sys.argv[1], encoding='utf-8') if l.strip() and l.strip() not in ('Model', '0')]   # '0' is kept and renamed to 6.1 if len(sys.argv) > 1 else []
jobs = L['jobs']
allj = dict(L); allj['del'] = names
json.dump(allj, open('w/lay2_all.json', 'w', encoding='utf-8'), ensure_ascii=False)
q = (len(jobs) + 3) // 4
for k in range(4):
    d = dict(L); d['jobs'] = jobs[k * q:(k + 1) * q]; d['del'] = names
    json.dump(d, open('w/lay2_p%d.json' % k, 'w', encoding='utf-8'), ensure_ascii=False)
    print(k, len(d['jobs']), d['jobs'][0]['n'] if d['jobs'] else '-', d['jobs'][-1]['n'] if d['jobs'] else '-')
print('del', len(names))
