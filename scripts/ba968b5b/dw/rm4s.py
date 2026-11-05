import ab, sys
sys.stdout.reconfigure(encoding='utf-8')
YW=(-1733500,-1729900)
ONLY=['LWPOLYLINE','LINE','DIMENSION','SPDSBREAK','SPDSSECTION','SPDSNOTECOMB','SPDSNOTEPOSITION']
def W(x0,x1,d,dx): return {'t':'stretchwin','win':[x0+dx,YW[0],x1+dx,YW[1]],'d':[d,0],'only':ONLY}
dx=789900.0
ops=[W(-453000,-451900,400,dx),W(-448500,-448350,-600,dx),W(-448340,-447250,-550,dx),W(-447000,-445900,550,dx),
     W(-442500,-442350,-450,dx),W(-442340,-441250,-400,dx)]
print(ab.run(ops+[{'t':'save'}],'st4',600)[-400:])
