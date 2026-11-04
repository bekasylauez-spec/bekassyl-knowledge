param([string]$Ops, [switch]$Load, [switch]$Final, [int]$TimeoutSec = 120, [string]$Target = "КМ Чертеж БЦ.dwg")
# STAPPLY с $Ops в открытом AutoCAD пользователя на документе $Target, затем вернуться к его документу.
$here = Split-Path $MyInvocation.MyCommand.Path
$dll = (Get-Content "$here\last_dll.txt" -Encoding UTF8).Trim()
$acad = [Runtime.InteropServices.Marshal]::GetActiveObject("AutoCAD.Application")
$prev = $acad.ActiveDocument
$doc = $null; for ($i = 0; $i -lt $acad.Documents.Count; $i++) { $d = $acad.Documents.Item($i); if ($d.Name -eq $Target) { $doc = $d } }
if (-not $doc) { throw "target doc not open; open: " + (($acad.Documents | ForEach-Object { $_.Name }) -join ", ") }
if ($doc.GetVariable("CMDACTIVE") -ne 0) { throw "command active in target" }
Copy-Item -LiteralPath $Ops "$env:TEMP\st_ops.json" -Force
Remove-Item "$env:TEMP\st_log.txt" -ErrorAction SilentlyContinue
function Retry($sb){ for($k=0;$k -lt 20;$k++){ try { return & $sb } catch { Start-Sleep -Milliseconds 700 } }; throw "COM busy" }
Retry { $doc.Activate() } | Out-Null
Start-Sleep -Milliseconds 800
$cmd = ""
if ($Load) { $cmd += "(setvar `"FILEDIA`" 0)`n(setvar `"SECURELOAD`" 0)`n_.NETLOAD`n" + $dll + "`n" }
$cmd += "STAPPLY4`n"
if ($Final) { $cmd += "_.REGENALL`n(setvar `"FILEDIA`" 1)`n(setvar `"SECURELOAD`" 1)`n" }
Retry { $doc.SendCommand($cmd) } | Out-Null
$t0 = Get-Date
while (-not (Test-Path "$env:TEMP\st_log.txt") -and ((Get-Date) - $t0).TotalSeconds -lt $TimeoutSec) { Start-Sleep -Milliseconds 500 }
Start-Sleep -Seconds 2
if ($prev.Name -ne $Target) { try { Retry { $prev.Activate() } | Out-Null } catch { "could not switch back: " + $_ } }
if (Test-Path "$env:TEMP\st_log.txt") { Get-Content "$env:TEMP\st_log.txt" -Encoding UTF8 } else { "NO LOG (timeout)" }
"active: " + $acad.ActiveDocument.Name
