# Caches / logs / leftovers of Claude and ChatGPT(Codex). Only regenerable data.
param([switch]$Apply)
$ErrorActionPreference = 'Stop'
$L = $env:LOCALAPPDATA
$U = $env:USERPROFILE
$script:total = [long]0

function Measure-Tree([string]$path) {
    $size = [long]0; $n = 0; $rp = 0
    $stack = New-Object System.Collections.Stack
    $stack.Push($path)
    while ($stack.Count -gt 0) {
        $p = $stack.Pop()
        try {
            $di = New-Object System.IO.DirectoryInfo($p)
            foreach ($e in $di.EnumerateFileSystemInfos()) {
                if (($e.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { $rp++ }
                elseif (($e.Attributes -band [IO.FileAttributes]::Directory) -ne 0) { $stack.Push($e.FullName) }
                else { $size += $e.Length; $n++ }
            }
        } catch {}
    }
    return @($size, $n, $rp)
}

function Drop-Tree([string]$path, [string]$what) {
    if (-not (Test-Path -LiteralPath $path)) { '  (absent) ' + $path; return }
    $m = Measure-Tree $path
    if ($m[2] -gt 0) { '  SKIP (contains {0} reparse points): {1}' -f $m[2], $path; return }
    if ($Apply) {
        cmd /c rd /s /q "$path" 2>$null
        $left = Test-Path -LiteralPath $path
        $rest = [long]0
        if ($left) { $rest = (Measure-Tree $path)[0] }
        $freed = $m[0] - $rest
        $script:total += $freed
        '  {0,8:N1} MB freed  {1}  [{2}]{3}' -f ($freed / 1MB), $path, $what, $(if ($left) { '  (partly in use, {0:N1} MB left)' -f ($rest / 1MB) } else { '' })
    } else {
        $script:total += $m[0]
        '  {0,8:N1} MB  {1} files  {2}  [{3}]' -f ($m[0] / 1MB), $m[1], $path, $what
    }
}

function Drop-File([string]$path, [string]$what) {
    if (-not (Test-Path -LiteralPath $path)) { '  (absent) ' + $path; return }
    $len = (Get-Item -LiteralPath $path -Force).Length
    if ($Apply) {
        try { [IO.File]::Delete($path); $script:total += $len; '  {0,8:N1} MB freed  {1}  [{2}]' -f ($len / 1MB), $path, $what }
        catch { '  in use, kept: ' + $path }
    } else { $script:total += $len; '  {0,8:N1} MB  {1}  [{2}]' -f ($len / 1MB), $path, $what }
}

'== Claude =='
foreach ($n in 'main1.log', 'main2.log', 'main3.log', 'mcp-server-Windows-MCP1.log') { Drop-File (Join-Path $L "Claude\logs\$n") 'rotated log' }
Drop-Tree (Join-Path $L 'Packages\Claude_pzs8sxrjxfjjc\LocalCache\Local\pip\cache') 'pip cache'
Drop-Tree (Join-Path $L 'Packages\Claude_pzs8sxrjxfjjc\LocalCache\Local\com.autodesk.cer-dialog') 'Autodesk crash-dialog web cache'
Drop-Tree (Join-Path $U '.claude-server-commander\puppeteer-cache') 'downloaded Chrome for Desktop Commander'

'== ChatGPT / Codex =='
$cut = (Get-Date).AddHours(-24)
Get-ChildItem -LiteralPath (Join-Path $L 'Temp') -Force -ErrorAction SilentlyContinue | Where-Object { $_.Name -match '^codex-(artifact-session|clipboard)-' -and $_.LastWriteTime -lt $cut } | ForEach-Object {
    if ($_.PSIsContainer) { Drop-Tree $_.FullName 'old temp artifact' } else { Drop-File $_.FullName 'old clipboard image' }
}
Drop-Tree (Join-Path $L 'Packages\OpenAI.Codex_2p2nqsd0c76g0\LocalCache\Local\pip\cache') 'pip cache'
Drop-Tree (Join-Path $L 'Packages\OpenAI.Codex_2p2nqsd0c76g0\LocalCache\Local\pnpm-cache') 'pnpm metadata cache'
Drop-Tree (Join-Path $L 'Packages\OpenAI.Codex_2p2nqsd0c76g0\LocalCache\Local\pnpm\store') 'pnpm package store'
Get-ChildItem -LiteralPath (Join-Path $U '.cache\codex-runtimes') -Directory -Force -ErrorAction SilentlyContinue | Where-Object { $_.Name -like 'codex-primary-runtime.previous-*' } | ForEach-Object { Drop-Tree $_.FullName 'previous runtime leftover' }

'TOTAL: {0:N1} MB {1}' -f ($script:total / 1MB), $(if ($Apply) { 'freed' } else { '(dry run)' })
