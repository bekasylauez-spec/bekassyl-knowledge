$net = "C:\Users\Admin\AppData\Local\Temp\claude\210ab68cad67e8c1\e166461b-bde0-4f75-9345-660eafbd0735\scratchpad\net"
$acadDir = "C:\Program Files\Autodesk\AutoCAD 2021"
$dll = Join-Path $net ("gxlisten_" + (Get-Date -Format HHmmssfff) + ".dll")
& "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe" /nologo /target:library /platform:x64 /r:"$acadDir\accoremgd.dll" /r:"$acadDir\acdbmgd.dll" /r:"$acadDir\acmgd.dll" /out:"$dll" "$net\rzlisten.cs" | Out-Host
function Try-Com([scriptblock]$b) { for ($i = 0; $i -lt 40; $i++) { try { return & $b } catch { Start-Sleep -Milliseconds 500 } }; throw "AutoCAD busy" }
$app = [Runtime.InteropServices.Marshal]::GetActiveObject("AutoCAD.Application")
$cur = $app.ActiveDocument; $doc = $null
for ($i = 0; $i -lt $app.Documents.Count; $i++) { $d = $app.Documents.Item($i); if ($d.Name -eq "2.Схема каркас для клауда.dwg") { $doc = $d } }
if ($doc -eq $null) { throw "target not open" }
"active before: " + $cur.Name
New-Item -ItemType Directory -Force "$env:TEMP\acadjob_gx" | Out-Null
Remove-Item "$env:TEMP\acadjob_gx\listening.txt" -ErrorAction SilentlyContinue
Try-Com { if ($app.ActiveDocument.Name -ne $doc.Name) { $app.ActiveDocument = $doc } }
Try-Com { $doc.SetVariable("FILEDIA", 0) }
Try-Com { $doc.SendCommand("(setvar `"SECURELOAD`" 0)`n") }
Try-Com { $doc.SendCommand("_.NETLOAD`n" + $dll + "`n") }
Try-Com { $doc.SendCommand("GXLISTEN`n") }
for ($i = 0; $i -lt 20 -and -not (Test-Path "$env:TEMP\acadjob_gx\listening.txt"); $i++) { Start-Sleep 1 }
Try-Com { $doc.SetVariable("FILEDIA", 1) }
Try-Com { $doc.SendCommand("(setvar `"SECURELOAD`" 1)`n") }
Get-Content "$env:TEMP\acadjob_gx\listening.txt"
