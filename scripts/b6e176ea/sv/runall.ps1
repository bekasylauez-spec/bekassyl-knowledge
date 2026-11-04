param([string]$A, [string]$Src)
# СВ2 for one album: console part (tables/texts) -> sv\k$A.dwg, then SPDS part in my own AutoCAD, save, plot sheets 1,2,4,6
$s = "C:\Users\Admin\AppData\Local\Temp\claude\D---------\b6e176ea-26b4-4762-a290-80708f71b8b2\scratchpad"
$sv = "$s\sv"
$old = Get-Content "$s\mc\svpid.txt" -ErrorAction SilentlyContinue
if ($old) { Stop-Process -Id $old -Force -ErrorAction SilentlyContinue; Start-Sleep 3 }
Remove-Item "$sv\k$A.dwl","$sv\k$A.dwl2" -Force -ErrorAction SilentlyContinue
Copy-Item $Src "$sv\w$A.dwg" -Force
Remove-Item "$sv\k$A.dwg" -Force -ErrorAction SilentlyContinue
"== console"
& "$s\net\run.ps1" -Ops "$sv\ops_con_$A.json" -Dwg "$sv\w$A.dwg"
if (-not (Test-Path "$sv\k$A.dwg")) { throw "console save failed" }
"== live"
& "$s\mc\svlaunch.ps1" -Dwg "$sv\k$A.dwg"
Remove-Item "$env:TEMP\rn_map.json" -ErrorAction SilentlyContinue
& "$s\mc\svjob.ps1" -Ops "$sv\ops_live_$A.json" -Target "k$A.dwg" -Wait 500 | Select-String "ERR|done|OK"
& "$s\mc\svjob.ps1" -Ops "$sv\save.json" -Target "k$A.dwg" | Select-String "saved|ERR"
Stop-Process -Id (Get-Content "$s\mc\svpid.txt") -Force -ErrorAction SilentlyContinue; Start-Sleep 3
Remove-Item "$sv\k$A.dwl","$sv\k$A.dwl2" -Force -ErrorAction SilentlyContinue
"== plot"
$pre = "k" + ($A -replace '\.', '')
python -X utf8 "$sv\mkplot_sv.py" $pre "1,2,4,6"
Copy-Item "$sv\k$A.dwg" "$sv\k${A}p.dwg" -Force
Start-Process "C:\Program Files\Autodesk\AutoCAD 2021\accoreconsole.exe" -ArgumentList "/i `"$sv\k${A}p.dwg`" /s `"$sv\plot_$pre.scr`" /l ru-RU" -Wait -NoNewWindow -RedirectStandardOutput "$sv\plot.log" | Out-Null
Get-ChildItem $sv -Filter "pl_${pre}_*" | Select-Object Name, Length, LastWriteTime
