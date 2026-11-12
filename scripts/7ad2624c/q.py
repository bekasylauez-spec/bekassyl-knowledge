import fitz,sys
d=fitz.open(r"D:\Бекасыл КЖ КМ\Завод_В113_КМ\227-23-П-УВПиОС-ВП-В113-КМ.pdf")
p=d[int(sys.argv[1])-1]; dpi=int(sys.argv[2]); n=int(sys.argv[3]) if len(sys.argv)>3 else 2
W,H=p.rect.width,p.rect.height
for a in range(n):
  for b in range(n):
    r=fitz.Rect(W*a/n-15*(a>0),H*b/n-15*(b>0),W*(a+1)/n+15*(a<n-1),H*(b+1)/n+15*(b<n-1))
    p.get_pixmap(dpi=dpi,clip=r).save(f"r/p{int(sys.argv[1]):02d}_{b}{a}.png")
