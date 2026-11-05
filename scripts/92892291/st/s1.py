import ezdxf,re,sys
d=ezdxf.readfile('st.dxf')
msp=d.modelspace()
hits=[]
pat=re.compile(r'(?i)(свая|сваи|свай|раскат|буро|скважин|бетон|ростверк)')
def walk(ents,src):
  for e in ents:
    if e.dxftype() in ('TEXT','MTEXT'):
      t=e.dxf.text if e.dxftype()=='TEXT' else e.text
      if pat.search(t):
        p=e.dxf.insert; hits.append((round(p.x),round(p.y),src,t[:200]))
walk(msp,'msp')
for b in d.blocks:
  if not b.name.startswith('*Model'):
    walk(b,b.name)
for h in sorted(hits,key=lambda h:(h[2],h[0],-h[1])): print(h)
