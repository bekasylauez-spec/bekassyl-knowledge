param([string]$Ops, [string]$Dwg, [string]$Dxf = "")
# compile sc2.cs, run SCAPPLY in accoreconsole on $Dwg (a test copy) with ops file $Ops; optional DXFOUT afterwards
$net = Split-Path $MyInvocation.MyCommand.Path
$acadDir = "C:\Program Files\Autodesk\AutoCAD 2021"
$dll = Join-Path $net ("sc2_" + (Get-Date -Format HHmmssfff) + ".dll")
& "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe" /nologo /nowarn:618 /target:library /platform:x64 /r:"$acadDir\accoremgd.dll" /r:"$acadDir\acdbmgd.dll" /r:"$acadDir\acmgd.dll" /r:System.Web.Extensions.dll /out:"$dll" "$net\sc2.cs" | Out-Host
if ($LASTEXITCODE -ne 0) { throw "compile failed" }
Set-Content -Path "$net\last_dll.txt" -Value $dll -Encoding UTF8
Copy-Item $Ops "$env:TEMP\sc_ops.json" -Force
Remove-Item "$env:TEMP\sc_log.txt" -ErrorAction SilentlyContinue
$scr = Join-Path $net "run.scr"
$lines = @('(setvar "FILEDIA" 0)', '(setvar "SECURELOAD" 0)', '_.NETLOAD', "`"$dll`"", 'SCAPPLY2')
if ($Dxf) { $lines += @('_.DXFOUT', "`"$Dxf`"", '16') }
$lines += @('_.QUIT', '_Y', '')
[IO.File]::WriteAllText($scr, ($lines -join "`r`n"), [Text.Encoding]::Default)
Start-Process "$acadDir\accoreconsole.exe" -ArgumentList "/i `"$Dwg`" /s `"$scr`" /l ru-RU" -Wait -NoNewWindow -RedirectStandardOutput "$net\run.log" | Out-Null
Get-Content "$env:TEMP\sc_log.txt" -Encoding UTF8
