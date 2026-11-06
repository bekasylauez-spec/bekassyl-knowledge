param($dwg,$scr,$log)
$exe='C:\Program Files\Autodesk\AutoCAD 2021\accoreconsole.exe'
$p=Start-Process $exe -ArgumentList "/i `"$dwg`" /s `"$scr`" /l ru-RU" -PassThru -NoNewWindow -RedirectStandardOutput $log
$p | Wait-Process -Timeout 300 -ErrorAction SilentlyContinue; if (!$p.HasExited) { Stop-Process -Id $p.Id -Force; "killed" }
