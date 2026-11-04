# -*- coding: utf-8 -*-
# Copy the built РПЗ (без СВ2, НТП) into «По НТП Без связей\Расчет», update fields/TOC in Word and export PDF.
import os, shutil, win32com.client as w

HERE = os.path.dirname(os.path.abspath(__file__))
R = r"D:\РАБОЧКА\От Рас груп\ЖК Қарасу село Абай\По НТП Без связей\Расчет"
os.makedirs(R, exist_ok=True)
wd = w.Dispatch("Word.Application"); wd.Visible = False
for al in ("1.1", "1.2", "2"):
    name = "РПЗ_Навес для ЛК %s" % al.replace(".", ",")
    dst = os.path.join(R, name + ".docx")
    shutil.copyfile(os.path.join(HERE, "n_lk" + al, "rpz", name + ".docx"), dst)
    d = wd.Documents.Open(dst)
    d.Fields.Update()
    if d.TablesOfContents.Count:
        d.TablesOfContents(1).Update()
    d.Save()
    d.SaveAs2(os.path.join(R, name + ".pdf"), FileFormat=17)
    print(name, "pages", d.ComputeStatistics(2))
    d.Close(False)
wd.Quit()
