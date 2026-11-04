$SP = "C:\Users\Admin\AppData\Local\Temp\claude\D---------\4ae264b2-3d49-4a11-8864-2d6523e82a02\scratchpad\plot"
$acad = "C:\Program Files\Autodesk\AutoCAD 2021"
$src = Get-ChildItem "D:\РАБОЧКА\От Мадениет\Офис Байтурсунова\КМ КЖ ЧЕРТЕЖ\4-этаж новый\Блок 1\КЖ Чертеж" -Filter "7.2 *.dwg"
Copy-Item $src.FullName "$SP\src.dwg" -Force
$dll = "$SP\plotw_" + (Get-Date -Format HHmmssfff) + ".dll"
& "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe" /nologo /target:library /platform:x64 /r:"$acad\accoremgd.dll" /r:"$acad\acdbmgd.dll" /r:"$acad\acmgd.dll" /r:System.Web.Extensions.dll /out:"$dll" "$SP\plotw.cs"
if ($LASTEXITCODE -ne 0) { throw "compile failed" }
$lines = @("(setvar `"SECURELOAD`" 0)", "(setvar `"FILEDIA`" 0)", "_.NETLOAD", "`"$dll`"", "PLOTW", "_.QUIT", "_Y")
[IO.File]::WriteAllText("$SP\run.scr", ($lines -join "`r`n") + "`r`n", [Text.Encoding]::GetEncoding(1251))
Remove-Item "$SP\plotc_log.txt" -ErrorAction SilentlyContinue
$psi = New-Object Diagnostics.ProcessStartInfo "$acad\accoreconsole.exe", "/i `"$SP\src.dwg`" /s `"$SP\run.scr`" /l ru-RU"
$psi.UseShellExecute = $false; $psi.CreateNoWindow = $true; $psi.RedirectStandardOutput = $true
$psi.EnvironmentVariables["TEMP"] = $SP; $psi.EnvironmentVariables["TMP"] = $SP
$p = [Diagnostics.Process]::Start($psi); $null = $p.StandardOutput.ReadToEnd(); $p.WaitForExit()
Get-Content "$SP\plotc_log.txt" -Encoding UTF8
