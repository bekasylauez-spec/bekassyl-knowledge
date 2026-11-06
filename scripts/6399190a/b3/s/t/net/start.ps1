$net = "C:\Users\Admin\AppData\Local\Temp\claude\210ab68cad67e8c1\6399190a-f172-4888-a7c9-e3d967ee3eb0\scratchpad\b3\s\t\net"
$acadDir = "C:\Program Files\Autodesk\AutoCAD 2021"
$dwg = "D:\РАБОЧКА\От Маке\Завод\Маслоподготовка Блок 3\4.Колонна Блок 3.dwg"
$dll = Join-Path $net ("mb3listen_" + (Get-Date -Format HHmmssfff) + ".dll")
& "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe" /nologo /target:library /platform:x64 /r:"$acadDir\accoremgd.dll" /r:"$acadDir\acdbmgd.dll" /r:"$acadDir\acmgd.dll" /out:"$dll" "$net\ablisten.cs" | Out-Host
if ($LASTEXITCODE -ne 0) { throw "compile failed" }
$scr = "(setvar `"FILEDIA`" 0)`r`n(setvar `"SECURELOAD`" 0)`r`n_.NETLOAD`r`n$dll`r`nMB3LISTEN`r`n"
[IO.File]::WriteAllText("$net\boot.scr", $scr, [Text.Encoding]::Default)
New-Item -ItemType Directory -Force "$env:TEMP\acadjob_mb3" | Out-Null
Remove-Item "$env:TEMP\acadjob_mb3\*" -ErrorAction SilentlyContinue
$p = Start-Process "$acadDir\acad.exe" -ArgumentList "`"$dwg`" /nologo /b `"$net\boot.scr`"" -PassThru
Set-Content "$net\pid.txt" $p.Id
for ($i = 0; $i -lt 300 -and -not (Test-Path "$env:TEMP\acadjob_mb3\listening.txt"); $i++) { Start-Sleep 1 }
"pid " + $p.Id + " listening: " + (Test-Path "$env:TEMP\acadjob_mb3\listening.txt")
