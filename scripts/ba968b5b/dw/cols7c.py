# -*- coding: utf-8 -*-
"""cols7b созуынан кейін X бойымен созылған элементтердің (Рм-1 ригель контуры т.б.) жылжыған төбелерін қайтару."""
import ab, json, sys, km2_sec as K
sys.stdout.reconfigure(encoding='utf-8')
S = json.load(open('w/sheets2.json'))
def run(s, dry=False):
    old = {e['h']: e for e in json.load(open('w/l%s.json' % s, encoding='cp1251'))}
    ops = []; hs = set()
    for e in K.listwin(S[s]):
        o = old.get(e['h'])
        if not o or e['t'] not in ('LINE', 'LWPOLYLINE') or len(o['pts']) != len(e['pts']): continue
        a = o['e']; w, h = a[2]-a[0], a[3]-a[1]
        if not (w > 1000 and w > 3 * h): continue
        for i, (p0, p1) in enumerate(zip(o['pts'], e['pts'])):
            if abs(p1[1]-p0[1]) > 1:
                ops.append({'t': 'movept', 'h': e['h'], 'idx': i, 'd': [p0[0]-p1[0], p0[1]-p1[1]]}); hs.add((e['h'], e['lay']))
    print(s, len(ops), len(hs), sorted(set(l for _, l in hs)))
    if ops and not dry: print(ab.run(ops + [{'t': 'save'}], 'c7c_' + s, 900)[-60:])
for s in [a for a in sys.argv[1:] if not a.startswith('--')]: run(s, dry=('--dry' in sys.argv))
