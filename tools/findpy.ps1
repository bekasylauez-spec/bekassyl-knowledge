# Returns the path of a real python.exe (not the Microsoft Store stub in WindowsApps), or $null.
# Use: $py = & "$PSScriptRoot\findpy.ps1"
$c = @()
$g = Get-Command python, py -All -ErrorAction SilentlyContinue | Where-Object { $_.Source -and $_.Source -notmatch '\\WindowsApps\\' }
if ($g) { $c += $g.Source }
$c += Get-ChildItem "$env:LOCALAPPDATA\Programs\Python\Python3*\python.exe", "$env:ProgramFiles\Python3*\python.exe", "${env:ProgramFiles(x86)}\Python3*\python.exe" -ErrorAction SilentlyContinue |
      Sort-Object FullName -Descending | ForEach-Object FullName
foreach ($p in ($c | Select-Object -Unique)) {
    try {
        $v = & $p --version 2>&1 | Out-String
        if ($v -match 'Python 3\.\d+') { return $p }
    } catch {}
}
return $null
