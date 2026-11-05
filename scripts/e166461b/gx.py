import json, subprocess, os, sys
S=r"C:\Users\Admin\AppData\Local\Temp\claude\210ab68cad67e8c1\e166461b-bde0-4f75-9345-660eafbd0735\scratchpad"
def run(ops, name='ops', doc=None):
    p=os.path.join(S,'ops',name+'.json')
    json.dump(ops,open(p,'w',encoding='utf-8'),ensure_ascii=False)
    r=subprocess.run(['powershell','-ExecutionPolicy','Bypass','-File',os.path.join(S,'net','job.ps1'),'-Ops',p]+(['-Doc',doc] if doc else []),capture_output=True)
    out=r.stdout.decode('utf-8','replace')+r.stderr.decode('utf-8','replace')
    return out
def tagmap():
    return json.load(open(os.path.join(os.environ['TEMP'],'gx_map.json'),encoding='utf-8-sig'))
if __name__=='__main__':
    print(run(json.load(open(sys.argv[1],encoding='utf-8')),'cli'))
