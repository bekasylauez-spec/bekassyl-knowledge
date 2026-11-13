import fitz,io,collections,re
d=fitz.open('km.pdf')
f=io.open('fonts.txt','w',encoding='utf-8')
bad=re.compile(r'3669|ЛК|RAS|Навес|ферм|Ф1|РС1|СГ1|Пр1|СВ1|СВ2|Абай|Қарасу',re.I)
for i,p in enumerate(d):
    c=collections.Counter(); ex={}
    for b in p.get_text('dict')['blocks']:
        for l in b.get('lines',[]):
            for s in l['spans']:
                k=(s['font'],round(s['size']/72*25.4,2)); c[k]+=1; ex.setdefault(k,s['text'])
                if bad.search(s['text']): f.write('BAD p%d %r\n'%(i+1,s['text']))
    f.write('p%d fonts:\n'%(i+1))
    for k,v in sorted(c.items(),key=lambda x:-x[1]): f.write('  %s  mm=%s n=%d ex=%r\n'%(k[0],k[1],v,ex[k]))
