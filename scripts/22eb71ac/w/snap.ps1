param([string]$Scr)
$s = "C:\Users\Admin\AppData\Local\Temp\claude\D---------\22eb71ac-88c3-4c99-9c61-2c7547468f19\scratchpad"
Start-Process "C:\Program Files\Autodesk\AutoCAD 2021\accoreconsole.exe" -ArgumentList "/i `"$s\w\snap.dwg`" /s `"$Scr`" /l ru-RU" -Wait -NoNewWindow -RedirectStandardOutput "$s\pl\plot.log" | Out-Null
