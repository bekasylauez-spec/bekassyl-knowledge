param([string]$act, [int]$x = 0, [int]$y = 0, [string]$text = "", [int]$procId = 0, [string]$crop = "0,0,2560,1440", [int]$div = 2)
Add-Type -AssemblyName System.Windows.Forms, System.Drawing
Add-Type @"
using System; using System.Runtime.InteropServices;
public class U {
 [DllImport("user32.dll")] public static extern bool SetProcessDPIAware();
 [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
 [DllImport("user32.dll")] public static extern void mouse_event(int f, int dx, int dy, int d, int e);
 [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
 [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int c);
}
"@
[U]::SetProcessDPIAware() | Out-Null
$dir = $PSScriptRoot
if ($procId -gt 0) { $p = Get-Process -Id $procId; [U]::SetForegroundWindow($p.MainWindowHandle) | Out-Null; Start-Sleep -Milliseconds 400 }
switch ($act) {
 'click'  { [U]::SetCursorPos($x, $y); Start-Sleep -Milliseconds 150; [U]::mouse_event(2,0,0,0,0); [U]::mouse_event(4,0,0,0,0) }
 'dclick' { [U]::SetCursorPos($x, $y); Start-Sleep -Milliseconds 150; 1..2 | % { [U]::mouse_event(2,0,0,0,0); [U]::mouse_event(4,0,0,0,0); Start-Sleep -Milliseconds 80 } }
 'rclick' { [U]::SetCursorPos($x, $y); Start-Sleep -Milliseconds 150; [U]::mouse_event(8,0,0,0,0); [U]::mouse_event(16,0,0,0,0) }
 'keys'   { [System.Windows.Forms.SendKeys]::SendWait($text) }
 'move'   { [U]::SetCursorPos($x, $y) }
 'wheel'  { [U]::SetCursorPos($x, $y); Start-Sleep -Milliseconds 100; [U]::mouse_event(0x0800,0,0,[int]$text,0) }
 'hwheel' { [U]::SetCursorPos($x, $y); Start-Sleep -Milliseconds 100; [U]::mouse_event(0x01000,0,0,[int]$text,0) }
}
Start-Sleep -Milliseconds 1200
$c = $crop.Split(',') | % { [int]$_ }
$bmp = New-Object System.Drawing.Bitmap $c[2], $c[3]
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen($c[0], $c[1], 0, 0, $bmp.Size)
$sm = New-Object System.Drawing.Bitmap $bmp, ([int]($c[2] / $div)), ([int]($c[3] / $div))
$sm.Save("$dir\ui.png", [System.Drawing.Imaging.ImageFormat]::Png)
"ok"
