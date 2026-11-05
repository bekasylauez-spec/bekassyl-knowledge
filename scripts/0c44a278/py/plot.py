import subprocess, sys, os, fitz
S=r"C:\Users\beka\AppData\Local\Temp\claude\61d567fc0ab17a45\0c44a278-d609-485d-a50c-02efd03030b0\scratchpad"
def plot(dwg, name, x0, y0, x1, y1, paper='ISO без полей A1 (841.00 x 594.00 мм)', orient='_L'):
    pdf=S+r'\w\%s.pdf'%name
    scr="_.FILEDIA\n0\n_-PLOT\n_Y\nModel\nDWG To PDF.pc3\n%s\n_M\n%s\n_N\n_W\n%f,%f\n%f,%f\n_F\n_C\n_Y\nmonochrome.ctb\n_Y\n_A\n%s\n_N\n_Y\n_.QUIT\n_Y\n"%(paper,orient,x0,y0,x1,y1,pdf)
    open(S+r'\w\pl_%s.scr'%name,'w',encoding='cp1251').write(scr)
    if os.path.exists(pdf): os.remove(pdf)
    exe='C:/Program Files/Autodesk/AutoCAD 2021/accoreconsole.exe'
    subprocess.run([exe,'/i',dwg,'/s',S+r'\w\pl_%s.scr'%name,'/l','ru-RU'],capture_output=True,timeout=300)
    return pdf
def png(pdf, out, dpi=110, clip=None):
    d=fitz.open(pdf); p=d[0]
    if clip: r=p.rect; cl=fitz.Rect(r.width*clip[0],r.height*clip[1],r.width*clip[2],r.height*clip[3]); p.get_pixmap(dpi=dpi,clip=cl).save(out)
    else: p.get_pixmap(dpi=dpi).save(out)
if __name__=='__main__':
    dwg,name=sys.argv[1],sys.argv[2]; x0,y0,x1,y1=map(float,sys.argv[3:7])
    dpi=int(sys.argv[7]) if len(sys.argv)>7 else 110
    pdf=plot(dwg,name,x0,y0,x1,y1); png(pdf,S+r'\w\%s.png'%name,dpi)
