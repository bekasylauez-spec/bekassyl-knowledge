import fitz,sys
d=fitz.open('sec5.pdf')
out=open('dc5/text_dump.txt','w',encoding='utf8')
for i,p in enumerate(d):
    out.write('=== PAGE %d\n'%(i+1))
    for b in p.get_text('blocks'):
        out.write('%d,%d,%d,%d | %s\n'%(b[0],b[1],b[2],b[3],b[4].replace('\n',' / ')))
    p.get_pixmap(dpi=80).save('dc5/p%02d_80.png'%(i+1))
