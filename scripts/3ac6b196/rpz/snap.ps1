param([string]$name, [string]$crop = "6,166,2148,1050")
Add-Type -AssemblyName System.Drawing
Add-Type @"
using System; using System.Runtime.InteropServices;
public class S { [DllImport("user32.dll")] public static extern bool SetProcessDPIAware(); }
"@
[S]::SetProcessDPIAware() | Out-Null
$c = $crop.Split(',') | % { [int]$_ }
$bmp = New-Object System.Drawing.Bitmap $c[2], $c[3]
$g = [System.Drawing.Graphics]::FromImage($bmp); $g.CopyFromScreen($c[0], $c[1], 0, 0, $bmp.Size)
$bmp.Save("$PSScriptRoot\snap\$name.png", [System.Drawing.Imaging.ImageFormat]::Png)
"saved $name"
