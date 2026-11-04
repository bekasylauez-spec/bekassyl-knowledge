import re,os
S=os.path.dirname(os.path.abspath(__file__))
t="".join(open(f"{S}/txt/pages/p{i:03d}.txt",encoding='utf8').read() for i in (2,3,4))
lines=[l.strip() for l in t.splitlines()]
# parse entries: number line followed by name lines until next number
ent=[];i=0
while i<len(lines):
    if re.fullmatch(r"\d\.\d{1,2}",lines[i]) and i+1<len(lines) and not re.fullmatch(r"\d\.\d{1,2}",lines[i+1]) and lines[i+1] not in ('РП','Листов'):
        n=lines[i];name=[];i+=1
        while i<len(lines) and not re.fullmatch(r"\d\.\d{1,2}",lines[i]) and not lines[i].startswith('Ведомость') and lines[i]!='РП':
            name.append(lines[i]);i+=1
        ent.append((n," ".join(name)))
    else:i+=1
ent=[e for e in ent if e[1].strip()]; print(len(ent))
norm=lambda s:re.sub(r"[\s\-–—.]","",s).lower()
for k,(n,name) in enumerate(ent,1):
    p=open(f"{S}/txt/pages/p{k:03d}.txt",encoding='utf8').read()
    hasnum = re.search(r"(^|\n)\s*"+re.escape(n)+r"\s*(\n|$)",p) is not None
    ok = norm(name) in norm(p)
    if not ok or not hasnum: print(k,n,hasnum,ok,name)
