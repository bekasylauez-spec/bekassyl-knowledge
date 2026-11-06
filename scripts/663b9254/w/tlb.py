import comtypes.typeinfo as ti
p = r"C:\Program Files (x86)\LIRA SAPR\LIRA SAPR 2024\Bin\x64\LiraSapr.exe"
tl = ti.LoadTypeLibEx(p)
skip = {'QueryInterface', 'AddRef', 'Release', 'GetTypeInfoCount', 'GetTypeInfo', 'GetIDsOfNames', 'Invoke'}
for i in range(tl.GetTypeInfoCount()):
    t = tl.GetTypeInfo(i); a = t.GetTypeAttr(); name = t.GetDocumentation(-1)[0]
    if a.typekind not in (3, 4): continue
    print('==', name)
    for j in range(a.cFuncs):
        f = t.GetFuncDesc(j); names = t.GetNames(f.memid, f.cParams + 1)
        if names[0] in skip: continue
        print('  ', names[0], names[1:], f.invkind)
