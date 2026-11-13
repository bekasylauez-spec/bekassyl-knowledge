import fitz,sys
d=fitz.open(sys.argv[1])
print(len(d))
for t in d.get_toc(): print("TOC",t)
for i,p in enumerate(d):
    r=p.rect; fonts=set(f[3] for f in p.get_fonts())
    print(i+1, round(r.width/72*25.4), round(r.height/72*25.4), len(p.get_text("words")), fonts)
