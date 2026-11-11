import re,glob,os,io,sys
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
root=r"D:\РАБОЧКА\База_КМ\01_Объекты"
ext=open("ext.md",encoding="utf-8").read()
fs=[f for f in glob.glob(root+r"\**\паспорт.md",recursive=True) if "КЖ" not in f]
for f in sorted(fs):
    print("==",os.path.relpath(f,root))
    for l in open(f,encoding="utf-8"):
        m=re.match(r'^(#{2,4}) +(.*)',l)
        if m and l.strip() not in ext:
            print("  ",l.strip()[:150])
