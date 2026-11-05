import ab, sys
sys.stdout.reconfigure(encoding='utf-8')
YW=(-1733500,-1729900)
ONLY=['LWPOLYLINE','LINE','DIMENSION','SPDSBREAK','SPDSSECTION','SPDSNOTECOMB','SPDSNOTEPOSITION']
def W(x0,x1,d,dx): return {'t':'stretchwin','win':[x0+dx,YW[0],x1+dx,YW[1]],'d':[d,0],'only':ONLY}
ops=[]
dx=760200.0  # 6.3 Рм-3
ops+=[W(-453000,-451900,400,dx),W(-448500,-447250,-200,dx),W(-447000,-445900,200,dx),W(-442500,-441250,-400,dx)]
dx=789900.0  # 6.4 Рм-4
ops+=[W(-453000,-451900,400,dx),W(-448500,-448350,-600,dx),W(-448340,-447250,-550,dx),W(-447000,-445900,550,dx),
      # 2-аралық: сол жақ +550, ортаңғы аймақ соңы (-442386) −400−(−150)…: оң аймақ −400, -442386 сызығы −450
      W(-442500,-442350,-450,dx),W(-442340,-441250,-400,dx)]
print(ab.run(ops+[{'t':'save'}],'st',600)[-500:])
