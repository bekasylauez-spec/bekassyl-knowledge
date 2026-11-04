import fitz, collections, sys
D='D:/РАБОЧКА/Bekassyl/15_Проекты/Онкологический центр Блок 1 Секция 1/Источники/'
MM=25.4/72
for f,pg in (('2.Схема каркаса Блок 1 Секция 1.pdf',0),('2.Схема каркаса Блок 1 Секция 1.pdf',6),('3. Фундамент Блок 1 Секция 1.pdf',0),('3. Фундамент Блок 1 Секция 1.pdf',1),('3. Фундамент Блок 1 Секция 1.pdf',2)):
    p=fitz.open(D+f)[pg]
    g=collections.defaultdict(list)
    for d in p.get_drawings():
        w=round((d.get('width') or 0)*MM,2); r=d['rect']
        g[w].append((round(r.x0*MM),round(r.y0*MM),round(r.width*MM,1),round(r.height*MM,1),len(d['items']),d.get('fill') is not None))
    print('==',f[:10],pg+1)
    for w in sorted(g):
        L=g[w]; big=sorted(L,key=lambda t:-(t[2]+t[3]))[:4]
        print('  lw',w,'n',len(L),'largest:',big)
