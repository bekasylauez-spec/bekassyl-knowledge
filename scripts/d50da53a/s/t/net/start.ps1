$net = "C:\Users\Admin\AppData\Local\Temp\claude\210ab68cad67e8c1\d50da53a-3ac3-4689-a264-f515b6d8bdb3\scratchpad\s\t\net"
$acadDir = "C:\Program Files\Autodesk\AutoCAD 2021"
$dwg = "D:\РАБОЧКА\От Маке\Завод\Маслоподготовка Блок 2\4.Колонна Блок 2.dwg"
$dll = Join-Path $net ("mb2listen_" + (Get-Date -Format HHmmssfff) + ".dll")
& "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe" /nologo /target:library /platform:x64 /r:"$acadDir\accoremgd.dll" /r:"$acadDir\acdbmgd.dll" /r:"$acadDir\acmgd.dll" /out:"$dll" "$net\ablisten.cs" | Out-Host
if ($LASTEXITCODE -ne 0) { throw "compile failed" }
$scr = "(setvar `"FILEDIA`" 0)`r`n(setvar `"SECURELOAD`" 0)`r`n_.NETLOAD`r`n$dll`r`nMB2LISTEN`r`n"
[IO.File]::WriteAllText("$net\boot.scr", $scr, [Text.Encoding]::Default)
New-Item -ItemType Directory -Force "$env:TEMP\acadjob_mb2" | Out-Null
Remove-Item "$env:TEMP\acadjob_mb2\*" -ErrorAction SilentlyContinue
$p = Start-Process "$acadDir\acad.exe" -ArgumentList "`"$dwg`" /nologo /b `"$net\boot.scr`"" -PassThru
Set-Content "$net\pid.txt" $p.Id
for ($i = 0; $i -lt 300 -and -not (Test-Path "$env:TEMP\acadjob_mb2\listening.txt"); $i++) { Start-Sleep 1 }
"pid " + $p.Id + " listening: " + (Test-Path "$env:TEMP\acadjob_mb2\listening.txt")
