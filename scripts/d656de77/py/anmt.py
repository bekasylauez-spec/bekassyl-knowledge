import sys,os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); from common import *
import ezdxf
AN=gx.S+r'\an\an.dwg'; AX,AY=-232571.9,411799.3
gx.run([dict(t='listfile',file=AN,win=[AX,AY,AX+31500,AY+21000])],'lf')
hs=[l.split('\t')[2] for l in gx.log().splitlines() if l.startswith('L\tMTEXT')]
gx.run([dict(t='listfile',file=AN,win=[-212900,426600,-204400,432650])],'lf')
hs+=[l.split('\t')[2] for l in gx.log().splitlines() if l.startswith('L\tMTEXT')]
run([dict(t='import',file=AN,h=hs,base=[0,0],to=[5000000,0],pre='AM:')],'im')
f=gx.S+r'\w\tmp.dxf'; gx.run([dict(t='dxfout',file=f)],'dx')
m=gx.tagmap(); doc=ezdxf.readfile(f)
for h in hs:
    nh=m.get('AM:'+h.upper())
    if nh: e=doc.entitydb[nh]; print(h, round(e.dxf.insert[0]-5e6-AX), round(e.dxf.insert[1]-AY), repr(e.text[:80]))
run([dict(t='erase',h=['AM:'+h.upper() for h in hs])],'er')
