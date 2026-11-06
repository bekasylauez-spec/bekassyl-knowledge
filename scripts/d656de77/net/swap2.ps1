param([string]$New, [string]$Like, [string]$Keep)
$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\rotlib.ps1"
$hit = $null; $name = $null
foreach ($it in [Rot]::All()) { if ($it[0] -like $Like) { $hit = $it[1]; $name = $it[0] } }
if (-not $hit) { "not found"; exit 2 }
"found: $name"
$app = $hit.Application; $full = $hit.FullName; "full: $full"
if (-not $hit.Saved) { $copy = Join-Path $Keep ("{0:HHmmss}_user_edits.dwg" -f (Get-Date)); $hit.SaveAs($copy); "unsaved changes kept: $copy"; $full2 = $full } else { "no unsaved changes" }
$hit.Close($false); "closed"
for ($i = 0; $i -lt 30; $i++) { try { $s = [IO.File]::Open($full, 'Open', 'ReadWrite', 'None'); $s.Close(); break } catch { [Threading.Thread]::Sleep(500) } }
Copy-Item $New $full -Force; "replaced"
$null = $app.Documents.Open($full); "reopened"
