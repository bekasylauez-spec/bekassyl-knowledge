import json, prep
marks = json.load(open(prep.LIRA + '/marks.json', encoding='utf-8'))
a3 = {p['no'] for M, p in prep.build(marks, first_no=5) if p.get('a3')}
jobs = []
for k in range(1, 75):
    no = '6.%d' % k; sx = 172179 + (k - 5) * 31500
    if no in a3: jobs.append(dict(n=no, x0=sx, y0=420000, x1=sx + 21000, y1=434850, sc=50, w=420, h=297, media='ISO_full_bleed_A3_(420.00_x_297.00_MM)'))
    else: jobs.append(dict(n=no, x0=sx, y0=420000, x1=sx + 31500, y1=434850, sc=50, w=630, h=297, media='ISO_full_bleed_A1_(841.00_x_594.00_MM)'))
json.dump(dict(ren=[['0', '6.1']], jobs=jobs), open('w/layfix.json', 'w', encoding='utf-8'), ensure_ascii=False)
print(len(jobs), sorted(a3, key=lambda s: int(s.split('.')[1])))
