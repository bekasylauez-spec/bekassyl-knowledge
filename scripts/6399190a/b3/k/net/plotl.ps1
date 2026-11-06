param([string]$Layouts, [string]$OutDir)
$S = 'C:\Users\Admin\AppData\Local\Temp\claude\210ab68cad67e8c1\6399190a-f172-4888-a7c9-e3d967ee3eb0\scratchpad\b3\k\w'
New-Item -ItemType Directory -Force $OutDir | Out-Null
Copy-Item 'C:\Users\Admin\AppData\Local\Temp\claude\210ab68cad67e8c1\6399190a-f172-4888-a7c9-e3d967ee3eb0\scratchpad\b3\k\w\m3col.dwg' "$S\plotcopy2.dwg" -Force
$scr = "(setvar `"FILEDIA`" 0)`r`n"
foreach ($l in $Layouts.Split(',')) {
    $f = "$OutDir\$l.pdf"; Remove-Item $f -ErrorAction SilentlyContinue
    $scr += "_-PLOT`r`n_N`r`n$l`r`n`r`nDWG To PDF.pc3`r`n$f`r`n_N`r`n_Y`r`n"
}
$scr += "_.QUIT`r`n_Y`r`n"
[IO.File]::WriteAllText("$S\pl_lay.scr", $scr, [Text.Encoding]::GetEncoding(1251))
$p = Start-Process 'C:\Program Files\Autodesk\AutoCAD 2021\accoreconsole.exe' -ArgumentList "/i `"$S\plotcopy2.dwg`" /s `"$S\pl_lay.scr`" /l ru-RU" -PassThru -WindowStyle Hidden
$p.WaitForExit(1200000) | Out-Null
(Get-ChildItem "$OutDir\*.pdf").Count
