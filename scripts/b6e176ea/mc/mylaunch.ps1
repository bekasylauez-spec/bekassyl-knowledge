$dwg = "D:\РАБОЧКА\От Рас груп\ЖК Қарасу село Абай\КМ Чертеж\КМ Чертеж Навес 1 Рампа.dwg"
if (Test-Path ($dwg -replace '\.dwg$','.dwl')) { "OPEN ELSEWHERE"; exit }
$jd = Join-Path $env:TEMP "acadjob_lk"
Remove-Item "$jd\listening.txt","$jd\job.txt","$jd\done.txt" -ErrorAction SilentlyContinue
$scr = Join-Path $PSScriptRoot "myboot.scr"
$p = Start-Process -FilePath "C:\Program Files\Autodesk\AutoCAD 2021\acad.exe" -ArgumentList @("`"$dwg`"","/nologo","/b","`"$scr`"") -WindowStyle Minimized -PassThru
"pid " + $p.Id
Set-Content (Join-Path $PSScriptRoot "mypid.txt") $p.Id
for ($i = 0; $i -lt 240 -and -not (Test-Path "$jd\listening.txt"); $i++) { Start-Sleep 1 }
if (Test-Path "$jd\listening.txt") { "listening: " + (Get-Content "$jd\listening.txt") } else { "timeout" }
