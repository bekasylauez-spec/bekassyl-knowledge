param([string]$List)
# sequential re-run of generator scripts in MY Revit. $env:A = _avto dir (passed in env to keep Cyrillic out of this file). $List = "rmc_u01:rmc_node_lib.cs,rmc_u02:rmc_node_lib.cs,..."
$sp = "C:\Users\Admin\AppData\Local\Temp\claude\a7137524bdaa49d0\c55bc92b-0511-4932-9c00-c1294111057c\scratchpad\w"
$a = $env:A
$sum = "$sp\out\driver_summary.txt"
foreach ($item in $List.Split(',')) {
    $p = $item.Split(':'); $name = $p[0]; $lib = if ($p.Count -gt 1) { $p[1] } else { "" }
    $t0 = Get-Date
    if ($lib -ne "") { $o = & D:\_claude_work\RMC\revit\run.ps1 -File "$a\$name.cs" -Lib "$a\$lib" -Wait 3000 } else { $o = & D:\_claude_work\RMC\revit\run.ps1 -File "$a\$name.cs" -Wait 3000 }
    $o | Out-File -Encoding utf8 "$sp\out\run_$name.txt"
    $txt = ($o | Out-String)
    $err = ([regex]::Matches($txt, "ERR |COMPILE ERROR|ABORT|timeout|exited")).Count
    $skip = ([regex]::Matches($txt, "SKIP ")).Count
    $line = "{0}  {1}  {2:N0}s  ERR={3} SKIP={4}  {5}" -f (Get-Date -Format "HH:mm:ss"), $name, ((Get-Date) - $t0).TotalSeconds, $err, $skip, (($o | Select-String "салынды [0-9]+|saved" | Select-Object -Last 2 | ForEach-Object { $_.Line.Trim() }) -join " | ")
    Add-Content -Path $sum -Value $line -Encoding UTF8
}
Add-Content -Path $sum -Value "DONE $(Get-Date -Format HH:mm:ss)" -Encoding UTF8
