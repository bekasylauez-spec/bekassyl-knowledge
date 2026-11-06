param([string]$In,[string]$Out)
$acc="C:\Program Files\Autodesk\AutoCAD 2021\accoreconsole.exe"
$tmp=Join-Path $env:TEMP ("mb3c_"+[guid]::NewGuid().ToString('N').Substring(0,8)); New-Item -ItemType Directory $tmp|Out-Null
$c=Join-Path $tmp "in.dwg"; Copy-Item -LiteralPath $In $c
$scr=Join-Path $tmp "s.scr"; [IO.File]::WriteAllText($scr,"(setvar `"FILEDIA`" 0)`r`n_.DXFOUT`r`n`"$Out`"`r`n_V`r`n2018`r`n16`r`n_.QUIT`r`n_Y`r`n",[Text.Encoding]::Default)
& $acc /i $c /s $scr /l ru-RU | Out-Null
Remove-Item -Recurse -Force $tmp
if(Test-Path $Out){"ok "+(Get-Item $Out).Length}else{"FAIL"}
