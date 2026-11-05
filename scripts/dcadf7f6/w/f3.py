import struct,collections,pickle
raw=open(r'D:\РАБОЧКА\От Маке\Завод\Аэротенк\Станция очистки -Аэротенк.lir','rb').read()
a=1781700; NE=16222; recs=[]
for k in range(NE):
    t,idx,s,ke,nn=struct.unpack_from('<HIIHH',raw,a)
    assert idx==k,(k,idx,a)
    # find next
    if k<NE-1:
        b=a+16
        while True:
            t2,i2,s2,ke2,nn2=struct.unpack_from('<HIIHH',raw,b)
            if i2==k+1 and ke2 in (1,2,3,4,5,10,41,42,44,51,55,56,57) and nn2<=8 and s2<100: break
            b+=1
            if b-a>400: raise SystemExit(('lost',k,a))
        L=b-a
    else: L=80+4*nn
    ns=struct.unpack_from('<%dI'%nn,raw,a+L-4*nn)
    recs.append((t,s,ke,ns)); a+=L
print('end',a)
C=collections.Counter((r[1],r[2],r[0]) for r in recs); print(C)
pickle.dump(recs,open('recs.pkl','wb'))
