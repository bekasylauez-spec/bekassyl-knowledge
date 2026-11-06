import comtypes.client as cc, os, json, time
app = cc.CreateObject("LiraSapr.Application")
import comtypes.gen as G
mod=[getattr(G,m) for m in dir(G) if hasattr(getattr(G,m),'ILiraTable')][0]
mine = os.path.abspath("../lira/бдм блок 3 униф.lir").lower()
d=[app.Document(i) for i in range(app.DocumentCount) if app.Document(i).PathName.lower()==mine][0]
T=d.AllTables; print('items',T.ItemCount)
it=T.Item(0); print(it.Name,it.Type)
tb=it.QueryInterface(mod.ILiraTable)
t0=time.time()
try: tb.RefillFromModel()
except Exception as e: print('refill',e)
c=tb.GetContents()
print('t',round(time.time()-t0,1), type(c), len(c))
json.dump(c,open('tab31.json','w',encoding='utf-8'),ensure_ascii=False,default=str)
for r in list(c)[:8]: print(str(r)[:300])
