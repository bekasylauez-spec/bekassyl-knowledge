import io
p = r"D:/_claude_work/RMC/kzh/kz86_all.ps1"
s = r'''# КЖ-4.x: әр рандбалка маркасы — жеке А2 парақ (kz86_rb.cs). Нәтиже: _тексеру\Парақ_КЖ-4-N_*.png
param([int]$From = 1, [int]$To = 9)
$ErrorActionPreference = 'Continue'
$dir = 'D:\_claude_work\RMC\kzh'
for ($n = $From; $n -le $To; $n++) {
    Set-Content -Path "$dir\kz86.txt" -Value ("sheet=КЖ-4.$n`r`nmark=Рб-$n") -Encoding utf8
    $out = & "$dir\rv.ps1" -File kz86_rb.cs -Wait 600 2>&1 | Out-String
    $sel = ($out -split "`n") | Where-Object { $_ -match 'run \(|WARN|err|fail|ERROR|error CS|groups|layout commit|png |Нет|Х1' }
    "==== КЖ-4.$n / Рб-$n ===="
    $sel
    Set-Content -Path "$dir\_kz86_4_$n.txt" -Value $out -Encoding utf8
}
'''
io.open(p, "w", encoding="utf-8-sig").write(s)
print("written", len(s))
