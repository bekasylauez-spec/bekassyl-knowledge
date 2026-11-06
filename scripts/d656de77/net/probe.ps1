. "$PSScriptRoot\rotlib.ps1"
foreach ($it in [Rot]::All()) { if ($it[0] -like '*.dwg') { $d = $it[1]; try { $it[0] + ' | Saved=' + $d.Saved + ' | ' + $d.FullName } catch { $it[0] + ' ERR ' + $_.Exception.Message } } }
