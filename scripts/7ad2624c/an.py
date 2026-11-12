import fitz,sys,re
d=fitz.open(sys.argv[1])
out=open("an.txt","w",encoding="utf-8")
for i,p in enumerate(d):
    t=p.get_text()
    out.write(f"\n=== {i+1} {p.rect.width/72*25.4:.0f}x{p.rect.height/72*25.4:.0f}\n"+t)
print(len(d))
