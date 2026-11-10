import ezdxf,sys,re,collections
for n in ('ar','tx'):
    doc=ezdxf.readfile(r'D:/_claude_work/v113/src/dxf/%s.dxf'%n)
    msp=doc.modelspace()
    c=collections.Counter(e.dxftype() for e in msp)
    out=open(r'D:/_claude_work/v113/src/dxf/%s_texts.txt'%n,'w',encoding='utf-8')
    out.write('%s %s\n'%(n,dict(c.most_common(15))))
    out.write('layouts %s\n'%doc.layouts.names())
    out.write('extmin %s extmax %s\n'%(doc.header.get('$EXTMIN'),doc.header.get('$EXTMAX')))
    k=0
    def walk(ents,depth=0):
        global k
        for e in ents:
            t=e.dxftype()
            if t in('TEXT','MTEXT'):
                s=e.dxf.text if t=='TEXT' else e.plain_text()
                p=e.dxf.insert
                out.write('%s|%.0f|%.0f|%s|%s\n'%(t,p.x,p.y,e.dxf.layer,s.replace('\n',' / ')))
            elif t=='DIMENSION':
                try:
                    out.write('DIM|%s|%s|meas=%.1f|%s\n'%(e.dxf.layer,e.dxf.text,e.get_measurement() if hasattr(e,'get_measurement') else 0,''))
                except Exception as ex: out.write('DIM err %s\n'%ex)
            elif t=='INSERT' and depth==0:
                for a in e.attribs:
                    out.write('ATT|%s|%s=%s\n'%(e.dxf.name,a.dxf.tag,a.dxf.text))
    walk(msp)
    out.close()
    print(n,dict(c.most_common(8)),doc.layouts.names())
