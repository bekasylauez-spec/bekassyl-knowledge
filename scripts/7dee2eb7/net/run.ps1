param([string]$Dwg, [string]$Ops, [switch]$Save, [int]$Wait = 900)
$net = "C:\Users\Admin\AppData\Local\Temp\claude\D---------\7dee2eb7-f7d4-469a-b62a-9bb72312cd9d\scratchpad\net"
$acad = "C:\Program Files\Autodesk\AutoCAD 2021"
$src = Get-Item "$net\p4.cs"; $stamp = "$net\p4_last.txt"
$dll = $null
if (Test-Path $stamp) { $s = (Get-Content $stamp -Raw).Split('|'); if ($s[0] -eq "$($src.LastWriteTime.Ticks)") { $dll = $s[1].Trim() } }
if (-not $dll) {
  $dll = Join-Path $net ("p4_" + (Get-Date -Format HHmmssfff) + ".dll")
  & "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe" /nologo /target:library /platform:x64 /r:"$acad\accoremgd.dll" /r:"$acad\acdbmgd.dll" /r:System.Web.Extensions.dll /out:"$dll" "$net\p4.cs" | Out-Host
  if ($LASTEXITCODE -ne 0) { throw "compile failed" }
  Set-Content $stamp ("" + $src.LastWriteTime.Ticks + "|" + $dll)
}
Copy-Item $Ops "$env:TEMP\p4_ops.json" -Force
Remove-Item "$env:TEMP\p4_log.txt" -ErrorAction SilentlyContinue
$lines = @("SECURELOAD 0", "_.NETLOAD", "`"$dll`"", "P4RUN")
if ($Save) { $lines += "_.QSAVE" }
$lines += @("_.QUIT", "_Y")
$scr = "$net\p4run.scr"; [IO.File]::WriteAllLines($scr, $lines, [Text.Encoding]::GetEncoding(1251))
$p = Start-Process "$acad\accoreconsole.exe" -ArgumentList "/i `"$Dwg`" /s `"$scr`" /l ru-RU" -PassThru -WindowStyle Hidden
if (-not $p.WaitForExit($Wait * 1000)) { $p.Kill(); "TIMEOUT" }
if (Test-Path "$env:TEMP\p4_log.txt") { Get-Content "$env:TEMP\p4_log.txt" -Encoding UTF8 | Select-Object -Last 15 } else { "no log" }
