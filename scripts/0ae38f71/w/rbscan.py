# find entities in modelspace whose raw tags mention "Рб-" (incl. SPDS proxies)
import re, sys
lines=open('live2.dxf',encoding='utf-8',errors='replace').read().split('\n')
lines=[l.rstrip('\r') for l in lines]
# locate ENTITIES section bounds
st=lines.index('ENTITIES'); en=st
while not (lines[en]=='ENDSEC'): en+=1
cur=None; out={}
i=st
while i<en:
    code=lines[i].strip(); val=lines[i+1] if i+1<len(lines) else ''
    if code=='0': cur={'type':val,'h':None,'x':None,'y':None,'txt':set()}
    elif cur is not None:
        if code=='5' and cur['h'] is None: cur['h']=val
        if code=='10' and cur['x'] is None: cur['x']=float(val)
        if code=='20' and cur['y'] is None: cur['y']=float(val)
        m=re.findall(r'Р[бБ]-\d',val)
        if m:
            cur['txt'].update(m); out[cur['h']]=cur
    i+=2
for h,c in out.items():
    print(c['type'],h,sorted(c['txt']),round(c['x'] or 0),round(c['y'] or 0))
