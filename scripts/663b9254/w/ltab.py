import comtypes.client as cc, os, sys, json, traceback
app = cc.CreateObject("LiraSapr.Application")
mine = os.path.abspath("../lira/бдм блок 3 униф.lir").lower()
d = None
for i in range(app.DocumentCount):
    x = app.Document(i)
    if x.PathName.lower() == mine: d = x
assert d is not None, 'my doc not open'
print('doc', d.PathName)
T = d.AllTables
for typ in [int(a) for a in sys.argv[1:]] or [31]:
    for pars in (None, [], ''):
        try:
            it = T.CreateNewItem(typ, pars, 0, 'col%d' % typ, -1)
            print('created', typ, repr(pars), it)
            break
        except Exception as e:
            print('fail', typ, repr(pars), e)
print('items', T.ItemCount)
for k in range(T.ItemCount):
    it = T.Item(k)
    print(k, it.Name, it.Type)
    try:
        print('  pars', str(it.GetParameters())[:300])
    except Exception as e: print('  pars err', e)
    try:
        c = it.GetContents()
        json.dump(c, open('tab_%d.json' % k, 'w', encoding='utf-8'), ensure_ascii=False, default=str)
        print('  contents', type(c), len(c) if hasattr(c, '__len__') else '', str(c)[:500])
    except Exception as e:
        print('  contents err', e)
