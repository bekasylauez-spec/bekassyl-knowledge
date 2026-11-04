param([string]$Dwg, [string]$Dir)
# plot jobs $Dir\plotc.json from $Dwg (console), crop each page to its frame and merge into $Dir\all.pdf
$SP = "C:\Users\Admin\AppData\Local\Temp\claude\D---------\760c999f-c28c-44e9-ba81-9cb2aa467e81\scratchpad"
Copy-Item $Dwg "$Dir\src.dwg" -Force
Remove-Item "$Dir\plotc_log.txt" -ErrorAction SilentlyContinue
& "$SP\net\run.ps1" -Cs "$SP\net\plotc.cs" -Cmd "_.UCS" -Extra @("_W", "PLOTC") -Dwg "$Dir\src.dwg" -Env @{TEMP = $Dir; TMP = $Dir} | Out-Null
$bad = Get-Content "$Dir\plotc_log.txt" -Encoding UTF8 | Where-Object { $_ -notmatch ' ok True' }
"plotted: " + (Get-Content "$Dir\plotc_log.txt" -Encoding UTF8 | Where-Object { $_ -match ' ok True' }).Count + " bad: " + ($bad -join ' | ')
python -X utf8 "$SP\w\merge.py" "$Dir"

