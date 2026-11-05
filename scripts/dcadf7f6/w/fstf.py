import numpy as np
d=np.frombuffer(open(r'D:\РАБОЧКА\От Маке\Завод\Аэротенк\Станция очистки -Аэротенк.lir','rb').read(),dtype=np.uint8)
NE=948+15274
e_off=425686; tab_end=e_off+NE*38
print('elem table end',tab_end)
# check element records: dump bytes 2..6 field of each record
import struct
raw=d.tobytes()
vals=set()
for k in range(0,NE,500):
    a=e_off+k*38
    print(k,struct.unpack_from('<HI',raw,a), raw[a:a+38].hex())
