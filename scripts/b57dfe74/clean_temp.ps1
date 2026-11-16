# Temp\claude: delete heavy regenerable files of OLD sessions only. Scripts and small data stay.
param([switch]$Apply, [int]$RecentHours = 48)
$ErrorActionPreference = 'Stop'
$T = Join-Path $env:LOCALAPPDATA 'Temp\claude'
$proj = 'C:\Users\Admin\.claude\projects'
$delExt = @('.output', '.png', '.jpg', '.jpeg', '.dxf', '.bak', '.wav', '.mp3', '.m4a', '.mp4', '.dwl', '.dwl2')
$guidRx = '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
$cut = (Get-Date).AddHours(-$RecentHours)

# protected sessions: live processes + transcripts touched recently
$protected = @{}
Get-ChildItem -LiteralPath 'C:\Users\Admin\.claude\sessions' -Filter *.json -Force -ErrorAction SilentlyContinue | ForEach-Object {
    $alive = [bool](Get-Process -Id ([int]$_.BaseName) -ErrorAction SilentlyContinue)
    try { $c = Get-Content -LiteralPath $_.FullName -Raw -Encoding UTF8 | ConvertFrom-Json } catch { $c = $null }
    if ($c -and $c.sessionId -and ($alive -or $_.LastWriteTime -gt $cut)) { $protected[$c.sessionId] = 'live' }
}
Get-ChildItem -LiteralPath $proj -Directory -Force | ForEach-Object {
    Get-ChildItem -LiteralPath $_.FullName -Filter *.jsonl -File -Force -ErrorAction SilentlyContinue | Where-Object { $_.LastWriteTime -gt $cut } | ForEach-Object {
        if (-not $protected.ContainsKey($_.BaseName)) { $protected[$_.BaseName] = 'recent transcript' }
    }
}
'protected sessions: {0}' -f $protected.Count

$del = New-Object System.Collections.Generic.List[object]
$keptRecent = [long]0
foreach ($top in Get-ChildItem -LiteralPath $T -Directory -Force) {
    foreach ($sess in Get-ChildItem -LiteralPath $top.FullName -Directory -Force -ErrorAction SilentlyContinue) {
        if ($sess.Name -notmatch $guidRx) { continue }
        $files = Get-ChildItem -LiteralPath $sess.FullName -Recurse -File -Force -ErrorAction SilentlyContinue
        $isRecent = $protected.ContainsKey($sess.Name) -or [bool]($files | Where-Object { $_.LastWriteTime -gt $cut } | Select-Object -First 1)
        foreach ($f in $files) {
            $ext = $f.Extension.ToLower()
            $hit = ($delExt -contains $ext) -or ($ext -eq '.exe' -and $f.Length -gt 100MB)
            if (-not $hit) { continue }
            if ($isRecent) { $keptRecent += $f.Length; continue }
            $del.Add($f)
        }
    }
}
'--- to delete, by extension ---'
$del | Group-Object { $_.Extension.ToLower() } | ForEach-Object { New-Object PSObject -Property @{ Ext = $_.Name; N = $_.Count; MB = [math]::Round((($_.Group | Measure-Object Length -Sum).Sum) / 1MB, 1) } } | Sort-Object MB -Descending | Format-Table Ext, N, MB -AutoSize | Out-String
$sum = ($del | Measure-Object Length -Sum).Sum
'total to delete: {0} files, {1:N1} MB   (same types kept in recent sessions: {2:N1} MB)' -f $del.Count, ($sum / 1MB), ($keptRecent / 1MB)
'--- media / installers in the list ---'
$del | Where-Object { '.mp4', '.wav', '.mp3', '.m4a', '.exe' -contains $_.Extension.ToLower() } | Sort-Object Length -Descending | Select-Object -First 30 | ForEach-Object { '{0,8:N1} MB  {1:yyyy-MM-dd}  {2}' -f ($_.Length / 1MB), $_.LastWriteTime, $_.FullName.Substring($T.Length) }

if ($Apply) {
    $ok = 0; $fail = 0; $freed = [long]0
    foreach ($f in $del) {
        try { [IO.File]::SetAttributes($f.FullName, [IO.FileAttributes]::Normal); [IO.File]::Delete($f.FullName); $ok++; $freed += $f.Length } catch { $fail++ }
    }
    'DELETED: {0} files, {1:N1} MB   failed: {2}' -f $ok, ($freed / 1MB), $fail
} else { 'DRY RUN - nothing deleted' }
