# non-final parts of a split rigel: the specification / steel list / bar sketches belong to the last part only
import json, os, gx, prep
marks = json.load(open(os.path.join(prep.LIRA, 'marks.json'), encoding='utf-8'))
TAGS = ['406488', '4064CF', '4064A2', '4064A3', '4064A6', '4064B8', '40648A', '40648B', '40648C', '40648D', '406493', '406499',
        '4064A4', '4064A7', '4064A8', '4064AA', '4064AB', '4064B0', '4064B9']
for M, p in prep.build(marks):
    if p['tables']: continue
    out = gx.run([dict(t='erase', h=[p['P'] + ':' + t for t in TAGS])], 'nt' + p['P'])
    print(p['no'], M['mark'], [l for l in out.splitlines() if 'ERR' in l][:2])
