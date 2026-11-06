import gx, os, sys, fitz
def plot(win, name, dpi=190, media='ISO_full_bleed_A1_(841.00_x_594.00_MM)'):
    pdf=os.path.join(gx.S,'w',name+'.pdf')
    print(gx.run([{'t':'plotpdf','win':win,'file':pdf,'media':media}],'plot')[-300:])
    d=fitz.open(pdf); pg=d[0]; pix=pg.get_pixmap(dpi=dpi); png=os.path.join(gx.S,'w',name+'.png'); pix.save(png); return png
if __name__=='__main__':
    w=list(map(float,sys.argv[2:6])); print(plot(w,sys.argv[1],int(sys.argv[6]) if len(sys.argv)>6 else 100))
