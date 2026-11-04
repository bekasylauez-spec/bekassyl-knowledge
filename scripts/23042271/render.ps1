param([string[]]$views)
$edge="C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
$dir="D:\Бекасыл КЖ КМ\Uy_joba_14x8"
$sp="C:\Users\beka\AppData\Local\Temp\claude\D---------------\23042271-b03d-4833-b9de-78a4b9df170c\scratchpad"
Add-Type -AssemblyName System.Drawing
$codec=[Drawing.Imaging.ImageCodecInfo]::GetImageEncoders() | ? { $_.MimeType -eq 'image/jpeg' }
$ep=New-Object Drawing.Imaging.EncoderParameters 1; $ep.Param[0]=[Drawing.Imaging.EncoderParameter]::new([Drawing.Imaging.Encoder]::Quality,[long]86)
foreach($v in $views){
  $url=([Uri]"$dir\index.html").AbsoluteUri + "#r-$v"
  $png="$sp\r_$v.png"; if(Test-Path $png){ Remove-Item $png }
  Start-Process $edge -ArgumentList "--headless=new","--disable-gpu-sandbox","--enable-gpu","--ignore-gpu-blocklist","--user-data-dir=`"$sp\edgeprof_$v`"","--window-size=1920,1080","--hide-scrollbars","--virtual-time-budget=25000","--screenshot=`"$png`"","`"$url`"" -Wait
  $img=[Drawing.Image]::FromFile($png); $img.Save("$dir\renders\$v.jpg",$codec,$ep); $img.Dispose()
  "$v ok"
}


