param([string]$New, [string]$Target, [string]$Keep)
$ErrorActionPreference = 'Stop'
$acad = $null; try { $acad = [Runtime.InteropServices.Marshal]::GetActiveObject("AutoCAD.Application.24") } catch { }
if (-not $acad) { "no COM acad"; exit 1 }
$hit = $null
foreach ($doc in @($acad.Documents)) { "doc: " + $doc.FullName; if ($doc.FullName -ieq $Target) { $hit = $doc } }
if (-not $hit) { "target not in this AutoCAD instance"; exit 2 }
if (-not $hit.Saved) { $copy = Join-Path $Keep ("{0:HHmmss}_user_edits.dwg" -f (Get-Date)); $hit.SaveAs($copy); "unsaved changes kept: $copy" } else { "no unsaved changes" }
$hit.Close($false); "closed"
for ($i = 0; $i -lt 20; $i++) { try { $s = [IO.File]::Open($Target, 'Open', 'ReadWrite', 'None'); $s.Close(); break } catch { [Threading.Thread]::Sleep(500) } }
Copy-Item $New $Target -Force; "replaced"
$null = $acad.Documents.Open($Target); "reopened"
