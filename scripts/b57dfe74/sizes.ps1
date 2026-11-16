param([string[]]$Paths, [int]$Depth = 1, [double]$MinMB = 20)

# Reparse point-тарға (junction/symlink) кірмейтін өлшеуіш
function Get-DirSize([string]$path) {
    $total = 0L; $count = 0; $errs = 0
    $stack = New-Object System.Collections.Stack
    $stack.Push($path)
    while ($stack.Count -gt 0) {
        $p = $stack.Pop()
        try {
            $di = New-Object System.IO.DirectoryInfo($p)
            foreach ($f in $di.EnumerateFiles()) { $total += $f.Length; $count++ }
            foreach ($d in $di.EnumerateDirectories()) {
                if (($d.Attributes -band [IO.FileAttributes]::ReparsePoint) -eq 0) { $stack.Push($d.FullName) }
            }
        } catch { $errs++ }
    }
    return New-Object PSObject -Property @{ Size = $total; Count = $count; Errs = $errs }
}

function Show-Tree([string]$path, [int]$level, [int]$maxDepth, [double]$minMB) {
    $item = Get-Item -LiteralPath $path -Force -ErrorAction SilentlyContinue
    if (-not $item) { return }
    $indent = ('  ' * $level)
    if (-not $item.PSIsContainer) {
        $mb = [math]::Round($item.Length / 1MB, 1)
        if ($level -eq 0 -or $mb -ge $minMB) { '{0}{1,10:N1} MB  {2}' -f $indent, $mb, $item.FullName }
        return
    }
    if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
        '{0}  [REPARSE]    {1}  -> {2}' -f $indent, $item.FullName, ($item.Target -join ';')
        return
    }
    $s = Get-DirSize $item.FullName
    $mb = [math]::Round($s.Size / 1MB, 1)
    if ($level -eq 0 -or $mb -ge $minMB) {
        $e = ''
        if ($s.Errs -gt 0) { $e = '  (errs ' + $s.Errs + ')' }
        '{0}{1,10:N1} MB  {2}  [{3} files, {5:yyyy-MM-dd}]{4}' -f $indent, $mb, $item.FullName, $s.Count, $e, $item.LastWriteTime
        if ($level -lt $maxDepth) {
            $kids = @()
            try { $kids = Get-ChildItem -LiteralPath $item.FullName -Force -ErrorAction SilentlyContinue } catch {}
            foreach ($k in $kids) { Show-Tree $k.FullName ($level + 1) $maxDepth $minMB }
        }
    }
}

foreach ($p in $Paths) { Show-Tree $p 0 $Depth $MinMB }
