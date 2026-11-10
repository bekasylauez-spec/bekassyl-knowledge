W = [("04","888600,-274700","918400,-232600")]
P41 = {21:("2877215,-274700","2881515,-271630"),22:("2881415,-274700","2885715,-271630"),23:("2885615,-274700","2889915,-271630"),
 24:("2889815,-274700","2894115,-271630"),25:("2894015,-274700","2898315,-271630"),26:("2898200,-274700","2908800,-267200"),
 27:("2908700,-274700","2915100,-270150"),28:("2915015,-274700","2919315,-271630"),38:("3681850,-274700","3686150,-271630")}
for n in sorted(P41): W.append(("%02d"%n,)+P41[n])
for n in range(39,60):
    x=3686100+4200*(n-39); W.append(("%02d"%n,"%d,-274700"%(x-50),"%d,-271630"%(x+4250)))
s='(setvar "FILEDIA" 0)\n(setvar "BACKGROUNDPLOT" 0)\n'
for nm,a,b in W:
    s+="_-PLOT\n_Y\nModel\nDWG To PDF.pc3\nISO без полей A0 (841.00 x 1189.00 мм)\n_M\n_L\n_N\n_W\n%s\n%s\n_F\n_C\n_Y\nmonochrome.ctb\n_Y\n_A\nD:/_claude_work/zavod_km_uz/png/all/a%s.pdf\n_N\n_Y\n"%(a,b,nm)
s+='(setvar "FILEDIA" 1)\n_QUIT _Y\n'
open(r'D:\_claude_work\zavod_km_uz\pall.scr','w',encoding='cp1251',newline='\r\n').write(s)
print(len(W))
