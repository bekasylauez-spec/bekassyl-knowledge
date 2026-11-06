# split w/layfix.json into 4 parts w/lay2_p0..3.json (+ w/lay2_all.json).
# fin2 has one paper layout "0": every part renames it to its own first job (so PLOTL never plots an unconfigured layout).
# argv[1] (optional) = file with other existing layout names to delete.
import json, sys
L = json.load(open('w/layfix.json', encoding='utf-8'))
names = []
if len(sys.argv) > 1:
    names = [l.strip() for l in open(sys.argv[1], encoding='utf-8') if l.strip() and l.strip() not in ('Model', '0')]
jobs = L['jobs']
json.dump(dict(ren=[['0', jobs[0]['n']]], jobs=jobs, **({'del': names} if names else {})), open('w/lay2_all.json', 'w', encoding='utf-8'), ensure_ascii=False)
q = (len(jobs) + 3) // 4
for k in range(4):
    part = jobs[k * q:(k + 1) * q]
    d = dict(ren=[['0', part[0]['n']]], jobs=part, **({'del': names} if names else {}))
    json.dump(d, open('w/lay2_p%d.json' % k, 'w', encoding='utf-8'), ensure_ascii=False)
    print(k, len(part), part[0]['n'], part[-1]['n'])
print('del', len(names))
