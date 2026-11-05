param([string]$Layouts, [string]$OutDir = 'pdf2')
# plot listed layouts (comma-separated) of a fresh copy of the live DWG via accoreconsole -> w\<OutDir>\<layout>.pdf
$S = 'C:\Users\beka\AppData\Local\Temp\claude\61d567fc0ab17a45\92892291-7735-4e20-9a30-a83b0b257986\scratchpad\w'
New-Item -ItemType Directory -Force "$S\$OutDir" | Out-Null
Copy-Item 'D:\РАБОЧКА\От Маке\Завод\АБК\КЖ Чертеж АБК ВАРИАНТ 2.dwg' "$S\plotcopy.dwg" -Force
$scr = ''
foreach ($l in $Layouts.Split(',')) {
    Remove-Item "$S\$OutDir\$l.pdf" -ErrorAction SilentlyContinue
    $scr += "_-PLOT`r`n_N`r`n$l`r`n`r`nDWG To PDF.pc3`r`n$S\$OutDir\$l.pdf`r`n_N`r`n_Y`r`n"
}
$scr += "_.QUIT`r`n_Y`r`n"
[IO.File]::WriteAllText("$S\pl_fix.scr", $scr, [Text.Encoding]::GetEncoding(1251))
$p = Start-Process 'C:\Program Files\Autodesk\AutoCAD 2021\accoreconsole.exe' -ArgumentList "/i `"$S\plotcopy.dwg`" /s `"$S\pl_fix.scr`" /l ru-RU" -PassThru -WindowStyle Hidden
$p.WaitForExit(500000) | Out-Null
(Get-ChildItem "$S\$OutDir\*.pdf").Name -join ' '
