param([string]$New, [string]$Target)
# user's AutoCAD has $Target open: save a copy of user edits, close it, replace the file, reopen (COM). Never kills AutoCAD.
$name = [IO.Path]::GetFileName($Target)
$app = $null; $doc = $null
try { $app = [Runtime.InteropServices.Marshal]::GetActiveObject("AutoCAD.Application.24") } catch { "no COM: $_"; exit 1 }
foreach ($d in $app.Documents) { if ($d.FullName -ieq $Target -or $d.Name -ieq $name) { $doc = $d } }
if (-not $doc) { "doc not in this instance"; exit 2 }
if (-not $doc.Saved) { $bk = [IO.Path]::Combine([IO.Path]::GetDirectoryName($New), "user_edits_" + $name); $doc.SaveAs($bk); "user edits saved to $bk" }
$doc.Close($false); "closed"
Start-Sleep 2
Copy-Item $New $Target -Force; "replaced"
$app.Documents.Open($Target) | Out-Null; "reopened"
