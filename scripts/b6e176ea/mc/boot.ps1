# NETLOAD lklisten.dll into the user's AutoCAD where the Рампа drawing is open, start LKLISTEN, switch back
$net = Split-Path $MyInvocation.MyCommand.Path
$dll = Join-Path $net "lklisten.dll"
$target = [IO.File]::ReadAllText((Join-Path $net "target.txt"), [Text.Encoding]::UTF8).Trim()
function Try-Com([scriptblock]$b) {
    for ($i = 0; $i -lt 40; $i++) { try { return & $b } catch { if ($_.Exception.HResult -ne -2147418111) { throw }; Start-Sleep -Milliseconds 500 } }
    throw "AutoCAD busy"
}
$jd = Join-Path $env:TEMP "acadjob_lk"
Remove-Item "$jd\listening.txt", "$jd\job.txt", "$jd\done.txt" -ErrorAction SilentlyContinue
$app = [Runtime.InteropServices.Marshal]::GetActiveObject("AutoCAD.Application")
$cur = Try-Com { $app.ActiveDocument }
$doc = $null; foreach ($d in $app.Documents) { if ($d.Name -eq $target) { $doc = $d } }
if ($doc -eq $null) { throw "target not open" }
Try-Com { if ($app.ActiveDocument.Name -ne $doc.Name) { $app.ActiveDocument = $doc } }
Try-Com { $doc.SetVariable("FILEDIA", 0) }
Try-Com { $doc.SendCommand("(setvar `"SECURELOAD`" 0)`n") }
Try-Com { $doc.SendCommand("_.NETLOAD`n" + $dll + "`n") }
Try-Com { $doc.SendCommand("LKLISTEN`n") }
for ($i = 0; $i -lt 20 -and -not (Test-Path "$jd\listening.txt"); $i++) { Start-Sleep 1 }
Try-Com { $doc.SetVariable("FILEDIA", 1) }
Try-Com { $doc.SendCommand("(setvar `"SECURELOAD`" 1)`n") }
if (Test-Path "$jd\listening.txt") { "listening: " + (Get-Content "$jd\listening.txt") } else { "not listening" }
Try-Com { if ($app.ActiveDocument.Name -ne $cur.Name) { $app.ActiveDocument = $cur } }
