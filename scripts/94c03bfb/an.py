import fitz,re
d=fitz.open('sec5.pdf')
o=open('dc5/an.txt','w',encoding='utf8')
def num(s): return float(s.replace(',','.').replace(' ',''))
for i,p in enumerate(d):
    W=p.get_text('words')
    blocks=p.get_text('blocks')
    txt=[(b[0],b[1],b[2],b[3],b[4].replace('\n',' / ')) for b in blocks]
    def find(pat):
        return [t for t in txt if re.search(pat,t[4])]
    r=[ 'P%d'%(i+1)]
    t=find(r'Стена См-\d+ \(t=')
    r.append(t[0][4].strip() if t else 'NO TITLE')
    sh=find(r'^РП')
    r.append(sh[0][4].replace('\n',' ') if sh else 'NOSHEET')
    s1=find(r'п\.м\.')
    s2=find(r'^Шп1 / См')
    bt=find(r'Бетон')
    ob=find(r'Арматурные изделия / всего')
    ok=[]
    try:
        m=re.findall(r'п\.м\. / ([\d, /]+)',s1[0][4])
        r.append('Ø16:'+m[0].strip())
        m2=re.findall(r'L= (\d+) / (\d+) / ([\d,]+) / ([\d,]+)',s2[0][4])[0]
        r.append('Шп:L%s n%s m%s tot%s'%m2)
        L16=num(m[0].replace(' / ','').replace('/','')) if True else 0
        a=num(m2[1])*num(m2[2])
        r.append('chkShp=%.2f'%a)
        tot=num(re.findall(r'([\d,]+) / $',ob[0][4])[0])
        r.append('расход_итого=%s'%tot)
        t16=num(re.findall(r'1,578 / ([\d,]+)',s1[0][4])[0])
        r.append('calc=%.2f'%(t16+num(m2[3])))
        r.append('16check=%.1f'%(L16*1.578) )
        r.append('t16=%.1f'%t16)
        r.append('bet='+re.findall(r'м³ / ([\d,]+)',bt[0][4])[0])
    except Exception as e:
        r.append('ERR %s'%e)
    o.write(' | '.join(r)+'\n')
