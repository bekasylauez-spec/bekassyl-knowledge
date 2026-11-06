param([string]$Ops, [int]$Wait = 900, [string]$Doc = "Б2 Ригели.dwg")
$net = "C:\Users\beka\AppData\Local\Temp\claude\61d567fc0ab17a45\4caa2bcf-418f-4319-ab71-13934baee5b7\scratchpad\net"
$acadDir = "C:\Program Files\Autodesk\AutoCAD 2021"
$mc = "C:\Program Files\CSoft\СПДС Металлоконструкции 2021 x64 для AutoCAD\mg142x64"
$src = Get-Item "$net\rz.cs"; $stamp = "$net\rz_last.txt"
$dll = if ((Test-Path $stamp) -and ((Get-Content $stamp -Raw).Split('|')[0] -eq $src.LastWriteTime.Ticks)) { (Get-Content $stamp -Raw).Split('|')[1].Trim() } else { $null }
if (-not $dll) {
  $dll = Join-Path $net ("b2r_" + (Get-Date -Format HHmmssfff) + ".dll")
  & "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe" /nologo /target:library /platform:x64 /r:"$acadDir\accoremgd.dll" /r:"$acadDir\acdbmgd.dll" /r:"$acadDir\acmgd.dll" /r:"$mc\mapimgd.dll" /r:"$mc\mapibasetypes.dll" /r:System.Web.Extensions.dll /out:"$dll" "$net\rz.cs" | Out-Host
  if ($LASTEXITCODE -ne 0) { throw "compile failed" }
  Set-Content $stamp ("" + $src.LastWriteTime.Ticks + "|" + $dll)
}
Copy-Item $Ops "$env:TEMP\b2_ops.json" -Force
$jd = "$env:TEMP\acadjob_b2"; Remove-Item "$jd\done.txt" -ErrorAction SilentlyContinue
[IO.File]::WriteAllText("$jd\job.txt", "$dll|B2R.Cmds|Apply|$Doc", [Text.Encoding]::UTF8)
$apid = (Get-Content "$net\pid.txt" -ErrorAction SilentlyContinue | Select-Object -First 1)
for ($i = 0; $i -lt $Wait -and -not (Test-Path "$jd\done.txt"); $i++) { Start-Sleep 1; if ($apid -and ($i % 5 -eq 0) -and -not (Get-Process -Id $apid -ErrorAction SilentlyContinue)) { "ACAD DEAD"; exit 3 } }
if (Test-Path "$jd\done.txt") { Get-Content "$jd\done.txt" -Encoding UTF8 | Select-Object -First 3 } else { "timeout" }
Get-Content "$env:TEMP\b2_log.txt" -Encoding UTF8 -ErrorAction SilentlyContinue | Select-Object -Last 40