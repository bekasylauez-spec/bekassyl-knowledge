# Phase 2: final sync, swap the C folder for a junction to D, merge anything written during the swap, verify.
# The original folder is kept as <Src>__old_C (deleted later, in a separate step).
param(
    [string]$Src = 'C:\Users\Admin\.claude\projects',
    [string]$Dst = 'D:\Users\Admin\.claude\projects',
    [string]$CopyFlags = 'DAT',
    [int]$MaxAttempts = 40
)
$ErrorActionPreference = 'Stop'
$Old  = $Src + '__old_C'
$TmpJ = $Src + '__new_J'

function Snap([string]$root) {
    $h = @{}
    $stack = New-Object System.Collections.Stack
    $stack.Push($root)
    $plen = $root.TrimEnd('\').Length + 1
    while ($stack.Count -gt 0) {
        $p = $stack.Pop()
        $di = New-Object System.IO.DirectoryInfo($p)
        foreach ($e in $di.EnumerateFileSystemInfos()) {
            if (($e.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { continue }
            if (($e.Attributes -band [IO.FileAttributes]::Directory) -ne 0) { $stack.Push($e.FullName) }
            else { $h[$e.FullName.Substring($plen)] = @([long]$e.Length, [long]$e.LastWriteTimeUtc.Ticks) }
        }
    }
    return $h
}

function Diff($a, $b) {
    $d = New-Object System.Collections.Generic.List[string]
    foreach ($k in $a.Keys) {
        if (-not $b.ContainsKey($k)) { $d.Add($k); continue }
        $x = $a[$k]; $y = $b[$k]
        if ($x[0] -ne $y[0]) { $d.Add($k); continue }
        if ([math]::Abs($x[1] - $y[1]) -gt 20000000) { $d.Add($k) }
    }
    return ,$d
}

function Ensure-Dir([string]$file) {
    $dir = [IO.Path]::GetDirectoryName($file)
    if (-not [IO.Directory]::Exists($dir)) { [IO.Directory]::CreateDirectory($dir) | Out-Null }
}

# Append bytes [from..end) of $srcFile to the end of $dstFile (append-only logs: nothing is overwritten)
function Append-Tail([string]$srcFile, [long]$from, [string]$dstFile) {
    Ensure-Dir $dstFile
    $in = New-Object IO.FileStream($srcFile, [IO.FileMode]::Open, [IO.FileAccess]::Read, [IO.FileShare]::ReadWrite)
    try {
        $len = $in.Length - $from
        if ($len -le 0) { return 0 }
        $buf = New-Object byte[] $len
        $in.Position = $from
        $read = 0
        while ($read -lt $len) { $n = $in.Read($buf, $read, $len - $read); if ($n -le 0) { break }; $read += $n }
    } finally { $in.Close() }
    $out = New-Object IO.FileStream($dstFile, [IO.FileMode]::Append, [IO.FileAccess]::Write, [IO.FileShare]::ReadWrite)
    try { $out.Write($buf, 0, $read) } finally { $out.Close() }
    return $read
}

# Merge files of $from (old or race dir) into $Dst. $base = snapshot at the verified moment (or $null for a race dir).
function Merge-Into([string]$from, $base, [string]$label) {
    $snap = Snap $from
    $handled = 0
    foreach ($k in $snap.Keys) {
        $o = $snap[$k]
        $V = [long]0
        if ($base -ne $null -and $base.ContainsKey($k)) {
            $v = $base[$k]
            if ($o[0] -eq $v[0] -and $o[1] -eq $v[1]) { continue }   # unchanged since verified sync
            $V = [long]$v[0]
        }
        $srcFile = Join-Path $from $k
        $dstFile = Join-Path $Dst $k
        $handled++
        if ($k.ToLower().EndsWith('.jsonl')) {
            if ($o[0] -gt $V) {
                $n = Append-Tail $srcFile $V $dstFile
                '  [{0}] jsonl appended {1} bytes: {2}' -f $label, $n, $k
            } else {
                '  [{0}] !! CONFLICT (jsonl not grown: old={1} verified={2}): {3}' -f $label, $o[0], $V, $k
                $script:Conflicts++
            }
        } else {
            $copy = $true
            if ([IO.File]::Exists($dstFile)) {
                $dt = [IO.File]::GetLastWriteTimeUtc($dstFile).Ticks
                if ($dt -gt $o[1]) { $copy = $false }
            }
            if ($copy) { Ensure-Dir $dstFile; [IO.File]::Copy($srcFile, $dstFile, $true); '  [{0}] copied: {1}' -f $label, $k }
            else { '  [{0}] kept newer file on D: {1}' -f $label, $k }
        }
    }
    return $handled
}

# --- pre-checks
$si = Get-Item -LiteralPath $Src -Force
if (($si.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw "Src is already a reparse point: $Src" }
if (-not (Test-Path -LiteralPath $Dst)) { throw "Dst missing: $Dst (run phase 1 first)" }
if (Test-Path -LiteralPath $Old) { throw "Old dir already exists: $Old" }
if (Test-Path -LiteralPath $TmpJ) { cmd /c rmdir "$TmpJ" | Out-Null }
New-Item -ItemType Junction -Path $TmpJ -Target $Dst | Out-Null

$script:Conflicts = 0
$raceDirs = @()
$swapped = $false
$base = $null
$attempt = 0
while (-not $swapped -and $attempt -lt $MaxAttempts) {
    $attempt++
    robocopy $Src $Dst /E /XJ /COPY:$CopyFlags /DCOPY:DAT /R:1 /W:1 /MT:8 /NFL /NDL /NP /NJH /NJS | Out-Null
    if ($LASTEXITCODE -ge 8) { 'attempt {0}: robocopy exit {1}' -f $attempt, $LASTEXITCODE; Start-Sleep -Milliseconds 500; continue }
    $snapD = Snap $Dst
    $snapS = Snap $Src
    $d = Diff $snapS $snapD
    if ($d.Count -gt 0) { 'attempt {0}: {1} file(s) changed during sync, syncing again' -f $attempt, $d.Count; continue }
    try { [IO.Directory]::Move($Src, $Old) }
    catch { 'attempt {0}: folder is in use, retrying ({1})' -f $attempt, $_.Exception.InnerException.Message; Start-Sleep -Milliseconds 800; continue }
    # the folder is renamed: put the junction in its place immediately
    $ok = $false
    for ($i = 0; $i -lt 300 -and -not $ok; $i++) {
        try { [IO.Directory]::Move($TmpJ, $Src); $ok = $true }
        catch {
            if ([IO.Directory]::Exists($Src)) {
                $race = $Src + '__race_' + $i
                try { [IO.Directory]::Move($Src, $race); $raceDirs += $race } catch { Start-Sleep -Milliseconds 10 }
            } else { Start-Sleep -Milliseconds 10 }
        }
    }
    if (-not $ok) {
        'SWAP FAILED - rolling back'
        [IO.Directory]::Move($Old, $Src)
        throw 'could not place the junction; original folder restored'
    }
    $base = $snapS
    $swapped = $true
}
if (-not $swapped) {
    if (Test-Path -LiteralPath $TmpJ) { cmd /c rmdir "$TmpJ" | Out-Null }
    'NOT SWAPPED after {0} attempts - C is unchanged' -f $attempt
    exit 2
}
'swapped on attempt {0} at {1:HH:mm:ss.fff}' -f $attempt, (Get-Date)

# --- merge whatever was written between the verified sync and the swap
$n = Merge-Into $Old $base 'window'
'files changed in the swap window: {0}' -f $n
foreach ($r in $raceDirs) {
    $n2 = Merge-Into $r $null 'race'
    'race dir {0}: {1} file(s) merged' -f $r, $n2
}

# --- verify
$ji = Get-Item -LiteralPath $Src -Force
'junction: {0}  type={1}  ->  {2}' -f $Src, $ji.LinkType, (@($ji.Target)[0])
$snapO = Snap $Old
$snapD = Snap $Dst
$missing = 0; $smaller = 0; $bytesO = [long]0; $bytesD = [long]0
foreach ($k in $snapO.Keys) {
    $bytesO += $snapO[$k][0]
    if (-not $snapD.ContainsKey($k)) { $missing++; '  MISSING on D: ' + $k; continue }
    if ($snapD[$k][0] -lt $snapO[$k][0]) { $smaller++; '  SMALLER on D: ' + $k }
}
foreach ($k in $snapD.Keys) { $bytesD += $snapD[$k][0] }
'old (C): {0} files, {1:N1} MB' -f $snapO.Count, ($bytesO / 1MB)
'new (D): {0} files, {1:N1} MB' -f $snapD.Count, ($bytesD / 1MB)
'missing={0} smaller={1} conflicts={2} raceDirs={3}' -f $missing, $smaller, $script:Conflicts, $raceDirs.Count
if ($missing -eq 0 -and $smaller -eq 0 -and $script:Conflicts -eq 0) { 'VERIFY OK' } else { 'VERIFY PROBLEMS - do not delete the old folder' }
