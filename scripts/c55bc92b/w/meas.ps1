# sequential read-only measurements in MY Revit; outputs in scratchpad\w\out\m_<name>.txt ; $env:A = _avto dir
$sp = "C:\Users\Admin\AppData\Local\Temp\claude\a7137524bdaa49d0\c55bc92b-0511-4932-9c00-c1294111057c\scratchpad\w"
$a = $env:A
Remove-Item "$sp\out\keys.txt" -ErrorAction SilentlyContinue
$jobs = @(
  @("moved", "$sp\moved.cs", ""),
  @("clash_h", "$sp\clash_h.cs", "$a\rmc_misc_lib.cs"),
  @("parts2", "$sp\parts2.cs", "$a\rmc_misc_lib.cs"),
  @("cap2", "$sp\cap2.cs", "$a\rmc_misc_lib.cs"),
  @("cc2", "$sp\cc2.cs", "$a\rmc_misc_lib.cs"),
  @("p2f", "$sp\p2f.cs", "$a\rmc_misc_lib.cs"),
  @("inv", "$sp\inv.cs", ""),
  @("ck_u", "$sp\ck_u.cs", "$a\rmc_node_lib.cs"),
  @("ck_u16", "$a\rmc_u16_check.cs", "$a\rmc_node_lib.cs"),
  @("ck_ub", "$a\rmc_ub_check.cs", "$a\rmc_brace_lib.cs"),
  @("ck_um", "$a\rmc_um_check.cs", "$a\rmc_misc_lib.cs")
)
foreach ($j in $jobs) {
    $t0 = Get-Date
    if ($j[2] -ne "") { $o = & D:\_claude_work\RMC\revit\run.ps1 -File $j[1] -Lib $j[2] -Wait 3000 } else { $o = & D:\_claude_work\RMC\revit\run.ps1 -File $j[1] -Wait 3000 }
    $o | Out-File -Encoding utf8 "$sp\out\m_$($j[0]).txt"
    Add-Content -Path "$sp\out\meas_done.txt" -Value ("{0} {1} {2:N0}s" -f (Get-Date -Format HH:mm:ss), $j[0], ((Get-Date) - $t0).TotalSeconds) -Encoding UTF8
}
Add-Content -Path "$sp\out\meas_done.txt" -Value "ALLDONE" -Encoding UTF8
