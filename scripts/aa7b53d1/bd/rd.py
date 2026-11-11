import ezdxf,sys,re
doc=ezdxf.readfile('w.dxf')
msp=doc.modelspace()
print('layouts',[l.name for l in doc.layouts])
import pickle
tabs=[]
for e in msp.query('ACAD_TABLE'):
    try:
        from ezdxf.entities import acad_table
    except: pass
    tabs.append(e)
print('tables',len(tabs))
for e in msp.query('MTEXT'):
    t=e.plain_text()
    if re.search('Грунтов|Эмаль|ГФ-021|ПФ-115|снегов|ветров|сейсм|Сейсм|агресс|промерз',t):
        print('MTEXT',e.dxf.handle,e.dxf.insert,e.dxf.char_height,'\n',t[:3000],'\n----')
