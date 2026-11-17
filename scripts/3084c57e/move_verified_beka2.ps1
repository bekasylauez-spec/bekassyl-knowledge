# Verified move C -> D: robocopy, then byte-by-byte compare (treecmp.exe), then remove the source.
# Usage: move_verified_beka2.ps1 -Src <file|dir> -Dst <file|dir>  [-Recycle]  (-Recycle: after the move, send the D copy to D's Recycle Bin)
param([Parameter(Mandatory)][string]$Src, [Parameter(Mandatory)][string]$Dst, [switch]$Recycle)
$ErrorActionPreference = 'Stop'
$sp  = 'C:\Users\beka\AppData\Local\Temp\claude\61d567fc0ab17a45\3084c57e-bfd6-4f37-98c3-78b360193443\scratchpad'
$log = "$sp\move_log.tsv"
$isFile = Test-Path -LiteralPath $Src -PathType Leaf
if (-not (Test-Path -LiteralPath $Src)) { "SKIP (no source): $Src"; exit 0 }
if (Test-Path -LiteralPath $Dst) { "STOP (destination exists): $Dst"; exit 1 }
if (-not $isFile) {
    $rp = Get-ChildItem -LiteralPath $Src -Recurse -Force -Directory -ErrorAction SilentlyContinue | Where-Object { $_.Attributes -band [IO.FileAttributes]::ReparsePoint }
    if ($rp) { "STOP (reparse point inside): $($rp[0].FullName)"; exit 1 }
}
$t0 = Get-Date
if ($isFile) {
    $sd = Split-Path -LiteralPath $Src; $sn = Split-Path -Leaf $Src; $dd = Split-Path $Dst; $dn = Split-Path -Leaf $Dst
    if ($sn -ne $dn) { "STOP: file name must stay the same"; exit 1 }
    robocopy $sd $dd $sn /COPY:DAT /R:1 /W:1 /J /NP /NFL /NDL /NJH /NJS | Out-Null
} else {
    robocopy $Src $Dst /E /COPY:DAT /DCOPY:T /R:1 /W:1 /XJ /J /NP /NFL /NDL /NJH /NJS | Out-Null
}
$rc = $LASTEXITCODE
if ($rc -ge 8) { "FAIL robocopy exit=$rc : $Src"; exit 1 }
$cmp = & "$sp\treecmp.exe" $Src $Dst; $cc = $LASTEXITCODE
if ($cc -ne 0) { "FAIL compare: $Src"; $cmp; exit 1 }
if ($isFile) { [IO.File]::Delete($Src) } else { cmd /c rd /s /q "`"$Src`"" 2>$null }
if (Test-Path -LiteralPath $Src) { "WARN: source still exists: $Src" }
$size = if ($isFile) { (Get-Item -LiteralPath $Dst).Length } else { (Get-ChildItem -LiteralPath $Dst -Recurse -File -Force | Measure-Object Length -Sum).Sum }
$note = ''
if ($Recycle) {
    Add-Type -AssemblyName Microsoft.VisualBasic
    if ($isFile) { [Microsoft.VisualBasic.FileIO.FileSystem]::DeleteFile($Dst, 'OnlyErrorDialogs', 'SendToRecycleBin') }
    else { [Microsoft.VisualBasic.FileIO.FileSystem]::DeleteDirectory($Dst, 'OnlyErrorDialogs', 'SendToRecycleBin') }
    $note = if (Test-Path -LiteralPath $Dst) { 'RECYCLE-FAILED' } else { 'D-recycle-bin' }
}
$line = "{0:yyyy-MM-dd HH:mm:ss}`t{1}`t{2}`t{3}`t{4}" -f (Get-Date), $size, $Src, $Dst, $note
Add-Content -LiteralPath $log -Value $line -Encoding UTF8
'OK {0,8:N2} GB {1,4}s  {2}  ->  {3} {4}   [{5}]' -f ($size/1GB), [int]((Get-Date)-$t0).TotalSeconds, $Src, $Dst, $note, ($cmp | Select-Object -Last 1)
