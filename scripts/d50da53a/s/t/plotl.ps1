param([string]$Dwg, [string]$Layouts, [string]$OutDir)
New-Item -ItemType Directory -Force $OutDir | Out-Null
$tmp = Join-Path $env:TEMP ("mb2p_" + [guid]::NewGuid().ToString('N').Substring(0,8)); New-Item -ItemType Directory $tmp | Out-Null
Copy-Item -LiteralPath $Dwg "$tmp\plotcopy.dwg" -Force
$scr = "(setvar `"FILEDIA`" 0)`r`n"
foreach ($l in $Layouts.Split(',')) {
    Remove-Item "$OutDir\$l.pdf" -ErrorAction SilentlyContinue
    $scr += "_-PLOT`r`n_N`r`n$l`r`n`r`nDWG To PDF.pc3`r`n$OutDir\$l.pdf`r`n_N`r`n_Y`r`n"
}
$scr += "_.QUIT`r`n_Y`r`n"
[IO.File]::WriteAllText("$tmp\pl.scr", $scr, [Text.Encoding]::GetEncoding(1251))
$p = Start-Process 'C:\Program Files\Autodesk\AutoCAD 2021\accoreconsole.exe' -ArgumentList "/i `"$tmp\plotcopy.dwg`" /s `"$tmp\pl.scr`" /l ru-RU" -PassThru -WindowStyle Hidden
$p.WaitForExit(900000) | Out-Null
Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue
(Get-ChildItem "$OutDir\*.pdf").Name -join ' '
