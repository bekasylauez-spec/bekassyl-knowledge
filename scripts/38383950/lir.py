import struct,re,collections,json
d=open('v3.lir','rb').read()
N=[struct.unpack_from('<ddd',d,166+28*i) for i in range(2724)]
E=[]
o=76434
while True:
    t,a,b=struct.unpack_from('<Hxxii',d,o)
    if t==0 or t>100 or not(0<a<=2724 and 0<b<=2724): break
    E.append((t,a-1,b-1)); o+=38
print('elements',len(E),'end',o)
st=[struct.unpack_from('<H',d,1517340+2*i)[0] for i in range(len(E))]
print(collections.Counter(st).most_common(40))
json.dump({'N':N,'E':E,'S':st},open('lir.json','w'))
