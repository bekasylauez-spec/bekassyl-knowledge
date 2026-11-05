param([int[]]$mods = @(0x11, 0x10), [int]$key = 0x50)
Add-Type @"
using System; using System.Runtime.InteropServices;
public class K { [DllImport("user32.dll")] public static extern void keybd_event(byte vk, byte sc, int f, int e); }
"@
foreach ($m in $mods) { [K]::keybd_event([byte]$m, 0, 0, 0) }
[K]::keybd_event([byte]$key, 0, 0, 0); Start-Sleep -Milliseconds 80; [K]::keybd_event([byte]$key, 0, 2, 0)
[array]::Reverse($mods); foreach ($m in $mods) { [K]::keybd_event([byte]$m, 0, 2, 0) }
