import json, subprocess, os, sys
S=r"C:\Users\beka\AppData\Local\Temp\claude\61d567fc0ab17a45\e9612f51-585b-4296-9d8b-098919c9d634\scratchpad"
def run(ops, name='ops', doc=None):
    p=os.path.join(S,'ops',name+'.json')
    json.dump(ops,open(p,'w',encoding='utf-8'),ensure_ascii=False)
    r=subprocess.run(['powershell','-ExecutionPolicy','Bypass','-File',os.path.join(S,'net','job.ps1'),'-Ops',p]+(['-Doc',doc] if doc else []),capture_output=True)
    out=r.stdout.decode('utf-8','replace')+r.stderr.decode('utf-8','replace')
    return out
def tagmap():
    return json.load(open(os.path.join(os.environ['TEMP'],'rg_map.json'),encoding='utf-8-sig'))
if __name__=='__main__':
    print(run(json.load(open(sys.argv[1],encoding='utf-8')),'cli'))

