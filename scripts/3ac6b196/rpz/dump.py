import sys; sys.stdout.reconfigure(encoding="utf-8")
import docx, sys
d = docx.Document(sys.argv[1])
body = d.element.body
from docx.table import Table
from docx.text.paragraph import Paragraph
i=0
for el in body.iterchildren():
    tag = el.tag.split('}')[1]
    if tag=='p':
        p = Paragraph(el, d)
        pics = len(el.findall('.//{http://schemas.openxmlformats.org/drawingml/2006/main}blip'))
        t = p.text.strip()
        if t or pics: print(i, '[%s]'%p.style.name, ('<PIC%d> '%pics if pics else '')+t[:300])
    elif tag=='tbl':
        t = Table(el, d)
        print(i, 'TABLE %dx%d'%(len(t.rows), len(t.columns)))
        for r in t.rows[:40]:
            try: print('   |', ' | '.join(c.text.strip().replace('\n',' / ')[:40] for c in r.cells))
            except Exception as e: print('   err', e)
    i+=1
print('sections', len(d.sections))
for s in d.sections: print(s.page_width, s.page_height, s.orientation, s.left_margin, s.top_margin)
