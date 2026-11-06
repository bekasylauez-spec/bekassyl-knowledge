import json, subprocess, os, sys
S=r"C:\Users\Admin\AppData\Local\Temp\claude\210ab68cad67e8c1\9a1000cd-e0d9-42b2-b432-f6f3db0e7099\scratchpad\gal"
class Hang(Exception): pass
def run(ops, name='ops', doc=None, wait=300):
    p=os.path.join(S,'ops',name+'.json')
    json.dump(ops,open(p,'w',encoding='utf-8'),ensure_ascii=False)
    r=subprocess.run(['powershell','-ExecutionPolicy','Bypass','-File',os.path.join(S,'net','job.ps1'),'-Ops',p,'-Wait',str(wait)]+(['-Doc',doc] if doc else []),capture_output=True)
    out=r.stdout.decode('utf-8','replace')+r.stderr.decode('utf-8','replace')
    if out.lstrip().startswith('timeout'): raise Hang(name)
    return out
def relaunch():
    r=subprocess.run(['powershell','-ExecutionPolicy','Bypass','-File',os.path.join(S,'net','relaunch.ps1')],capture_output=True)
    return r.stdout.decode('utf-8','replace')
def tagmap():
    return json.load(open(os.path.join(os.environ['TEMP'],'m2_map.json'),encoding='utf-8-sig'))
if __name__=='__main__':
    print(run(json.load(open(sys.argv[1],encoding='utf-8')),'cli'))
