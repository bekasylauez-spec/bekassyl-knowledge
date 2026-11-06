import comtypes.client as cc, time, sys, os
app=cc.CreateObject("LiraSapr.Application")
print('app ok', app.DocumentCount)
p=os.path.abspath('b3rig.lir')
msgs=None
r=app.OpenDocument(p, False, True)
print('open', r, app.DocumentCount)
doc=app.ActiveDocument
print(doc.Title, doc.PathName)
import comtypes, array
doc.SetGenerateCsvTables(True, [31,33])
print('csv set', doc.GetGenerateCsvTables())
app.StartAnalysis(p)
print('started', time.strftime('%X'))
