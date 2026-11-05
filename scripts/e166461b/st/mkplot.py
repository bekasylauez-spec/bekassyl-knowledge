import json, sys
F=json.load(open('frames.json')); S=r"C:\Users\Admin\AppData\Local\Temp\claude\210ab68cad67e8c1\e166461b-bde0-4f75-9345-660eafbd0735\scratchpad\st"
for n in sys.argv[1:]:
    scr=''
    for i,(x0,y0,x1,y1,s) in enumerate(F[n]):
        w,h=x1-x0,y1-y0; land=w>h
        pap='ISO без полей A2 (594.00 x 420.00 мм)' if max(w,h)/s<60000 else 'ISO без полей A1 (841.00 x 594.00 мм)'
        if max(w,h)/s<43000: pap='ISO без полей A3 (420.00 x 297.00 мм)'
        scr+="_-PLOT\n_Y\nModel\nDWG To PDF.pc3\n%s\n_M\n%s\n_N\n_W\n%f,%f\n%f,%f\n_F\n_C\n_Y\nmonochrome.ctb\n_Y\n_A\n%s\%s_%02d.pdf\n_N\n_Y\n"%(pap,'_L' if land else '_P',x0,y0,x1,y1,S,n,i)
    scr+="_.QUIT\n_Y\n"
    open('pl_%s.scr'%n,'w',encoding='cp1251').write(scr)
