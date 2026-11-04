import re,sys
from collections import defaultdict
SP=r"C:\Users\Admin\AppData\Local\Temp\claude\D---------\4ae264b2-3d49-4a11-8864-2d6523e82a02\scratchpad"
KG={6:0.222,8:0.395,10:0.617,12:0.888,14:1.208,16:1.578,18:1.998,20:2.466,22:2.984,25:3.853,28:4.834,32:6.313}
def num(s):
    s=re.sub(r'\{F:.*?\}\s*$','',s).strip()
    s=re.sub(r'\{F:.*','',s).strip()
    try: return float(s.replace(',','.'))
    except: return None
def tables(f):
    T=[];cur=None
    for line in open(SP+r"\dxf\%s.tables.txt"%f,encoding='utf-8-sig'):
        if line.startswith('TABLE'):
            cur={'hdr':line.strip(),'rows':[]};T.append(cur)
        elif line.strip().startswith('R') and cur is not None:
            m=re.match(r'\s*R(\d+) h=\S+ \|(.*)\|\s*$',line.rstrip('\n'))
            if m: cur['rows'].append([c.strip() for c in m.group(2).split(' | ')])
    return T
for f in sys.argv[1:]:
  for t in tables(f):
    if 'Спецификация ААТ' not in t['hdr']: continue
    rows=t['rows']
    print('\n###',f,t['hdr'][:60], '|', rows[0][2] if len(rows[0])>2 else '', '| title total', rows[0][-1][:40] if rows[0] else '')
    bydia=defaultdict(float);s=0
    for r in rows:
        if len(r)<13: continue
        try: d=int(num(r[3]) or 0)
        except: d=0
        if not d: 
            if any('бетон' in c.lower() for c in r): print('  CONCRETE',r[2][:40],r[-1])
            continue
        L=r[9]; q=num(r[10]); um=num(r[11]); tot=num(r[12])
        Ln=num(L)
        if 'пог' in L:
            exp_um=KG.get(d); exp_tot=q*KG[d] if q else None
        else:
            exp_um=Ln*KG[d]/1000 if Ln else None; exp_tot=exp_um*q if (exp_um and q) else None
        flag=''
        if exp_tot and tot and abs(exp_tot-tot)>max(1,0.005*tot): flag='  <-- tot diff %.2f'%(tot-exp_tot)
        if um is not None and exp_um and abs(um-exp_um)>0.011: flag+=' um %.3f vs %.3f'%(um,exp_um)
        cls=r[4]+r[5]
        print('  %-5s d%-3d %-6s L=%-8s q=%-9s um=%-7s tot=%-9s %s'%(r[0],d,cls,r[9].split('{')[0].strip(),r[10].split('{')[0].strip()+(' '+re.search(r'\{F:(.*)\}',r[10]).group(1) if '{F' in r[10] else ''),r[11].split('{')[0],r[12].split('{')[0],flag))
        if tot: bydia[(cls,d)]+=tot; s+=tot
    print('  SUM=%.2f'%s, {k:round(v,2) for k,v in sorted(bydia.items(),key=lambda x:x[0][1])})
