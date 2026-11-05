import ezdxf,json
SH=json.load(open('sheets.json'))
def sheet(x,y):
    for k,(a,b,c,d) in SH.items():
        if a<=x<=c and b<=y<=d: return k
d=ezdxf.readfile('w/live.dxf')
for e in d.modelspace().query('MULTILEADER'):
    try:
        c=e.context; t=c.mtext.default_content if c.mtext else ''; p=c.mtext.insert if c.mtext else c.base_point
    except Exception as ex: print('err',ex); continue
    print(sheet(p.x,p.y),e.dxf.handle,repr(t[:80]))
