import re,sys
d=open(r'D:\РАБОЧКА\От Маке\Завод\Аэротенк\Станция очистки -Аэротенк.lir','rb').read()
out=[];i=0
for mm in re.finditer(b'\xff\xfe\xff',d):
    a=mm.start();n=d[a+3]
    s=d[a+4:a+4+2*n]
    try: t=s.decode('utf-16le')
    except: continue
    if t.strip(): out.append((a,t))
seen=set()
for a,t in out:
    if t in seen: continue
    seen.add(t);print(a,t)
