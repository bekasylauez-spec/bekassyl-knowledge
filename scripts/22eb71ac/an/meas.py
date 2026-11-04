import fitz, json, collections
D='D:/РАБОЧКА/Bekassyl/15_Проекты/Онкологический центр Блок 1 Секция 1/Источники/'
MM=25.4/72
for f,pg in (('2.Схема каркаса Блок 1 Секция 1.pdf',0),('3. Фундамент Блок 1 Секция 1.pdf',0),('3. Фундамент Блок 1 Секция 1.pdf',2)):
    p=fitz.open(D+f)[pg]
    circ=collections.Counter(); arrows=collections.Counter()
    for d in p.get_drawings():
        r=d['rect']; w=r.width*MM; h=r.height*MM
        kinds=''.join(i[0] for i in d['items'])
        if kinds.count('c')>=4 and abs(w-h)<0.3 and 4<w<15: circ[(round(w,1),round((d.get('width') or 0)*MM,2))]+=1
        if d.get('fill') is not None and 1<max(w,h)<6 and kinds in ('lll','ll','l'*3): arrows[(round(max(w,h),1),round(min(w,h),1))]+=1
    print(f[:12],pg+1,'circles(d,lw):',circ.most_common(6))
    print('   filled small (arrows):',arrows.most_common(6))
    # text glyph heights: measure bbox height of digit-only spans
    hs=collections.Counter()
    for b in p.get_text('rawdict')['blocks']:
        for l in b.get('lines',[]):
            for s in l['spans']:
                for c in s['chars']:
                    if c['c'] in '0123456789':
                        hs[(round(s['size']*MM,2))]+=0
    break_=0
