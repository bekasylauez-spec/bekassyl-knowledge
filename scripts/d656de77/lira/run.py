import comtypes.client as cc, time, os, subprocess, glob, sys
app=cc.CreateObject("LiraSapr.Application")
p=os.path.abspath('galx.lir')
app.OpenDocument(p, False, True)
doc=None
for i in range(app.DocumentCount):
    if app.Document(i).PathName.lower()==p.lower(): doc=app.Document(i)
print('doc', doc.Title, flush=True)
try: doc.SetGenerateCsvTables(True, (31,))
except Exception as e: print('csv err', e, flush=True)
print('csv', doc.GetGenerateCsvTables(), flush=True)
app.StartAnalysis(p); print('started', time.strftime('%X'), flush=True)
def busy():
    o=subprocess.run(['tasklist'],capture_output=True).stdout.decode('cp866','replace')
    return any(n in o for n in ('FESolver','ArmaDA','ComAndArm'))
t0=time.time(); seen=False
while time.time()-t0<9000:
    time.sleep(20)
    b=busy(); seen|=b
    if seen and not b:
        time.sleep(30)
        if not busy(): break
print('end', time.strftime('%X'), flush=True)
W=r'C:\Users\Public\Documents\LIRA SAPR\LIRA SAPR 2024\Work'
print(glob.glob(W+r'\galx*\**\*.csv',recursive=True), flush=True)
