import struct
d=open(r'D:\РАБОЧКА\От Маке\Завод\Аэротенк\Станция очистки -Аэротенк.lir','rb').read()
for a in (3365122,3365200,3365290,3365380,3365522,3365596,3365752):
    n=d[a+3];s=d[a+4:a+4+2*n].decode('utf-16le');e=a+4+2*n
    seg=d[e:e+80]
    fl=[round(x,4) for x in struct.unpack_from('<20f',seg)]
    print(s, fl)
    print('   prev', [round(x,4) for x in struct.unpack_from('<20f',d[a-80:a])])
