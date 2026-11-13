param([string]$File, [string]$Lib = "", [string]$Out = "", [int]$Wait = 900)
# run a script in MY Revit via run.ps1 (absolute paths only; no Cyrillic literals here); save output to scratchpad\w\out\<Out>.txt
$sp = "C:\Users\Admin\AppData\Local\Temp\claude\a7137524bdaa49d0\c55bc92b-0511-4932-9c00-c1294111057c\scratchpad\w"
$t = Get-Date
if ($Lib -ne "") { $o = & D:\_claude_work\RMC\revit\run.ps1 -File $File -Lib $Lib -Wait $Wait } else { $o = & D:\_claude_work\RMC\revit\run.ps1 -File $File -Wait $Wait }
if ($Out -eq "") { $Out = [IO.Path]::GetFileNameWithoutExtension($File) }
$o | Out-File -Encoding utf8 "$sp\out\$Out.txt"
"{0:N0} s -> $sp\out\$Out.txt" -f ((Get-Date) - $t).TotalSeconds
