import sys,io; sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding="utf-8")
import ezdxf,sys,re
d=ezdxf.readfile(sys.argv[1]); m=d.modelspace()
for e in m:
    t=e.dxftype()
    if t in('TEXT','MTEXT'):
        s=e.plain_text() if t=='MTEXT' else e.dxf.text
        if re.search(r'Схема|Разрез|Узел|План|Фасад|Вид|ЛК',s):
            p=e.dxf.insert; print(e.dxf.handle,t,round(p.x),round(p.y),s[:90].replace('\n',' '))
