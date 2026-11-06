param([string]$Wins, [string]$Names, [string]$Media = 'ISO без полей A1 (841.00 x 594.00 мм)', [string]$Src = '', [string]$Orients = '', [string]$OutDir = 'C:\Users\Admin\AppData\Local\Temp\claude\210ab68cad67e8c1\6399190a-f172-4888-a7c9-e3d967ee3eb0\scratchpad\b3\k\w\pdf')

# Wins: "x0,y0,x1,y1;x0,y0,x1,y1"  Names: "2.1;2.2"  -> model-space window plots (Fit) of a wblock copy

$S = 'C:\Users\Admin\AppData\Local\Temp\claude\210ab68cad67e8c1\6399190a-f172-4888-a7c9-e3d967ee3eb0\scratchpad\b3\k\w'

New-Item -ItemType Directory -Force $OutDir | Out-Null

if ($Src -eq '') { $Src = "$S\plotcopy.dwg" }

$ws = $Wins.Split(';'); $ns = $Names.Split(';'); $ms = $Media.Split(';'); $os = $Orients.Split(';')

$scr = "(setvar `"FILEDIA`" 0)`r`n"

for ($i = 0; $i -lt $ws.Count; $i++) {

  $w = $ws[$i].Split(','); $f = "$OutDir\" + $ns[$i] + ".pdf"; Remove-Item $f -ErrorAction SilentlyContinue

  $md = if ($ms.Count -gt $i) { $ms[$i] } else { $ms[0] }

  $or = if (($os.Count -gt $i) -and ($os[$i] -eq "P")) { "_P" } else { "_L" }

  $scr += "_-PLOT`r`n_Y`r`nModel`r`nDWG To PDF.pc3`r`n$md`r`n_M`r`n$or`r`n_N`r`n_W`r`n" + $w[0] + "," + $w[1] + "`r`n" + $w[2] + "," + $w[3] + "`r`n_F`r`n_C`r`n_Y`r`nmonochrome.ctb`r`n_Y`r`n_A`r`n$f`r`n_N`r`n_Y`r`n"

}

$scr += "_.QUIT`r`n_Y`r`n"

[IO.File]::WriteAllText("$S\plotwin.scr", $scr, [Text.Encoding]::GetEncoding(1251))

$p = Start-Process 'C:\Program Files\Autodesk\AutoCAD 2021\accoreconsole.exe' -ArgumentList "/i `"$Src`" /s `"$S\plotwin.scr`" /l ru-RU" -PassThru -WindowStyle Hidden

$p.WaitForExit(600000) | Out-Null

(Get-ChildItem "$OutDir\*.pdf" | Where-Object { $_.LastWriteTime -gt (Get-Date).AddMinutes(-10) }).Name -join ' '

