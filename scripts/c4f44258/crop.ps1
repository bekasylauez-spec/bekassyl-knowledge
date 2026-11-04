Add-Type -AssemblyName System.Drawing
function Crop($src,$dst,$x,$y,$w,$h,$scale=1.0){
 $im=[System.Drawing.Image]::FromFile($src)
 $W=[int]($w*$scale);$H=[int]($h*$scale)
 $bm=New-Object System.Drawing.Bitmap $W,$H
 $g=[System.Drawing.Graphics]::FromImage($bm)
 $g.InterpolationMode='HighQualityBicubic'
 $g.DrawImage($im,(New-Object System.Drawing.Rectangle 0,0,$W,$H),(New-Object System.Drawing.Rectangle $x,$y,$w,$h),[System.Drawing.GraphicsUnit]::Pixel)
 $bm.Save($dst,[System.Drawing.Imaging.ImageFormat]::Png)
 $g.Dispose();$bm.Dispose();$im.Dispose()
}
