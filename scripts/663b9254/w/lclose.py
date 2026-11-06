import comtypes.client as cc, os
app = cc.CreateObject("LiraSapr.Application")
mine = os.path.abspath("../lira/бдм блок 3 униф.lir").lower()
for i in range(app.DocumentCount):
    d=app.Document(i)
    if d.PathName.lower()==mine:
        T=d.AllTables
        while T.ItemCount: T.Delete(0)
        d.Close(); print('closed')
        break
print('docs',app.DocumentCount,[app.Document(i).Title for i in range(app.DocumentCount)])
