import re,glob,os,sys
root=r"D:\РАБОЧКА\База_КМ\01_Объекты"
fs=[f for f in glob.glob(root+r"\**\паспорт.md",recursive=True) if "КЖ" not in f]
excl=re.compile(r'(?i)баз|связ|распор|прогон|подкранов|фахверк|лестниц|площад|расход|спецификац|состав альбома|примечан|^#+ *1\.|объект$|арматур|крыльц|ограж|прочее')
incl=re.compile(r'(?i)оголов|опиран|стык|ферм|балк|ригел|геометр|элемент|вывод|каркас|противореч|не прочит|узл|закономер|брать|ведомост|колонн')
out=open("ext.md","w",encoding="utf-8")
for f in sorted(fs):
    L=open(f,encoding="utf-8").read().split("\n")
    name=os.path.relpath(f,root)
    out.write(f"\n\n######## {name}\n")
    keep=False
    for i,l in enumerate(L):
        m=re.match(r'^(#{1,4}) +(.*)',l)
        if m:
            h=m.group(2)
            if len(m.group(1))==1: keep=True
            elif excl.search(h) and not re.search(r'(?i)оголов|ригел|ферм|стык',h): keep=False
            elif incl.search(h): keep=True
            else: keep=False
        if keep: out.write(l+"\n")
out.close()
print(os.path.getsize("ext.md"))
