. "$PSScriptRoot\rotlib.ps1"
$all = [Rot]::All(); "count " + $all.Count
foreach ($it in $all) { $n = [string]$it[0]; if ($n.EndsWith('.dwg')) { $o = $it[1]; $s = ''; try { $s = [string]$o.GetType().InvokeMember('Saved','GetProperty',$null,$o,$null) } catch { $s = 'ERR ' + $_.Exception.InnerException.Message }; [IO.File]::AppendAllText("$PSScriptRoot\probe2.txt", $n + ' | ' + $s + "`r`n", [Text.Encoding]::UTF8) } }
