import comtypes.client as cc, time, os, glob
app=cc.CreateObject("LiraSapr.Application")
p=os.path.abspath('galx.lir'); doc=None
for i in range(app.DocumentCount):
    if app.Document(i).PathName.lower()==p.lower(): doc=app.Document(i)
print('doc', doc.Title, flush=True)
doc.SetGenerateCsvTables(True, (31,)); print(doc.GetGenerateCsvTables(), flush=True)
doc.Save(True); print('saved', flush=True)
app.StartAnalysis(p); print('started', time.strftime('%X'), flush=True)
W=r'C:\Users\Public\Documents\LIRA SAPR\LIRA SAPR 2024\Work'
t0=time.time()
while time.time()-t0<3600:
    time.sleep(15)
    g=glob.glob(W+r'\galx.DOCS\**\*31*.csv',recursive=True)
    if g:
        time.sleep(20); print('csv', g, time.strftime('%X'), flush=True); break
print('end', time.strftime('%X'), flush=True)
