$net = Split-Path -Parent $MyInvocation.MyCommand.Path
$jd = Join-Path $env:TEMP "acadjob_b4"
foreach($f in "listening.txt","done.txt","job.txt"){ $q=Join-Path $jd $f; if(Test-Path $q){ [IO.File]::Delete($q) } }
$dwg = "D:\РАБОЧКА\От Шерхан\БДМ Блок 4\Б4.ригели.dwg"
$p = Start-Process "C:\Program Files\Autodesk\AutoCAD 2021\acad.exe" -ArgumentList "`"$dwg`" /nologo /b `"$net\boot.scr`"" -PassThru
for($i=0;$i -lt 200 -and -not (Test-Path "$jd\listening.txt");$i++){Start-Sleep 2}
$p.Id
