s=open('gen_nodes.py',encoding='utf-8').read()
s=s.replace("""        if '{SIDE}' in mdir: mdir = '" + (bx%d ? "-Y" : "-X") + "' % gi
        mdir_s = ('"%s"' % mdir) if '{' not in mdir and '"' not in mdir else '(bx%d ? "-Y" : "-X")' % gi""","""        mdir_s = ('(bx%d ? "-Y" : "-X")' % gi) if '{SIDE}' in mdir else ('"%s"' % mdir)""")
s=s.replace("шаг I25Б1 на верхнем поясе ПБ1","упор из I25Б1 на верхнем поясе ПБ1")
open('gen_nodes.py','w',encoding='utf-8').write(s)
