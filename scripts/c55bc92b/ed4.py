import io
p=r"D:/Бекасыл КЖ КМ/РМЦ_КМ/_авто/rmc_92_baza_check.cs"
s=io.open(p,encoding='utf-8').read()
a='for (int i = 0; i < rowsBy[loc].Count; i++) if (rowsBy[loc][i].StartsWith("подколонник: габарит")'
assert s.count(a)==1
s=s.replace(a,'for (int i = 0; i < rowsBy[loc].Count; i++) { if (rowsBy[loc][i].StartsWith("подколонник: габарит")')
b='diffs.Add(loc + ": " + rowsBy[loc][i] + "  (≠ " + refLoc + ": " + rowsBy[refLoc][i].Split(\'\t\')[1] + ")"); }'
assert s.count(b)==1
s=s.replace(b,b+' }')
io.open(p,'w',encoding='utf-8',newline='').write(s)
