# Phase 1: prepare destination on D and bulk-copy. Nothing on C is changed here.
param(
    [string]$Src = 'C:\Users\Admin\.claude\projects',
    [string]$DstParent = 'D:\Users\Admin\.claude',
    [switch]$ProtectAcl,
    [string]$CopyFlags = 'DAT'
)
$ErrorActionPreference = 'Stop'
$Dst = Join-Path $DstParent (Split-Path $Src -Leaf)

$si = Get-Item -LiteralPath $Src -Force
if (($si.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw "Src is already a reparse point: $Src" }
if (Test-Path -LiteralPath $Dst) { throw "Dst already exists: $Dst" }

if (-not (Test-Path -LiteralPath $DstParent)) { New-Item -ItemType Directory -Path $DstParent -Force | Out-Null }
if ($ProtectAcl) {
    $me = "$env:USERDOMAIN\$env:USERNAME"
    icacls $DstParent /grant:r "*S-1-5-18:(OI)(CI)F" "*S-1-5-32-544:(OI)(CI)F" "${me}:(OI)(CI)F" | Out-Null
    icacls $DstParent /inheritance:r | Out-Null
    'ACL of ' + $DstParent + ':'
    icacls $DstParent
}
$sw = [Diagnostics.Stopwatch]::StartNew()
robocopy $Src $Dst /E /XJ /COPY:$CopyFlags /DCOPY:DAT /R:2 /W:1 /MT:8 /NFL /NDL /NP /NJH
$rc = $LASTEXITCODE
'robocopy exit: {0}   time: {1:N0} s' -f $rc, $sw.Elapsed.TotalSeconds
if ($rc -ge 8) { throw "robocopy failed with exit code $rc" }

# Re-create junctions that /XJ skipped (same targets as on C)
$stack = New-Object System.Collections.Stack
$stack.Push($Src)
$plen = $Src.TrimEnd('\').Length + 1
while ($stack.Count -gt 0) {
    $p = $stack.Pop()
    $di = New-Object System.IO.DirectoryInfo($p)
    foreach ($e in $di.EnumerateDirectories()) {
        if (($e.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
            $item = Get-Item -LiteralPath $e.FullName -Force
            $target = @($item.Target)[0]
            $rel = $e.FullName.Substring($plen)
            $newLink = Join-Path $Dst $rel
            if (-not (Test-Path -LiteralPath $newLink)) {
                New-Item -ItemType Junction -Path $newLink -Target $target | Out-Null
            }
            $n = @(Get-ChildItem -LiteralPath $newLink -Force -ErrorAction SilentlyContinue).Count
            'junction re-created: {0}  ->  {1}   (entries visible: {2})' -f $rel, $target, $n
        } else { $stack.Push($e.FullName) }
    }
}
'phase 1 done'
