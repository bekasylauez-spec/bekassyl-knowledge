# NETLOAD rzlisten into the user's AutoCAD on «КЖ Резервуар.dwg», then RZLISTEN
$net = "C:\Users\Admin\AppData\Local\Temp\claude\D---------\22eb71ac-88c3-4c99-9c61-2c7547468f19\scratchpad\net"
$dll = (Get-ChildItem "$net\rzlisten_*.dll" | Sort-Object LastWriteTime | Select-Object -Last 1).FullName
function Try-Com([scriptblock]$b) { for ($i = 0; $i -lt 40; $i++) { try { return & $b } catch { Start-Sleep -Milliseconds 500 } }; throw "AutoCAD busy" }
$app = [Runtime.InteropServices.Marshal]::GetActiveObject("AutoCAD.Application")
$cur = $app.ActiveDocument; $doc = $null
for ($i = 0; $i -lt $app.Documents.Count; $i++) { $d = $app.Documents.Item($i); if ($d.Name -eq "КЖ Резервуар.dwg") { $doc = $d } }
if ($doc -eq $null) { throw "target not open" }
"active before: " + $cur.Name
Remove-Item "$env:TEMP\acadjob_rz\listening.txt" -ErrorAction SilentlyContinue
Try-Com { if ($app.ActiveDocument.Name -ne $doc.Name) { $app.ActiveDocument = $doc } }
Try-Com { $doc.SetVariable("FILEDIA", 0) }
Try-Com { $doc.SendCommand("(setvar `"SECURELOAD`" 0)`n") }
Try-Com { $doc.SendCommand("_.NETLOAD`n" + $dll + "`n") }
Try-Com { $doc.SendCommand("RZLISTEN`n") }
for ($i = 0; $i -lt 20 -and -not (Test-Path "$env:TEMP\acadjob_rz\listening.txt"); $i++) { Start-Sleep 1 }
Try-Com { $doc.SetVariable("FILEDIA", 1) }
Try-Com { $doc.SendCommand("(setvar `"SECURELOAD`" 1)`n") }
Try-Com { if ($cur -ne $null -and $app.ActiveDocument.Name -ne $cur.Name) { $app.ActiveDocument = $cur } }
Get-Content "$env:TEMP\acadjob_rz\listening.txt"
