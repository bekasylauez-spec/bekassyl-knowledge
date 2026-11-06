import json, subprocess, os, sys
S=r"C:\Users\Admin\AppData\Local\Temp\claude\210ab68cad67e8c1\25849707-e40f-4af8-947c-f7481c780970\scratchpad"
def run(ops, name='ops', doc=None, wait=900):
    p=os.path.join(S,'ops',name+'.json')
    json.dump(ops,open(p,'w',encoding='utf-8'),ensure_ascii=False)
    r=subprocess.run(['powershell','-ExecutionPolicy','Bypass','-File',os.path.join(S,'net','job.ps1'),'-Ops',p,'-Wait',str(wait)]+(['-Doc',doc] if doc else []),capture_output=True)
    return r.stdout.decode('utf-8','replace')+r.stderr.decode('utf-8','replace')
def tagmap():
    return json.load(open(os.path.join(os.environ['TEMP'],'b1_map.json'),encoding='utf-8-sig'))
if __name__=='__main__':
    print(run(json.load(open(sys.argv[1],encoding='utf-8')),'cli'))
