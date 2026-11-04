# compile bclisten.cs and NETLOAD it into the user's AutoCAD on «КМ Чертеж БЦ.dwg», then BCLISTEN
$net = Split-Path $MyInvocation.MyCommand.Path
$acadDir = "C:\Program Files\Autodesk\AutoCAD 2021"
$dll = Join-Path $net ("bclisten_" + (Get-Date -Format HHmmssfff) + ".dll")
& "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe" /nologo /target:library /platform:x64 /r:"$acadDir\accoremgd.dll" /r:"$acadDir\acdbmgd.dll" /r:"$acadDir\acmgd.dll" /out:"$dll" "$net\bclisten.cs" | Out-Host
if ($LASTEXITCODE -ne 0) { throw "compile failed" }
function Try-Com([scriptblock]$b) { for ($i = 0; $i -lt 40; $i++) { try { return & $b } catch { Start-Sleep -Milliseconds 500 } }; throw "AutoCAD busy" }
$app = [Runtime.InteropServices.Marshal]::GetActiveObject("AutoCAD.Application")
$cur = $app.ActiveDocument; $doc = $null
for ($i = 0; $i -lt $app.Documents.Count; $i++) { $d = $app.Documents.Item($i); if ($d.Name -eq "КМ Чертеж БЦ.dwg") { $doc = $d } }
if ($doc -eq $null) { throw "target not open" }
Try-Com { if ($app.ActiveDocument.Name -ne $doc.Name) { $app.ActiveDocument = $doc } }
Try-Com { $doc.SetVariable("FILEDIA", 0) }
Try-Com { $doc.SendCommand("(setvar `"SECURELOAD`" 0)`n") }
Try-Com { $doc.SendCommand("_.NETLOAD`n" + $dll + "`n") }
Try-Com { $doc.SendCommand("BCLISTEN`n") }
for ($i = 0; $i -lt 20 -and -not (Test-Path "$env:TEMP\acadjob_bc\listening.txt"); $i++) { Start-Sleep 1 }
Try-Com { $doc.SetVariable("FILEDIA", 1) }
Try-Com { $doc.SendCommand("(setvar `"SECURELOAD`" 1)`n") }
Get-Content "$env:TEMP\acadjob_bc\listening.txt"
