import comtypes.client as cc
import os,sys
app = cc.CreateObject("LiraSapr.Application")
p=os.path.abspath("../lira/бдм блок 3 униф.lir")
print("open", app.OpenDocument(p, False, True))
print('docs', app.DocumentCount)
for i in range(app.DocumentCount):
    d = app.Document(i)
    print(i, d.Title, d.PathName, 'modified', d.IsModified())
    T = d.AllTables
    print('  tables', T.Name, T.Type, T.ItemCount)
    def walk(node, ind):
        try: n = node.ItemCount
        except Exception: return
        for k in range(n):
            it = node.Item(k)
            try: pars = it.GetParameters()
            except Exception as e: pars = 'ERR %s' % e
            print(ind, k, it.Name, it.Type, str(pars)[:200])
            walk(it, ind + '  ')
    walk(T, '   ')
