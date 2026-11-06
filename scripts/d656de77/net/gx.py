import json, subprocess, os, sys
S=r"C:\Users\beka\AppData\Local\Temp\claude\61d567fc0ab17a45\d656de77-c990-4fe2-b159-b1f2f72711f7\scratchpad"
def run(ops, name='ops', doc=None):
    p=os.path.join(S,'ops',name+'.json')
    json.dump(ops,open(p,'w',encoding='utf-8'),ensure_ascii=False)
    r=subprocess.run(['powershell','-ExecutionPolicy','Bypass','-File',os.path.join(S,'net','job.ps1'),'-Ops',p]+(['-Doc',doc] if doc else []),capture_output=True)
    return r.stdout.decode('utf-8','replace')+r.stderr.decode('utf-8','replace')
def tagmap():
    return json.load(open(os.path.join(os.environ['TEMP'],'gq_map.json'),encoding='utf-8-sig'))
def log():
    return open(os.path.join(os.environ['TEMP'],'gq_log.txt'),encoding='utf-8-sig').read()
if __name__=='__main__':
    print(run(json.load(open(sys.argv[1],encoding='utf-8')),'cli'))
