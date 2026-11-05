import ab,subprocess,sys,fitz,os
S=r'C:\Users\Admin\AppData\Local\Temp\claude\210ab68cad67e8c1\dcadf7f6-8c14-4657-945c-bf48b0ae9a19\scratchpad'
def plot(items, media='ISO без полей A1 (841.00 x 594.00 мм)', copy=True, orients=None):
    """items: [(name,(x0,y0,x1,y1))]"""
    if copy: ab.run([{'t':'wblock','file':S+r'\w\plotcopy.dwg'}],'wb',300)
    wins=';'.join('%.0f,%.0f,%.0f,%.0f'%w for n,w in items); names=';'.join(n for n,w in items)
    meds=media if isinstance(media,str) else ';'.join(media)
    r=subprocess.run(['powershell','-ExecutionPolicy','Bypass','-File',S+r'\net\plotwin.ps1','-Wins',wins,'-Names',names,'-Media',meds]+(['-Orients',';'.join(orients)] if orients else []),capture_output=True)
    return r.stdout.decode('utf-8','replace')+r.stderr.decode('utf-8','replace')
def png(name,dpi=60,clip=None,out=None):
    d=fitz.open(S+r'\w\pdf\%s.pdf'%name);p=d[0]
    if clip:
        W,H=p.rect.width,p.rect.height
        c=fitz.Rect(clip[0]*W,clip[1]*H,clip[2]*W,clip[3]*H)
        pm=p.get_pixmap(dpi=dpi,clip=c)
    else: pm=p.get_pixmap(dpi=dpi)
    out=out or S+r'\w\pv\%s.png'%name.replace('.','_'); os.makedirs(os.path.dirname(out),exist_ok=True); pm.save(out); return out
if __name__=='__main__':
    print(plot([(sys.argv[1],tuple(map(float,sys.argv[2].split(','))))]))
    print(png(sys.argv[1]))
MED={(84100,59400):'ISO без полей A1 (841.00 x 594.00 мм)',(59400,42000):'ISO без полей A2 (594.00 x 420.00 мм)',(42000,29700):'ISO без полей A3 (420.00 x 297.00 мм)',
     (29700,21000):'ISO без полей A2 (594.00 x 420.00 мм)',(14850,10500):'ISO без полей A2 (594.00 x 420.00 мм)',(10500,7425):'ISO без полей A3 (420.00 x 297.00 мм)',(29700,42000):'ISO без полей A2 (594.00 x 420.00 мм)'}
MED[(21025,14850)]='ISO без полей A1 (841.00 x 594.00 мм)'
MED[(29700,42000)]='ISO без полей A3 (420.00 x 297.00 мм)'
MED[(10500,7425)]='ISO без полей A3 (420.00 x 297.00 мм)'
MED[(42000,59400)]='ISO без полей A2 (594.00 x 420.00 мм)'
