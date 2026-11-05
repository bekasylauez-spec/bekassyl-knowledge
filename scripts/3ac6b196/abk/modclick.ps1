param([int]$x,[int]$y,[byte]$vk=0x10)
Add-Type @"
using System; using System.Runtime.InteropServices;
public class K { [DllImport("user32.dll")] public static extern bool SetCursorPos(int x,int y);
[DllImport("user32.dll")] public static extern void mouse_event(int f,int dx,int dy,int d,int e);
[DllImport("user32.dll")] public static extern void keybd_event(byte vk,byte sc,int f,int e);
[DllImport("user32.dll")] public static extern bool SetProcessDPIAware(); }
"@
[K]::SetProcessDPIAware()|Out-Null
[K]::SetCursorPos($x,$y); Start-Sleep -m 150
[K]::keybd_event($vk,0,0,0); Start-Sleep -m 150
[K]::mouse_event(2,0,0,0,0); [K]::mouse_event(4,0,0,0,0); Start-Sleep -m 300
[K]::keybd_event($vk,0,2,0)
