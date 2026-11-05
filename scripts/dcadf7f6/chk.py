import ab,subprocess,sys,json
S=ab.S
print(ab.run([{'t':'dxfout','file':S+r'\w\live.dxf'},{'t':'geomdump','win':[-1000,449000,2710000,510000],'file':S+r'\w\geom.txt'}],'gd',900)[-80:])
r=subprocess.run([sys.executable,'-W','ignore','oc.py','live.dxf','sheets.json','--geom=geom.txt'],cwd=S+r'\w',capture_output=True)
open(S+r'\w\oc_out.txt','wb').write(r.stdout+r.stderr)
out=r.stdout.decode('utf-8','replace')
print('\n'.join(l for l in out.splitlines() if l.startswith('==') or l.startswith('TOTAL') or 'ПРОЧИТ' in l))
