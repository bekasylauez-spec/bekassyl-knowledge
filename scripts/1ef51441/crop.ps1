param([string]$In, [string]$Out, [double]$X0, [double]$Y0, [double]$X1, [double]$Y1)
# fractions of the image (0..1)
Add-Type -AssemblyName System.Drawing
$img = [System.Drawing.Image]::FromFile($In)
$r = New-Object System.Drawing.Rectangle ([int]($X0 * $img.Width)), ([int]($Y0 * $img.Height)), ([int](($X1 - $X0) * $img.Width)), ([int](($Y1 - $Y0) * $img.Height))
$bmp = New-Object System.Drawing.Bitmap $r.Width, $r.Height
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.DrawImage($img, (New-Object System.Drawing.Rectangle 0, 0, $r.Width, $r.Height), $r, [System.Drawing.GraphicsUnit]::Pixel)
$g.Dispose(); $img.Dispose()
$bmp.Save($Out, [System.Drawing.Imaging.ImageFormat]::Png); $bmp.Dispose()
