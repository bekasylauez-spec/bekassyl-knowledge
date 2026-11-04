import re,sys,math
fn=sys.argv[1]
lines=open(fn,encoding='utf-8-sig').read().splitlines()
tables=[];cur=None
for l in lines:
    if l.startswith('TABLE'):
        cur={'hdr':l,'rows':[]};tables.append(cur)
    elif l.strip().startswith('R') and cur is not None:
        m=re.match(r'\s*R(\d+) h=[\d.]+ \| (.*)\|\s*$',l)
        if m:
            cells=[c.strip() for c in m.group(2).split(' | ')]
            cur['rows'].append(cells)
def val(c):
    c=re.sub(r'\{F:.*\}','',c).strip()
    try: return float(c)
    except: return None
def raw(c): return re.sub(r'\{F:.*\}','',c).strip()
kgm=lambda d: d*d*math.pi/4*0.00785
specs=[]
for t in tables:
    if 'Спецификация' not in t['hdr']: continue
    name=None;tot=None;rows=[];conc=None
    for r in t['rows']:
        if len(r)<13: continue
        if raw(r[2]).startswith(('Ригель','Стена')) : name=raw(r[2]);tot=val(r[12]);continue
        if 'бетона' in r[2]: conc=r[12];continue
        try: d=float(raw(r[3]))
        except: continue
        L=raw(r[9]);q=val(r[10]);u=val(r[11]);m=val(r[12])
        rows.append((raw(r[0]),d,raw(r[4])+raw(r[5]),L,q,u,m,r[10],r[12]))
    if name is None: continue
    print('=====',name,'итог',tot,'бетон',conc, t['hdr'][:40])
    s=0;bydia={}
    for p,d,cl,L,q,u,m,qf,mf in rows:
        try:
            Lm=float(L)/1000
        except: Lm=1.0 if 'пог' in L else None
        uc=kgm(d)*Lm if Lm is not None else None
        mc=(uc*q) if (uc is not None and q is not None) else None
        flag=''
        if mc is not None and m is not None and abs(mc-m)>max(1,0.005*abs(mc)): flag='  <<< '
        if uc is not None and u is not None and abs(round(uc,2)-u)>0.011: flag+=' UNIT'
        print(f'  {p:5} d{d:.0f} {cl:6} L={L:8} q={q} u={u} (calc {uc if uc is None else round(uc,3)}) m={m} calc={None if mc is None else round(mc,2)}{flag}  |q:{qf[:40]} ')
        s+= m or 0
        k=(cl.replace('A','А').replace(' ',''),int(d)); bydia[k]=bydia.get(k,0)+(m or 0)
    print('  sum rows',round(s,2),'vs',tot, '<<<' if tot and abs(s-tot)>1 else '')
    print('  by dia',{k:round(v,2) for k,v in sorted(bydia.items())})
for t in tables:
    if 'Ведомость расхода' in t['hdr']:
        for r in t['rows']:
            if r and ('Ригель' in r[0] or 'Стена' in r[0]):
                hdr=[x for x in t['rows'][5]]
                print('VED',raw(r[0]),[ (raw(h),raw(c)) for h,c in zip(hdr[1:],r[1:])])
                for c in r[1:]:
                    mm=re.search(r'\{F:(.*)\}',c)
                    if mm: print('     F:',mm.group(1)[:200].replace('Table(%<\_ObjId ',''))
