import re,struct
d=open(r'D:/_claude_work/v113/src/copy/v113.lir','rb').read()
o=open(r'D:/_claude_work/v113/src/lir_strings.txt','w',encoding='utf-8')
o.write('size %d header %r\n'%(len(d),d[:80]))
# utf-16 strings
for m in re.finditer(rb'(?:[\x20-\x7e\xa0-\xff]\x00|[\x00-\xff][\x04]){4,}',d):
    try:s=m.group().decode('utf-16le')
    except: continue
    o.write('U16 %d %r\n'%(m.start(),s))
# cp1251 strings
for m in re.finditer(rb'[\x20-\x7e\xc0-\xff]{6,}',d):
    s=m.group().decode('cp1251')
    if re.search('[А-Яа-я]',s) or 'sto' in s or 'MATS' in s:
        o.write('A %d %r\n'%(m.start(),s))
