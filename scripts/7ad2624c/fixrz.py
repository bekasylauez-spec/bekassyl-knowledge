p = r'D:\Бекасыл КЖ КМ\Завод_В113_КМ\_авто\v113_razv.cs'
s = open(p, encoding='utf-8').read()
old = 'try { d.Create.NewDimension(v, Line.CreateBound(Wp(srt.First().Item1, -500), Wp(srt.Last().Item1, -500)), ra2, dimT); nd++; } catch (Exception ex) { sb.AppendLine("  chain " + ex.Message); }'
new = ('try { var dch = d.Create.NewDimension(v, Line.CreateBound(Wp(srt.First().Item1, -500), Wp(srt.Last().Item1, -500)), ra2, dimT); nd++; d.Regenerate();\n'
       '          // 13.11 (checker: «2000600», «5002000» — short 500/600 numbers ran into the neighbours): numbers of segments < 1000 under the line\n'
       '          foreach (DimensionSegment sg in dch.Segments) if ((sg.Value ?? 0) / M < 1000) { try { sg.TextPosition = sg.TextPosition - v.UpDirection * (4.0 * v.Scale * M); } catch { } } }\n'
       '        catch (Exception ex) { sb.AppendLine("  chain " + ex.Message); }')
assert old in s
s = s.replace(old, new, 1)
open(p, 'w', encoding='utf-8').write(s)
print('ok')
