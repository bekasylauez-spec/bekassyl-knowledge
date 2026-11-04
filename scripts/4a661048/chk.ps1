function Retry($sb) { for ($rt = 0; $rt -lt 20; $rt++) { try { return & $sb } catch { Start-Sleep -Milliseconds 500 } }; throw "COM failed" }
$app = Retry { [Runtime.InteropServices.Marshal]::GetActiveObject("AutoCAD.Application") }
$doc = Retry { $app.ActiveDocument }
"active: " + (Retry { $doc.Name })
$ms = Retry { $doc.ModelSpace }
$all = @(); foreach ($e in $ms) { if ($e.ObjectName -eq "AcDbTable") { $all += $e } }
foreach ($t in $all) {
    $p = $t.InsertionPoint
    if ([math]::Abs($p[1] + 50200) -lt 50) {
        "table " + $t.Handle + " cols=" + $t.Columns + " rows=" + $t.Rows
        for ($r = 2; $r -le 3; $r++) { $line = ""; for ($c = 0; $c -lt $t.Columns; $c++) { $line += $t.GetText($r, $c) + " | " }; $line }
    }
}

