param([long]$Hwnd, [int]$X, [int]$Y)
# Real mouse click on screen point X,Y after bringing window Hwnd to front (Revit task dialogs ignore BM_CLICK).
Add-Type @"
using System; using System.Runtime.InteropServices;
public class MClk { [DllImport("user32.dll")] public static extern bool SetCursorPos(int x,int y); [DllImport("user32.dll")] public static extern void mouse_event(uint f,uint x,uint y,uint d,UIntPtr e); [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h); }
"@
[MClk]::SetForegroundWindow([IntPtr]$Hwnd) | Out-Null; Start-Sleep -Milliseconds 400
[MClk]::SetCursorPos($X, $Y) | Out-Null; [MClk]::mouse_event(2,0,0,0,[UIntPtr]::Zero); [MClk]::mouse_event(4,0,0,0,[UIntPtr]::Zero)
