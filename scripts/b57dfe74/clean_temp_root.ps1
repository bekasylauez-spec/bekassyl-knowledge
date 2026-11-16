# %TEMP% root + NVIDIA DXCache: delete old regenerable files only. Files in use are skipped (locked).
# Never touched here: sub-folders, .sv$ / .bak / .dwg (AutoCAD autosave/backup), anything newer than $OldDays.
param([switch]$Apply, [int]$OldDays = 2, [string[]]$Classes = @())
$T = Join-Path $env:LOCALAPPDATA 'Temp'
$cut = (Get-Date).AddDays(-$OldDays)
$sets = @{}
function Add-To([string]$k, $f) { if (-not $sets.ContainsKey($k)) { $sets[$k] = New-Object System.Collections.Generic.List[object] }; $sets[$k].Add($f) }

$otherAc = 0
foreach ($f in (New-Object IO.DirectoryInfo($T)).EnumerateFiles()) {
    $newest = $f.LastWriteTime; if ($f.CreationTime -gt $newest) { $newest = $f.CreationTime }
    if ($newest -ge $cut) { continue }
    $ext = $f.Extension.ToLower()
    if ($ext -eq '.ac$') { if ($f.Name -like 'UND*') { Add-To 'undo' $f } else { $otherAc++ } }
    elseif ($ext -eq '.tmp') { Add-To 'tmp' $f }
    elseif ($ext -eq '.log') { Add-To 'log' $f }
    elseif ($ext -eq '.dmp') { Add-To 'dmp' $f }
    elseif ($ext -eq '') { Add-To 'noext' $f }
}
$dxDir = Join-Path $env:LOCALAPPDATA 'NVIDIA\DXCache'
if (Test-Path -LiteralPath $dxDir) {
    foreach ($f in (New-Object IO.DirectoryInfo($dxDir)).EnumerateFiles()) { if ($f.LastWriteTime -lt $cut) { Add-To 'dxcache' $f } }
}

'cut-off: nothing newer than {0:yyyy-MM-dd HH:mm} is touched' -f $cut
foreach ($k in ($sets.Keys | Sort-Object)) {
    $s = [long]0; foreach ($f in $sets[$k]) { $s += $f.Length }
    '{0,-8} {1,7} files  {2,9:N1} MB' -f $k, $sets[$k].Count, ($s / 1MB)
}
'other old .ac$ (not UND*, left alone): ' + $otherAc

if ($sets.ContainsKey('noext') -and -not $Apply) {
    '--- extension-less files: name shapes (sample of 5000) ---'
    $sample = $sets['noext'] | Select-Object -First 5000
    $sample | ForEach-Object { [regex]::Replace([regex]::Replace($_.Name, '[0-9]', '9'), '[A-Za-z]', 'a') } | Group-Object | Sort-Object Count -Descending | Select-Object -First 6 | ForEach-Object { '{0,6}  {1}' -f $_.Count, $_.Name }
    '--- biggest / samples ---'
    $sets['noext'] | Sort-Object Length -Descending | Select-Object -First 5 | ForEach-Object { '{0,9:N1} KB  {1:yyyy-MM-dd HH:mm}  {2}' -f ($_.Length / 1KB), $_.LastWriteTime, $_.Name }
    '--- by day ---'
    $sets['noext'] | Group-Object { $_.LastWriteTime.ToString('yyyy-MM-dd') } | Sort-Object Name | ForEach-Object { $s = [long]0; foreach ($f in $_.Group) { $s += $f.Length }; '{0}  {1,7} files  {2,8:N1} MB' -f $_.Name, $_.Count, ($s / 1MB) }
    '--- first bytes of 4 samples ---'
    $sets['noext'] | Sort-Object Length -Descending | Select-Object -First 2 -Skip 0 | ForEach-Object {
        try { $fs = [IO.File]::Open($_.FullName, 'Open', 'Read', 'ReadWrite'); $b = New-Object byte[] 64; $n = $fs.Read($b, 0, 64); $fs.Close()
            $_.Name + ' : ' + (($b[0..($n - 1)] | ForEach-Object { if ($_ -ge 32 -and $_ -lt 127) { [char]$_ } else { '.' } }) -join '') } catch { $_.Name + ' : (locked)' }
    }
    $mid = [int]($sets['noext'].Count / 2)
    $sets['noext'] | Select-Object -First 2 -Skip $mid | ForEach-Object {
        try { $fs = [IO.File]::Open($_.FullName, 'Open', 'Read', 'ReadWrite'); $b = New-Object byte[] 64; $n = $fs.Read($b, 0, 64); $fs.Close()
            ('{0} ({1} bytes) : ' -f $_.Name, $_.Length) + (($b[0..([math]::Max($n - 1, 0))] | ForEach-Object { if ($_ -ge 32 -and $_ -lt 127) { [char]$_ } else { '.' } }) -join '') } catch { $_.Name + ' : (locked)' }
    }
}

if ($Apply) {
    foreach ($k in $Classes) {
        if (-not $sets.ContainsKey($k)) { continue }
        $ok = 0; $fail = 0; $freed = [long]0
        foreach ($f in $sets[$k]) {
            try { if ($f.IsReadOnly) { $f.IsReadOnly = $false }; $len = $f.Length; [IO.File]::Delete($f.FullName); $ok++; $freed += $len } catch { $fail++ }
        }
        'DELETED {0,-8} {1,7} files  {2,9:N1} MB   (in use / skipped: {3})' -f $k, $ok, ($freed / 1MB), $fail
    }
} else { 'DRY RUN - nothing deleted' }
