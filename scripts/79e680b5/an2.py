import ezdxf,sys
doc=ezdxf.readfile(sys.argv[1]); msp=doc.modelspace()
out=open('an2.txt','w',encoding='utf-8')
e=doc.entitydb['1285AB']
out.write(f'{e.dxf.insert} h={e.dxf.char_height} w={e.dxf.width} ap={e.dxf.attachment_point}\n')
out.write(e.text+'\n')
# texts mentioning ст/фм/Тип
for e in msp.query('MTEXT TEXT'):
    t=e.plain_text() if e.dxftype()=='MTEXT' else e.dxf.text
    if any(k in t for k in ['Опалубочный','Схема расположения','Разрез','Спецификация']): out.write(f'{e.dxf.handle}\t{e.dxf.layer}\t{tuple(round(v) for v in e.dxf.insert)[:2]}\t{t[:90]!r}\n')
