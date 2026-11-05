import sys,os,subprocess,shutil
P=r'C:\Users\Admin\AppData\Local\Temp\claude\210ab68cad67e8c1\2ce8f87a-4a49-4808-8cfa-d9a5f578e5ce\scratchpad\an'
hs=sys.argv[1:]
src=os.path.join(P,'..','w','snap.dwg'); t=os.path.join(P,'pt.dwg'); shutil.copy(src,t)
pdf=os.path.join(P,'pt.pdf')
if os.path.exists(pdf): os.remove(pdf)
er=''.join('(if (handent "%s") (entdel (handent "%s")))\n'%(h,h) for h in hs)
scr=('(setvar "FILEDIA" 0)\n'+er+'_-PLOT\n_Y\nModel\nDWG To PDF.pc3\nISO без полей A3 (420.00 x 297.00 мм)\n_M\n_L\n_N\n_W\n172179,455939\n203679,470789\n_F\n_C\n_Y\nmonochrome.ctb\n_Y\n_A\n%s\n_N\n_Y\n_.QUIT\n_Y\n'%pdf.replace(os.sep,'/'))
open(os.path.join(P,'pt.scr'),'w',encoding='cp1251').write(scr)
subprocess.run(['powershell','-ExecutionPolicy','Bypass','-File',os.path.join(P,'run.ps1'),t,os.path.join(P,'pt.scr'),os.path.join(P,'pt.log')])
print('PDF' if os.path.exists(pdf) else 'FAIL')
