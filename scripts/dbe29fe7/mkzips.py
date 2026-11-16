import os
import sys
import zipfile

d = sys.argv[1]
os.makedirs(d, exist_ok=True)

with zipfile.ZipFile(os.path.join(d, 'z32.zip'), 'w', zipfile.ZIP_STORED) as z:
    z.writestr('a.bin', os.urandom(5000))
    z.writestr('b.txt', 'hello' * 100)

# force ZIP64 end records on a tiny archive
zipfile.ZIP64_LIMIT = 10
with zipfile.ZipFile(os.path.join(d, 'z64.zip'), 'w', zipfile.ZIP_STORED, allowZip64=True) as z:
    z.writestr('a.bin', os.urandom(5000))
    z.writestr('b.txt', 'hello' * 100)

for n in ('z32.zip', 'z64.zip'):
    with zipfile.ZipFile(os.path.join(d, n)) as z:
        print(n, 'testzip:', z.testzip(), 'entries:', len(z.namelist()))
with open(os.path.join(d, 'z64.zip'), 'rb') as f:
    print('z64 has EOCD64:', b'PK\x06\x06' in f.read())
