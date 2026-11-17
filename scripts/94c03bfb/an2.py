import fitz,re
d=fitz.open('sec5.pdf')
o=open('dc5/an2.txt','w',encoding='utf8')
def num(s): return float(s.replace(',','.').replace(' ',''))
for i,p in enumerate(d):
    blocks=[b[4].replace('\n',' / ') for b in p.get_text('blocks')]
    full=' ## '.join(blocks)
    r=['P%d'%(i+1)]
    s1=[b for b in blocks if 'п.м.' in b][0]
    s1c=s1.replace(', / ',',').replace(' / ','|')
    m=re.search(r'п\.м\.\|([\d,]+)\|1,578\|([\d,]+)',s1c)
    q=num(m.group(1));t=num(m.group(2))
    r.append('q=%s t=%s calc=%.2f %s'%(m.group(1),m.group(2),q*1.578,'OK' if abs(q*1.578-t)<0.6 else 'DIFF'))
    s2=[b for b in blocks if b.startswith('Шп1 / См')][0].replace(' / ','|')
    m2=re.search(r'L= (\d+)\|(\d+)\|([\d,]+)\|([\d,]+)',s2)
    n=int(m2.group(2));mm=num(m2.group(3));tt=num(m2.group(4))
    r.append('Шп %s n=%d %.3f tt=%s %s'%(m2.group(1),n,n*mm,m2.group(4),'OK' if abs(n*mm-tt)<0.02 else 'DIFF'))
    ob=[b for b in blocks if 'Арматурные изделия / всего' in b][0]
    tot=num(re.findall(r'всего / ([\d,]+)',ob)[0])
    # расход values
    ras=[b for b in blocks if b.startswith('Ø16 /') or ('Ø16' in b and 'А500' not in b and len(b)<40)]
    r.append('итого=%s calc=%.2f'%(tot,t+tt))
    r.append('ras:'+';'.join(ras)[:60])
    # details
    det=[b for b in blocks if re.match(r'^A=|Ø8А240; / A=',b)]
    r.append('det:'+';'.join(det)[:80])
    o.write(' | '.join(r)+'\n')
