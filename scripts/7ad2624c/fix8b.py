import re
root = 'D:\\Бекасыл КЖ КМ\\Завод_В113_КМ\\_авто\\'
# 1) sec lib: +6.200 head on the left like the others (stagger handles 6.200 / 6.450)
p = root + 'v113_sec_lib.cs'; s = open(p, encoding='utf-8').read()
a = 'bool right = l.Name.StartsWith("+6.200");'
assert a in s; s = s.replace(a, 'bool right = false;   /* 13.11: +6.200 on the right hit the notes of sheet 8 */', 1)
open(p, 'w', encoding='utf-8').write(s)
# 2) secs: notes bottom 3 mm above the schedule top (measured after creation)
p = root + 'v113_secs.cs'; s = open(p, encoding='utf-8').read()
i = s.index('TextNote.Create(d, s8.Id, new XYZ(bb.Max.X - 190 * M, sbb.Max.Y + 37 * M, 0), 185 * M,')
s = s[:i] + 'var ntn = ' + s[i:]
j = s.index('VerticalAlignment = VerticalTextAlignment.Top });', i) + len('VerticalAlignment = VerticalTextAlignment.Top });')
s = s[:j] + '\n          d.Regenerate(); { var nb = ntn.get_BoundingBox(s8); if (nb != null) ElementTransformUtils.MoveElement(d, ntn.Id, new XYZ(0, sbb.Max.Y + 3 * M - nb.Min.Y, 0)); }   // 13.11: bottom 3 mm over the schedule' + s[j:]
open(p, 'w', encoding='utf-8').write(s)
# 3) plans: lower ridge Пр1 label — shifted along the purlin and between the ridge pair and the next purlin label
p = root + 'v113_plans.cs'; s = open(p, encoding='utf-8').read()
a = 'new XYZ(0, c.Y > 6000 ? off : -(off + 1000), 0) : nrm * off)'
assert a in s
s = s.replace(a, 'new XYZ(c.Y > 6000 ? 0 : 1800, c.Y > 6000 ? off : -(off + 870), 0) : nrm * off)', 1)
open(p, 'w', encoding='utf-8').write(s)
print('ok')
