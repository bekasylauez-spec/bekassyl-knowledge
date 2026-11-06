import json
N = 101
jobs = []
for k in range(1, N + 1):
    sx = 172179 + (k - 5) * 31500
    jobs.append(dict(n='6.%d' % k, x0=sx, y0=420000, x1=sx + 31500, y1=434850, sc=50, w=630, h=297, media='ISO_full_bleed_A1_(841.00_x_594.00_MM)'))
json.dump(dict(jobs=jobs), open('w/layfix3.json', 'w', encoding='utf-8'), ensure_ascii=False)
print(len(jobs), jobs[0]['x0'], jobs[-1]['x1'])
