import zipfile,sys,os,shutil
z=zipfile.ZipFile(sys.argv[1]); out=sys.argv[2]; os.makedirs(out,exist_ok=True)
for i in z.infolist():
    n=i.filename
    if not (i.flag_bits & 0x800):
        n=n.encode('cp437').decode('cp866')
    n=n.replace(chr(92),'/')
    p=os.path.join(out,*[x for x in n.split('/') if x not in('','..')])
    if n.endswith('/'): os.makedirs(p,exist_ok=True); continue
    os.makedirs(os.path.dirname(p),exist_ok=True)
    if os.path.exists(p) and os.path.getsize(p)==i.file_size: continue
    with z.open(i) as s, open(p,'wb') as d: shutil.copyfileobj(s,d,1<<22)
    print(n,flush=True)
print('DONE')
