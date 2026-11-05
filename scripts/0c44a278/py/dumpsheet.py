import ezdxf,sys,collections
from ezdxf import bbox
S=r'C:\Users\beka\AppData\Local\Temp\claude\61d567fc0ab17a45\0c44a278-d609-485d-a50c-02efd03030b0\scratchpad\w'
d=ezdxf.readfile(S+r'\b3.dxf'); m=d.modelspace()
x0,y0,x1,y1=map(float,sys.argv[1:5])
C=collections.Counter(); ex={}
for e in m:
    try: b=bbox.extents([e],fast=True)
    except: continue
    if not b.has_data: continue
    if b.extmin.x>=x0 and b.extmax.x<=x1 and b.extmin.y>=y0 and b.extmax.y<=y1:
        k=(e.dxftype(),e.dxf.layer, e.dxf.get('name','') if e.dxftype()=='INSERT' else '')
        C[k]+=1; ex.setdefault(k,[]).append(e)
for k,v in sorted(C.items(),key=lambda x:-x[1]):
    e=ex[k][0]; info=''
    if k[0]=='LINE': info='lw=%s col=%s len=%.0f'%(e.dxf.lineweight,e.dxf.color,(e.dxf.end-e.dxf.start).magnitude)
    if k[0]=='LWPOLYLINE': info='lw=%s w=%s col=%s n=%d lt=%s'%(e.dxf.lineweight,e.dxf.get('const_width',0),e.dxf.color,len(e),e.dxf.get('linetype'))
    if k[0]=='DIMENSION': info='style=%s text=%r meas=%s'%(e.dxf.dimstyle,e.dxf.text,e.get_measurement())
    if k[0]=='MULTILEADER': info='style=%s txt=%r'%(e.dxf.get('style_handle'), e.context.mtext.default_content if e.context.mtext else None)
    if k[0] in('TEXT',): info='h=%s style=%s %r'%(e.dxf.height,e.dxf.style,e.dxf.text)
    if k[0] in('MTEXT',): info='h=%s style=%s %r'%(e.dxf.char_height,e.dxf.style,e.text[:60])
    print(v,k,e.dxf.handle,info)
