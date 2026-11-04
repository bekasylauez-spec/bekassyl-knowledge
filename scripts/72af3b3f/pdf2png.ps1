# pdf2png.ps1 -Pdf x.pdf -Out x.png [-Width 8000] [-Page 0] [-Crop "x0,y0,x1,y1" (fractions)]
param([string]$Pdf, [string]$Out, [int]$Width = 8000, [int]$Page = 0, [string]$Crop = "")
Add-Type -AssemblyName System.Runtime.WindowsRuntime
$null = [Windows.Data.Pdf.PdfDocument, Windows.Data.Pdf, ContentType = WindowsRuntime]
$null = [Windows.Storage.StorageFile, Windows.Storage, ContentType = WindowsRuntime]
$null = [Windows.Storage.Streams.InMemoryRandomAccessStream, Windows.Storage.Streams, ContentType = WindowsRuntime]
$asTaskG = ([System.WindowsRuntimeSystemExtensions].GetMethods() | ? { $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1' })[0]
$asTaskA = ([System.WindowsRuntimeSystemExtensions].GetMethods() | ? { $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncAction' })[0]
function Await($op, [Type]$t) { $task = $asTaskG.MakeGenericMethod($t).Invoke($null, @($op)); $task.Wait(-1) | Out-Null; $task.Result }
function AwaitA($op) { $task = $asTaskA.Invoke($null, @($op)); $task.Wait(-1) | Out-Null }
$f = Await ([Windows.Storage.StorageFile]::GetFileFromPathAsync((Resolve-Path $Pdf).Path)) ([Windows.Storage.StorageFile])
$doc = Await ([Windows.Data.Pdf.PdfDocument]::LoadFromFileAsync($f)) ([Windows.Data.Pdf.PdfDocument])
$pg = $doc.GetPage($Page)
$opt = New-Object Windows.Data.Pdf.PdfPageRenderOptions
$sz = $pg.Size
if ($Crop) { $c = $Crop.Split(',') | % { [double]$_ }
  $opt.SourceRect = New-Object Windows.Foundation.Rect ($c[0]*$sz.Width), ($c[1]*$sz.Height), (($c[2]-$c[0])*$sz.Width), (($c[3]-$c[1])*$sz.Height)
  $ar = (($c[3]-$c[1])*$sz.Height) / (($c[2]-$c[0])*$sz.Width) } else { $ar = $sz.Height / $sz.Width }
$opt.DestinationWidth = $Width; $opt.DestinationHeight = [uint32]($Width * $ar)
$opt.BackgroundColor = [Windows.UI.Color]::FromArgb(255,255,255,255)
$ms = New-Object Windows.Storage.Streams.InMemoryRandomAccessStream
AwaitA ($pg.RenderToStreamAsync($ms, $opt))
$st = [System.IO.WindowsRuntimeStreamExtensions]::AsStreamForRead($ms.GetInputStreamAt(0))
$fs = [IO.File]::Create($Out); $st.CopyTo($fs); $fs.Close()
"$Out $($opt.DestinationWidth)x$($opt.DestinationHeight) (page $($sz.Width)x$($sz.Height))"
