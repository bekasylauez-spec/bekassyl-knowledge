import zipfile,sys,os,shutil
z=sys.argv[1]; out=sys.argv[2]; os.makedirs(out,exist_ok=True)
with zipfile.ZipFile(z) as f:
    for i in f.infolist():
        n=i.filename
        if not (i.flag_bits & 0x800):
            n=n.encode('cp437').decode('cp866')
        if n.endswith('/'): continue
        dst=os.path.join(out,os.path.basename(n))
        if os.path.exists(dst) and os.path.getsize(dst)==i.file_size: continue
        with f.open(i) as s, open(dst,'wb') as d: shutil.copyfileobj(s,d,1<<24)
        print(n,i.file_size,flush=True)
print('DONE')
