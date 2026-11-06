import ab,os,re,sys
W=os.path.join(ab.S,'w')
hs=sys.argv[1:]
ab.run([{'t':'serdump','h':h,'file':os.path.join(W,h+'.bin')} for h in hs],'lv')
for h in hs:
    b=open(os.path.join(W,h+'.bin'),'rb').read()
    print(h, re.findall(rb'[ -~]{4,}',b)[:30])
    print('  U16:', [m.decode('utf-16le','replace') for m in re.findall(rb'(?:[ -~\x00-\xff][\x00\x04]){4,}',b)][:20])
