import csv, collections, math, itertools, sys
D=r"C:\Users\Admin\AppData\Local\Temp\claude\a7137524bdaa49d0\c55bc92b-0511-4932-9c00-c1294111057c\scratchpad\mine\\"
def rd(n): return list(csv.DictReader(open(D+n,encoding='utf-8'),delimiter='\t'))
F=rd('frame.tsv'); 
print(len(F))
# materials/color
bymk=collections.defaultdict(set)
for f in F: bymk[f['mark']].add((f['mat'],f['r'],f['g'],f['b'],f['shin'],f['smooth']))
for k,v in sorted(bymk.items()): print(k,v)
print('badface', sum(int(f['badface']) for f in F), [ (f['id'],f['mark'],f['badface']) for f in F if int(f['badface'])>0][:10])
cols=collections.defaultdict(list)
for f in F:
    if f['mark'] in ('К1','К2','К3'): cols[(round(float(f['x0'])),round(float(f['y0'])))].append(f)
print('col positions',len(cols), 'multi', [(k,len(v)) for k,v in cols.items() if len(v)>1])
print('joined counts', collections.Counter(int(f['joined']) for f in F))
# first few rows
for f in F[:3]+[x for x in F if x['kind']=='C'][:3]: print({k:f[k] for k in ('id','mark','x0','y0','z0','x1','y1','z1','bx0','by0','bz0','bx1','by1','bz1','ext0','ext1')})
