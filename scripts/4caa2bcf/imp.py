import ezdxf, gx, os
d=ezdxf.readfile('an/a61.dxf'); hs=[e.dxf.handle for e in d.modelspace()]
print(len(hs))
ops=[{'t':'import','file':os.path.join(gx.S,'an','a61.dwg'),'h':hs,'base':[0,0],'to':[3000000,0],'pre':'A:'},{'t':'frames'},{'t':'save'}]
print(gx.run(ops,'imp'))
