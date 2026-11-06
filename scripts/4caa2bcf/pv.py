import plot, sys, gx
if sys.argv[1]=='snap': plot.snap(); sys.argv.pop(1)
n=sys.argv[1]; x0,y0,x1,y1=map(float,sys.argv[2:6]); paper=sys.argv[6] if len(sys.argv)>6 else 'ISO без полей A2 (594.00 x 420.00 мм)'
pdf=plot.plot(n,x0,y0,x1,y1,paper)
plot.png(pdf, gx.S+r'\w\%s.png'%n, int(sys.argv[7]) if len(sys.argv)>7 else 90)
print('ok')
