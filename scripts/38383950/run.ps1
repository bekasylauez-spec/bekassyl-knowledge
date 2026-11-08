param([string]$File, [int]$Wait = 900)
. "$PSScriptRoot\revit.ps1"
$job = Join-Path $PSScriptRoot "_job.cs"; [IO.File]::WriteAllText($job, [IO.File]::ReadAllText($File, [Text.Encoding]::UTF8), (New-Object Text.UTF8Encoding($false)))
$stub = [IO.File]::ReadAllText("$PSScriptRoot\runner_stub.cs", [Text.Encoding]::UTF8).Replace("__FILE__", $job)
$r = Invoke-RevitCode -Code $stub -TimeoutSec $Wait
if ($r.result) { if ($r.result.success) { "OK: " + $r.result.result } else { "FAIL: " + $r.result.errorMessage } } else { "ERR: " + ($r | ConvertTo-Json -Depth 5 -Compress) }
