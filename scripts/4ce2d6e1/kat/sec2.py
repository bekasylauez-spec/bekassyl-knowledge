import re,glob,os,io,sys
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
root=r"D:\РАБОЧКА\База_КМ\01_Объекты"
for key in ["Магазин","Склад 2020","Тойота","Хьюндай","Цех","КМ Блок 1\\","КМ Блок 2\\","КМ Блок 3","КМ Блок 4","1А","1Б","1В","1Г","1Е","Колеса","Булакты"]:
    f=[x for x in glob.glob(root+r"\**\паспорт.md",recursive=True) if key in x and "КЖ" not in x][0]
    t=open(f,encoding="utf-8").read()
    m=re.search(r'\n## 2\..*?(?=\n## 3)',t,re.S)
    s=m.group(0) if m else ''
    rows=[l for l in s.split("\n") if l.startswith("|") and re.search(r'M_\d',l)]
    print("==",key)
    for r in rows:
        c=[x.strip() for x in r.strip('|').split('|')]
        print("  ",' | '.join(c[:3])[:110])
