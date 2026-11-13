import io, collections, csv, re, sys
D = r"C:\Users\Admin\AppData\Local\Temp\claude\a7137524bdaa49d0\c55bc92b-0511-4932-9c00-c1294111057c\scratchpad\w\out" + "\\"
Pl = list(csv.DictReader(io.open(D + 'plates.tsv', encoding='utf-8'), delimiter='\t'))
byid = collections.defaultdict(list)
for r in Pl: byid[r['id']].append(r)
KW = ('гусет', 'фасонка', 'жота пластинасы', 'косынка', 'кронштейн', 'тартпа', 'тірек листі', 'оголовок', 'ребро')
grp = collections.defaultdict(list)
for pid, l in byid.items():
    n = re.sub(r' - [^ ]+$', '', l[0]['name'])
    if not any(k in n for k in KW): continue
    t = float(l[0]['t'])
    elems = set(x['contactElem'] for x in l)
    outs = sorted(set(round(float(x['outstand'])) for x in l))
    grp[n].append((pid, t, len(l), len(elems), outs, l[0]['loc']))
rows = []
for n, l in grp.items():
    l.sort(key=lambda x: (x[2], x[3]))
    pid, t, nrows, nel, outs, loc = l[0]
    rows.append((max(outs) / t, n, len(l), t, nrows, nel, outs, loc))
rows.sort(reverse=True)
o = io.open(D + 'plates_after.txt', 'w', encoding='utf-8')
for r in rows[:60]:
    o.write('%.1f | %s | plates %d | t %s | contact rows %d | supports %d | outstands %s\n' % (r[0], r[1][:70], r[2], r[3], r[4], r[5], r[6][:6]))
o.write('types with ratio > 15: %d\n' % sum(1 for r in rows if r[0] > 15))
o.close()
print('ok', len(rows))
