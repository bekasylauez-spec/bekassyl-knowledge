$ErrorActionPreference = 'Stop'
function Retry($sb) { for ($rt = 0; $rt -lt 20; $rt++) { try { return & $sb } catch { Start-Sleep -Milliseconds 500 } }; throw "COM failed" }
$dll = "C:\Users\Admin\AppData\Local\Temp\claude\D---------\4a661048-0918-42f9-b6f8-d2949692c1cf\scratchpad\paint2.dll"
$app = Retry { [Runtime.InteropServices.Marshal]::GetActiveObject("AutoCAD.Application") }
$target = $null
$prev = Retry { $app.ActiveDocument }
$n = Retry { $app.Documents.Count }
for ($i = 0; $i -lt $n; $i++) {
    $d = Retry { $app.Documents.Item($i) }
    $nm = Retry { $d.Name }
    "doc: $nm"
    if ($nm -like '*Площадка 2 07-09-2026 v2.dwg') { $target = $d }
}
if (-not $target) { "NOT FOUND in this instance"; return }
if ($args[0] -ne 'go') { "found, dry run"; return }
$prevName = Retry { $prev.Name }
Retry { $app.ActiveDocument = $target } | Out-Null
Start-Sleep 1
$cmd = "(setvar `"SECURELOAD`" 0)(setvar `"FILEDIA`" 0)(setvar `"CMDDIA`" 0)`n_.NETLOAD`n$dll`nPAINTTBL2`n(setvar `"FILEDIA`" 1)(setvar `"CMDDIA`" 1)(setvar `"SECURELOAD`" 1)`n_.REGENALL`n"
Retry { $target.SendCommand($cmd) } | Out-Null
"sent; prev=$prevName"
Start-Sleep 6
if ($prevName -ne (Retry { $target.Name })) { Retry { $app.ActiveDocument = $prev } | Out-Null; "switched back to $prevName" }
