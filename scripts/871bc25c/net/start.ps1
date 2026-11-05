$net = "C:\Users\Admin\AppData\Local\Temp\claude\210ab68cad67e8c1\871bc25c-1995-48d6-a9cc-b596c8ecdf97\scratchpad\net"
$acadDir = "C:\Program Files\Autodesk\AutoCAD 2021"
$dwg = "D:\РАБОЧКА\От Маке\Завод\АБК\КЖ Чертеж АБК.dwg"
$dll = Join-Path $net ("ablisten_" + (Get-Date -Format HHmmssfff) + ".dll")
& "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe" /nologo /target:library /platform:x64 /r:"$acadDir\accoremgd.dll" /r:"$acadDir\acdbmgd.dll" /r:"$acadDir\acmgd.dll" /out:"$dll" "$net\ablisten.cs" | Out-Host
if ($LASTEXITCODE -ne 0) { throw "compile failed" }
$scr = "(setvar `"FILEDIA`" 0)`r`n(setvar `"SECURELOAD`" 0)`r`n_.NETLOAD`r`n$dll`r`nABLISTEN`r`n"
[IO.File]::WriteAllText("$net\boot.scr", $scr, [Text.Encoding]::Default)
New-Item -ItemType Directory -Force "$env:TEMP\acadjob_ab" | Out-Null
Remove-Item "$env:TEMP\acadjob_ab\*" -ErrorAction SilentlyContinue
$p = Start-Process "$acadDir\acad.exe" -ArgumentList "`"$dwg`" /nologo /b `"$net\boot.scr`"" -PassThru
Set-Content "$net\pid.txt" $p.Id
for ($i = 0; $i -lt 240 -and -not (Test-Path "$env:TEMP\acadjob_ab\listening.txt"); $i++) { Start-Sleep 1 }
"pid " + $p.Id + " listening: " + (Test-Path "$env:TEMP\acadjob_ab\listening.txt")
