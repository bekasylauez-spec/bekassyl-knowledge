import sys, fitz
# crop.py pdf out dpi wx0 wy0 wx1 wy1  (plot window) X0 Y0 X1 Y1 (model crop)
pdf,out,dpi=sys.argv[1],sys.argv[2],int(sys.argv[3])
wx0,wy0,wx1,wy1,X0,Y0,X1,Y1=map(float,sys.argv[4:12])
d=fitz.open(pdf); p=d[0]; R=p.rect
s=min(R.width/(wx1-wx0), R.height/(wy1-wy0))
ox=(R.width-(wx1-wx0)*s)/2; oy=(R.height-(wy1-wy0)*s)/2
clip=fitz.Rect(ox+(X0-wx0)*s, oy+(wy1-Y1)*s, ox+(X1-wx0)*s, oy+(wy1-Y0)*s)
pix=p.get_pixmap(dpi=dpi,clip=clip); pix.save(out); print(pix.width,pix.height)
