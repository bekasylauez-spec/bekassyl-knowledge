import ezdxf, re
d=ezdxf.readfile("r.dxf"); m=d.modelspace()
pat=re.compile(sys_argv:=r'(?i)(профлист|поликарбонат|кровл|покрыти|профнастил|Н\d\d|С\d\d-|сэндвич|Зд-|-18|окраск|грунт)')
with open("txt.out","w",encoding="utf-8") as f:
  for e in m.query("TEXT MTEXT"):
    s=e.plain_text() if e.dxftype()=="MTEXT" else e.dxf.text
    if pat.search(s): f.write(f"{round(e.dxf.insert.x)} {round(e.dxf.insert.y)} | {s[:400]}\n")
