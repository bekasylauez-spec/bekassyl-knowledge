param([string]$List)
# compile-check "script:lib" pairs (names relative to $env:A unless rooted)
$a = $env:A
foreach ($item in $List.Split(',')) {
    $p = $item.Split(':', 2); $f = $p[0]; if (-not [IO.Path]::IsPathRooted($f)) { $f = "$a\$f" }
    $lib = if ($p.Count -gt 1 -and $p[1] -ne "") { $p[1] } else { "" }
    if ($lib -ne "" -and -not [IO.Path]::IsPathRooted($lib)) { $lib = "$a\$lib" }
    if ($lib -ne "") { dotnet D:\_claude_work\RMC\revit\build_check\Chk.dll $f $lib | Select-String "error|FILE" } else { dotnet D:\_claude_work\RMC\revit\build_check\Chk.dll $f | Select-String "error|FILE" }
}
