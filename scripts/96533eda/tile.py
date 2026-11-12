import fitz,sys
S='C:/Users/beka/AppData/Local/Temp/claude/61d567fc0ab17a45/96533eda-cf0e-4a1d-a01c-2f95091abb51/scratchpad/v/'
d=fitz.open('D:/_claude_work/v113_b1/out/album.pdf')
pg=int(sys.argv[1]); nx=int(sys.argv[2]); ny=int(sys.argv[3]); dpi=int(sys.argv[4]) if len(sys.argv)>4 else 190
p=d[pg-1]; r=p.rect
for j in range(ny):
  for i in range(nx):
    c=fitz.Rect(r.x0+r.width*i/nx, r.y0+r.height*j/ny, r.x0+r.width*(i+1)/nx, r.y0+r.height*(j+1)/ny)
    c=c+(-8,-8,8,8)
    p.get_pixmap(dpi=dpi,clip=c&r).save(S+f'p{pg}_{i}{j}.png')
