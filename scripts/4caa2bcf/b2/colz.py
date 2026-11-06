import ezdxf, json
d=ezdxf.readfile('sch.dxf'); m=d.modelspace()
AXX={'13':0,'14':1300,'15':4975,'16':11075,'17':17075,'18':23075,'19':29075,'20':35075,'21':41075,'22':47450,'23':48750}
AXY={'А':0,'Б':9000,'В':13900,'Г':21000,'Д':27500,'Е':36000,'Ж':39000}
out={}
for k,lev in enumerate(['-1.200','-0.050','+4.500','+7.000']):
    X0=229592-84100+84100*k; Y0=-1773284; F0=135817+84100*k
    cols=[]
    for e in m.query('LWPOLYLINE[layer=="Размеры"]'):
        p=e.get_points('xy')
        if len(p)!=4: continue
        xs=[q[0] for q in p]; ys=[q[1] for q in p]
        if F0<min(xs)<F0+84100 and -1788184<min(ys)<-1728784 and max(xs)-min(xs)<2000 and max(ys)-min(ys)<2000:
            cols.append([min(xs)-X0,min(ys)-Y0,max(xs)-X0,max(ys)-Y0])
    out[lev]=cols; print(lev,len(cols))
json.dump(dict(cols=out,AXX=AXX,AXY=AXY),open('cols.json','w'),ensure_ascii=False)
