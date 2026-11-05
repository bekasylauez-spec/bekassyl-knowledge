$net = "C:\Users\Admin\AppData\Local\Temp\claude\210ab68cad67e8c1\dcadf7f6-8c14-4657-945c-bf48b0ae9a19\scratchpad\net"
$acadDir = "C:\Program Files\Autodesk\AutoCAD 2021"
$dwg = "D:\РАБОЧКА\От Маке\Завод\Аэротенк\КЖ Аэротенк.dwg"
$dll = Join-Path $net ("aelisten_" + (Get-Date -Format HHmmssfff) + ".dll")
& "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe" /nologo /target:library /platform:x64 /r:"$acadDir\accoremgd.dll" /r:"$acadDir\acdbmgd.dll" /r:"$acadDir\acmgd.dll" /out:"$dll" "$net\ablisten.cs" | Out-Host
if ($LASTEXITCODE -ne 0) { throw "compile failed" }
$scr = "(setvar `"FILEDIA`" 0)`r`n(setvar `"SECURELOAD`" 0)`r`n_.NETLOAD`r`n$dll`r`nAELISTEN`r`n"
[IO.File]::WriteAllText("$net\boot.scr", $scr, [Text.Encoding]::Default)
New-Item -ItemType Directory -Force "$env:TEMP\acadjob_ae" | Out-Null
Remove-Item "$env:TEMP\acadjob_ae\*" -ErrorAction SilentlyContinue
$p = Start-Process "$acadDir\acad.exe" -ArgumentList "`"$dwg`" /nologo /b `"$net\boot.scr`"" -PassThru
Set-Content "$net\pid.txt" $p.Id
for ($i = 0; $i -lt 300 -and -not (Test-Path "$env:TEMP\acadjob_ae\listening.txt"); $i++) { Start-Sleep 1 }
"pid " + $p.Id + " listening: " + (Test-Path "$env:TEMP\acadjob_ae\listening.txt")
