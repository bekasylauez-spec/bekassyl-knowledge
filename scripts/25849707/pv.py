import gx,sys,os,fitz,subprocess
P=gx.S+r'\pv'
def snap():
    import shutil
    f=os.path.join(P,'snap.dwg')
    out=gx.run([dict(t='save')],'sv')
    shutil.copy(r'D:\РАБОЧКА\От Шерхан\Бдм Блок 1\Б1.ригели.dwg', f)
    return out
def plot(name,x0,y0,x1,y1,paper='ISO без полей A3 (420.00 x 297.00 мм)',orient='_L',dpi=150,quarters=0,dosnap=True):
    if dosnap: snap()
    pdf=os.path.join(P,name+'.pdf')
    if os.path.exists(pdf): os.remove(pdf)
    scr=('(setvar "FILEDIA" 0)\n_-PLOT\n_Y\nModel\nDWG To PDF.pc3\n%s\n_M\n%s\n_N\n_W\n%f,%f\n%f,%f\n_F\n_C\n_Y\nmonochrome.ctb\n_Y\n_A\n%s\n_N\n_Y\n_.QUIT\n_Y\n'%(paper,orient,x0,y0,x1,y1,pdf.replace(os.sep,'/')))
    sp=os.path.join(P,'pl_'+name+'.scr'); open(sp,'w',encoding='cp1251').write(scr)
    subprocess.run(['powershell','-ExecutionPolicy','Bypass','-File',gx.S+r'\an\run.ps1',os.path.join(P,'snap.dwg'),sp,os.path.join(P,'pl_'+name+'.log')])
    d=fitz.open(pdf); p=d[0]; p.get_pixmap(dpi=dpi).save(os.path.join(P,name+'.png'))
    if quarters:
        r=p.rect; W,H=r.width,r.height
        for i,(a,b,c,e) in enumerate([(0,0,.52,.52),(.48,0,1,.52),(0,.48,.52,1),(.48,.48,1,1)]):
            p.get_pixmap(dpi=quarters,clip=fitz.Rect(W*a,H*b,W*c,H*e)).save(os.path.join(P,'%s_q%d.png'%(name,i)))
    return pdf
