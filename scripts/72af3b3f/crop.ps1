# crop.ps1 -In a.png -Out b.png -R "x0,y0,x1,y1" (fractions 0..1) [-Max 2000]
param([string]$In, [string]$Out, [string]$R, [int]$Max = 2000)
Add-Type -AssemblyName System.Drawing
$img = [Drawing.Image]::FromFile((Resolve-Path $In).Path)
$c = $R.Split(',') | % { [double]$_ }
$x0 = [int]($c[0]*$img.Width); $y0 = [int]($c[1]*$img.Height); $cw = [int](($c[2]-$c[0])*$img.Width); $ch = [int](($c[3]-$c[1])*$img.Height)
$s = [Math]::Min(1.0, $Max / [double][Math]::Max($cw, $ch))
$bmp = New-Object Drawing.Bitmap ([int]($cw*$s)), ([int]($ch*$s))
$g = [Drawing.Graphics]::FromImage($bmp); $g.InterpolationMode = 'HighQualityBicubic'
$g.DrawImage($img, (New-Object Drawing.Rectangle 0,0,$bmp.Width,$bmp.Height), (New-Object Drawing.Rectangle $x0,$y0,$cw,$ch), 'Pixel')
$bmp.Save($Out, [Drawing.Imaging.ImageFormat]::Png); $g.Dispose(); $bmp.Dispose(); $img.Dispose()
