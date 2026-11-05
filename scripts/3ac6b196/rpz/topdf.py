import sys, os, win32com.client
src = os.path.abspath(sys.argv[1]); pdf = os.path.abspath(sys.argv[2]); upd = len(sys.argv) > 3
w = win32com.client.DispatchEx('Word.Application'); w.Visible = False
d = w.Documents.Open(src, ReadOnly=not upd)
if upd:
    for t in d.TablesOfContents: t.Update()
    d.Fields.Update(); d.Save()
d.ExportAsFixedFormat(pdf, 17)
print('pages', d.ComputeStatistics(2))
d.Close(False); w.Quit()
