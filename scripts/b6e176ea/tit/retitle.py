# -*- coding: utf-8 -*-
# РПЗ title pages: keep the РПЗ's own style, replace only the company and the object address with those of the КМ album (DWG).
# Usage: python -X utf8 retitle.py "<src.docx>" "<dst.docx>"
import sys
import docx

COMPANY = ('ТОО "VSN"', 'ТОО "RAS Group Project"')
LICENSE = ("ГСЛ № 08109", "ГСЛ № 08854")
OBJECT = ("Многоквартирный жилой комплекс со встроенными, встроенно-пристроенными помещениями, расположенный по адресу: "
          "обл. Алматинская, р-н Карасайский, с.о. Райымбекский, с. Абай, к.х. АКХ Райымбек, уч. 179Б, 1-я очередь "
          "строительства (без наружных инженерных сетей)")


def set_text(p, text):
    runs = p.runs
    runs[0].text = text
    for r in runs[1:]:
        r._element.getparent().remove(r._element)


def apply(src, dst):
    d = docx.Document(src)
    t = d.tables[0]
    n = 0
    for row in t.rows:
        for p in row.cells[0].paragraphs:
            s = p.text.strip()
            if s == COMPANY[0]:
                set_text(p, COMPANY[1]); n += 1
            elif s == LICENSE[0]:
                set_text(p, LICENSE[1]); n += 1
            elif s.startswith("Многоквартирный жилой комплекс"):
                set_text(p, OBJECT); n += 1
    assert n == 6, (src, n)
    d.save(dst)


if __name__ == "__main__":
    apply(sys.argv[1], sys.argv[2])
    print("ok", sys.argv[2])
