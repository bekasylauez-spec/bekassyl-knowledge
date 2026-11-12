import ezdxf,sys
sys.stdout.reconfigure(encoding='utf-8')
doc=ezdxf.readfile(r'D:\_claude_work\otst\src\analog.dxf')
for h in ('2D4651','2D44BD'):
    ins=doc.entitydb[h]; print(h,ins.dxf.name,tuple(ins.dxf.insert),ins.dxf.xscale,ins.dxf.rotation, ins.dxf.layer)
    blk=doc.blocks[ins.dxf.name]
    for e in blk:
        t=e.dxftype(); s=''
        if t=='LINE': s='%.0f,%.0f %.0f,%.0f'%(e.dxf.start.x,e.dxf.start.y,e.dxf.end.x,e.dxf.end.y)
        elif t in('TEXT','MTEXT'): s=(e.dxf.text if t=='TEXT' else e.text)+' h%.0f @%.0f,%.0f'%((e.dxf.height if t=='TEXT' else e.dxf.char_height),e.dxf.insert.x,e.dxf.insert.y)
        elif t=='CIRCLE': s='c %.0f,%.0f r%.0f'%(e.dxf.center.x,e.dxf.center.y,e.dxf.radius)
        elif t=='LWPOLYLINE': s=str([(round(x),round(y)) for x,y in e.get_points('xy')])
        elif t=='DIMENSION': s=e.dxf.dimstyle+' '+str(e.dxf.get('text',''))+' m=%.0f'%e.get_measurement()
        elif t=='INSERT': s=e.dxf.name
        print('  ',t,e.dxf.layer,s)
