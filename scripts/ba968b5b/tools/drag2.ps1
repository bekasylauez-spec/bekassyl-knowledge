param([int]$x1,[int]$y1,[int]$x2,[int]$y2)
Add-Type @"
using System; using System.Runtime.InteropServices;
public class D2 { [DllImport("user32.dll")] public static extern bool SetProcessDPIAware(); [DllImport("user32.dll")] public static extern bool SetCursorPos(int x,int y); [DllImport("user32.dll")] public static extern void mouse_event(int f,int a,int b,int c,int d);}
"@
[D2]::SetProcessDPIAware() | Out-Null
[D2]::SetCursorPos($x1,$y1); Start-Sleep -Milliseconds 200; [D2]::mouse_event(2,0,0,0,0)
for($i=1;$i -le 20;$i++){ [D2]::SetCursorPos([int]($x1+($x2-$x1)*$i/20),[int]($y1+($y2-$y1)*$i/20)); Start-Sleep -Milliseconds 30 }
Start-Sleep -Milliseconds 200; [D2]::mouse_event(4,0,0,0,0)
