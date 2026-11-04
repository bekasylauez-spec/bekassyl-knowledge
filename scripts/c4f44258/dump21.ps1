param([double]$X0,[double]$X1,[double]$Y0,[double]$Y1,[double]$OX=0,[double]$OY=0,[string]$Skip='')
# sheet21 dumper: entities from s21.txt with a vertex in window; coords relative to OX,OY
$ci=[Globalization.CultureInfo]::InvariantCulture
$s="C:\Users\beka\AppData\Local\Temp\claude\D---------------\c4f44258-6943-4b10-8e73-e6f1e42efec6\scratchpad\s21.txt"
function XY($t){$v=$t.Split('~')[0].Split(' ');@([double]::Parse($v[0],$ci),[double]::Parse($v[1],$ci))}
function In($p){$p[0]-ge $X0 -and $p[0]-le $X1 -and $p[1]-ge $Y0 -and $p[1]-le $Y1}
function R($p){ "{0:0.#},{1:0.#}" -f ($p[0]-$OX),($p[1]-$OY) }
foreach($l in [IO.File]::ReadLines($s,[Text.Encoding]::UTF8)){
 $f=$l.Split('|'); if($Skip -and $f[1] -match $Skip){continue}
 switch($f[0]){
  'L'{$a=XY $f[2];$b=XY $f[3]; if((In $a) -or (In $b)){ $dx=$b[0]-$a[0];$dy=$b[1]-$a[1]; $len=[math]::Sqrt($dx*$dx+$dy*$dy); $ang=[math]::Atan2($dy,$dx)*180/[math]::PI; "L {0} -> {1}  len={2:0.##} ang={3:0.##} [{4}]" -f (R $a),(R $b),$len,$ang,$f[1]}}
  'P'{$pts=@(); for($i=3;$i -lt $f.Count;$i++){$pts+=,$f[$i]}; $hit=$false; foreach($t in $pts){ if(In (XY $t)){$hit=$true;break}}; if($hit){ $o=($pts|%{ $q=XY $_; $bb=$_.Split('~'); (R $q)+$(if($bb.Count -gt 1){"~"+$bb[1]}else{''}) }) -join ' | '; "P c={0} [{1}] {2}" -f $f[2],$f[1],$o}}
  'C'{$c=XY $f[2]; if(In $c){"C {0} r={1} [{2}]" -f (R $c),$f[3],$f[1]}}
  'A'{$c=XY $f[2]; if(In $c){"A {0} r={1} a={2}..{3} [{4}]" -f (R $c),$f[3],$f[4],$f[5],$f[1]}}
  'T'{$c=XY $f[2]; if(In $c){"T {0} h={1} '{2}' [{3}]" -f (R $c),$f[3],($f[4..($f.Count-1)] -join '|'),$f[1]}}
 }}
