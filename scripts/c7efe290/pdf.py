import fitz
d=fitz.open(r'D:\_claude_work\v113\src\copy\km.pdf')
print(len(d))
out=open(r'D:\_claude_work\v113\src\pdf\text.txt','w',encoding='utf-8')
for i,p in enumerate(d,1):
    p.get_pixmap(dpi=200).save(r'D:\_claude_work\v113\src\pdf\p%02d.png'%i)
    t=p.get_text()
    out.write('\n===== PAGE %d size %s =====\n'%(i,p.rect)+t)
    print(i,p.rect,len(t))
