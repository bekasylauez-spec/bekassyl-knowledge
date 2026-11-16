# Read-only survey of the LIRA-SAPR work folder: file classes and per-model totals.
param([string]$W = 'C:\Users\Public\Documents\LIRA SAPR\LIRA SAPR 2024\work', [int]$TopModels = 60)
$di = New-Object IO.DirectoryInfo($W)
'work: {0}' -f $W

'--- sub-folders ---'
foreach ($d in $di.EnumerateDirectories()) {
    $s = [long]0; $n = 0; $newest = $d.LastWriteTime
    foreach ($f in $d.EnumerateFiles('*', [IO.SearchOption]::AllDirectories)) { $s += $f.Length; $n++; if ($f.LastWriteTime -gt $newest) { $newest = $f.LastWriteTime } }
    '{0,9:N1} MB  {1,5} files  newest {2:yyyy-MM-dd HH:mm}  {3}' -f ($s / 1MB), $n, $newest, $d.Name
}

$rows = New-Object System.Collections.Generic.List[object]
foreach ($f in $di.EnumerateFiles()) {
    $name = $f.Name
    $m = [regex]::Match($name, '^(?<b>.+)#(?<n>[0-9]{2}[0-9A-Za-z]*)\.(?<b2>.+)$')
    if ($m.Success) { $base = $m.Groups['b'].Value; $class = '#NN' }
    else {
        $ext = $f.Extension
        $base = if ($ext) { $name.Substring(0, $name.Length - $ext.Length) } else { $name }
        $class = if ($ext) { $ext.ToLower() } else { '(none)' }
    }
    $rows.Add((New-Object PSObject -Property @{ Name = $name; Base = $base; Class = $class; Size = [long]$f.Length; Time = $f.LastWriteTime; Access = $f.LastAccessTime }))
}
$tot = [long]0; foreach ($r in $rows) { $tot += $r.Size }
'--- files in root: {0}, {1:N1} GB ---' -f $rows.Count, ($tot / 1GB)

'--- by class ---'
$rows | Group-Object Class | ForEach-Object {
    $s = [long]0; foreach ($r in $_.Group) { $s += $r.Size }
    New-Object PSObject -Property @{ Class = $_.Name; N = $_.Count; MB = [math]::Round($s / 1MB, 1); Sample = ($_.Group | Sort-Object Size -Descending | Select-Object -First 1).Name }
} | Sort-Object MB -Descending | Format-Table Class, N, MB, Sample -AutoSize | Out-String -Width 220

'--- by model (base name), top {0} by size ---' -f $TopModels
$rows | Group-Object Base | ForEach-Object {
    $s = [long]0; $newest = [datetime]::MinValue
    foreach ($r in $_.Group) { $s += $r.Size; if ($r.Time -gt $newest) { $newest = $r.Time } }
    New-Object PSObject -Property @{ Base = $_.Name; N = $_.Count; MB = [math]::Round($s / 1MB, 1); Newest = $newest; Classes = (($_.Group | Group-Object Class | ForEach-Object { $_.Name + 'x' + $_.Count }) -join ' ') }
} | Sort-Object MB -Descending | Select-Object -First $TopModels | ForEach-Object { '{0,9:N1} MB  {1,4} files  newest {2:yyyy-MM-dd HH:mm}  [{3}]  {4}' -f $_.MB, $_.N, $_.Newest, $_.Base, $_.Classes }
