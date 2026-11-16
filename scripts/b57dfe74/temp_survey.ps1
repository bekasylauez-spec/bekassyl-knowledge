# Read-only: what is in %TEMP% (top level), how big, how old.
param([double]$MinMB = 15, [int]$OldDays = 2)
$T = Join-Path $env:LOCALAPPDATA 'Temp'
$cut = (Get-Date).AddDays(-$OldDays)
$rows = New-Object System.Collections.Generic.List[object]
foreach ($e in Get-ChildItem -LiteralPath $T -Force -ErrorAction SilentlyContinue) {
    if ($e.PSIsContainer) {
        if (($e.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { continue }
        $size = [long]0; $n = 0; $newest = [datetime]::MinValue
        $stack = New-Object System.Collections.Stack
        $stack.Push($e.FullName)
        while ($stack.Count -gt 0) {
            $p = $stack.Pop()
            try {
                $di = New-Object System.IO.DirectoryInfo($p)
                foreach ($x in $di.EnumerateFileSystemInfos()) {
                    if (($x.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { continue }
                    if (($x.Attributes -band [IO.FileAttributes]::Directory) -ne 0) { $stack.Push($x.FullName) }
                    else { $size += $x.Length; $n++; if ($x.LastWriteTime -gt $newest) { $newest = $x.LastWriteTime }; if ($x.CreationTime -gt $newest) { $newest = $x.CreationTime } }
                }
            } catch {}
        }
        if ($e.LastWriteTime -gt $newest) { $newest = $e.LastWriteTime }
        if ($e.CreationTime -gt $newest) { $newest = $e.CreationTime }
        $rows.Add((New-Object PSObject -Property @{ Kind = 'dir'; Name = $e.Name; Size = $size; N = $n; Newest = $newest }))
    } else {
        $newest = $e.LastWriteTime; if ($e.CreationTime -gt $newest) { $newest = $e.CreationTime }
        $rows.Add((New-Object PSObject -Property @{ Kind = 'file'; Name = $e.Name; Size = [long]$e.Length; N = 1; Newest = $newest }))
    }
}
$tot = ($rows | Measure-Object Size -Sum).Sum
$old = $rows | Where-Object { $_.Newest -lt $cut }
'Temp top-level entries: {0}; total {1:N1} GB; entries with nothing newer than {2} days: {3} ({4:N1} GB)' -f $rows.Count, ($tot / 1GB), $OldDays, @($old).Count, ((($old | Measure-Object Size -Sum).Sum) / 1GB)
'--- biggest dirs (>= {0} MB) ---' -f $MinMB
$rows | Where-Object { $_.Kind -eq 'dir' -and $_.Size -ge $MinMB * 1MB } | Sort-Object Size -Descending | ForEach-Object { '{0,9:N1} MB  {1,6} files  newest {2:yyyy-MM-dd HH:mm}  {3}' -f ($_.Size / 1MB), $_.N, $_.Newest, $_.Name }
'--- root files by extension ---'
$rows | Where-Object { $_.Kind -eq 'file' } | Group-Object { [IO.Path]::GetExtension($_.Name).ToLower() } | ForEach-Object {
    $g = $_.Group
    New-Object PSObject -Property @{ Ext = $_.Name; N = $g.Count; MB = [math]::Round((($g | Measure-Object Size -Sum).Sum) / 1MB, 1); OldMB = [math]::Round((($g | Where-Object { $_.Newest -lt $cut } | Measure-Object Size -Sum).Sum) / 1MB, 1) }
} | Sort-Object MB -Descending | Select-Object -First 25 | Format-Table Ext, N, MB, OldMB -AutoSize | Out-String
'--- biggest root files ---'
$rows | Where-Object { $_.Kind -eq 'file' } | Sort-Object Size -Descending | Select-Object -First 15 | ForEach-Object { '{0,9:N1} MB  newest {1:yyyy-MM-dd HH:mm}  {2}' -f ($_.Size / 1MB), $_.Newest, $_.Name }
