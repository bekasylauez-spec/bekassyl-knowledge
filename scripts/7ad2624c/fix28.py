root = 'D:\\Бекасыл КЖ КМ\\Завод_В113_КМ\\_авто\\'
p = root + 'v113_hide_node_marks.cs'; s = open(p, encoding='utf-8').read()
old = '.Where(x => !keep.Contains(x.Name) && x.CanBeHidden(v))'
new = ('.Where(x => !keep.Contains(x.Name) && x.CanBeHidden(v) && !(s.SheetNumber.CompareTo("28") >= 0 && s.SheetNumber.Length == 2 && '
       '(x.Name == "Узел 11" || x.Name == "Узел 12" || x.Name == "Узел 12а")))   /* 13.11: the фахверк node marks 11 / 12 / 12а stay on the elevations 28–31 */')
assert old in s; s = s.replace(old, new, 1); open(p, 'w', encoding='utf-8').write(s)
p = root + 'v113_secs.cs'; s = open(p, encoding='utf-8').read()
old = 'Levels = lvT, Cx = 140, Cy = 175'
assert old in s; s = s.replace(old, 'Levels = lvT, Cx = 150, Cy = 175', 1); open(p, 'w', encoding='utf-8').write(s)
print('ok')
