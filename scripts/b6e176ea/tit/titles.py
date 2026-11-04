# -*- coding: utf-8 -*-
# РПЗ title pages (обложка + титул) taken from the КМ album covers (layouts «0»/«00»):
# RAS Group Project logo, object name, «РАБОЧИЙ ПРОЕКТ», album lines, signatures with the stamp.
# Usage: python -X utf8 titles.py "<rpz.docx>" "<album.pdf>" "<name line, e.g. Лестница ЛК-1.1>"
import copy, os, sys
import fitz
import docx
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

HERE = os.path.dirname(os.path.abspath(__file__))
GOST, ISO = "GOST Common", "ISOCPEUR"
OBJ = ["«Многоквартирный жилой комплекс со встроенными,",
       "встроенно-пристроенными помещениями, расположенный по адресу: обл.",
       "Алматинская, р-н Карасайский, с.о. Райымбекский, с. Абай, к.х. АКХ Райымбек,",
       "уч. 179Б, 1-я очередь строительства (без наружных инженерных сетей)»"]


def images(album):
    """Logo and the signature block (stamp + vector signatures + names) cut from the album PDF."""
    d = fitz.open(album)
    logo = os.path.join(HERE, "logo.png")
    sig = os.path.join(HERE, "sign.png")
    p0 = d[0]
    xref = [x[0] for x in p0.get_images(full=True)][0]
    pix = fitz.Pixmap(d, xref)
    if pix.alpha or pix.n > 3:
        pix = fitz.Pixmap(fitz.csRGB, pix)
    pix.save(logo)
    p1 = d[1]
    # signature block: find the «Генеральный директор» line and the stamp, crop everything to the right edge of the names
    st = [r for x in p1.get_images(full=True) for r in p1.get_image_rects(x[0]) if r.y0 > p1.rect.height * 0.5]
    lines = [l["bbox"] for b in p1.get_text("dict")["blocks"] if b["type"] == 0 for l in b["lines"]]
    y_city = max(bb[1] for bb in lines)
    sl = [bb for bb in lines if bb[1] > st[0].y0 - 20 and bb[1] < y_city - 5]
    x0 = min(bb[0] for bb in sl) - 4
    x1 = max(bb[2] for bb in sl) + 4
    y0 = min(st[0].y0, min(bb[1] for bb in sl)) - 4
    y1 = max(bb[3] for bb in sl) + 14
    p1.get_pixmap(dpi=300, clip=fitz.Rect(x0, y0, x1, y1)).save(sig)
    return logo, sig, (x1 - x0) / 72 * 2.54


def run(p, text, font, size, bold=False):
    r = p.add_run(text)
    r.font.name = font
    r.font.size = Pt(size)
    r.font.italic = True
    r.font.bold = bold
    r.font.color.rgb = RGBColor(0, 0, 0)
    rpr = r._element.get_or_add_rPr()
    rf = rpr.find(qn("w:rFonts"))
    for a in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rf.set(qn(a), font)
    return r


def para(cell, text="", font=GOST, size=11, before=0, after=0, align=WD_ALIGN_PARAGRAPH.CENTER):
    p = cell.add_paragraph()
    p.style = cell.part.document.styles["Normal"]
    f = p.paragraph_format
    f.alignment = align
    f.space_before = Pt(before)
    f.space_after = Pt(after)
    f.line_spacing = 1.0
    f.first_line_indent = Cm(0)
    f.left_indent = Cm(0)
    f.right_indent = Cm(0)
    if text:
        run(p, text, font, size)
    return p


def fill(cell, name, logo, sig, sig_w, titul):
    for el in list(cell._tc):
        if el.tag != qn("w:tcPr"):
            cell._tc.remove(el)
    p = para(cell, before=18)
    p.add_run().add_picture(logo, width=Cm(2.6))
    para(cell, 'ТОО "RAS Group Project" г. Алматы', size=8, before=2)
    para(cell, "ГСЛ № 08854", size=8)
    for i, t in enumerate(OBJ):
        para(cell, t, size=12.5, before=40 if i == 0 else 3)
    para(cell, "РАБОЧИЙ ПРОЕКТ", size=21, before=44, after=6)
    para(cell, "9-этажный жилой дом со встроенными помещениями", size=11.5)
    para(cell, "общественного назначения", size=11.5, before=3)
    for i, t in enumerate([name, "Конструкции металлические", "Расчетно-пояснительная записка", "Том-4", "Альбом: 3669-1-КМ"]):
        para(cell, t, font=ISO, size=12.5, before=10 if i == 0 else 5)
    if titul:
        p = para(cell, before=40, align=WD_ALIGN_PARAGRAPH.RIGHT)
        p.paragraph_format.right_indent = Cm(0.3)
        p.add_run().add_picture(sig, width=Cm(min(sig_w * 0.62, 11.0)))
        city_before = 60
    else:
        city_before = 150
    para(cell, "Алматы 2026г.", size=10.5, before=city_before, after=6)


def apply(path, album, name):
    logo, sig, sig_w = images(album)
    d = docx.Document(path)
    t = d.tables[0]
    assert len(t.rows) == 2 and "ГСЛ" in t.rows[0].cells[0].text, path
    for i, row in enumerate(t.rows):
        fill(row.cells[0], name, logo, sig, sig_w, titul=(i == 1))
    # the table of contents always starts on its own page after the two title pages
    sdt = t._tbl.getnext()
    while sdt is not None and sdt.tag != qn("w:sdt"):
        sdt = sdt.getnext()
    p = sdt.find(".//" + qn("w:p"))
    ppr = p.find(qn("w:pPr"))
    if ppr is None:
        ppr = p.makeelement(qn("w:pPr"), {})
        p.insert(0, ppr)
    if ppr.find(qn("w:pageBreakBefore")) is None:
        # schema order: pStyle, keepNext, keepLines, pageBreakBefore, ...
        pos = sum(1 for c in ppr if c.tag in (qn("w:pStyle"), qn("w:keepNext"), qn("w:keepLines")))
        ppr.insert(pos, ppr.makeelement(qn("w:pageBreakBefore"), {}))
    d.save(path)


if __name__ == "__main__":
    apply(sys.argv[1], sys.argv[2], sys.argv[3])
    print("ok", sys.argv[1])
