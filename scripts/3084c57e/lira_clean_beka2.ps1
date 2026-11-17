# LIRA Work: delete recomputable calculation results of CLOSED models (#NN, .f74*, .crsn1, _pv/_01/_01c).
# Keeps .ald/.lir/.~lir/.txt/.rez, #sn/#rsm/#sl/#pr/#of, *.DOCS, data\*.lir. Default dry-run; -Apply deletes.
param([switch]$Apply)
$ErrorActionPreference = 'Stop'
$sp = 'C:\Users\beka\AppData\Local\Temp\claude\61d567fc0ab17a45\3084c57e-bfd6-4f37-98c3-78b360193443\scratchpad'
$wk = 'C:\Users\Public\Documents\LIRA SAPR\LIRA SAPR 2024\Work'
$lira = Get-Process | Where-Object { $_.ProcessName -match '^(LiraSapr|LirAnSvr|Sapfir|LiraLand|Lira.*)$' }
if ($lira) { "STOP: LIRA is running -> " + (($lira | ForEach-Object ProcessName) -join ', '); exit 1 }
$sel = Get-ChildItem -LiteralPath $wk -File -Force | Where-Object {
    $_.Name -match '#\d+[a-z]?\.' -or $_.Name -match '\.f74[a-z]?$' -or $_.Name -match '\.crsn1$' -or $_.Name -match '_(pv|01|01c)\.'
}
$byModel = $sel | Group-Object { ($_.Name -replace '(#\d+[a-z]?\..*|\.f74[a-z]?|\.crsn1|_(pv|01|01c)\..*)$', '') }
foreach ($g in $byModel) { '{0,-24} {1,3} files {2,9:N2} GB  newest {3:yyyy-MM-dd HH:mm}' -f $g.Name, $g.Count, (($g.Group | Measure-Object Length -Sum).Sum/1GB), ($g.Group | Sort-Object LastWriteTime -Descending | Select-Object -First 1).LastWriteTime }
$tot = ($sel | Measure-Object Length -Sum).Sum
'TOTAL {0} files {1:N2} GB' -f $sel.Count, ($tot/1GB)
if (-not $Apply) { 'DRY-RUN'; exit 0 }
$log = New-Object System.Collections.Generic.List[string]; $freed = 0L; $fail = 0
foreach ($f in $sel) {
    try { $f.Delete(); $freed += $f.Length; $log.Add("OK`t$($f.Length)`t$($f.FullName)") }
    catch { $fail++; $log.Add("FAIL`t$($f.Length)`t$($f.FullName)`t$($_.Exception.Message)") }
}
[IO.File]::WriteAllLines("$sp\lira_clean_log.tsv", $log, (New-Object Text.UTF8Encoding($false)))
'DELETED {0:N2} GB, failed {1}' -f ($freed/1GB), $fail
