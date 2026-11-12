import fitz,sys
d=fitz.open(r'D:\Бекасыл КЖ КМ\Завод_В113_КМ\_тексеру\227-23-П-УВПиОС-ВП-В113-КМ.pdf')
pg=int(sys.argv[1]);dpi=int(sys.argv[2]);nx=int(sys.argv[3]);ny=int(sys.argv[4])
p=d[pg-1];W,H=p.rect.width,p.rect.height
for j in range(ny):
  for i in range(nx):
    r=fitz.Rect(i*W/nx-15 if i else 0,j*H/ny-15 if j else 0,min(W,(i+1)*W/nx+15),min(H,(j+1)*H/ny+15))
    p.get_pixmap(dpi=dpi,clip=r).save(rf'r2\p{pg:02d}_{j}{i}.png')
