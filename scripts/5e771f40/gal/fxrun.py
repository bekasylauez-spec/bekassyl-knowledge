p = r'C:\Users\Admin\AppData\Local\Temp\claude\210ab68cad67e8c1\5e771f40-144d-493e-a1c3-679c0085cfb9\scratchpad\gal\net\run.ps1'
s = open(p, encoding='utf-8-sig').read()
i = s.index('$tagd = '); j = s.index('[IO.File]::WriteAllText($scr')
s = s[:i] + '$tagd = [IO.Path]::GetFileNameWithoutExtension($Dwg); $scr = "$SP\\net\\run_${name}_$tagd.scr"\n' + s[j:]
open(p, 'w', encoding='utf-8-sig').write(s)
print(s.splitlines()[11])
