import ab,os,re
W=os.path.join(ab.S,'w')
hs=('lv_37FB07','lv_37FB08','37FB07','37FB08')
ab.run([{'t':'serdump','h':h,'file':os.path.join(W,h+'.bin')} for h in hs],'lv')
for h in hs:
    b=open(os.path.join(W,h+'.bin'),'rb').read()
    print(h, set(re.findall(rb'[+-]?\d{1,3}[,.]\d{3}',b)))
