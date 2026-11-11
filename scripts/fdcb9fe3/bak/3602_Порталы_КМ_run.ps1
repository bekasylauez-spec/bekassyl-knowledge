# run.ps1 <script.cs> [-Idle <log>] : send C# to Revit; with -Idle wait for the log file written on Idling.
param([string]$File, [string]$Idle = "", [int]$Wait = 900)
. "$PSScriptRoot\revit.ps1"; . "$PSScriptRoot\win.ps1"
$revitPid = [int](Get-Content "$PSScriptRoot\_pid.txt")
if ($Idle) { Remove-Item -LiteralPath $Idle -ErrorAction SilentlyContinue }
$job = Join-Path $PSScriptRoot "_job.cs"; [IO.File]::WriteAllText($job, [IO.File]::ReadAllText($File, [Text.Encoding]::UTF8), (New-Object Text.UTF8Encoding($false)))
$stub = [IO.File]::ReadAllText("$PSScriptRoot\runner_stub.cs", [Text.Encoding]::UTF8).Replace("__FILE__", $job)
$r = Invoke-RevitCode -Code $stub -TimeoutSec $Wait
if ($r.result) { if ($r.result.success) { "OK: " + $r.result.result } else { "FAIL: " + $r.result.errorMessage } } else { "ERR: " + ($r | ConvertTo-Json -Depth 5 -Compress) }
if ($Idle) {
  $m = (Get-Wins $revitPid | ? { $_.Title -like "Autodesk Revit 2025 - *" }).H; if ($m) { [W]::SetForegroundWindow($m) | Out-Null }
  for ($i = 0; $i -lt $Wait / 5; $i++) { Start-Sleep 5; if (Test-Path -LiteralPath $Idle) { Start-Sleep 1; break }
    $d = Get-Wins $revitPid | ? { $_.Class -eq "#32770" }; if ($d) { $kids = Get-Kids $d[0].H | ? Vis | % Text
      if ($kids -contains "Удаление опорного объекта") { Click-Text $revitPid "Удаление опорного объекта" | Out-Null; "dim refs removed" }
      elseif ($kids -contains "Удалить размер(ы)") { Click-Text $revitPid "Удалить размер(ы)" | Out-Null; "dims removed" }
      elseif ($kids -contains "Отсоединить элементы") { Click-Text $revitPid "Отсоединить элементы" | Out-Null; "conflicting joins unjoined" }
      elseif ($kids -match "0 Ошибки" -or ($kids -match "Предупрежд" -and -not ($kids -match "Ошибка"))) { Click-Text $revitPid "&OK" | Out-Null; "warning dismissed" } else { "DIALOG: " + ($d.Title -join "; ") + " :: " + ($kids -join "|"); break } } }
  if (Test-Path -LiteralPath $Idle) { Get-Content -LiteralPath $Idle -Encoding UTF8 } else { "no log yet" } }



