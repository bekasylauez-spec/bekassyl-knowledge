# Move folders to another drive: copy -> SHA256-verify every file -> only then remove the source.
# Skips a folder if it is a link, the destination exists, or any file in it is in use.
param([string[]]$Sources, [string]$DstParent, [switch]$Apply)
$ErrorActionPreference = 'Stop'
if (-not (Test-Path -LiteralPath $DstParent)) { throw "destination parent missing: $DstParent" }
$sha = [Security.Cryptography.SHA256]::Create()
function Get-Sha([string]$p) { $fs = [IO.File]::Open($p, 'Open', 'Read', 'Read'); try { return [BitConverter]::ToString($sha.ComputeHash($fs)) } finally { $fs.Close() } }

# files of a tree, never descending into reparse points; returns @(files, reparseCount)
function Get-Tree([string]$root) {
    $files = New-Object System.Collections.Generic.List[object]; $rp = 0
    $stack = New-Object System.Collections.Stack; $stack.Push($root)
    while ($stack.Count -gt 0) {
        $p = $stack.Pop()
        foreach ($e in (New-Object IO.DirectoryInfo($p)).EnumerateFileSystemInfos()) {
            if (($e.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { $rp++ }
            elseif (($e.Attributes -band [IO.FileAttributes]::Directory) -ne 0) { $stack.Push($e.FullName) }
            else { $files.Add($e) }
        }
    }
    return @($files, $rp)
}

$moved = [long]0
foreach ($src in $Sources) {
    $src = $src.TrimEnd('\')
    $name = Split-Path $src -Leaf
    $dst = Join-Path $DstParent $name
    if (-not (Test-Path -LiteralPath $src)) { 'SKIP (not found): ' + $name; continue }
    $si = Get-Item -LiteralPath $src -Force
    if (($si.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { 'SKIP (is a link): ' + $name; continue }
    if (Test-Path -LiteralPath $dst) { 'SKIP (destination exists): ' + $dst; continue }
    $t = Get-Tree $src; $files = $t[0]
    if ($t[1] -gt 0) { 'SKIP (contains links): ' + $name; continue }
    $size = [long]0; $locked = 0
    foreach ($f in $files) { $size += $f.Length; try { $fs = [IO.File]::Open($f.FullName, 'Open', 'Read', 'None'); $fs.Close() } catch { $locked++ } }
    if ($locked -gt 0) { 'SKIP ({0} file(s) in use): {1}' -f $locked, $name; continue }
    if (-not $Apply) { 'would move {0,9:N1} MB  {1,4} files  {2}  ->  {3}' -f ($size / 1MB), $files.Count, $name, $dst; continue }

    $sw = [Diagnostics.Stopwatch]::StartNew()
    robocopy $src $dst /E /XJ /COPY:DAT /DCOPY:DAT /R:1 /W:1 /MT:8 /NFL /NDL /NP /NJH /NJS | Out-Null
    if ($LASTEXITCODE -ge 8) { 'COPY FAILED (robocopy {0}) - source kept: {1}' -f $LASTEXITCODE, $name; continue }
    $bad = 0
    foreach ($f in $files) {
        $target = Join-Path $dst $f.FullName.Substring($src.Length + 1)
        if (-not [IO.File]::Exists($target)) { $bad++; continue }
        if ((Get-Sha $f.FullName) -ne (Get-Sha $target)) { $bad++ }
    }
    if ($bad -gt 0) { 'VERIFY FAILED ({0} file(s)) - source kept: {1}' -f $bad, $name; continue }
    foreach ($f in $files) { if ($f.IsReadOnly) { $f.IsReadOnly = $false } }
    cmd /c rd /s /q "$src"
    if (Test-Path -LiteralPath $src) { 'COPIED+VERIFIED, but source could not be fully removed: ' + $name; continue }
    $moved += $size
    'MOVED {0,9:N1} MB  {1,4} files  SHA256 ok  {2:N0} s  {3}' -f ($size / 1MB), $files.Count, $sw.Elapsed.TotalSeconds, $dst
}
if ($Apply) { 'total moved: {0:N1} GB' -f ($moved / 1GB) } else { 'DRY RUN - nothing moved' }
