import io, collections, csv, re
D=r"C:\Users\Admin\AppData\Local\Temp\claude\a7137524bdaa49d0\c55bc92b-0511-4932-9c00-c1294111057c\scratchpad\mine\\"
out=io.open(D+'a9_out.txt','w',encoding='utf-8')
def P(*a): out.write(' '.join(str(x) for x in a)+'\n')
Pl=list(csv.DictReader(io.open(D+'plates.tsv',encoding='utf-8'),delimiter='\t'))
byid=collections.defaultdict(list)
for r in Pl: byid[r['id']].append(r)
KW=('гусет','фасонка','жота пластинасы','косынка','кронштейн','тартпа','тірек листі','оголовок','ребро')
grp=collections.defaultdict(list)
for pid,l in byid.items():
    n=re.sub(r' - [^ ]+$','',l[0]['name'])
    if not any(k in n for k in KW): continue
    t=float(l[0]['t'])
    elems=set(x['contactElem'] for x in l)
    # distinct contact faces by (elem, area rounded)
    faces=set((x['contactElem'],round(float(x['contactArea'])),round(float(x['outstand']))) for x in l)
    outs=sorted(set(round(float(x['outstand'])) for x in l))
    grp[n].append((pid,t,len(l),len(elems),outs,l[0]['loc']))
P('plate types with frame side contacts:',len(grp))
rows=[]
for n,l in grp.items():
    # take representative: the one with min rows
    l.sort(key=lambda x:(x[2],x[3]))
    pid,t,nrows,nel,outs,loc=l[0]
    mxo=max(outs); mno=min(outs)
    rows.append((mxo/t,n,len(l),t,nrows,nel,outs,loc))
rows.sort(reverse=True)
for r in rows: P('%.1f'%r[0],'|',r[1][:70],'| plates',r[2],'| t',r[3],'| contact rows',r[4],'distinct supports',r[5],'| outstands',r[6][:6])
out.close()