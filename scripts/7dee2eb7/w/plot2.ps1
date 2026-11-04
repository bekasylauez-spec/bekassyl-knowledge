param([string]$Dwg,[string[]]$Scr)
foreach($s in $Scr){ $p=Start-Process "C:\Program Files\Autodesk\AutoCAD 2021\accoreconsole.exe" -ArgumentList "/i `"$Dwg`" /s `"$s`" /l ru-RU" -PassThru -WindowStyle Hidden; if(-not $p.WaitForExit(400000)){$p.Kill(); "timeout $s"} }
