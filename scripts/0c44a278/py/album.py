import plot, fitz, os
S=plot.S+r'\w'
dwg=S+r'\b1_2.dwg'
A1='ISO без полей A1 (841.00 x 594.00 мм)'; A2='ISO без полей A2 (594.00 x 420.00 мм)'
sheets=[]
for k in range(1,7): x0=-791072+(k-1)*90000; sheets.append((x0,-3179400,x0+84100,-3120000,A1))
sheets.append((-251072,-3162000,-191672,-3120000,A2))
for k in range(1,5): x0=-791072+(k-1)*64000; sheets.append((x0,-3242000,x0+59400,-3200000,A2))
sheets.append((-535072,-3242000,-475672,-3200000,A2))
out=fitz.open()
for i,(a,b,c,d,p) in enumerate(sheets):
    pdf=plot.plot(dwg,'al%02d'%(i+1),a,b,c,d,paper=p)
    out.insert_pdf(fitz.open(pdf)); print(i+1,os.path.getsize(pdf))
out.save(S+r'\album.pdf'); print('pages',len(out))
