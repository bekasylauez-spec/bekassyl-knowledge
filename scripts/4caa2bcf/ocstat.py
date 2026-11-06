import re, json, os, collections, sys
m=json.load(open(os.environ['TEMP']+'/b2_map.json',encoding='utf-8-sig')); inv={v:k for k,v in m.items()}
t=open('w/oc_all.txt',encoding='utf-8').read().splitlines()
sh=None; c=collections.Counter(); ex=collections.defaultdict(list)
def strip(s): return re.sub(r'_\d+$','_#',re.sub(r'^(R\d+|ST\d+_\d+):','',re.sub(r'(DOPN|DOP|BR|CH\d_)\d+.*$',r'\1#',s)))
for l in t:
    if l.startswith('=='): sh=l.split()[1]; continue
    mm=re.match(r'\s+(\S+)\s+"([^"]*)"\s+<>\s+(\S*)\s*@\((\-?\d+), (\-?\d+)\)',l)
    if not mm: continue
    a=mm.group(2).split('#')[-1] if '#' in mm.group(2) else ''
    b=mm.group(3).split('#')[-1]
    ta=strip(inv.get(a,mm.group(2)[:8])); tb=strip(inv.get(b,mm.group(3)[:8]))
    tb=re.sub(r'^X\d+_ST\d+_\d+_','S:',tb); ta=re.sub(r'^X\d+_ST\d+_\d+_','S:',ta)
    k=(mm.group(1),ta,tb); c[k]+=1; ex[k].append((sh,mm.group(4),mm.group(5)))
for k,v in c.most_common(int(sys.argv[1]) if len(sys.argv)>1 else 40): print(v,k,ex[k][:2])
