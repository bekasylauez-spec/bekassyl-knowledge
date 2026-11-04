param([string]$name,[int]$x,[int]$y,[int]$w,[int]$h,[int]$step=25,[double]$z=2)
# coords in 3000-px page units (page1.png); output zoom z. NB: PowerShell vars are case-insensitive.
$sp="C:\Users\beka\AppData\Local\Temp\claude\D---------------\23042271-b03d-4833-b9de-78a4b9df170c\scratchpad\uy"
Add-Type -AssemblyName System.Drawing
$src=New-Object Drawing.Bitmap "$sp\page1.png"
$outW=[int]($w*$z); $outH=[int]($h*$z)
$bmp=New-Object Drawing.Bitmap $outW,$outH; $g=[Drawing.Graphics]::FromImage($bmp); $g.Clear([Drawing.Color]::White)
$g.InterpolationMode=[Drawing.Drawing2D.InterpolationMode]::NearestNeighbor
$g.DrawImage($src,(New-Object Drawing.Rectangle 0,0,$outW,$outH),(New-Object Drawing.Rectangle $x,$y,$w,$h),[Drawing.GraphicsUnit]::Pixel)
$pen=New-Object Drawing.Pen ([Drawing.Color]::FromArgb(80,0,120,255)),1; $f=New-Object Drawing.Font "Arial",9; $br=[Drawing.Brushes]::Blue
for($gx=[Math]::Ceiling($x/$step)*$step;$gx -lt $x+$w;$gx+=$step){ $px=($gx-$x)*$z; $g.DrawLine($pen,$px,0,$px,$outH); $g.DrawString("$gx",$f,$br,$px+1,1) }
for($gy=[Math]::Ceiling($y/$step)*$step;$gy -lt $y+$h;$gy+=$step){ $py=($gy-$y)*$z; $g.DrawLine($pen,0,$py,$outW,$py); $g.DrawString("$gy",$f,$br,1,$py+1) }
$bmp.Save("$sp\$name.png"); $g.Dispose(); $bmp.Dispose(); $src.Dispose()
