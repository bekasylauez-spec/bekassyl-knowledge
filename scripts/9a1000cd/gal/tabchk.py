import json, prep, ezdxf, collections, re
marks = json.load(open(prep.LIRA + '/marks.json', encoding='utf-8'))
sh=json.load(open('w/sh_all.json'))
doc=ezdxf.readfile('w/live_all.dxf'); msp=doc.modelspace()
txt=collections.defaultdict(list); low={}
for e in msp.query('ACAD_TABLE'):
    ins=e.dxf.insert
    n=next((n for n,(x0,y0,x1,y1) in sh.items() if x0<=ins.x<=x1 and y0<=ins.y<=y1),None)
    if not n: continue
    s=[]; ys=[]
    for v in e.virtual_entities():
        if v.dxftype()=='MTEXT': s.append(v.plain_text())
        elif v.dxftype()=='TEXT': s.append(v.dxf.text)
        elif v.dxftype()=='LINE': ys += [v.dxf.start.y, v.dxf.end.y]
    txt[n].append(' | '.join(s)); low[n]=min(low.get(n,1e18), min(ys) if ys else 1e18)
T={}
for l in open('w/geo_all.txt',encoding='utf-8-sig'):
    f=l.rstrip('\n').split('|')
    if f[0]!='T': continue
    x,y=float(f[3]),float(f[4])
    for n,(x0,y0,x1,y1) in sh.items():
        if x0<=x<=x1 and y0<=y<=y1: T.setdefault(n,[]).append((y-y0,f[2],f[-1]))
def tot(tok,pos):
    i=tok.index(pos); j=tok.index('L=',i); return float(tok[j+4])
bad=[]; nspec=0; npin=0
for M,p in prep.build(marks, first_no=5):
    n=p['no']; tabs=txt[n]; tt=T.get(n,[])
    if any('###' in x or '%<' in x for x in tabs): bad.append((n,'#### / field'))
    has=any(s=='Х1;Шп1' for y,t,s in tt)
    if has!=bool(M.get('npin')): bad.append((n,'Шп1 section mismatch'))
    for y,t,s in tt:
        m=re.fullmatch(r'(\d+)х\d+(=\d+)?',s)
        if t=='DIMENSION' and m and int(m.group(1)) not in (50,100,200) and y>9000: bad.append((n,'step',s))
    sp=[x for x in tabs if x.startswith('Спецификация')]
    if not sp: continue
    nspec+=1
    tok=[x.strip() for x in sp[0].split('|')]
    vr=[x for x in tabs if x.startswith('Ведомость расхода')]; tv=[x.strip() for x in vr[0].split('|')]
    x1=tot(tok,'Х1*'); s1=tot(tok,'Шп1*') if 'Шп1*' in tok else 0
    if M.get('npin') and not s1: bad.append((n,'no Шп1 in spec'))
    npin+= bool(s1)
    k=next(i for i,x in enumerate(tv) if x.startswith('Ригель')); a240=float(tv[k+1])
    if abs(a240-x1-s1)>0.06: bad.append((n,'A240',x1,s1,a240))
    if low[n]-sh[n][1] < 240: bad.append((n,'table below frame', low[n]-sh[n][1]))
print('spec sheets',nspec,'with Шп1',npin,'marks npin',sum(1 for m in marks if m.get('npin')),'nbad',sum(m.get('nbad',0) for m in marks))
print('BAD',bad)
