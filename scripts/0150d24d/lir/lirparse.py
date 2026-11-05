import struct
def load(path='v3.lir'):
    d=open(path,'rb').read()
    nodes=[]; a=166
    while a+24<=76434:
        nodes.append(struct.unpack_from('<3d',d,a)); a+=28
    els=[]; a=76434
    while True:
        f=struct.unpack_from('<I',d,a)[0]; ns=[v for v in struct.unpack_from('<8I',d,a+4) if v]
        if f!=1 or not ns or max(ns)>len(nodes): break
        t=struct.unpack_from('<H',d,a+36)[0]
        els.append((t,ns)); a+=38
    return d,nodes,els,a
