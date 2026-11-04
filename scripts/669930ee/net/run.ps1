param([string]$Ops, [string]$Dwg)
$net = "C:\Users\Admin\AppData\Local\Temp\claude\D---------\669930ee-eb32-4d12-a14d-27254f43259a\scratchpad\net"
$acadDir = "C:\Program Files\Autodesk\AutoCAD 2021"
$src = Get-Item "$net\ops.cs"; $stamp = "$net\ops_last.txt"
$dll = $null
if ((Test-Path $stamp)) { $p = (Get-Content $stamp -Raw).Split('|'); if ($p[0] -eq $src.LastWriteTime.Ticks) { $dll = $p[1].Trim() } }
if (-not $dll) {
  $dll = Join-Path $net ("al_" + (Get-Date -Format HHmmssfff) + ".dll")
  & "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe" /nologo /target:library /platform:x64 /r:"$acadDir\accoremgd.dll" /r:"$acadDir\acdbmgd.dll" /r:System.Web.Extensions.dll /out:"$dll" "$net\ops.cs" | Out-Host
  if ($LASTEXITCODE -ne 0) { throw "compile failed" }
  Set-Content $stamp ("" + $src.LastWriteTime.Ticks + "|" + $dll)
}
Copy-Item $Ops "$env:TEMP\al_ops.json" -Force
Remove-Item "$env:TEMP\al_log.txt" -ErrorAction SilentlyContinue
$scr = "SECURELOAD 0`nFILEDIA 0`nNETLOAD`n`"$dll`"`nAPPLYOPS`n_.QUIT`n_Y`n"
[IO.File]::WriteAllText("$net\run.scr", $scr, [Text.Encoding]::ASCII)
& "$acadDir\accoreconsole.exe" /i "$Dwg" /s "$net\run.scr" /l ru-RU > "$net\run.log"
if (Test-Path "$env:TEMP\al_log.txt") { Get-Content "$env:TEMP\al_log.txt" -Encoding UTF8 } else { "NO LOG"; Get-Content "$net\run.log" -Tail 15 }
