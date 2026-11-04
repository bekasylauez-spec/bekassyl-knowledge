# compile rzlisten, write boot.scr, start my own AutoCAD on the КЖ file
$net = "C:\Users\Admin\AppData\Local\Temp\claude\D---------\22eb71ac-88c3-4c99-9c61-2c7547468f19\scratchpad\net"
$acadDir = "C:\Program Files\Autodesk\AutoCAD 2021"
$dll = Join-Path $net ("rzlisten_" + (Get-Date -Format HHmmssfff) + ".dll")
& "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe" /nologo /target:library /platform:x64 /r:"$acadDir\accoremgd.dll" /r:"$acadDir\acdbmgd.dll" /r:"$acadDir\acmgd.dll" /out:"$dll" "$net\rzlisten.cs" | Out-Host
if ($LASTEXITCODE -ne 0) { throw "compile failed" }
Remove-Item "$env:TEMP\acadjob_rz\listening.txt" -ErrorAction SilentlyContinue
$scr = "(setvar `"FILEDIA`" 0)`n(setvar `"SECURELOAD`" 0)`n_.NETLOAD`n$dll`nRZLISTEN`n(setvar `"FILEDIA`" 1)`n"
[IO.File]::WriteAllText("$net\boot.scr", $scr, (New-Object Text.UTF8Encoding $false))
$p = Start-Process "$acadDir\acad.exe" -ArgumentList "`"D:\РАБОЧКА\Резервуар\КЖ Резервуар.dwg`" /nologo /b `"$net\boot.scr`"" -PassThru
"pid " + $p.Id | Set-Content "$net\pid.txt"; "pid " + $p.Id
for ($i = 0; $i -lt 240 -and -not (Test-Path "$env:TEMP\acadjob_rz\listening.txt"); $i++) { Start-Sleep 1 }
if (Test-Path "$env:TEMP\acadjob_rz\listening.txt") { "listening after $i s" } else { "not listening" }
