param([string]$Ops, [int]$Wait = 420, [string]$Doc = "b3w.dwg")
$net = "C:\Users\beka\AppData\Local\Temp\claude\61d567fc0ab17a45\e9612f51-585b-4296-9d8b-098919c9d634\scratchpad\net"
$acadDir = "C:\Program Files\Autodesk\AutoCAD 2021"
$mc = (Get-ChildItem "C:\Program Files\CSoft" -Directory | ForEach-Object { Join-Path $_.FullName "mg142x64" } | Where-Object { Test-Path (Join-Path $_ "mapimgd.dll") } | Select-Object -First 1)
$src = Get-Item "$net\rz.cs"; $stamp = "$net\rz_last_b3.txt"
$dll = if ((Test-Path $stamp) -and ((Get-Content $stamp -Raw).Split('|')[0] -eq $src.LastWriteTime.Ticks)) { (Get-Content $stamp -Raw).Split('|')[1].Trim() } else { $null }
if (-not $dll) {
  $dll = Join-Path $net ("b3j_" + (Get-Date -Format HHmmssfff) + ".dll")
  & "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe" /nologo /target:library /platform:x64 /r:"$acadDir\accoremgd.dll" /r:"$acadDir\acdbmgd.dll" /r:"$acadDir\acmgd.dll" /r:"$mc\mapimgd.dll" /r:"$mc\mapibasetypes.dll" /r:System.Web.Extensions.dll /out:"$dll" "$net\rz.cs" | Out-Host
  if ($LASTEXITCODE -ne 0) { throw "compile failed" }
  Set-Content $stamp ("" + $src.LastWriteTime.Ticks + "|" + $dll)
}
Copy-Item $Ops "$env:TEMP\b3_ops.json" -Force
$jd = "$env:TEMP\acadjob_b3"; Remove-Item "$jd\done.txt" -ErrorAction SilentlyContinue
[IO.File]::WriteAllText("$jd\job.txt", "$dll|RG.Cmds|Apply|$Doc", [Text.Encoding]::UTF8)
for ($i = 0; $i -lt $Wait -and -not (Test-Path "$jd\done.txt"); $i++) {
  Start-Sleep 1
  if ($i % 10 -eq 9) { $al = Get-Process acad -ErrorAction SilentlyContinue | ? { $_.MainWindowTitle -like '*b3w.dwg*' -and $_.Responding }; if (-not $al) { $dead++ } else { $dead = 0 }; if ($dead -ge 6) { break } }
}
if (Test-Path "$jd\done.txt") { Get-Content "$jd\done.txt" -Encoding UTF8 | Select-Object -First 3 } else { "timeout" }
Get-Content "$env:TEMP\b3_log.txt" -Encoding UTF8 -ErrorAction SilentlyContinue | Select-Object -Last 25

