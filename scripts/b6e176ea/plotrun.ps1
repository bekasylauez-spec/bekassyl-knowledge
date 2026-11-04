param([string]$Scr, [string]$Dwg, [string]$Prefix = "t", [int]$Dpi = 220)
$s = "C:\Users\Admin\AppData\Local\Temp\claude\D---------\b6e176ea-26b4-4762-a290-80708f71b8b2\scratchpad"
Start-Process "C:\Program Files\Autodesk\AutoCAD 2021\accoreconsole.exe" -ArgumentList "/i `"$Dwg`" /s `"$Scr`" /l ru-RU" -Wait -NoNewWindow -RedirectStandardOutput "$s\pl\plot.log" | Out-Null
Set-Location $s
python -X utf8 "$s\topng.py" $Prefix $Dpi
