param([string]$spec)  # e.g. "r1600:700-2600;c1000:780-1850"  r=row(y) scan along x, c=column(x) scan along y
Add-Type -AssemblyName System.Drawing
$sp="C:\Users\beka\AppData\Local\Temp\claude\D---------------\23042271-b03d-4833-b9de-78a4b9df170c\scratchpad\uy"
$i=New-Object Drawing.Bitmap "$sp\page1.png"
foreach($s in $spec.Split(';')){
  if($s -notmatch '^([rc])(\d+):(\d+)-(\d+)$'){ continue }
  $k=$matches[1]; $v=[int]$matches[2]; $a=[int]$matches[3]; $b=[int]$matches[4]
  $runs=@(); $st=-1
  for($t=$a;$t -le $b;$t++){
    $p= if($k -eq 'r'){ $i.GetPixel($t,$v) } else { $i.GetPixel($v,$t) }
    $dark = ($p.R -lt 80 -and $p.G -lt 80 -and $p.B -lt 80)
    if($dark -and $st -lt 0){$st=$t}
    if(-not $dark -and $st -ge 0){ $runs += $(if($t-1 -eq $st){"$st"}else{"$st-$($t-1)"}); $st=-1 }
  }
  "$s => " + ($runs -join ' ')
}
$i.Dispose()
