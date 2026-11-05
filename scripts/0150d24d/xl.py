import openpyxl,sys
f,out=sys.argv[1],sys.argv[2]
wb=openpyxl.load_workbook(f,data_only=True)
with open(out,'w',encoding='utf-8') as o:
  for ws in wb:
    o.write(f'== {ws.title} {ws.max_row} {ws.max_column}\n')
    for r in ws.iter_rows(values_only=True):
        if any(c is not None for c in r): o.write(' | '.join(str(c)[:600] for c in r if c is not None)+'\n')
