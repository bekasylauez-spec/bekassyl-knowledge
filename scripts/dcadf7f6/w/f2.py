import struct
raw=open(r'D:\РАБОЧКА\От Маке\Завод\Аэротенк\Станция очистки -Аэротенк.lir','rb').read()
for base in (0,1):
  pat=struct.pack('<II',0x33-base,0x34-base)
  i=raw.find(pat); hits=[]
  while i!=-1 and len(hits)<10: hits.append(i); i=raw.find(pat,i+1)
  print(base,hits)
