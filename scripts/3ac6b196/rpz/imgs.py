import sys; sys.stdout.reconfigure(encoding="utf-8")
import docx, os
d = docx.Document(sys.argv[1]); out=sys.argv[2]; os.makedirs(out, exist_ok=True)
A='{http://schemas.openxmlformats.org/drawingml/2006/main}blip'
R='{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed'
n=0
for i,el in enumerate(d.element.body.iterchildren()):
    for b in el.iter(A):
        rid=b.get(R); part=d.part.related_parts[rid]
        ext=os.path.splitext(part.partname)[1]
        n+=1; fn='%03d_e%04d%s'%(n,i,ext)
        open(os.path.join(out,fn),'wb').write(part.blob)
        txt=''.join(t.text or '' for t in el.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'))[:60]
        print(fn, len(part.blob), txt)
