import comtypes.client as cc, time, os, subprocess, glob
app=cc.CreateObject("LiraSapr.Application")
p=os.path.abspath('b3rig.lir')
doc=None
for i in range(app.DocumentCount):
    if app.Document(i).PathName.lower()==p.lower(): doc=app.Document(i)
if doc is None:
    app.OpenDocument(p, False, True)
    for i in range(app.DocumentCount):
        if app.Document(i).PathName.lower()==p.lower(): doc=app.Document(i)
print('doc', doc.Title, flush=True)
try: doc.SetGenerateCsvTables(True, (31,))
except Exception as e: print('csv err', e)
print('csv', doc.GetGenerateCsvTables(), flush=True)
app.StartAnalysis(p); print('started', time.strftime('%X'), flush=True)
W=r'C:\Users\Public\Documents\LIRA SAPR\LIRA SAPR 2024\Work'
def busy():
    o=subprocess.run(['tasklist'],capture_output=True,text=True).stdout
    return any(n in o for n in ('FESolver','ArmaDA','ComAndArm'))
t0=time.time(); seen=False
while time.time()-t0<5400:
    time.sleep(20)
    b=busy(); seen|=b
    if seen and not b:
        time.sleep(30)
        if not busy(): break
print('end', time.strftime('%X'), flush=True)
print(glob.glob(W+r'\b3rig*\**\*.csv',recursive=True))
print(open(W+r'\b3rig_01.b3rig',encoding='utf-8',errors='replace').read()[-1500:])
