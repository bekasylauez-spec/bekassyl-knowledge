import ezdxf,sys
for f in sys.argv[2:]:
    d=ezdxf.readfile(sys.argv[1]+'/ar/'+f+'.dxf'); m=d.modelspace(); print('=====',f)
    for e in m:
        t=e.dxftype()
        if t=='MTEXT': print('MT',e.dxf.layer,[round(v) for v in e.dxf.insert][:2],repr(e.plain_text()[:120]))
        elif t=='TEXT': print('TX',e.dxf.layer,[round(v) for v in e.dxf.insert][:2],repr(e.dxf.text))
        elif t=='DIMENSION':
            try: mv=round(e.get_measurement(),1)
            except: mv=None
            print('DIM',[round(v) for v in e.dxf.defpoint2][:2],[round(v) for v in e.dxf.defpoint3][:2],mv,repr(e.dxf.text))
        elif t=='INSERT' and e.dxf.layer in('Аннотация','Узлы','Разрезы','Оси','Марки помещений','Несущие колонны'):
            print('INS',e.dxf.layer,e.dxf.name[:60],[round(v) for v in e.dxf.insert][:2],[(a.dxf.tag,a.dxf.text) for a in e.attribs])
