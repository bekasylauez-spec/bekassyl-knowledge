param([double]$X0,[double]$X1,[double]$Y0,[double]$Y1,[double]$OX,[double]$OY,[switch]$NoText)
$s=Get-Content "C:\Users\beka\AppData\Local\Temp\claude\D---------------\c4f44258-6943-4b10-8e73-e6f1e42efec6\scratchpad\s20.txt" -Encoding UTF8
foreach($l in $s){ $p=$l.Split('|'); if($NoText -and $p[0] -eq 'T'){continue}
 $pts=@(); $any=$false
 for($i=1;$i -lt $p.Count;$i++){ $seg=$p[$i]; $b=''; if($seg.Contains('~')){$b='~'+$seg.Split('~')[1]; $seg=$seg.Split('~')[0]}; $c=$seg.Trim().Split(' '); $x=0.0;$y=0.0
  if($c.Count -eq 2 -and [double]::TryParse($c[0],[ref]$x) -and [double]::TryParse($c[1],[ref]$y)){ if($x -ge $X0 -and $x -le $X1 -and $y -ge $Y0 -and $y -le $Y1){$any=$true}; $pts+=('{0:0.#} {1:0.#}{2}' -f ($x-$OX),($y-$OY),$b) } else { $pts+=$p[$i] } }
 if($any){ $p[0]+'|'+($pts -join '|') } }
