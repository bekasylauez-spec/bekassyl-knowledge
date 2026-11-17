# Bash heredoc-тан түскен \r (CR) және жол ішіндегі нақты жаңа жолды (\n) C# мәтінінде қайта «\n» тізбегіне айналдыру
import io, sys
BS = chr(92)
base = r'D:\_claude_work\Kasymova\rvbi\rv\scripts\kas' + BS
# 1) slib.cs: жол ішіндегі CR
p = base + 'slib.cs'
b = open(p, 'rb').read()
bad = b'Kasymova\rvbi'
good = b'Kasymova' + bytes([92]) + b'rvbi'
print('slib CR fixes:', b.count(bad))
b = b.replace(bad, good)
open(p, 'wb').write(b)
# 2) r10, f10: "...сечениях." + (X != null ? "<NL>6. ВНИМАНИЕ..." -> "\n6. ВНИМАНИЕ..."
for fn, marker in (('r10_beam.cs', '6. ВНИМАНИЕ: " + dfc'), ('f10_found.cs', '6. ВНИМАНИЕ: " + Deficit')):
    p = base + fn
    s = io.open(p, encoding='utf-8', newline='').read()
    i = s.find(marker)
    assert i > 0, fn
    # маркердің алдындағы жаңа жол таңбалары (\r\n не \n) -> литерал \n
    j = i
    while s[j - 1] in '\r\n': j -= 1
    s = s[:j] + BS + 'n' + s[i:]
    io.open(p, 'w', encoding='utf-8', newline='').write(s)
    print(fn, 'fixed at', j)
