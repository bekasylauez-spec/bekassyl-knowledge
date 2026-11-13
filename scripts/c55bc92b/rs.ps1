param([string]$File, [string]$Lib = "", [string]$Out, [int]$Wait = 300)
$o = if ($Lib) { & "D:\_claude_work\RMC\revit\run.ps1" -File $File -Lib $Lib -Wait $Wait } else { & "D:\_claude_work\RMC\revit\run.ps1" -File $File -Wait $Wait }
$o | Out-File -Encoding utf8 $Out
"done " + $Out
