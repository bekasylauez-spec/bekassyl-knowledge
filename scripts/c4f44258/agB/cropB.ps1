param($src,$x,$y,$w,$h,$out,$scale=1)
Add-Type -AssemblyName System.Drawing
$img=[System.Drawing.Image]::FromFile($src)
$bmp=New-Object System.Drawing.Bitmap ([int]($w*$scale)),([int]($h*$scale))
$g=[System.Drawing.Graphics]::FromImage($bmp)
$g.InterpolationMode='HighQualityBicubic'
$g.DrawImage($img,(New-Object System.Drawing.Rectangle 0,0,([int]($w*$scale)),([int]($h*$scale))),(New-Object System.Drawing.Rectangle $x,$y,$w,$h),'Pixel')
$bmp.Save($out,[System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose();$bmp.Dispose();$img.Dispose()
