sp = r'C:\Users\Admin\AppData\Local\Temp\claude\a7137524bdaa49d0\c55bc92b-0511-4932-9c00-c1294111057c\scratchpad' + chr(92)
s=open('rmc_01b_test_planes.cs',encoding='utf-8').read()
s=s.replace('string outDir = @"D:' + chr(92) + '_claude_work' + chr(92) + 'RMC' + chr(92) + 'revit' + chr(92) + 'fam' + chr(92) + '";','string outDir = @"'+sp+'";')
open('rmc_01b_test_planes.cs','w',encoding='utf-8').write(s)
t=open('t_fam2.cs',encoding='utf-8').read()
t=t.replace('string fam = @"D:' + chr(92) + '_claude_work' + chr(92) + 'RMC' + chr(92) + 'revit' + chr(92) + 'fam' + chr(92) + '";','string fam = @"'+sp+'";')
for a in ('Б1','Б3','Б5L5804'):
    t=t.replace('"РМЦ_%s_двутавр_сварной.rfa"'%a,'"TEST_%s_двутавр_сварной.rfa"'%a)
open('t_fam3.cs','w',encoding='utf-8').write(t)
