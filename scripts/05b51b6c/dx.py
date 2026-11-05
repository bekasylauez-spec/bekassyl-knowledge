import ezdxf,collections,sys,pickle,os
from ezdxf import bbox
if not os.path.exists('w/live.pkl') or os.path.getmtime('w/live.pkl')<os.path.getmtime('w/live.dxf'):
    d=ezdxf.readfile('w/live.dxf')
    ents=[]
    c=bbox.Cache()
    for e in d.modelspace():
        try: bb=bbox.extents([e],fast=True,cache=c)
        except Exception: continue
        if not bb.has_data: continue
        info=dict(h=e.dxf.handle,t=e.dxftype(),lay=e.dxf.get('layer',''),bb=(bb.extmin.x,bb.extmin.y,bb.extmax.x,bb.extmax.y))
        t=e.dxftype()
        if t=='TEXT': info['s']=e.dxf.text; info['ht']=e.dxf.height; info['p']=tuple(e.dxf.insert)[:2]
        elif t=='MTEXT': info['s']=e.plain_text(); info['ht']=e.dxf.char_height; info['p']=tuple(e.dxf.insert)[:2]
        elif t=='CIRCLE': info['c']=tuple(e.dxf.center)[:2]; info['r']=e.dxf.radius
        elif t=='LINE': info['p']=(tuple(e.dxf.start)[:2],tuple(e.dxf.end)[:2])
        elif t=='LWPOLYLINE': info['p']=[tuple(q) for q in e.get_points('xyb')]; info['cl']=e.closed
        elif t=='INSERT': info['n']=e.dxf.name; info['p']=tuple(e.dxf.insert)[:2]
        elif t=='DIMENSION': 
            info['s']=e.dxf.get('text',''); info['m']=e.get_measurement() if hasattr(e,'get_measurement') else None
            info['p']=(tuple(e.dxf.defpoint2)[:2],tuple(e.dxf.defpoint3)[:2],tuple(e.dxf.defpoint)[:2]); info['st']=e.dxf.get('dimstyle','')
        ents.append(info)
    pickle.dump(ents,open('w/live.pkl','wb'))
E=pickle.load(open('w/live.pkl','rb'))
def win(x0,y0,x1,y1):
    return [e for e in E if e['bb'][0]>=x0-1 and e['bb'][1]>=y0-1 and e['bb'][2]<=x1+1 and e['bb'][3]<=y1+1]
