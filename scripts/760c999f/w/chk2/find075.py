import ezdxf,re,json,sys
sys.stdout.reconfigure(encoding='utf-8')
d=ezdxf.readfile(r'C:\Users\Admin\AppData\Local\Temp\claude\D---------\760c999f-c28c-44e9-ba81-9cb2aa467e81\scratchpad\w\chk2\sch.dxf'); ops=[]
for e in d.modelspace():
    s=e.text if e.dxftype()=='MTEXT' else (e.dxf.text if e.dxftype()=='TEXT' else None)
    if s and re.search(r'-0[.,]100',s) and e.dxf.handle not in ('5D4BDD','5D4BE7'):
        for m in re.finditer(r'.{70}-0[.,]100.{30}',s): print(e.dxf.handle,repr(m.group(0)))
        ops.append({'t':'text','h':e.dxf.handle,'v':s.replace('-0.100','-0.750').replace('-0,100','-0,750')})
print('ops',len(ops)); json.dump(ops,open(r'C:\Users\Admin\AppData\Local\Temp\claude\D---------\760c999f-c28c-44e9-ba81-9cb2aa467e81\scratchpad\w\chk2\fx_sch075b.json','w',encoding='utf-8'),ensure_ascii=False)
