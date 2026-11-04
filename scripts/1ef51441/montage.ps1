param([string]$Dir, [string]$Out, [int]$From = 1, [int]$To = 99, [int]$Cols = 4, [int]$CellW = 700)
Add-Type -AssemblyName System.Drawing
$files = Get-ChildItem $Dir -Filter "p*.png" | Sort-Object Name | Where-Object { $n = [int]($_.BaseName.Substring(1)); $n -ge $From -and $n -le $To }
$cellH = [int]($CellW * 0.72)
$rows = [math]::Ceiling($files.Count / $Cols)
$bmp = New-Object System.Drawing.Bitmap ($Cols * $CellW), ($rows * ($cellH + 24))
$g = [System.Drawing.Graphics]::FromImage($bmp); $g.Clear([System.Drawing.Color]::White)
$g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
$font = New-Object System.Drawing.Font "Arial", 14, ([System.Drawing.FontStyle]::Bold)
$i = 0
foreach ($f in $files) {
  $img = [System.Drawing.Image]::FromFile($f.FullName)
  $s = [math]::Min(($CellW - 10) / $img.Width, ($cellH - 10) / $img.Height)
  $w = [int]($img.Width * $s); $h = [int]($img.Height * $s)
  $x = ($i % $Cols) * $CellW + 5; $y = [math]::Floor($i / $Cols) * ($cellH + 24) + 22
  $g.DrawImage($img, $x, $y, $w, $h); $img.Dispose()
  $g.DrawString($f.BaseName, $font, [System.Drawing.Brushes]::Red, $x, $y - 20)
  $g.DrawRectangle([System.Drawing.Pens]::Gray, $x, $y, $w, $h)
  $i++
}
$g.Dispose(); $bmp.Save($Out, [System.Drawing.Imaging.ImageFormat]::Png); $bmp.Dispose()
