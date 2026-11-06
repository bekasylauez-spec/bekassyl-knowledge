param([string]$Cs, [string]$Cmd, [string]$Dwg, [string[]]$Extra = @(), [hashtable]$Env = @{}, [switch]$Save)
# compile $Cs, run $Cmd on $Dwg in accoreconsole (optionally QSAVE)
$SP = "C:\Users\Admin\AppData\Local\Temp\claude\210ab68cad67e8c1\9a1000cd-e0d9-42b2-b432-f6f3db0e7099\scratchpad\gal"
$acad = "C:\Program Files\Autodesk\AutoCAD 2021"
$name = [IO.Path]::GetFileNameWithoutExtension($Cs)
$dll = "$SP\net\${name}_" + (Get-Date -Format HHmmssfff) + ".dll"
& "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe" /nologo /target:library /platform:x64 /r:"$acad\accoremgd.dll" /r:"$acad\acdbmgd.dll" /r:"$acad\acmgd.dll" /r:System.Web.Extensions.dll /out:"$dll" $Cs
if ($LASTEXITCODE -ne 0) { throw "compile failed" }
$lines = @("(setvar `"SECURELOAD`" 0)", "(setvar `"FILEDIA`" 0)", "_.NETLOAD", "`"$dll`"", $Cmd) + $Extra
if ($Save) { $lines += @("_.QSAVE") }
$lines += @("_.QUIT", "_Y")
$scr = "$SP\net\run_$name.scr"
[IO.File]::WriteAllText($scr, ($lines -join "`r`n") + "`r`n", [Text.Encoding]::GetEncoding(1251))
$psi = New-Object Diagnostics.ProcessStartInfo "$acad\accoreconsole.exe", "/i `"$Dwg`" /s `"$scr`" /l ru-RU"
$psi.UseShellExecute = $false; $psi.CreateNoWindow = $true; $psi.RedirectStandardOutput = $true
foreach ($k in $Env.Keys) { $psi.EnvironmentVariables[$k] = $Env[$k] }
$p = [Diagnostics.Process]::Start($psi)
$o = $p.StandardOutput.ReadToEnd(); $p.WaitForExit()
[IO.File]::WriteAllText("$SP\net\console_$name.txt", $o)
"exit $($p.ExitCode)"

