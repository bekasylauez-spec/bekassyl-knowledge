import subprocess, json, gx, sys
S = gx.S
def check():
    gx.run([{'t': 'geomdump', 'win': [150000, 440000, 700000, 510000], 'file': S + r'\w\geom.txt'}, {'t': 'dxfout', 'file': S + r'\w\live.dxf'}], 'chk')
    r = subprocess.run(['python', '-X', 'utf8', 'oc.py', 'live.dxf', 'sheets_789.json', '--geom=geom.txt'], cwd=S + r'\w', capture_output=True)
    out = r.stdout.decode('utf-8', 'replace'); open(S + r'\w\oc_789.txt', 'w', encoding='utf-8').write(out)
    return out
for it in range(int(sys.argv[1]) if len(sys.argv) > 1 else 3):
    out = check()
    print('iter', it, [l for l in out.splitlines() if l.startswith('==') or l.startswith('TOTAL')])
    r = subprocess.run(['python', '-X', 'utf8', 'fixtext.py', S + r'\w\live.dxf', S + r'\w\geom.txt', S + r'\w\oc_789.txt', '528579,455939,644829,515339'], cwd=S, capture_output=True)
    print(r.stdout.decode('utf-8', 'replace').strip(), r.stderr.decode('utf-8', 'replace')[-300:])
    ops = json.load(open(S + r'\ops\fixtext.json'))
    if not ops: break
    gx.run(ops, 'fixtext')
out = check(); print('final', [l for l in out.splitlines() if l.startswith('==') or l.startswith('TOTAL')])
